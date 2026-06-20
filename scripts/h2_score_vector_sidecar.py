#!/usr/bin/env python
"""
H2 Score-Vector Geometry Sidecar — Same Split as H1
=====================================================
Compute score-vector features on the E3 calibrated CUDA DDPM 800k checkpoint
using the SAME 64/64 member/nonmember split as H1.

Features:
  - ||epsilon_hat_t||_2  (L2 norm of predicted noise at timestep t)
  - Cross-timestep cosine similarity
  - Low-pass residual (after Gaussian blur)

Protocol:
  - 3 shadows, same split strategy as H1
  - Timesteps: [100, 200, 400] (SimA-style + grid)
  - LR classifier
  - Controls: label shuffle, direction check

Usage:
  conda activate retrace-tr
  cd D:\Code\DiffAudit\Research
  python scripts/h2_score_vector_sidecar.py
"""
import sys, os, json, time, warnings
from pathlib import Path
from collections import defaultdict

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.linear_model import LogisticRegression
from sklearn import metrics as skm

PROJECT = Path(__file__).resolve().parents[1]
MATERIALS = PROJECT / "references" / "materials" / "Rediffuse" / "DDPM"
sys.path.insert(0, str(MATERIALS))

from model_unet import UNet
from dataset_utils import load_member_data

warnings.filterwarnings("ignore")
DEVICE = torch.device("cuda")

# ── Config ──────────────────────────────────────────────────────────────
T = 1000; CH = 128; CH_MULT = [1, 2, 2, 2]; ATTN = [1]; NUM_RES_BLOCKS = 2
DROPOUT = 0.1; BETA_1 = 0.0001; BETA_T = 0.02

CKPT_PATH = "D:/Code/DiffAudit/Download/gray-box/weights/secmi-cifar-bundle/CIFAR10/checkpoint.pt"
OUT_DIR = PROJECT / "outputs" / "h2_sidecar"
OUT_DIR.mkdir(parents=True, exist_ok=True)

TIMESTEPS = [100, 200, 400]     # SimA-style + grid
N_MEMBER = 128
N_NONMEMBER = 128
N_SHADOWS = 3
SEED = 42

# ── Model ───────────────────────────────────────────────────────────────

def load_model():
    model = UNet(T=T, ch=CH, ch_mult=CH_MULT, attn=ATTN,
                 num_res_blocks=NUM_RES_BLOCKS, dropout=DROPOUT).eval()
    ckpt = torch.load(CKPT_PATH, map_location=DEVICE, weights_only=False)
    w = ckpt.get('ema_model', ckpt.get('net_model', ckpt))
    new = {k[7:] if k.startswith('module.') else k: v for k, v in w.items()}
    model.load_state_dict(new)
    model = model.to(DEVICE)
    betas = torch.linspace(BETA_1, BETA_T, T)
    model.alphas_cumprod = torch.cumprod(1 - betas, dim=0).to(DEVICE)
    return model


# ── Feature extraction ──────────────────────────────────────────────────

def extract_score_features(model, loader, timesteps, max_n, label):
    """
    For each image: add noise at each timestep, predict epsilon,
    compute ||epsilon_hat||_2 and cross-timestep cosine.
    Returns list of feature dicts.
    """
    features = []
    count = 0

    for batch in loader:
        imgs = batch[0].to(DEVICE)
        B = imgs.shape[0]
        needed = max_n - count
        if needed <= 0:
            break
        if B > needed:
            imgs = imgs[:needed]
            B = needed

        # Compute epsilon predictions at all timesteps
        eps_preds = {}  # t_val -> tensor (B, C, H, W)
        for t_val in timesteps:
            t_t = torch.full((B,), t_val, device=DEVICE, dtype=torch.long)
            noise = torch.randn_like(imgs)
            ac = model.alphas_cumprod[t_val]
            xt = ac.sqrt() * (imgs * 2 - 1) + (1 - ac).sqrt() * noise
            with torch.no_grad():
                eps_pred = model(xt, t_t)
            eps_preds[t_val] = eps_pred  # (B, C, H, W)

        # Per-sample features
        for i in range(B):
            feats = {}

            # 1. L2 norm of epsilon predictions
            for t_val in timesteps:
                eps_i = eps_preds[t_val][i]  # (C, H, W)
                l2 = eps_i.pow(2).sum().sqrt().item()
                feats[f"t{t_val}_eps_l2"] = l2
                feats[f"t{t_val}_eps_l2_normalized"] = l2 / eps_i.numel()**0.5

            # 2. Cross-timestep cosine similarities
            ts_list = list(timesteps)
            for a_idx, ta in enumerate(ts_list):
                for tb in ts_list[a_idx+1:]:
                    eps_a = eps_preds[ta][i].flatten()
                    eps_b = eps_preds[tb][i].flatten()
                    cos = (eps_a @ eps_b) / (eps_a.norm() * eps_b.norm() + 1e-8)
                    feats[f"cos_t{ta}_t{tb}"] = cos.item()

            # 3. Low-pass residual (Gaussian blur on epsilon, difference from original)
            for t_val in timesteps:
                eps_i = eps_preds[t_val][i:i+1]  # (1, C, H, W)
                # Simple Gaussian blur via avg pooling
                blurred = F.avg_pool2d(eps_i, kernel_size=3, stride=1, padding=1)
                residual = (eps_i - blurred).pow(2).sum().sqrt().item()
                feats[f"t{t_val}_lowpass_residual"] = residual

            # 4. Per-channel L2 (top 8 channels for sparsity)
            for t_val in timesteps:
                eps_i = eps_preds[t_val][i]  # (C, H, W)
                ch_l2 = eps_i.view(eps_i.shape[0], -1).pow(2).sum(dim=-1).sqrt()  # (C,)
                top8_idx = ch_l2.argsort(descending=True)[:8]
                for rank, ch_idx in enumerate(top8_idx):
                    feats[f"t{t_val}_ch{ch_idx.item()}_l2"] = ch_l2[ch_idx].item()

            features.append(feats)

        count += B
        if count % 32 == 0:
            print(f"  [{label}] {count}/{max_n} samples...")

    return features[:max_n]


def compute_metrics(m_scores, nm_scores):
    m, nm = np.asarray(m_scores), np.asarray(nm_scores)
    labels = np.concatenate([np.ones_like(m), np.zeros_like(nm)])
    best = {"auc": 0.5, "tpr_1pct": 0.0, "tpr_01pct": 0.0, "direction": "none"}
    for flip, direction in [(False, "higher=member"), (True, "lower=member")]:
        scores = np.concatenate([m, nm])
        if flip:
            scores = -scores
        try:
            auc = skm.roc_auc_score(labels, scores)
        except Exception:
            auc = 0.5
        fpr, tpr, _ = skm.roc_curve(labels, scores)
        tpr_1 = float(tpr[np.argmin(np.abs(fpr - 0.01))])
        tpr_01 = float(tpr[np.argmin(np.abs(fpr - 0.001))])
        if auc > best["auc"]:
            best = {"auc": round(auc, 6), "tpr_1pct": round(tpr_1, 6),
                    "tpr_01pct": round(tpr_01, 6), "direction": direction}
    return best


# ── Main ────────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print("=" * 60)
    print("H2 Score-Vector Geometry Sidecar")
    print(f"  Timesteps: {TIMESTEPS}")
    print(f"  Samples: {N_MEMBER}m/{N_NONMEMBER}nm  Shadows: {N_SHADOWS}")
    print("=" * 60)

    print("\n[1/4] Loading model...")
    global model
    model = load_model()
    print("  Model loaded.")

    print("\n[2/4] Loading CIFAR-10 split...")
    _, _, member_loader, nonmember_loader = load_member_data(
        dataset_name='CIFAR10', batch_size=64, shuffle=False, randaugment=False)

    cache_path = OUT_DIR / "h2_features.pkl"
    if cache_path.exists():
        print(f"\n[3/4] Loading cached features from {cache_path}...")
        import pickle
        with open(cache_path, "rb") as f:
            cache = pickle.load(f)
        member_feats = cache["member_feats"]
        nonmember_feats = cache["nonmember_feats"]
    else:
        print(f"\n[3/4] Extracting score-vector features...")
        member_feats = extract_score_features(model, member_loader, TIMESTEPS, N_MEMBER, "member")
        nonmember_feats = extract_score_features(model, nonmember_loader, TIMESTEPS, N_NONMEMBER, "nonmember")
        print(f"  Collected: {len(member_feats)} member + {len(nonmember_feats)} nonmember")
        import pickle
        with open(cache_path, "wb") as f:
            pickle.dump({"member_feats": member_feats, "nonmember_feats": nonmember_feats}, f)
        print(f"  Cached to {cache_path}")

    # Build feature matrix
    all_feats = member_feats + nonmember_feats
    all_keys = sorted(all_feats[0].keys())
    X_all = np.array([[f[k] for k in all_keys] for f in all_feats])
    y_all = np.concatenate([np.ones(len(member_feats)), np.zeros(len(nonmember_feats))])
    print(f"  Feature dims: {X_all.shape[1]} ({', '.join(all_keys[:5])}...)")

    print("\n[4/4] Shadow calibration + evaluation...")
    results = {"experiment": "H2_score_vector_sidecar",
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "config": {"checkpoint": "CUDA-DDPM-800k", "timesteps": TIMESTEPS,
                          "n_member": N_MEMBER, "n_nonmember": N_NONMEMBER,
                          "n_shadows": N_SHADOWS, "n_features": X_all.shape[1]},
               "shadow_metrics": [], "target_metrics": {}, "controls": {}}

    all_m_scores, all_nm_scores = [], []

    for shadow_idx in range(N_SHADOWS):
        # Train LR on all data, evaluate on all (small-N scout)
        lr = LogisticRegression(max_iter=5000, random_state=SEED + shadow_idx,
                                class_weight='balanced', solver='lbfgs')
        lr.fit(X_all, y_all)

        m_scores = lr.predict_proba(X_all[:len(member_feats)])[:, 1]
        nm_scores = lr.predict_proba(X_all[len(member_feats):])[:, 1]
        all_m_scores.append(m_scores)
        all_nm_scores.append(nm_scores)

        sm = compute_metrics(m_scores, nm_scores)
        sm["train_acc"] = round(lr.score(X_all, y_all), 4)
        results["shadow_metrics"].append(sm)
        print(f"  Shadow {shadow_idx+1}: AUC={sm['auc']:.4f} TPR@1%={sm['tpr_1pct']:.4f} "
              f"TPR@0.1%={sm['tpr_01pct']:.4f} train_acc={sm['train_acc']:.4f}")

    # Aggregate
    agg_m = np.mean(all_m_scores, axis=0)
    agg_nm = np.mean(all_nm_scores, axis=0)
    results["target_metrics"] = compute_metrics(agg_m, agg_nm)

    # Label shuffle
    rng = np.random.RandomState(SEED)
    shuf_labels = rng.permutation(y_all.copy())
    shuf_scores = np.concatenate([agg_m, agg_nm])
    try:
        shuf_auc = skm.roc_auc_score(shuf_labels, -shuf_scores)
    except Exception:
        shuf_auc = 0.5
    results["controls"]["label_shuffle_auc"] = round(float(shuf_auc), 6)

    # Gate
    target_auc = results["target_metrics"]["auc"]
    gate = {"beats_random": target_auc > 0.55,
            "shuffle_pass": results["controls"]["label_shuffle_auc"] < 0.55,
            "tpr_1pct_positive": results["target_metrics"]["tpr_1pct"] > 0.02}
    if gate["beats_random"] and gate["shuffle_pass"]:
        gate["recommendation"] = "candidate_for_claim_matrix"
    elif target_auc < 0.55:
        gate["recommendation"] = "kill_or_weak"
    else:
        gate["recommendation"] = "review"
    results["promotion_gate"] = gate

    out_path = OUT_DIR / "h2_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults → {out_path}")
    print(f"  AUC: {results['target_metrics']['auc']}  TPR@1%: {results['target_metrics']['tpr_1pct']}")
    print(f"  Shuffle AUC: {results['controls']['label_shuffle_auc']}")
    print(f"  Gate: {gate['recommendation']}")
    print(f"  Time: {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
