"""Canonical DDPM PIA scoring and corrected-evidence packet validation."""

from __future__ import annotations

import hashlib
import io
import json
import math
import pickle
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Literal

import numpy as np
import torch

from diffaudit.evidence.corrected_protocol import (
    paper1_pia_contract,
    render_paper1_run_label,
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
    "training_manifest_sha256",
    "target_code_commit",
    "scorer_code_commit",
    "split_sha256",
    "protocol_hash",
    "extraction",
    "rows",
}
_RECEIPT_FIELDS = {
    "checkpoint_sha256",
    "protocol_hash",
    "code_commit",
    "run_seed",
    "step",
    "run_label",
    "training_config_hash",
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
    "schema_version": 2,
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
    rosters: dict[str, tuple[tuple[int, ...], int]]
    pia_contract: dict[str, object]
    heterogeneity_contract: dict[str, object]


@dataclass(frozen=True, slots=True)
class PiaScorePacket:
    payload: dict[str, object]
    role: str
    indices: np.ndarray
    labels: np.ndarray
    classes: np.ndarray
    scores: np.ndarray
    provenance: dict[str, object]
    trusted_source_sha256: str | None = None


@dataclass(frozen=True, slots=True)
class TrustedPiaCheckpointSource:
    """Path-only formal PIA inputs bound to externally supplied raw-byte hashes."""

    calibration_packet: str | Path
    calibration_packet_sha256: str
    evaluation_packet: str | Path
    evaluation_packet_sha256: str
    training_output_manifest: str | Path


@dataclass(frozen=True, slots=True)
class PiaTrainingIdentity:
    stage: str
    run_seed: int
    step: int
    run_label: str
    checkpoint_filename: str
    checkpoint_sha256: str
    training_manifest_sha256: str
    training_config_hash: str
    scorer_code_commit: str


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def _load_trusted_packet_payload(
    path_source: str | Path,
    expected_sha256: str,
    *,
    role: str,
) -> tuple[dict[str, object], str]:
    if isinstance(path_source, Mapping) or not isinstance(path_source, (str, Path)):
        raise ValueError("formal corrected_evaluation packets must use trusted path-based sources")
    expected = _require_hash(f"expected {role} packet SHA256", expected_sha256, _SHA256_RE)
    path = Path(path_source)
    try:
        raw_bytes = path.read_bytes()
    except OSError as error:
        raise ValueError(f"canonical PIA {role} packet path is unreadable") from error
    realized = hashlib.sha256(raw_bytes).hexdigest()
    if realized != expected:
        raise ValueError(
            f"canonical PIA {role} packet SHA256 does not match the trusted expected hash"
        )
    try:
        raw = json.loads(
            raw_bytes.decode("utf-8"),
            parse_constant=_reject_json_constant,
            object_pairs_hook=_reject_duplicate_json_keys,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"canonical PIA {role} packet must contain valid finite JSON") from error
    try:
        copied = json.loads(json.dumps(raw, allow_nan=False))
    except (TypeError, ValueError) as error:
        raise ValueError(f"canonical PIA {role} packet must contain finite JSON") from error
    if not isinstance(copied, dict):
        raise ValueError(f"canonical PIA {role} packet must be a JSON mapping")
    return copied, realized


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
    rosters: dict[str, tuple[tuple[int, ...], int]] = {}
    for stage, raw_roster in raw_rosters.items():
        assert isinstance(stage, str) and isinstance(raw_roster, dict)
        seeds = raw_roster["seeds"]
        assert isinstance(seeds, list)
        rosters[stage] = (tuple(int(seed) for seed in seeds), int(raw_roster["step"]))
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
        heterogeneity_contract=dict(contract["confirmatory_heterogeneity"]),
    )


def validate_pia_stage_identity(
    context: PiaProtocolContext,
    *,
    stage: str,
    run_seed: object,
    step: object,
    packet_purpose: str = "corrected_evaluation",
) -> tuple[int, int]:
    if packet_purpose == "preflight_benchmark":
        if stage != "preflight":
            raise ValueError("preflight_benchmark requires the sealed preflight stage")
        identity = context.pia_contract["preflight_identity"]
        assert isinstance(identity, dict)
        expected_seed = identity["run_seed"]
        expected_step = identity["step"]
        if type(run_seed) is not int or type(step) is not int:
            raise ValueError("preflight identity requires integer run_seed and step")
        if run_seed != expected_seed or step != expected_step:
            raise ValueError("preflight identity does not match the sealed seed and step")
        return run_seed, step
    if stage == "preflight":
        raise ValueError("preflight stage requires packet_purpose=preflight_benchmark")
    if stage not in context.rosters:
        raise ValueError("stage does not identify a sealed H1/PIA target roster")
    if type(run_seed) is not int or run_seed <= 0:
        raise ValueError("run_seed must be a positive integer")
    if type(step) is not int or step <= 0:
        raise ValueError("step must be a positive integer")
    roster_seed_order, roster_step = context.rosters[stage]
    roster_seeds = set(roster_seed_order)
    if run_seed not in roster_seeds:
        raise ValueError("run_seed is not allowed by the sealed stage roster")
    if step != roster_step:
        raise ValueError("step does not match the sealed stage step")
    return run_seed, step


def validate_pia_cpu_runtime(
    extraction_contract: Mapping[str, object],
    *,
    device: str,
    batch_size: int,
    evaluator_environment: Mapping[str, object],
) -> None:
    """Enforce the exact CPU-only PIA extraction runtime frozen in the protocol."""

    expected_fields = {"batch_size", "device", "weights_key", "evaluator_environment"}
    if set(extraction_contract) != expected_fields:
        raise ValueError("canonical PIA extraction contract fields must be exact")
    if device != "cpu" or extraction_contract["device"] != "cpu":
        raise ValueError("canonical PIA runtime device must be exactly cpu")
    if type(batch_size) is not int or batch_size != 8 or extraction_contract["batch_size"] != 8:
        raise ValueError("canonical PIA runtime batch_size must be exactly 8")
    expected_environment = extraction_contract["evaluator_environment"]
    if not isinstance(expected_environment, Mapping):
        raise ValueError("canonical PIA evaluator_environment must be a mapping")
    if dict(evaluator_environment) != dict(expected_environment):
        raise ValueError(
            "canonical PIA CPU evaluator_environment does not match the sealed runtime"
        )


def derive_pia_stage(
    context: PiaProtocolContext,
    *,
    run_seed: object,
    step: object,
    packet_purpose: str = "corrected_evaluation",
) -> str:
    purposes = context.pia_contract["packet_purposes"]
    if type(packet_purpose) is not str or packet_purpose not in purposes:
        raise ValueError("canonical PIA packet_purpose does not match the sealed contract")
    if type(run_seed) is not int or run_seed <= 0:
        raise ValueError("run_seed must be a positive integer")
    if type(step) is not int or step <= 0:
        raise ValueError("step must be a positive integer")
    if packet_purpose == "preflight_benchmark":
        validate_pia_stage_identity(
            context,
            stage="preflight",
            run_seed=run_seed,
            step=step,
            packet_purpose=packet_purpose,
        )
        return "preflight"
    matches = [
        stage
        for stage in context.rosters
        if _stage_identity_matches(context, stage=stage, run_seed=run_seed, step=step)
    ]
    if not matches:
        raise ValueError("checkpoint seed and step do not map to one sealed stage")
    minimum_roster_size = min(len(context.rosters[stage][0]) for stage in matches)
    most_specific = [
        stage for stage in matches if len(context.rosters[stage][0]) == minimum_roster_size
    ]
    if len(most_specific) != 1:
        raise ValueError("checkpoint seed and step map ambiguously to sealed stages")
    return most_specific[0]


def _stage_identity_matches(
    context: PiaProtocolContext, *, stage: str, run_seed: object, step: object
) -> bool:
    roster_seed_order, roster_step = context.rosters[stage]
    roster_seeds = set(roster_seed_order)
    return (
        type(run_seed) is int
        and type(step) is int
        and run_seed in roster_seeds
        and step == roster_step
    )


def _load_training_manifest(
    source: str | Path,
) -> tuple[dict[str, object], str, dict[str, dict[str, object]]]:
    path = Path(source)
    payload = _load_finite_json(path, name="corrected training output manifest")
    manifest_sha256 = _sha256_file(path)
    raw_receipts = payload.get("checkpoint_receipts")
    if not isinstance(raw_receipts, dict) or not raw_receipts:
        raise ValueError("training output manifest requires checkpoint_receipts")
    receipts: dict[str, dict[str, object]] = {}
    for name, receipt in raw_receipts.items():
        if (
            not isinstance(name, str)
            or not isinstance(receipt, dict)
            or set(receipt) != _RECEIPT_FIELDS
        ):
            raise ValueError("training checkpoint receipt fields must be exact")
        receipts[name] = receipt
    return payload, manifest_sha256, receipts


def _manifest_checkpoint_path(
    manifest_path: Path,
    payload: Mapping[str, object],
    receipts: Mapping[str, Mapping[str, object]],
) -> Path:
    raw_name = payload.get("checkpoint")
    if (
        not isinstance(raw_name, str)
        or not raw_name
        or PurePosixPath(raw_name).name != raw_name
        or PureWindowsPath(raw_name).name != raw_name
    ):
        raise ValueError("training manifest checkpoint must be a safe basename")
    if raw_name not in receipts:
        raise ValueError("training manifest checkpoint does not identify one checkpoint receipt")
    checkpoint_path = (manifest_path.parent / raw_name).resolve()
    if checkpoint_path.parent != manifest_path.parent.resolve():
        raise ValueError("training manifest checkpoint must stay under the manifest parent")
    if not checkpoint_path.is_file():
        raise ValueError("training manifest checkpoint file does not exist")
    return checkpoint_path


def resolve_pia_training_checkpoint_path(
    training_output_manifest: str | Path,
    *,
    expected_model_dir: str | Path,
) -> Path:
    """Resolve only the safe checkpoint named by the corrected training manifest."""

    manifest_path = Path(training_output_manifest).resolve()
    payload, _, receipts = _load_training_manifest(manifest_path)
    checkpoint_path = _manifest_checkpoint_path(manifest_path, payload, receipts)
    if checkpoint_path.parent != Path(expected_model_dir).resolve():
        raise ValueError("canonical PIA model_dir must equal the training manifest parent")
    return checkpoint_path


def load_pia_training_identity(
    context: PiaProtocolContext,
    *,
    checkpoint_path: str | Path,
    training_output_manifest: str | Path,
    scorer_code_commit: str,
    packet_purpose: str = "corrected_evaluation",
    checkpoint_snapshot: bytes | None = None,
) -> PiaTrainingIdentity:
    checkpoint_path = Path(checkpoint_path)
    try:
        checkpoint_bytes = (
            checkpoint_path.read_bytes() if checkpoint_snapshot is None else checkpoint_snapshot
        )
    except OSError as error:
        raise ValueError("corrected checkpoint is unreadable") from error
    checkpoint_sha256 = hashlib.sha256(checkpoint_bytes).hexdigest()
    try:
        checkpoint = torch.load(io.BytesIO(checkpoint_bytes), map_location="cpu", weights_only=True)
    except (OSError, RuntimeError, EOFError, ValueError, pickle.UnpicklingError) as error:
        raise ValueError("checkpoint must be a weights-only-safe corrected checkpoint") from error
    expected_checkpoint_fields = {"model", "ema", "optim", "sched", "step", "metadata", "rng_state"}
    if not isinstance(checkpoint, Mapping) or set(checkpoint) != expected_checkpoint_fields:
        raise ValueError("checkpoint payload fields do not match the corrected schema")
    metadata = checkpoint.get("metadata")
    expected_metadata_fields = {
        "run_label",
        "seed",
        "protocol_hash",
        "checkpoint_step",
        "split_sha256",
        "code_commit",
        "training_config",
        "training_config_hash",
        "environment",
    }
    if not isinstance(metadata, Mapping) or set(metadata) != expected_metadata_fields:
        raise ValueError("checkpoint metadata fields do not match the corrected schema")
    manifest_path = Path(training_output_manifest).resolve()
    payload, manifest_sha256, receipts = _load_training_manifest(manifest_path)
    manifest_checkpoint_path = _manifest_checkpoint_path(manifest_path, payload, receipts)
    if checkpoint_path.resolve() != manifest_checkpoint_path:
        raise ValueError("checkpoint path does not match the training manifest checkpoint")
    receipt = receipts.get(checkpoint_path.name)
    if receipt is None:
        raise ValueError("training output manifest has no receipt for checkpoint")
    run_seed = metadata["seed"]
    step = metadata["checkpoint_step"]
    run_label = metadata["run_label"]
    training_config_hash = metadata["training_config_hash"]
    training_config = metadata["training_config"]
    if not isinstance(training_config, Mapping):
        raise ValueError("checkpoint training_config must be a mapping")
    canonical_config_hash = hashlib.sha256(
        json.dumps(
            training_config, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
    ).hexdigest()
    if training_config_hash != canonical_config_hash:
        raise ValueError("checkpoint training_config_hash does not match training_config")
    stage = derive_pia_stage(
        context,
        run_seed=run_seed,
        step=step,
        packet_purpose=packet_purpose,
    )
    expected_run_label = render_paper1_run_label(
        int(run_seed), preflight=packet_purpose == "preflight_benchmark"
    )
    if run_label != expected_run_label:
        raise ValueError("checkpoint run_label does not match the sealed purpose-specific template")
    expected_identity = {
        "checkpoint_sha256": checkpoint_sha256,
        "protocol_hash": context.protocol_hash,
        "code_commit": context.code_commit,
        "run_seed": run_seed,
        "step": step,
        "run_label": run_label,
        "training_config_hash": training_config_hash,
    }
    for field, expected in expected_identity.items():
        _require_exact_value(f"training receipt.{field}", receipt[field], expected)
    for field, expected in {
        "protocol_hash": context.protocol_hash,
        "split_sha256": context.split_sha256,
        "code_commit": context.code_commit,
        "seed": run_seed,
        "run_label": run_label,
        "step": step,
        "training_config_hash": training_config_hash,
    }.items():
        _require_exact_value(f"training manifest.{field}", payload.get(field), expected)
    for field, expected in {
        "protocol_hash": context.protocol_hash,
        "split_sha256": context.split_sha256,
        "code_commit": context.code_commit,
        "checkpoint_step": step,
    }.items():
        _require_exact_value(f"checkpoint metadata.{field}", metadata[field], expected)
    if checkpoint["step"] != step:
        raise ValueError("checkpoint top-level step does not match metadata")
    if not isinstance(run_label, str) or not isinstance(training_config_hash, str):
        raise ValueError("checkpoint run_label or training_config_hash is invalid")
    return PiaTrainingIdentity(
        stage=stage,
        run_seed=int(run_seed),
        step=int(step),
        run_label=run_label,
        checkpoint_filename=checkpoint_path.name,
        checkpoint_sha256=checkpoint_sha256,
        training_manifest_sha256=manifest_sha256,
        training_config_hash=_require_hash(
            "training_config_hash", training_config_hash, _SHA256_RE
        ),
        scorer_code_commit=_require_hash("scorer_code_commit", scorer_code_commit, _GIT_COMMIT_RE),
    )


def validate_pia_score_packet(
    source: Mapping[str, object] | str | Path,
    *,
    expected_role: Literal["calibration", "evaluation"],
    context: PiaProtocolContext,
    training_output_manifest: str | Path,
    trusted_source_sha256: str | None = None,
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
    packet_purpose = payload["packet_purpose"]
    assert isinstance(packet_purpose, str)
    stage = derive_pia_stage(
        context,
        run_seed=payload["run_seed"],
        step=payload["step"],
        packet_purpose=packet_purpose,
    )
    run_seed, step = validate_pia_stage_identity(
        context,
        stage=stage,
        run_seed=payload["run_seed"],
        step=payload["step"],
        packet_purpose=packet_purpose,
    )
    expected_run_label = render_paper1_run_label(
        run_seed, preflight=packet_purpose == "preflight_benchmark"
    )
    checkpoint_sha256 = _require_hash("checkpoint_sha256", payload["checkpoint_sha256"], _SHA256_RE)
    manifest_payload, manifest_sha256, receipts = _load_training_manifest(training_output_manifest)
    packet_manifest_sha256 = _require_hash(
        "training_manifest_sha256", payload["training_manifest_sha256"], _SHA256_RE
    )
    if packet_manifest_sha256 != manifest_sha256:
        raise ValueError("packet training_manifest_sha256 does not match training manifest")
    matching_receipts = [
        receipt
        for receipt in receipts.values()
        if receipt["checkpoint_sha256"] == checkpoint_sha256
    ]
    if len(matching_receipts) != 1:
        raise ValueError("packet checkpoint_sha256 does not identify one training receipt")
    receipt = matching_receipts[0]
    if receipt["run_label"] != expected_run_label:
        raise ValueError("packet run_label does not match the sealed purpose-specific template")
    checkpoint_filename = manifest_payload.get("checkpoint")
    if (
        not isinstance(checkpoint_filename, str)
        or PurePosixPath(checkpoint_filename).name != checkpoint_filename
        or PureWindowsPath(checkpoint_filename).name != checkpoint_filename
        or receipts.get(checkpoint_filename) is not receipt
    ):
        raise ValueError("packet checkpoint does not match the training manifest checkpoint")
    for field, expected in {
        "protocol_hash": context.protocol_hash,
        "code_commit": context.code_commit,
        "run_seed": run_seed,
        "step": step,
    }.items():
        if receipt[field] != expected or type(receipt[field]) is not type(expected):
            raise ValueError(f"packet provenance does not match training receipt: {field}")
    for field, expected in {
        "protocol_hash": context.protocol_hash,
        "split_sha256": context.split_sha256,
        "code_commit": context.code_commit,
        "seed": run_seed,
        "step": step,
        "run_label": receipt["run_label"],
        "training_config_hash": receipt["training_config_hash"],
    }.items():
        _require_exact_value(f"training manifest.{field}", manifest_payload.get(field), expected)
    target_code_commit = _require_hash(
        "target_code_commit", payload["target_code_commit"], _GIT_COMMIT_RE
    )
    if target_code_commit != context.code_commit:
        raise ValueError("packet target_code_commit does not match the sealed protocol")
    scorer_code_commit = _require_hash(
        "scorer_code_commit", payload["scorer_code_commit"], _GIT_COMMIT_RE
    )
    if scorer_code_commit != context.code_commit:
        raise ValueError("packet scorer_code_commit does not match the sealed protocol")
    split_sha256 = _require_hash("split_sha256", payload["split_sha256"], _SHA256_RE)
    if split_sha256 != context.split_sha256:
        raise ValueError("packet split_sha256 does not match the sealed protocol")
    protocol_hash = _require_hash("protocol_hash", payload["protocol_hash"], _SHA256_RE)
    if protocol_hash != context.protocol_hash:
        raise ValueError("packet protocol_hash does not match trusted expected_protocol_hash")
    extraction_contract = context.pia_contract["extraction"]
    upstream_contract = context.pia_contract["upstream"]
    assert isinstance(extraction_contract, dict) and isinstance(upstream_contract, dict)
    expected_extraction = {
        "packet_purpose": packet_purpose,
        "device": extraction_contract["device"],
        "batch_size": extraction_contract["batch_size"],
        "weights_key": extraction_contract["weights_key"],
        "evaluator_environment": extraction_contract["evaluator_environment"],
        "upstream": {**upstream_contract, "git_clean": True},
        "checkpoint_filename": checkpoint_filename,
        "run_label": receipt["run_label"],
        "training_config_hash": receipt["training_config_hash"],
    }
    _require_exact_value("extraction", payload["extraction"], expected_extraction)

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
        trusted_source_sha256=trusted_source_sha256,
    )


def validate_pia_score_packet_pair(
    calibration_source: Mapping[str, object] | str | Path,
    evaluation_source: Mapping[str, object] | str | Path,
    *,
    context: PiaProtocolContext,
    training_output_manifest: str | Path,
    calibration_trusted_sha256: str | None = None,
    evaluation_trusted_sha256: str | None = None,
) -> tuple[PiaScorePacket, PiaScorePacket]:
    calibration = validate_pia_score_packet(
        calibration_source,
        expected_role="calibration",
        context=context,
        training_output_manifest=training_output_manifest,
        trusted_source_sha256=calibration_trusted_sha256,
    )
    evaluation = validate_pia_score_packet(
        evaluation_source,
        expected_role="evaluation",
        context=context,
        training_output_manifest=training_output_manifest,
        trusted_source_sha256=evaluation_trusted_sha256,
    )
    if calibration.provenance != evaluation.provenance:
        raise ValueError("calibration/evaluation packet provenance must be identical")
    if not set(calibration.indices.tolist()).isdisjoint(evaluation.indices.tolist()):
        raise ValueError("calibration and evaluation packet rows must be disjoint")
    return calibration, evaluation


def _validate_pia_checkpoint_sources(
    sources: Sequence[TrustedPiaCheckpointSource],
    *,
    protocol_envelope: Mapping[str, object] | str | Path,
    expected_protocol_hash: str,
    analysis_mode: str | None,
    stage: str | None,
) -> tuple[PiaProtocolContext, list[tuple[PiaScorePacket, PiaScorePacket]], str]:
    if not isinstance(sources, Sequence) or isinstance(sources, (str, bytes)) or not sources:
        raise ValueError("PIA checkpoint sources must be a non-empty sequence")
    context = load_pia_protocol_context(
        protocol_envelope,
        expected_protocol_hash=expected_protocol_hash,
    )
    analysis_code_commit = _validate_analysis_repository_state(context)
    validated: list[tuple[PiaScorePacket, PiaScorePacket]] = []
    for source in sources:
        if not isinstance(source, TrustedPiaCheckpointSource):
            raise ValueError(
                "formal corrected_evaluation sources must be trusted path-based packet sources"
            )
        calibration_source, calibration_sha256 = _load_trusted_packet_payload(
            source.calibration_packet,
            source.calibration_packet_sha256,
            role="calibration",
        )
        evaluation_source, evaluation_sha256 = _load_trusted_packet_payload(
            source.evaluation_packet,
            source.evaluation_packet_sha256,
            role="evaluation",
        )
        calibration, evaluation = validate_pia_score_packet_pair(
            calibration_source,
            evaluation_source,
            context=context,
            training_output_manifest=source.training_output_manifest,
            calibration_trusted_sha256=calibration_sha256,
            evaluation_trusted_sha256=evaluation_sha256,
        )
        if calibration.provenance["packet_purpose"] != "corrected_evaluation":
            raise ValueError("confirmatory PIA analysis requires corrected_evaluation packets")
        validated.append((calibration, evaluation))

    if analysis_mode != "cross_target_same_step":
        raise ValueError("formal PIA analysis_mode must be cross_target_same_step")
    if stage not in context.rosters:
        raise ValueError("cross-target stage does not identify a sealed target roster")
    roster_seed_order, roster_step = context.rosters[stage]
    roster_seeds = set(roster_seed_order)
    seeds = [int(calibration.provenance["run_seed"]) for calibration, _ in validated]
    if len(set(seeds)) != len(seeds):
        raise ValueError("cross-target roster contains a duplicate seed")
    seed_set = set(seeds)
    missing = roster_seeds - seed_set
    extra = seed_set - roster_seeds
    if missing and extra:
        raise ValueError("cross-target roster has missing and extra seeds")
    if missing:
        raise ValueError("cross-target roster has a missing seed")
    if extra:
        raise ValueError("cross-target roster has an extra seed")
    if len(seeds) != len(roster_seeds):
        raise ValueError("cross-target roster does not exactly match the sealed stage roster")
    steps = {int(calibration.provenance["step"]) for calibration, _ in validated}
    if steps != {roster_step}:
        raise ValueError("cross-target roster has a wrong step")
    validated_by_seed = {
        int(calibration.provenance["run_seed"]): (calibration, evaluation)
        for calibration, evaluation in validated
    }
    validated = [validated_by_seed[seed] for seed in roster_seed_order]
    return context, validated, analysis_code_commit


def _validate_analysis_repository_state(context: PiaProtocolContext) -> str:
    from diffaudit.attacks import pia_adapter

    head, tracked_status, untracked_code = pia_adapter.read_pia_repository_state(
        pia_adapter.RESEARCH_ROOT
    )
    return pia_adapter.validate_pia_repository_state(
        head,
        context.code_commit,
        tracked_status,
        untracked_code,
    )


def _canonical_payload_sha256(payload: Mapping[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _analysis_provenance(
    context: PiaProtocolContext,
    analysis_code_commit: str,
) -> dict[str, str]:
    analysis_contract = {
        "pia": context.pia_contract,
        "confirmatory_heterogeneity": context.heterogeneity_contract,
    }
    return {
        "analysis_code_commit": analysis_code_commit,
        "analysis_contract_hash": _canonical_payload_sha256(analysis_contract),
    }


def _pia_target_provenance(
    context: PiaProtocolContext,
    calibration: PiaScorePacket,
    evaluation: PiaScorePacket,
) -> dict[str, object]:
    return {
        **calibration.provenance,
        "dataset_id": context.dataset_id,
        "calibration_packet_sha256": calibration.trusted_source_sha256,
        "evaluation_packet_sha256": evaluation.trusted_source_sha256,
    }


def _score_pia_packet_pair(
    context: PiaProtocolContext,
    calibration: PiaScorePacket,
    evaluation: PiaScorePacket,
) -> dict[str, object]:
    evaluated = evaluate_calibrated_packets(
        calibration.scores,
        calibration.labels,
        calibration.indices,
        evaluation.scores,
        evaluation.labels,
        evaluation.indices,
    )
    metrics = {key: value for key, value in evaluated.items() if key != "predictions"}
    raw_rows = evaluation.payload["rows"]
    assert isinstance(raw_rows, list)
    evaluation_rows = [
        {
            "dataset_index": row["dataset_index"],
            "label": row["label"],
            "class": row["class"],
            "calibration_or_evaluation": row["calibration_or_evaluation"],
            "noise_id": row["noise_id"],
            "score": float(row["score"]),
        }
        for row in raw_rows
    ]
    return {
        "target": _pia_target_provenance(context, calibration, evaluation),
        "metrics": metrics,
        "evaluation_rows": evaluation_rows,
    }


def summarize_pia_heterogeneity(
    target_keys: Sequence[str],
    observed_aucs: Sequence[float],
    bootstrap_auc_vectors: Sequence[Sequence[float]],
    *,
    alpha: float,
    practical_range: float,
) -> dict[str, object]:
    """Summarize the sealed AUC-range null and all Holm-adjusted paired deltas."""

    keys = list(target_keys)
    observed = np.asarray(observed_aucs, dtype=float)
    draws = np.asarray(bootstrap_auc_vectors, dtype=float)
    if len(keys) < 2 or any(not isinstance(key, str) or not key for key in keys):
        raise ValueError("PIA heterogeneity requires at least two non-empty target keys")
    if len(set(keys)) != len(keys):
        raise ValueError("PIA heterogeneity target keys must be unique")
    if observed.ndim != 1 or observed.size != len(keys):
        raise ValueError("observed AUCs must match the target keys")
    if draws.ndim != 2 or draws.shape[1] != observed.size or draws.shape[0] == 0:
        raise ValueError("bootstrap AUC vectors must be a non-empty B by target matrix")
    if not np.isfinite(observed).all() or not np.isfinite(draws).all():
        raise ValueError("PIA heterogeneity AUC values must be finite")
    if bool(((observed < 0) | (observed > 1)).any()) or bool(((draws < 0) | (draws > 1)).any()):
        raise ValueError("PIA heterogeneity AUC values must lie in [0, 1]")
    if (
        isinstance(alpha, bool)
        or not isinstance(alpha, (int, float))
        or not math.isfinite(alpha)
        or not 0 < float(alpha) <= 1
    ):
        raise ValueError("alpha must be finite and lie in (0, 1]")
    if (
        isinstance(practical_range, bool)
        or not isinstance(practical_range, (int, float))
        or not math.isfinite(practical_range)
        or not 0 <= float(practical_range) <= 1
    ):
        raise ValueError("practical_range must be finite and lie in [0, 1]")

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
                "left": keys[left_index],
                "right": keys[right_index],
                "observed_delta": observed_delta,
                "test": "two_sided_centered_paired_bootstrap",
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
        row["decision"] = bool(adjusted[index] <= float(alpha))

    practical_gate = bool(observed_range >= float(practical_range))
    result = {
        "global": {
            "statistic": "auc_range",
            "null_centering": "target_observed_to_grand_mean",
            "observed_range": observed_range,
            "null_ranges": [float(value) for value in null_ranges],
            "p_value": global_p,
            "practical_range_at_least": float(practical_range),
            "practical_gate": practical_gate,
            "decision": bool(global_p <= float(alpha) and practical_gate),
        },
        "pairwise": pairwise,
        "correction": "holm",
    }
    json.dumps(result, allow_nan=False)
    return result


def _draw_pia_stratified_indices(
    packet: PiaScorePacket,
    rng: np.random.Generator,
) -> np.ndarray:
    draws: list[np.ndarray] = []
    for label in (0, 1):
        for class_id in range(10):
            indices = np.flatnonzero((packet.labels == label) & (packet.classes == class_id))
            if indices.size == 0:
                raise ValueError("PIA bootstrap requires every label/class stratum")
            draws.append(rng.choice(indices, size=indices.size, replace=True))
    return np.concatenate(draws).astype(int, copy=False)


def _percentile_interval(samples: Sequence[float]) -> list[float]:
    values = np.asarray(samples, dtype=float)
    return [float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))]


def _pia_target_key(calibration: PiaScorePacket) -> str:
    return str(calibration.provenance["checkpoint_sha256"])


def bootstrap_pia_checkpoints(
    sources: Sequence[TrustedPiaCheckpointSource],
    *,
    protocol_envelope: Mapping[str, object] | str | Path,
    expected_protocol_hash: str,
    n_bootstrap: int,
    random_state: int,
    analysis_mode: str,
    stage: str,
) -> dict[str, object]:
    """Run paired label/class-stratified PIA bootstrap draws for a sealed roster."""

    contract = paper1_pia_contract()
    expected_bootstrap = int(contract["bootstrap_replicates"])
    if type(n_bootstrap) is not int or n_bootstrap != expected_bootstrap:
        raise ValueError(f"n_bootstrap must equal the sealed protocol count {expected_bootstrap}")
    expected_random_state = int(contract["bootstrap_random_state"])
    if type(random_state) is not int or random_state != expected_random_state:
        raise ValueError(
            f"bootstrap random_state must equal the sealed protocol value {expected_random_state}"
        )
    context, validated, analysis_code_commit = _validate_pia_checkpoint_sources(
        sources,
        protocol_envelope=protocol_envelope,
        expected_protocol_hash=expected_protocol_hash,
        analysis_mode=analysis_mode,
        stage=stage,
    )
    keys = [_pia_target_key(calibration) for calibration, _ in validated]
    if len(set(keys)) != len(keys):
        raise ValueError("PIA checkpoint identities must be unique")
    target_samples: dict[str, list[float]] = {key: [] for key in keys}
    threshold_samples: dict[str, list[float]] = {key: [] for key in keys}
    observed_aucs: dict[str, float] = {}
    observed_thresholds: dict[str, float] = {}
    pair_samples: dict[tuple[str, str], list[float]] = {pair: [] for pair in combinations(keys, 2)}

    for key, (calibration, evaluation) in zip(keys, validated, strict=True):
        observed = evaluate_calibrated_packets(
            calibration.scores,
            calibration.labels,
            calibration.indices,
            evaluation.scores,
            evaluation.labels,
            evaluation.indices,
        )
        observed_aucs[key] = float(observed["evaluation_auc"])
        observed_thresholds[key] = float(observed["calibration_threshold"])

    rng = np.random.default_rng(random_state)
    paired_replicates: list[dict[str, object]] = []
    for replicate in range(n_bootstrap):
        calibration_draw = _draw_pia_stratified_indices(validated[0][0], rng)
        evaluation_draw = _draw_pia_stratified_indices(validated[0][1], rng)
        shared_rows = (
            validated[0][0].indices[calibration_draw].astype("<i8", copy=False).tobytes()
            + validated[0][1].indices[evaluation_draw].astype("<i8", copy=False).tobytes()
        )
        digest = hashlib.sha256(shared_rows).hexdigest()
        target_aucs: dict[str, float] = {}
        target_thresholds: dict[str, float] = {}
        for key, (calibration, evaluation) in zip(keys, validated, strict=True):
            evaluated = evaluate_calibrated_packets(
                calibration.scores[calibration_draw],
                calibration.labels[calibration_draw],
                calibration.indices[calibration_draw],
                evaluation.scores[evaluation_draw],
                evaluation.labels[evaluation_draw],
                evaluation.indices[evaluation_draw],
            )
            auc = float(evaluated["evaluation_auc"])
            threshold = float(evaluated["calibration_threshold"])
            target_samples[key].append(auc)
            threshold_samples[key].append(threshold)
            target_aucs[key] = auc
            target_thresholds[key] = threshold
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
                "target_calibration_thresholds": target_thresholds,
                "pairwise_auc_deltas": replicate_deltas,
            }
        )

    result = {
        "schema_version": 1,
        "protocol_hash": context.protocol_hash,
        **_analysis_provenance(context, analysis_code_commit),
        "analysis_mode": analysis_mode,
        "stage": stage,
        "heterogeneity_contract": context.heterogeneity_contract,
        "random_state": random_state,
        "n_bootstrap": n_bootstrap,
        "strata": ["calibration_or_evaluation", "label", "class"],
        "recalibrate_threshold_per_replicate": True,
        "targets": [
            {
                "target": _pia_target_provenance(context, calibration, evaluation),
                "observed_auc": observed_aucs[key],
                "observed_calibration_threshold": observed_thresholds[key],
                "auc_samples": target_samples[key],
                "auc_ci_95": _percentile_interval(target_samples[key]),
                "calibration_threshold_samples": threshold_samples[key],
            }
            for key, (calibration, evaluation) in zip(keys, validated, strict=True)
        ],
        "paired_replicates": paired_replicates,
        "pairwise_deltas": [
            {
                "left": left,
                "right": right,
                "observed_delta": observed_aucs[left] - observed_aucs[right],
                "samples": samples,
                "ci_95": _percentile_interval(samples),
            }
            for (left, right), samples in pair_samples.items()
        ],
        "heterogeneity_summary": summarize_pia_heterogeneity(
            keys,
            [observed_aucs[key] for key in keys],
            [[replicate["target_aucs"][key] for key in keys] for replicate in paired_replicates],
            alpha=float(context.heterogeneity_contract["global_test_alpha"]),
            practical_range=float(context.heterogeneity_contract["practical_auc_range_at_least"]),
        ),
    }
    json.dumps(result, allow_nan=False)
    return result


def _permuted_pia_membership_labels(
    packet: PiaScorePacket,
    rng: np.random.Generator,
) -> np.ndarray:
    labels = packet.labels.copy()
    for class_id in range(10):
        indices = np.flatnonzero(packet.classes == class_id)
        if indices.size == 0:
            raise ValueError("PIA permutation requires every class stratum")
        labels[indices] = rng.permutation(labels[indices])
    return labels


def full_label_permutation_test_pia(
    sources: Sequence[TrustedPiaCheckpointSource],
    *,
    protocol_envelope: Mapping[str, object] | str | Path,
    expected_protocol_hash: str,
    n_permutations: int,
    random_state: int,
    analysis_mode: str,
    stage: str,
    target_seed: int,
) -> dict[str, object]:
    """Run the sealed split/class-preserving PIA full membership-label null."""

    contract = paper1_pia_contract()
    expected_permutations = int(contract["permutation_replicates"])
    if type(n_permutations) is not int or n_permutations != expected_permutations:
        raise ValueError(
            f"n_permutations must equal the sealed protocol count {expected_permutations}"
        )
    expected_random_state = int(contract["permutation_random_state"])
    if type(random_state) is not int or random_state != expected_random_state:
        raise ValueError(
            f"permutation random_state must equal the sealed protocol value {expected_random_state}"
        )
    context, validated, analysis_code_commit = _validate_pia_checkpoint_sources(
        sources,
        protocol_envelope=protocol_envelope,
        expected_protocol_hash=expected_protocol_hash,
        analysis_mode=analysis_mode,
        stage=stage,
    )
    matches = [pair for pair in validated if int(pair[0].provenance["run_seed"]) == target_seed]
    if len(matches) != 1:
        raise ValueError("target_seed must identify exactly one target in the sealed roster")
    calibration, evaluation = matches[0]
    observed = evaluate_calibrated_packets(
        calibration.scores,
        calibration.labels,
        calibration.indices,
        evaluation.scores,
        evaluation.labels,
        evaluation.indices,
    )
    observed_auc = float(observed["evaluation_auc"])
    observed_threshold = float(observed["calibration_threshold"])

    rng = np.random.default_rng(random_state)
    null_aucs: list[float] = []
    null_thresholds: list[float] = []
    for _ in range(n_permutations):
        calibration_labels = _permuted_pia_membership_labels(calibration, rng)
        evaluation_labels = _permuted_pia_membership_labels(evaluation, rng)
        permuted = evaluate_calibrated_packets(
            calibration.scores,
            calibration_labels,
            calibration.indices,
            evaluation.scores,
            evaluation_labels,
            evaluation.indices,
        )
        null_aucs.append(float(permuted["evaluation_auc"]))
        null_thresholds.append(float(permuted["calibration_threshold"]))
    exceedances = sum(value >= observed_auc for value in null_aucs)
    result = {
        "schema_version": 1,
        "protocol_hash": context.protocol_hash,
        **_analysis_provenance(context, analysis_code_commit),
        "target": _pia_target_provenance(context, calibration, evaluation),
        "score_direction": "higher_is_member",
        "permutation_scheme": "within_each_split_and_class",
        "random_state": random_state,
        "n_permutations": n_permutations,
        "observed_auc": observed_auc,
        "observed_calibration_threshold": observed_threshold,
        "null_aucs": null_aucs,
        "null_calibration_thresholds": null_thresholds,
        "p_value": float((exceedances + 1) / (n_permutations + 1)),
        "p_value_correction": "plus_one",
        "recalibrate_threshold_per_permutation": True,
    }
    json.dumps(result, allow_nan=False)
    return result


def score_pia_checkpoints(
    sources: Sequence[TrustedPiaCheckpointSource],
    *,
    protocol_envelope: Mapping[str, object] | str | Path,
    expected_protocol_hash: str,
    analysis_mode: str | None = None,
    stage: str | None = None,
) -> dict[str, object]:
    """Validate one checkpoint or one complete sealed same-step PIA roster."""

    context, validated, analysis_code_commit = _validate_pia_checkpoint_sources(
        sources,
        protocol_envelope=protocol_envelope,
        expected_protocol_hash=expected_protocol_hash,
        analysis_mode=analysis_mode,
        stage=stage,
    )
    result = {
        "schema_version": 1,
        "protocol_hash": context.protocol_hash,
        **_analysis_provenance(context, analysis_code_commit),
        "analysis_mode": analysis_mode or "single_checkpoint",
        "stage": stage,
        "scorer_contract": context.pia_contract,
        "score_direction": "higher_is_member",
        "targets": [
            _score_pia_packet_pair(context, calibration, evaluation)
            for calibration, evaluation in validated
        ],
    }
    json.dumps(result, allow_nan=False)
    return result


def build_pia_score_packet(
    context: PiaProtocolContext,
    *,
    calibration_or_evaluation: Literal["calibration", "evaluation"],
    scores_by_index: Mapping[int, float],
    packet_purpose: str,
    training_identity: PiaTrainingIdentity,
    training_output_manifest: str | Path,
    device: str,
    batch_size: int,
    weights_key: str,
    upstream_verification: Mapping[str, object],
) -> dict[str, object]:
    """Build and self-validate the sole canonical exporter packet shape."""

    validate_pia_stage_identity(
        context,
        stage=training_identity.stage,
        run_seed=training_identity.run_seed,
        step=training_identity.step,
        packet_purpose=packet_purpose,
    )
    extraction_contract = context.pia_contract["extraction"]
    upstream_contract = context.pia_contract["upstream"]
    assert isinstance(extraction_contract, dict) and isinstance(upstream_contract, dict)
    expected_upstream = {**upstream_contract, "git_clean": True}
    _require_exact_value("extraction.device", device, extraction_contract["device"])
    _require_exact_value("extraction.batch_size", batch_size, extraction_contract["batch_size"])
    _require_exact_value("extraction.weights_key", weights_key, extraction_contract["weights_key"])
    _require_exact_value("extraction.upstream", dict(upstream_verification), expected_upstream)
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
        "run_seed": training_identity.run_seed,
        "step": training_identity.step,
        "checkpoint_sha256": training_identity.checkpoint_sha256,
        "training_manifest_sha256": training_identity.training_manifest_sha256,
        "target_code_commit": context.code_commit,
        "scorer_code_commit": training_identity.scorer_code_commit,
        "split_sha256": context.split_sha256,
        "protocol_hash": context.protocol_hash,
        "extraction": {
            "packet_purpose": packet_purpose,
            "device": device,
            "batch_size": batch_size,
            "weights_key": weights_key,
            "evaluator_environment": extraction_contract["evaluator_environment"],
            "upstream": dict(upstream_verification),
            "checkpoint_filename": training_identity.checkpoint_filename,
            "run_label": training_identity.run_label,
            "training_config_hash": training_identity.training_config_hash,
        },
        "rows": rows,
    }
    return validate_pia_score_packet(
        payload,
        expected_role=calibration_or_evaluation,
        context=context,
        training_output_manifest=training_output_manifest,
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
    observed_candidates = np.unique(score_values)[::-1]
    all_negative_threshold = np.nextafter(observed_candidates[0], np.inf)
    if not np.isfinite(all_negative_threshold):
        raise ValueError("scores are too large to construct a finite all-negative threshold")
    candidates = np.concatenate(([all_negative_threshold], observed_candidates))
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

    contract = paper1_pia_contract()
    gate = contract["positive_control_gate"]
    assert isinstance(gate, dict)
    for name, labels, member_key, nonmember_key in (
        (
            "calibration",
            calibration_labels,
            "calibration_member_count",
            "calibration_nonmember_count",
        ),
        (
            "evaluation",
            evaluation_labels,
            "evaluation_member_count",
            "evaluation_nonmember_count",
        ),
    ):
        _, validated_labels = _validated_score_labels(
            calibration_scores if name == "calibration" else evaluation_scores,
            labels,
        )
        member_count = int((validated_labels == 1).sum())
        nonmember_count = int((validated_labels == 0).sum())
        if member_count != int(gate[member_key]) or nonmember_count != int(gate[nonmember_key]):
            raise ValueError(
                f"positive-control {name} split requires exactly 128 members and 128 nonmembers"
            )

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
