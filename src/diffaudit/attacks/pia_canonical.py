"""Canonical DDPM PIA scoring and corrected-evidence packet validation."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np
import torch

from diffaudit.evidence.corrected_protocol import (
    paper1_pia_contract,
    validate_paper1_protocol_envelope,
)
from diffaudit.utils.metrics import auc_score, tpr_at_fpr_with_wilson

EpsilonOracle = Callable[[torch.Tensor, torch.Tensor], torch.Tensor]
CANONICAL_TIMESTEP = 200
CANONICAL_LP_ORDER = 4
CANONICAL_NUM_DIFFUSION_STEPS = 1000
_SHA256_RE = re.compile(r"[0-9a-f]{64}")
_GIT_COMMIT_RE = re.compile(r"[0-9a-f]{40}")
_ROLES = ("calibration", "evaluation")
_PACKET_FIELDS = {
    "schema_version",
    "attack",
    "variant",
    "timestep",
    "lp_order",
    "score_form",
    "score_direction",
    "input_range",
    "packet_purpose",
    "run_seed",
    "step",
    "checkpoint_sha256",
    "code_commit",
    "split_sha256",
    "protocol_hash",
    "rows",
}
_ROW_FIELDS = {
    "dataset_id",
    "dataset_index",
    "label",
    "class",
    "calibration_or_evaluation",
    "score",
    "noise_id",
}
_FIXED_PACKET_VALUES: dict[str, object] = {
    "schema_version": 1,
    "attack": "pia",
    "variant": "pia",
    "timestep": CANONICAL_TIMESTEP,
    "lp_order": CANONICAL_LP_ORDER,
    "score_form": "negative_lp_norm",
    "score_direction": "higher_is_member",
    "input_range": [-1.0, 1.0],
}


@dataclass(frozen=True, slots=True)
class PiaProtocolContext:
    protocol_hash: str
    dataset_id: str
    split_sha256: str
    code_commit: str
    manifest_rows: dict[int, tuple[int, int, str]]
    role_indices: dict[str, tuple[int, ...]]
    rosters: dict[str, tuple[frozenset[int], int]]
    pia_contract: dict[str, object]


@dataclass(frozen=True, slots=True)
class PiaScorePacket:
    payload: dict[str, object]
    role: str
    indices: np.ndarray
    labels: np.ndarray
    classes: np.ndarray
    scores: np.ndarray
    provenance: dict[str, object]


def _validate_inputs(x0: torch.Tensor, betas: torch.Tensor) -> None:
    if not isinstance(x0, torch.Tensor) or not x0.is_floating_point():
        raise TypeError("x0 must be a floating point torch.Tensor")
    if x0.ndim != 4:
        raise ValueError("x0 must be four-dimensional BCHW input")
    if x0.shape[0] == 0:
        raise ValueError("x0 batch must not be empty")
    if not bool(torch.isfinite(x0).all()):
        raise ValueError("x0 must contain only finite values")
    if float(x0.min()) < -1.0 or float(x0.max()) > 1.0:
        raise ValueError("x0 must be in the target training domain [-1, 1]")
    if not isinstance(betas, torch.Tensor) or not betas.is_floating_point():
        raise TypeError("betas must be a floating point torch.Tensor")
    if betas.ndim != 1 or betas.numel() != CANONICAL_NUM_DIFFUSION_STEPS:
        raise ValueError("betas must contain exactly 1000 diffusion steps")
    if betas.device != x0.device:
        raise ValueError("betas and x0 must be on the same device")
    if not bool(torch.isfinite(betas).all()) or bool(((betas <= 0) | (betas >= 1)).any()):
        raise ValueError("betas must be finite values strictly between zero and one")


def _validate_oracle_output(output: object, x0: torch.Tensor) -> torch.Tensor:
    if not isinstance(output, torch.Tensor):
        raise ValueError("epsilon oracle output must be a torch.Tensor")
    if output.shape != x0.shape or output.device != x0.device or output.dtype != x0.dtype:
        raise ValueError("epsilon oracle output must match x0 shape, device, and dtype")
    if not bool(torch.isfinite(output).all()):
        raise ValueError("epsilon oracle output must contain only finite values")
    return output


def score_pia_canonical(
    epsilon_oracle: EpsilonOracle,
    x0: torch.Tensor,
    betas: torch.Tensor,
    *,
    timestep: int = CANONICAL_TIMESTEP,
    lp_order: int = CANONICAL_LP_ORDER,
    diagnostics: bool = False,
) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor]:
    """Return one member-positive Eq. 9 score per row using queries ``[0, 200]``."""

    if timestep != CANONICAL_TIMESTEP:
        raise ValueError("canonical PIA timestep must be 200")
    if lp_order != CANONICAL_LP_ORDER:
        raise ValueError("canonical PIA lp_order must be 4")
    _validate_inputs(x0, betas)
    batch_size = x0.shape[0]
    t0 = torch.zeros(batch_size, dtype=torch.long, device=x0.device)
    tt = torch.full((batch_size,), timestep, dtype=torch.long, device=x0.device)
    e0 = _validate_oracle_output(epsilon_oracle(x0, t0), x0)
    alpha_bar_t = torch.cumprod(1.0 - betas, dim=0)[timestep]
    xt = alpha_bar_t.sqrt() * x0 + (1.0 - alpha_bar_t).sqrt() * e0
    if not bool(torch.isfinite(xt).all()):
        raise ValueError("canonical PIA x_t must contain only finite values")
    et = _validate_oracle_output(epsilon_oracle(xt, tt), x0)
    difference = e0 - et
    if not bool(torch.isfinite(difference).all()):
        raise ValueError("canonical PIA epsilon distance input must contain only finite values")
    residual = torch.linalg.vector_norm(difference.flatten(start_dim=1), ord=lp_order, dim=1)
    if not bool(torch.isfinite(residual).all()):
        raise ValueError("canonical PIA distances must contain only finite values")
    scores = -residual
    if not bool(torch.isfinite(scores).all()):
        raise ValueError("canonical PIA scores must contain only finite values")
    return (scores, residual) if diagnostics else scores


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is not allowed: {value}")


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key is not allowed: {key}")
        result[key] = value
    return result


def _load_finite_json(source: Mapping[str, object] | str | Path, *, name: str) -> dict[str, object]:
    if isinstance(source, Mapping):
        raw: object = source
    else:
        try:
            raw = json.loads(
                Path(source).read_text(encoding="utf-8"),
                parse_constant=_reject_json_constant,
                object_pairs_hook=_reject_duplicate_json_keys,
            )
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ValueError(f"{name} must contain valid finite JSON") from error
    try:
        copied = json.loads(json.dumps(raw, allow_nan=False))
    except (TypeError, ValueError) as error:
        raise ValueError(f"{name} must contain only finite JSON values") from error
    if not isinstance(copied, dict):
        raise ValueError(f"{name} must be a JSON mapping")
    return copied


def _require_exact_value(name: str, actual: object, expected: object) -> None:
    if type(actual) is not type(expected):
        raise ValueError(f"canonical PIA {name} does not match the sealed contract")
    if isinstance(expected, dict):
        if set(actual) != set(expected):
            raise ValueError(f"canonical PIA {name} fields do not match the sealed contract")
        for key, value in expected.items():
            _require_exact_value(f"{name}.{key}", actual[key], value)
        return
    if isinstance(expected, list):
        if len(actual) != len(expected):
            raise ValueError(f"canonical PIA {name} does not match the sealed contract")
        for index, (actual_value, expected_value) in enumerate(zip(actual, expected, strict=True)):
            _require_exact_value(f"{name}[{index}]", actual_value, expected_value)
        return
    if actual != expected:
        raise ValueError(f"canonical PIA {name} does not match the sealed contract")


def _require_hash(name: str, value: object, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        length = 64 if pattern is _SHA256_RE else 40
        raise ValueError(f"{name} must be {length} lowercase hex characters")
    return value


def derive_pia_noise_id(
    protocol_hash: str,
    dataset_index: int,
    *,
    timestep: int = CANONICAL_TIMESTEP,
    draw: str = "pia-e0",
) -> str:
    """Derive the deterministic Eq. 9 noise identity; no random draw is generated."""

    _require_hash("protocol_hash", protocol_hash, _SHA256_RE)
    if type(dataset_index) is not int or dataset_index < 0:
        raise ValueError("dataset_index must be a non-negative integer")
    if type(timestep) is not int or timestep != CANONICAL_TIMESTEP:
        raise ValueError("canonical PIA noise timestep must be 200")
    if draw != "pia-e0":
        raise ValueError("canonical PIA noise draw must be pia-e0")
    encoded = json.dumps(
        [protocol_hash, dataset_index, timestep, draw],
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_pia_protocol_context(
    source: Mapping[str, object] | str | Path,
    *,
    expected_protocol_hash: str,
) -> PiaProtocolContext:
    """Load the complete Paper 1 protocol under an external trust anchor."""

    loaded = validate_paper1_protocol_envelope(
        source,
        expected_protocol_hash=expected_protocol_hash,
    )
    contract = loaded["contract"]
    assert isinstance(contract, dict)
    dataset = contract["dataset"]
    assert isinstance(dataset, dict)
    split = dataset["split"]
    assert isinstance(split, dict)
    evaluation = contract["evaluation"]
    assert isinstance(evaluation, dict)
    raw_rows = evaluation["rows"]
    assert isinstance(raw_rows, list)
    manifest_rows: dict[int, tuple[int, int, str]] = {}
    role_indices: dict[str, list[int]] = {role: [] for role in _ROLES}
    for raw_row in raw_rows:
        assert isinstance(raw_row, dict)
        index = int(raw_row["dataset_index"])
        role = str(raw_row["split"])
        manifest_rows[index] = (int(raw_row["label"]), int(raw_row["class_id"]), role)
        role_indices[role].append(index)
    h1 = contract["h1"]
    assert isinstance(h1, dict)
    raw_rosters = h1["cross_target_rosters"]
    assert isinstance(raw_rosters, dict)
    rosters: dict[str, tuple[frozenset[int], int]] = {}
    for stage, raw_roster in raw_rosters.items():
        assert isinstance(stage, str) and isinstance(raw_roster, dict)
        seeds = raw_roster["seeds"]
        assert isinstance(seeds, list)
        rosters[stage] = (frozenset(int(seed) for seed in seeds), int(raw_roster["step"]))
    protocol_hash = loaded["protocol_hash"]
    assert isinstance(protocol_hash, str)
    return PiaProtocolContext(
        protocol_hash=protocol_hash,
        dataset_id=str(dataset["name"]),
        split_sha256=str(split["sha256"]),
        code_commit=str(contract["code_commit"]),
        manifest_rows=manifest_rows,
        role_indices={role: tuple(indices) for role, indices in role_indices.items()},
        rosters=rosters,
        pia_contract=paper1_pia_contract(),
    )


def validate_pia_stage_identity(
    context: PiaProtocolContext,
    *,
    stage: str,
    run_seed: object,
    step: object,
) -> tuple[int, int]:
    if stage not in context.rosters:
        raise ValueError("stage does not identify a sealed H1/PIA target roster")
    if type(run_seed) is not int or run_seed <= 0:
        raise ValueError("run_seed must be a positive integer")
    if type(step) is not int or step <= 0:
        raise ValueError("step must be a positive integer")
    roster_seeds, roster_step = context.rosters[stage]
    if run_seed not in roster_seeds:
        raise ValueError("run_seed is not allowed by the sealed stage roster")
    if step != roster_step:
        raise ValueError("step does not match the sealed stage step")
    return run_seed, step


def validate_pia_score_packet(
    source: Mapping[str, object] | str | Path,
    *,
    expected_role: Literal["calibration", "evaluation"],
    context: PiaProtocolContext,
    stage: str,
    expected_checkpoint_sha256: str,
) -> PiaScorePacket:
    """Validate one exact, complete, row-bound PIA score packet."""

    payload = _load_finite_json(source, name="canonical PIA score packet")
    if set(payload) != _PACKET_FIELDS:
        raise ValueError("canonical PIA score packet fields must be exact")
    for field, expected in _FIXED_PACKET_VALUES.items():
        _require_exact_value(field, payload[field], expected)
    purposes = context.pia_contract["packet_purposes"]
    if type(payload["packet_purpose"]) is not str or payload["packet_purpose"] not in purposes:
        raise ValueError("canonical PIA packet_purpose does not match the sealed contract")
    run_seed, step = validate_pia_stage_identity(
        context,
        stage=stage,
        run_seed=payload["run_seed"],
        step=payload["step"],
    )
    expected_checkpoint_sha256 = _require_hash(
        "expected_checkpoint_sha256", expected_checkpoint_sha256, _SHA256_RE
    )
    checkpoint_sha256 = _require_hash("checkpoint_sha256", payload["checkpoint_sha256"], _SHA256_RE)
    if checkpoint_sha256 != expected_checkpoint_sha256:
        raise ValueError("packet checkpoint_sha256 does not match trusted expected checkpoint")
    code_commit = _require_hash("code_commit", payload["code_commit"], _GIT_COMMIT_RE)
    if code_commit != context.code_commit:
        raise ValueError("packet code_commit does not match the sealed protocol")
    split_sha256 = _require_hash("split_sha256", payload["split_sha256"], _SHA256_RE)
    if split_sha256 != context.split_sha256:
        raise ValueError("packet split_sha256 does not match the sealed protocol")
    protocol_hash = _require_hash("protocol_hash", payload["protocol_hash"], _SHA256_RE)
    if protocol_hash != context.protocol_hash:
        raise ValueError("packet protocol_hash does not match trusted expected_protocol_hash")

    raw_rows = payload["rows"]
    if not isinstance(raw_rows, list) or not raw_rows:
        raise ValueError("canonical PIA score packet rows must be non-empty")
    indices: list[int] = []
    labels: list[int] = []
    classes: list[int] = []
    scores: list[float] = []
    seen: set[int] = set()
    for raw_row in raw_rows:
        if not isinstance(raw_row, dict) or set(raw_row) != _ROW_FIELDS:
            raise ValueError("canonical PIA score packet row fields must be exact")
        dataset_id = raw_row["dataset_id"]
        dataset_index = raw_row["dataset_index"]
        label = raw_row["label"]
        class_id = raw_row["class"]
        role = raw_row["calibration_or_evaluation"]
        score = raw_row["score"]
        noise_id = raw_row["noise_id"]
        if type(dataset_id) is not str or dataset_id != context.dataset_id:
            raise ValueError("dataset_id does not match the sealed protocol")
        if type(dataset_index) is not int or dataset_index < 0:
            raise ValueError("dataset_index must be a non-negative integer")
        if dataset_index in seen:
            raise ValueError("canonical PIA score packet contains a duplicate dataset_index")
        seen.add(dataset_index)
        if type(label) is not int or label not in (0, 1):
            raise ValueError("label must be integer 0 or 1")
        if type(class_id) is not int or class_id not in range(10):
            raise ValueError("class must be an integer from 0 through 9")
        if type(role) is not str or role != expected_role:
            raise ValueError("calibration_or_evaluation does not match the packet role")
        if (
            isinstance(score, bool)
            or not isinstance(score, (int, float))
            or not math.isfinite(score)
        ):
            raise ValueError("canonical PIA scores must be finite numbers")
        expected_manifest = context.manifest_rows.get(dataset_index)
        if expected_manifest != (label, class_id, role):
            raise ValueError("packet row does not match the locked manifest")
        expected_noise_id = derive_pia_noise_id(context.protocol_hash, dataset_index)
        if type(noise_id) is not str or noise_id != expected_noise_id:
            raise ValueError("noise_id does not match the canonical PIA derivation")
        indices.append(dataset_index)
        labels.append(label)
        classes.append(class_id)
        scores.append(float(score))
    if tuple(indices) != context.role_indices[expected_role]:
        raise ValueError("packet rows do not match the complete locked rows in the manifest")
    if set(labels) != {0, 1}:
        raise ValueError("canonical PIA packet requires both binary labels")
    provenance = {field: payload[field] for field in _PACKET_FIELDS if field != "rows"}
    provenance["run_seed"] = run_seed
    provenance["step"] = step
    return PiaScorePacket(
        payload=payload,
        role=expected_role,
        indices=np.asarray(indices, dtype=np.int64),
        labels=np.asarray(labels, dtype=np.int64),
        classes=np.asarray(classes, dtype=np.int64),
        scores=np.asarray(scores, dtype=float),
        provenance=provenance,
    )


def validate_pia_score_packet_pair(
    calibration_source: Mapping[str, object] | str | Path,
    evaluation_source: Mapping[str, object] | str | Path,
    *,
    context: PiaProtocolContext,
    stage: str,
    expected_checkpoint_sha256: str,
) -> tuple[PiaScorePacket, PiaScorePacket]:
    calibration = validate_pia_score_packet(
        calibration_source,
        expected_role="calibration",
        context=context,
        stage=stage,
        expected_checkpoint_sha256=expected_checkpoint_sha256,
    )
    evaluation = validate_pia_score_packet(
        evaluation_source,
        expected_role="evaluation",
        context=context,
        stage=stage,
        expected_checkpoint_sha256=expected_checkpoint_sha256,
    )
    if calibration.provenance != evaluation.provenance:
        raise ValueError("calibration/evaluation packet provenance must be identical")
    if not set(calibration.indices.tolist()).isdisjoint(evaluation.indices.tolist()):
        raise ValueError("calibration and evaluation packet rows must be disjoint")
    return calibration, evaluation


def build_pia_score_packet(
    context: PiaProtocolContext,
    *,
    calibration_or_evaluation: Literal["calibration", "evaluation"],
    scores_by_index: Mapping[int, float],
    packet_purpose: str,
    stage: str,
    run_seed: int,
    step: int,
    checkpoint_sha256: str,
) -> dict[str, object]:
    """Build and self-validate the sole canonical exporter packet shape."""

    validate_pia_stage_identity(context, stage=stage, run_seed=run_seed, step=step)
    checkpoint_sha256 = _require_hash("checkpoint_sha256", checkpoint_sha256, _SHA256_RE)
    expected_indices = context.role_indices[calibration_or_evaluation]
    if set(scores_by_index) != set(expected_indices) or len(scores_by_index) != len(
        expected_indices
    ):
        raise ValueError("scores_by_index must exactly cover the locked packet role")
    rows: list[dict[str, object]] = []
    for dataset_index in expected_indices:
        label, class_id, role = context.manifest_rows[dataset_index]
        rows.append(
            {
                "dataset_id": context.dataset_id,
                "dataset_index": dataset_index,
                "label": label,
                "class": class_id,
                "calibration_or_evaluation": role,
                "score": scores_by_index[dataset_index],
                "noise_id": derive_pia_noise_id(context.protocol_hash, dataset_index),
            }
        )
    payload = {
        **_FIXED_PACKET_VALUES,
        "packet_purpose": packet_purpose,
        "run_seed": run_seed,
        "step": step,
        "checkpoint_sha256": checkpoint_sha256,
        "code_commit": context.code_commit,
        "split_sha256": context.split_sha256,
        "protocol_hash": context.protocol_hash,
        "rows": rows,
    }
    return validate_pia_score_packet(
        payload,
        expected_role=calibration_or_evaluation,
        context=context,
        stage=stage,
        expected_checkpoint_sha256=checkpoint_sha256,
    ).payload


def write_pia_score_packet(path: str | Path, payload: Mapping[str, object]) -> Path:
    destination = Path(path)
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True, allow_nan=False),
        encoding="utf-8",
    )
    return destination


def _validated_score_labels(
    scores: np.ndarray, labels: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    score_values = np.asarray(scores, dtype=float)
    label_values = np.asarray(labels)
    if score_values.ndim != 1 or label_values.shape != score_values.shape:
        raise ValueError("scores and labels must be matching vectors")
    if not np.isfinite(score_values).all():
        raise ValueError("scores must contain only finite values")
    if label_values.dtype == np.bool_ or not np.issubdtype(label_values.dtype, np.integer):
        raise ValueError("labels must contain integer 0 and 1 values")
    labels_int = label_values.astype(np.int64, copy=False)
    if set(labels_int.tolist()) != {0, 1}:
        raise ValueError("labels must contain both binary classes")
    return score_values, labels_int


def calibrate_membership_threshold(scores: np.ndarray, labels: np.ndarray) -> float:
    """Select an observed calibration threshold by BA, FPR, then conservatism."""

    score_values, label_values = _validated_score_labels(scores, labels)
    candidates = np.unique(score_values)[::-1]
    best: tuple[float, float, float] | None = None
    best_threshold = float(candidates[0])
    for threshold in candidates:
        predictions = score_values >= threshold
        tpr = float(predictions[label_values == 1].mean())
        fpr = float(predictions[label_values == 0].mean())
        key = ((tpr + (1.0 - fpr)) / 2.0, -fpr, float(threshold))
        if best is None or key > best:
            best, best_threshold = key, float(threshold)
    return best_threshold


def apply_membership_threshold(
    scores: np.ndarray, labels: np.ndarray, threshold: float
) -> dict[str, Any]:
    """Apply a frozen calibration threshold to evaluation rows without reselection."""

    score_values, label_values = _validated_score_labels(scores, labels)
    if (
        not isinstance(threshold, (int, float))
        or isinstance(threshold, bool)
        or not math.isfinite(threshold)
    ):
        raise ValueError("threshold must be finite")
    predictions = (score_values >= threshold).astype(np.int64)
    tpr = float(predictions[label_values == 1].mean())
    fpr = float(predictions[label_values == 0].mean())
    return {
        "calibration_threshold": float(threshold),
        "evaluation_balanced_accuracy": (tpr + (1.0 - fpr)) / 2.0,
        "evaluation_tpr": tpr,
        "evaluation_fpr": fpr,
        "predictions": predictions,
    }


def evaluate_calibrated_packets(
    calibration_scores: np.ndarray,
    calibration_labels: np.ndarray,
    calibration_indices: np.ndarray,
    evaluation_scores: np.ndarray,
    evaluation_labels: np.ndarray,
    evaluation_indices: np.ndarray,
) -> dict[str, Any]:
    """Fit on calibration rows and report fixed-direction held-out metrics only."""

    calibration_scores, calibration_labels = _validated_score_labels(
        calibration_scores, calibration_labels
    )
    evaluation_scores, evaluation_labels = _validated_score_labels(
        evaluation_scores, evaluation_labels
    )
    calibration_indices = np.asarray(calibration_indices)
    evaluation_indices = np.asarray(evaluation_indices)
    if calibration_indices.ndim != 1 or calibration_indices.shape != calibration_scores.shape:
        raise ValueError("calibration indices and scores must be matching vectors")
    if evaluation_indices.ndim != 1 or evaluation_indices.shape != evaluation_scores.shape:
        raise ValueError("evaluation indices and scores must be matching vectors")
    overlap = np.intersect1d(calibration_indices, evaluation_indices)
    if overlap.size:
        raise ValueError("calibration and evaluation rows must be disjoint")
    threshold = calibrate_membership_threshold(calibration_scores, calibration_labels)
    result = apply_membership_threshold(evaluation_scores, evaluation_labels, threshold)
    tpr_metric = tpr_at_fpr_with_wilson(
        evaluation_scores,
        evaluation_labels,
        target_fpr=0.01,
    )
    result.update(
        {
            "evaluation_auc": float(auc_score(evaluation_scores, evaluation_labels)),
            "tpr_at_1pct_fpr": tpr_metric["estimate"],
            "tpr_at_1pct_fpr_wilson_95_ci": tpr_metric["wilson_95_ci"],
            "tpr_at_1pct_fpr_member_successes": tpr_metric["member_successes"],
            "tpr_at_1pct_fpr_member_total": tpr_metric["member_total"],
            "tpr_at_1pct_fpr_fpr_cap": tpr_metric["fpr_cap"],
        }
    )
    return result


def aggregate_synthetic_checkpoint_positive_control(
    calibration_scores: np.ndarray,
    calibration_labels: np.ndarray,
    calibration_indices: np.ndarray,
    evaluation_scores: np.ndarray,
    evaluation_labels: np.ndarray,
    evaluation_indices: np.ndarray,
    zero_scores: np.ndarray,
    zero_labels: np.ndarray,
) -> dict[str, object]:
    """Aggregate the sealed full gate for a label-blind synthetic checkpoint test."""

    evaluated = evaluate_calibrated_packets(
        calibration_scores,
        calibration_labels,
        calibration_indices,
        evaluation_scores,
        evaluation_labels,
        evaluation_indices,
    )
    evaluation_scores, evaluation_labels = _validated_score_labels(
        evaluation_scores, evaluation_labels
    )
    zero_scores, zero_labels = _validated_score_labels(zero_scores, zero_labels)
    if not np.array_equal(zero_labels, evaluation_labels):
        raise ValueError("zero-control labels must match evaluation labels")
    contract = paper1_pia_contract()
    gate = contract["positive_control_gate"]
    assert isinstance(gate, dict)
    negative_score_auc = float(auc_score(-evaluation_scores, evaluation_labels))
    zero_signal_auc = float(auc_score(zero_scores, zero_labels))
    permutation_count = int(gate["permutations"])
    rng = np.random.default_rng(int(gate["permutation_random_state"]))
    permutation_aucs = [
        float(auc_score(evaluation_scores, rng.permutation(evaluation_labels)))
        for _ in range(permutation_count)
    ]
    permutation_mean = float(np.mean(permutation_aucs))
    evaluation_auc = float(evaluated["evaluation_auc"])
    zero_range = gate["zero_signal_auc_range"]
    null_range = gate["null_auc_mean_range"]
    assert isinstance(zero_range, list) and isinstance(null_range, list)
    checks = {
        "evaluation_auc": evaluation_auc >= float(gate["evaluation_auc_min"]),
        "evaluation_balanced_accuracy": float(evaluated["evaluation_balanced_accuracy"])
        >= float(gate["evaluation_balanced_accuracy_min"]),
        "evaluation_fpr": float(evaluated["evaluation_fpr"]) <= float(gate["evaluation_fpr_max"]),
        "negative_score_auc": negative_score_auc <= float(gate["negative_score_auc_max"]),
        "zero_signal_auc": float(zero_range[0]) <= zero_signal_auc <= float(zero_range[1]),
        "permutation_auc_mean": float(null_range[0]) <= permutation_mean <= float(null_range[1]),
        "positive_auc_exceeds_all_permutations": evaluation_auc > max(permutation_aucs),
    }
    status = (
        "synthetic_checkpoint_positive_control_passed"
        if all(checks.values())
        else "synthetic_checkpoint_positive_control_failed"
    )
    return {
        "status": status,
        "evidence_scope": "synthetic_checkpoint_positive_control_only",
        "real_model_evidence": False,
        "checks": checks,
        "metrics": {
            "evaluation_auc": evaluation_auc,
            "evaluation_balanced_accuracy": evaluated["evaluation_balanced_accuracy"],
            "evaluation_fpr": evaluated["evaluation_fpr"],
            "negative_score_auc": negative_score_auc,
            "zero_signal_auc": zero_signal_auc,
            "permutation_auc_mean": permutation_mean,
            "permutation_auc_max": max(permutation_aucs),
            "permutation_count": permutation_count,
        },
    }
