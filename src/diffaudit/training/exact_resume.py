"""Exact-resume primitives for corrected training runs."""

from __future__ import annotations

import hashlib
import os
import random
import re
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from numbers import Integral
from typing import Any

import numpy as np
import torch
from torch.utils.data import Sampler

_CORRECTED_RUN_LABEL_RE = re.compile(
    r"(?:ddpm-cifar10-)?corrected-[a-z0-9]+(?:-[a-z0-9]+)*\Z"
)
_HISTORICAL_SEED_RE = re.compile(r"(?:^|-)seed-?(?:42|43|44|45)(?:-|$)")
_PROTOCOL_HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
_RNG_SCHEMA_VERSION = 1
_RNG_STATE_FIELDS = frozenset(
    {
        "schema_version",
        "python",
        "numpy",
        "torch_cpu",
        "cuda_device_count",
        "cuda_device_uuids",
        "torch_cuda",
    }
)
_NUMPY_RNG_STATE_FIELDS = frozenset(
    {"bit_generator", "keys", "position", "has_gauss", "cached_gaussian"}
)


def _require_int(name: str, value: object, *, minimum: int) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return value


def _require_integral(name: str, value: object, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{name} must be an integer")
    normalized = int(value)
    if normalized < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return normalized


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


def _cuda_device_uuids() -> list[str]:
    uuids: list[str] = []
    for device_index in range(torch.cuda.device_count()):
        properties = torch.cuda.get_device_properties(device_index)
        if not hasattr(properties, "uuid"):
            raise RuntimeError(f"CUDA device {device_index} does not expose a UUID")
        uuids.append(str(properties.uuid))
    return uuids


def _encode_numpy_rng_state() -> dict[str, object]:
    bit_generator, keys, position, has_gauss, cached_gaussian = np.random.get_state()
    return {
        "bit_generator": str(bit_generator),
        "keys": torch.tensor(keys.astype(np.int64), dtype=torch.int64),
        "position": int(position),
        "has_gauss": int(has_gauss),
        "cached_gaussian": float(cached_gaussian),
    }


def _raise_rng_state_error(message: str) -> None:
    raise ValueError(f"invalid RNG state: {message}")


def _validate_exact_fields(
    state: Mapping[object, object],
    expected_fields: frozenset[str],
    *,
    name: str,
) -> None:
    actual_fields = set(state)
    missing = expected_fields - actual_fields
    unexpected = actual_fields - expected_fields
    if missing:
        _raise_rng_state_error(f"{name} is missing fields {sorted(missing)!r}")
    if unexpected:
        _raise_rng_state_error(f"{name} has unexpected fields {list(unexpected)!r}")


def _validate_numpy_rng_state(state: object) -> tuple[object, ...]:
    if not isinstance(state, Mapping):
        _raise_rng_state_error("numpy must be a mapping")
    _validate_exact_fields(state, _NUMPY_RNG_STATE_FIELDS, name="numpy")

    bit_generator = state["bit_generator"]
    keys = state["keys"]
    position = state["position"]
    has_gauss = state["has_gauss"]
    cached_gaussian = state["cached_gaussian"]
    if type(bit_generator) is not str or bit_generator != "MT19937":
        _raise_rng_state_error("numpy bit_generator must be 'MT19937'")
    if not isinstance(keys, torch.Tensor):
        _raise_rng_state_error("numpy keys must be a torch tensor")
    if keys.device.type != "cpu" or keys.dtype is not torch.int64 or keys.shape != (624,):
        _raise_rng_state_error("numpy keys must be a CPU int64 tensor with shape (624,)")
    if bool(torch.any(keys < 0)) or bool(torch.any(keys > np.iinfo(np.uint32).max)):
        _raise_rng_state_error("numpy keys contain values outside uint32 range")
    if type(position) is not int or not 0 <= position <= 624:
        _raise_rng_state_error("numpy position must be an integer in [0, 624]")
    if type(has_gauss) is not int or has_gauss not in (0, 1):
        _raise_rng_state_error("numpy has_gauss must be 0 or 1")
    if type(cached_gaussian) is not float:
        _raise_rng_state_error("numpy cached_gaussian must be a float")

    decoded = (
        bit_generator,
        keys.numpy().astype(np.uint32, copy=True),
        position,
        has_gauss,
        cached_gaussian,
    )
    try:
        np.random.RandomState().set_state(decoded)
    except (TypeError, ValueError, IndexError) as error:
        _raise_rng_state_error(f"numpy state is invalid: {error}")
    return decoded


def _validate_torch_rng_tensor(
    name: str,
    state: object,
    *,
    expected_shape: torch.Size,
    device: torch.device,
) -> torch.Tensor:
    if not isinstance(state, torch.Tensor):
        _raise_rng_state_error(f"{name} must be a torch tensor")
    if state.device.type != "cpu" or state.dtype is not torch.uint8:
        _raise_rng_state_error(f"{name} must be a CPU uint8 tensor")
    if state.shape != expected_shape:
        _raise_rng_state_error(
            f"{name} has shape {tuple(state.shape)!r}; expected {tuple(expected_shape)!r}"
        )
    try:
        torch.Generator(device=device).set_state(state)
    except (TypeError, RuntimeError) as error:
        _raise_rng_state_error(f"{name} is invalid: {error}")
    return state


def _validate_rng_state(
    state: object,
) -> tuple[object, tuple[object, ...], torch.Tensor, list[torch.Tensor]]:
    if not isinstance(state, Mapping):
        _raise_rng_state_error("top-level value must be a mapping")
    _validate_exact_fields(state, _RNG_STATE_FIELDS, name="top-level state")

    schema_version = state["schema_version"]
    if type(schema_version) is not int or schema_version != _RNG_SCHEMA_VERSION:
        _raise_rng_state_error(
            f"schema_version must equal {_RNG_SCHEMA_VERSION}, got {schema_version!r}"
        )

    python_state = state["python"]
    try:
        random.Random().setstate(python_state)  # type: ignore[arg-type]
    except (TypeError, ValueError) as error:
        _raise_rng_state_error(f"python state is invalid: {error}")
    numpy_state = _validate_numpy_rng_state(state["numpy"])

    torch_cpu = _validate_torch_rng_tensor(
        "torch_cpu",
        state["torch_cpu"],
        expected_shape=torch.get_rng_state().shape,
        device=torch.device("cpu"),
    )

    cuda_device_count = state["cuda_device_count"]
    if type(cuda_device_count) is not int or cuda_device_count < 0:
        _raise_rng_state_error("cuda_device_count must be a non-negative integer")
    current_cuda_device_count = torch.cuda.device_count()
    if cuda_device_count != current_cuda_device_count:
        _raise_rng_state_error(
            "cuda_device_count mismatch: "
            f"checkpoint={cuda_device_count}, current={current_cuda_device_count}"
        )

    cuda_device_uuids = state["cuda_device_uuids"]
    if type(cuda_device_uuids) is not list or any(
        type(device_uuid) is not str or not device_uuid for device_uuid in cuda_device_uuids
    ):
        _raise_rng_state_error("cuda_device_uuids must be a list of non-empty strings")
    if len(cuda_device_uuids) != cuda_device_count:
        _raise_rng_state_error("cuda_device_uuids length must match cuda_device_count")
    current_cuda_device_uuids = _cuda_device_uuids()
    if cuda_device_uuids != current_cuda_device_uuids:
        _raise_rng_state_error(
            "cuda_device_uuids mismatch: "
            f"checkpoint={cuda_device_uuids!r}, current={current_cuda_device_uuids!r}"
        )

    torch_cuda = state["torch_cuda"]
    if type(torch_cuda) is not list:
        _raise_rng_state_error("torch_cuda must be a list")
    if len(torch_cuda) != cuda_device_count:
        _raise_rng_state_error("torch_cuda length must match cuda_device_count")
    current_cuda_states = torch.cuda.get_rng_state_all() if cuda_device_count else []
    validated_cuda_states = [
        _validate_torch_rng_tensor(
            f"torch_cuda[{device_index}]",
            cuda_state,
            expected_shape=current_cuda_states[device_index].shape,
            device=torch.device("cuda", device_index),
        )
        for device_index, cuda_state in enumerate(torch_cuda)
    ]
    return python_state, numpy_state, torch_cpu, validated_cuda_states


def capture_rng_state() -> dict[str, Any]:
    """Capture all process RNG streams used by corrected training."""

    cuda_device_count = torch.cuda.device_count()
    cuda_state = torch.cuda.get_rng_state_all() if cuda_device_count else []
    return {
        "schema_version": _RNG_SCHEMA_VERSION,
        "python": random.getstate(),
        "numpy": _encode_numpy_rng_state(),
        "torch_cpu": torch.get_rng_state(),
        "cuda_device_count": cuda_device_count,
        "cuda_device_uuids": _cuda_device_uuids(),
        "torch_cuda": cuda_state,
    }


def restore_rng_state(state: object) -> None:
    """Restore a state produced by :func:`capture_rng_state`."""

    python_state, numpy_state, torch_cpu, torch_cuda = _validate_rng_state(state)
    random.setstate(python_state)  # type: ignore[arg-type]
    np.random.set_state(numpy_state)
    torch.set_rng_state(torch_cpu)
    if torch_cuda:
        torch.cuda.set_rng_state_all(torch_cuda)


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
            "run label must use a corrected safe slug"
        )
    suffix = label.removeprefix("ddpm-cifar10-").removeprefix("corrected-")
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
    expected_checkpoint_step: int,
) -> int:
    """Reject checkpoints that do not belong to the expected corrected run."""

    if not isinstance(checkpoint_metadata, Mapping):
        raise TypeError("checkpoint_metadata must be a mapping")
    expected_run_label = validate_corrected_run_label(expected_run_label)
    expected_seed = _require_int("expected_seed", expected_seed, minimum=0)
    expected_protocol_hash = _validate_protocol_hash(
        "expected protocol hash", expected_protocol_hash
    )
    expected_checkpoint_step = _require_integral(
        "expected_checkpoint_step", expected_checkpoint_step, minimum=0
    )

    for field in ("run_label", "seed", "protocol_hash", "checkpoint_step"):
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

    try:
        checkpoint_step = _require_integral(
            "checkpoint_step", checkpoint_metadata["checkpoint_step"], minimum=0
        )
    except (TypeError, ValueError) as error:
        raise ValueError(str(error)) from error

    if checkpoint_run_label != expected_run_label:
        raise ValueError("checkpoint run_label does not match expected_run_label")
    if checkpoint_seed != expected_seed:
        raise ValueError("checkpoint seed does not match expected_seed")
    if checkpoint_protocol_hash != expected_protocol_hash:
        raise ValueError("checkpoint protocol_hash does not match expected_protocol_hash")
    if checkpoint_step != expected_checkpoint_step:
        raise ValueError("checkpoint checkpoint_step does not match expected_checkpoint_step")
    return checkpoint_step


def configure_deterministic_torch() -> None:
    """Opt in to deterministic cuDNN behavior for a training process."""

    required_workspace = ":4096:8"
    configured_workspace = os.environ.get("CUBLAS_WORKSPACE_CONFIG")
    if configured_workspace not in (None, required_workspace):
        raise RuntimeError(
            "CUBLAS_WORKSPACE_CONFIG conflicts with exact resume; "
            f"expected {required_workspace!r}, got {configured_workspace!r}"
        )
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = required_workspace
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
