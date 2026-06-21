#!/usr/bin/env python
"""
H1 DDIM 750k Channel Knockout — Causal Test
============================================
Verifies that DDIM's channel-level non-localizability matches DDPM's:
targeted knockout of top membership-correlated channels does NOT degrade
AUC more than random deletion of the same number of channels.

Design: matched-percent (4% of channels), 30 random seeds.

Usage:
  conda activate retrace-tr
  python scripts/h1_channel_knockout_ddim.py
"""
import sys, os, json, time, pickle, warnings
from pathlib import Path

import numpy as np
import torch
from scipy import stats as sps
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

# ── Constants ──
T = 1000; CH = 128; CH_MULT = [1, 2, 2, 2]; ATTN = [1]; NUM_RES_BLOCKS = 2
DROPOUT = 0.1; BETA_1 = 0.0001; BETA_T = 0.02

CKPT_PATH = "D:/Code/DiffAudit/Download/checkpoints/ddim-cifar10-750k/DDIM-ckpt-step750000.pt"
OUT_DIR = PROJECT / "outputs" / "h1-scout"

TIMESTEPS = [100, 400, 700]
SITES = ["late_down", "mid_0", "mid_1", "early_up"]
N_MEMBER = 64
N_NONMEMBER = 64
PCT_CHANNELS = 0.04  # 4% knockout
N_SEEDS = 30
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


SITE_PATHS = {
    "late_down": ["downblocks", "-1"],
    "mid_0":     ["middleblocks", "0"],
    "mid_1":     ["middleblocks", "1"],
    "early_up":  ["upblocks", "0"],
}


class ChannelKnockoutHook:
    def __init__(self, site_channels):
        self.site_channels = site_channels  # {site_name: [channel_indices to zero]}
        self.current_site = None

    def set_site(self, name):
        self.current_site = name

    def __call__(self, module, inp, out):
        if self.current_site and self.current_site in self.site_channels:
            ch_list = self.site_channels[self.current_site]
            if ch_list:
                o = out.clone()
                o[:, ch_list] = 0
                return o
        return out


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


def extract_activations(model, loader, hook, max_n, label):
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
    for flip in [False, True]:
        scores = np.concatenate([m, nm])
        if flip:
            scores = -scores
        try:
            auc = round(skm.roc_auc_score(labels, scores), 6)
            return auc
        except Exception:
            pass
    return 0.5


def find_top_channels(member_feats, nonmember_feats):
    """Per-channel t-test, return top 4% channels sorted by p-value."""
    all_channels = {}
    for site in SITES:
        for t_val in TIMESTEPS:
            key = f"{site}_t{t_val}_mu_abs"
            if key not in member_feats[0]:
                continue
            m_arr = np.stack([f[key] for f in member_feats])
            nm_arr = np.stack([f[key] for f in nonmember_feats])
            n_ch = m_arr.shape[1]
            n_ko = max(1, int(n_ch * PCT_CHANNELS))
            p_values = []
            for c in range(n_ch):
                _, p = sps.ttest_ind(m_arr[:, c], nm_arr[:, c])
                p_values.append((p, site, t_val, c))
            p_values.sort()
            top = p_values[:n_ko]
            for _, s, tv, c in top:
                if s not in all_channels:
                    all_channels[s] = []
                all_channels[s].append(c)
    return all_channels


def run_knockout_eval(model, loader, hook, member_feats, nonmember_feats,
                      channel_map, seed, label):
    """Evaluate H1 AUC with specified channels zeroed."""
    np.random.seed(seed)

    # Register knockout hooks on all sites
    ko_hook = ChannelKnockoutHook(channel_map)
    handles = []
    for site in SITES:
        target = model
        for p in SITE_PATHS[site]:
            if p.lstrip('-').isdigit():
                target = target[int(p)]
            else:
                target = getattr(target, p)
        h = target.register_forward_hook(ko_hook)
        handles.append((site, h))

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
                    ko_hook.set_site(site)
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

    m_ko = extract_ko(N_MEMBER, f"m_{label}")
    nm_ko = extract_ko(N_NONMEMBER, f"nm_{label}")

    m_feats_ko = compute_features(m_ko)
    nm_feats_ko = compute_features(nm_ko)

    all_feats = m_feats_ko + nm_feats_ko
    y = np.concatenate([np.ones(len(m_feats_ko)), np.zeros(len(nm_feats_ko))])
    pca = PCA(n_components=6, random_state=SEED)
    pc_arr = build_pca_matrix(all_feats, SITES, TIMESTEPS, ["mu_abs", "var"])
    pca.fit(pc_arr)
    X = build_feature_matrix(all_feats, pca, SITES, TIMESTEPS, ["mu_abs", "var"])
    lr = LogisticRegression(max_iter=5000, random_state=SEED, class_weight='balanced', solver='lbfgs')
    lr.fit(X, y)

    X_m = build_feature_matrix(m_feats_ko, pca, SITES, TIMESTEPS, ["mu_abs", "var"])
    X_nm = build_feature_matrix(nm_feats_ko, pca, SITES, TIMESTEPS, ["mu_abs", "var"])
    auc = compute_metrics(lr.predict_proba(X_m)[:, 1], lr.predict_proba(X_nm)[:, 1])

    for _, h in handles:
        h.remove()
    return auc


def main():
    t0 = time.time()
    print("=" * 60)
    print("H1 DDIM 750k Channel Knockout — Matched-Percent Causal Test")
    print(f"  Sites: {SITES}  Timesteps: {TIMESTEPS}")
    print(f"  N: {N_MEMBER}m/{N_NONMEMBER}nm  KO: {PCT_CHANNELS*100:.0f}%")
    print(f"  Seeds: {N_SEEDS}")
    print("=" * 60)

    # Load model
    print("\n[1/3] Loading DDIM 750k model...")
    model = load_model()
    hook = HookManager()
    for name in SITES:
        hook.register(model, name, SITE_PATHS[name])

    # Load data and extract baseline activations
    _, _, member_loader, nonmember_loader = load_member_data(
        dataset_name='CIFAR10', batch_size=64, shuffle=False, randaugment=False)

    cache_path = OUT_DIR / "h1_ddim_3t_activations.pkl"
    if cache_path.exists():
        print(f"\n[2/3] Loading cached activations...")
        with open(cache_path, "rb") as f:
            cache = pickle.load(f)
        member_raw = cache["member_raw"]
        nonmember_raw = cache["nonmember_raw"]
    else:
        print(f"\n[2/3] Extracting baseline activations...")
        member_raw = extract_activations(model, member_loader, hook, N_MEMBER, "member")
        nonmember_raw = extract_activations(model, nonmember_loader, hook, N_NONMEMBER, "nonmember")
        with open(cache_path, "wb") as f:
            pickle.dump({"member_raw": member_raw, "nonmember_raw": nonmember_raw}, f)

    member_feats = compute_features(member_raw)
    nonmember_feats = compute_features(nonmember_raw)

    # Baseline AUC
    all_feats = member_feats + nonmember_feats
    y = np.concatenate([np.ones(len(member_feats)), np.zeros(len(nonmember_feats))])
    pca = PCA(n_components=6, random_state=SEED)
    pc_arr = build_pca_matrix(all_feats, SITES, TIMESTEPS, ["mu_abs", "var"])
    pca.fit(pc_arr)
    X_base = build_feature_matrix(all_feats, pca, SITES, TIMESTEPS, ["mu_abs", "var"])
    lr_base = LogisticRegression(max_iter=5000, random_state=SEED, class_weight='balanced', solver='lbfgs')
    lr_base.fit(X_base, y)
    X_m = build_feature_matrix(member_feats, pca, SITES, TIMESTEPS, ["mu_abs", "var"])
    X_nm = build_feature_matrix(nonmember_feats, pca, SITES, TIMESTEPS, ["mu_abs", "var"])
    base_auc = compute_metrics(lr_base.predict_proba(X_m)[:, 1], lr_base.predict_proba(X_nm)[:, 1])
    print(f"  Baseline AUC: {base_auc:.4f}")

    # Find top channels
    top_channels = find_top_channels(member_feats, nonmember_feats)
    total_ko = sum(len(v) for v in top_channels.values())
    print(f"  Top {PCT_CHANNELS*100:.0f}% channels to knockout: {total_ko}")
    for s, chs in top_channels.items():
        n_ch_total = member_feats[0][f"{s}_t100_mu_abs"].shape[0]
        print(f"    {s}: {len(chs)}/{n_ch_total} ({len(chs)/n_ch_total*100:.1f}%)")

    # Run knockout experiments
    print(f"\n[3/3] Running {N_SEEDS}-seed matched-percent knockout...")
    targeted_aucs = []
    random_aucs = []

    for seed_idx in range(N_SEEDS):
        rs = SEED + seed_idx
        np.random.seed(rs)

        # Targeted: knockout top 4% channels
        ta = run_knockout_eval(model, member_loader, hook, member_feats, nonmember_feats,
                               top_channels, rs, f"targeted_s{seed_idx}")
        targeted_aucs.append(ta)

        # Random: knockout random 4% channels (same count per site)
        random_map = {}
        for site in SITES:
            key = f"{site}_t100_mu_abs"
            if key in member_feats[0]:
                n_ch = member_feats[0][key].shape[0]
                n_ko = max(1, int(n_ch * PCT_CHANNELS))
                random_map[site] = list(np.random.choice(n_ch, n_ko, replace=False))

        ra = run_knockout_eval(model, member_loader, hook, member_feats, nonmember_feats,
                               random_map, rs, f"random_s{seed_idx}")
        random_aucs.append(ra)

        print(f"  seed {seed_idx+1:2d}/{N_SEEDS}: targeted={ta:.4f}  random={ra:.4f}  "
              f"Δ={ta-ra:+.4f}")

    hook.remove()

    # Statistics
    t_arr = np.array(targeted_aucs)
    r_arr = np.array(random_aucs)
    diff = t_arr - r_arr
    mu_diff = np.mean(diff)
    sigma_diff = np.std(diff, ddof=1)
    d = mu_diff / sigma_diff if sigma_diff > 0 else 0
    t_stat, p_val = sps.ttest_rel(t_arr, r_arr)
    ci_lo = mu_diff - 1.96 * sigma_diff / np.sqrt(N_SEEDS)
    ci_hi = mu_diff + 1.96 * sigma_diff / np.sqrt(N_SEEDS)

    results = {
        "checkpoint": "DDIM-750k",
        "experiment": "matched_percent_channel_knockout",
        "baseline_auc": base_auc,
        "pct_channels": PCT_CHANNELS,
        "n_seeds": N_SEEDS,
        "targeted": {"mean": float(np.mean(t_arr)), "std": float(np.std(t_arr, ddof=1))},
        "random": {"mean": float(np.mean(r_arr)), "std": float(np.std(r_arr, ddof=1))},
        "comparison": {
            "mean_diff": float(mu_diff),
            "std_diff": float(sigma_diff),
            "cohens_d": float(d),
            "p_value": float(p_val),
            "ci_95": [float(ci_lo), float(ci_hi)],
        },
    }

    out_path = OUT_DIR / "h1_channel_knockout_ddim.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults → {out_path}")
    print(f"  Baseline: AUC={base_auc:.4f}")
    print(f"  Targeted: μ={np.mean(t_arr):.4f}, σ={np.std(t_arr, ddof=1):.4f}")
    print(f"  Random:   μ={np.mean(r_arr):.4f}, σ={np.std(r_arr, ddof=1):.4f}")
    print(f"  Diff:     μ={mu_diff:+.4f}, σ={sigma_diff:.4f}, d={d:.2f}, p={p_val:.3f}")
    print(f"  95% CI:   [{ci_lo:+.4f}, {ci_hi:+.4f}]")
    print(f"  Time: {(time.time() - t0):.0f}s")

    # Comparison with DDPM
    print(f"\n  DDPM 800k (from h1_matched_knockout): μ_diff=+0.004, σ=0.019, d=0.21, p=0.26")
    print(f"  DDIM 750k (this experiment):          μ_diff={mu_diff:+.4f}, σ={sigma_diff:.4f}, d={d:.2f}, p={p_val:.3f}")


if __name__ == "__main__":
    main()
