from __future__ import annotations

import hashlib
import importlib.util
import json
from argparse import Namespace
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType, ModuleType

import numpy as np
import pytest
import torch
from torch.utils.data import Dataset

from diffaudit.evidence.corrected_protocol import (
    build_paper1_corrected_contract,
    build_protocol_envelope,
)
from diffaudit.training.corrected_ddpm import (
    CorrectedTrainingContract,
    build_training_config,
    canonical_training_config_hash,
)

CODE_COMMIT = "b" * 40
SEED = 1746574482


class SyntheticCIFAR(Dataset[tuple[torch.Tensor, int]]):
    def __init__(self) -> None:
        self.targets = [index % 10 for index in range(50_000)]

    def __len__(self) -> int:
        return 50_000

    def __getitem__(self, index: int) -> tuple[torch.Tensor, int]:
        return torch.tensor([float(index)]), self.targets[index]


class FakeTrainer:
    def __init__(self, model: torch.nn.Module, runtime: "FakeRuntime") -> None:
        self.model = model
        self.runtime = runtime

    def __call__(self, batch: torch.Tensor) -> torch.Tensor:
        self.runtime.completed_steps += 1
        return self.model(batch.float()).mean()


class FakeRuntime:
    def __init__(
        self,
        *,
        save_every: int = 2_000,
        sample_every: int = 50_000,
        interrupt_after: int | None = None,
    ) -> None:
        self.events: list[str] = []
        self.saved_steps: list[int] = []
        self.sampled_steps: list[int] = []
        self.completed_steps = 0
        self.interrupt_after = interrupt_after
        base = build_training_config(num_workers=0)
        checkpointing = dict(base.checkpointing)
        checkpointing.update(save_every=save_every, sample_every=sample_every)
        self.config = replace(base, checkpointing=MappingProxyType(checkpointing))

    def training_config(self, num_workers: int):
        assert num_workers == 0
        return self.config

    def read_repository_state(self, _root: Path) -> tuple[str, str]:
        return CODE_COMMIT, ""

    def load_dataset(self, _root: Path) -> SyntheticCIFAR:
        self.events.append("dataset")
        return SyntheticCIFAR()

    def configure_deterministic(self) -> None:
        self.events.append("configure")

    def seed_everything(self, _seed: int) -> None:
        self.events.append("seed")

    def collect_environment(self) -> dict[str, object]:
        self.events.append("environment")
        return {
            "python": "test",
            "pytorch": "test",
            "cuda": None,
            "cudnn": None,
            "gpu_name": None,
            "gpu_uuid": None,
        }

    def build_training_objects(self, _config):
        self.events.append("build_model")
        model = torch.nn.Linear(1, 1)
        ema = torch.nn.Linear(1, 1)
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1.0)
        return Namespace(
            model=model,
            ema_model=ema,
            optimizer=optimizer,
            scheduler=scheduler,
            trainer=FakeTrainer(model, self),
            quality_sampler=object(),
            device=torch.device("cpu"),
        )

    def build_dataloader(self, _dataset, _seed, start_step, stop_step, _num_workers):
        return [(torch.ones(1, 1), torch.zeros(1)) for _ in range(start_step, stop_step)]

    def save_checkpoint(self, *, step: int, **_kwargs) -> Path:
        self.events.append(f"save:{step}")
        self.saved_steps.append(step)
        return Path(f"checkpoint-step{step:06d}.pt")

    @contextmanager
    def preserve_rng(self):
        self.events.append("preserve_enter")
        try:
            yield
        finally:
            self.events.append("preserve_exit")

    def sample_quality(self, *, step: int, **_kwargs) -> None:
        self.events.append(f"sample:{step}")
        self.sampled_steps.append(step)

    def interrupted(self) -> bool:
        return self.interrupt_after is not None and self.completed_steps >= self.interrupt_after


@pytest.fixture(scope="module")
def entrypoint() -> ModuleType:
    script = (
        Path(__file__).resolve().parents[1]
        / "training/ddpm-cifar10/train_ddpm_cifar10_corrected.py"
    )
    spec = importlib.util.spec_from_file_location("corrected_training_entrypoint", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def protocol_files(tmp_path: Path) -> tuple[Path, Path]:
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
    return protocol_path, split_path


def _args(protocol_path: Path, split_path: Path, *, stop_step: int, dry_run: bool) -> Namespace:
    return Namespace(
        protocol_manifest=protocol_path,
        split_path=split_path,
        seed=SEED,
        run_label=f"corrected-preflight-s{SEED}",
        stop_step=stop_step,
        resume=None,
        dataset_root=Path("synthetic-cifar"),
        num_workers=0,
        log_file=None,
        dry_run=dry_run,
        preflight=True,
    )


def test_dry_run_validates_real_contract_without_model_or_outputs(
    entrypoint: ModuleType,
    protocol_files: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol_path, split_path = protocol_files
    runtime = FakeRuntime()
    research_root = tmp_path / "Research"
    download_root = tmp_path / "Download"
    monkeypatch.setattr(entrypoint, "RESEARCH_ROOT", research_root)
    monkeypatch.setattr(entrypoint, "DOWNLOAD_ROOT", download_root)

    summary = entrypoint._train(
        _args(protocol_path, split_path, stop_step=5, dry_run=True), runtime
    )

    assert summary["member_count"] == 25_000
    assert "build_model" not in runtime.events
    assert "configure" not in runtime.events
    assert not download_root.exists()
    assert not research_root.exists()


def test_training_runs_exact_steps_and_saves_periodic_plus_final(
    entrypoint: ModuleType,
    protocol_files: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol_path, split_path = protocol_files
    runtime = FakeRuntime(save_every=2, sample_every=99)
    monkeypatch.setattr(entrypoint, "RESEARCH_ROOT", tmp_path / "Research")
    monkeypatch.setattr(entrypoint, "DOWNLOAD_ROOT", tmp_path / "Download")

    result = entrypoint._train(
        _args(protocol_path, split_path, stop_step=5, dry_run=False), runtime
    )

    assert runtime.completed_steps == 5
    assert runtime.saved_steps == [2, 4, 5]
    assert result["step"] == 5


def test_sampling_executes_inside_rng_preservation(
    entrypoint: ModuleType,
    protocol_files: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol_path, split_path = protocol_files
    runtime = FakeRuntime(save_every=99, sample_every=2)
    monkeypatch.setattr(entrypoint, "RESEARCH_ROOT", tmp_path / "Research")
    monkeypatch.setattr(entrypoint, "DOWNLOAD_ROOT", tmp_path / "Download")

    entrypoint._train(_args(protocol_path, split_path, stop_step=3, dry_run=False), runtime)

    sample_index = runtime.events.index("sample:2")
    assert runtime.events[sample_index - 1 : sample_index + 2] == [
        "preserve_enter",
        "sample:2",
        "preserve_exit",
    ]


def test_signal_interrupt_saves_at_next_step_boundary(
    entrypoint: ModuleType,
    protocol_files: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol_path, split_path = protocol_files
    runtime = FakeRuntime(save_every=99, sample_every=99, interrupt_after=2)
    monkeypatch.setattr(entrypoint, "RESEARCH_ROOT", tmp_path / "Research")
    monkeypatch.setattr(entrypoint, "DOWNLOAD_ROOT", tmp_path / "Download")

    result = entrypoint._train(
        _args(protocol_path, split_path, stop_step=5, dry_run=False), runtime
    )

    assert runtime.completed_steps == 2
    assert runtime.saved_steps == [2]
    assert result == {"step": 2, "interrupted": True}


def test_deterministic_configuration_precedes_environment_and_model_workload(
    entrypoint: ModuleType,
    protocol_files: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol_path, split_path = protocol_files
    runtime = FakeRuntime(save_every=99, sample_every=99)
    monkeypatch.setattr(entrypoint, "RESEARCH_ROOT", tmp_path / "Research")
    monkeypatch.setattr(entrypoint, "DOWNLOAD_ROOT", tmp_path / "Download")

    entrypoint._train(_args(protocol_path, split_path, stop_step=1, dry_run=False), runtime)

    assert runtime.events.index("configure") < runtime.events.index("environment")
    assert runtime.events.index("configure") < runtime.events.index("build_model")


def test_output_manifest_binds_training_config_hash_and_environment(
    entrypoint: ModuleType, tmp_path: Path
) -> None:
    model = torch.nn.Linear(1, 1)
    ema_model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1.0)
    config = build_training_config(num_workers=0)
    environment = {
        "python": "test",
        "pytorch": "test",
        "cuda": None,
        "cudnn": None,
        "gpu_name": None,
        "gpu_uuid": None,
    }
    contract = CorrectedTrainingContract(
        protocol_hash="a" * 64,
        split_sha256="c" * 64,
        code_commit=CODE_COMMIT,
        seed=SEED,
        run_label=f"corrected-s{SEED}",
        training_seeds=(SEED,),
        member_indices=tuple(range(25_000)),
    )

    entrypoint._checkpoint(
        tmp_path,
        contract,
        model,
        ema_model,
        optimizer,
        scheduler,
        1,
        config,
        environment,
    )

    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["training_config"] == config.to_dict()
    assert manifest["training_config_hash"] == canonical_training_config_hash(config)
    assert manifest["environment"] == environment
