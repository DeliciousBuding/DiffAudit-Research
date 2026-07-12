from __future__ import annotations

import hashlib
import importlib.util
import json
import signal
import sys
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


class FakeBatch:
    def to(self, *_args, **_kwargs):
        return self


class FakeLoss:
    def backward(self) -> None:
        return None


class FakeModel:
    def train(self) -> None:
        return None

    def parameters(self):
        return iter(())


class FakeOptimizer:
    def zero_grad(self, **_kwargs) -> None:
        return None

    def step(self) -> None:
        return None


class FakeScheduler:
    def step(self) -> None:
        return None


class FakeTrainer:
    def __init__(self, runtime: "FakeRuntime") -> None:
        self.runtime = runtime

    def __call__(self, _batch: FakeBatch) -> FakeLoss:
        self.runtime.completed_steps += 1
        if self.runtime.after_step is not None:
            self.runtime.after_step(self.runtime.completed_steps)
        return FakeLoss()


class FakeRuntime:
    def __init__(
        self,
        *,
        interrupt_after: int | None = None,
        interrupted_callback=None,
        reject_side_effects: bool = False,
        raise_on_build: bool = False,
        after_step=None,
    ) -> None:
        self.events: list[str] = []
        self.saved_steps: list[int] = []
        self.sampled_steps: list[int] = []
        self.completed_steps = 0
        self.interrupt_after = interrupt_after
        self.interrupted_callback = interrupted_callback
        self.reject_side_effects = reject_side_effects
        self.raise_on_build = raise_on_build
        self.after_step = after_step
        self.config = build_training_config()

    def training_config(self, num_workers: int):
        assert num_workers == 4
        return self.config

    def read_repository_state(self, _root: Path) -> tuple[str, str]:
        return CODE_COMMIT, ""

    def load_dataset(self, _root: Path, _config) -> SyntheticCIFAR:
        self.events.append("dataset")
        return SyntheticCIFAR()

    def configure_deterministic(self, _config) -> None:
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
        if self.raise_on_build:
            raise RuntimeError("injected build failure")
        model = FakeModel()
        return Namespace(
            model=model,
            ema_model=FakeModel(),
            optimizer=FakeOptimizer(),
            scheduler=FakeScheduler(),
            trainer=FakeTrainer(self),
            quality_sampler=object(),
            device=torch.device("cpu"),
        )

    def build_dataloader(self, _dataset, _seed, start_step, stop_step, _config):
        return ((FakeBatch(), None) for _ in range(start_step, stop_step))

    def save_checkpoint(self, *, step: int, **_kwargs) -> Path:
        if self.reject_side_effects:
            raise AssertionError("dry-run must not call checkpoint saving")
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
        if self.reject_side_effects:
            raise AssertionError("dry-run must not call sampling")
        self.events.append(f"sample:{step}")
        self.sampled_steps.append(step)

    def interrupted(self) -> bool:
        if self.interrupted_callback is not None:
            return bool(self.interrupted_callback())
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
        num_workers=4,
        log_file=None,
        dry_run=dry_run,
        preflight=stop_step <= 5_000,
    )


def test_dry_run_validates_real_contract_without_model_or_outputs(
    entrypoint: ModuleType,
    protocol_files: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol_path, split_path = protocol_files
    runtime = FakeRuntime(reject_side_effects=True)
    research_root = tmp_path / "Research"
    download_root = tmp_path / "Download"
    monkeypatch.setattr(entrypoint, "RESEARCH_ROOT", research_root)
    monkeypatch.setattr(entrypoint, "DOWNLOAD_ROOT", download_root)
    monkeypatch.delitem(sys.modules, "model_unet", raising=False)
    monkeypatch.delitem(sys.modules, "diffusion", raising=False)

    summary = entrypoint._train(
        _args(protocol_path, split_path, stop_step=5, dry_run=True), runtime
    )

    assert summary["member_count"] == 25_000
    assert "build_model" not in runtime.events
    assert "configure" not in runtime.events
    assert "model_unet" not in sys.modules
    assert "diffusion" not in sys.modules
    assert not any(event.startswith(("save:", "sample:")) for event in runtime.events)
    assert not download_root.exists()
    assert not research_root.exists()


def test_production_runtime_rejects_num_workers_outside_frozen_protocol(
    entrypoint: ModuleType,
) -> None:
    with pytest.raises(ValueError, match="protocol-frozen"):
        entrypoint.ProductionRuntime().training_config(0)


def test_training_runs_exact_steps_and_saves_periodic_plus_final(
    entrypoint: ModuleType,
    protocol_files: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol_path, split_path = protocol_files
    runtime = FakeRuntime()
    monkeypatch.setattr(entrypoint, "RESEARCH_ROOT", tmp_path / "Research")
    monkeypatch.setattr(entrypoint, "DOWNLOAD_ROOT", tmp_path / "Download")

    result = entrypoint._train(
        _args(protocol_path, split_path, stop_step=2_000, dry_run=False), runtime
    )

    assert runtime.completed_steps == 2_000
    assert runtime.saved_steps == [2_000]
    assert result["step"] == 2_000

    final_runtime = FakeRuntime()
    result = entrypoint._train(
        _args(protocol_path, split_path, stop_step=2_001, dry_run=False), final_runtime
    )
    assert final_runtime.saved_steps == [2_000, 2_001]
    assert result["step"] == 2_001


def test_sampling_executes_inside_rng_preservation(
    entrypoint: ModuleType,
    protocol_files: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol_path, split_path = protocol_files
    runtime = FakeRuntime()
    monkeypatch.setattr(entrypoint, "RESEARCH_ROOT", tmp_path / "Research")
    monkeypatch.setattr(entrypoint, "DOWNLOAD_ROOT", tmp_path / "Download")

    entrypoint._train(_args(protocol_path, split_path, stop_step=100_000, dry_run=False), runtime)

    sample_index = runtime.events.index("sample:50000")
    assert runtime.events[sample_index - 1 : sample_index + 2] == [
        "preserve_enter",
        "sample:50000",
        "preserve_exit",
    ]
    assert runtime.sampled_steps == [50_000, 100_000]


def test_signal_interrupt_saves_at_next_step_boundary(
    entrypoint: ModuleType,
    protocol_files: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol_path, split_path = protocol_files
    runtime = FakeRuntime(interrupt_after=2)
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
    runtime = FakeRuntime()
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
    config = build_training_config()
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
        training_config=config,
        training_config_hash=canonical_training_config_hash(config),
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
    receipt = manifest["checkpoint_receipts"]["checkpoint-step000001.pt"]
    assert receipt == {
        "checkpoint_sha256": hashlib.sha256(
            (tmp_path / "checkpoint-step000001.pt").read_bytes()
        ).hexdigest(),
        "protocol_hash": contract.protocol_hash,
        "code_commit": contract.code_commit,
        "run_seed": contract.seed,
        "step": 1,
        "run_label": contract.run_label,
        "training_config_hash": contract.training_config_hash,
    }


def test_runbook_uses_only_corrected_entrypoint_with_required_identity_arguments() -> None:
    runbook = (
        Path(__file__).resolve().parents[1]
        / "docs/start-here/paper1-corrected-evidence-runbook-2026-07-11.md"
    ).read_text(encoding="utf-8")
    corrected_command = "training/ddpm-cifar10/train_ddpm_cifar10_corrected.py"

    assert "training/ddpm-cifar10/train_ddpm_cifar10.py" not in runbook
    assert runbook.count(corrected_command) == 3
    for option in (
        "--protocol-manifest",
        "--split-path",
        "--seed",
        "--run-label",
        "--stop-step",
    ):
        assert runbook.count(option) >= 3
    assert "--preflight" in runbook
    assert "--resume 100000" in runbook


def test_production_build_deepcopies_ema_while_model_is_still_on_cpu(
    entrypoint: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    events: list[str] = []

    class FakeUNet(torch.nn.Module):
        def __init__(self, **_kwargs) -> None:
            super().__init__()
            self.weight = torch.nn.Parameter(torch.ones(1))
            self.logical_device = "cpu"

        def __deepcopy__(self, _memo):
            events.append(f"deepcopy:{self.logical_device}")
            clone = FakeUNet()
            clone.weight.data.copy_(self.weight.data)
            return clone

        def to(self, device):
            self.logical_device = str(device)
            events.append(f"model_to:{self.logical_device}")
            return self

    class FakeDiffusion:
        def __init__(self, *_args, **_kwargs) -> None:
            return None

        def to(self, device):
            events.append(f"diffusion_to:{device}")
            return self

    model_module = ModuleType("model_unet")
    model_module.UNet = FakeUNet
    diffusion_module = ModuleType("diffusion")
    diffusion_module.GaussianDiffusionTrainer = FakeDiffusion
    diffusion_module.GaussianDiffusionSampler = FakeDiffusion
    monkeypatch.setitem(sys.modules, "model_unet", model_module)
    monkeypatch.setitem(sys.modules, "diffusion", diffusion_module)
    monkeypatch.setattr(entrypoint.torch.cuda, "is_available", lambda: True)

    entrypoint.ProductionRuntime().build_training_objects(build_training_config())

    assert events.count("deepcopy:cpu") == 1
    assert events.index("deepcopy:cpu") < events.index("model_to:cuda")


def _log_path(research_root: Path) -> Path:
    return research_root / "training" / "outputs" / f"corrected-preflight-s{SEED}" / "training.log"


def test_formal_training_tees_console_and_writes_normal_terminal_log(
    entrypoint: ModuleType,
    protocol_files: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    protocol_path, split_path = protocol_files
    research_root = tmp_path / "Research"
    monkeypatch.setattr(entrypoint, "RESEARCH_ROOT", research_root)
    monkeypatch.setattr(entrypoint, "DOWNLOAD_ROOT", tmp_path / "Download")
    args = _args(protocol_path, split_path, stop_step=1, dry_run=False)
    args.log_file = _log_path(research_root)

    entrypoint._train(args, FakeRuntime())

    logged = args.log_file.read_text(encoding="utf-8")
    captured = capsys.readouterr()
    assert '"event": "training_start"' in logged
    assert '"event": "training_end"' in logged
    assert '"step": 1' in logged
    assert '"interrupted": false' in logged
    assert '"event": "training_end"' in captured.out


class SignalLifecycleRuntime(FakeRuntime):
    def __init__(self, entrypoint: ModuleType, *, trigger_signal: bool) -> None:
        self.entrypoint = entrypoint
        self.trigger_signal = trigger_signal
        super().__init__(
            interrupted_callback=lambda: entrypoint._interrupted,
            after_step=self._after_step,
        )

    def install_signal_handlers(self):
        return self.entrypoint.ProductionRuntime().install_signal_handlers()

    def restore_signal_handlers(self, handlers) -> None:
        self.entrypoint.ProductionRuntime().restore_signal_handlers(handlers)

    def _after_step(self, step: int) -> None:
        if self.trigger_signal and step == 1:
            handler = signal.getsignal(signal.SIGINT)
            assert callable(handler)
            handler(signal.SIGINT, None)


def test_signal_handlers_logs_interrupt_restores_handlers_and_does_not_leak_state(
    entrypoint: ModuleType,
    protocol_files: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol_path, split_path = protocol_files
    research_root = tmp_path / "Research"
    monkeypatch.setattr(entrypoint, "RESEARCH_ROOT", research_root)
    monkeypatch.setattr(entrypoint, "DOWNLOAD_ROOT", tmp_path / "Download")
    original = (signal.getsignal(signal.SIGINT), signal.getsignal(signal.SIGTERM))
    first_args = _args(protocol_path, split_path, stop_step=5, dry_run=False)
    first_args.log_file = _log_path(research_root)

    first = entrypoint._train(first_args, SignalLifecycleRuntime(entrypoint, trigger_signal=True))

    assert first == {"step": 1, "interrupted": True}
    assert '"interrupted": true' in first_args.log_file.read_text(encoding="utf-8")
    assert (signal.getsignal(signal.SIGINT), signal.getsignal(signal.SIGTERM)) == original

    second_args = _args(protocol_path, split_path, stop_step=2, dry_run=False)
    second_args.log_file = first_args.log_file.with_name("training-second.log")
    second = entrypoint._train(
        second_args, SignalLifecycleRuntime(entrypoint, trigger_signal=False)
    )
    assert second == {"step": 2, "interrupted": False}
    assert (signal.getsignal(signal.SIGINT), signal.getsignal(signal.SIGTERM)) == original


def test_training_exception_logs_traceback_and_restores_streams(
    entrypoint: ModuleType,
    protocol_files: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol_path, split_path = protocol_files
    research_root = tmp_path / "Research"
    monkeypatch.setattr(entrypoint, "RESEARCH_ROOT", research_root)
    monkeypatch.setattr(entrypoint, "DOWNLOAD_ROOT", tmp_path / "Download")
    args = _args(protocol_path, split_path, stop_step=1, dry_run=False)
    args.log_file = _log_path(research_root)
    stdout_before, stderr_before = sys.stdout, sys.stderr

    with pytest.raises(RuntimeError, match="injected build failure"):
        entrypoint._train(args, FakeRuntime(raise_on_build=True))

    assert sys.stdout is stdout_before
    assert sys.stderr is stderr_before
    logged = args.log_file.read_text(encoding="utf-8")
    assert "Traceback (most recent call last)" in logged
    assert "injected build failure" in logged
    args.log_file.rename(args.log_file.with_suffix(".closed"))


def test_dry_run_does_not_create_requested_log_file(
    entrypoint: ModuleType,
    protocol_files: tuple[Path, Path],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protocol_path, split_path = protocol_files
    research_root = tmp_path / "Research"
    monkeypatch.setattr(entrypoint, "RESEARCH_ROOT", research_root)
    monkeypatch.setattr(entrypoint, "DOWNLOAD_ROOT", tmp_path / "Download")
    args = _args(protocol_path, split_path, stop_step=1, dry_run=True)
    args.log_file = _log_path(research_root)

    entrypoint._train(args, FakeRuntime(reject_side_effects=True))

    assert not args.log_file.exists()


def test_production_dataloader_receives_all_frozen_runtime_and_batch_fields(
    entrypoint: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, object] = {}

    def fake_builder(dataset, seed, start_step, stop_step, **kwargs):
        captured.update(
            dataset=dataset,
            seed=seed,
            start_step=start_step,
            stop_step=stop_step,
            **kwargs,
        )
        return "loader"

    monkeypatch.setattr(entrypoint, "build_corrected_dataloader", fake_builder)
    monkeypatch.setattr(entrypoint.torch.cuda, "is_available", lambda: False)
    config = build_training_config()

    result = entrypoint.ProductionRuntime().build_dataloader("dataset", SEED, 3, 9, config)

    assert result == "loader"
    assert captured == {
        "dataset": "dataset",
        "seed": SEED,
        "start_step": 3,
        "stop_step": 9,
        "batch_size": 64,
        "num_workers": 4,
        "pin_memory": False,
        "persistent_workers": True,
    }


def test_batch_transfer_uses_frozen_non_blocking_policy(entrypoint: ModuleType) -> None:
    calls: list[tuple[object, bool]] = []

    class RecordingBatch:
        def to(self, device, *, non_blocking: bool):
            calls.append((device, non_blocking))
            return self

    config = build_training_config()
    runtime_fields = dict(config.runtime)
    runtime_fields["non_blocking_device_transfer"] = False
    drifted = replace(config, runtime=MappingProxyType(runtime_fields))
    device = torch.device("cpu")

    assert entrypoint._move_batch(RecordingBatch(), device, drifted) is not None
    assert calls == [(device, False)]


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("data", "batch_size", "64"),
        ("runtime", "num_workers", "4"),
        ("runtime", "persistent_workers", "true"),
    ],
)
def test_production_dataloader_rejects_noncanonical_runtime_field_types(
    entrypoint: ModuleType,
    section: str,
    field: str,
    value: object,
) -> None:
    config = build_training_config()
    changed_section = dict(getattr(config, section))
    changed_section[field] = value
    drifted = replace(config, **{section: MappingProxyType(changed_section)})

    with pytest.raises((TypeError, ValueError), match=field):
        entrypoint.ProductionRuntime().build_dataloader("dataset", SEED, 0, 1, drifted)
