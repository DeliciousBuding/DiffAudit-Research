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
    )
    saved = torch.load(path, map_location="cpu", weights_only=True)
    assert set(saved) == {"model", "ema", "optim", "sched", "step", "metadata", "rng_state"}
    assert "x_T" not in saved
    assert saved["metadata"]["split_sha256"] == "c" * 64
    assert saved["metadata"]["code_commit"] == CODE_COMMIT

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
    save_corrected_checkpoint(
        path,
        *source,
        step=1,
        run_label=f"corrected-s{SEEDS[0]}",
        seed=SEEDS[0],
        protocol_hash="a" * 64,
        split_sha256="c" * 64,
        code_commit=CODE_COMMIT,
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
