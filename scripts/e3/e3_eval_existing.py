#!/usr/bin/env python
"""
E3 Fast Path: Use existing secmi-cifar checkpoint, run SecMI + PIA attacks.
Purpose: Compare NVIDIA Standard-UNet scores against DCU weak signal (AUC≈0.518).

Usage:
  python scripts/e3_eval_existing.py
"""
import sys, os, time, json, copy
from pathlib import Path

import numpy as np
import torch

PROJECT = Path(__file__).resolve().parents[2]  # Research/
MATERIALS = PROJECT / "training" / "ddpm-cifar10"
sys.path.insert(0, str(MATERIALS))

from model_unet import UNet
from diffusion import GaussianDiffusionTrainer
from dataset_utils import load_member_data
import components

DEVICE = torch.device("cuda")

T = 1000; CH = 128; CH_MULT = [1,2,2,2]; ATTN = [1]; NUM_RES_BLOCKS = 2; DROPOUT = 0.1
BETA_1 = 0.0001; BETA_T = 0.02
LOG_DIR = PROJECT / "outputs" / "e3-existing-eval"

# Checkpoints to evaluate
CKPT_PATHS = [
    ("secmi-bundle-800k", "D:/Code/DiffAudit/Download/checkpoints/ddpm-cifar10-800k/checkpoint.pt"),
    ("ddim-750k", "D:/Code/DiffAudit/Download/checkpoints/ddim-cifar10-750k/DDIM-ckpt-step750000.pt"),
    ("pia-upstream", "D:/Code/DiffAudit/Download/checkpoints/pia-ddpm-cifar10/checkpoint.pt"),
]

SECMI_CONFIGS = [
    {"t_sec": 100, "k": 10, "label": "t100_k10"},
    {"t_sec": 50,  "k": 5,  "label": "t50_k5"},
    {"t_sec": 200, "k": 20, "label": "t200_k20"},
]
PIA_CONFIGS = [
    {"interval": 200, "attack_num": 1, "label": "int200_num1"},
    {"interval": 100, "attack_num": 2, "label": "int100_num2"},
]


class EpsGetter(components.EpsGetter):
    def __call__(self, xt, condition=None, noise_level=None, t=None):
        t_t = torch.ones([xt.shape[0]], device=xt.device, dtype=torch.long) * t
        return self.model(xt, t=t_t)


def load_model(ckpt_path):
    model = UNet(T=T, ch=CH, ch_mult=CH_MULT, attn=ATTN,
                 num_res_blocks=NUM_RES_BLOCKS, dropout=DROPOUT).eval()
    ckpt = torch.load(ckpt_path, map_location=DEVICE, weights_only=False)
    w = ckpt.get('ema_model', ckpt.get('net_model', ckpt))
    new = {k[7:] if k.startswith('module.') else k: v for k, v in w.items()}
    model.load_state_dict(new)
    return model.to(DEVICE)


def run_stats_attack(attacker, loader, max_samples=5000):
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


def compute_metrics(m_scores, nm_scores):
    m = m_scores.cpu().numpy()
    nm = nm_scores.cpu().numpy()
    labels = np.concatenate([np.ones_like(m), np.zeros_like(nm)])
    scores = -np.concatenate([m, nm])
    from sklearn import metrics
    auc = metrics.roc_auc_score(labels, scores)
    fpr, tpr, _ = metrics.roc_curve(labels, scores)
    tpr_1 = float(tpr[np.argmin(np.abs(fpr - 0.01))])
    tpr_01 = float(tpr[np.argmin(np.abs(fpr - 0.001))])
    return {"auc": round(auc, 6), "tpr_at_1pct_fpr": round(tpr_1, 6),
            "tpr_at_0_1pct_fpr": round(tpr_01, 6)}


def main():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    print("Loading CIFAR-10 member/nonmember split...")
    _, _, member_ldr, nonmember_ldr = load_member_data(
        dataset_name='CIFAR10', batch_size=64, shuffle=False, randaugment=False)

    all_results = {}
    for ckpt_name, ckpt_path in CKPT_PATHS:
        if not Path(ckpt_path).exists():
            print(f"\nSKIP {ckpt_name}: checkpoint not found at {ckpt_path}")
            continue

        print(f"\n{'='*60}")
        print(f"Evaluating: {ckpt_name}")
        print(f"Checkpoint: {ckpt_path}")
        print(f"{'='*60}")

        try:
            model = load_model(ckpt_path)
            eps_getter = EpsGetter(model)
        except Exception as e:
            print(f"  FAILED to load: {e}")
            continue

        ckpt_results = {}
        betas = torch.from_numpy(np.linspace(BETA_1, BETA_T, T)).to(DEVICE)

        # --- SecMI ---
        for cfg in SECMI_CONFIGS:
            label = f"secmi_{cfg['label']}"
            print(f"  {label}...")
            attacker = components.SecMIAttacker(
                betas, interval=1, attack_num=1, k=cfg['k'],
                eps_getter=eps_getter, average=1,
                normalize=None, denormalize=None)
            m_scores = run_stats_attack(attacker, member_ldr)
            nm_scores = run_stats_attack(attacker, nonmember_ldr)
            mets = compute_metrics(m_scores, nm_scores)
            ckpt_results[label] = mets
            print(f"    AUC={mets['auc']:.4f} TPR@1%={mets['tpr_at_1pct_fpr']:.4f} "
                  f"TPR@0.1%={mets['tpr_at_0_1pct_fpr']:.4f}")

        # --- PIA ---
        for cfg in PIA_CONFIGS:
            label = f"pia_{cfg['label']}"
            print(f"  {label}...")
            attacker = components.PIA(
                betas, interval=cfg['interval'], attack_num=cfg['attack_num'],
                eps_getter=eps_getter,
                normalize=None, denormalize=None, lp=2)
            m_scores = run_stats_attack(attacker, member_ldr)
            nm_scores = run_stats_attack(attacker, nonmember_ldr)
            mets = compute_metrics(m_scores, nm_scores)
            ckpt_results[label] = mets
            print(f"    AUC={mets['auc']:.4f} TPR@1%={mets['tpr_at_1pct_fpr']:.4f} "
                  f"TPR@0.1%={mets['tpr_at_0_1pct_fpr']:.4f}")

        all_results[ckpt_name] = ckpt_results

    # --- Summary ---
    out_path = LOG_DIR / "e3_eval_results.json"
    json.dump(all_results, open(out_path, "w"), indent=2)
    print(f"\nResults: {out_path}")

    print(f"\n{'='*80}")
    print(f"E3 COMPARISON: NVIDIA Standard-UNet vs DCU weak signal baseline")
    print(f"DCU Reference: TC192 AUC≈0.518 (weak evidence)")
    print(f"{'='*80}")
    for ckpt_name, res in all_results.items():
        print(f"\n{ckpt_name}:")
        for attack_name, mets in res.items():
            flag = "*** SIGNAL FOUND ***" if mets['auc'] > 0.6 else "weak"
            print(f"  {attack_name:20s} AUC={mets['auc']:.4f} TPR@1%={mets['tpr_at_1pct_fpr']:.4f} "
                  f"TPR@0.1%={mets['tpr_at_0_1pct_fpr']:.4f}  [{flag}]")


if __name__ == "__main__":
    main()
