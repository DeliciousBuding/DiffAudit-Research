from __future__ import annotations

import copy
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from torch.utils.data import Dataset, Subset

from diffaudit.evidence.corrected_protocol import (
    build_paper1_corrected_contract,
    build_protocol_envelope,
)
from diffaudit.training.corrected_ddpm import (
    build_corrected_dataloader,
    build_member_subset,
    build_training_config,
    canonical_training_config_hash,
    collect_environment,
    load_corrected_checkpoint,
    load_training_contract,
    save_corrected_checkpoint,
    validate_output_safety,
    validate_repository_state,
    validate_stop_step,
)

CODE_COMMIT = "b" * 40
SEEDS = (
    1746574482,
    1403859882,
    1877216607,
    120492209,
    1624907720,
    761208184,
    1867632528,
    1918927372,
)


class TinyDataset(Dataset[tuple[torch.Tensor, int]]):
    def __init__(self, size: int) -> None:
        self.targets = [index % 10 for index in range(size)]

    def __len__(self) -> int:
        return len(self.targets)

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
        return torch.tensor(index), self.targets[index]


@pytest.fixture()
def protocol_files(tmp_path: Path) -> tuple[Path, Path, np.ndarray]:
    split_path = tmp_path / "CIFAR10_train_ratio0.5.npz"
    members = np.arange(25_000, dtype=np.int64)
    nonmembers = np.arange(25_000, 50_000, dtype=np.int64)
    labels = np.arange(50_000, dtype=np.int64) % 10
    np.savez(split_path, mia_train_idxs=members, mia_eval_idxs=nonmembers)
    contract = build_paper1_corrected_contract(
        split_filename=split_path.name,
        split_sha256=hashlib.sha256(split_path.read_bytes()).hexdigest(),
        member_indices=members,
        nonmember_indices=nonmembers,
        class_labels=labels,
        code_commit=CODE_COMMIT,
    )
    protocol_path = tmp_path / "protocol.json"
    protocol_path.write_text(json.dumps(build_protocol_envelope(contract)), encoding="utf-8")
    return protocol_path, split_path, labels


def test_load_training_contract_returns_typed_verified_identity(
    protocol_files: tuple[Path, Path, np.ndarray],
) -> None:
    protocol_path, split_path, labels = protocol_files

    loaded = load_training_contract(
        protocol_path,
        split_path,
        labels,
        CODE_COMMIT,
        SEEDS[0],
        f"corrected-s{SEEDS[0]}",
    )

    assert loaded.seed == SEEDS[0]
    assert loaded.run_label == f"corrected-s{SEEDS[0]}"
    assert loaded.protocol_hash == json.loads(protocol_path.read_text())["protocol_hash"]
    assert loaded.split_sha256 == hashlib.sha256(split_path.read_bytes()).hexdigest()
    assert loaded.code_commit == CODE_COMMIT
    assert loaded.member_indices == tuple(range(25_000))
    assert loaded.training_seeds == SEEDS


@pytest.mark.parametrize(
    ("seed", "label"),
    [
        (99, "corrected-s99"),
        (SEEDS[0], f"corrected-s{SEEDS[1]}"),
        (SEEDS[0], f"corrected-s{SEEDS[0]}-s{SEEDS[1]}"),
        (SEEDS[0], "ddpm-cifar10-seed42"),
    ],
)
def test_load_training_contract_rejects_seed_or_label_identity_drift(
    protocol_files: tuple[Path, Path, np.ndarray], seed: int, label: str
) -> None:
    protocol_path, split_path, labels = protocol_files

    with pytest.raises(ValueError, match="seed|run label"):
        load_training_contract(protocol_path, split_path, labels, CODE_COMMIT, seed, label)


def test_repository_gate_requires_expected_head_and_clean_tracked_tree() -> None:
    assert validate_repository_state(CODE_COMMIT, CODE_COMMIT, "") == CODE_COMMIT
    with pytest.raises(ValueError, match="HEAD"):
        validate_repository_state("a" * 40, CODE_COMMIT, "")
    with pytest.raises(ValueError, match="tracked"):
        validate_repository_state(CODE_COMMIT, CODE_COMMIT, " M src/file.py\n")


def test_member_subset_requires_real_cifar10_size_and_exact_members(
    protocol_files: tuple[Path, Path, np.ndarray],
) -> None:
    protocol_path, split_path, labels = protocol_files
    loaded = load_training_contract(
        protocol_path,
        split_path,
        labels,
        CODE_COMMIT,
        SEEDS[0],
        f"corrected-s{SEEDS[0]}",
    )
    subset = build_member_subset(TinyDataset(50_000), loaded.member_indices)

    assert isinstance(subset, Subset)
    assert len(subset) == 25_000
    assert tuple(subset.indices) == loaded.member_indices
    with pytest.raises(ValueError, match="50000"):
        build_member_subset(TinyDataset(49_999), loaded.member_indices)


def test_dataloader_uses_finite_exact_resume_sampler_without_global_rng_consumption() -> None:
    dataset = TinyDataset(25_000)
    torch.manual_seed(123)
    before = torch.get_rng_state().clone()
    full = build_corrected_dataloader(dataset, SEEDS[0], 0, 5, num_workers=0)
    resumed = build_corrected_dataloader(dataset, SEEDS[0], 2, 5, num_workers=0)

    assert torch.equal(before, torch.get_rng_state())
    assert list(full.batch_sampler)[2:] == list(resumed.batch_sampler)
    assert len(full) == 5
    assert full.batch_size is None


def _tiny_training_state():
    model = torch.nn.Linear(3, 2)
    ema = copy.deepcopy(model)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1.0)
    optimizer.zero_grad()
    model(torch.ones(1, 3)).sum().backward()
    optimizer.step()
    scheduler.step()
    return model, ema, optimizer, scheduler


def test_checkpoint_is_weights_only_safe_and_round_trips(tmp_path: Path) -> None:
    model, ema, optimizer, scheduler = _tiny_training_state()
    path = tmp_path / "checkpoint-step000001.pt"
    training_config = build_training_config()
    environment = collect_environment()
    save_corrected_checkpoint(
        path,
        model,
        ema,
        optimizer,
        scheduler,
        step=1,
        run_label=f"corrected-preflight-s{SEEDS[0]}",
        seed=SEEDS[0],
        protocol_hash="a" * 64,
        split_sha256="c" * 64,
        code_commit=CODE_COMMIT,
        training_config=training_config,
        environment=environment,
    )
    saved = torch.load(path, map_location="cpu", weights_only=True)
    assert set(saved) == {"model", "ema", "optim", "sched", "step", "metadata", "rng_state"}
    assert "x_T" not in saved
    assert saved["metadata"]["split_sha256"] == "c" * 64
    assert saved["metadata"]["code_commit"] == CODE_COMMIT
    assert saved["metadata"]["training_config"] == training_config.to_dict()
    assert saved["metadata"]["training_config_hash"] == canonical_training_config_hash(
        training_config
    )
    assert saved["metadata"]["environment"] == environment

    restored = _tiny_training_state()
    restored_step = load_corrected_checkpoint(
        path,
        *restored,
        expected_step=1,
        expected_run_label=f"corrected-preflight-s{SEEDS[0]}",
        expected_seed=SEEDS[0],
        expected_protocol_hash="a" * 64,
        expected_split_sha256="c" * 64,
        expected_code_commit=CODE_COMMIT,
        expected_training_config_hash=canonical_training_config_hash(training_config),
        expected_environment=environment,
    )
    assert restored_step == 1
    assert all(
        torch.equal(left, right)
        for left, right in zip(
            model.state_dict().values(), restored[0].state_dict().values(), strict=True
        )
    )


def test_wrong_checkpoint_identity_is_rejected_before_model_or_rng_changes(tmp_path: Path) -> None:
    source = _tiny_training_state()
    path = tmp_path / "checkpoint-step000001.pt"
    training_config = build_training_config()
    save_corrected_checkpoint(
        path,
        *source,
        step=1,
        run_label=f"corrected-s{SEEDS[0]}",
        seed=SEEDS[0],
        protocol_hash="a" * 64,
        split_sha256="c" * 64,
        code_commit=CODE_COMMIT,
        training_config=training_config,
        environment=collect_environment(),
    )
    target = _tiny_training_state()
    model_before = copy.deepcopy(target[0].state_dict())
    random_before = random.getstate()
    numpy_before = np.random.get_state()
    torch_before = torch.get_rng_state().clone()

    with pytest.raises(ValueError, match="checkpoint_step"):
        load_corrected_checkpoint(
            path,
            *target,
            expected_step=2,
            expected_run_label=f"corrected-s{SEEDS[0]}",
            expected_seed=SEEDS[0],
            expected_protocol_hash="a" * 64,
            expected_split_sha256="c" * 64,
            expected_code_commit=CODE_COMMIT,
            expected_training_config_hash=canonical_training_config_hash(training_config),
            expected_environment=collect_environment(),
        )

    assert all(
        torch.equal(model_before[name], target[0].state_dict()[name]) for name in model_before
    )
    assert random.getstate() == random_before
    numpy_after = np.random.get_state()
    assert numpy_after[0] == numpy_before[0]
    assert np.array_equal(numpy_after[1], numpy_before[1])
    assert numpy_after[2:] == numpy_before[2:]
    assert torch.equal(torch_before, torch.get_rng_state())


def test_training_config_is_complete_immutable_and_canonically_hashed() -> None:
    config = build_training_config()
    payload = config.to_dict()

    assert set(payload) == {
        "precision",
        "model",
        "diffusion",
        "optimizer",
        "scheduler",
        "ema_decay",
        "grad_clip",
        "transform",
        "data",
        "determinism",
        "checkpointing",
        "runtime",
    }
    assert payload["precision"] == {"dtype": "float32", "amp": False}
    assert payload["runtime"]["num_workers"] == 4
    assert payload["checkpointing"]["save_every"] == 2_000
    assert payload["checkpointing"]["sample_every"] == 50_000
    assert canonical_training_config_hash(config) == canonical_training_config_hash(config)
    with pytest.raises((AttributeError, TypeError)):
        config.runtime["num_workers"] = 9


def test_environment_is_separate_from_training_config_hash() -> None:
    config = build_training_config()
    environment = collect_environment()

    assert set(environment) == {
        "python",
        "pytorch",
        "cuda",
        "cudnn",
        "gpu_name",
        "gpu_uuid",
    }
    assert canonical_training_config_hash(config) == canonical_training_config_hash(config)


def test_wrong_training_config_hash_is_rejected_before_any_mutation(tmp_path: Path) -> None:
    source = _tiny_training_state()
    path = tmp_path / "checkpoint-step000001.pt"
    config = build_training_config()
    save_corrected_checkpoint(
        path,
        *source,
        step=1,
        run_label=f"corrected-s{SEEDS[0]}",
        seed=SEEDS[0],
        protocol_hash="a" * 64,
        split_sha256="c" * 64,
        code_commit=CODE_COMMIT,
        training_config=config,
        environment=collect_environment(),
    )
    target = _tiny_training_state()
    model_before = copy.deepcopy(target[0].state_dict())
    torch_before = torch.get_rng_state().clone()

    with pytest.raises(ValueError, match="training_config_hash"):
        load_corrected_checkpoint(
            path,
            *target,
            expected_step=1,
            expected_run_label=f"corrected-s{SEEDS[0]}",
            expected_seed=SEEDS[0],
            expected_protocol_hash="a" * 64,
            expected_split_sha256="c" * 64,
            expected_code_commit=CODE_COMMIT,
            expected_training_config_hash="d" * 64,
            expected_environment=collect_environment(),
        )

    assert all(
        torch.equal(model_before[name], target[0].state_dict()[name]) for name in model_before
    )
    assert torch.equal(torch_before, torch.get_rng_state())


def _assert_nested_equal(left: object, right: object) -> None:
    if isinstance(left, torch.Tensor):
        assert isinstance(right, torch.Tensor)
        assert torch.equal(left, right)
    elif isinstance(left, dict):
        assert isinstance(right, dict)
        assert left.keys() == right.keys()
        for key in left:
            _assert_nested_equal(left[key], right[key])
    elif isinstance(left, list | tuple):
        assert isinstance(right, type(left))
        assert len(left) == len(right)
        for left_item, right_item in zip(left, right, strict=True):
            _assert_nested_equal(left_item, right_item)
    else:
        assert left == right


def _snapshot_training_state(objects) -> dict[str, object]:
    model, ema, optimizer, scheduler = objects
    return {
        "model": copy.deepcopy(model.state_dict()),
        "ema": copy.deepcopy(ema.state_dict()),
        "optim": copy.deepcopy(optimizer.state_dict()),
        "sched": copy.deepcopy(scheduler.state_dict()),
        "python_rng": random.getstate(),
        "numpy_rng": np.random.get_state(),
        "torch_rng": torch.get_rng_state().clone(),
    }


def _assert_training_state_unchanged(objects, before: dict[str, object]) -> None:
    model, ema, optimizer, scheduler = objects
    _assert_nested_equal(model.state_dict(), before["model"])
    _assert_nested_equal(ema.state_dict(), before["ema"])
    _assert_nested_equal(optimizer.state_dict(), before["optim"])
    _assert_nested_equal(scheduler.state_dict(), before["sched"])
    assert random.getstate() == before["python_rng"]
    numpy_after = np.random.get_state()
    numpy_before = before["numpy_rng"]
    assert numpy_after[0] == numpy_before[0]
    assert np.array_equal(numpy_after[1], numpy_before[1])
    assert numpy_after[2:] == numpy_before[2:]
    assert torch.equal(torch.get_rng_state(), before["torch_rng"])


def test_resume_environment_mismatch_is_rejected_before_any_mutation(tmp_path: Path) -> None:
    source = _tiny_training_state()
    path = tmp_path / "checkpoint-step000001.pt"
    config = build_training_config()
    environment = collect_environment()
    save_corrected_checkpoint(
        path,
        *source,
        step=1,
        run_label=f"corrected-s{SEEDS[0]}",
        seed=SEEDS[0],
        protocol_hash="a" * 64,
        split_sha256="c" * 64,
        code_commit=CODE_COMMIT,
        training_config=config,
        environment=environment,
    )
    target = _tiny_training_state()
    before = _snapshot_training_state(target)
    mismatched = dict(environment)
    mismatched["python"] = "different"

    with pytest.raises(ValueError, match="environment"):
        load_corrected_checkpoint(
            path,
            *target,
            expected_step=1,
            expected_run_label=f"corrected-s{SEEDS[0]}",
            expected_seed=SEEDS[0],
            expected_protocol_hash="a" * 64,
            expected_split_sha256="c" * 64,
            expected_code_commit=CODE_COMMIT,
            expected_training_config_hash=canonical_training_config_hash(config),
            expected_environment=mismatched,
        )

    _assert_training_state_unchanged(target, before)


@pytest.mark.parametrize("corrupt_field", ["model", "ema", "optim", "sched", "rng_state"])
def test_corrupt_checkpoint_component_is_atomic_and_leaves_all_state_unchanged(
    tmp_path: Path, corrupt_field: str
) -> None:
    source = _tiny_training_state()
    path = tmp_path / f"checkpoint-{corrupt_field}.pt"
    config = build_training_config()
    environment = collect_environment()
    save_corrected_checkpoint(
        path,
        *source,
        step=1,
        run_label=f"corrected-s{SEEDS[0]}",
        seed=SEEDS[0],
        protocol_hash="a" * 64,
        split_sha256="c" * 64,
        code_commit=CODE_COMMIT,
        training_config=config,
        environment=environment,
    )
    payload = torch.load(path, map_location="cpu", weights_only=True)
    payload[corrupt_field] = None
    torch.save(payload, path)
    target = _tiny_training_state()
    before = _snapshot_training_state(target)

    with pytest.raises((TypeError, ValueError, RuntimeError, AttributeError)):
        load_corrected_checkpoint(
            path,
            *target,
            expected_step=1,
            expected_run_label=f"corrected-s{SEEDS[0]}",
            expected_seed=SEEDS[0],
            expected_protocol_hash="a" * 64,
            expected_split_sha256="c" * 64,
            expected_code_commit=CODE_COMMIT,
            expected_training_config_hash=canonical_training_config_hash(config),
            expected_environment=environment,
        )

    _assert_training_state_unchanged(target, before)


class NoDeviceDeepcopyLinear(torch.nn.Linear):
    def __deepcopy__(self, _memo):
        raise AssertionError("resume validation must not deepcopy modules on their device")


def _no_deepcopy_training_state():
    model = NoDeviceDeepcopyLinear(3, 2)
    ema = NoDeviceDeepcopyLinear(3, 2)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1.0)
    return model, ema, optimizer, scheduler


def test_resume_validation_never_deepcopies_model_or_optimizer_bundle(tmp_path: Path) -> None:
    source = _no_deepcopy_training_state()
    path = tmp_path / "checkpoint-no-device-deepcopy.pt"
    config = build_training_config()
    environment = collect_environment()
    save_corrected_checkpoint(
        path,
        *source,
        step=1,
        run_label=f"corrected-s{SEEDS[0]}",
        seed=SEEDS[0],
        protocol_hash="a" * 64,
        split_sha256="c" * 64,
        code_commit=CODE_COMMIT,
        training_config=config,
        environment=environment,
    )

    assert (
        load_corrected_checkpoint(
            path,
            *_no_deepcopy_training_state(),
            expected_step=1,
            expected_run_label=f"corrected-s{SEEDS[0]}",
            expected_seed=SEEDS[0],
            expected_protocol_hash="a" * 64,
            expected_split_sha256="c" * 64,
            expected_code_commit=CODE_COMMIT,
            expected_training_config_hash=canonical_training_config_hash(config),
            expected_environment=environment,
        )
        == 1
    )


class FailOnceLambdaLR(torch.optim.lr_scheduler.LambdaLR):
    def __init__(self, optimizer: torch.optim.Optimizer, *, fail_once: bool) -> None:
        self._inject_failure = fail_once
        super().__init__(optimizer, lambda _: 1.0)

    def state_dict(self):
        state = super().state_dict()
        state.pop("_inject_failure", None)
        return state

    def load_state_dict(self, state_dict) -> None:
        super().load_state_dict(state_dict)
        if self._inject_failure:
            self._inject_failure = False
            raise RuntimeError("injected scheduler commit failure")


def _transactional_training_state(*, fail_scheduler_once: bool):
    model = torch.nn.Linear(3, 2)
    ema = torch.nn.Linear(3, 2)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    scheduler = FailOnceLambdaLR(optimizer, fail_once=fail_scheduler_once)
    return model, ema, optimizer, scheduler


def test_commit_phase_failure_rolls_back_every_training_and_rng_state(tmp_path: Path) -> None:
    source = _transactional_training_state(fail_scheduler_once=False)
    source[2].zero_grad()
    source[0](torch.ones(1, 3)).sum().backward()
    source[2].step()
    source[3].step()
    path = tmp_path / "checkpoint-transaction.pt"
    config = build_training_config()
    environment = collect_environment()
    save_corrected_checkpoint(
        path,
        *source,
        step=1,
        run_label=f"corrected-s{SEEDS[0]}",
        seed=SEEDS[0],
        protocol_hash="a" * 64,
        split_sha256="c" * 64,
        code_commit=CODE_COMMIT,
        training_config=config,
        environment=environment,
    )
    target = _transactional_training_state(fail_scheduler_once=True)
    before = _snapshot_training_state(target)

    with pytest.raises(RuntimeError, match="injected scheduler commit failure"):
        load_corrected_checkpoint(
            path,
            *target,
            expected_step=1,
            expected_run_label=f"corrected-s{SEEDS[0]}",
            expected_seed=SEEDS[0],
            expected_protocol_hash="a" * 64,
            expected_split_sha256="c" * 64,
            expected_code_commit=CODE_COMMIT,
            expected_training_config_hash=canonical_training_config_hash(config),
            expected_environment=environment,
        )

    _assert_training_state_unchanged(target, before)


@pytest.mark.parametrize("corruption", ["adam_moment_shape", "scheduler_extra_key"])
def test_semantically_invalid_state_is_rejected_before_commit(
    tmp_path: Path, corruption: str
) -> None:
    source = _tiny_training_state()
    path = tmp_path / f"checkpoint-{corruption}.pt"
    config = build_training_config()
    environment = collect_environment()
    save_corrected_checkpoint(
        path,
        *source,
        step=1,
        run_label=f"corrected-s{SEEDS[0]}",
        seed=SEEDS[0],
        protocol_hash="a" * 64,
        split_sha256="c" * 64,
        code_commit=CODE_COMMIT,
        training_config=config,
        environment=environment,
    )
    payload = torch.load(path, map_location="cpu", weights_only=True)
    if corruption == "adam_moment_shape":
        first_state = next(iter(payload["optim"]["state"].values()))
        first_state["exp_avg"] = torch.zeros(99)
    else:
        payload["sched"]["unexpected"] = True
    torch.save(payload, path)
    target = _tiny_training_state()
    before = _snapshot_training_state(target)

    with pytest.raises(ValueError, match="optimizer|scheduler"):
        load_corrected_checkpoint(
            path,
            *target,
            expected_step=1,
            expected_run_label=f"corrected-s{SEEDS[0]}",
            expected_seed=SEEDS[0],
            expected_protocol_hash="a" * 64,
            expected_split_sha256="c" * 64,
            expected_code_commit=CODE_COMMIT,
            expected_training_config_hash=canonical_training_config_hash(config),
            expected_environment=environment,
        )

    _assert_training_state_unchanged(target, before)


@pytest.mark.parametrize(
    ("step", "preflight", "valid"),
    [
        (100_000, False, True),
        (200_000, False, True),
        (2_000, True, True),
        (2_000, False, False),
        (5_001, True, False),
    ],
)
def test_stop_step_contract(step: int, preflight: bool, valid: bool) -> None:
    if valid:
        assert validate_stop_step(step, preflight=preflight) == step
    else:
        with pytest.raises(ValueError, match="stop_step"):
            validate_stop_step(step, preflight=preflight)


def test_output_safety_allows_only_corrected_roots_and_requires_resume(tmp_path: Path) -> None:
    download_root = tmp_path / "Download"
    research_root = tmp_path / "Research"
    output_dir = download_root / "checkpoints" / f"corrected-s{SEEDS[0]}"
    log_dir = research_root / "training" / "outputs" / f"corrected-s{SEEDS[0]}"

    validate_output_safety(output_dir, log_dir, download_root, research_root, resume_step=None)
    output_dir.mkdir(parents=True)
    (output_dir / "checkpoint-step002000.pt").touch()
    with pytest.raises(ValueError, match="resume"):
        validate_output_safety(output_dir, log_dir, download_root, research_root, resume_step=None)
    validate_output_safety(output_dir, log_dir, download_root, research_root, resume_step=2_000)
    with pytest.raises(ValueError, match="corrected"):
        validate_output_safety(
            download_root / "checkpoints" / "ddpm-cifar10-seed42",
            log_dir,
            download_root,
            research_root,
            resume_step=None,
        )


def test_cli_requires_contract_identity_and_stop_step() -> None:
    script = (
        Path(__file__).resolve().parents[1]
        / "training/ddpm-cifar10/train_ddpm_cifar10_corrected.py"
    )
    result = subprocess.run(
        [sys.executable, str(script), "--dry-run"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    for option in ("--protocol-manifest", "--split-path", "--seed", "--run-label", "--stop-step"):
        assert option in result.stderr
