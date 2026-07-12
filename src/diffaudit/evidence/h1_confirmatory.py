"""CPU-only confirmatory H1 scoring over row-bound feature packets."""

from __future__ import annotations

import hashlib
import json
import math
import re
import time
import warnings
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from importlib.metadata import version
from itertools import combinations
from statistics import NormalDist
from typing import Any

import numpy as np
from sklearn.decomposition import PCA
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression

from diffaudit.utils.metrics import auc_score, tpr_at_fpr

_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
_GIT_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
_SPLITS = ("calibration", "evaluation")
_CLASS_IDS = tuple(range(10))
_REQUIRED_ROW_FIELDS = {
    "dataset_index",
    "label",
    "class",
    "calibration_or_evaluation",
    "noise_id",
}
_PACKET_FIELDS = {
    "schema_version",
    "packet_format",
    "packet_purpose",
    "provenance",
    "rows",
    "pca_features",
    "scalar_features",
}
_PACKET_PROVENANCE_FIELDS = {
    "dataset_id",
    "run_seed",
    "step",
    "attack",
    "checkpoint_sha256",
    "training_manifest_sha256",
    "target_code_commit",
    "scorer_code_commit",
    "split_sha256",
    "protocol_hash",
    "run_label",
}
_CHECKPOINT_PROVENANCE_FIELDS = (
    "dataset_id",
    "run_seed",
    "step",
    "attack",
    "checkpoint_sha256",
    "training_manifest_sha256",
    "target_code_commit",
    "scorer_code_commit",
    "split_sha256",
    "protocol_hash",
    "run_label",
)
_LOCKED_ROW_FIELDS = (
    "dataset_index",
    "label",
    "class",
    "calibration_or_evaluation",
    "noise_id",
)


def h1_scorer_contract() -> dict[str, object]:
    """Return a detached copy of the H1 fit contract sealed by Paper 1 protocols."""

    from diffaudit.evidence.corrected_protocol import _paper1_h1_contract

    return json.loads(json.dumps(_paper1_h1_contract(), allow_nan=False))


def _require_exact_value(name: str, actual: object, expected: object) -> None:
    if type(actual) is not type(expected):
        raise ValueError(f"{name} does not match the fixed H1 scorer contract")
    if isinstance(expected, dict):
        if set(actual) != set(expected):
            raise ValueError(f"{name} does not match the fixed H1 scorer contract")
        for key, value in expected.items():
            _require_exact_value(f"{name}.{key}", actual[key], value)
        return
    if isinstance(expected, list):
        if len(actual) != len(expected):
            raise ValueError(f"{name} does not match the fixed H1 scorer contract")
        for index, (actual_value, expected_value) in enumerate(zip(actual, expected, strict=True)):
            _require_exact_value(f"{name}[{index}]", actual_value, expected_value)
        return
    if actual != expected:
        raise ValueError(f"{name} does not match the fixed H1 scorer contract")


def _validate_h1_contract(value: object) -> dict[str, object]:
    expected = h1_scorer_contract()
    _require_exact_value("protocol h1", value, expected)
    return expected


@dataclass(frozen=True, slots=True)
class _ProtocolContext:
    protocol_hash: str
    h1_contract: dict[str, object]
    dataset_id: str
    split_sha256: str
    code_commit: str
    manifest_rows: dict[int, tuple[int, int, str]]
    allowed_run_seeds: frozenset[int]
    allowed_steps: frozenset[int]
    common_noise_namespace: str
    common_noise_timesteps: tuple[int, ...]
    common_noise_draws: tuple[int, ...]
    heterogeneity_contract: dict[str, object]


@dataclass(frozen=True, slots=True)
class _FeatureRow:
    provenance: dict[str, object]


@dataclass(frozen=True, slots=True)
class _FeaturePacket:
    rows: tuple[_FeatureRow, ...]
    pca_features: np.ndarray
    scalar_features: np.ndarray
    labels: np.ndarray
    classes: np.ndarray
    split_values: tuple[str, ...]
    calibration_indices: np.ndarray
    evaluation_indices: np.ndarray
    target_provenance: dict[str, object]
    packet_purpose: str


@dataclass(slots=True)
class H1FittedModel:
    """A fitted PCA and membership classifier; no evaluation data is retained."""

    pca: PCA
    classifier: LogisticRegression
    sklearn_version: str
    realized_logistic_regression: dict[str, object]

    def predict_scores(self, pca_features: np.ndarray, scalar_features: np.ndarray) -> np.ndarray:
        transformed = self.pca.transform(np.asarray(pca_features, dtype=float))
        matrix = _assemble_h1_lr_features(transformed, scalar_features)
        member_column = int(np.flatnonzero(self.classifier.classes_ == 1)[0])
        return np.asarray(self.classifier.predict_proba(matrix)[:, member_column], dtype=float)


def _assemble_h1_lr_features(
    pca_components: np.ndarray,
    scalar_features: np.ndarray,
) -> np.ndarray:
    """Assemble the frozen legacy LR column order: scalar summaries, then PCA."""

    pca_matrix = np.asarray(pca_components, dtype=float)
    scalar_matrix = np.asarray(scalar_features, dtype=float)
    if pca_matrix.ndim != 2 or scalar_matrix.ndim != 2:
        raise ValueError("H1 LR feature blocks must be two-dimensional")
    if pca_matrix.shape[0] != scalar_matrix.shape[0]:
        raise ValueError("H1 LR feature blocks must have the same row count")
    return np.concatenate([scalar_matrix, pca_matrix], axis=1)


def _validate_protocol_envelope(
    protocol_envelope: Mapping[str, object],
    *,
    expected_protocol_hash: str,
) -> _ProtocolContext:
    from diffaudit.evidence.corrected_protocol import (
        _PAPER1_CONTRACT_FIELDS,
        _PAPER1_PROTOCOL_NAMESPACE,
        _paper1_branch_rules,
        _paper1_common_noise_contract,
        _paper1_confirmatory_heterogeneity,
        _paper1_pia_contract,
        _require_exact_json_value,
        _validate_split_filename,
        derive_training_seeds,
        load_protocol_envelope,
    )
    from diffaudit.evidence.training_config import (
        build_training_config,
        canonical_training_config_hash,
    )

    _require_hash("expected_protocol_hash", expected_protocol_hash, _SHA256_PATTERN)
    loaded = load_protocol_envelope(protocol_envelope)
    if loaded["protocol_hash"] != expected_protocol_hash:
        raise ValueError("sealed protocol hash does not match trusted expected_protocol_hash")
    contract = loaded["contract"]
    if not isinstance(contract, dict) or set(contract) != _PAPER1_CONTRACT_FIELDS:
        raise ValueError("protocol top-level fields do not match the full Paper 1 contract")
    _require_exact_json_value(
        "protocol_namespace", contract["protocol_namespace"], _PAPER1_PROTOCOL_NAMESPACE
    )
    h1_contract = _validate_h1_contract(contract.get("h1"))

    code_commit = contract.get("code_commit")
    if not isinstance(code_commit, str) or _GIT_COMMIT_PATTERN.fullmatch(code_commit) is None:
        raise ValueError("protocol code_commit must be 40 lowercase hex characters")
    dataset = contract.get("dataset")
    if not isinstance(dataset, dict) or set(dataset) != {"name", "size", "split"}:
        raise ValueError("protocol dataset fields do not match the fixed contract")
    _require_exact_json_value("dataset.name", dataset["name"], "CIFAR10")
    _require_exact_json_value("dataset.size", dataset["size"], 50_000)
    dataset_id = dataset["name"]
    split = dataset.get("split")
    if not isinstance(split, dict) or set(split) != {
        "filename",
        "sha256",
        "member_count",
        "nonmember_count",
    }:
        raise ValueError("protocol dataset.split fields do not match the fixed contract")
    _validate_split_filename(split["filename"])
    split_sha256 = split.get("sha256")
    if not isinstance(split_sha256, str) or _SHA256_PATTERN.fullmatch(split_sha256) is None:
        raise ValueError("protocol split sha256 must be 64 lowercase hex characters")
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
    training = contract.get("training")
    _require_exact_json_value("training", training, expected_training)
    if not isinstance(training, dict):
        raise ValueError("protocol training must be a mapping")

    _require_exact_json_value("pia", contract["pia"], _paper1_pia_contract())
    common_noise = _paper1_common_noise_contract()
    _require_exact_json_value("common_noise", contract["common_noise"], common_noise)
    _require_exact_json_value("branch_rules", contract["branch_rules"], _paper1_branch_rules())
    heterogeneity_contract = _paper1_confirmatory_heterogeneity()
    _require_exact_json_value(
        "confirmatory_heterogeneity",
        contract["confirmatory_heterogeneity"],
        heterogeneity_contract,
    )

    evaluation = contract.get("evaluation")
    raw_manifest = evaluation.get("rows") if isinstance(evaluation, dict) else None
    if not isinstance(raw_manifest, list) or len(raw_manifest) != 2048:
        raise ValueError("protocol evaluation.rows must contain exactly 2048 locked rows")
    manifest_rows: dict[int, tuple[int, int, str]] = {}
    for raw_row in raw_manifest:
        if not isinstance(raw_row, dict) or set(raw_row) != {
            "dataset_index",
            "label",
            "class_id",
            "split",
        }:
            raise ValueError("protocol evaluation row fields are invalid")
        dataset_index = raw_row["dataset_index"]
        label = raw_row["label"]
        class_id = raw_row["class_id"]
        row_split = raw_row["split"]
        if (
            type(dataset_index) is not int
            or dataset_index < 0
            or dataset_index in manifest_rows
            or type(label) is not int
            or label not in (0, 1)
            or type(class_id) is not int
            or class_id not in _CLASS_IDS
            or row_split not in _SPLITS
        ):
            raise ValueError("protocol evaluation row identity is invalid")
        manifest_rows[dataset_index] = (label, class_id, row_split)

    protocol_hash = loaded["protocol_hash"]
    if not isinstance(protocol_hash, str):
        raise ValueError("protocol hash must be a string")
    return _ProtocolContext(
        protocol_hash=protocol_hash,
        h1_contract=h1_contract,
        dataset_id=dataset_id,
        split_sha256=split_sha256,
        code_commit=code_commit,
        manifest_rows=manifest_rows,
        allowed_run_seeds=frozenset(int(seed) for seed in training["seeds"]),
        allowed_steps=frozenset((int(training["interim_steps"]), int(training["mature_steps"]))),
        common_noise_namespace=str(common_noise["namespace"]),
        common_noise_timesteps=tuple(int(value) for value in common_noise["timesteps"]),
        common_noise_draws=tuple(int(value) for value in common_noise["draws"]),
        heterogeneity_contract=heterogeneity_contract,
    )


def _require_hash(name: str, value: object, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        length = 64 if pattern is _SHA256_PATTERN else 40
        raise ValueError(f"{name} must be {length} lowercase hex characters")
    return value


def _parse_feature_matrix(
    name: str,
    value: object,
    *,
    row_count: int,
    feature_count: int,
) -> np.ndarray:
    matrix = np.asarray(value)
    if matrix.shape != (row_count, feature_count):
        raise ValueError(f"{name} shape does not match the frozen H1 feature definition")
    if matrix.dtype != np.float32:
        raise ValueError(f"{name} dtype must be float32")
    if not np.isfinite(matrix).all():
        raise ValueError(f"{name} must contain only finite values")
    return matrix


def _validate_row(raw_row: object) -> _FeatureRow:
    if not isinstance(raw_row, Mapping):
        raise ValueError("each packet row must be a JSON mapping")
    if set(raw_row) != _REQUIRED_ROW_FIELDS:
        raise ValueError("packet row fields must exactly match the H1 row schema")

    dataset_index = raw_row["dataset_index"]
    if type(dataset_index) is not int or dataset_index < 0:
        raise ValueError("dataset_index must be a non-negative integer")
    label = raw_row["label"]
    if type(label) is not int or label not in (0, 1):
        raise ValueError("label must be integer 0 or 1 membership")
    class_id = raw_row["class"]
    if type(class_id) is not int or class_id not in _CLASS_IDS:
        raise ValueError("class must be an integer in range 0..9, separate from membership label")
    split = raw_row["calibration_or_evaluation"]
    if not isinstance(split, str) or split not in _SPLITS:
        raise ValueError("calibration_or_evaluation must be calibration or evaluation")
    if not isinstance(raw_row["noise_id"], Mapping):
        raise ValueError("noise_id must be the canonical common-noise mapping")

    try:
        json.dumps(raw_row, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError("packet rows must be finite JSON-safe structures") from error
    return _FeatureRow(provenance={field: raw_row[field] for field in _REQUIRED_ROW_FIELDS})


def _canonical_row_key(row: _FeatureRow) -> tuple[int, int, int, int]:
    provenance = row.provenance
    split_order = 0 if provenance["calibration_or_evaluation"] == "calibration" else 1
    return (
        split_order,
        int(provenance["label"]),
        int(provenance["class"]),
        int(provenance["dataset_index"]),
    )


def _canonical_noise_id(context: _ProtocolContext, dataset_index: int) -> dict[str, object]:
    from diffaudit.evidence.corrected_protocol import derive_noise_seed

    return {
        "namespace": context.common_noise_namespace,
        "dataset_index": dataset_index,
        "entries": [
            {
                "timestep": timestep,
                "draw": draw,
                "seed": derive_noise_seed(
                    context.common_noise_namespace,
                    dataset_index,
                    timestep,
                    draw,
                ),
            }
            for timestep in context.common_noise_timesteps
            for draw in context.common_noise_draws
        ],
    }


def _validate_cell_balance(rows: Sequence[_FeatureRow]) -> None:
    for split in _SPLITS:
        membership_vectors: list[tuple[int, ...]] = []
        for label in (0, 1):
            vector = tuple(
                sum(
                    row.provenance["calibration_or_evaluation"] == split
                    and row.provenance["label"] == label
                    and row.provenance["class"] == class_id
                    for row in rows
                )
                for class_id in _CLASS_IDS
            )
            if sum(vector) != 512:
                raise ValueError(f"{split} must contain exactly 512 rows for membership {label}")
            if max(vector) - min(vector) > 1:
                raise ValueError(f"{split} membership cells must be CIFAR10 class-balanced")
            membership_vectors.append(vector)
        if membership_vectors[0] != membership_vectors[1]:
            raise ValueError(f"{split} membership cells must be CIFAR10 class-balanced")


def _validate_one_packet(
    raw_packet: object,
    *,
    context: _ProtocolContext,
) -> _FeaturePacket:
    if not isinstance(raw_packet, Mapping) or set(raw_packet) != _PACKET_FIELDS:
        raise ValueError("feature packet fields must exactly match h1-feature-packet-v2")
    if raw_packet["schema_version"] != 1 or raw_packet["packet_format"] != "h1-feature-packet-v2":
        raise ValueError("feature packet schema version or format is invalid")
    packet_purpose = raw_packet["packet_purpose"]
    if packet_purpose not in context.h1_contract["packet_purposes"]:
        raise ValueError("feature packet purpose is not allowed by the sealed H1 contract")
    provenance = raw_packet["provenance"]
    if not isinstance(provenance, Mapping) or set(provenance) != _PACKET_PROVENANCE_FIELDS:
        raise ValueError("feature packet provenance fields do not match the exact schema")
    if provenance["attack"] != "H1":
        raise ValueError("packet attack must be H1")
    if not isinstance(provenance["dataset_id"], str) or not provenance["dataset_id"]:
        raise ValueError("packet dataset_id must be a non-empty string")
    for name in ("run_seed", "step"):
        value = provenance[name]
        if type(value) is not int or value <= 0:
            raise ValueError(f"packet {name} must be a positive integer")
    for name in (
        "checkpoint_sha256",
        "training_manifest_sha256",
        "split_sha256",
        "protocol_hash",
    ):
        _require_hash(name, provenance[name], _SHA256_PATTERN)
    for name in ("target_code_commit", "scorer_code_commit"):
        _require_hash(name, provenance[name], _GIT_COMMIT_PATTERN)
    if not isinstance(provenance["run_label"], str) or not provenance["run_label"]:
        raise ValueError("packet run_label must be a non-empty string")
    raw_rows = raw_packet["rows"]
    if not isinstance(raw_rows, list) or len(raw_rows) != 2048:
        raise ValueError("each feature packet must contain exactly 2048 rows")
    rows = [_validate_row(row) for row in raw_rows]
    definition = context.h1_contract["feature_definition"]
    pca_features = _parse_feature_matrix(
        "pca_features",
        raw_packet["pca_features"],
        row_count=len(rows),
        feature_count=int(definition["pca_input_dimension"]),
    )
    scalar_features = _parse_feature_matrix(
        "scalar_features",
        raw_packet["scalar_features"],
        row_count=len(rows),
        feature_count=int(definition["scalar_feature_dimension"]),
    )

    identities: set[int] = set()
    for row in rows:
        identity = int(row.provenance["dataset_index"])
        if identity in identities:
            raise ValueError("duplicate row identity or calibration/evaluation overlap")
        identities.add(identity)
    _validate_cell_balance(rows)

    if provenance["protocol_hash"] != context.protocol_hash:
        raise ValueError("packet protocol_hash does not match the sealed protocol")
    if provenance["dataset_id"] != context.dataset_id:
        raise ValueError("packet dataset_id does not match the sealed protocol")
    if provenance["split_sha256"] != context.split_sha256:
        raise ValueError("packet split_sha256 does not match the sealed protocol")
    if provenance["target_code_commit"] != context.code_commit:
        raise ValueError("packet target_code_commit does not match the sealed protocol")
    if provenance["run_seed"] not in context.allowed_run_seeds:
        raise ValueError("run_seed is not allowed by the sealed protocol")
    if packet_purpose == "corrected_evaluation":
        if provenance["step"] not in context.allowed_steps:
            raise ValueError("corrected evaluation step is not allowed by the sealed protocol")
    elif provenance["step"] > 5000 or "corrected" not in provenance["run_label"]:
        raise ValueError("preflight packet requires a corrected label and step <= 5000")

    for row in rows:
        dataset_index = int(row.provenance["dataset_index"])
        expected = context.manifest_rows.get(dataset_index)
        actual = (
            row.provenance["label"],
            row.provenance["class"],
            row.provenance["calibration_or_evaluation"],
        )
        if expected != actual:
            raise ValueError("packet rows do not match locked protocol row provenance")
        expected_noise_id = _canonical_noise_id(context, dataset_index)
        if row.provenance["noise_id"] != expected_noise_id:
            raise ValueError("noise_id does not match the canonical common-noise derivation")
    if {int(row.provenance["dataset_index"]) for row in rows} != set(context.manifest_rows):
        raise ValueError("packet rows do not match the complete locked protocol row set")
    try:
        json.dumps({"provenance": provenance, "rows": raw_rows}, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError("packet manifest must be a finite JSON-safe structure") from error

    order = sorted(range(len(rows)), key=lambda index: _canonical_row_key(rows[index]))
    sorted_rows = tuple(rows[index] for index in order)
    pca_features = pca_features[order]
    scalar_features = scalar_features[order]
    labels = np.asarray([row.provenance["label"] for row in sorted_rows], dtype=int)
    classes = np.asarray([row.provenance["class"] for row in sorted_rows], dtype=int)
    split_values = tuple(str(row.provenance["calibration_or_evaluation"]) for row in sorted_rows)
    calibration_indices = np.asarray(
        [index for index, split in enumerate(split_values) if split == "calibration"],
        dtype=int,
    )
    evaluation_indices = np.asarray(
        [index for index, split in enumerate(split_values) if split == "evaluation"],
        dtype=int,
    )
    return _FeaturePacket(
        rows=sorted_rows,
        pca_features=pca_features,
        scalar_features=scalar_features,
        labels=labels,
        classes=classes,
        split_values=split_values,
        calibration_indices=calibration_indices,
        evaluation_indices=evaluation_indices,
        target_provenance=dict(provenance),
        packet_purpose=str(packet_purpose),
    )


def _locked_row_signature(row: _FeatureRow) -> tuple[object, ...]:
    return tuple(row.provenance[field] for field in _LOCKED_ROW_FIELDS)


def _validate_packets(
    packets: Sequence[Mapping[str, object] | str | Any],
    *,
    protocol_envelope: Mapping[str, object],
    expected_protocol_hash: str,
    require_corrected_evaluation: bool,
) -> tuple[_ProtocolContext, tuple[_FeaturePacket, ...]]:
    if not isinstance(packets, Sequence) or isinstance(packets, (str, bytes)) or not packets:
        raise ValueError("at least one feature packet is required")
    context = _validate_protocol_envelope(
        protocol_envelope,
        expected_protocol_hash=expected_protocol_hash,
    )
    from diffaudit.evidence.h1_extraction import load_h1_feature_packet

    loaded_packets = tuple(
        packet if isinstance(packet, Mapping) else load_h1_feature_packet(packet)
        for packet in packets
    )
    validated = tuple(_validate_one_packet(packet, context=context) for packet in loaded_packets)
    if require_corrected_evaluation and any(
        packet.packet_purpose != "corrected_evaluation" for packet in validated
    ):
        raise ValueError("preflight_benchmark packets are forbidden for scientific H1 scoring")
    checkpoint_hashes = [str(packet.target_provenance["checkpoint_sha256"]) for packet in validated]
    if len(set(checkpoint_hashes)) != len(checkpoint_hashes):
        raise ValueError("checkpoint_sha256 must be unique across feature packets")

    reference = validated[0]
    for packet in validated[1:]:
        if len(packet.rows) != len(reference.rows) or any(
            _locked_row_signature(left) != _locked_row_signature(right)
            for left, right in zip(reference.rows, packet.rows, strict=True)
        ):
            raise ValueError("cross-packet provenance drift in locked row provenance")
        if packet.packet_purpose != reference.packet_purpose:
            raise ValueError("cross-packet purpose drift is forbidden")
        if (
            packet.target_provenance["scorer_code_commit"]
            != reference.target_provenance["scorer_code_commit"]
        ):
            raise ValueError("cross-packet scorer commit drift is forbidden")
    return context, validated


def validate_h1_feature_packets(
    packets: Sequence[Mapping[str, object]],
    *,
    protocol_envelope: Mapping[str, object],
    expected_protocol_hash: str,
) -> dict[str, object]:
    """Validate one or more production-sized packets without fitting a model."""

    context, validated = _validate_packets(
        packets,
        protocol_envelope=protocol_envelope,
        expected_protocol_hash=expected_protocol_hash,
        require_corrected_evaluation=False,
    )
    return {
        "protocol_hash": context.protocol_hash,
        "row_count_per_checkpoint": len(validated[0].rows),
        "pca_feature_dimension": int(validated[0].pca_features.shape[1]),
        "scalar_feature_dimension": int(validated[0].scalar_features.shape[1]),
        "checkpoint_sha256s": [
            packet.target_provenance["checkpoint_sha256"] for packet in validated
        ],
    }


def _fit_h1_arrays(
    pca_features: np.ndarray,
    scalar_features: np.ndarray,
    labels: np.ndarray,
    contract: dict[str, object],
) -> H1FittedModel:
    _validate_h1_contract(contract)
    pca_contract = contract["pca"]
    logistic_contract = contract["logistic_regression"]
    sklearn_version = version("scikit-learn")
    if sklearn_version != contract["sklearn_version"]:
        raise ValueError("installed scikit-learn version does not match the sealed protocol")
    pca = PCA(
        n_components=pca_contract["n_components"],
        svd_solver=pca_contract["svd_solver"],
        whiten=pca_contract["whiten"],
        random_state=pca_contract["random_state"],
        n_oversamples=pca_contract["n_oversamples"],
        iterated_power=pca_contract["iterated_power"],
        power_iteration_normalizer=pca_contract["power_iteration_normalizer"],
    )
    transformed = pca.fit_transform(np.asarray(pca_features, dtype=float))
    classifier_features = _assemble_h1_lr_features(transformed, scalar_features)
    expected_lr_dimension = int(contract["feature_definition"]["lr_input_dimension"])
    if classifier_features.shape[1] != expected_lr_dimension:
        raise ValueError("realized H1 LR input dimension does not match the frozen contract")
    classifier_kwargs: dict[str, Any] = dict(logistic_contract["constructor"])
    classifier = LogisticRegression(**classifier_kwargs)
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        classifier.fit(classifier_features, np.asarray(labels, dtype=int))
    if np.any(classifier.n_iter_ >= int(classifier_kwargs["max_iter"])):
        raise RuntimeError("LogisticRegression reached max_iter without confirmed convergence")
    params = classifier.get_params()
    realized = {
        key: params[key]
        for key in (
            "penalty",
            "dual",
            "l1_ratio",
            "C",
            "fit_intercept",
            "class_weight",
            "solver",
            "max_iter",
            "tol",
            "random_state",
        )
    }
    if (
        logistic_contract["logical_penalty"] != "l2"
        or realized["penalty"] not in ("l2", "deprecated")
        or realized["dual"] is not False
        or realized["l1_ratio"] != 0.0
    ):
        raise RuntimeError("realized LogisticRegression parameters do not implement logical L2")
    return H1FittedModel(
        pca=pca,
        classifier=classifier,
        sklearn_version=sklearn_version,
        realized_logistic_regression=realized,
    )


def fit_h1_model(
    packet: Mapping[str, object],
    *,
    protocol_envelope: Mapping[str, object],
    expected_protocol_hash: str,
) -> H1FittedModel:
    """Fit PCA/LR using calibration rows only."""

    context, packets = _validate_packets(
        [packet],
        protocol_envelope=protocol_envelope,
        expected_protocol_hash=expected_protocol_hash,
        require_corrected_evaluation=True,
    )
    validated = packets[0]
    indices = validated.calibration_indices
    return _fit_h1_arrays(
        validated.pca_features[indices],
        validated.scalar_features[indices],
        validated.labels[indices],
        context.h1_contract,
    )


def benchmark_h1_refit_runtime(
    packet: Mapping[str, object] | str,
    *,
    protocol_envelope: Mapping[str, object],
    expected_protocol_hash: str,
    fit_count: int,
) -> dict[str, object]:
    """Time repeated calibration-only H1 refits without computing any attack outcome."""

    if type(fit_count) is not int or fit_count <= 0:
        raise ValueError("fit_count must be a positive integer")
    context, packets = _validate_packets(
        [packet],
        protocol_envelope=protocol_envelope,
        expected_protocol_hash=expected_protocol_hash,
        require_corrected_evaluation=False,
    )
    validated = packets[0]
    calibration = validated.calibration_indices
    started = time.perf_counter()
    for _ in range(fit_count):
        _fit_h1_arrays(
            validated.pca_features[calibration],
            validated.scalar_features[calibration],
            validated.labels[calibration],
            context.h1_contract,
        )
    total_seconds = time.perf_counter() - started
    return {
        "fit_count": fit_count,
        "total_seconds": total_seconds,
        "seconds_per_fit": total_seconds / fit_count,
        "calibration_rows": int(calibration.size),
        "pca_input_dimension": int(validated.pca_features.shape[1]),
        "scalar_feature_dimension": int(validated.scalar_features.shape[1]),
    }


def wilson_interval(
    successes: int,
    total: int,
    *,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Return a two-sided Wilson score interval for a binomial proportion."""

    if type(successes) is not int or type(total) is not int:
        raise ValueError("successes and total must be integers")
    if total <= 0 or not 0 <= successes <= total:
        raise ValueError("Wilson counts must satisfy 0 <= successes <= total and total > 0")
    if type(confidence) is not float or not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be a float strictly between zero and one")
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    proportion = successes / total
    denominator = 1.0 + z * z / total
    center = (proportion + z * z / (2.0 * total)) / denominator
    radius = (
        z
        * math.sqrt(proportion * (1.0 - proportion) / total + z * z / (4.0 * total * total))
        / denominator
    )
    lower = max(0.0, center - radius)
    upper = min(1.0, center + radius)
    if successes == 0:
        lower = 0.0
    if successes == total:
        upper = 1.0
    return float(lower), float(upper)


def tpr_at_1pct_fpr_with_wilson(
    scores: np.ndarray,
    labels: np.ndarray,
) -> dict[str, object]:
    """Return max TPR where empirical FPR is at most 1%, plus Wilson 95% CI."""

    score_values = np.asarray(scores, dtype=float)
    label_values = np.asarray(labels, dtype=int)
    estimate = tpr_at_fpr(score_values, label_values, 0.01)
    positives = int((label_values == 1).sum())
    raw_successes = estimate * positives
    successes = int(round(raw_successes))
    if not math.isclose(raw_successes, successes, rel_tol=0.0, abs_tol=1e-9):
        raise RuntimeError("TPR helper returned a value that is not an exact empirical count")
    lower, upper = wilson_interval(successes, positives)
    return {
        "estimate": float(estimate),
        "wilson_95_ci": [lower, upper],
        "member_successes": successes,
        "member_total": positives,
        "fpr_cap": 0.01,
    }


def _evaluation_row_result(row: _FeatureRow, score: float) -> dict[str, object]:
    result = dict(row.provenance)
    result["score"] = float(score)
    return result


def _target_result(
    packet: _FeaturePacket,
    *,
    contract: dict[str, object],
) -> dict[str, object]:
    calibration = packet.calibration_indices
    evaluation = packet.evaluation_indices
    model = _fit_h1_arrays(
        packet.pca_features[calibration],
        packet.scalar_features[calibration],
        packet.labels[calibration],
        contract,
    )
    scores = model.predict_scores(
        packet.pca_features[evaluation], packet.scalar_features[evaluation]
    )
    labels = packet.labels[evaluation]
    tpr_metric = tpr_at_1pct_fpr_with_wilson(scores, labels)
    return {
        "target": dict(packet.target_provenance),
        "fit_provenance": {
            "sklearn_version": model.sklearn_version,
            "realized_logistic_regression": model.realized_logistic_regression,
        },
        "metrics": {
            "auc": float(auc_score(scores, labels)),
            "tpr_at_1pct_fpr": tpr_metric["estimate"],
            "tpr_at_1pct_fpr_wilson_95_ci": tpr_metric["wilson_95_ci"],
            "tpr_member_successes": tpr_metric["member_successes"],
            "tpr_member_total": tpr_metric["member_total"],
        },
        "evaluation_rows": [
            _evaluation_row_result(packet.rows[int(index)], score)
            for index, score in zip(evaluation, scores, strict=True)
        ],
    }


def _validate_cross_target_roster(
    packets: Sequence[_FeaturePacket],
    contract: Mapping[str, object],
    *,
    analysis_mode: str | None,
    stage: str | None,
) -> None:
    if len(packets) == 1 and analysis_mode is None and stage is None:
        return
    if analysis_mode != "cross_target_same_step":
        raise ValueError("multi-packet analysis_mode must be cross_target_same_step")
    rosters = contract["cross_target_rosters"]
    if stage not in rosters:
        raise ValueError("cross-target stage does not identify a sealed target roster")
    roster = rosters[stage]
    seeds = [int(packet.target_provenance["run_seed"]) for packet in packets]
    if len(set(seeds)) != len(seeds):
        raise ValueError("cross-target roster requires unique run_seed values")
    if set(seeds) != set(roster["seeds"]) or len(seeds) != len(roster["seeds"]):
        raise ValueError("cross-target roster does not exactly match the sealed stage roster")
    steps = {int(packet.target_provenance["step"]) for packet in packets}
    if steps != {int(roster["step"])}:
        raise ValueError("cross-target roster must use the exact sealed stage step")


def score_h1_checkpoints(
    packets: Sequence[Mapping[str, object]],
    *,
    protocol_envelope: Mapping[str, object],
    expected_protocol_hash: str,
    analysis_mode: str | None = None,
    stage: str | None = None,
) -> dict[str, object]:
    """Fit on calibration and report evaluation-only scores for every checkpoint."""

    context, validated = _validate_packets(
        packets,
        protocol_envelope=protocol_envelope,
        expected_protocol_hash=expected_protocol_hash,
        require_corrected_evaluation=True,
    )
    _validate_cross_target_roster(
        validated,
        context.h1_contract,
        analysis_mode=analysis_mode,
        stage=stage,
    )
    result = {
        "schema_version": 1,
        "protocol_hash": context.protocol_hash,
        "analysis_mode": analysis_mode or "single_checkpoint",
        "stage": stage,
        "scorer_contract": context.h1_contract,
        "score_direction": "higher_is_member",
        "targets": [_target_result(packet, contract=context.h1_contract) for packet in validated],
    }
    json.dumps(result, allow_nan=False)
    return result


def _draw_stratified_indices(
    packet: _FeaturePacket,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    draws: dict[str, list[np.ndarray]] = {split: [] for split in _SPLITS}
    for split in _SPLITS:
        split_mask = np.asarray([value == split for value in packet.split_values], dtype=bool)
        for label in (0, 1):
            for class_id in _CLASS_IDS:
                indices = np.flatnonzero(
                    split_mask & (packet.labels == label) & (packet.classes == class_id)
                )
                draws[split].append(rng.choice(indices, size=indices.size, replace=True))
    return (
        np.concatenate(draws["calibration"]).astype(int, copy=False),
        np.concatenate(draws["evaluation"]).astype(int, copy=False),
    )


def _percentile_interval(samples: Sequence[float]) -> list[float]:
    values = np.asarray(samples, dtype=float)
    return [float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))]


def _target_key(packet: _FeaturePacket) -> str:
    return str(packet.target_provenance["checkpoint_sha256"])


def summarize_h1_heterogeneity(
    target_keys: Sequence[str],
    observed_aucs: Sequence[float],
    bootstrap_auc_vectors: Sequence[Sequence[float]],
    *,
    alpha: float,
    practical_range: float,
) -> dict[str, object]:
    observed = np.asarray(observed_aucs, dtype=float)
    draws = np.asarray(bootstrap_auc_vectors, dtype=float)
    if draws.ndim != 2 or draws.shape[1] != observed.size or draws.shape[0] == 0:
        raise ValueError("bootstrap AUC vectors must be a non-empty B by target matrix")
    observed_range = float(np.ptp(observed))
    null_draws = draws - observed[None, :] + float(observed.mean())
    null_ranges = np.ptp(null_draws, axis=1)
    global_p = float((1 + int((null_ranges >= observed_range).sum())) / (draws.shape[0] + 1))

    pairwise: list[dict[str, object]] = []
    for left_index, right_index in combinations(range(observed.size), 2):
        observed_delta = float(observed[left_index] - observed[right_index])
        bootstrap_deltas = draws[:, left_index] - draws[:, right_index]
        centered = bootstrap_deltas - observed_delta
        raw_p = float(
            (1 + int((np.abs(centered) >= abs(observed_delta)).sum())) / (draws.shape[0] + 1)
        )
        pairwise.append(
            {
                "left": target_keys[left_index],
                "right": target_keys[right_index],
                "observed_delta": observed_delta,
                "raw_p_value": raw_p,
            }
        )
    order = sorted(range(len(pairwise)), key=lambda index: (pairwise[index]["raw_p_value"], index))
    running = 0.0
    adjusted = [1.0] * len(pairwise)
    for rank, index in enumerate(order):
        candidate = min(1.0, (len(pairwise) - rank) * float(pairwise[index]["raw_p_value"]))
        running = max(running, candidate)
        adjusted[index] = running
    for index, row in enumerate(pairwise):
        row["adjusted_p_value"] = adjusted[index]
        row["decision"] = adjusted[index] <= alpha

    practical_gate = observed_range >= practical_range
    return {
        "global": {
            "statistic": "auc_range",
            "observed_range": observed_range,
            "null_ranges": [float(value) for value in null_ranges],
            "p_value": global_p,
            "practical_gate": practical_gate,
            "decision": bool(global_p <= alpha and practical_gate),
        },
        "pairwise": pairwise,
        "correction": "holm",
    }


def bootstrap_h1_checkpoints(
    packets: Sequence[Mapping[str, object]],
    *,
    protocol_envelope: Mapping[str, object],
    expected_protocol_hash: str,
    n_bootstrap: int,
    random_state: int,
    analysis_mode: str,
    stage: str,
) -> dict[str, object]:
    """Run paired stratified bootstrap draws, refitting PCA/LR in every replicate."""

    expected_bootstrap = int(h1_scorer_contract()["bootstrap_replicates"])
    if type(n_bootstrap) is not int or n_bootstrap != expected_bootstrap:
        raise ValueError(f"n_bootstrap must equal the sealed protocol count {expected_bootstrap}")
    expected_random_state = int(h1_scorer_contract()["bootstrap_random_state"])
    if type(random_state) is not int or random_state != expected_random_state:
        raise ValueError(
            f"bootstrap random_state must equal the sealed protocol value {expected_random_state}"
        )
    context, validated = _validate_packets(
        packets,
        protocol_envelope=protocol_envelope,
        expected_protocol_hash=expected_protocol_hash,
        require_corrected_evaluation=True,
    )
    _validate_cross_target_roster(
        validated,
        context.h1_contract,
        analysis_mode=analysis_mode,
        stage=stage,
    )
    rng = np.random.default_rng(random_state)
    keys = [_target_key(packet) for packet in validated]
    target_samples: dict[str, list[float]] = {key: [] for key in keys}
    observed_aucs: dict[str, float] = {}
    observed_fit_provenance: dict[str, dict[str, object]] = {}
    pair_samples: dict[tuple[str, str], list[float]] = {pair: [] for pair in combinations(keys, 2)}
    paired_replicates: list[dict[str, object]] = []

    for key, packet in zip(keys, validated, strict=True):
        calibration = packet.calibration_indices
        evaluation = packet.evaluation_indices
        model = _fit_h1_arrays(
            packet.pca_features[calibration],
            packet.scalar_features[calibration],
            packet.labels[calibration],
            context.h1_contract,
        )
        scores = model.predict_scores(
            packet.pca_features[evaluation], packet.scalar_features[evaluation]
        )
        observed_aucs[key] = float(auc_score(scores, packet.labels[evaluation]))
        observed_fit_provenance[key] = {
            "sklearn_version": model.sklearn_version,
            "realized_logistic_regression": model.realized_logistic_regression,
        }

    for replicate in range(n_bootstrap):
        calibration_draw, evaluation_draw = _draw_stratified_indices(validated[0], rng)
        digest = hashlib.sha256(
            calibration_draw.astype("<i8", copy=False).tobytes()
            + evaluation_draw.astype("<i8", copy=False).tobytes()
        ).hexdigest()
        target_aucs: dict[str, float] = {}
        for key, packet in zip(keys, validated, strict=True):
            model = _fit_h1_arrays(
                packet.pca_features[calibration_draw],
                packet.scalar_features[calibration_draw],
                packet.labels[calibration_draw],
                context.h1_contract,
            )
            scores = model.predict_scores(
                packet.pca_features[evaluation_draw], packet.scalar_features[evaluation_draw]
            )
            auc = float(auc_score(scores, packet.labels[evaluation_draw]))
            target_samples[key].append(auc)
            target_aucs[key] = auc
        replicate_deltas: list[dict[str, object]] = []
        for left, right in combinations(keys, 2):
            delta = target_aucs[left] - target_aucs[right]
            pair_samples[(left, right)].append(delta)
            replicate_deltas.append({"left": left, "right": right, "delta": delta})
        paired_replicates.append(
            {
                "replicate": replicate,
                "shared_draw_sha256": digest,
                "target_aucs": target_aucs,
                "pairwise_auc_deltas": replicate_deltas,
            }
        )

    result = {
        "schema_version": 1,
        "protocol_hash": context.protocol_hash,
        "analysis_mode": analysis_mode,
        "stage": stage,
        "heterogeneity_contract": context.heterogeneity_contract,
        "random_state": random_state,
        "n_bootstrap": n_bootstrap,
        "strata": ["calibration_or_evaluation", "label", "class"],
        "targets": [
            {
                "target": dict(packet.target_provenance),
                "observed_auc": observed_aucs[key],
                "fit_provenance": observed_fit_provenance[key],
                "auc_samples": target_samples[key],
                "auc_ci_95": _percentile_interval(target_samples[key]),
            }
            for key, packet in zip(keys, validated, strict=True)
        ],
        "paired_replicates": paired_replicates,
        "pairwise_deltas": [
            {
                "left": left,
                "right": right,
                "samples": samples,
                "ci_95": _percentile_interval(samples),
            }
            for (left, right), samples in pair_samples.items()
        ],
        "heterogeneity_summary": summarize_h1_heterogeneity(
            keys,
            [observed_aucs[key] for key in keys],
            [[replicate["target_aucs"][key] for key in keys] for replicate in paired_replicates],
            alpha=float(context.heterogeneity_contract["global_test_alpha"]),
            practical_range=float(context.heterogeneity_contract["practical_auc_range_at_least"]),
        ),
    }
    json.dumps(result, allow_nan=False)
    return result


def _permuted_membership_labels(
    packet: _FeaturePacket,
    rng: np.random.Generator,
) -> np.ndarray:
    labels = packet.labels.copy()
    for split in _SPLITS:
        split_mask = np.asarray([value == split for value in packet.split_values], dtype=bool)
        for class_id in _CLASS_IDS:
            indices = np.flatnonzero(split_mask & (packet.classes == class_id))
            labels[indices] = rng.permutation(labels[indices])
    return labels


def full_label_permutation_test(
    packet: Mapping[str, object],
    *,
    protocol_envelope: Mapping[str, object],
    expected_protocol_hash: str,
    n_permutations: int,
    random_state: int,
) -> dict[str, object]:
    """Run a full-refit, split/class-preserving membership-label null."""

    expected_permutations = int(h1_scorer_contract()["permutation_replicates"])
    if type(n_permutations) is not int or n_permutations != expected_permutations:
        raise ValueError(
            f"n_permutations must equal the sealed protocol count {expected_permutations}"
        )
    expected_random_state = int(h1_scorer_contract()["permutation_random_state"])
    if type(random_state) is not int or random_state != expected_random_state:
        raise ValueError(
            f"permutation random_state must equal the sealed protocol value {expected_random_state}"
        )
    context, packets = _validate_packets(
        [packet],
        protocol_envelope=protocol_envelope,
        expected_protocol_hash=expected_protocol_hash,
        require_corrected_evaluation=True,
    )
    validated = packets[0]
    calibration = validated.calibration_indices
    evaluation = validated.evaluation_indices

    observed_model = _fit_h1_arrays(
        validated.pca_features[calibration],
        validated.scalar_features[calibration],
        validated.labels[calibration],
        context.h1_contract,
    )
    observed_scores = observed_model.predict_scores(
        validated.pca_features[evaluation], validated.scalar_features[evaluation]
    )
    observed_auc = float(auc_score(observed_scores, validated.labels[evaluation]))

    rng = np.random.default_rng(random_state)
    null_aucs: list[float] = []
    for _ in range(n_permutations):
        permuted_labels = _permuted_membership_labels(validated, rng)
        null_model = _fit_h1_arrays(
            validated.pca_features[calibration],
            validated.scalar_features[calibration],
            permuted_labels[calibration],
            context.h1_contract,
        )
        null_scores = null_model.predict_scores(
            validated.pca_features[evaluation], validated.scalar_features[evaluation]
        )
        null_aucs.append(float(auc_score(null_scores, permuted_labels[evaluation])))
    exceedances = sum(value >= observed_auc for value in null_aucs)
    result = {
        "schema_version": 1,
        "protocol_hash": context.protocol_hash,
        "target": dict(validated.target_provenance),
        "score_direction": "higher_is_member",
        "permutation_scheme": "within_each_split_and_class",
        "random_state": random_state,
        "n_permutations": n_permutations,
        "observed_auc": observed_auc,
        "fit_provenance": {
            "sklearn_version": observed_model.sklearn_version,
            "realized_logistic_regression": observed_model.realized_logistic_regression,
        },
        "null_aucs": null_aucs,
        "p_value": float((exceedances + 1) / (n_permutations + 1)),
        "p_value_correction": "plus_one",
        "refit_per_permutation": True,
    }
    json.dumps(result, allow_nan=False)
    return result


__all__ = [
    "H1FittedModel",
    "benchmark_h1_refit_runtime",
    "bootstrap_h1_checkpoints",
    "fit_h1_model",
    "full_label_permutation_test",
    "h1_scorer_contract",
    "score_h1_checkpoints",
    "summarize_h1_heterogeneity",
    "tpr_at_1pct_fpr_with_wilson",
    "validate_h1_feature_packets",
    "wilson_interval",
]
