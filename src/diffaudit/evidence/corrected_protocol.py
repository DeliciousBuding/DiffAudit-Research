"""Corrected-evidence protocol primitives for Paper 1."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from importlib.metadata import version
from itertools import combinations
from numbers import Integral
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Literal

import numpy as np

from diffaudit.evidence.training_config import (
    build_training_config,
    canonical_training_config_hash,
)

_SPLIT_FILENAMES = {"cifar10": "CIFAR10_train_ratio0.5.npz"}
_CLASS_IDS = tuple(range(10))
_PROTOCOL_ENVELOPE_FIELDS = {"schema_version", "protocol_hash", "contract"}
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_GIT_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
_PAPER1_PROTOCOL_NAMESPACE = "paper1-corrected-evidence"
_PAPER1_COMMON_NOISE_NAMESPACE = "paper1-corrected-v1"
_PAPER1_ROW_RANDOM_STATE = 1746574482
_PAPER1_CONTRACT_FIELDS = {
    "protocol_namespace",
    "dataset",
    "training",
    "evaluation",
    "h1",
    "pia",
    "common_noise",
    "branch_rules",
    "confirmatory_heterogeneity",
    "code_commit",
}


def _digest_parts(*parts: object) -> bytes:
    encoded = "\0".join(str(part) for part in parts).encode("utf-8")
    return hashlib.sha256(encoded).digest()


def _validated_indices(membership: str, values: Sequence[int]) -> tuple[int, ...]:
    raw_values = tuple(values)
    if any(isinstance(value, bool) or not isinstance(value, Integral) for value in raw_values):
        raise ValueError(f"{membership} indices must contain integers")
    return tuple(int(value) for value in raw_values)


def _validated_nonnegative_count(name: str, value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return int(value)


def _balanced_split_class_counts(
    calibration_count: int,
    evaluation_count: int,
    capacities: Mapping[int, int],
    *,
    random_state: int,
) -> tuple[dict[int, int], dict[int, int]]:
    calibration_base, calibration_remainder = divmod(calibration_count, len(_CLASS_IDS))
    evaluation_base, evaluation_remainder = divmod(evaluation_count, len(_CLASS_IDS))
    base_total = calibration_base + evaluation_base
    remaining = {class_id: capacities[class_id] - base_total for class_id in _CLASS_IDS}
    if any(capacity < 0 for capacity in remaining.values()):
        raise ValueError("shared membership class capacities cannot support balanced splits")

    calibration_candidates = sorted(
        combinations(
            [class_id for class_id in _CLASS_IDS if remaining[class_id] > 0],
            calibration_remainder,
        ),
        key=lambda classes: _digest_parts(
            "diffaudit-row-class-order-v1",
            random_state,
            "calibration",
            *classes,
        ),
    )
    for calibration_extras in calibration_candidates:
        after_calibration = remaining.copy()
        for class_id in calibration_extras:
            after_calibration[class_id] -= 1
        evaluation_candidates = sorted(
            combinations(
                [class_id for class_id in _CLASS_IDS if after_calibration[class_id] > 0],
                evaluation_remainder,
            ),
            key=lambda classes: _digest_parts(
                "diffaudit-row-class-order-v1",
                random_state,
                "evaluation",
                *classes,
            ),
        )
        if not evaluation_candidates:
            continue
        evaluation_extras = evaluation_candidates[0]
        calibration_counts = {class_id: calibration_base for class_id in _CLASS_IDS}
        evaluation_counts = {class_id: evaluation_base for class_id in _CLASS_IDS}
        for class_id in calibration_extras:
            calibration_counts[class_id] += 1
        for class_id in evaluation_extras:
            evaluation_counts[class_id] += 1
        return calibration_counts, evaluation_counts

    raise ValueError("shared membership class capacities cannot support balanced splits")


def _reject_absolute_paths(value: object) -> None:
    if isinstance(value, str):
        if (
            value.startswith("\\")
            or PureWindowsPath(value).is_absolute()
            or PurePosixPath(value).is_absolute()
        ):
            raise ValueError("absolute paths are not allowed in public protocol manifests")
        return
    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            _reject_absolute_paths(key)
            _reject_absolute_paths(nested_value)
        return
    if isinstance(value, (list, tuple)):
        for nested_value in value:
            _reject_absolute_paths(nested_value)


def _json_safe_copy(value: object, *, name: str) -> object:
    _reject_absolute_paths(value)
    try:
        payload = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        return json.loads(payload)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must contain only finite JSON values") from error


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is not allowed: {value}")


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key is not allowed: {key}")
        result[key] = value
    return result


def _require_exact_json_value(name: str, actual: object, expected: object) -> None:
    if type(actual) is not type(expected):
        raise ValueError(f"Paper 1 {name} does not match the fixed contract")
    if isinstance(expected, dict):
        if set(actual) != set(expected):
            raise ValueError(f"Paper 1 {name} does not match the fixed contract")
        for key, expected_value in expected.items():
            _require_exact_json_value(f"{name}.{key}", actual[key], expected_value)
        return
    if isinstance(expected, list):
        if len(actual) != len(expected):
            raise ValueError(f"Paper 1 {name} does not match the fixed contract")
        for index, (actual_value, expected_value) in enumerate(zip(actual, expected, strict=True)):
            _require_exact_json_value(f"{name}[{index}]", actual_value, expected_value)
        return
    if actual != expected:
        raise ValueError(f"Paper 1 {name} does not match the fixed contract")


@dataclass(frozen=True, slots=True)
class MembershipSplit:
    """Validated member and nonmember dataset indices."""

    member_indices: tuple[int, ...]
    nonmember_indices: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class ProtocolRow:
    """One frozen dataset row in a corrected-evidence protocol split."""

    dataset_index: int
    label: Literal[0, 1]
    class_id: int
    split: Literal["calibration", "evaluation"]


def canonical_protocol_hash(protocol: Mapping[str, object]) -> str:
    """Hash a public-safe protocol mapping using recursive canonical JSON."""

    _reject_absolute_paths(protocol)
    payload = json.dumps(
        protocol,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_protocol_envelope(contract: Mapping[str, object]) -> dict[str, object]:
    """Return a hash-sealed, detached JSON-safe copy of a protocol contract."""

    if not isinstance(contract, Mapping):
        raise ValueError("contract must be a JSON mapping")
    copied_contract = _json_safe_copy(contract, name="contract")
    if not isinstance(copied_contract, dict):
        raise ValueError("contract must be a JSON mapping")
    return {
        "schema_version": 1,
        "protocol_hash": canonical_protocol_hash(copied_contract),
        "contract": copied_contract,
    }


def load_protocol_envelope(
    source: Mapping[str, object] | str | Path,
) -> dict[str, object]:
    """Load and verify a hash-sealed integrity envelope from a mapping or JSON path."""

    if isinstance(source, Mapping):
        raw_envelope: object = source
    else:
        try:
            raw_envelope = json.loads(
                Path(source).read_text(encoding="utf-8"),
                parse_constant=_reject_json_constant,
                object_pairs_hook=_reject_duplicate_json_keys,
            )
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ValueError("protocol envelope path must contain valid finite JSON") from error

    copied_envelope = _json_safe_copy(raw_envelope, name="protocol envelope")
    if not isinstance(copied_envelope, dict):
        raise ValueError("protocol envelope must be a JSON mapping")
    if set(copied_envelope) != _PROTOCOL_ENVELOPE_FIELDS:
        raise ValueError("protocol envelope top-level fields must be exact")
    if type(copied_envelope["schema_version"]) is not int or copied_envelope["schema_version"] != 1:
        raise ValueError("protocol envelope schema_version must be 1")

    protocol_hash = copied_envelope["protocol_hash"]
    if not isinstance(protocol_hash, str) or _SHA256_PATTERN.fullmatch(protocol_hash) is None:
        raise ValueError("protocol envelope protocol_hash must be 64 lowercase hex characters")
    contract = copied_envelope["contract"]
    if not isinstance(contract, dict):
        raise ValueError("protocol envelope contract must be a JSON mapping")
    if canonical_protocol_hash(contract) != protocol_hash:
        raise ValueError("protocol envelope protocol_hash does not match contract")
    return copied_envelope


def derive_noise_seed(
    protocol_namespace: str,
    dataset_index: int,
    timestep: int,
    draw: int,
) -> int:
    """Derive a stable common-noise seed without generating a tensor."""

    digest = _digest_parts(
        "diffaudit-common-noise-seed-v1",
        protocol_namespace,
        dataset_index,
        timestep,
        draw,
    )
    return int.from_bytes(digest[:8], "big") % (2**63 - 1) + 1


def build_stratified_row_manifest(
    member_indices: Sequence[int],
    nonmember_indices: Sequence[int],
    class_labels: Sequence[int],
    *,
    n_calibration_per_group: int = 512,
    n_evaluation_per_group: int = 512,
    random_state: int,
) -> tuple[ProtocolRow, ...]:
    """Build deterministic class-stratified calibration and evaluation rows."""

    n_calibration_per_group = _validated_nonnegative_count(
        "n_calibration_per_group", n_calibration_per_group
    )
    n_evaluation_per_group = _validated_nonnegative_count(
        "n_evaluation_per_group", n_evaluation_per_group
    )
    if n_calibration_per_group + n_evaluation_per_group == 0:
        raise ValueError("at least one row count must be positive")

    member = _validated_indices("member", member_indices)
    nonmember = _validated_indices("nonmember", nonmember_indices)
    labels = np.asarray(class_labels)
    if labels.ndim != 1:
        raise ValueError("class_labels must be one-dimensional")
    for membership, source_indices in (("member", member), ("nonmember", nonmember)):
        if len(set(source_indices)) != len(source_indices):
            raise ValueError(f"{membership} indices contain duplicates")
        if any(index < 0 for index in source_indices):
            raise ValueError("indices must be non-negative")
        if any(index >= labels.size for index in source_indices):
            raise ValueError("class_labels does not cover dataset index")
    if set(member) & set(nonmember):
        raise ValueError("member and nonmember indices overlap")

    source_class_ids: dict[int, int] = {}
    for index in (*member, *nonmember):
        class_id = labels[index]
        if isinstance(class_id, bool) or not isinstance(class_id, Integral):
            raise ValueError("class_labels for source rows must contain integers")
        normalized_class_id = int(class_id)
        if normalized_class_id not in _CLASS_IDS:
            raise ValueError("source class IDs must be in range 0..9")
        source_class_ids[index] = normalized_class_id

    total_required = n_calibration_per_group + n_evaluation_per_group
    group_specs = (
        ("member", 1, member),
        ("nonmember", 0, nonmember),
    )
    pools_by_membership: dict[str, dict[int, list[int]]] = {}
    for membership, _, source_indices in group_specs:
        if len(source_indices) < total_required:
            raise ValueError(f"{membership} group requires at least {total_required} rows")
        pools_by_membership[membership] = {
            class_id: [index for index in source_indices if source_class_ids[index] == class_id]
            for class_id in _CLASS_IDS
        }

    calibration_counts, evaluation_counts = _balanced_split_class_counts(
        n_calibration_per_group,
        n_evaluation_per_group,
        {
            class_id: min(
                len(pools_by_membership["member"][class_id]),
                len(pools_by_membership["nonmember"][class_id]),
            )
            for class_id in _CLASS_IDS
        },
        random_state=random_state,
    )

    rows: list[ProtocolRow] = []
    for membership, label, _ in group_specs:
        pools = pools_by_membership[membership]
        for class_id in _CLASS_IDS:
            calibration_count = calibration_counts[class_id]
            evaluation_count = evaluation_counts[class_id]
            required = calibration_count + evaluation_count
            if len(pools[class_id]) < required:
                raise ValueError(
                    f"{membership} class {class_id} requires {required} rows, "
                    f"found {len(pools[class_id])}"
                )
            ranked = sorted(
                pools[class_id],
                key=lambda index: _digest_parts(
                    "diffaudit-row-selection-v1",
                    random_state,
                    membership,
                    class_id,
                    index,
                ),
            )
            rows.extend(
                ProtocolRow(index, label, class_id, "calibration")
                for index in ranked[:calibration_count]
            )
            rows.extend(
                ProtocolRow(index, label, class_id, "evaluation")
                for index in ranked[calibration_count:required]
            )

    return tuple(rows)


def build_paper1_corrected_row_manifest(
    member_indices: Sequence[int],
    nonmember_indices: Sequence[int],
    class_labels: Sequence[int],
    *,
    random_state: int,
) -> tuple[ProtocolRow, ...]:
    """Build the fixed 512/512-per-membership Paper 1 corrected row manifest."""

    return build_stratified_row_manifest(
        member_indices,
        nonmember_indices,
        class_labels,
        n_calibration_per_group=512,
        n_evaluation_per_group=512,
        random_state=random_state,
    )


def derive_training_seeds(seed_material: str | bytes, count: int = 8) -> tuple[int, ...]:
    """Derive deterministic training seeds from stable seed material."""

    if isinstance(count, bool) or not isinstance(count, Integral) or count <= 0:
        raise ValueError("count must be a positive integer")
    count = int(count)
    material = seed_material.encode("utf-8") if isinstance(seed_material, str) else seed_material
    seeds: list[int] = []
    seen: set[int] = set()
    counter = 0
    while len(seeds) < count:
        digest = hashlib.sha256(
            b"diffaudit-training-seed-v1\0" + material + b"\0" + counter.to_bytes(8, "big")
        ).digest()
        seed = int.from_bytes(digest[:4], "big") & 0x7FFF_FFFF
        if seed > 0 and seed not in seen:
            seeds.append(seed)
            seen.add(seed)
        counter += 1
    return tuple(seeds)


def load_member_nonmember_indices(
    split_path: str | Path | None = None,
    *,
    split_root: str | Path | None = None,
    dataset: str | None = None,
    dataset_size: int | None = None,
) -> MembershipSplit:
    """Load and validate the canonical member and nonmember index arrays."""

    if (split_path is None) == (split_root is None):
        raise ValueError("provide exactly one of split_path or split_root")
    if split_path is None:
        normalized_dataset = str(dataset).lower()
        if normalized_dataset not in _SPLIT_FILENAMES:
            raise ValueError(f"Unsupported dataset for membership split: {dataset}")
        split_path = Path(split_root) / _SPLIT_FILENAMES[normalized_dataset]

    with np.load(Path(split_path), allow_pickle=False) as payload:
        required_keys = ("mia_train_idxs", "mia_eval_idxs")
        for key in required_keys:
            if key not in payload:
                raise ValueError(f"Membership split is missing required key: {key}")
        member = np.asarray(payload["mia_train_idxs"])
        nonmember = np.asarray(payload["mia_eval_idxs"])

    for key, values in (("mia_train_idxs", member), ("mia_eval_idxs", nonmember)):
        if values.ndim != 1:
            raise ValueError(f"{key} must be one-dimensional")
        if not np.issubdtype(values.dtype, np.integer):
            raise ValueError(f"{key} must contain integers")
        if np.unique(values).size != values.size:
            raise ValueError(f"{key} contains duplicate indices")

    if np.intersect1d(member, nonmember).size:
        raise ValueError("member and nonmember indices overlap")
    if np.any(member < 0) or np.any(nonmember < 0):
        raise ValueError("indices must be non-negative")
    if dataset_size is not None and (
        np.any(member >= dataset_size) or np.any(nonmember >= dataset_size)
    ):
        raise ValueError(f"indices must be smaller than dataset_size={dataset_size}")

    return MembershipSplit(
        member_indices=tuple(int(value) for value in member),
        nonmember_indices=tuple(int(value) for value in nonmember),
    )


def _paper1_h1_contract() -> dict[str, object]:
    seeds = list(derive_training_seeds(_PAPER1_PROTOCOL_NAMESPACE))
    return {
        "sites": ["late_down", "mid_0", "mid_1", "early_up"],
        "timesteps": [100, 400, 700],
        "score_direction": "higher_is_member",
        "feature_scaler": "none",
        "sklearn_version": version("scikit-learn"),
        "pca": {
            "n_components": 6,
            "svd_solver": "randomized",
            "whiten": False,
            "random_state": 42,
            "n_oversamples": 10,
            "iterated_power": 4,
            "power_iteration_normalizer": "QR",
        },
        "bootstrap_replicates": 200,
        "permutation_replicates": 200,
        "bootstrap_random_state": 20260711,
        "permutation_random_state": 20260712,
        "cross_target_rosters": {
            "stage1": {"seeds": seeds[:4], "step": 100_000},
            "replicate": {"seeds": seeds[4:], "step": 100_000},
            "full": {"seeds": seeds, "step": 100_000},
            "mature": {"seeds": seeds[:4], "step": 200_000},
        },
        "logistic_regression": {
            "logical_penalty": "l2",
            "constructor": {
                "dual": False,
                "l1_ratio": 0.0,
                "C": 1.0,
                "fit_intercept": True,
                "class_weight": "balanced",
                "solver": "lbfgs",
                "max_iter": 5000,
                "tol": 0.0001,
                "random_state": 42,
            },
        },
    }


def paper1_pia_contract() -> dict[str, object]:
    """Return the fixed canonical PIA packet, evaluation, and control contract."""

    return {
        "packet_schema_version": 1,
        "attack": "pia",
        "variant": "pia",
        "excluded_variant": "PIAN",
        "timestep": 200,
        "lp_order": 4,
        "score_form": "negative_lp_norm",
        "score_direction": "higher_is_member",
        "input_range": [-1.0, 1.0],
        "query_timesteps": [0, 200],
        "query_count_per_batch": 2,
        "normalization": "per_row_vector_lp",
        "beta_semantics": "linear_1000_steps_inclusive_0.0001_to_0.02",
        "packet_purposes": ["corrected_evaluation", "cpu_positive_control"],
        "noise_id": {
            "random_noise": False,
            "derivation": "sha256_canonical_json_v1",
            "draw": "pia-e0",
            "fields": ["protocol_hash", "dataset_index", "timestep", "draw"],
        },
        "threshold_calibration": (
            "calibration_only_maximize_balanced_accuracy_then_minimize_fpr_then_highest_threshold"
        ),
        "reporting": {
            "primary_endpoint": "held_out_fixed_direction_auc",
            "secondary_endpoint": "tpr_at_1pct_fpr_with_wilson_95_ci",
            "forbidden_endpoint": "tpr_at_0.1pct_fpr",
        },
        "positive_control_gate": {
            "calibration_member_count": 128,
            "calibration_nonmember_count": 128,
            "evaluation_member_count": 128,
            "evaluation_nonmember_count": 128,
            "evaluation_auc_min": 0.95,
            "evaluation_balanced_accuracy_min": 0.90,
            "evaluation_fpr_max": 0.05,
            "negative_score_auc_max": 0.05,
            "zero_signal_auc_range": [0.45, 0.55],
            "permutations": 200,
            "permutation_random_state": 20260712,
            "null_auc_mean_range": [0.45, 0.55],
            "positive_auc_exceeds_all_permutations": True,
        },
        "validation_status": "synthetic_checkpoint_positive_control_required",
    }


def _paper1_pia_contract() -> dict[str, object]:
    return paper1_pia_contract()


def _paper1_common_noise_contract() -> dict[str, object]:
    return {
        "namespace": _PAPER1_COMMON_NOISE_NAMESPACE,
        "algorithm": "diffaudit-common-noise-seed-v1",
        "timesteps": [100, 400, 700],
        "draws": [0],
    }


def _paper1_branch_rules() -> dict[str, object]:
    return {
        "STOP": {
            "first_stage_target_count": 4,
            "attacks": ["H1", "PIA"],
            "all_auc_95pct_upper_bounds_below": 0.55,
        },
        "REPLICATE": {
            "first_stage_target_count": 4,
            "same_attack_minimum_target_count": 2,
            "auc_point_estimate_at_least": 0.55,
            "auc_95pct_lower_bound_above": 0.50,
            "full_label_permutation_null_calibrated": True,
            "minimum_full_label_permutations": 200,
            "target_steps": 100_000,
        },
        "MATURE": {
            "condition": "not_STOP_and_not_REPLICATE",
            "target_count": 4,
            "target_steps": 200_000,
        },
    }


def _paper1_confirmatory_heterogeneity() -> dict[str, object]:
    return {
        "global_test_alpha": 0.05,
        "practical_auc_range_at_least": 0.05,
        "global_statistic": "auc_range",
        "global_null": "paired_stratified_refit_bootstrap_null_centering",
        "pairwise_test": "two_sided_centered_paired_bootstrap",
        "pairwise_correction": "holm",
        "report_all_pairwise_deltas": True,
    }


def validate_paper1_protocol_envelope(
    source: Mapping[str, object] | str | Path,
    *,
    expected_protocol_hash: str,
) -> dict[str, object]:
    """Validate the complete Paper 1 envelope against an external trusted hash."""

    if (
        not isinstance(expected_protocol_hash, str)
        or _SHA256_PATTERN.fullmatch(expected_protocol_hash) is None
    ):
        raise ValueError("expected_protocol_hash must be 64 lowercase hex characters")
    loaded = load_protocol_envelope(source)
    if loaded["protocol_hash"] != expected_protocol_hash:
        raise ValueError("sealed protocol hash does not match trusted expected_protocol_hash")
    contract = loaded["contract"]
    if not isinstance(contract, dict) or set(contract) != _PAPER1_CONTRACT_FIELDS:
        raise ValueError("Paper 1 contract top-level fields do not match the fixed shape")
    _require_exact_json_value(
        "protocol_namespace", contract["protocol_namespace"], _PAPER1_PROTOCOL_NAMESPACE
    )

    dataset = contract["dataset"]
    if not isinstance(dataset, dict) or set(dataset) != {"name", "size", "split"}:
        raise ValueError("Paper 1 dataset does not match the fixed contract")
    _require_exact_json_value("dataset.name", dataset["name"], "CIFAR10")
    _require_exact_json_value("dataset.size", dataset["size"], 50_000)
    split = dataset["split"]
    if not isinstance(split, dict) or set(split) != {
        "filename",
        "sha256",
        "member_count",
        "nonmember_count",
    }:
        raise ValueError("Paper 1 dataset split does not match the fixed contract")
    _validate_split_filename(split["filename"])
    if not isinstance(split["sha256"], str) or _SHA256_PATTERN.fullmatch(split["sha256"]) is None:
        raise ValueError("Paper 1 dataset split sha256 must be 64 lowercase hex characters")
    _require_exact_json_value("dataset.split.member_count", split["member_count"], 25_000)
    _require_exact_json_value("dataset.split.nonmember_count", split["nonmember_count"], 25_000)

    training_config = build_training_config()
    expected_training = {
        "seeds": list(derive_training_seeds(_PAPER1_PROTOCOL_NAMESPACE)),
        "batch_size": training_config.data["batch_size"],
        "interim_steps": 100_000,
        "mature_steps": 200_000,
        "deterministic": True,
        "member_only": True,
        "training_config": training_config.to_dict(),
        "training_config_hash": canonical_training_config_hash(training_config),
    }
    _require_exact_json_value("training", contract["training"], expected_training)
    evaluation = contract["evaluation"]
    if not isinstance(evaluation, dict) or set(evaluation) != {"rows"}:
        raise ValueError("Paper 1 evaluation does not match the fixed contract")
    _validate_paper1_rows(evaluation["rows"])

    _require_exact_json_value("h1", contract["h1"], _paper1_h1_contract())
    _require_exact_json_value("pia", contract["pia"], paper1_pia_contract())
    _require_exact_json_value(
        "common_noise", contract["common_noise"], _paper1_common_noise_contract()
    )
    _require_exact_json_value("branch_rules", contract["branch_rules"], _paper1_branch_rules())
    _require_exact_json_value(
        "confirmatory_heterogeneity",
        contract["confirmatory_heterogeneity"],
        _paper1_confirmatory_heterogeneity(),
    )
    code_commit = contract["code_commit"]
    if not isinstance(code_commit, str) or _GIT_COMMIT_PATTERN.fullmatch(code_commit) is None:
        raise ValueError("Paper 1 code_commit must be 40 lowercase hex characters")
    return loaded


def _validate_split_filename(split_filename: object) -> str:
    if (
        not isinstance(split_filename, str)
        or not split_filename
        or PurePosixPath(split_filename).name != split_filename
        or PureWindowsPath(split_filename).name != split_filename
    ):
        raise ValueError("split_filename must be a public-safe filename")
    _reject_absolute_paths(split_filename)
    return split_filename


def _validate_paper1_partition(
    member_indices: Sequence[int],
    nonmember_indices: Sequence[int],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    member = _validated_indices("member", member_indices)
    nonmember = _validated_indices("nonmember", nonmember_indices)
    if (
        len(member) != 25_000
        or len(nonmember) != 25_000
        or len(set(member)) != 25_000
        or len(set(nonmember)) != 25_000
        or set(member).isdisjoint(nonmember) is False
        or set(member) | set(nonmember) != set(range(50_000))
    ):
        raise ValueError("membership split must be a complete 25000/25000 partition of 0..49999")
    return member, nonmember


def build_paper1_corrected_contract(
    *,
    split_filename: str,
    split_sha256: str,
    member_indices: Sequence[int],
    nonmember_indices: Sequence[int],
    class_labels: Sequence[int],
    code_commit: str,
) -> dict[str, object]:
    """Build the fixed, timestamp-free Paper 1 corrected-evidence contract."""

    split_filename = _validate_split_filename(split_filename)
    if not isinstance(split_sha256, str) or _SHA256_PATTERN.fullmatch(split_sha256) is None:
        raise ValueError("split_sha256 must be 64 lowercase hex characters")
    if not isinstance(code_commit, str) or _GIT_COMMIT_PATTERN.fullmatch(code_commit) is None:
        raise ValueError("code_commit must be 40 lowercase hex characters")
    member, nonmember = _validate_paper1_partition(member_indices, nonmember_indices)

    labels = np.asarray(class_labels)
    if labels.ndim != 1 or labels.size != 50_000:
        raise ValueError("class_labels must contain exactly 50000 CIFAR10 train labels")
    rows = build_paper1_corrected_row_manifest(
        member,
        nonmember,
        labels,
        random_state=_PAPER1_ROW_RANDOM_STATE,
    )
    row_payload = [
        {
            "dataset_index": row.dataset_index,
            "label": row.label,
            "class_id": row.class_id,
            "split": row.split,
        }
        for row in rows
    ]
    training_seeds = list(derive_training_seeds(_PAPER1_PROTOCOL_NAMESPACE))
    training_config = build_training_config()
    contract = {
        "protocol_namespace": _PAPER1_PROTOCOL_NAMESPACE,
        "dataset": {
            "name": "CIFAR10",
            "size": 50_000,
            "split": {
                "filename": split_filename,
                "sha256": split_sha256,
                "member_count": 25_000,
                "nonmember_count": 25_000,
            },
        },
        "training": {
            "seeds": training_seeds,
            "batch_size": training_config.data["batch_size"],
            "interim_steps": 100_000,
            "mature_steps": 200_000,
            "deterministic": True,
            "member_only": True,
            "training_config": training_config.to_dict(),
            "training_config_hash": canonical_training_config_hash(training_config),
        },
        "evaluation": {"rows": row_payload},
        "h1": _paper1_h1_contract(),
        "pia": _paper1_pia_contract(),
        "common_noise": _paper1_common_noise_contract(),
        "branch_rules": _paper1_branch_rules(),
        "confirmatory_heterogeneity": _paper1_confirmatory_heterogeneity(),
        "code_commit": code_commit,
    }
    copied_contract = _json_safe_copy(contract, name="Paper 1 contract")
    if not isinstance(copied_contract, dict):
        raise ValueError("Paper 1 contract must be a JSON mapping")
    return copied_contract


def _validate_paper1_rows(value: object) -> None:
    if not isinstance(value, list) or len(value) != 2048:
        raise ValueError("Paper 1 evaluation rows must contain exactly 2048 rows")

    seen_indices: set[int] = set()
    group_class_counts: dict[tuple[int, str], dict[int, int]] = {
        (label, split): {class_id: 0 for class_id in _CLASS_IDS}
        for label in (0, 1)
        for split in ("calibration", "evaluation")
    }
    row_fields = {"dataset_index", "label", "class_id", "split"}
    for row in value:
        if not isinstance(row, dict) or set(row) != row_fields:
            raise ValueError("Paper 1 evaluation rows have invalid fields")
        dataset_index = row["dataset_index"]
        label = row["label"]
        class_id = row["class_id"]
        split = row["split"]
        if (
            type(dataset_index) is not int
            or not 0 <= dataset_index < 50_000
            or dataset_index in seen_indices
            or type(label) is not int
            or label not in (0, 1)
            or type(class_id) is not int
            or class_id not in _CLASS_IDS
            or not isinstance(split, str)
            or split not in ("calibration", "evaluation")
        ):
            raise ValueError("Paper 1 evaluation rows have invalid row identity")
        seen_indices.add(dataset_index)
        group_class_counts[(label, split)][class_id] += 1

    for split in ("calibration", "evaluation"):
        membership_vectors = []
        for label in (0, 1):
            vector = tuple(group_class_counts[(label, split)].values())
            if sum(vector) != 512 or max(vector) - min(vector) > 1:
                raise ValueError("Paper 1 evaluation rows are not class-balanced 512-row groups")
            membership_vectors.append(vector)
        if membership_vectors[0] != membership_vectors[1]:
            raise ValueError("Paper 1 evaluation rows are not membership-balanced by class")


def verify_paper1_contract(
    envelope: Mapping[str, object] | str | Path,
    *,
    split_path: str | Path,
    class_labels: Sequence[int],
    expected_code_commit: str,
) -> dict[str, object]:
    """Verify the hash seal and rebuild every field from external source truth."""

    loaded = load_protocol_envelope(envelope)
    if (
        not isinstance(expected_code_commit, str)
        or _GIT_COMMIT_PATTERN.fullmatch(expected_code_commit) is None
    ):
        raise ValueError("expected_code_commit must be 40 lowercase hex characters")
    contract = loaded["contract"]
    if not isinstance(contract, dict) or set(contract) != _PAPER1_CONTRACT_FIELDS:
        raise ValueError("Paper 1 contract top-level fields do not match the fixed shape")
    _require_exact_json_value(
        "protocol_namespace", contract["protocol_namespace"], _PAPER1_PROTOCOL_NAMESPACE
    )

    dataset = contract["dataset"]
    if not isinstance(dataset, dict) or set(dataset) != {"name", "size", "split"}:
        raise ValueError("Paper 1 dataset does not match the fixed contract")
    _require_exact_json_value("dataset.name", dataset["name"], "CIFAR10")
    _require_exact_json_value("dataset.size", dataset["size"], 50_000)
    split = dataset["split"]
    if not isinstance(split, dict) or set(split) != {
        "filename",
        "sha256",
        "member_count",
        "nonmember_count",
    }:
        raise ValueError("Paper 1 dataset split does not match the fixed contract")
    _validate_split_filename(split["filename"])
    if not isinstance(split["sha256"], str) or _SHA256_PATTERN.fullmatch(split["sha256"]) is None:
        raise ValueError("Paper 1 dataset split sha256 must be 64 lowercase hex characters")
    _require_exact_json_value("dataset.split.member_count", split["member_count"], 25_000)
    _require_exact_json_value("dataset.split.nonmember_count", split["nonmember_count"], 25_000)

    training = contract["training"]
    training_config = build_training_config()
    expected_training = {
        "seeds": list(derive_training_seeds(_PAPER1_PROTOCOL_NAMESPACE)),
        "batch_size": training_config.data["batch_size"],
        "interim_steps": 100_000,
        "mature_steps": 200_000,
        "deterministic": True,
        "member_only": True,
        "training_config": training_config.to_dict(),
        "training_config_hash": canonical_training_config_hash(training_config),
    }
    if not isinstance(training, dict):
        raise ValueError("Paper 1 training does not match the fixed contract")
    seeds = training.get("seeds")
    if (
        not isinstance(seeds, list)
        or len(seeds) != 8
        or any(type(seed) is not int or not 0 < seed < 2**31 for seed in seeds)
        or len(set(seeds)) != 8
    ):
        raise ValueError("Paper 1 training seeds must be eight unique positive 31-bit integers")
    _require_exact_json_value("training seeds", seeds, expected_training["seeds"])
    _require_exact_json_value("training", training, expected_training)

    evaluation = contract["evaluation"]
    if not isinstance(evaluation, dict) or set(evaluation) != {"rows"}:
        raise ValueError("Paper 1 evaluation does not match the fixed contract")
    _validate_paper1_rows(evaluation["rows"])

    _require_exact_json_value("h1", contract["h1"], _paper1_h1_contract())
    _require_exact_json_value("pia", contract["pia"], _paper1_pia_contract())
    _require_exact_json_value(
        "common_noise", contract["common_noise"], _paper1_common_noise_contract()
    )
    _require_exact_json_value("branch_rules", contract["branch_rules"], _paper1_branch_rules())
    _require_exact_json_value(
        "confirmatory_heterogeneity",
        contract["confirmatory_heterogeneity"],
        _paper1_confirmatory_heterogeneity(),
    )
    code_commit = contract["code_commit"]
    if not isinstance(code_commit, str) or _GIT_COMMIT_PATTERN.fullmatch(code_commit) is None:
        raise ValueError("Paper 1 code_commit must be 40 lowercase hex characters")
    if code_commit != expected_code_commit:
        raise ValueError("Paper 1 code_commit does not match expected_code_commit")

    source_split_path = Path(split_path)
    if split["filename"] != source_split_path.name:
        raise ValueError("Paper 1 split filename does not match source truth")
    source_split_sha256 = hashlib.sha256(source_split_path.read_bytes()).hexdigest()
    if split["sha256"] != source_split_sha256:
        raise ValueError("Paper 1 split sha256 does not match source truth")
    source_split = load_member_nonmember_indices(source_split_path, dataset_size=50_000)
    member_indices, nonmember_indices = _validate_paper1_partition(
        source_split.member_indices,
        source_split.nonmember_indices,
    )
    expected_contract = build_paper1_corrected_contract(
        split_filename=source_split_path.name,
        split_sha256=source_split_sha256,
        member_indices=member_indices,
        nonmember_indices=nonmember_indices,
        class_labels=class_labels,
        code_commit=expected_code_commit,
    )
    _require_exact_json_value("contract source truth", contract, expected_contract)

    copied_contract = _json_safe_copy(contract, name="Paper 1 contract")
    if not isinstance(copied_contract, dict):
        raise ValueError("Paper 1 contract must be a JSON mapping")
    return copied_contract
