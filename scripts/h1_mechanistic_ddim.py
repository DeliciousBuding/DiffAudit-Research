#!/usr/bin/env python
"""
H1 DDIM 750k Mechanistic Analysis — Confirm channel-level DAAB properties
==========================================================================
Verifies that DDIM 750k shares the same channel-level DAAB signatures as DDPM 800k:
 1. mu_abs dominance (activation magnitude carries most signal)
 2. mu/var redundancy (either alone captures ~95% of combined AUC)
 3. Channel sparsity at chance level
 4. Per-channel t-test (which sites have significant channels)

Uses the DDIM fine grid activation cache (N=64/64, 8 timesteps, 2 sites).
Extends analysis to include 4 sites at 3 timesteps for full comparison.

Usage:
  conda activate retrace-tr
  python scripts/h1_mechanistic_ddim.py
"""
import sys, os, json, time, pickle, warnings
from pathlib import Path

import numpy as np
import torch
from scipy import stats as sps
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

# ── Constants ──
T = 1000; CH = 128; CH_MULT = [1, 2, 2, 2]; ATTN = [1]; NUM_RES_BLOCKS = 2
DROPOUT = 0.1; BETA_1 = 0.0001; BETA_T = 0.02

CKPT_PATH = "D:/Code/DiffAudit/Download/shared/weights/ddim-cifar10-step750000/raw/DDIM-ckpt-step750000.pt"
OUT_DIR = PROJECT / "outputs" / "h1_scout"

TIMESTEPS_3 = [100, 400, 700]
TIMESTEPS_8 = [50, 100, 150, 200, 300, 400, 600, 800]
SITES_4 = ["late_down", "mid_0", "mid_1", "early_up"]
SEED = 42


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


SITE_PATHS_4 = {
    "late_down": ["downblocks", "-1"],
    "mid_0":     ["middleblocks", "0"],
    "mid_1":     ["middleblocks", "1"],
    "early_up":  ["upblocks", "0"],
}


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


def extract_activations(model, loader, hook, site_names, timesteps, max_n, label):
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
    pc_arr = build_pca_matrix(feat_list, sites, timesteps, stat_types)
    if pc_arr is not None and pca_model is not None:
        X_pca = pca_model.transform(pc_arr)
        return np.concatenate([X_scalar, X_pca], axis=1)
    return X_scalar


def compute_metrics(m_scores, nm_scores):
    m, nm = np.asarray(m_scores), np.asarray(nm_scores)
    labels = np.concatenate([np.ones_like(m), np.zeros_like(nm)])
    best = {"auc": 0.5}
    for flip in [False, True]:
        scores = np.concatenate([m, nm])
        if flip:
            scores = -scores
        try:
            auc = skm.roc_auc_score(labels, scores)
        except Exception:
            auc = 0.5
        if auc > best["auc"]:
            best["auc"] = round(auc, 6)
    return best


def main():
    t0 = time.time()
    print("=" * 60)
    print("H1 DDIM 750k Mechanistic Analysis")
    print("=" * 60)

    # Load model
    model = load_model()
    hook = HookManager()
    for name in SITES_4:
        hook.register(model, name, SITE_PATHS_4[name])

    # Load data
    _, _, member_loader, nonmember_loader = load_member_data(
        dataset_name='CIFAR10', batch_size=64, shuffle=False, randaugment=False)

    # Check for cached fine grid activations
    fg_cache = OUT_DIR / "h1_ddim_fine_grid_activations.pkl"
    cache_3t = OUT_DIR / "h1_ddim_3t_activations.pkl"

    if cache_3t.exists():
        print("\nLoading cached 3-timestep activations...")
        with open(cache_3t, "rb") as f:
            cache = pickle.load(f)
        member_raw = cache["member_raw"]
        nonmember_raw = cache["nonmember_raw"]
    else:
        print("\nExtracting 3-timestep activations (4 sites × 3 timesteps)...")
        member_raw = extract_activations(model, member_loader, hook, SITES_4,
                                         TIMESTEPS_3, 64, "member")
        nonmember_raw = extract_activations(model, nonmember_loader, hook, SITES_4,
                                            TIMESTEPS_3, 64, "nonmember")
        with open(cache_3t, "wb") as f:
            pickle.dump({"member_raw": member_raw, "nonmember_raw": nonmember_raw}, f)
        print(f"  Cached to {cache_3t}")

    hook.remove()

    member_feats = compute_features(member_raw)
    nonmember_feats = compute_features(nonmember_raw)
    all_feats = member_feats + nonmember_feats
    y = np.concatenate([np.ones(len(member_feats)), np.zeros(len(nonmember_feats))])

    results = {"checkpoint": "DDIM-750k", "n_m": len(member_feats), "n_nm": len(nonmember_feats)}

    # 1. Baseline with all stats
    stat_sets = {
        "all": ["mu_abs", "var", "sparsity"],
        "mu_only": ["mu_abs"],
        "var_only": ["var"],
        "sparsity_only": ["sparsity"],
    }
    print("\n[1] Feature decomposition (4 sites × 3 timesteps):")
    for label, stats in stat_sets.items():
        pca = PCA(n_components=6, random_state=SEED)
        pc_arr = build_pca_matrix(all_feats, SITES_4, TIMESTEPS_3, stats)
        if pc_arr is not None:
            pca.fit(pc_arr)
        X = build_feature_matrix(all_feats, pca, SITES_4, TIMESTEPS_3, stats)
        lr = LogisticRegression(max_iter=5000, random_state=SEED, class_weight='balanced', solver='lbfgs')
        lr.fit(X, y)
        train_auc = round(skm.roc_auc_score(y, lr.predict_proba(X)[:, 1]), 4)
        results[f"decomp_{label}"] = train_auc
        print(f"  {label:<20}: AUC={train_auc:.4f}")

    # 2. Channel importance
    print("\n[2] Per-channel t-tests (member vs nonmember):")
    ch_results = {}
    for site in SITES_4:
        for t_val in TIMESTEPS_3:
            key_mu = f"{site}_t{t_val}_mu_abs"
            if key_mu not in member_feats[0]:
                continue
            m_arr = np.stack([f[key_mu] for f in member_feats])
            nm_arr = np.stack([f[key_mu] for f in nonmember_feats])
            n_ch = m_arr.shape[1]
            sig_count = 0
            for c in range(n_ch):
                t_stat, p_val = sps.ttest_ind(m_arr[:, c], nm_arr[:, c])
                if p_val < 0.01:
                    sig_count += 1
            pct = sig_count / n_ch * 100
            ch_results[f"{site}_t{t_val}"] = {"n_channels": n_ch, "sig_p01": sig_count, "pct": round(pct, 1)}
            print(f"  {site}_t{t_val:<4}: {sig_count}/{n_ch} ({pct:.1f}%) channels sig at p<0.01")

    results["channel_tests"] = ch_results

    # 3. Channel importance — variance explained
    print("\n[3] Per-channel variance explained:")
    for site in SITES_4:
        for t_val in TIMESTEPS_3:
            key_mu = f"{site}_t{t_val}_mu_abs"
            key_var = f"{site}_t{t_val}_var"
            if key_mu not in member_feats[0]:
                continue
            m_mu = np.stack([f[key_mu] for f in all_feats])
            m_var = np.stack([f[key_var] for f in all_feats])
            # LR with just this (site, timestep, stat)
            X_mu = np.mean(m_mu, axis=1, keepdims=True)
            X_var = np.mean(m_var, axis=1, keepdims=True)
            X_both = np.concatenate([X_mu, X_var], axis=1)
            for label, X in [("mu_abs", X_mu), ("var", X_var), ("mu+var", X_both)]:
                lr = LogisticRegression(max_iter=5000, random_state=SEED, class_weight='balanced', solver='lbfgs')
                lr.fit(X, y)
                auc = round(skm.roc_auc_score(y, lr.predict_proba(X)[:, 1]), 4)
                results[f"single_{site}_t{t_val}_{label}"] = auc

    # 4. Baseline with 8 timesteps (from fine grid cache)
    if fg_cache.exists():
        print("\n[4] 8-timestep feature decomposition:")
        with open(fg_cache, "rb") as f:
            fg = pickle.load(f)
        m8 = compute_features(fg["member_raw"])
        nm8 = compute_features(fg["nonmember_raw"])
        all8 = m8 + nm8
        y8 = np.concatenate([np.ones(len(m8)), np.zeros(len(nm8))])
        for label, stats in [("all", ["mu_abs", "var"]), ("mu_only", ["mu_abs"]), ("var_only", ["var"])]:
            pca = PCA(n_components=6, random_state=SEED)
            pc_arr = build_pca_matrix(all8, ["late_down", "mid_0"], TIMESTEPS_8, stats)
            if pc_arr is not None:
                pca.fit(pc_arr)
            X = build_feature_matrix(all8, pca, ["late_down", "mid_0"], TIMESTEPS_8, stats)
            lr = LogisticRegression(max_iter=5000, random_state=SEED, class_weight='balanced', solver='lbfgs')
            lr.fit(X, y8)
            auc = round(skm.roc_auc_score(y8, lr.predict_proba(X)[:, 1]), 4)
            results[f"fine8_{label}"] = auc
            print(f"  {label:<20}: AUC={auc:.4f}")

    # Save
    out_path = OUT_DIR / "h1_mechanistic_ddim.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults → {out_path}")
    print(f"Time: {(time.time() - t0):.0f}s")

    # Summary
    print("\n" + "=" * 60)
    print("DDPM vs DDIM Channel-Level Comparison")
    print("=" * 60)
    print(f"  DDPM mu_only AUC: 0.800 (from h1-activation-scout-memo)")
    print(f"  DDIM mu_only AUC: {results.get('decomp_mu_only', 'TBD')}")
    print(f"  DDPM sig channels (early_up): 4.7%")
    dd_early = ch_results.get("early_up_t100", {})
    print(f"  DDIM sig channels (early_up@t100): {dd_early.get('pct', 'TBD')}%")


if __name__ == "__main__":
    main()
