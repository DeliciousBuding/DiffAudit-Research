"""Contract-bound primitives for corrected Paper 1 DDPM training."""

from __future__ import annotations

import functools
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset, Subset

from diffaudit.evidence.corrected_protocol import verify_paper1_contract
from diffaudit.training.exact_resume import (
    DeterministicEpochBatchSampler,
    capture_rng_state,
    restore_rng_state,
    validate_resume_identity,
)

_SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
_COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")
_RUN_LABEL_RE = re.compile(r"corrected-(?:[a-z0-9]+-)*s([0-9]+)(?:-[a-z0-9]+)*\Z")
_SEED_TOKEN_RE = re.compile(r"(?:(?<=-)|^)s([0-9]+)(?=-|$)")


@dataclass(frozen=True, slots=True)
class CorrectedTrainingContract:
    protocol_hash: str
    split_sha256: str
    code_commit: str
    seed: int
    run_label: str
    training_seeds: tuple[int, ...]
    member_indices: tuple[int, ...]


def _freeze_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    frozen: dict[str, object] = {}
    for key, item in value.items():
        if isinstance(item, Mapping):
            frozen[key] = _freeze_mapping(item)
        elif isinstance(item, list | tuple):
            frozen[key] = tuple(item)
        else:
            frozen[key] = item
    return MappingProxyType(frozen)


def _thaw_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _thaw_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_value(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class TrainingConfig:
    precision: Mapping[str, object]
    model: Mapping[str, object]
    diffusion: Mapping[str, object]
    optimizer: Mapping[str, object]
    scheduler: Mapping[str, object]
    ema_decay: float
    grad_clip: float
    transform: Mapping[str, object]
    data: Mapping[str, object]
    determinism: Mapping[str, object]
    checkpointing: Mapping[str, object]
    runtime: Mapping[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "precision": _thaw_value(self.precision),
            "model": _thaw_value(self.model),
            "diffusion": _thaw_value(self.diffusion),
            "optimizer": _thaw_value(self.optimizer),
            "scheduler": _thaw_value(self.scheduler),
            "ema_decay": self.ema_decay,
            "grad_clip": self.grad_clip,
            "transform": _thaw_value(self.transform),
            "data": _thaw_value(self.data),
            "determinism": _thaw_value(self.determinism),
            "checkpointing": _thaw_value(self.checkpointing),
            "runtime": _thaw_value(self.runtime),
        }


def build_training_config(*, num_workers: int) -> TrainingConfig:
    if type(num_workers) is not int or num_workers < 0:
        raise ValueError("num_workers must be a non-negative integer")
    return TrainingConfig(
        precision=_freeze_mapping({"dtype": "float32", "amp": False}),
        model=_freeze_mapping(
            {
                "architecture": "UNet",
                "T": 1_000,
                "channels": 128,
                "channel_multipliers": [1, 2, 2, 2],
                "attention_levels": [1],
                "num_res_blocks": 2,
                "dropout": 0.1,
            }
        ),
        diffusion=_freeze_mapping(
            {
                "schedule": "linear",
                "timesteps": 1_000,
                "beta_1": 0.0001,
                "beta_T": 0.02,
                "mean_type": "epsilon",
                "variance_type": "fixedlarge",
            }
        ),
        optimizer=_freeze_mapping(
            {"name": "Adam", "learning_rate": 0.0002, "betas": [0.9, 0.999], "eps": 1e-8}
        ),
        scheduler=_freeze_mapping(
            {"name": "LambdaLR", "policy": "linear_warmup", "warmup_steps": 5_000}
        ),
        ema_decay=0.9999,
        grad_clip=1.0,
        transform=_freeze_mapping(
            {
                "operations": ["ToTensor", "Normalize"],
                "normalize_mean": [0.5, 0.5, 0.5],
                "normalize_std": [0.5, 0.5, 0.5],
                "random_augmentation": False,
            }
        ),
        data=_freeze_mapping(
            {
                "dataset": "CIFAR10",
                "train_size": 50_000,
                "member_size": 25_000,
                "member_only": True,
                "batch_size": 64,
                "drop_last": True,
                "shuffle": False,
                "sampler": "DeterministicEpochBatchSampler",
            }
        ),
        determinism=_freeze_mapping(
            {
                "deterministic_algorithms": True,
                "cudnn_benchmark": False,
                "cudnn_deterministic": True,
                "allow_tf32_matmul": False,
                "allow_tf32_cudnn": False,
                "cublas_workspace_config": ":4096:8",
                "seed_python": True,
                "seed_numpy": True,
                "seed_torch_cpu": True,
                "seed_torch_cuda": True,
                "worker_rng_independent": True,
            }
        ),
        checkpointing=_freeze_mapping(
            {
                "save_every": 2_000,
                "sample_every": 50_000,
                "save_final": True,
                "save_on_signal": "next_step_boundary",
                "atomic_replace": True,
                "weights_only_load": True,
                "retention": "retain_all_corrected_checkpoints",
            }
        ),
        runtime=_freeze_mapping(
            {
                "num_workers": num_workers,
                "pin_memory": "cuda_available",
                "persistent_workers": num_workers > 0,
                "non_blocking_device_transfer": True,
                "device_policy": "cuda_if_available_else_cpu",
            }
        ),
    )


def canonical_training_config_hash(config: TrainingConfig) -> str:
    canonical = json.dumps(
        config.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def collect_environment() -> dict[str, object]:
    cuda_available = torch.cuda.is_available()
    gpu_name: str | None = None
    gpu_uuid: str | None = None
    if cuda_available:
        properties = torch.cuda.get_device_properties(0)
        gpu_name = torch.cuda.get_device_name(0)
        gpu_uuid = str(properties.uuid) if hasattr(properties, "uuid") else None
    return {
        "python": sys.version.split()[0],
        "pytorch": str(torch.__version__),
        "cuda": torch.version.cuda if cuda_available else None,
        "cudnn": torch.backends.cudnn.version() if cuda_available else None,
        "gpu_name": gpu_name,
        "gpu_uuid": gpu_uuid,
    }


def _load_protocol_envelope(path: Path) -> Mapping[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load protocol manifest: {error}") from error
    if not isinstance(value, Mapping):
        raise ValueError("protocol manifest must contain a JSON object")
    return value


def _validate_run_label(run_label: str, seed: int) -> str:
    if not isinstance(run_label, str) or _RUN_LABEL_RE.fullmatch(run_label) is None:
        raise ValueError("run label must be a corrected slug containing one s<seed> token")
    tokens = [int(value) for value in _SEED_TOKEN_RE.findall(run_label)]
    if tokens != [seed]:
        raise ValueError("run label must contain exactly the requested s<seed> token")
    return run_label


def _load_member_indices(split_path: Path) -> tuple[int, ...]:
    try:
        with np.load(split_path, allow_pickle=False) as split:
            members = np.asarray(split["mia_train_idxs"])
    except (OSError, KeyError, ValueError) as error:
        raise ValueError(f"cannot load verified member split: {error}") from error
    if members.shape != (25_000,) or not np.issubdtype(members.dtype, np.integer):
        raise ValueError("verified member split must contain exactly 25000 integer indices")
    return tuple(int(index) for index in members.tolist())


def load_training_contract(
    protocol_path: str | Path,
    split_path: str | Path,
    class_labels: Sequence[int] | np.ndarray,
    expected_code_commit: str,
    seed: int,
    run_label: str,
) -> CorrectedTrainingContract:
    """Verify the frozen protocol and select one corrected training identity."""

    protocol_path = Path(protocol_path)
    split_path = Path(split_path)
    envelope = _load_protocol_envelope(protocol_path)
    verified = verify_paper1_contract(
        envelope,
        split_path=split_path,
        class_labels=class_labels,
        expected_code_commit=expected_code_commit,
    )
    protocol_hash = envelope.get("protocol_hash")
    if not isinstance(protocol_hash, str) or _SHA256_RE.fullmatch(protocol_hash) is None:
        raise ValueError("protocol_hash must be 64 lowercase hexadecimal characters")
    training = verified["training"]
    if not isinstance(training, Mapping) or not isinstance(training.get("seeds"), list):
        raise ValueError("verified protocol training seeds are invalid")
    training_seeds = tuple(training["seeds"])
    if type(seed) is not int or seed not in training_seeds:
        raise ValueError("seed must be one of the eight verified training seeds")
    run_label = _validate_run_label(run_label, seed)
    split = verified["dataset"]["split"]
    return CorrectedTrainingContract(
        protocol_hash=protocol_hash,
        split_sha256=split["sha256"],
        code_commit=verified["code_commit"],
        seed=seed,
        run_label=run_label,
        training_seeds=training_seeds,
        member_indices=_load_member_indices(split_path),
    )


def validate_repository_state(
    current_head: str, expected_code_commit: str, tracked_status: str
) -> str:
    """Pure repository gate; untracked-only status must be filtered by the caller."""

    if current_head != expected_code_commit:
        raise ValueError("repository HEAD does not match protocol code_commit")
    if tracked_status.strip():
        raise ValueError("repository has tracked worktree changes")
    return current_head


def read_repository_state(repository_root: str | Path) -> tuple[str, str]:
    root = Path(repository_root)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    tracked_status = subprocess.run(
        ["git", "status", "--short", "--untracked-files=no"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return head, tracked_status


def build_member_subset(dataset: Dataset[Any], member_indices: Sequence[int]) -> Subset[Any]:
    if len(dataset) != 50_000:
        raise ValueError("CIFAR10 training dataset length must be exactly 50000")
    normalized = tuple(int(index) for index in member_indices)
    if len(normalized) != 25_000 or len(set(normalized)) != 25_000:
        raise ValueError("member split must contain exactly 25000 unique indices")
    if min(normalized) < 0 or max(normalized) >= 50_000:
        raise ValueError("member split indices must be within CIFAR10 training rows")
    return Subset(dataset, normalized)


def _seed_worker(worker_id: int, *, worker_seed: int) -> None:
    seed = (worker_seed + worker_id) % (2**32)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def build_corrected_dataloader(
    member_dataset: Dataset[Any],
    seed: int,
    start_step: int,
    stop_step: int,
    *,
    num_workers: int,
) -> DataLoader[Any]:
    if len(member_dataset) != 25_000:
        raise ValueError("corrected member dataset length must be exactly 25000")
    batch_sampler = DeterministicEpochBatchSampler(
        dataset_size=25_000,
        batch_size=64,
        seed=seed,
        start_step=start_step,
        stop_step=stop_step,
    )
    worker_seed = int.from_bytes(
        hashlib.sha256(f"diffaudit-worker-v1:{seed}".encode()).digest()[:8], "big"
    )
    generator = torch.Generator(device="cpu")
    generator.manual_seed(worker_seed)
    return DataLoader(
        member_dataset,
        batch_sampler=batch_sampler,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
        worker_init_fn=functools.partial(_seed_worker, worker_seed=worker_seed),
        generator=generator,
        persistent_workers=num_workers > 0,
    )


def validate_stop_step(stop_step: int, *, preflight: bool) -> int:
    if type(stop_step) is not int:
        raise TypeError("stop_step must be an integer")
    if preflight:
        if not 1 <= stop_step <= 5_000:
            raise ValueError("preflight stop_step must be in [1, 5000]")
    elif stop_step not in (100_000, 200_000):
        raise ValueError("normal stop_step must be 100000 or 200000")
    return stop_step


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def validate_output_safety(
    output_dir: str | Path,
    log_dir: str | Path,
    download_root: str | Path,
    research_root: str | Path,
    *,
    resume_step: int | None,
) -> None:
    output_dir = Path(output_dir).resolve()
    log_dir = Path(log_dir).resolve()
    checkpoint_root = (Path(download_root) / "checkpoints").resolve()
    training_output_root = (Path(research_root) / "training" / "outputs").resolve()
    if not _is_relative_to(output_dir, checkpoint_root) or not _is_relative_to(
        log_dir, training_output_root
    ):
        raise ValueError("corrected outputs must stay within approved output roots")
    if not output_dir.name.startswith("corrected-") or not log_dir.name.startswith("corrected-"):
        raise ValueError("output directories must use a corrected run label")
    if output_dir.name != log_dir.name:
        raise ValueError("checkpoint and log directories must share the corrected run label")
    checkpoints = list(output_dir.glob("checkpoint-step*.pt")) if output_dir.exists() else []
    if checkpoints and resume_step is None:
        raise ValueError("existing corrected checkpoints require an explicit --resume step")


def _require_hash(name: str, value: str, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise ValueError(f"{name} has invalid format")
    return value


def save_corrected_checkpoint(
    path: str | Path,
    model: torch.nn.Module,
    ema_model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
    *,
    step: int,
    run_label: str,
    seed: int,
    protocol_hash: str,
    split_sha256: str,
    code_commit: str,
    training_config: TrainingConfig,
    environment: Mapping[str, object],
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _validate_run_label(run_label, seed)
    _require_hash("protocol_hash", protocol_hash, _SHA256_RE)
    _require_hash("split_sha256", split_sha256, _SHA256_RE)
    _require_hash("code_commit", code_commit, _COMMIT_RE)
    training_config_hash = canonical_training_config_hash(training_config)
    payload = {
        "model": model.state_dict(),
        "ema": ema_model.state_dict(),
        "optim": optimizer.state_dict(),
        "sched": scheduler.state_dict(),
        "step": step,
        "metadata": {
            "run_label": run_label,
            "seed": seed,
            "protocol_hash": protocol_hash,
            "checkpoint_step": step,
            "split_sha256": split_sha256,
            "code_commit": code_commit,
            "training_config": training_config.to_dict(),
            "training_config_hash": training_config_hash,
            "environment": dict(environment),
        },
        "rng_state": capture_rng_state(),
    }
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as fh:
            temporary = Path(fh.name)
            torch.save(payload, fh)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return path


def load_corrected_checkpoint(
    path: str | Path,
    model: torch.nn.Module,
    ema_model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
    *,
    expected_step: int,
    expected_run_label: str,
    expected_seed: int,
    expected_protocol_hash: str,
    expected_split_sha256: str,
    expected_code_commit: str,
    expected_training_config_hash: str,
) -> int:
    payload = torch.load(Path(path), map_location="cpu", weights_only=True)
    if not isinstance(payload, Mapping) or not isinstance(payload.get("metadata"), Mapping):
        raise ValueError("checkpoint payload or metadata is invalid")
    metadata = payload["metadata"]
    validated_step = validate_resume_identity(
        metadata,
        expected_run_label,
        expected_seed,
        expected_protocol_hash,
        expected_step,
    )
    if metadata.get("split_sha256") != expected_split_sha256:
        raise ValueError("checkpoint split_sha256 does not match expected split")
    if metadata.get("code_commit") != expected_code_commit:
        raise ValueError("checkpoint code_commit does not match expected commit")
    checkpoint_config = metadata.get("training_config")
    checkpoint_config_hash = metadata.get("training_config_hash")
    if not isinstance(checkpoint_config, Mapping) or not isinstance(
        checkpoint_config_hash, str
    ):
        raise ValueError("checkpoint training_config or training_config_hash is invalid")
    canonical_checkpoint_hash = hashlib.sha256(
        json.dumps(
            checkpoint_config, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("utf-8")
    ).hexdigest()
    if checkpoint_config_hash != canonical_checkpoint_hash:
        raise ValueError("checkpoint training_config_hash does not match training_config")
    if checkpoint_config_hash != expected_training_config_hash:
        raise ValueError("checkpoint training_config_hash does not match expected config")
    if payload.get("step") != validated_step:
        raise ValueError("checkpoint top-level step does not match validated metadata")
    model.load_state_dict(payload["model"])
    ema_model.load_state_dict(payload["ema"])
    optimizer.load_state_dict(payload["optim"])
    scheduler.load_state_dict(payload["sched"])
    restore_rng_state(payload["rng_state"])
    return validated_step
