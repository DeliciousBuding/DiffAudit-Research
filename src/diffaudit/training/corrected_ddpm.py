"""Contract-bound primitives for corrected Paper 1 DDPM training."""

from __future__ import annotations

import functools
import hashlib
import json
import os
import random
import re
import subprocess
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
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
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _validate_run_label(run_label, seed)
    _require_hash("protocol_hash", protocol_hash, _SHA256_RE)
    _require_hash("split_sha256", split_sha256, _SHA256_RE)
    _require_hash("code_commit", code_commit, _COMMIT_RE)
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
    if payload.get("step") != validated_step:
        raise ValueError("checkpoint top-level step does not match validated metadata")
    model.load_state_dict(payload["model"])
    ema_model.load_state_dict(payload["ema"])
    optimizer.load_state_dict(payload["optim"])
    scheduler.load_state_dict(payload["sched"])
    restore_rng_state(payload["rng_state"])
    return validated_step
