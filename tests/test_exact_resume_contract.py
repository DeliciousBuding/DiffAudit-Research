from __future__ import annotations

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


def test_captured_rng_state_is_torch_save_serializable() -> None:
    buffer = io.BytesIO()

    torch.save(capture_rng_state(), buffer)

    assert buffer.tell() > 0


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
    )

    assert result is None


@pytest.mark.parametrize("missing_field", ["run_label", "seed", "protocol_hash"])
def test_validate_resume_identity_rejects_missing_required_fields(missing_field: str) -> None:
    metadata = _checkpoint_metadata()
    del metadata[missing_field]

    with pytest.raises(ValueError, match=missing_field):
        validate_resume_identity(
            metadata,
            expected_run_label=_RUN_LABEL,
            expected_seed=1001,
            expected_protocol_hash=_PROTOCOL_HASH,
        )


@pytest.mark.parametrize(
    ("field", "checkpoint_value", "expected_message"),
    [
        ("run_label", "ddpm-cifar10-corrected-seed-1002", "run_label"),
        ("seed", 1002, "seed"),
        ("protocol_hash", "b" * 64, "protocol_hash"),
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
        )


@pytest.mark.parametrize("invalid_seed", [True, 1001.0, -1])
def test_validate_resume_identity_rejects_invalid_expected_seeds(invalid_seed: object) -> None:
    with pytest.raises((TypeError, ValueError), match="expected_seed"):
        validate_resume_identity(
            _checkpoint_metadata(),
            expected_run_label=_RUN_LABEL,
            expected_seed=invalid_seed,  # type: ignore[arg-type]
            expected_protocol_hash=_PROTOCOL_HASH,
        )


def test_validate_resume_identity_rejects_non_mapping_metadata() -> None:
    with pytest.raises(TypeError, match="checkpoint_metadata"):
        validate_resume_identity(
            [],  # type: ignore[arg-type]
            expected_run_label=_RUN_LABEL,
            expected_seed=1001,
            expected_protocol_hash=_PROTOCOL_HASH,
        )


def test_configure_deterministic_torch_sets_cudnn_flags_only_when_called() -> None:
    original_benchmark = torch.backends.cudnn.benchmark
    original_deterministic = torch.backends.cudnn.deterministic
    try:
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False

        result = configure_deterministic_torch()

        assert result is None
        assert torch.backends.cudnn.benchmark is False
        assert torch.backends.cudnn.deterministic is True
    finally:
        torch.backends.cudnn.benchmark = original_benchmark
        torch.backends.cudnn.deterministic = original_deterministic


def test_importing_exact_resume_does_not_mutate_cudnn_flags() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    script = """
import torch

torch.backends.cudnn.benchmark = True
torch.backends.cudnn.deterministic = False
import diffaudit.training.exact_resume  # noqa: F401, E402
assert torch.backends.cudnn.benchmark is True
assert torch.backends.cudnn.deterministic is False
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


def _run_tiny_training_steps(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    start_step: int,
    stop_step: int,
) -> list[float]:
    features = torch.linspace(-1.0, 1.0, 24, dtype=torch.float32).reshape(12, 2)
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
        random_target = torch.rand(4, 1) + random.random() + float(np.random.random())
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
    loaded = torch.load(checkpoint_buffer, map_location="cpu", weights_only=False)

    validate_resume_identity(
        loaded["metadata"],
        expected_run_label=_RUN_LABEL,
        expected_seed=1001,
        expected_protocol_hash=_PROTOCOL_HASH,
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
            start_step=checkpoint_step,
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
