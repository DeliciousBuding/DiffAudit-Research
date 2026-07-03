#!/usr/bin/env python
"""
Train DDPM on CIFAR-10 for Phase G run-dynamics replication.
Reliability: checkpoint every 2k steps (~15min), SIGINT/SIGTERM graceful save,
line-buffered log file, resume from any step, heartbeat monitoring.

Purpose: Produce parameterized ddpm-cifar10-seed<N> checkpoints for run-identity
         replication in Phase G of Paper 1.

Output: <DOWNLOAD_ROOT>/checkpoints/ddpm-cifar10-seed<N>/
Storage: ~548 MB per checkpoint (kept: every 100k + last 10 saves)
Total GPU time: ~133h for 800k steps on RTX 4070 8GB

Usage:
  python -u train_ddpm_cifar10.py --seed 45 --stop-step 750000
  python -u train_ddpm_cifar10.py --seed 45 --run-label ddpm-cifar10-seed45 --resume
  python -u train_ddpm_cifar10.py --seed 45 --resume 38000 --stop-step 750000
  python -u train_ddpm_cifar10.py --seed 45 --resume --log-file training-750k.log
  python -u train_ddpm_cifar10.py --seed 45 --dry-run

Graceful interrupt: Ctrl+C or kill saves checkpoint at current step.
Resume from interrupt: --resume (auto-detects latest checkpoint).
"""
import sys
import os
import time
import json
import argparse
import hashlib
import signal
from pathlib import Path
from datetime import datetime, timezone

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.tensorboard import SummaryWriter
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# --- Project paths ---
PROJECT = Path(__file__).resolve().parents[2]  # Research/
DOWNLOAD = Path(os.environ.get("DIFFAUDIT_DOWNLOAD_ROOT", PROJECT.parent / "Download"))
RUN_LABEL = "ddpm-cifar10-seed43"
OUTPUT_DIR = DOWNLOAD / "checkpoints" / RUN_LABEL
LOG_DIR = PROJECT / "training" / "outputs" / RUN_LABEL


def _resolve_cifar10_root() -> Path:
    direct = os.environ.get("DIFFAUDIT_CIFAR10_ROOT")
    if direct:
        return Path(direct).expanduser()

    dataset_root = os.environ.get("DIFFAUDIT_DATASET_ROOT")
    if dataset_root:
        return Path(dataset_root).expanduser() / "cifar10"

    return DOWNLOAD / "datasets" / "cifar-10"


DATASET_DIR = _resolve_cifar10_root()

# --- Add local modules ---
sys.path.insert(0, str(PROJECT / "training" / "ddpm-cifar10"))
from model_unet import UNet
from diffusion import GaussianDiffusionTrainer, GaussianDiffusionSampler
from dataset_utils import load_member_data
import components

# ============================================================================
# CONFIG (must match ddpm-cifar10-800k exactly, except TOTAL_STEPS)
# ============================================================================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 43

# UNet architecture (DDPM CIFAR-10 standard)
T = 1000
CH = 128
CH_MULT = [1, 2, 2, 2]
ATTN = [1]
NUM_RES_BLOCKS = 2
DROPOUT = 0.1

# Training hyperparams
BETA_1 = 0.0001
BETA_T = 0.02
LR = 2e-4
BATCH_SIZE = 64
TOTAL_STEPS = 800_000  # Default max; --stop-step overrides
EMA_DECAY = 0.9999
GRAD_CLIP = 1.0
WARMUP_STEPS = 5000

# Checkpointing
SAVE_EVERY = 2_000        # Save every 2k steps (~15min at 8k/hr)
KEEP_EVERY = 100_000      # Archive every 100k
CKPT_FILENAME = "checkpoint.pt"
STATE_FILENAME = "training_state.json"

# Sampling
EVAL_SAMPLE_SIZE = 64
SAMPLE_EVERY = 50_000      # Generate samples for quality check

# ── Signal handling for graceful interrupt ──
_interrupted = False
_train_state = None  # will hold (model, ema, optim, sched, step, stop_step) for handler

def _signal_handler(signum, frame):
    global _interrupted
    print(f"\n  [SIGNAL] Received signal {signum}, saving checkpoint before exit...", flush=True)
    _interrupted = True


def setup_dirs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR, LOG_DIR


def warmup_lr(step):
    if step >= WARMUP_STEPS:
        return 1.0
    return step / WARMUP_STEPS


def ema_update(source, target, decay):
    sd = source.state_dict()
    td = target.state_dict()
    for k in sd:
        td[k].data.copy_(td[k].data * decay + sd[k].data * (1.0 - decay))


@torch.no_grad()
def sample_and_save(model, sampler, step, log_dir, device):
    """Generate sample images for visual quality check."""
    model.eval()
    noise = torch.randn(EVAL_SAMPLE_SIZE, 3, 32, 32, device=device)
    samples = sampler(noise)
    samples = (samples.clamp(-1, 1) + 1) / 2  # [-1,1] -> [0,1]
    model.train()
    # Save as .npy for lightweight storage
    np.save(log_dir / f"samples-step{step:06d}.npy", samples.cpu().numpy())
    return samples


def get_checkpoint_path(step: int) -> Path:
    return OUTPUT_DIR / f"checkpoint-step{step:06d}.pt"


def find_latest_checkpoint() -> int | None:
    """Find the most recent checkpoint file, return step number or None."""
    if not OUTPUT_DIR.exists():
        return None
    ckpts = sorted(OUTPUT_DIR.glob("checkpoint-step*.pt"))
    if not ckpts:
        return None
    # Parse step numbers
    steps = []
    for ckpt in ckpts:
        try:
            s = int(ckpt.stem.replace("checkpoint-step", ""))
            steps.append(s)
        except ValueError:
            continue
    return max(steps) if steps else None


def save_checkpoint(model, ema_model, optimizer, scheduler, step, extra=None):
    """Save a full training checkpoint with optimizer state for resume."""
    ckpt = {
        "net_model": model.state_dict(),
        "ema_model": ema_model.state_dict(),
        "sched": scheduler.state_dict(),
        "optim": optimizer.state_dict(),
        "step": step,
        "x_T": torch.randn(1, 3, 32, 32),
    }
    if extra:
        ckpt.update(extra)

    path = get_checkpoint_path(step)
    torch.save(ckpt, path)

    # Also save as canonical name for H1 scripts
    canonical = OUTPUT_DIR / CKPT_FILENAME
    torch.save(ckpt, canonical)

    # Clean up old frequent checkpoints (keep only every 100k + last 10)
    all_ckpts = sorted(OUTPUT_DIR.glob("checkpoint-step*.pt"))
    for c in all_ckpts:
        c_step = int(c.stem.replace("checkpoint-step", ""))
        if c_step % KEEP_EVERY != 0 and c_step != step and c_step > (step - 10 * SAVE_EVERY):
            # Keep this one (within last 10 saves)
            pass
        elif c_step % KEEP_EVERY != 0 and c_step < (step - 10 * SAVE_EVERY):
            c.unlink(missing_ok=True)

    return path


def save_state(step, total, metrics, extra=None):
    """Save lightweight training state as JSON for quick resume info."""
    state = {
        "step": step,
        "total_steps": total,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
    }
    if extra:
        state.update(extra)
    (OUTPUT_DIR / STATE_FILENAME).write_text(json.dumps(state, indent=2))


def load_checkpoint(resume_step: int = None):
    """Load checkpoint. If resume_step is given, load that specific step.
    Otherwise load the latest."""
    if resume_step is not None:
        path = get_checkpoint_path(resume_step)
        if not path.exists():
            raise FileNotFoundError(f"No checkpoint at step {resume_step}: {path}")
    else:
        latest = find_latest_checkpoint()
        if latest is None:
            return None, 0
        path = get_checkpoint_path(latest)

    print(f"Loading checkpoint: {path}")
    ckpt = torch.load(path, map_location=DEVICE, weights_only=False)
    return ckpt, ckpt["step"]


def build_dataloader(dataset_dir: Path, batch_size: int):
    """Build CIFAR-10 training dataloader (members only for our use case)."""
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])
    dataset = datasets.CIFAR10(
        root=str(dataset_dir), train=True, download=False, transform=transform
    )
    loader = DataLoader(
        dataset, batch_size=batch_size, shuffle=True,
        num_workers=4, pin_memory=True, drop_last=True,
    )
    return loader


def compute_gradient_norm(model):
    total = 0.0
    for p in model.parameters():
        if p.grad is not None:
            total += p.grad.data.norm(2).item() ** 2
    return total ** 0.5


def compute_checksum(path: Path) -> str:
    """SHA-256 of checkpoint file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_heartbeat(log_dir: Path, step: int, total: int):
    """Write lightweight heartbeat so monitors can detect liveness."""
    heartbeat = {
        "step": step,
        "total_steps": total,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    (log_dir / "heartbeat.json").write_text(json.dumps(heartbeat))


def resilient_dataloader(dataset_dir: Path, batch_size: int, max_retries: int = 3):
    """Build CIFAR-10 DataLoader with auto-recovery on worker crash.

    Power outages or system interrupts can kill DataLoader workers.
    This wrapper catches RuntimeError and retries with a fresh loader."""
    for attempt in range(max_retries):
        try:
            loader = build_dataloader(dataset_dir, batch_size)
            # Test first batch to catch immediate worker failures
            test_iter = iter(loader)
            next(test_iter)
            return loader
        except RuntimeError as e:
            if "DataLoader worker" in str(e) and attempt < max_retries - 1:
                print(f"  [WARN] DataLoader worker crash (attempt {attempt+1}/{max_retries}), retrying...")
                time.sleep(2)
            else:
                raise


def train(args):
    global _train_state
    output_dir, log_dir = setup_dirs()
    stop_step = getattr(args, 'stop_step', TOTAL_STEPS)

    # ── Log file (avoid shell redirect buffering) ──
    log_file = getattr(args, 'log_file', None)
    if log_file:
        import builtins
        log_fh = open(log_file, 'a', buffering=1)  # line-buffered
        original_print = builtins.print

        def tee_print(*a, **kw):
            kw.pop('flush', None)  # we always flush, avoid duplicate kwarg
            original_print(*a, **kw, flush=True)
            original_print(*a, **kw, file=log_fh, flush=True)
        builtins.print = tee_print
        print(f"--- LOG START {datetime.now(timezone.utc).isoformat()} ---")

    # ── Register signal handlers ──
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # --- Seed ---
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    torch.backends.cudnn.benchmark = True

    # --- Model ---
    model = UNet(
        T=T, ch=CH, ch_mult=CH_MULT, attn=ATTN,
        num_res_blocks=NUM_RES_BLOCKS, dropout=DROPOUT,
    ).to(DEVICE)
    ema_model = UNet(
        T=T, ch=CH, ch_mult=CH_MULT, attn=ATTN,
        num_res_blocks=NUM_RES_BLOCKS, dropout=DROPOUT,
    ).to(DEVICE)
    ema_model.load_state_dict(model.state_dict())  # Init EMA

    # --- Optimizer & Scheduler ---
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda=warmup_lr)

    # --- Diffusion ---
    trainer = GaussianDiffusionTrainer(model, beta_1=BETA_1, beta_T=BETA_T, T=T).to(DEVICE)
    sampler = GaussianDiffusionSampler(model, beta_1=BETA_1, beta_T=BETA_T, T=T).to(DEVICE)

    # --- Data ---
    print(f"--- SESSION START {datetime.now(timezone.utc).isoformat()} ---")
    print(f"Dataset root: {DATASET_DIR}")
    dataloader = resilient_dataloader(DATASET_DIR, BATCH_SIZE)
    print(f"Dataset: {len(dataloader.dataset)} samples, {len(dataloader)} batches/epoch")

    # --- Resume ---
    start_step = 0
    if args.resume:
        if args.resume is True:
            result = load_checkpoint()
        else:
            result = load_checkpoint(int(args.resume))
        if result[0] is not None:
            ckpt, start_step = result
            model.load_state_dict(ckpt["net_model"])
            ema_model.load_state_dict(ckpt["ema_model"])
            optimizer.load_state_dict(ckpt["optim"])
            scheduler.load_state_dict(ckpt["sched"])
            print(f"Resumed from step {start_step}")
        else:
            print("No checkpoint found, starting from scratch")

    # --- Logger ---
    writer = SummaryWriter(log_dir=str(log_dir))
    print(f"Device: {DEVICE}")
    print(f"Output: {output_dir}")
    print(f"Stop step: {stop_step}  Seed: {SEED}  Phase G Run-Dynamics Replication")

    # --- Training loop ---
    model.train()
    ema_model.train()
    data_iter = iter(dataloader)
    t_start = time.time()
    global_step = start_step

    while global_step < stop_step:
        try:
            x_0, _ = next(data_iter)
        except StopIteration:
            data_iter = iter(dataloader)
            x_0, _ = next(data_iter)
        except RuntimeError as e:
            if "DataLoader worker" in str(e):
                print(f"  [RECOVER] DataLoader worker crash at step {global_step}, rebuilding...")
                dataloader = resilient_dataloader(DATASET_DIR, BATCH_SIZE)
                data_iter = iter(dataloader)
                x_0, _ = next(data_iter)
            else:
                raise

        x_0 = x_0.to(DEVICE)

        optimizer.zero_grad()
        loss = trainer(x_0)
        loss.backward()

        # Gradient clipping
        grad_norm = compute_gradient_norm(model)
        torch.nn.utils.clip_grad_norm_(model.parameters(), GRAD_CLIP)

        optimizer.step()
        scheduler.step()

        # EMA update
        ema_update(model, ema_model, EMA_DECAY)

        global_step += 1

        # ── Interrupt check ──
        if _interrupted:
            break

        # --- Logging ---
        if global_step % 100 == 0:
            elapsed = time.time() - t_start
            steps_per_sec = global_step / elapsed if elapsed > 0 else 0
            eta_sec = (stop_step - global_step) / steps_per_sec if steps_per_sec > 0 else 0
            writer.add_scalar("train/loss", loss.item(), global_step)
            writer.add_scalar("train/grad_norm", grad_norm, global_step)
            writer.add_scalar("train/lr", scheduler.get_last_lr()[0], global_step)
            print(
                f"[{global_step:06d}/{stop_step}] "
                f"loss={loss.item():.4f} grad={grad_norm:.2f} "
                f"lr={scheduler.get_last_lr()[0]:.2e} "
                f"eta={eta_sec/3600:.1f}h",
                flush=True,
            )
            write_heartbeat(log_dir, global_step, stop_step)

        # --- Checkpoint ---
        if global_step % SAVE_EVERY == 0:
            path = save_checkpoint(model, ema_model, optimizer, scheduler, global_step)
            save_state(global_step, stop_step, {"loss": loss.item(), "grad_norm": grad_norm})
            checksum = compute_checksum(path)
            print(f"  -> Checkpoint saved: {path.name} (SHA256: {checksum[:16]}...)")

        # --- Sample ---
        if global_step % SAMPLE_EVERY == 0:
            sample_and_save(ema_model, sampler, global_step, log_dir, DEVICE)
            print(f"  -> Samples saved at step {global_step}")

    # --- Final / Interrupt ---
    if _interrupted:
        print(f"\n[SIGNAL] Interrupted at step {global_step}. Saving emergency checkpoint...", flush=True)
    path = save_checkpoint(model, ema_model, optimizer, scheduler, global_step)
    save_state(global_step, stop_step,
               {"loss": loss.item(), "grad_norm": grad_norm,
                "status": "interrupted" if _interrupted else "complete"})
    checksum = compute_checksum(path)
    elapsed = time.time() - t_start
    if _interrupted:
        print(f"Emergency checkpoint saved: {path.name} (SHA256: {checksum[:16]}...)")
        print(f"Resume with: --resume {global_step}")
    else:
        print(f"\nTraining complete: {stop_step} steps in {elapsed/3600:.1f}h")
        print(f"Final checkpoint: {path}")
        print(f"SHA256: {checksum}")

    # Write manifest entry
    manifest = {
        "checkpoint": RUN_LABEL,
        "path": str(OUTPUT_DIR),
        "step": global_step,
        "sha256": checksum,
        "config": {
            "T": T, "CH": CH, "CH_MULT": CH_MULT, "ATTN": ATTN,
            "NUM_RES_BLOCKS": NUM_RES_BLOCKS, "DROPOUT": DROPOUT,
            "BETA_1": BETA_1, "BETA_T": BETA_T,
            "LR": LR, "BATCH_SIZE": BATCH_SIZE, "EMA_DECAY": EMA_DECAY,
            "GRAD_CLIP": GRAD_CLIP, "WARMUP_STEPS": WARMUP_STEPS,
            "SEED": SEED,
        },
        "source": f"Phase G run-dynamics replication (seed={SEED}, {global_step} steps)",
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    writer.close()
    return output_dir


def main():
    parser = argparse.ArgumentParser(description="Train DDPM on CIFAR-10 — Phase G run-dynamics replication")
    parser.add_argument("--seed", type=int, default=43,
                        help="Training random seed and output label default (default: 43)")
    parser.add_argument("--run-label", type=str, default=None,
                        help="Checkpoint/log directory label (default: ddpm-cifar10-seed<seed>)")
    parser.add_argument("--resume", nargs="?", const=True, default=False,
                        help="Resume from latest (or specific step)")
    parser.add_argument("--stop-step", type=int, default=TOTAL_STEPS,
                        help=f"Stop after this many steps (default: {TOTAL_STEPS})")
    parser.add_argument("--log-file", type=str, default=None,
                        help="Write log to file (line-buffered, avoids shell redirect issues)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate setup without training")
    args = parser.parse_args()

    global SEED, RUN_LABEL, OUTPUT_DIR, LOG_DIR
    SEED = args.seed
    RUN_LABEL = args.run_label or f"ddpm-cifar10-seed{SEED}"
    OUTPUT_DIR = DOWNLOAD / "checkpoints" / RUN_LABEL
    LOG_DIR = PROJECT / "training" / "outputs" / RUN_LABEL

    if args.dry_run:
        output_dir, log_dir = setup_dirs()
        print(f"Output dir: {output_dir}")
        print(f"Log dir: {log_dir}")
        print(f"Device: {DEVICE}")
        print(f"CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        print("Dry run OK")
        return

    train(args)


if __name__ == "__main__":
    main()
