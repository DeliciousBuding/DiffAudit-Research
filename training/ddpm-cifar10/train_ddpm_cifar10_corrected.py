"""Train a contract-bound member-only CIFAR-10 DDPM target."""

from __future__ import annotations

import argparse
import copy
import json
import os
import random
import signal
import sys
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
    _atomic_json(
        output_dir / "training-state.json",
        {
            **_identity(contract, step),
            "training_config_hash": training_config_hash,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    _atomic_json(
        output_dir / "manifest.json",
        {
            **_identity(contract, step),
            "checkpoint": path.name,
            "member_count": 25_000,
            "batch_size": training_config.data["batch_size"],
            "training_config": training_config.to_dict(),
            "training_config_hash": training_config_hash,
            "environment": environment,
        },
    )
    return path


def _load_dataset(dataset_root: Path) -> datasets.CIFAR10:
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
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

    def load_dataset(self, root: Path):
        return _load_dataset(root)

    def configure_deterministic(self) -> None:
        configure_deterministic_torch()

    def seed_everything(self, seed: int) -> None:
        _seed_everything(seed)

    def collect_environment(self) -> dict[str, object]:
        return collect_environment()

    def build_training_objects(self, config: TrainingConfig) -> TrainingObjects:
        from diffusion import GaussianDiffusionSampler, GaussianDiffusionTrainer
        from model_unet import UNet

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_config = config.model
        model = UNet(
            T=model_config["T"],
            ch=model_config["channels"],
            ch_mult=list(model_config["channel_multipliers"]),
            attn=list(model_config["attention_levels"]),
            num_res_blocks=model_config["num_res_blocks"],
            dropout=model_config["dropout"],
        ).to(device)
        ema_model = copy.deepcopy(model).to(device)
        optimizer_config = config.optimizer
        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=optimizer_config["learning_rate"],
            betas=tuple(optimizer_config["betas"]),
            eps=optimizer_config["eps"],
        )
        warmup_steps = int(config.scheduler["warmup_steps"])

        def warmup(step: int) -> float:
            return 1.0 if step >= warmup_steps else step / warmup_steps

        scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=warmup)
        diffusion = config.diffusion
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
        self, dataset, seed: int, start_step: int, stop_step: int, num_workers: int
    ):
        return build_corrected_dataloader(
            dataset, seed, start_step, stop_step, num_workers=num_workers
        )

    def save_checkpoint(self, **kwargs) -> Path:
        return _checkpoint(**kwargs)

    def preserve_rng(self):
        return preserve_rng_state()

    def sample_quality(self, *, objects: TrainingObjects, log_dir: Path, step: int) -> None:
        with torch.no_grad():
            noise = torch.randn(64, 3, 32, 32, device=objects.device)
            samples = objects.quality_sampler(noise).cpu()
            torch.save(samples, log_dir / f"quality-step{step:06d}.pt")

    def interrupted(self) -> bool:
        return _interrupted

    def install_signal_handlers(self) -> None:
        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)


def _prepare(args: argparse.Namespace, runtime, training_config: TrainingConfig):
    stop_step = validate_stop_step(args.stop_step, preflight=args.preflight)
    head, tracked_status = runtime.read_repository_state(RESEARCH_ROOT)
    dataset_root = (
        args.dataset_root
        or Path(os.environ.get("DIFFAUDIT_CIFAR10_ROOT", DOWNLOAD_ROOT / "datasets/cifar-10"))
    ).expanduser()
    dataset = runtime.load_dataset(dataset_root)
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

    runtime.configure_deterministic()
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
        args.num_workers,
    )
    if hasattr(runtime, "install_signal_handlers"):
        runtime.install_signal_handlers()
    objects.model.train()
    step = start_step
    for batch, _labels in loader:
        batch = batch.to(objects.device, non_blocking=True)
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
                runtime.sample_quality(objects=objects, log_dir=log_dir, step=step)
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
    print(json.dumps({**_identity(contract, step), **result}, sort_keys=True))
    return result


def main() -> None:
    _train(build_parser().parse_args())


if __name__ == "__main__":
    main()
