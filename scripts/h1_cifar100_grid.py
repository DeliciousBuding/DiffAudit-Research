#!/usr/bin/env python
"""
H1 CIFAR-100 Cross-Dataset DAAB Validation — Spatiotemporal Grid
=================================================================
Tests whether the DAAB causal gradient (late_down >> mid_0 > mid_1 > early_up)
generalizes from CIFAR-10 to CIFAR-100.

Design: 4 sites × 3 timesteps, full-site knockout, CIFAR-100 DDPM checkpoint.

Usage:
  conda activate retrace-tr
  python scripts/h1_cifar100_grid.py
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

CKPT_PATH = "D:/Code/DiffAudit/Download/gray-box/weights/secmi-cifar-bundle/CIFAR100/checkpoint.pt"
OUT_DIR = PROJECT / "outputs" / "h1_scout"

TIMESTEPS = [100, 400, 700]
SITES = ["late_down", "mid_0", "mid_1", "early_up"]
N_MEMBER = 64
N_NONMEMBER = 64
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
            feats[f"{key}_mu_abs"] = mu_abs.numpy()
            feats[f"{key}_var"] = var.numpy()
            feats[f"{key}_mu_abs_mean"] = float(mu_abs.mean())
            feats[f"{key}_var_mean"] = float(var.mean())
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
            auc = round(skm.roc_auc_score(labels, scores), 4)
            if auc > best["auc"]:
                best["auc"] = auc
        except:
            pass
    return best

def knockout_eval(model, loader, hook, member_feats, nonmember_feats,
                  ko_site=None, ko_t=None):
    """Full-site knockout: zero ALL channels at ko_site during ko_t."""
    class SiteTimestepKO:
        def __init__(self):
            self.current_site = None
            self.current_t = None
        def set(self, s, t):
            self.current_site = s
            self.current_t = t
        def __call__(self, module, inp, out):
            if self.current_site == ko_site and self.current_t == ko_t:
                return out * 0.0
            return out

    ko = SiteTimestepKO()
    handles = []
    for s in SITES:
        target = model
        for p in SITE_PATHS[s]:
            if p.lstrip('-').isdigit():
                target = target[int(p)]
            else:
                target = getattr(target, p)
        handles.append(target.register_forward_hook(ko))

    def extract_ko(max_n, lbl):
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
            for t_val in TIMESTEPS:
                hook.clear()
                for site in SITES:
                    ko.set(site, t_val)
                t_t = torch.full((B,), t_val, device=DEVICE, dtype=torch.long)
                noise = torch.randn_like(imgs)
                ac = model.alphas_cumprod[t_val]
                xt = ac.sqrt() * (imgs * 2 - 1) + (1 - ac).sqrt() * noise
                with torch.no_grad():
                    model(xt, t_t)
                for site in SITES:
                    act = hook.data.get(site)
                    if act is None:
                        continue
                    key = f"{site}_t{t_val}"
                    for i in range(B):
                        batch_acts[i][key] = act[i:i+1].cpu()
            samples.extend(batch_acts)
            count += B
        return samples[:max_n]

    m_ko = extract_ko(N_MEMBER, f"ko_{ko_site}_t{ko_t}_m")
    nm_ko = extract_ko(N_NONMEMBER, f"ko_{ko_site}_t{ko_t}_nm")
    m_feats = compute_features(m_ko)
    nm_feats = compute_features(nm_ko)
    all_f = m_feats + nm_feats
    y = np.concatenate([np.ones(len(m_feats)), np.zeros(len(nm_feats))])

    pca = PCA(n_components=6, random_state=SEED)
    pc_arr = build_pca_matrix(all_f, SITES, TIMESTEPS, ["mu_abs", "var"])
    pca.fit(pc_arr)
    X = build_feature_matrix(all_f, pca, SITES, TIMESTEPS, ["mu_abs", "var"])
    lr = LogisticRegression(max_iter=5000, random_state=SEED, class_weight='balanced', solver='lbfgs')
    lr.fit(X, y)
    Xm = build_feature_matrix(m_feats, pca, SITES, TIMESTEPS, ["mu_abs", "var"])
    Xnm = build_feature_matrix(nm_feats, pca, SITES, TIMESTEPS, ["mu_abs", "var"])
    auc = compute_metrics(lr.predict_proba(Xm)[:, 1], lr.predict_proba(Xnm)[:, 1])["auc"]
    for h in handles:
        h.remove()
    return auc

def main():
    t0 = time.time()
    print("=" * 60)
    print("H1 CIFAR-100 Spatiotemporal Grid — Cross-Dataset DAAB")
    print("=" * 60)

    model = load_model()
    hook = HookManager()
    for name in SITES:
        hook.register(model, name, SITE_PATHS[name])

    print("\nLoading CIFAR-100 data...")
    _, _, member_loader, nonmember_loader = load_member_data(
        dataset_name='CIFAR100', batch_size=64, shuffle=False, randaugment=False)

    cache_path = OUT_DIR / "h1_cifar100_activations.pkl"
    if cache_path.exists():
        with open(cache_path, "rb") as f:
            cache = pickle.load(f)
        member_raw = cache["member_raw"]
        nonmember_raw = cache["nonmember_raw"]
        print("  Loaded cached activations")
    else:
        print("  Extracting (N=64/64, 4 sites, 3 timesteps)...")
        member_raw = extract_activations(model, member_loader, hook, SITES, TIMESTEPS, N_MEMBER, "member")
        nonmember_raw = extract_activations(model, nonmember_loader, hook, SITES, TIMESTEPS, N_NONMEMBER, "nonmember")
        with open(cache_path, "wb") as f:
            pickle.dump({"member_raw": member_raw, "nonmember_raw": nonmember_raw}, f)

    m_feats = compute_features(member_raw)
    nm_feats = compute_features(nonmember_raw)
    all_f = m_feats + nm_feats
    y = np.concatenate([np.ones(len(m_feats)), np.zeros(len(nm_feats))])

    # Baseline
    pca = PCA(n_components=6, random_state=SEED)
    pc_arr = build_pca_matrix(all_f, SITES, TIMESTEPS, ["mu_abs", "var"])
    pca.fit(pc_arr)
    X = build_feature_matrix(all_f, pca, SITES, TIMESTEPS, ["mu_abs", "var"])
    lr = LogisticRegression(max_iter=5000, random_state=SEED, class_weight='balanced', solver='lbfgs')
    lr.fit(X, y)
    Xm = build_feature_matrix(m_feats, pca, SITES, TIMESTEPS, ["mu_abs", "var"])
    Xnm = build_feature_matrix(nm_feats, pca, SITES, TIMESTEPS, ["mu_abs", "var"])
    base = compute_metrics(lr.predict_proba(Xm)[:, 1], lr.predict_proba(Xnm)[:, 1])
    print(f"\n  Baseline AUC: {base['auc']:.4f}")

    # Full-site knockout grid
    print("\nRunning full-site knockout grid...")
    results = {"checkpoint": "CIFAR100-DDPM", "baseline_auc": base["auc"], "grid": {}}
    for site in SITES:
        for t_val in TIMESTEPS:
            label = f"{site}_t{t_val}"
            print(f"  {label}...", end=" ", flush=True)
            auc = knockout_eval(model, member_loader, hook, m_feats, nm_feats, ko_site=site, ko_t=t_val)
            delta = round(base["auc"] - auc, 4)
            results["grid"][label] = {"auc": auc, "delta": delta}
            print(f"AUC={auc:.4f}  Δ={delta:+.4f}")

    hook.remove()

    # Save
    out_path = OUT_DIR / "h1_cifar100_grid.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults → {out_path}")

    # Summary table
    print(f"\n{'Site':<12} {'t=100':>10} {'t=400':>10} {'t=700':>10}")
    for site in SITES:
        vals = [f"{results['grid'][f'{site}_t{t}']['delta']:+.4f}" for t in TIMESTEPS]
        print(f"  {site:<12}{vals[0]:>10}{vals[1]:>10}{vals[2]:>10}")

    # Compare with CIFAR-10 DDPM
    print(f"\n  CIFAR-10 DDPM: late_down Δ=[+0.138, +0.039, +0.006], mid_0 [+0.149, +0.002, +0.008]")
    print(f"  CIFAR-100:      late_down Δ=[{results['grid']['late_down_t100']['delta']:+.4f}, {results['grid']['late_down_t400']['delta']:+.4f}, {results['grid']['late_down_t700']['delta']:+.4f}]")
    print(f"  Time: {(time.time()-t0):.0f}s")

if __name__ == "__main__":
    main()
