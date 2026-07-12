"""Train a contract-bound member-only CIFAR-10 DDPM target."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import random
import signal
import sys
import traceback
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torchvision import datasets, transforms

RESEARCH_ROOT = Path(__file__).resolve().parents[2]
DOWNLOAD_ROOT = Path(
    os.environ.get("DIFFAUDIT_DOWNLOAD_ROOT", RESEARCH_ROOT.parent / "Download")
).expanduser()
sys.path.insert(0, str(RESEARCH_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from diffaudit.training.corrected_ddpm import (  # noqa: E402
    CorrectedTrainingContract,
    TrainingConfig,
    build_corrected_dataloader,
    build_member_subset,
    build_training_config,
    canonical_training_config_hash,
    collect_environment,
    load_corrected_checkpoint,
    load_training_contract,
    read_repository_state,
    save_corrected_checkpoint,
    validate_output_safety,
    validate_repository_state,
    validate_stop_step,
)
from diffaudit.training.exact_resume import (  # noqa: E402
    configure_deterministic_torch,
    preserve_rng_state,
)

_interrupted = False


class _TeeStream:
    def __init__(self, console, log_file) -> None:
        self.console = console
        self.log_file = log_file

    def write(self, value: str) -> int:
        self.console.write(value)
        self.log_file.write(value)
        return len(value)

    def flush(self) -> None:
        self.console.flush()
        self.log_file.flush()

    def __getattr__(self, name: str):
        return getattr(self.console, name)


@contextmanager
def _tee_training_log(path: Path | None):
    if path is None:
        yield
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", buffering=1) as log_file:
        stdout = _TeeStream(sys.stdout, log_file)
        stderr = _TeeStream(sys.stderr, log_file)
        with redirect_stdout(stdout), redirect_stderr(stderr):
            yield


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol-manifest", type=Path, required=True)
    parser.add_argument("--split-path", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--run-label", required=True)
    parser.add_argument("--stop-step", type=int, required=True)
    parser.add_argument("--resume", type=int)
    parser.add_argument("--dataset-root", type=Path)
    parser.add_argument("--num-workers", type=int, default=4)
    parser.add_argument("--log-file", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    return parser


def _signal_handler(signum: int, _frame: Any) -> None:
    global _interrupted
    _interrupted = True
    print(f"received signal {signum}; saving at the next step boundary", flush=True)


@torch.no_grad()
def _ema_update(model: torch.nn.Module, ema_model: torch.nn.Module, *, decay: float) -> None:
    for source, target in zip(model.parameters(), ema_model.parameters(), strict=True):
        target.mul_(decay).add_(source, alpha=1.0 - decay)


def _atomic_json(path: Path, value: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _identity(contract: CorrectedTrainingContract, step: int) -> dict[str, object]:
    return {
        "protocol_hash": contract.protocol_hash,
        "split_sha256": contract.split_sha256,
        "code_commit": contract.code_commit,
        "seed": contract.seed,
        "run_label": contract.run_label,
        "step": step,
    }


def _checkpoint(
    output_dir: Path,
    contract: CorrectedTrainingContract,
    model: torch.nn.Module,
    ema_model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
    step: int,
    training_config: TrainingConfig,
    environment: dict[str, object],
) -> Path:
    path = output_dir / f"checkpoint-step{step:06d}.pt"
    save_corrected_checkpoint(
        path,
        model,
        ema_model,
        optimizer,
        scheduler,
        step=step,
        run_label=contract.run_label,
        seed=contract.seed,
        protocol_hash=contract.protocol_hash,
        split_sha256=contract.split_sha256,
        code_commit=contract.code_commit,
        training_config=training_config,
        environment=environment,
    )
    training_config_hash = canonical_training_config_hash(training_config)
    checkpoint_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path = output_dir / "manifest.json"
    checkpoint_receipts: dict[str, object] = {}
    if manifest_path.exists():
        previous_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        previous_receipts = previous_manifest.get("checkpoint_receipts", {})
        if isinstance(previous_receipts, dict):
            checkpoint_receipts.update(previous_receipts)
    checkpoint_receipts[path.name] = {
        "checkpoint_sha256": checkpoint_sha256,
        "protocol_hash": contract.protocol_hash,
        "code_commit": contract.code_commit,
        "run_seed": contract.seed,
        "step": step,
        "run_label": contract.run_label,
        "training_config_hash": training_config_hash,
    }
    _atomic_json(
        output_dir / "training-state.json",
        {
            **_identity(contract, step),
            "training_config_hash": training_config_hash,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    _atomic_json(
        manifest_path,
        {
            **_identity(contract, step),
            "checkpoint": path.name,
            "member_count": 25_000,
            "batch_size": training_config.data["batch_size"],
            "training_config": training_config.to_dict(),
            "training_config_hash": training_config_hash,
            "environment": environment,
            "checkpoint_receipts": checkpoint_receipts,
        },
    )
    return path


def _load_dataset(dataset_root: Path, config: TrainingConfig) -> datasets.CIFAR10:
    transform_config = config.transform
    if transform_config["operations"] != ("ToTensor", "Normalize"):
        raise ValueError("only the protocol-frozen ToTensor+Normalize transform is supported")
    if transform_config["random_augmentation"] is not False:
        raise ValueError("random training transforms are forbidden")
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize(
                tuple(transform_config["normalize_mean"]),
                tuple(transform_config["normalize_std"]),
            ),
        ]
    )
    return datasets.CIFAR10(root=str(dataset_root), train=True, download=False, transform=transform)


@dataclass(slots=True)
class TrainingObjects:
    model: torch.nn.Module
    ema_model: torch.nn.Module
    optimizer: torch.optim.Optimizer
    scheduler: torch.optim.lr_scheduler.LRScheduler
    trainer: torch.nn.Module
    quality_sampler: torch.nn.Module
    device: torch.device


class ProductionRuntime:
    def training_config(self, num_workers: int) -> TrainingConfig:
        config = build_training_config()
        if num_workers != config.runtime["num_workers"]:
            raise ValueError(
                f"--num-workers must equal protocol-frozen value {config.runtime['num_workers']}"
            )
        return config

    def read_repository_state(self, root: Path) -> tuple[str, str]:
        return read_repository_state(root)

    def load_dataset(self, root: Path, config: TrainingConfig):
        return _load_dataset(root, config)

    def configure_deterministic(self, config: TrainingConfig) -> None:
        if dict(config.determinism) != dict(build_training_config().determinism):
            raise ValueError("unsupported deterministic policy drift")
        configure_deterministic_torch()

    def seed_everything(self, seed: int) -> None:
        _seed_everything(seed)

    def collect_environment(self) -> dict[str, object]:
        return collect_environment()

    def build_training_objects(self, config: TrainingConfig) -> TrainingObjects:
        from diffusion import GaussianDiffusionSampler, GaussianDiffusionTrainer
        from model_unet import UNet

        if dict(config.precision) != {"dtype": "float32", "amp": False}:
            raise ValueError("only protocol-frozen float32 without AMP is supported")
        if config.runtime["device_policy"] != "cuda_if_available_else_cpu":
            raise ValueError("unsupported device policy")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_config = config.model
        if model_config["architecture"] != "UNet":
            raise ValueError("unsupported model architecture")
        model = UNet(
            T=model_config["T"],
            ch=model_config["channels"],
            ch_mult=list(model_config["channel_multipliers"]),
            attn=list(model_config["attention_levels"]),
            num_res_blocks=model_config["num_res_blocks"],
            dropout=model_config["dropout"],
        )
        ema_model = copy.deepcopy(model)
        model = model.to(device)
        ema_model = ema_model.to(device)
        optimizer_config = config.optimizer
        if optimizer_config["name"] != "Adam":
            raise ValueError("unsupported optimizer")
        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=optimizer_config["learning_rate"],
            betas=tuple(optimizer_config["betas"]),
            eps=optimizer_config["eps"],
        )
        warmup_steps = int(config.scheduler["warmup_steps"])
        if config.scheduler["name"] != "LambdaLR" or config.scheduler["policy"] != "linear_warmup":
            raise ValueError("unsupported scheduler policy")

        def warmup(step: int) -> float:
            return 1.0 if step >= warmup_steps else step / warmup_steps

        scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=warmup)
        diffusion = config.diffusion
        if diffusion["schedule"] != "linear":
            raise ValueError("unsupported diffusion schedule")
        trainer = GaussianDiffusionTrainer(
            model,
            beta_1=diffusion["beta_1"],
            beta_T=diffusion["beta_T"],
            T=diffusion["timesteps"],
        ).to(device)
        quality_sampler = GaussianDiffusionSampler(
            ema_model,
            beta_1=diffusion["beta_1"],
            beta_T=diffusion["beta_T"],
            T=diffusion["timesteps"],
            mean_type=diffusion["mean_type"],
            var_type=diffusion["variance_type"],
        ).to(device)
        return TrainingObjects(
            model=model,
            ema_model=ema_model,
            optimizer=optimizer,
            scheduler=scheduler,
            trainer=trainer,
            quality_sampler=quality_sampler,
            device=device,
        )

    def build_dataloader(
        self,
        dataset,
        seed: int,
        start_step: int,
        stop_step: int,
        config: TrainingConfig,
    ):
        pin_memory_policy = config.runtime["pin_memory"]
        if pin_memory_policy != "cuda_available":
            raise ValueError("unsupported pin_memory policy")
        batch_size = config.data["batch_size"]
        num_workers = config.runtime["num_workers"]
        persistent_workers = config.runtime["persistent_workers"]
        if type(batch_size) is not int or batch_size < 1:
            raise ValueError("batch_size must be a positive integer")
        if type(num_workers) is not int or num_workers < 0:
            raise ValueError("num_workers must be a non-negative integer")
        if type(persistent_workers) is not bool:
            raise ValueError("persistent_workers must be a boolean")
        return build_corrected_dataloader(
            dataset,
            seed,
            start_step,
            stop_step,
            batch_size=batch_size,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available(),
            persistent_workers=persistent_workers,
        )

    def save_checkpoint(self, **kwargs) -> Path:
        return _checkpoint(**kwargs)

    def preserve_rng(self):
        return preserve_rng_state()

    def sample_quality(
        self,
        *,
        objects: TrainingObjects,
        log_dir: Path,
        step: int,
        training_config: TrainingConfig,
    ) -> None:
        with torch.no_grad():
            sample_size = int(training_config.checkpointing["quality_sample_size"])
            noise = torch.randn(sample_size, 3, 32, 32, device=objects.device)
            samples = objects.quality_sampler(noise).cpu()
            torch.save(samples, log_dir / f"quality-step{step:06d}.pt")

    def interrupted(self) -> bool:
        return _interrupted

    def install_signal_handlers(self):
        previous = (signal.getsignal(signal.SIGINT), signal.getsignal(signal.SIGTERM))
        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)
        return previous

    def restore_signal_handlers(self, handlers) -> None:
        signal.signal(signal.SIGINT, handlers[0])
        signal.signal(signal.SIGTERM, handlers[1])


def _prepare(args: argparse.Namespace, runtime, training_config: TrainingConfig):
    stop_step = validate_stop_step(args.stop_step, preflight=args.preflight)
    head, tracked_status = runtime.read_repository_state(RESEARCH_ROOT)
    dataset_root = (
        args.dataset_root
        or Path(os.environ.get("DIFFAUDIT_CIFAR10_ROOT", DOWNLOAD_ROOT / "datasets/cifar-10"))
    ).expanduser()
    dataset = runtime.load_dataset(dataset_root, training_config)
    labels = np.asarray(dataset.targets, dtype=np.int64)
    contract = load_training_contract(
        args.protocol_manifest,
        args.split_path,
        labels,
        head,
        args.seed,
        args.run_label,
    )
    validate_repository_state(head, contract.code_commit, tracked_status)
    member_dataset = build_member_subset(dataset, contract.member_indices)
    output_dir = DOWNLOAD_ROOT / "checkpoints" / contract.run_label
    log_dir = RESEARCH_ROOT / "training" / "outputs" / contract.run_label
    validate_output_safety(
        output_dir,
        log_dir,
        DOWNLOAD_ROOT,
        RESEARCH_ROOT,
        resume_step=args.resume,
    )
    if args.resume is not None and args.resume >= stop_step:
        raise ValueError("--resume must be less than --stop-step")
    if args.num_workers < 0:
        raise ValueError("--num-workers must be non-negative")
    if training_config.runtime["num_workers"] != args.num_workers:
        raise ValueError("training config num_workers does not match CLI")
    if training_config.to_dict() != contract.training_config.to_dict():
        raise ValueError("runtime training_config does not match frozen protocol config")
    if canonical_training_config_hash(training_config) != contract.training_config_hash:
        raise ValueError("runtime training_config_hash does not match frozen protocol hash")
    if args.log_file is not None:
        requested_log = args.log_file.resolve()
        try:
            requested_log.relative_to(log_dir.resolve())
        except ValueError as error:
            raise ValueError("--log-file must stay inside the corrected log directory") from error
    return contract, member_dataset, output_dir, log_dir, stop_step


def _seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed % (2**32))
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _move_batch(batch, device: torch.device, training_config: TrainingConfig):
    non_blocking = training_config.runtime["non_blocking_device_transfer"]
    if type(non_blocking) is not bool:
        raise ValueError("non_blocking_device_transfer must be a boolean")
    return batch.to(device, non_blocking=non_blocking)


def _run_formal_training(
    args: argparse.Namespace,
    runtime,
    training_config: TrainingConfig,
    contract: CorrectedTrainingContract,
    member_dataset,
    output_dir: Path,
    log_dir: Path,
    stop_step: int,
) -> dict[str, object]:
    runtime.configure_deterministic(training_config)
    runtime.seed_everything(contract.seed)
    environment = runtime.collect_environment()
    objects = runtime.build_training_objects(training_config)
    start_step = args.resume or 0
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    if args.resume is not None:
        load_corrected_checkpoint(
            output_dir / f"checkpoint-step{args.resume:06d}.pt",
            objects.model,
            objects.ema_model,
            objects.optimizer,
            objects.scheduler,
            expected_step=args.resume,
            expected_run_label=contract.run_label,
            expected_seed=contract.seed,
            expected_protocol_hash=contract.protocol_hash,
            expected_split_sha256=contract.split_sha256,
            expected_code_commit=contract.code_commit,
            expected_training_config_hash=contract.training_config_hash,
            expected_environment=environment,
        )
    loader = runtime.build_dataloader(
        member_dataset,
        contract.seed,
        start_step,
        stop_step,
        training_config,
    )
    handlers = None
    handlers_installed = False
    if hasattr(runtime, "install_signal_handlers"):
        handlers = runtime.install_signal_handlers()
        handlers_installed = True
    try:
        objects.model.train()
        step = start_step
        for batch, _labels in loader:
            batch = _move_batch(batch, objects.device, training_config)
            objects.optimizer.zero_grad(set_to_none=True)
            loss = objects.trainer(batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(objects.model.parameters(), training_config.grad_clip)
            objects.optimizer.step()
            objects.scheduler.step()
            _ema_update(objects.model, objects.ema_model, decay=training_config.ema_decay)
            step += 1
            if step % int(training_config.checkpointing["save_every"]) == 0:
                runtime.save_checkpoint(
                    output_dir=output_dir,
                    contract=contract,
                    model=objects.model,
                    ema_model=objects.ema_model,
                    optimizer=objects.optimizer,
                    scheduler=objects.scheduler,
                    step=step,
                    training_config=training_config,
                    environment=environment,
                )
            if step % int(training_config.checkpointing["sample_every"]) == 0:
                with runtime.preserve_rng():
                    runtime.sample_quality(
                        objects=objects,
                        log_dir=log_dir,
                        step=step,
                        training_config=training_config,
                    )
            if runtime.interrupted():
                break
        if step % int(training_config.checkpointing["save_every"]) != 0:
            runtime.save_checkpoint(
                output_dir=output_dir,
                contract=contract,
                model=objects.model,
                ema_model=objects.ema_model,
                optimizer=objects.optimizer,
                scheduler=objects.scheduler,
                step=step,
                training_config=training_config,
                environment=environment,
            )
        result = {"step": step, "interrupted": runtime.interrupted()}
    finally:
        if handlers_installed and hasattr(runtime, "restore_signal_handlers"):
            runtime.restore_signal_handlers(handlers)
    return result


def _train(args: argparse.Namespace, runtime=None) -> dict[str, object]:
    runtime = runtime or ProductionRuntime()
    training_config = runtime.training_config(args.num_workers)
    contract, member_dataset, output_dir, log_dir, stop_step = _prepare(
        args, runtime, training_config
    )
    if args.dry_run:
        summary = {
            **_identity(contract, args.resume or 0),
            "dataset": "CIFAR10",
            "dataset_size": 50_000,
            "member_count": len(member_dataset),
            "stop_step": stop_step,
            "preflight": args.preflight,
            "repository_clean": True,
            "output_scope": "corrected-only",
            "training_config_hash": canonical_training_config_hash(training_config),
        }
        print(json.dumps(summary, sort_keys=True))
        return summary

    global _interrupted
    _interrupted = False
    log_file = args.log_file.resolve() if args.log_file is not None else None
    with _tee_training_log(log_file):
        start = {
            "event": "training_start",
            **_identity(contract, args.resume or 0),
            "stop_step": stop_step,
        }
        print(json.dumps(start, sort_keys=True))
        try:
            result = _run_formal_training(
                args,
                runtime,
                training_config,
                contract,
                member_dataset,
                output_dir,
                log_dir,
                stop_step,
            )
        except BaseException:
            print(json.dumps({"event": "training_error"}, sort_keys=True), file=sys.stderr)
            traceback.print_exc()
            raise
        terminal = {"event": "training_end", **_identity(contract, result["step"]), **result}
        print(json.dumps(terminal, sort_keys=True))
        return result


def main() -> None:
    _train(build_parser().parse_args())


if __name__ == "__main__":
    main()
