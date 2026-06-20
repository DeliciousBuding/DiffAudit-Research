#!/usr/bin/env python
"""
H1 DDIM 750k — N=128 Full Activation Scout
==========================================
Scale-up replication of the main H1 scout on DDIM 750k checkpoint.
Extracts 4-site × 3-timestep activations, computes full feature decomposition
(mu_abs, var, sparsity), trains LR with PCA=6, reports AUC + TPR.

Completes the last DDIM evidence gap: channel-level DAAB at scale.

Usage:
  conda activate retrace-tr
  python scripts/h1_scout_ddim_n128.py
"""
import sys, os, json, time, pickle, warnings
from pathlib import Path

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA
from sklearn import metrics as skm

PROJECT = Path(__file__).resolve().parents[1]
MATERIALS = PROJECT / "references" / "materials" / "Rediffuse" / "DDPM"
sys.path.insert(0, str(MATERIALS))

from model_unet import UNet
from dataset_utils import load_member_data

warnings.filterwarnings("ignore")
DEVICE = torch.device("cuda")

T = 1000; CH = 128; CH_MULT = [1, 2, 2, 2]; ATTN = [1]; NUM_RES_BLOCKS = 2
DROPOUT = 0.1; BETA_1 = 0.0001; BETA_T = 0.02

CKPT_PATH = "D:/Code/DiffAudit/Download/checkpoints/ddim-cifar10-750k/DDIM-ckpt-step750000.pt"
OUT_DIR = PROJECT / "outputs" / "h1-scout"

TIMESTEPS = [100, 400, 700]
SITES = ["late_down", "mid_0", "mid_1", "early_up"]
N_MEMBER = 128
N_NONMEMBER = 128
N_SHADOWS = 3
PCA_N = 6
SEED = 42

SITE_PATHS = {
    "late_down": ["downblocks", "-1"], "mid_0": ["middleblocks", "0"],
    "mid_1": ["middleblocks", "1"], "early_up": ["upblocks", "0"],
}

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

def extract_raw(model, loader, hook, site_names, timesteps, max_n, label):
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
            hook.clear()
            t_t = torch.full((B,), t_val, device=DEVICE, dtype=torch.long)
            noise = torch.randn_like(imgs)
            ac = model.alphas_cumprod[t_val]
            xt = ac.sqrt() * (imgs * 2 - 1) + (1 - ac).sqrt() * noise
            with torch.no_grad():
                model(xt, t_t)
            for site in site_names:
                act = hook.data.get(site)
                if act is None:
                    continue
                key = f"{site}_t{t_val}"
                for i in range(B):
                    batch_acts[i][key] = act[i:i+1].cpu()
        samples.extend(batch_acts)
        count += B
        if count % 16 == 0:
            print(f"  [{label}] {count}/{max_n}...")
    return samples[:max_n]

def compute_features(raw_samples):
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

def build_pca_matrix(feat_list, sites, timesteps, stat_types):
    components = []
    for s in sites:
        for t in timesteps:
            for st in stat_types:
                key = f"{s}_t{t}_{st}"
                if key in feat_list[0]:
                    components.append(np.stack([f[key] for f in feat_list], axis=0))
    return np.concatenate(components, axis=1) if components else None

def build_feature_matrix(feat_list, pca_model, sites, timesteps, stat_types):
    scalar_keys = [k for k in feat_list[0] if isinstance(feat_list[0][k], (float, int, np.floating))]
    X_scalar = np.array([[f.get(k, 0.0) for k in scalar_keys] for f in feat_list])
    if pca_model is not None:
        pc_arr = build_pca_matrix(feat_list, sites, timesteps, stat_types)
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

def main():
    t0 = time.time()
    print("=" * 60)
    print("H1 DDIM 750k N=128 Activation Scout")
    print(f"  Sites: {SITES}  Timesteps: {TIMESTEPS}  N: {N_MEMBER}/{N_NONMEMBER}")
    print("=" * 60)

    print("\n[1/4] Loading DDIM 750k model...")
    model = load_model()
    hook = HookManager()
    for name in SITES:
        hook.register(model, name, SITE_PATHS[name])

    print("\n[2/4] Loading CIFAR-10 split...")
    _, _, member_loader, nonmember_loader = load_member_data(
        dataset_name='CIFAR10', batch_size=64, shuffle=False, randaugment=False)

    cache_path = OUT_DIR / "h1_ddim_n128_activations.pkl"
    if cache_path.exists():
        print(f"\n[3/4] Loading cached activations...")
        with open(cache_path, "rb") as f:
            cache = pickle.load(f)
        member_raw = cache["member_raw"]
        nonmember_raw = cache["nonmember_raw"]
    else:
        print(f"\n[3/4] Extracting activations...")
        member_raw = extract_raw(model, member_loader, hook, SITES, TIMESTEPS, N_MEMBER, "member")
        nonmember_raw = extract_raw(model, nonmember_loader, hook, SITES, TIMESTEPS, N_NONMEMBER, "nonmember")
        with open(cache_path, "wb") as f:
            pickle.dump({"member_raw": member_raw, "nonmember_raw": nonmember_raw}, f)
        print(f"  Cached to {cache_path}")

    hook.remove()

    print("\n[4/4] Computing features + evaluating...")
    member_feats = compute_features(member_raw)
    nonmember_feats = compute_features(nonmember_raw)
    all_feats = member_feats + nonmember_feats
    y = np.concatenate([np.ones(len(member_feats)), np.zeros(len(nonmember_feats))])

    results = {"checkpoint": "DDIM-750k", "n_m": N_MEMBER, "n_nm": N_NONMEMBER}

    # Full decomposition
    stat_sets = {"all": ["mu_abs", "var", "sparsity"], "mu_only": ["mu_abs"],
                 "var_only": ["var"], "sparsity_only": ["sparsity"]}
    for label, stats in stat_sets.items():
        pca = PCA(n_components=PCA_N, random_state=SEED)
        pc_arr = build_pca_matrix(all_feats, SITES, TIMESTEPS, stats)
        pca.fit(pc_arr)
        X = build_feature_matrix(all_feats, pca, SITES, TIMESTEPS, stats)
        lr = LogisticRegression(max_iter=5000, random_state=SEED, class_weight='balanced', solver='lbfgs')
        lr.fit(X, y)
        train_auc = round(skm.roc_auc_score(y, lr.predict_proba(X)[:, 1]), 4)
        results[f"decomp_{label}"] = train_auc
        print(f"  {label:<20}: AUC={train_auc:.4f}")

    # Shadow evaluation
    agg_m_scores, agg_nm_scores = [], []
    for shadow_idx in range(N_SHADOWS):
        rng = np.random.RandomState(SEED + shadow_idx)
        pca = PCA(n_components=PCA_N, random_state=SEED + shadow_idx)
        pc_arr = build_pca_matrix(all_feats, SITES, TIMESTEPS, ["mu_abs", "var", "sparsity"])
        pca.fit(pc_arr)
        X = build_feature_matrix(all_feats, pca, SITES, TIMESTEPS, ["mu_abs", "var", "sparsity"])
        lr = LogisticRegression(max_iter=5000, random_state=SEED + shadow_idx,
                                class_weight='balanced', solver='lbfgs')
        lr.fit(X, y)
        m_scores = lr.predict_proba(X[:len(member_feats)])[:, 1]
        nm_scores = lr.predict_proba(X[len(member_feats):])[:, 1]
        agg_m_scores.append(m_scores)
        agg_nm_scores.append(nm_scores)
        shadow_metrics = compute_metrics(m_scores, nm_scores)
        print(f"  Shadow {shadow_idx+1}: AUC={shadow_metrics['auc']:.4f}  "
              f"TPR@1%={shadow_metrics['tpr_1pct']:.4f}  TPR@0.1%={shadow_metrics['tpr_01pct']:.4f}  "
              f"dir={shadow_metrics['direction']}")

    agg_m = np.mean(agg_m_scores, axis=0)
    agg_nm = np.mean(agg_nm_scores, axis=0)
    results["target"] = compute_metrics(agg_m, agg_nm)

    # Shuffle control
    all_scores = np.concatenate([agg_m, agg_nm])
    all_labels = np.concatenate([np.ones_like(agg_m), np.zeros_like(agg_nm)])
    rng = np.random.RandomState(SEED)
    shuf = rng.permutation(all_labels)
    try:
        shuf_auc = skm.roc_auc_score(shuf, -all_scores)
    except Exception:
        shuf_auc = 0.5
    results["shuffle_auc"] = round(float(shuf_auc), 6)

    # Per-site ablation
    ablation = {}
    for drop_site in SITES:
        reduced = [s for s in SITES if s != drop_site]
        pc_arr = build_pca_matrix(all_feats, reduced, TIMESTEPS, ["mu_abs", "var", "sparsity"])
        pca = PCA(n_components=PCA_N, random_state=SEED)
        pca.fit(pc_arr)
        X = build_feature_matrix(all_feats, pca, reduced, TIMESTEPS, ["mu_abs", "var", "sparsity"])
        lr = LogisticRegression(max_iter=5000, random_state=SEED, class_weight='balanced', solver='lbfgs')
        lr.fit(X, y)
        sm = lr.predict_proba(X[:len(member_feats)])[:, 1]
        snm = lr.predict_proba(X[len(member_feats):])[:, 1]
        ablation[f"drop_{drop_site}"] = compute_metrics(sm, snm)["auc"]
        print(f"  Ablation drop {drop_site}: AUC={ablation[f'drop_{drop_site}']:.4f}")

    results["ablation"] = ablation

    out_path = OUT_DIR / "h1_ddim_n128_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults → {out_path}")
    print(f"  Aggregate AUC: {results['target']['auc']:.4f}")
    print(f"  TPR@1%FPR:     {results['target']['tpr_1pct']:.4f}")
    print(f"  TPR@0.1%FPR:   {results['target']['tpr_01pct']:.4f}")
    print(f"  Shuffle AUC:   {results['shuffle_auc']:.4f}")
    print(f"  Time: {(time.time()-t0):.0f}s")



if __name__ == "__main__":
    main()
