#!/usr/bin/env python
"""
E3: NVIDIA Standard-UNet CIFAR-10 Calibration
==============================================
Train a DDPM on CIFAR-10 members only, then run SecMI + PIA attacks.
Hard cap: 48 GPU-hours per ccf-a-research-roadmap-2026-06-06.

Usage:
  python scripts/e3_train_and_eval.py --train    # Train only
  python scripts/e3_train_and_eval.py --eval     # Evaluate only
  python scripts/e3_train_and_eval.py --all      # Train + eval
"""
import sys, os, time, json, copy
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.tensorboard import SummaryWriter
from sklearn import metrics

# --- Paths ---
PROJECT = Path(__file__).resolve().parents[1]
# GONE - module removed during restructuring; no replacement found on disk
# MATERIALS = PROJECT / "references" / "materials" / "Rediffuse" / "DDPM"
# sys.path.insert(0, str(MATERIALS))
MATERIALS = PROJECT / "references" / "materials" / "Rediffuse" / "DDPM"  # GONE

from model_unet import UNet
from diffusion import GaussianDiffusionTrainer, GaussianDiffusionSampler
from dataset_utils import load_member_data
import components

# --- Config ---
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEED = 42

T = 1000
CH = 128
CH_MULT = [1, 2, 2, 2]
ATTN = [1]
NUM_RES_BLOCKS = 2
DROPOUT = 0.1

BETA_1 = 0.0001
BETA_T = 0.02
LR = 2e-4
BATCH_SIZE = 64   # fits 8GB VRAM
TOTAL_STEPS = 800000
EMA_DECAY = 0.9999
GRAD_CLIP = 1.0
WARMUP_STEPS = 5000

SAVE_STEPS = [80000, 160000, 240000, 320000, 400000, 480000, 560000, 640000, 720000, 800000]
EVAL_SAMPLE_SIZE = 64
# GONE - output directory not found; re-run training to regenerate
# LOG_DIR = PROJECT / "outputs" / "e3_nvidia_unet_cifar10"
LOG_DIR = PROJECT / "outputs" / "e3-nvidia-unet-cifar10"  # relocated


def setup():
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    torch.backends.cudnn.benchmark = True
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Device: {DEVICE}, Log dir: {LOG_DIR}")


def warmup_lr(step):
    return min(step, WARMUP_STEPS) / WARMUP_STEPS


def ema_update(source, target, decay):
    sd = source.state_dict()
    td = target.state_dict()
    for k in sd:
        td[k].data.copy_(td[k].data * decay + sd[k].data * (1 - decay))


def infin_loop(loader):
    while True:
        for batch in loader:
            yield batch


def build_model():
    return UNet(T=T, ch=CH, ch_mult=CH_MULT, attn=ATTN,
                num_res_blocks=NUM_RES_BLOCKS, dropout=DROPOUT).to(DEVICE)


def train():
    setup()
    print(f"\n{'='*60}")
    print(f"E3 Training: UNet on CIFAR-10 members ({TOTAL_STEPS} steps)")
    print(f"{'='*60}\n")

    member_set, nonmember_set, member_loader, nonmember_loader = load_member_data(
        dataset_name='CIFAR10', batch_size=BATCH_SIZE, shuffle=True, randaugment=False
    )
    datalooper = infin_loop(member_loader)
    print(f"Member: {len(member_set)}, Nonmember: {len(nonmember_set)}")

    net_model = build_model()
    ema_model = copy.deepcopy(net_model).eval()
    net_model.train()

    trainer = GaussianDiffusionTrainer(net_model, BETA_1, BETA_T, T).to(DEVICE)
    optim = torch.optim.Adam(net_model.parameters(), lr=LR)
    sched = torch.optim.lr_scheduler.LambdaLR(optim, lr_lambda=warmup_lr)

    writer = SummaryWriter(str(LOG_DIR / "tensorboard"))
    loss_hist = []
    t0 = time.time()

    for step in range(1, TOTAL_STEPS + 1):
        x_0 = next(datalooper)[0].to(DEVICE)
        optim.zero_grad()
        loss = trainer(x_0).mean()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(net_model.parameters(), GRAD_CLIP)
        optim.step()
        sched.step()
        ema_update(net_model, ema_model, EMA_DECAY)
        loss_hist.append(loss.item())

        if step % 1000 == 0:
            elapsed = time.time() - t0
            avg = np.mean(loss_hist[-100:])
            eta = elapsed / step * (TOTAL_STEPS - step) if step > 0 else 0
            print(f"  step={step:7d} loss={avg:.4f} lr={sched.get_last_lr()[0]:.2e} "
                  f"elapsed={elapsed/3600:.1f}h eta={eta/3600:.1f}h", flush=True)

        if step in SAVE_STEPS:
            ckpt = {'net_model': net_model.state_dict(), 'ema_model': ema_model.state_dict(),
                    'optim': optim.state_dict(), 'sched': sched.state_dict(), 'step': step}
            torch.save(ckpt, LOG_DIR / f"ckpt-step{step}.pt")
            print(f"  Saved ckpt-step{step}.pt", flush=True)

    writer.close()
    print(f"\nTraining done. Time: {(time.time()-t0)/3600:.1f}h")


class EpsGetter(components.EpsGetter):
    def __call__(self, xt, condition=None, noise_level=None, t=None):
        t_t = torch.ones([xt.shape[0]], device=xt.device, dtype=torch.long) * t
        return self.model(xt, t=t_t)


def load_model_for_eval(ckpt_path, use_ema=True):
    model = build_model().eval()
    ckpt = torch.load(ckpt_path, map_location=DEVICE, weights_only=False)
    w = ckpt['ema_model'] if use_ema else ckpt['net_model']
    new = {k[7:] if k.startswith('module.') else k: v for k, v in w.items()}
    model.load_state_dict(new)
    return model.to(DEVICE)


def run_stats_attack(attacker, loader, max_samples=None):
    scores, n = [], 0
    for batch in loader:
        imgs = batch[0].to(DEVICE)
        with torch.no_grad():
            inter, inter_d = attacker(imgs)
            dist = ((inter - inter_d).abs() ** 2).flatten(1).sum(dim=-1)
        scores.append(dist.cpu())
        n += imgs.shape[0]
        if max_samples and n >= max_samples:
            break
    return torch.cat(scores)[:max_samples].flatten()


def run_secmi(model, member_ldr, nonmember_ldr, t_sec=100, k=10):
    print(f"  SecMI t_sec={t_sec} k={k}")
    betas = torch.from_numpy(np.linspace(BETA_1, BETA_T, T)).to(DEVICE)
    attacker = components.SecMIAttacker(betas, interval=1, attack_num=1, k=k,
                                         eps_model=EpsGetter(model), average=1,
                                         denoise_fn=lambda x: x * 2 - 1)
    m_scores = run_stats_attack(attacker, member_ldr)
    nm_scores = run_stats_attack(attacker, nonmember_ldr)
    return compute_metrics(m_scores, nm_scores)


def run_pia(model, member_ldr, nonmember_ldr, interval=200, attack_num=1):
    print(f"  PIA interval={interval} attack_num={attack_num}")
    betas = torch.from_numpy(np.linspace(BETA_1, BETA_T, T)).to(DEVICE)
    attacker = components.PIA(betas, interval=interval, attack_num=attack_num, k=None,
                               eps_model=EpsGetter(model), average=1,
                               denoise_fn=lambda x: x * 2 - 1)
    m_scores = run_stats_attack(attacker, member_ldr)
    nm_scores = run_stats_attack(attacker, nonmember_ldr)
    return compute_metrics(m_scores, nm_scores)


def compute_metrics(m_scores, nm_scores):
    m = m_scores.cpu().numpy()
    nm = nm_scores.cpu().numpy()
    labels = np.concatenate([np.ones_like(m), np.zeros_like(nm)])
    scores = -np.concatenate([m, nm])  # invert: higher = member for sklearn
    auc = metrics.roc_auc_score(labels, scores)
    fpr, tpr, _ = metrics.roc_curve(labels, scores)
    tpr_1 = float(tpr[np.argmin(np.abs(fpr - 0.01))])
    tpr_01 = float(tpr[np.argmin(np.abs(fpr - 0.001))])
    return {"auc": round(auc, 6), "tpr_at_1pct_fpr": round(tpr_1, 6),
            "tpr_at_0_1pct_fpr": round(tpr_01, 6)}


def evaluate_all():
    print(f"\n{'='*60}")
    print(f"E3 Evaluation: SecMI + PIA on all checkpoints")
    print(f"{'='*60}\n")

    _, _, member_ldr, nonmember_ldr = load_member_data(
        dataset_name='CIFAR10', batch_size=64, shuffle=False, randaugment=False)

    results = {}
    for step in SAVE_STEPS:
        ckpt_path = LOG_DIR / f"ckpt-step{step}.pt"
        if not ckpt_path.exists():
            continue
        print(f"\n--- step={step} ---")
        model = load_model_for_eval(ckpt_path)
        sm = run_secmi(model, member_ldr, nonmember_ldr)
        print(f"  SecMI: AUC={sm['auc']:.4f} TPR@1%={sm['tpr_at_1pct_fpr']:.4f} TPR@0.1%={sm['tpr_at_0_1pct_fpr']:.4f}")
        pm = run_pia(model, member_ldr, nonmember_ldr)
        print(f"  PIA:   AUC={pm['auc']:.4f} TPR@1%={pm['tpr_at_1pct_fpr']:.4f} TPR@0.1%={pm['tpr_at_0_1pct_fpr']:.4f}")
        results[step] = {"secmi": sm, "pia": pm}

    json.dump(results, open(LOG_DIR / "e3_results.json", "w"), indent=2)
    print(f"\nResults: {LOG_DIR / 'e3_results.json'}")
    print(f"\n{'='*80}")
    print(f"{'Step':>7} {'SecMI AUC':>10} {'@1%':>8} {'@0.1%':>8} {'PIA AUC':>10} {'@1%':>8} {'@0.1%':>8}")
    for step in SAVE_STEPS:
        if step in results:
            r = results[step]
            print(f"{step:7d} {r['secmi']['auc']:10.4f} {r['secmi']['tpr_at_1pct_fpr']:8.4f} "
                  f"{r['secmi']['tpr_at_0_1pct_fpr']:8.4f} "
                  f"{r['pia']['auc']:10.4f} {r['pia']['tpr_at_1pct_fpr']:8.4f} "
                  f"{r['pia']['tpr_at_0_1pct_fpr']:8.4f}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--train", action="store_true")
    p.add_argument("--eval", action="store_true")
    p.add_argument("--all", action="store_true")
    args = p.parse_args()
    if args.all or args.train:
        train()
    if args.all or args.eval:
        evaluate_all()
    if not (args.train or args.eval or args.all):
        p.print_help()
