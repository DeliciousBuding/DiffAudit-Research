"""Protocol-bound H1 activation feature extraction primitives."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn

from diffaudit.evidence.corrected_protocol import derive_noise_seed

_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
_COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")
_SITE_PATHS: dict[str, tuple[str, ...]] = {
    "late_down": ("downblocks", "-1"),
    "mid_0": ("middleblocks", "0"),
    "mid_1": ("middleblocks", "1"),
    "early_up": ("upblocks", "0"),
}
_CHECKPOINT_FIELDS = {"model", "ema", "optim", "sched", "step", "metadata", "rng_state"}
_METADATA_FIELDS = {
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
_MANIFEST_FIELDS = {
    "protocol_hash",
    "split_sha256",
    "code_commit",
    "seed",
    "run_label",
    "step",
    "checkpoint",
    "member_count",
    "batch_size",
    "training_config",
    "training_config_hash",
    "environment",
    "checkpoint_receipts",
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


def sha256_file(path: str | Path, *, chunk_size: int = 8 * 1024 * 1024) -> str:
    """Hash a file with bounded memory."""

    if type(chunk_size) is not int or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer")
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class CheckpointProvenance:
    checkpoint_sha256: str
    training_manifest_sha256: str
    target_code_commit: str
    protocol_hash: str
    split_sha256: str
    training_config_hash: str
    run_seed: int
    step: int
    run_label: str


@dataclass(frozen=True, slots=True)
class CheckpointBundle:
    ema_state_dict: Mapping[str, Any]
    provenance: CheckpointProvenance


@dataclass(frozen=True, slots=True)
class ExtractionResult:
    rows: list[dict[str, object]]
    pca_features: np.ndarray
    scalar_features: np.ndarray


def _resolve_module(model: nn.Module, path: Sequence[str]) -> nn.Module:
    target: Any = model
    for part in path:
        target = target[int(part)] if part.lstrip("-").isdigit() else getattr(target, part)
    if not isinstance(target, nn.Module):
        raise ValueError("H1 site path did not resolve to a torch module")
    return target


class ActivationHookCollector:
    """Collect exactly one finite activation for every frozen H1 site and query."""

    def __init__(
        self,
        model: nn.Module,
        site_paths: Mapping[str, Sequence[str]] = _SITE_PATHS,
    ) -> None:
        self._site_paths = dict(site_paths)
        self._activations: dict[str, list[torch.Tensor]] = {}
        self._expected_batch: int | None = None
        self._handles = [
            _resolve_module(model, path).register_forward_hook(self._hook(site))
            for site, path in self._site_paths.items()
        ]

    def _hook(self, site: str):
        def capture(_module: nn.Module, _inputs: tuple[Any, ...], output: Any) -> None:
            if not isinstance(output, torch.Tensor):
                raise ValueError(f"H1 site {site} did not emit a tensor activation")
            self._activations.setdefault(site, []).append(output.detach())

        return capture

    def begin_query(self, *, expected_batch: int) -> None:
        if type(expected_batch) is not int or expected_batch <= 0:
            raise ValueError("expected_batch must be a positive integer")
        self._activations = {}
        self._expected_batch = expected_batch

    def finish_query(self) -> dict[str, torch.Tensor]:
        if self._expected_batch is None:
            raise ValueError("begin_query must be called before finish_query")
        result: dict[str, torch.Tensor] = {}
        for site in self._site_paths:
            captured = self._activations.get(site, [])
            if len(captured) != 1:
                raise ValueError(f"H1 site {site} must emit exactly one activation per query")
            activation = captured[0]
            if activation.ndim < 2 or activation.shape[0] != self._expected_batch:
                raise ValueError(f"H1 site {site} activation batch dimension is invalid")
            if not torch.isfinite(activation).all().item():
                raise ValueError(f"H1 site {site} activation must be finite")
            result[site] = activation
        self._expected_batch = None
        return result

    def close(self) -> None:
        for handle in self._handles:
            handle.remove()
        self._handles.clear()

    def __enter__(self) -> ActivationHookCollector:
        return self

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        self.close()


def _validate_feature_definition(definition: Mapping[str, object]) -> tuple[list[str], list[int]]:
    sites = definition.get("sites")
    timesteps = definition.get("timesteps")
    channels = definition.get("channels_per_site")
    if (
        not isinstance(sites, list)
        or sites != list(_SITE_PATHS)
        or not isinstance(timesteps, list)
        or timesteps != [100, 400, 700]
        or not isinstance(channels, Mapping)
    ):
        raise ValueError("H1 feature definition does not match the frozen site/timestep layout")
    for site in sites:
        value = channels.get(site)
        if type(value) is not int or value <= 0:
            raise ValueError("H1 feature definition channels_per_site is invalid")
    expected_orders = {
        "pca_feature_order": "site_then_timestep_then_statistic_then_channel",
        "scalar_feature_order": "timestep_then_site_then_statistic",
        "lr_feature_order": ["scalar_features", "pca_components"],
    }
    if any(definition.get(name) != expected for name, expected in expected_orders.items()):
        raise ValueError("H1 feature definition column order does not match the frozen contract")
    return sites, timesteps


def compute_activation_features(
    activations: Mapping[tuple[str, int], torch.Tensor],
    feature_definition: Mapping[str, object],
) -> tuple[np.ndarray, np.ndarray]:
    """Compute the scout's sample-level per-channel and scalar activation statistics."""

    sites, timesteps = _validate_feature_definition(feature_definition)
    channels = feature_definition["channels_per_site"]
    pca_parts: list[torch.Tensor] = []
    scalar_parts: list[torch.Tensor] = []
    statistics: dict[tuple[str, int], tuple[torch.Tensor, torch.Tensor, torch.Tensor]] = {}
    batch_size: int | None = None
    for site in sites:
        for timestep in timesteps:
            activation = activations.get((site, timestep))
            if not isinstance(activation, torch.Tensor) or activation.ndim < 3:
                raise ValueError(f"missing or invalid activation for {site} at timestep {timestep}")
            if activation.shape[1] != channels[site]:
                raise ValueError(f"activation channel count for {site} does not match the protocol")
            if batch_size is None:
                batch_size = int(activation.shape[0])
            if activation.shape[0] != batch_size:
                raise ValueError("activation batch dimensions must agree across all H1 queries")
            if not torch.isfinite(activation).all().item():
                raise ValueError("activation features require finite activations")
            flat = activation.detach().to(device="cpu", dtype=torch.float32).flatten(start_dim=2)
            mu_abs = flat.abs().mean(dim=-1)
            variance = flat.var(dim=-1, unbiased=False)
            threshold = 0.01 * flat.std(dim=-1, unbiased=False)
            sparsity = (flat.abs() < threshold.unsqueeze(-1)).to(torch.float32).mean(dim=-1)
            statistics[(site, timestep)] = (mu_abs, variance, sparsity)
            pca_parts.extend((mu_abs, variance, sparsity))
    for timestep in timesteps:
        for site in sites:
            scalar_parts.extend(
                statistic.mean(dim=1, keepdim=True) for statistic in statistics[(site, timestep)]
            )
    pca_features = torch.cat(pca_parts, dim=1)
    scalar_features = torch.cat(scalar_parts, dim=1)
    expected_pca = feature_definition.get("pca_input_dimension")
    expected_scalar = feature_definition.get("scalar_feature_dimension")
    if pca_features.shape[1] != expected_pca or scalar_features.shape[1] != expected_scalar:
        raise ValueError("realized H1 feature dimensions do not match the frozen protocol")
    return pca_features.numpy(), scalar_features.numpy()


def build_common_noise(
    sample_shape: Sequence[int],
    protocol_namespace: str,
    dataset_indices: Sequence[int],
    timestep: int,
    draw: int,
    *,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    """Generate row-bound noise on CPU so batching, order, and device cannot change it."""

    rows: list[torch.Tensor] = []
    for dataset_index in dataset_indices:
        generator = torch.Generator(device="cpu")
        generator.manual_seed(
            derive_noise_seed(protocol_namespace, int(dataset_index), int(timestep), int(draw))
        )
        rows.append(
            torch.randn(tuple(sample_shape), generator=generator, dtype=dtype, device="cpu")
        )
    return torch.stack(rows, dim=0)


def _noise_id(namespace: str, dataset_index: int, timesteps: Sequence[int]) -> dict[str, object]:
    return {
        "namespace": namespace,
        "dataset_index": dataset_index,
        "entries": [
            {
                "timestep": timestep,
                "draw": 0,
                "seed": derive_noise_seed(namespace, dataset_index, timestep, 0),
            }
            for timestep in timesteps
        ],
    }


def extract_locked_rows(
    model: nn.Module,
    dataset: Any,
    locked_rows: Sequence[Mapping[str, object]],
    *,
    feature_definition: Mapping[str, object],
    protocol_namespace: str,
    batch_size: int,
    device: torch.device,
) -> ExtractionResult:
    """Extract row-bound features by direct dataset index, never loader position."""

    sites, timesteps = _validate_feature_definition(feature_definition)
    del sites
    if type(batch_size) is not int or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")
    if not hasattr(model, "alphas_cumprod"):
        raise ValueError("target model must expose alphas_cumprod")
    output_rows: list[dict[str, object]] = []
    pca_batches: list[np.ndarray] = []
    scalar_batches: list[np.ndarray] = []
    model.eval()
    with ActivationHookCollector(model) as collector, torch.no_grad():
        for start in range(0, len(locked_rows), batch_size):
            batch_rows = locked_rows[start : start + batch_size]
            images: list[torch.Tensor] = []
            dataset_indices: list[int] = []
            for raw_row in batch_rows:
                dataset_index = raw_row.get("dataset_index")
                if type(dataset_index) is not int or dataset_index < 0:
                    raise ValueError("locked dataset_index must be a non-negative integer")
                image, class_id = dataset[dataset_index]
                if not isinstance(image, torch.Tensor) or image.ndim != 3:
                    raise ValueError("CIFAR10 dataset rows must return CHW tensors")
                if (
                    not torch.isfinite(image).all().item()
                    or image.min().item() < 0.0
                    or image.max().item() > 1.0
                ):
                    raise ValueError("CIFAR10 tensors must use the ToTensor source range [0, 1]")
                if int(class_id) != raw_row.get("class_id"):
                    raise ValueError("dataset class does not match locked protocol class")
                images.append(image.to(dtype=torch.float32))
                dataset_indices.append(dataset_index)
            clean = torch.stack(images, dim=0).mul(2.0).sub(1.0)
            query_activations: dict[tuple[str, int], torch.Tensor] = {}
            for timestep in timesteps:
                noise = build_common_noise(
                    clean.shape[1:],
                    protocol_namespace,
                    dataset_indices,
                    timestep,
                    0,
                    dtype=clean.dtype,
                )
                alpha = model.alphas_cumprod[timestep].detach().to(device="cpu", dtype=clean.dtype)
                noisy = alpha.sqrt() * clean + (1.0 - alpha).sqrt() * noise
                noisy = noisy.to(device)
                timestep_tensor = torch.full(
                    (len(batch_rows),), timestep, dtype=torch.long, device=device
                )
                collector.begin_query(expected_batch=len(batch_rows))
                model(noisy, timestep_tensor)
                for site, activation in collector.finish_query().items():
                    query_activations[(site, timestep)] = activation
            pca_features, scalar_features = compute_activation_features(
                query_activations, feature_definition
            )
            pca_batches.append(pca_features.astype(np.float32, copy=False))
            scalar_batches.append(scalar_features.astype(np.float32, copy=False))
            for offset, raw_row in enumerate(batch_rows):
                dataset_index = dataset_indices[offset]
                output_rows.append(
                    {
                        "dataset_index": dataset_index,
                        "label": raw_row["label"],
                        "class": raw_row["class_id"],
                        "calibration_or_evaluation": raw_row["split"],
                        "noise_id": _noise_id(protocol_namespace, dataset_index, timesteps),
                    }
                )
    return ExtractionResult(
        rows=output_rows,
        pca_features=np.concatenate(pca_batches, axis=0),
        scalar_features=np.concatenate(scalar_batches, axis=0),
    )


def _canonical_training_config_hash(value: Mapping[str, object]) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    ).hexdigest()


def _require_hash(name: str, value: object, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise ValueError(f"{name} has invalid hash format")
    return value


def validate_checkpoint_bundle(
    checkpoint_path: str | Path,
    training_manifest_path: str | Path,
    *,
    expected_protocol_hash: str,
    expected_split_sha256: str,
    expected_target_code_commit: str,
    expected_training_config_hash: str,
    packet_purpose: str,
    preflight: bool,
) -> CheckpointBundle:
    """Validate a corrected checkpoint against weights-only metadata and its receipt."""

    checkpoint_path = Path(checkpoint_path)
    manifest_path = Path(training_manifest_path)
    checkpoint_sha256 = sha256_file(checkpoint_path)
    training_manifest_sha256 = sha256_file(manifest_path)
    try:
        with manifest_path.open("r", encoding="utf-8") as handle:
            manifest = json.load(handle)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("training manifest must contain valid JSON") from error
    if not isinstance(manifest, Mapping):
        raise ValueError("training manifest must contain a JSON mapping")
    if set(manifest) != _MANIFEST_FIELDS:
        raise ValueError("training manifest fields do not match the exact corrected schema")
    payload = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    if not isinstance(payload, Mapping) or set(payload) != _CHECKPOINT_FIELDS:
        raise ValueError("checkpoint payload fields do not match the corrected schema")
    metadata = payload.get("metadata")
    if not isinstance(metadata, Mapping) or set(metadata) != _METADATA_FIELDS:
        raise ValueError("checkpoint metadata fields do not match the corrected schema")
    training_config = metadata.get("training_config")
    if not isinstance(training_config, Mapping):
        raise ValueError("checkpoint training_config is invalid")
    realized_config_hash = _canonical_training_config_hash(training_config)
    expected_values = {
        "protocol_hash": expected_protocol_hash,
        "split_sha256": expected_split_sha256,
        "code_commit": expected_target_code_commit,
        "training_config_hash": expected_training_config_hash,
    }
    for field, expected in expected_values.items():
        if metadata.get(field) != expected or manifest.get(field) != expected:
            raise ValueError(f"checkpoint or training manifest {field} does not match source truth")
    if realized_config_hash != expected_training_config_hash:
        raise ValueError("checkpoint training_config_hash does not match training_config")
    if manifest.get("training_config") != training_config:
        raise ValueError("training manifest config does not match checkpoint metadata")
    if manifest.get("environment") != metadata.get("environment"):
        raise ValueError("training manifest environment does not match checkpoint metadata")
    config_data = training_config.get("data")
    expected_batch_size = (
        config_data.get("batch_size")
        if isinstance(config_data, Mapping)
        else training_config.get("batch_size")
    )
    if manifest.get("member_count") != 25_000:
        raise ValueError("training manifest member_count must equal 25000")
    if manifest.get("batch_size") != expected_batch_size:
        raise ValueError("training manifest batch_size does not match checkpoint config")
    step = metadata.get("checkpoint_step")
    seed = metadata.get("seed")
    run_label = metadata.get("run_label")
    if (
        type(step) is not int
        or step <= 0
        or payload.get("step") != step
        or manifest.get("step") != step
        or type(seed) is not int
        or seed <= 0
        or manifest.get("seed") != seed
        or not isinstance(run_label, str)
        or manifest.get("run_label") != run_label
        or manifest.get("checkpoint") != checkpoint_path.name
    ):
        raise ValueError("checkpoint identity does not match training manifest")
    if packet_purpose == "preflight_benchmark":
        if not preflight or step > 5000 or "corrected" not in run_label:
            raise ValueError(
                "preflight benchmark requires --preflight, corrected label, and step <= 5000"
            )
    elif packet_purpose == "corrected_evaluation":
        if preflight or step not in (100_000, 200_000):
            raise ValueError("corrected evaluation requires a frozen 100k or 200k checkpoint")
    else:
        raise ValueError("unsupported H1 packet_purpose")
    receipts = manifest.get("checkpoint_receipts")
    receipt = receipts.get(checkpoint_path.name) if isinstance(receipts, Mapping) else None
    if not isinstance(receipt, Mapping) or set(receipt) != _RECEIPT_FIELDS:
        raise ValueError("checkpoint receipt is missing or malformed")
    expected_receipt = {
        "checkpoint_sha256": checkpoint_sha256,
        "protocol_hash": expected_protocol_hash,
        "code_commit": expected_target_code_commit,
        "run_seed": seed,
        "step": step,
        "run_label": run_label,
        "training_config_hash": expected_training_config_hash,
    }
    if dict(receipt) != expected_receipt:
        raise ValueError("checkpoint receipt does not match checkpoint and manifest")
    ema_state = payload.get("ema")
    if not isinstance(ema_state, Mapping):
        raise ValueError("checkpoint ema state must be a mapping")
    return CheckpointBundle(
        ema_state_dict=ema_state,
        provenance=CheckpointProvenance(
            checkpoint_sha256=checkpoint_sha256,
            training_manifest_sha256=training_manifest_sha256,
            target_code_commit=expected_target_code_commit,
            protocol_hash=expected_protocol_hash,
            split_sha256=expected_split_sha256,
            training_config_hash=expected_training_config_hash,
            run_seed=seed,
            step=step,
            run_label=run_label,
        ),
    )


def validate_h1_repository_state(
    head: str,
    tracked_status: str,
    relevant_untracked: tuple[str, ...],
    *,
    expected_scorer_commit: str,
) -> str:
    _require_hash("expected_scorer_commit", expected_scorer_commit, _COMMIT_RE)
    if head != expected_scorer_commit:
        raise ValueError("repository HEAD does not match expected scorer commit")
    if tracked_status.strip():
        raise ValueError("repository has tracked worktree changes")
    if relevant_untracked:
        raise ValueError("repository has relevant untracked scorer code or configuration")
    return head


def read_h1_repository_state(root: str | Path) -> tuple[str, str, tuple[str, ...]]:
    repository = Path(root)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    tracked = subprocess.run(
        ["git", "status", "--short", "--untracked-files=no"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    relevant = subprocess.run(
        [
            "git",
            "status",
            "--short",
            "--untracked-files=all",
            "--",
            "src",
            "configs",
            "training",
            "scripts",
        ],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    suffixes = {".py", ".yaml", ".yml", ".toml"}
    untracked = tuple(
        line[3:].strip()
        for line in relevant.splitlines()
        if line.startswith("?? ") and Path(line[3:].strip()).suffix.lower() in suffixes
    )
    return head, tracked, untracked


def validate_h1_extraction_runtime(
    extraction_config: Mapping[str, object],
    *,
    batch_size: int,
    device: str,
    evaluator_environment: Mapping[str, object],
) -> None:
    from diffaudit.evidence.training_config import build_training_config

    if extraction_config.get("batch_size") != 16 or batch_size != 16:
        raise ValueError("H1 extraction batch_size must equal the protocol-frozen value 16")
    if (
        extraction_config.get("device_policy") != "cuda_required_for_confirmatory"
        or device != "cuda"
    ):
        raise ValueError("H1 extraction device_policy requires the exact cuda device")
    if extraction_config.get("determinism") != dict(build_training_config().determinism):
        raise ValueError("H1 extraction determinism does not match the complete policy")
    if extraction_config.get("evaluator_environment") != dict(evaluator_environment):
        raise ValueError("H1 extraction evaluator_environment does not match the sealed protocol")


def build_benchmark_summary(
    *,
    rows: int,
    queries: int,
    end_to_end_seconds: float,
    extraction_seconds: float,
    phase_timings: Mapping[str, float],
    peak_cuda_allocated_bytes: int,
    peak_cuda_reserved_bytes: int,
    packet_path: str,
    packet_sha256: str,
) -> dict[str, object]:
    """Build the only permitted outcome-blind preflight stdout payload."""

    expected_phases = {
        "identity_protocol",
        "checkpoint_hash_load",
        "model_to_device",
        "dataset_load",
        "extraction",
        "packet_write_hash",
    }
    if (
        rows <= 0
        or queries <= 0
        or end_to_end_seconds <= 0
        or extraction_seconds <= 0
        or set(phase_timings) != expected_phases
        or any(type(value) not in (int, float) or value < 0 for value in phase_timings.values())
    ):
        raise ValueError("benchmark timing inputs must be positive")
    if not math.isclose(
        float(phase_timings["extraction"]), extraction_seconds, rel_tol=0.0, abs_tol=1e-9
    ):
        raise ValueError("phase_timings extraction must equal extraction_seconds")
    _require_hash("packet_sha256", packet_sha256, _SHA256_RE)
    return {
        "rows": rows,
        "queries": queries,
        "end_to_end_seconds": end_to_end_seconds,
        "extraction_seconds": extraction_seconds,
        "phase_timings": dict(phase_timings),
        "rows_per_second": rows / extraction_seconds,
        "peak_cuda_allocated_bytes": peak_cuda_allocated_bytes,
        "peak_cuda_reserved_bytes": peak_cuda_reserved_bytes,
        "packet_path": packet_path,
        "packet_sha256": packet_sha256,
    }


def _atomic_bytes(path: Path, payload: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def write_h1_feature_packet(
    output_dir: str | Path,
    *,
    packet_purpose: str,
    provenance: Mapping[str, object],
    rows: Sequence[Mapping[str, object]],
    pca_features: np.ndarray,
    scalar_features: np.ndarray,
) -> dict[str, object]:
    """Write the v2 manifest/NPZ packet, publishing the manifest last."""

    if packet_purpose not in {"corrected_evaluation", "preflight_benchmark"}:
        raise ValueError("unsupported H1 packet purpose")
    pca = np.asarray(pca_features)
    scalar = np.asarray(scalar_features)
    if (
        pca.dtype != np.float32
        or scalar.dtype != np.float32
        or pca.ndim != 2
        or scalar.ndim != 2
        or pca.shape[0] != len(rows)
        or scalar.shape[0] != len(rows)
        or not np.isfinite(pca).all()
        or not np.isfinite(scalar).all()
    ):
        raise ValueError(
            "H1 packet arrays and metadata must be finite JSON-aligned float32 matrices"
        )
    dataset_indices = np.asarray([row.get("dataset_index") for row in rows], dtype=np.int64)
    if dataset_indices.shape != (len(rows),):
        raise ValueError("H1 packet row identities are invalid")
    try:
        json.dumps({"provenance": provenance, "rows": rows}, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError("H1 packet arrays and metadata must be finite JSON-safe values") from error

    destination = Path(output_dir)
    if destination.exists():
        raise FileExistsError(f"H1 packet output already exists: {destination}")
    destination.mkdir(parents=True)
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=".features.", suffix=".tmp", dir=destination
        )
        os.close(descriptor)
        temporary_features = Path(temporary_name)
        try:
            with temporary_features.open("wb") as handle:
                np.savez(
                    handle,
                    pca_features=pca,
                    scalar_features=scalar,
                    dataset_indices=dataset_indices,
                )
                handle.flush()
                os.fsync(handle.fileno())
            features_path = destination / "features.npz"
            os.replace(temporary_features, features_path)
        except BaseException:
            temporary_features.unlink(missing_ok=True)
            raise
        features_sha256 = sha256_file(features_path)
        manifest = {
            "schema_version": 1,
            "packet_format": "h1-feature-packet-v2",
            "packet_purpose": packet_purpose,
            "provenance": dict(provenance),
            "rows": [dict(row) for row in rows],
            "features": {
                "file": "features.npz",
                "sha256": features_sha256,
                "arrays": {
                    "dataset_indices": {"shape": [len(rows)], "dtype": "int64"},
                    "pca_features": {"shape": list(pca.shape), "dtype": "float32"},
                    "scalar_features": {"shape": list(scalar.shape), "dtype": "float32"},
                },
            },
        }
        encoded = (json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(
            "utf-8"
        )
        _atomic_bytes(destination / "manifest.json", encoded)
        return manifest
    except BaseException:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def load_h1_feature_packet(packet_dir: str | Path) -> dict[str, object]:
    """Load and strictly verify a v2 packet directory before scientific use."""

    root = Path(packet_dir)
    try:
        manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("H1 packet manifest must contain valid JSON") from error
    required = {
        "schema_version",
        "packet_format",
        "packet_purpose",
        "provenance",
        "rows",
        "features",
    }
    if not isinstance(manifest, Mapping) or set(manifest) != required:
        raise ValueError("H1 packet manifest fields do not match the v2 schema")
    if manifest["schema_version"] != 1 or manifest["packet_format"] != "h1-feature-packet-v2":
        raise ValueError("H1 packet manifest version or format is invalid")
    rows = manifest["rows"]
    feature_manifest = manifest["features"]
    if (
        not isinstance(rows, list)
        or not isinstance(feature_manifest, Mapping)
        or set(feature_manifest) != {"file", "sha256", "arrays"}
        or feature_manifest["file"] != "features.npz"
        or not isinstance(feature_manifest["sha256"], str)
        or _SHA256_RE.fullmatch(feature_manifest["sha256"]) is None
    ):
        raise ValueError("H1 packet feature manifest is invalid")
    features_path = root / "features.npz"
    try:
        with features_path.open("rb") as handle:
            digest = hashlib.sha256()
            for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
                digest.update(chunk)
            if digest.hexdigest() != feature_manifest["sha256"]:
                raise ValueError("H1 packet features hash does not match manifest")
            handle.seek(0)
            with np.load(handle, allow_pickle=False) as arrays:
                if set(arrays.files) != {"dataset_indices", "pca_features", "scalar_features"}:
                    raise ValueError("H1 packet NPZ arrays do not match the exact schema")
                dataset_indices = np.asarray(arrays["dataset_indices"])
                pca = np.asarray(arrays["pca_features"])
                scalar = np.asarray(arrays["scalar_features"])
    except (OSError, ValueError) as error:
        raise ValueError("H1 packet NPZ is invalid or truncated") from error
    array_manifest = feature_manifest["arrays"]
    realized = {
        "dataset_indices": {
            "shape": list(dataset_indices.shape),
            "dtype": str(dataset_indices.dtype),
        },
        "pca_features": {"shape": list(pca.shape), "dtype": str(pca.dtype)},
        "scalar_features": {"shape": list(scalar.shape), "dtype": str(scalar.dtype)},
    }
    if array_manifest != realized:
        raise ValueError("H1 packet NPZ dtype or shape does not match manifest")
    if (
        dataset_indices.dtype != np.int64
        or pca.dtype != np.float32
        or scalar.dtype != np.float32
        or pca.ndim != 2
        or scalar.ndim != 2
        or pca.shape[0] != len(rows)
        or scalar.shape[0] != len(rows)
        or not np.isfinite(pca).all()
        or not np.isfinite(scalar).all()
    ):
        raise ValueError("H1 packet NPZ arrays are nonfinite or structurally invalid")
    manifest_indices = np.asarray([row.get("dataset_index") for row in rows], dtype=np.int64)
    if not np.array_equal(dataset_indices, manifest_indices):
        raise ValueError("H1 packet row alignment does not match NPZ dataset indices")
    return {
        "schema_version": manifest["schema_version"],
        "packet_format": manifest["packet_format"],
        "packet_purpose": manifest["packet_purpose"],
        "provenance": manifest["provenance"],
        "rows": rows,
        "pca_features": pca,
        "scalar_features": scalar,
    }


__all__ = [
    "ActivationHookCollector",
    "CheckpointBundle",
    "CheckpointProvenance",
    "ExtractionResult",
    "build_benchmark_summary",
    "build_common_noise",
    "compute_activation_features",
    "extract_locked_rows",
    "load_h1_feature_packet",
    "read_h1_repository_state",
    "sha256_file",
    "validate_checkpoint_bundle",
    "validate_h1_extraction_runtime",
    "validate_h1_repository_state",
    "write_h1_feature_packet",
]
