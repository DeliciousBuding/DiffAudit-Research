"""Train a contract-bound member-only CIFAR-10 DDPM target."""

from __future__ import annotations

import argparse
import copy
import json
import os
import random
import signal
import sys
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
    build_corrected_dataloader,
    build_member_subset,
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

BATCH_SIZE = 64
SAVE_EVERY = 2_000
SAMPLE_EVERY = 50_000
T = 1_000
CH = 128
CH_MULT = [1, 2, 2, 2]
ATTN = [1]
NUM_RES_BLOCKS = 2
DROPOUT = 0.1
BETA_1 = 0.0001
BETA_T = 0.02
LR = 2e-4
EMA_DECAY = 0.9999
GRAD_CLIP = 1.0
WARMUP_STEPS = 5_000
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


def _warmup(step: int) -> float:
    return 1.0 if step >= WARMUP_STEPS else step / WARMUP_STEPS


@torch.no_grad()
def _ema_update(model: torch.nn.Module, ema_model: torch.nn.Module) -> None:
    for source, target in zip(model.parameters(), ema_model.parameters(), strict=True):
        target.mul_(EMA_DECAY).add_(source, alpha=1.0 - EMA_DECAY)


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
    )
    _atomic_json(
        output_dir / "training-state.json",
        {**_identity(contract, step), "updated_at": datetime.now(timezone.utc).isoformat()},
    )
    _atomic_json(
        output_dir / "manifest.json",
        {
            **_identity(contract, step),
            "checkpoint": path.name,
            "member_count": 25_000,
            "batch_size": BATCH_SIZE,
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


def _prepare(args: argparse.Namespace):
    stop_step = validate_stop_step(args.stop_step, preflight=args.preflight)
    head, tracked_status = read_repository_state(RESEARCH_ROOT)
    dataset_root = (
        args.dataset_root
        or Path(os.environ.get("DIFFAUDIT_CIFAR10_ROOT", DOWNLOAD_ROOT / "datasets/cifar-10"))
    ).expanduser()
    dataset = _load_dataset(dataset_root)
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


def _train(args: argparse.Namespace) -> None:
    contract, member_dataset, output_dir, log_dir, stop_step = _prepare(args)
    if args.dry_run:
        print(
            json.dumps(
                {
                    **_identity(contract, args.resume or 0),
                    "dataset": "CIFAR10",
                    "dataset_size": 50_000,
                    "member_count": len(member_dataset),
                    "stop_step": stop_step,
                    "preflight": args.preflight,
                    "repository_clean": True,
                    "output_scope": "corrected-only",
                },
                sort_keys=True,
            )
        )
        return

    configure_deterministic_torch()
    _seed_everything(contract.seed)
    from diffusion import GaussianDiffusionSampler, GaussianDiffusionTrainer
    from model_unet import UNet

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = UNet(
        T=T,
        ch=CH,
        ch_mult=CH_MULT,
        attn=ATTN,
        num_res_blocks=NUM_RES_BLOCKS,
        dropout=DROPOUT,
    ).to(device)
    ema_model = copy.deepcopy(model).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=_warmup)
    trainer = GaussianDiffusionTrainer(model, beta_1=BETA_1, beta_T=BETA_T, T=T).to(device)
    quality_sampler = GaussianDiffusionSampler(
        ema_model, beta_1=BETA_1, beta_T=BETA_T, T=T
    ).to(device)
    start_step = args.resume or 0
    output_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    if args.resume is not None:
        load_corrected_checkpoint(
            output_dir / f"checkpoint-step{args.resume:06d}.pt",
            model,
            ema_model,
            optimizer,
            scheduler,
            expected_step=args.resume,
            expected_run_label=contract.run_label,
            expected_seed=contract.seed,
            expected_protocol_hash=contract.protocol_hash,
            expected_split_sha256=contract.split_sha256,
            expected_code_commit=contract.code_commit,
        )
    loader = build_corrected_dataloader(
        member_dataset,
        contract.seed,
        start_step,
        stop_step,
        num_workers=args.num_workers,
    )
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)
    model.train()
    step = start_step
    for batch, _labels in loader:
        batch = batch.to(device, non_blocking=True)
        optimizer.zero_grad(set_to_none=True)
        loss = trainer(batch)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)
        optimizer.step()
        scheduler.step()
        _ema_update(model, ema_model)
        step += 1
        if step % SAVE_EVERY == 0:
            _checkpoint(output_dir, contract, model, ema_model, optimizer, scheduler, step)
        if step % SAMPLE_EVERY == 0:
            with preserve_rng_state(), torch.no_grad():
                noise = torch.randn(64, 3, 32, 32, device=device)
                samples = quality_sampler(noise).cpu()
                torch.save(samples, log_dir / f"quality-step{step:06d}.pt")
        if _interrupted:
            break
    _checkpoint(output_dir, contract, model, ema_model, optimizer, scheduler, step)
    print(json.dumps({**_identity(contract, step), "interrupted": _interrupted}, sort_keys=True))


def main() -> None:
    _train(build_parser().parse_args())


if __name__ == "__main__":
    main()
