"""Corrected-evidence protocol primitives for Paper 1."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations
from numbers import Integral
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Literal

import numpy as np

_SPLIT_FILENAMES = {"cifar10": "CIFAR10_train_ratio0.5.npz"}
_CLASS_IDS = tuple(range(10))


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
