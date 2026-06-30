#!/usr/bin/env python
"""
H1 Activation-Subspace Fingerprint Attack — Bounded Scout (v3, CLI-parameterized)
===============================================================================
Extract activation features from UNet intermediate layers and train
logistic regression to detect membership.

Two-stage design:
  Stage 1: Extract raw activations for all samples → save to disk
  Stage 2: Compute features, train LR, evaluate metrics

Usage:
  conda activate retrace-tr
  # Quick run (uses defaults)
  python scripts/h1/h1_activation_scout.py --ckpt <path> --out <dir>
  # Full control
  python scripts/h1/h1_activation_scout.py \
    --ckpt <DOWNLOAD_ROOT>/checkpoints/ddpm-cifar10-seed43/checkpoint-step750000.pt \
    --ckpt-label ddpm-cifar10-seed43-750k \
    --out outputs/h1-scout-seed43-750k \
    --n-member 128 --n-nonmember 128 --force
"""
import sys, os, json, time, pickle, warnings, argparse, hashlib
from pathlib import Path
from collections import defaultdict

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA
from sklearn import metrics as skm

PROJECT = Path(__file__).resolve().parents[2]  # Research/
MATERIALS = PROJECT / "training" / "ddpm-cifar10"
sys.path.insert(0, str(MATERIALS))

from model_unet import UNet
from dataset_utils import load_member_data

warnings.filterwarnings("ignore")
DEVICE = torch.device("cuda")

# ── Architecture constants (never change) ──
T = 1000; CH = 128; CH_MULT = [1, 2, 2, 2]; ATTN = [1]; NUM_RES_BLOCKS = 2
DROPOUT = 0.1; BETA_1 = 0.0001; BETA_T = 0.02

TIMESTEPS = [100, 400, 700]  # early, mid, late denoising
N_SHADOWS = 3
PCA_N = 6
SEED = 42


def get_ckpt_sha(ckpt_path, prefix_len=12):
    """Return first `prefix_len` chars of checkpoint file SHA256."""
    h = hashlib.sha256()
    with open(ckpt_path, "rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:prefix_len]


def parse_args():
    p = argparse.ArgumentParser(description="H1 Activation-Subspace Scout v3")
    p.add_argument("--ckpt", required=True, help="Path to checkpoint .pt file")
    p.add_argument("--ckpt-label", help="Public-safe checkpoint label for result metadata")
    p.add_argument("--out", required=True, help="Output directory (relative to Research/ or absolute)")
    p.add_argument("--n-member", type=int, default=128, help="Number of member samples (default: 128)")
    p.add_argument("--n-nonmember", type=int, default=128, help="Number of nonmember samples (default: 128)")
    p.add_argument("--force", action="store_true", help="Delete existing cache and re-extract activations")
    p.add_argument("--stage2", action="store_true", help="Feature computation + eval only (skip extraction)")
    return p.parse_args()


# ── Model loading ──

def load_model(ckpt_path):
    model = UNet(T=T, ch=CH, ch_mult=CH_MULT, attn=ATTN,
                 num_res_blocks=NUM_RES_BLOCKS, dropout=DROPOUT).eval()
    ckpt = torch.load(ckpt_path, map_location=DEVICE, weights_only=False)
    w = ckpt.get('ema_model', ckpt.get('net_model', ckpt))
    new = {k[7:] if k.startswith('module.') else k: v for k, v in w.items()}
    model.load_state_dict(new)
    model = model.to(DEVICE)
    betas = torch.linspace(BETA_1, BETA_T, T)
    model.alphas_cumprod = torch.cumprod(1 - betas, dim=0).to(DEVICE)
    return model


# ── Hook management ──

class HookManager:
    def __init__(self):
        self.data = {}
        self.handles = []

    def _hook(self, name):
        def fn(module, inp, out):
            self.data[name] = out.detach()
        return fn

    def register(self, model, name, path_parts):
        target = model
        for p in path_parts:
            if p.lstrip('-').isdigit():
                target = target[int(p)]
            else:
                target = getattr(target, p)
        self.handles.append(target.register_forward_hook(self._hook(name)))

    def clear(self):
        self.data.clear()

    def remove(self):
        for h in self.handles:
            h.remove()
        self.handles.clear()


def get_site_paths():
    return {
        "late_down":  ["downblocks", "-1"],
        "mid_0":      ["middleblocks", "0"],
        "mid_1":      ["middleblocks", "1"],
        "early_up":   ["upblocks", "0"],
    }


# ── Stage 1: Raw activation extraction ──

def extract_raw_activations(model, loader, hook_mgr, site_names, timesteps, max_n, label):
    samples = []
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

        batch_acts = [{} for _ in range(B)]
        for t_val in timesteps:
            hook_mgr.clear()
            t_t = torch.full((B,), t_val, device=DEVICE, dtype=torch.long)
            noise = torch.randn_like(imgs)
            ac = model.alphas_cumprod[t_val]
            xt = ac.sqrt() * (imgs * 2 - 1) + (1 - ac).sqrt() * noise
            with torch.no_grad():
                model(xt, t_t)
            for site in site_names:
                act = hook_mgr.data.get(site)
                if act is None:
                    continue
                key = f"{site}_t{t_val}"
                for i in range(B):
                    batch_acts[i][key] = act[i:i+1].cpu()

        samples.extend(batch_acts)
        count += B
        if count % 64 == 0:
            print(f"  [{label}] {count}/{max_n} samples extracted...")
    return samples[:max_n]


# ── Stage 2: Feature computation ──

def compute_features_from_raw(raw_samples):
    features = []
    for s in raw_samples:
        feats = {}
        for key, act in s.items():
            C = act.shape[1]
            flat = act.view(C, -1)
            mu_abs = flat.abs().mean(dim=-1)
            var = flat.var(dim=-1, unbiased=False)
            threshold = 0.01 * flat.std(dim=-1, unbiased=False)
            sparsity = (flat.abs() < threshold.unsqueeze(-1)).float().mean(dim=-1)
            feats[f"{key}_mu_abs"] = mu_abs.numpy()
            feats[f"{key}_var"] = var.numpy()
            feats[f"{key}_sparsity"] = sparsity.numpy()
            feats[f"{key}_mu_abs_mean"] = float(mu_abs.mean())
            feats[f"{key}_var_mean"] = float(var.mean())
            feats[f"{key}_sparsity_mean"] = float(sparsity.mean())
        features.append(feats)
    return features


def build_pca_features(feat_list, site_names, timesteps, stat_types):
    components = []
    for s in site_names:
        for t in timesteps:
            for st in stat_types:
                key = f"{s}_t{t}_{st}"
                if key in feat_list[0]:
                    components.append(np.stack([f[key] for f in feat_list], axis=0))
    if not components:
        return None
    return np.concatenate(components, axis=1)


def build_feature_matrix(feat_list, pca_model=None, site_names=None, timesteps=None, stat_types=None):
    scalar_keys = [k for k in feat_list[0] if isinstance(feat_list[0][k], (float, int, np.floating))]
    X_scalar = np.array([[f.get(k, 0.0) for k in scalar_keys] for f in feat_list])
    if pca_model is not None and site_names is not None:
        pc_arr = build_pca_features(feat_list, site_names, timesteps, stat_types)
        if pc_arr is not None:
            X_pca = pca_model.transform(pc_arr)
            return np.concatenate([X_scalar, X_pca], axis=1)
    return X_scalar


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


# ── Main ──

def main():
    args = parse_args()
    ckpt_path = args.ckpt
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = PROJECT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    # Cache file bound to checkpoint hash + sample size
    ckpt_sha = get_ckpt_sha(ckpt_path)
    cache_path = out_dir / f"h1_raw_activations_{ckpt_sha}_n{args.n_member}.pkl"

    if args.force and cache_path.exists():
        cache_path.unlink()
        print(f"  --force: deleted cache {cache_path.name}")

    t0 = time.time()
    print("=" * 60)
    print("H1 Activation-Subspace Fingerprint — Bounded Scout v3")
    print(f"  Checkpoint: {ckpt_path}")
    print(f"  Output:     {out_dir}")
    print(f"  Sites: late_down, mid_0, mid_1, early_up")
    print(f"  Timesteps: {TIMESTEPS}")
    print(f"  Shadows: {N_SHADOWS}  Target: {args.n_member}m/{args.n_nonmember}nm  PCA: {PCA_N}d")
    print("=" * 60)

    site_paths = get_site_paths()
    site_names = list(site_paths.keys())
    stat_types = ["mu_abs", "var", "sparsity"]
    print(f"  Hook points: {site_names}")

    # ── Load model and set up hooks ──
    print("\n[1/5] Loading model & setting up hooks...")
    model = load_model(ckpt_path)
    hook = HookManager()
    for name, path in site_paths.items():
        hook.register(model, name, path)
    print("  Model loaded. Hooks registered.")

    # ── Load data ──
    print("\n[2/5] Loading CIFAR-10 member/nonmember split...")
    _, _, member_loader, nonmember_loader = load_member_data(
        dataset_name='CIFAR10', batch_size=64, shuffle=False, randaugment=False)

    # ── Stage 1: Extract raw activations ──
    if args.stage2 and cache_path.exists():
        print(f"\n[3/5] --stage2: Loading cached activations from {cache_path}...")
        with open(cache_path, "rb") as f:
            cache = pickle.load(f)
        member_raw = cache["member_raw"]
        nonmember_raw = cache["nonmember_raw"]
    elif cache_path.exists() and not args.force:
        print(f"\n[3/5] Loading cached raw activations from {cache_path}...")
        with open(cache_path, "rb") as f:
            cache = pickle.load(f)
        member_raw = cache["member_raw"]
        nonmember_raw = cache["nonmember_raw"]
    else:
        print(f"\n[3/5] Extracting raw activations (member {args.n_member} + nonmember {args.n_nonmember})...")
        member_raw = extract_raw_activations(model, member_loader, hook, site_names, TIMESTEPS, args.n_member, "member")
        nonmember_raw = extract_raw_activations(model, nonmember_loader, hook, site_names, TIMESTEPS, args.n_nonmember, "nonmember")
        print(f"  Collected: {len(member_raw)} member + {len(nonmember_raw)} nonmember")
        with open(cache_path, "wb") as f:
            pickle.dump({"member_raw": member_raw, "nonmember_raw": nonmember_raw}, f)
        print(f"  Cached to {cache_path}")

    hook.remove()

    # ── Stage 2: Compute features ──
    print("\n[4/5] Computing features from raw activations...")
    member_feats = compute_features_from_raw(member_raw)
    nonmember_feats = compute_features_from_raw(nonmember_raw)

    n_scalar = sum(1 for k in member_feats[0] if isinstance(member_feats[0][k], (float, int, np.floating)))
    n_pc_total = sum(member_feats[0][f"{s}_t{t}_mu_abs"].shape[0] for s in site_names for t in TIMESTEPS)
    print(f"  Scalar features: {n_scalar}  Per-channel dims: {n_pc_total}")

    # ── Shadow calibration + Target evaluation ──
    ckpt_name = args.ckpt_label or Path(ckpt_path).parent.name
    results = {"experiment": "H1_activation_subspace_scout_v3",
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "config": {"checkpoint": ckpt_name, "ckpt_file": Path(ckpt_path).name,
                          "ckpt_sha": ckpt_sha, "sites": site_names,
                          "timesteps": TIMESTEPS, "n_shadows": N_SHADOWS,
                          "shadow_n": args.n_member, "target_n": args.n_member, "pca_n": PCA_N},
               "shadow_metrics": [], "target_metrics": {}, "controls": {}}

    all_target_m_scores = []
    all_target_nm_scores = []

    for shadow_idx in range(N_SHADOWS):
        rng = np.random.RandomState(SEED + shadow_idx)
        shadow_all = member_feats + nonmember_feats
        y_shadow = np.concatenate([np.ones(len(member_feats)), np.zeros(len(nonmember_feats))])

        pca = PCA(n_components=min(PCA_N, len(shadow_all) - 1), random_state=SEED + shadow_idx)
        pc_arr = build_pca_features(shadow_all, site_names, TIMESTEPS, stat_types)
        if pc_arr is not None and pc_arr.shape[0] > PCA_N:
            pca.fit(pc_arr)
        else:
            pca = None

        X_shadow = build_feature_matrix(shadow_all, pca, site_names, TIMESTEPS, stat_types)
        print(f"  Shadow {shadow_idx+1}: X={X_shadow.shape}, y={y_shadow.shape}")

        lr = LogisticRegression(max_iter=5000, random_state=SEED + shadow_idx,
                                class_weight='balanced', solver='lbfgs')
        lr.fit(X_shadow, y_shadow)
        train_score = lr.score(X_shadow, y_shadow)

        X_tm = build_feature_matrix(member_feats, pca, site_names, TIMESTEPS, stat_types)
        X_tnm = build_feature_matrix(nonmember_feats, pca, site_names, TIMESTEPS, stat_types)

        m_scores = lr.predict_proba(X_tm)[:, 1]
        nm_scores = lr.predict_proba(X_tnm)[:, 1]

        shadow_metrics = compute_metrics(m_scores, nm_scores)
        shadow_metrics["train_acc"] = round(train_score, 4)
        shadow_metrics["n_shadow_m"] = len(member_feats)
        shadow_metrics["n_shadow_nm"] = len(nonmember_feats)
        shadow_metrics["n_target_m"] = len(member_feats)
        shadow_metrics["n_target_nm"] = len(nonmember_feats)
        shadow_metrics["n_features"] = X_shadow.shape[1]
        results["shadow_metrics"].append(shadow_metrics)

        all_target_m_scores.append(m_scores)
        all_target_nm_scores.append(nm_scores)

        print(f"    AUC={shadow_metrics['auc']:.4f}  TPR@1%={shadow_metrics['tpr_1pct']:.4f}  "
              f"TPR@0.1%={shadow_metrics['tpr_01pct']:.4f}  dims={X_shadow.shape[1]}")

    agg_m = np.mean(all_target_m_scores, axis=0)
    agg_nm = np.mean(all_target_nm_scores, axis=0)
    results["target_metrics"] = compute_metrics(agg_m, agg_nm)

    # ── Controls ──
    all_scores = np.concatenate([agg_m, agg_nm])
    all_labels = np.concatenate([np.ones_like(agg_m), np.zeros_like(agg_nm)])
    rng = np.random.RandomState(SEED)
    shuf_labels = rng.permutation(all_labels)
    try:
        shuf_auc = skm.roc_auc_score(shuf_labels, -all_scores)
    except Exception:
        shuf_auc = 0.5
    results["controls"]["label_shuffle_auc"] = round(float(shuf_auc), 6)

    lr0 = LogisticRegression(max_iter=5000, random_state=SEED, class_weight='balanced', solver='lbfgs')
    ablation = {}
    for drop_site in site_names:
        reduced_sites = [s for s in site_names if s != drop_site]
        if len(reduced_sites) < 1:
            continue
        pc_arr_abl = build_pca_features(member_feats + nonmember_feats, reduced_sites, TIMESTEPS, stat_types)
        pca_abl = PCA(n_components=min(PCA_N, len(member_feats) + len(nonmember_feats) - 1), random_state=SEED)
        if pc_arr_abl is not None and pc_arr_abl.shape[0] > PCA_N:
            pca_abl.fit(pc_arr_abl)
        else:
            pca_abl = None
        X_abl = build_feature_matrix(member_feats + nonmember_feats, pca_abl, reduced_sites, TIMESTEPS, stat_types)
        y_abl = np.concatenate([np.ones(len(member_feats)), np.zeros(len(nonmember_feats))])
        lr0.fit(X_abl, y_abl)
        s_m = lr0.predict_proba(X_abl[:len(member_feats)])[:, 1]
        s_nm = lr0.predict_proba(X_abl[len(member_feats):])[:, 1]
        abl_m = compute_metrics(s_m, s_nm)
        ablation[f"drop_{drop_site}"] = abl_m["auc"]
        print(f"  Ablation drop {drop_site}: AUC={abl_m['auc']:.4f}")
    results["controls"]["ablation"] = ablation

    # ── Promotion gate ──
    best_auc = max(s["auc"] for s in results["shadow_metrics"])
    gate = {
        "beats_random": best_auc > 0.55,
        "shuffle_pass": results["controls"]["label_shuffle_auc"] < 0.55,
        "not_single_site": any(v < best_auc - 0.03 for v in ablation.values()),
        "tpr_1pct_positive": results["target_metrics"]["tpr_1pct"] > 0.02,
        "promotion_recommendation": "TBD",
    }
    if gate["beats_random"] and gate["shuffle_pass"] and gate["tpr_1pct_positive"]:
        gate["promotion_recommendation"] = "scale_to_128"
    elif best_auc < 0.55:
        gate["promotion_recommendation"] = "kill"
    else:
        gate["promotion_recommendation"] = "weak_candidate_review"
    results["promotion_gate"] = gate

    # ── Write results ──
    out_path = out_dir / "h1_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n[5/5] Results -> {out_path}")
    print(f"  Aggregate AUC: {results['target_metrics']['auc']}")
    print(f"  TPR@1%FPR:     {results['target_metrics']['tpr_1pct']}")
    print(f"  TPR@0.1%FPR:   {results['target_metrics']['tpr_01pct']}")
    print(f"  Shuffle AUC:   {results['controls']['label_shuffle_auc']}")
    print(f"  Gate:          {gate['promotion_recommendation']}")
    print(f"  Time:          {(time.time() - t0):.0f}s")


if __name__ == "__main__":
    main()
