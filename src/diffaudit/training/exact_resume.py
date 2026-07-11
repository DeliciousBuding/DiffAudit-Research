"""Exact-resume primitives for corrected training runs."""

from __future__ import annotations

import hashlib
import random
import re
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Any

import numpy as np
import torch
from torch.utils.data import Sampler

_CORRECTED_RUN_LABEL_RE = re.compile(r"ddpm-cifar10-corrected-[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_HISTORICAL_SEED_RE = re.compile(r"(?:^|-)seed-?(?:42|43|44|45)(?:-|$)")
_PROTOCOL_HASH_RE = re.compile(r"[0-9a-f]{64}\Z")


def _require_int(name: str, value: object, *, minimum: int) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


class DeterministicEpochBatchSampler(Sampler[list[int]]):
    """Yield full shuffled batches for a global half-open step interval."""

    def __init__(
        self,
        dataset_size: int,
        batch_size: int,
        seed: int,
        start_step: int,
        stop_step: int,
        drop_last: bool = True,
    ) -> None:
        self.dataset_size = _require_int("dataset_size", dataset_size, minimum=1)
        self.batch_size = _require_int("batch_size", batch_size, minimum=1)
        self.seed = _require_int("seed", seed, minimum=0)
        self.start_step = _require_int("start_step", start_step, minimum=0)
        self.stop_step = _require_int("stop_step", stop_step, minimum=0)
        if type(drop_last) is not bool:
            raise TypeError("drop_last must be a boolean")
        if not drop_last:
            raise ValueError("drop_last must be true for exact full batches")
        if self.dataset_size < self.batch_size:
            raise ValueError("dataset_size must be at least batch_size")
        if self.stop_step < self.start_step:
            raise ValueError("stop_step must be greater than or equal to start_step")
        self.drop_last = drop_last
        self._batches_per_epoch = self.dataset_size // self.batch_size

    def __iter__(self) -> Iterator[list[int]]:
        current_epoch = -1
        permutation: torch.Tensor | None = None
        for step in range(self.start_step, self.stop_step):
            epoch, batch_in_epoch = divmod(step, self._batches_per_epoch)
            if epoch != current_epoch:
                generator = torch.Generator(device="cpu")
                generator.manual_seed(self._epoch_seed(epoch))
                permutation = torch.randperm(self.dataset_size, generator=generator)
                current_epoch = epoch
            assert permutation is not None
            offset = batch_in_epoch * self.batch_size
            yield permutation[offset : offset + self.batch_size].tolist()

    def __len__(self) -> int:
        return self.stop_step - self.start_step

    def _epoch_seed(self, epoch: int) -> int:
        material = f"diffaudit-exact-resume-v1:{self.seed}:{epoch}".encode("ascii")
        return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")


def capture_rng_state() -> dict[str, Any]:
    """Capture all process RNG streams used by corrected training."""

    cuda_state = torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None
    return {
        "python": random.getstate(),
        "numpy": np.random.get_state(),
        "torch_cpu": torch.get_rng_state(),
        "torch_cuda": cuda_state,
    }


def restore_rng_state(state: dict[str, Any]) -> None:
    """Restore a state produced by :func:`capture_rng_state`."""

    random.setstate(state["python"])
    np.random.set_state(state["numpy"])
    torch.set_rng_state(state["torch_cpu"])
    if state["torch_cuda"] is not None:
        torch.cuda.set_rng_state_all(state["torch_cuda"])


@contextmanager
def preserve_rng_state() -> Iterator[None]:
    """Restore all RNG streams after a temporary block, including on error."""

    state = capture_rng_state()
    try:
        yield
    finally:
        restore_rng_state(state)


def validate_corrected_run_label(label: str) -> str:
    """Return a corrected public-safe label, rejecting historical run identities."""

    if type(label) is not str:
        raise TypeError("run label must be a string")
    if _CORRECTED_RUN_LABEL_RE.fullmatch(label) is None:
        raise ValueError(
            "run label must start with 'ddpm-cifar10-corrected-' and contain a safe slug"
        )
    suffix = label.removeprefix("ddpm-cifar10-corrected-")
    if _HISTORICAL_SEED_RE.search(suffix) or "ddpm-cifar10-750k" in suffix:
        raise ValueError("run label must not identify a historical target")
    return label


def _validate_protocol_hash(name: str, value: object) -> str:
    if type(value) is not str:
        raise TypeError(f"{name} must be a string")
    if _PROTOCOL_HASH_RE.fullmatch(value) is None:
        raise ValueError(f"{name} must be exactly 64 lowercase hexadecimal characters")
    return value


def validate_resume_identity(
    checkpoint_metadata: Mapping[str, object],
    expected_run_label: str,
    expected_seed: int,
    expected_protocol_hash: str,
) -> None:
    """Reject checkpoints that do not belong to the expected corrected run."""

    if not isinstance(checkpoint_metadata, Mapping):
        raise TypeError("checkpoint_metadata must be a mapping")
    expected_run_label = validate_corrected_run_label(expected_run_label)
    expected_seed = _require_int("expected_seed", expected_seed, minimum=0)
    expected_protocol_hash = _validate_protocol_hash(
        "expected protocol hash", expected_protocol_hash
    )

    for field in ("run_label", "seed", "protocol_hash"):
        if field not in checkpoint_metadata:
            raise ValueError(f"checkpoint metadata is missing required field {field!r}")

    checkpoint_run_label = checkpoint_metadata["run_label"]
    try:
        checkpoint_run_label = validate_corrected_run_label(checkpoint_run_label)  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        raise ValueError(f"checkpoint run_label is invalid: {error}") from error

    checkpoint_seed = checkpoint_metadata["seed"]
    if type(checkpoint_seed) is not int or checkpoint_seed < 0:
        raise ValueError("checkpoint seed must be a non-negative integer")

    try:
        checkpoint_protocol_hash = _validate_protocol_hash(
            "checkpoint protocol_hash", checkpoint_metadata["protocol_hash"]
        )
    except (TypeError, ValueError) as error:
        raise ValueError(str(error)) from error

    if checkpoint_run_label != expected_run_label:
        raise ValueError("checkpoint run_label does not match expected_run_label")
    if checkpoint_seed != expected_seed:
        raise ValueError("checkpoint seed does not match expected_seed")
    if checkpoint_protocol_hash != expected_protocol_hash:
        raise ValueError("checkpoint protocol_hash does not match expected_protocol_hash")


def configure_deterministic_torch() -> None:
    """Opt in to deterministic cuDNN behavior for a training process."""

    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
