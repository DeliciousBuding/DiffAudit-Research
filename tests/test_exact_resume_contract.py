from __future__ import annotations

import copy
import io
import json
import os
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

from diffaudit.training.exact_resume import (
    DeterministicEpochBatchSampler,
    capture_rng_state,
    configure_deterministic_torch,
    preserve_rng_state,
    restore_rng_state,
    validate_corrected_run_label,
    validate_resume_identity,
)

_RUN_LABEL = "ddpm-cifar10-corrected-seed-1001"
_PROTOCOL_HASH = "a" * 64


def _sampler_kwargs(**overrides: object) -> dict[str, object]:
    kwargs: dict[str, object] = {
        "dataset_size": 11,
        "batch_size": 3,
        "seed": 17,
        "start_step": 0,
        "stop_step": 7,
        "drop_last": True,
    }
    kwargs.update(overrides)
    return kwargs


def _batches(**overrides: object) -> list[list[int]]:
    return list(DeterministicEpochBatchSampler(**_sampler_kwargs(**overrides)))


def test_sampler_resume_is_exact_without_a_saved_cursor() -> None:
    full = _batches(start_step=0, stop_step=11)
    before_checkpoint = _batches(start_step=0, stop_step=4)
    after_resume = _batches(start_step=4, stop_step=11)

    assert full == before_checkpoint + after_resume


def test_sampler_uses_full_batches_without_replacement_within_each_epoch() -> None:
    batches = _batches(dataset_size=11, batch_size=3, start_step=0, stop_step=3)

    flattened = [index for batch in batches for index in batch]
    assert all(len(batch) == 3 for batch in batches)
    assert len(flattened) == len(set(flattened))
    assert all(0 <= index < 11 for index in flattened)


def test_sampler_len_matches_requested_global_step_interval() -> None:
    sampler = DeterministicEpochBatchSampler(**_sampler_kwargs(start_step=2, stop_step=9))

    assert len(sampler) == 7
    assert len(list(sampler)) == 7


def test_sampler_is_stable_across_python_hash_seeds() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    script = """
import json
from diffaudit.training.exact_resume import DeterministicEpochBatchSampler

sampler = DeterministicEpochBatchSampler(
    dataset_size=13,
    batch_size=4,
    seed=123,
    start_step=1,
    stop_step=8,
)
print(json.dumps(list(sampler)))
"""

    outputs: list[object] = []
    for hash_seed in ("1", "987654"):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = hash_seed
        env["PYTHONPATH"] = str(repository_root / "src")
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=repository_root,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
        outputs.append(json.loads(result.stdout))

    assert outputs[0] == outputs[1]


@pytest.mark.parametrize(
    ("parameter", "value"),
    [
        ("dataset_size", True),
        ("dataset_size", 11.0),
        ("batch_size", False),
        ("batch_size", 3.0),
        ("seed", True),
        ("seed", 17.0),
        ("start_step", False),
        ("start_step", 0.0),
        ("stop_step", True),
        ("stop_step", 7.0),
        ("drop_last", 1),
    ],
)
def test_sampler_rejects_non_integer_contract_values(parameter: str, value: object) -> None:
    with pytest.raises(TypeError, match=parameter):
        DeterministicEpochBatchSampler(**_sampler_kwargs(**{parameter: value}))


@pytest.mark.parametrize(
    ("parameter", "value"),
    [
        ("dataset_size", 0),
        ("dataset_size", -1),
        ("batch_size", 0),
        ("batch_size", -1),
        ("seed", -1),
        ("start_step", -1),
        ("stop_step", -1),
    ],
)
def test_sampler_rejects_out_of_range_values(parameter: str, value: int) -> None:
    with pytest.raises(ValueError, match=parameter):
        DeterministicEpochBatchSampler(**_sampler_kwargs(**{parameter: value}))


def test_sampler_rejects_an_inverted_step_interval() -> None:
    with pytest.raises(ValueError, match="stop_step"):
        DeterministicEpochBatchSampler(**_sampler_kwargs(start_step=8, stop_step=7))


def test_sampler_rejects_a_dataset_smaller_than_one_batch() -> None:
    with pytest.raises(ValueError, match="dataset_size"):
        DeterministicEpochBatchSampler(**_sampler_kwargs(dataset_size=2, batch_size=3))


def test_sampler_rejects_partial_batches() -> None:
    with pytest.raises(ValueError, match="drop_last"):
        DeterministicEpochBatchSampler(**_sampler_kwargs(drop_last=False))


def _draw_rng_sample() -> tuple[float, np.ndarray, torch.Tensor]:
    return random.random(), np.random.random(4), torch.rand(4)


def test_restore_rng_state_replays_python_numpy_and_torch_cpu_sequences() -> None:
    random.seed(101)
    np.random.seed(202)
    torch.manual_seed(303)
    state = capture_rng_state()

    expected = _draw_rng_sample()
    _draw_rng_sample()
    restore_rng_state(state)
    actual = _draw_rng_sample()

    assert actual[0] == expected[0]
    assert np.array_equal(actual[1], expected[1])
    assert torch.equal(actual[2], expected[2])


def test_captured_rng_state_uses_a_versioned_topology_bound_schema() -> None:
    state = capture_rng_state()

    assert set(state) == {
        "schema_version",
        "python",
        "numpy",
        "torch_cpu",
        "cuda_device_count",
        "cuda_device_uuids",
        "torch_cuda",
    }
    assert state["schema_version"] == 1
    assert state["cuda_device_count"] == torch.cuda.device_count()
    assert state["cuda_device_uuids"] == [
        str(torch.cuda.get_device_properties(index).uuid)
        for index in range(torch.cuda.device_count())
    ]
    assert set(state["numpy"]) == {
        "bit_generator",
        "keys",
        "position",
        "has_gauss",
        "cached_gaussian",
    }
    assert isinstance(state["numpy"]["keys"], torch.Tensor)
    assert state["numpy"]["keys"].dtype is torch.int64
    assert state["numpy"]["keys"].shape == (624,)
    assert len(state["torch_cuda"]) == state["cuda_device_count"]


def test_captured_rng_state_is_weights_only_safe_and_restorable() -> None:
    random.seed(1111)
    np.random.seed(2222)
    torch.manual_seed(3333)
    state = capture_rng_state()
    expected = _draw_rng_sample()
    buffer = io.BytesIO()
    torch.save(state, buffer)
    buffer.seek(0)

    loaded = torch.load(buffer, map_location="cpu", weights_only=True)
    restore_rng_state(loaded)
    actual = _draw_rng_sample()

    _assert_rng_samples_equal(actual, expected)


def _assert_invalid_rng_state_does_not_mutate_streams(
    invalid_state: object,
    *,
    match: str,
) -> None:
    random.seed(4444)
    np.random.seed(5555)
    torch.manual_seed(6666)
    current_state = capture_rng_state()
    expected = _draw_rng_sample()
    restore_rng_state(current_state)
    cuda_before = [state.clone() for state in torch.cuda.get_rng_state_all()]

    with pytest.raises(ValueError, match=match):
        restore_rng_state(invalid_state)  # type: ignore[arg-type]

    actual = _draw_rng_sample()
    cuda_after = torch.cuda.get_rng_state_all()
    _assert_rng_samples_equal(actual, expected)
    assert all(
        torch.equal(before, after) for before, after in zip(cuda_before, cuda_after, strict=True)
    )


@pytest.mark.parametrize(
    "corruption",
    [
        "not_mapping",
        "missing_top_level",
        "unexpected_top_level",
        "schema_version",
        "python_state",
        "numpy_fields",
        "numpy_dtype",
        "numpy_shape",
        "torch_cpu_dtype",
        "torch_cpu_shape",
        "cuda_device_count_type",
        "cuda_uuids_type",
        "torch_cuda_type",
    ],
)
def test_restore_rng_state_prevalidates_complete_schema(corruption: str) -> None:
    state: object = copy.deepcopy(capture_rng_state())
    if corruption == "not_mapping":
        state = []
    else:
        assert isinstance(state, dict)
        if corruption == "missing_top_level":
            del state["numpy"]
        elif corruption == "unexpected_top_level":
            state["unexpected"] = 1
        elif corruption == "schema_version":
            state["schema_version"] = 2
        elif corruption == "python_state":
            state["python"] = ("invalid",)
        elif corruption == "numpy_fields":
            del state["numpy"]["position"]
        elif corruption == "numpy_dtype":
            state["numpy"]["keys"] = state["numpy"]["keys"].to(torch.uint8)
        elif corruption == "numpy_shape":
            state["numpy"]["keys"] = state["numpy"]["keys"][:-1]
        elif corruption == "torch_cpu_dtype":
            state["torch_cpu"] = state["torch_cpu"].to(torch.int64)
        elif corruption == "torch_cpu_shape":
            state["torch_cpu"] = state["torch_cpu"][:-1]
        elif corruption == "cuda_device_count_type":
            state["cuda_device_count"] = True
        elif corruption == "cuda_uuids_type":
            state["cuda_device_uuids"] = tuple(state["cuda_device_uuids"])
        elif corruption == "torch_cuda_type":
            state["torch_cuda"] = tuple(state["torch_cuda"])

    _assert_invalid_rng_state_does_not_mutate_streams(state, match="RNG state")


def test_restore_rng_state_rejects_cuda_device_count_mismatch_before_mutation() -> None:
    state = copy.deepcopy(capture_rng_state())
    state["cuda_device_count"] += 1

    _assert_invalid_rng_state_does_not_mutate_streams(state, match="cuda_device_count")


@pytest.mark.gpu
@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA is unavailable")
def test_restore_rng_state_rejects_cuda_uuid_mismatch_before_mutation() -> None:
    state = copy.deepcopy(capture_rng_state())
    state["cuda_device_uuids"][0] = "00000000-0000-0000-0000-000000000000"

    _assert_invalid_rng_state_does_not_mutate_streams(state, match="cuda_device_uuids")


@pytest.mark.gpu
@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA is unavailable")
@pytest.mark.parametrize("corruption", ["length", "dtype", "shape"])
def test_restore_rng_state_prevalidates_cuda_rng_tensors(corruption: str) -> None:
    state = copy.deepcopy(capture_rng_state())
    if corruption == "length":
        state["torch_cuda"] = []
    elif corruption == "dtype":
        state["torch_cuda"][0] = state["torch_cuda"][0].to(torch.int64)
    else:
        state["torch_cuda"][0] = state["torch_cuda"][0][:-1]

    _assert_invalid_rng_state_does_not_mutate_streams(state, match="torch_cuda")


@pytest.mark.gpu
@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA is unavailable")
def test_restore_rng_state_replays_every_cuda_device_sequence() -> None:
    torch.cuda.manual_seed_all(404)
    state = capture_rng_state()
    expected = [
        torch.rand(4, device=torch.device("cuda", device_index))
        for device_index in range(torch.cuda.device_count())
    ]

    for device_index in range(torch.cuda.device_count()):
        torch.rand(4, device=torch.device("cuda", device_index))
    restore_rng_state(state)
    actual = [
        torch.rand(4, device=torch.device("cuda", device_index))
        for device_index in range(torch.cuda.device_count())
    ]

    assert all(torch.equal(left, right) for left, right in zip(actual, expected, strict=True))


def _assert_rng_samples_equal(
    actual: tuple[float, np.ndarray, torch.Tensor],
    expected: tuple[float, np.ndarray, torch.Tensor],
) -> None:
    assert actual[0] == expected[0]
    assert np.array_equal(actual[1], expected[1])
    assert torch.equal(actual[2], expected[2])


def test_preserve_rng_state_does_not_advance_external_rng_streams() -> None:
    random.seed(505)
    np.random.seed(606)
    torch.manual_seed(707)
    starting_state = capture_rng_state()
    expected = _draw_rng_sample()
    restore_rng_state(starting_state)

    with preserve_rng_state():
        _draw_rng_sample()
        _draw_rng_sample()
    actual = _draw_rng_sample()

    _assert_rng_samples_equal(actual, expected)


def test_preserve_rng_state_restores_streams_after_an_exception() -> None:
    random.seed(808)
    np.random.seed(909)
    torch.manual_seed(1001)
    starting_state = capture_rng_state()
    expected = _draw_rng_sample()
    restore_rng_state(starting_state)

    with pytest.raises(RuntimeError, match="deliberate failure"), preserve_rng_state():
        _draw_rng_sample()
        raise RuntimeError("deliberate failure")
    actual = _draw_rng_sample()

    _assert_rng_samples_equal(actual, expected)


@pytest.mark.parametrize(
    "label",
    [
        "ddpm-cifar10-corrected-seed-1001",
        "ddpm-cifar10-corrected-preflight-a1",
        "ddpm-cifar10-corrected-hash-a42b",
        "ddpm-cifar10-corrected-seed-420",
    ],
)
def test_validate_corrected_run_label_accepts_public_safe_corrected_slugs(label: str) -> None:
    assert validate_corrected_run_label(label) == label


@pytest.mark.parametrize(
    "label",
    [
        "",
        "DDPM-cifar10-corrected-seed-1001",
        "ddpm-cifar10-corrected-",
        "ddpm-cifar10-corrected--seed-1001",
        "ddpm-cifar10-corrected-seed-1001-",
        "ddpm-cifar10-corrected-seed_1001",
        "ddpm-cifar10-corrected-..",
        "ddpm-cifar10-corrected-../escape",
        "ddpm-cifar10-corrected-folder/run",
        "ddpm-cifar10-corrected-folder\\run",
        "ddpm-cifar10-750k",
        "ddpm-cifar10-corrected-ddpm-cifar10-750k",
        "ddpm-cifar10-corrected-seed42",
        "ddpm-cifar10-corrected-reuse-seed43-target",
        "ddpm-cifar10-corrected-seed44-restart",
        "ddpm-cifar10-corrected-historical-seed45",
        "ddpm-cifar10-corrected-seed-42",
        "ddpm-cifar10-corrected-seed-43",
        "ddpm-cifar10-corrected-seed-44",
        "ddpm-cifar10-corrected-seed-45",
        "ddpm-cifar10-corrected-historical-seed-42",
    ],
)
def test_validate_corrected_run_label_rejects_unsafe_or_historical_labels(label: str) -> None:
    with pytest.raises(ValueError, match="run label"):
        validate_corrected_run_label(label)


@pytest.mark.parametrize("label", [None, 123, True])
def test_validate_corrected_run_label_rejects_non_strings(label: object) -> None:
    with pytest.raises(TypeError, match="run label"):
        validate_corrected_run_label(label)  # type: ignore[arg-type]


def _checkpoint_metadata(**overrides: object) -> dict[str, object]:
    metadata: dict[str, object] = {
        "run_label": _RUN_LABEL,
        "seed": 1001,
        "protocol_hash": _PROTOCOL_HASH,
        "checkpoint_step": 4,
    }
    metadata.update(overrides)
    return metadata


def test_validate_resume_identity_accepts_matching_required_fields_with_extra_metadata() -> None:
    result = validate_resume_identity(
        _checkpoint_metadata(),
        expected_run_label=_RUN_LABEL,
        expected_seed=1001,
        expected_protocol_hash=_PROTOCOL_HASH,
        expected_checkpoint_step=4,
    )

    assert result == 4


@pytest.mark.parametrize("missing_field", ["run_label", "seed", "protocol_hash", "checkpoint_step"])
def test_validate_resume_identity_rejects_missing_required_fields(missing_field: str) -> None:
    metadata = _checkpoint_metadata()
    del metadata[missing_field]

    with pytest.raises(ValueError, match=missing_field):
        validate_resume_identity(
            metadata,
            expected_run_label=_RUN_LABEL,
            expected_seed=1001,
            expected_protocol_hash=_PROTOCOL_HASH,
            expected_checkpoint_step=4,
        )


@pytest.mark.parametrize(
    ("field", "checkpoint_value", "expected_message"),
    [
        ("run_label", "ddpm-cifar10-corrected-seed-1002", "run_label"),
        ("seed", 1002, "seed"),
        ("protocol_hash", "b" * 64, "protocol_hash"),
        ("checkpoint_step", 5, "checkpoint_step"),
    ],
)
def test_validate_resume_identity_rejects_field_mismatches(
    field: str,
    checkpoint_value: object,
    expected_message: str,
) -> None:
    with pytest.raises(ValueError, match=expected_message):
        validate_resume_identity(
            _checkpoint_metadata(**{field: checkpoint_value}),
            expected_run_label=_RUN_LABEL,
            expected_seed=1001,
            expected_protocol_hash=_PROTOCOL_HASH,
            expected_checkpoint_step=4,
        )


@pytest.mark.parametrize(
    "historical_label",
    [
        "ddpm-cifar10-750k",
        "ddpm-cifar10-corrected-seed42",
        "ddpm-cifar10-corrected-seed43",
        "ddpm-cifar10-corrected-seed44",
        "ddpm-cifar10-corrected-seed45",
        "ddpm-cifar10-corrected-seed-42",
        "ddpm-cifar10-corrected-historical-seed-43",
        "ddpm-cifar10-corrected-seed-44-restart",
        "ddpm-cifar10-corrected-reuse-seed-45-target",
    ],
)
def test_validate_resume_identity_rejects_historical_checkpoint_labels(
    historical_label: str,
) -> None:
    with pytest.raises(ValueError, match="checkpoint run_label is invalid"):
        validate_resume_identity(
            _checkpoint_metadata(run_label=historical_label),
            expected_run_label=_RUN_LABEL,
            expected_seed=1001,
            expected_protocol_hash=_PROTOCOL_HASH,
            expected_checkpoint_step=4,
        )


@pytest.mark.parametrize("invalid_hash", ["a" * 63, "A" * 64, "g" * 64, 123])
def test_validate_resume_identity_rejects_invalid_expected_protocol_hashes(
    invalid_hash: object,
) -> None:
    with pytest.raises((TypeError, ValueError), match="protocol hash"):
        validate_resume_identity(
            _checkpoint_metadata(),
            expected_run_label=_RUN_LABEL,
            expected_seed=1001,
            expected_protocol_hash=invalid_hash,  # type: ignore[arg-type]
            expected_checkpoint_step=4,
        )


@pytest.mark.parametrize("invalid_hash", ["a" * 63, "A" * 64, "g" * 64, 123])
def test_validate_resume_identity_rejects_invalid_checkpoint_protocol_hashes(
    invalid_hash: object,
) -> None:
    with pytest.raises(ValueError, match="protocol_hash"):
        validate_resume_identity(
            _checkpoint_metadata(protocol_hash=invalid_hash),
            expected_run_label=_RUN_LABEL,
            expected_seed=1001,
            expected_protocol_hash=_PROTOCOL_HASH,
            expected_checkpoint_step=4,
        )


@pytest.mark.parametrize("invalid_seed", [True, 1001.0, -1])
def test_validate_resume_identity_rejects_invalid_expected_seeds(invalid_seed: object) -> None:
    with pytest.raises((TypeError, ValueError), match="expected_seed"):
        validate_resume_identity(
            _checkpoint_metadata(),
            expected_run_label=_RUN_LABEL,
            expected_seed=invalid_seed,  # type: ignore[arg-type]
            expected_protocol_hash=_PROTOCOL_HASH,
            expected_checkpoint_step=4,
        )


@pytest.mark.parametrize("invalid_step", [True, 4.0, -1])
def test_validate_resume_identity_rejects_invalid_expected_checkpoint_steps(
    invalid_step: object,
) -> None:
    with pytest.raises((TypeError, ValueError), match="expected_checkpoint_step"):
        validate_resume_identity(
            _checkpoint_metadata(),
            expected_run_label=_RUN_LABEL,
            expected_seed=1001,
            expected_protocol_hash=_PROTOCOL_HASH,
            expected_checkpoint_step=invalid_step,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("invalid_step", [True, 4.0, -1])
def test_validate_resume_identity_rejects_invalid_checkpoint_steps(
    invalid_step: object,
) -> None:
    with pytest.raises(ValueError, match="checkpoint_step"):
        validate_resume_identity(
            _checkpoint_metadata(checkpoint_step=invalid_step),
            expected_run_label=_RUN_LABEL,
            expected_seed=1001,
            expected_protocol_hash=_PROTOCOL_HASH,
            expected_checkpoint_step=4,
        )


def test_validate_resume_identity_accepts_integral_checkpoint_steps() -> None:
    result = validate_resume_identity(
        _checkpoint_metadata(checkpoint_step=np.int64(4)),
        expected_run_label=_RUN_LABEL,
        expected_seed=1001,
        expected_protocol_hash=_PROTOCOL_HASH,
        expected_checkpoint_step=np.int64(4),  # type: ignore[arg-type]
    )

    assert result == 4


def test_validate_resume_identity_rejects_non_mapping_metadata() -> None:
    with pytest.raises(TypeError, match="checkpoint_metadata"):
        validate_resume_identity(
            [],  # type: ignore[arg-type]
            expected_run_label=_RUN_LABEL,
            expected_seed=1001,
            expected_protocol_hash=_PROTOCOL_HASH,
            expected_checkpoint_step=4,
        )


def test_configure_deterministic_torch_sets_all_required_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CUBLAS_WORKSPACE_CONFIG", raising=False)
    original_algorithms = torch.are_deterministic_algorithms_enabled()
    original_benchmark = torch.backends.cudnn.benchmark
    original_deterministic = torch.backends.cudnn.deterministic
    original_matmul_tf32 = torch.backends.cuda.matmul.allow_tf32
    original_cudnn_tf32 = torch.backends.cudnn.allow_tf32
    try:
        torch.use_deterministic_algorithms(False)
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

        result = configure_deterministic_torch()

        assert result is None
        assert os.environ["CUBLAS_WORKSPACE_CONFIG"] == ":4096:8"
        assert torch.are_deterministic_algorithms_enabled() is True
        assert torch.backends.cudnn.benchmark is False
        assert torch.backends.cudnn.deterministic is True
        assert torch.backends.cuda.matmul.allow_tf32 is False
        assert torch.backends.cudnn.allow_tf32 is False
    finally:
        torch.use_deterministic_algorithms(original_algorithms)
        torch.backends.cudnn.benchmark = original_benchmark
        torch.backends.cudnn.deterministic = original_deterministic
        torch.backends.cuda.matmul.allow_tf32 = original_matmul_tf32
        torch.backends.cudnn.allow_tf32 = original_cudnn_tf32


def test_configure_deterministic_torch_rejects_conflicting_cublas_workspace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CUBLAS_WORKSPACE_CONFIG", ":16:8")
    original_algorithms = torch.are_deterministic_algorithms_enabled()
    original_benchmark = torch.backends.cudnn.benchmark

    with pytest.raises(RuntimeError, match="CUBLAS_WORKSPACE_CONFIG"):
        configure_deterministic_torch()

    assert torch.are_deterministic_algorithms_enabled() is original_algorithms
    assert torch.backends.cudnn.benchmark is original_benchmark


def test_importing_exact_resume_does_not_mutate_cudnn_flags() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    script = """
import os
import torch

os.environ["CUBLAS_WORKSPACE_CONFIG"] = "sentinel"
torch.use_deterministic_algorithms(False)
torch.backends.cudnn.benchmark = True
torch.backends.cudnn.deterministic = False
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
import diffaudit.training.exact_resume  # noqa: F401, E402
assert os.environ["CUBLAS_WORKSPACE_CONFIG"] == "sentinel"
assert torch.are_deterministic_algorithms_enabled() is False
assert torch.backends.cudnn.benchmark is True
assert torch.backends.cudnn.deterministic is False
assert torch.backends.cuda.matmul.allow_tf32 is True
assert torch.backends.cudnn.allow_tf32 is True
"""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repository_root / "src")

    subprocess.run(
        [sys.executable, "-c", script],
        cwd=repository_root,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )


def _seed_tiny_training(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _run_tiny_training_steps(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    start_step: int,
    stop_step: int,
    device: torch.device | None = None,
) -> list[float]:
    device = device or torch.device("cpu")
    features = torch.linspace(-1.0, 1.0, 24, dtype=torch.float32, device=device).reshape(12, 2)
    sampler = DeterministicEpochBatchSampler(
        dataset_size=len(features),
        batch_size=4,
        seed=31337,
        start_step=start_step,
        stop_step=stop_step,
    )
    losses: list[float] = []
    for batch_indices in sampler:
        optimizer.zero_grad()
        prediction = model(features[batch_indices])
        random_target = (
            torch.rand(4, 1, device=device) + random.random() + float(np.random.random())
        )
        loss = torch.nn.functional.mse_loss(prediction, random_target)
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach()))
    return losses


def test_tiny_cpu_training_is_exact_after_checkpoint_resume() -> None:
    total_steps = 8
    checkpoint_step = 4

    _seed_tiny_training(111)
    continuous_model = torch.nn.Linear(2, 1)
    continuous_optimizer = torch.optim.Adam(continuous_model.parameters(), lr=0.01)
    continuous_losses = _run_tiny_training_steps(
        continuous_model,
        continuous_optimizer,
        start_step=0,
        stop_step=total_steps,
    )

    _seed_tiny_training(111)
    checkpoint_model = torch.nn.Linear(2, 1)
    checkpoint_optimizer = torch.optim.Adam(checkpoint_model.parameters(), lr=0.01)
    resumed_losses = _run_tiny_training_steps(
        checkpoint_model,
        checkpoint_optimizer,
        start_step=0,
        stop_step=checkpoint_step,
    )
    checkpoint = {
        "model": checkpoint_model.state_dict(),
        "optimizer": checkpoint_optimizer.state_dict(),
        "rng": capture_rng_state(),
        "metadata": _checkpoint_metadata(checkpoint_step=checkpoint_step),
    }
    checkpoint_buffer = io.BytesIO()
    torch.save(checkpoint, checkpoint_buffer)
    checkpoint_buffer.seek(0)
    loaded = torch.load(checkpoint_buffer, map_location="cpu", weights_only=True)

    resume_step = validate_resume_identity(
        loaded["metadata"],
        expected_run_label=_RUN_LABEL,
        expected_seed=1001,
        expected_protocol_hash=_PROTOCOL_HASH,
        expected_checkpoint_step=checkpoint_step,
    )
    resumed_model = torch.nn.Linear(2, 1)
    resumed_optimizer = torch.optim.Adam(resumed_model.parameters(), lr=0.01)
    resumed_model.load_state_dict(loaded["model"])
    resumed_optimizer.load_state_dict(loaded["optimizer"])
    restore_rng_state(loaded["rng"])
    resumed_losses.extend(
        _run_tiny_training_steps(
            resumed_model,
            resumed_optimizer,
            start_step=resume_step,
            stop_step=total_steps,
        )
    )

    assert resumed_losses == continuous_losses
    assert all(
        torch.equal(resumed_value, continuous_value)
        for resumed_value, continuous_value in zip(
            resumed_model.state_dict().values(),
            continuous_model.state_dict().values(),
            strict=True,
        )
    )


@pytest.mark.gpu
@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA is unavailable")
def test_tiny_cuda_training_is_exact_after_checkpoint_resume(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CUBLAS_WORKSPACE_CONFIG", raising=False)
    original_algorithms = torch.are_deterministic_algorithms_enabled()
    original_benchmark = torch.backends.cudnn.benchmark
    original_deterministic = torch.backends.cudnn.deterministic
    original_matmul_tf32 = torch.backends.cuda.matmul.allow_tf32
    original_cudnn_tf32 = torch.backends.cudnn.allow_tf32
    device = torch.device("cuda", 0)
    total_steps = 6
    checkpoint_step = 3
    try:
        configure_deterministic_torch()

        _seed_tiny_training(777)
        continuous_model = torch.nn.Linear(2, 1, device=device)
        continuous_optimizer = torch.optim.Adam(continuous_model.parameters(), lr=0.01)
        continuous_losses = _run_tiny_training_steps(
            continuous_model,
            continuous_optimizer,
            start_step=0,
            stop_step=total_steps,
            device=device,
        )

        _seed_tiny_training(777)
        checkpoint_model = torch.nn.Linear(2, 1, device=device)
        checkpoint_optimizer = torch.optim.Adam(checkpoint_model.parameters(), lr=0.01)
        resumed_losses = _run_tiny_training_steps(
            checkpoint_model,
            checkpoint_optimizer,
            start_step=0,
            stop_step=checkpoint_step,
            device=device,
        )
        checkpoint = {
            "model": checkpoint_model.state_dict(),
            "optimizer": checkpoint_optimizer.state_dict(),
            "rng": capture_rng_state(),
            "metadata": _checkpoint_metadata(checkpoint_step=checkpoint_step),
        }
        checkpoint_buffer = io.BytesIO()
        torch.save(checkpoint, checkpoint_buffer)
        checkpoint_buffer.seek(0)
        loaded = torch.load(checkpoint_buffer, map_location="cpu", weights_only=True)

        resume_step = validate_resume_identity(
            loaded["metadata"],
            expected_run_label=_RUN_LABEL,
            expected_seed=1001,
            expected_protocol_hash=_PROTOCOL_HASH,
            expected_checkpoint_step=checkpoint_step,
        )
        resumed_model = torch.nn.Linear(2, 1, device=device)
        resumed_optimizer = torch.optim.Adam(resumed_model.parameters(), lr=0.01)
        resumed_model.load_state_dict(loaded["model"])
        resumed_optimizer.load_state_dict(loaded["optimizer"])
        restore_rng_state(loaded["rng"])
        resumed_losses.extend(
            _run_tiny_training_steps(
                resumed_model,
                resumed_optimizer,
                start_step=resume_step,
                stop_step=total_steps,
                device=device,
            )
        )
        torch.cuda.synchronize(device)

        assert resumed_losses == continuous_losses
        assert all(
            torch.equal(resumed_value, continuous_value)
            for resumed_value, continuous_value in zip(
                resumed_model.state_dict().values(),
                continuous_model.state_dict().values(),
                strict=True,
            )
        )
    finally:
        torch.use_deterministic_algorithms(original_algorithms)
        torch.backends.cudnn.benchmark = original_benchmark
        torch.backends.cudnn.deterministic = original_deterministic
        torch.backends.cuda.matmul.allow_tf32 = original_matmul_tf32
        torch.backends.cudnn.allow_tf32 = original_cudnn_tf32
