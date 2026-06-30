#!/usr/bin/env python
"""
H1 Fine Temporal Grid — CLI-parameterized (v2)
==============================================
Tests whether the resolution-dependence of causal effects
generalizes across checkpoints.

Design:
  - 8 timesteps: t=50,100,150,200,300,400,600,800
  - Sites: late_down, mid_0
  - Full-site knockout at each (site, timestep)
  - LR classifier, default N=64/64

Usage:
  conda activate retrace-tr
  python scripts/h1/h1_fine_grid_ddpm750k.py \
    --ckpt <path> --out <dir> [--n-member 64] [--n-nonmember 64] [--force]
"""
import sys, os, json, time, pickle, warnings, argparse, hashlib
from pathlib import Path

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

# ── Architecture constants ──
T = 1000; CH = 128; CH_MULT = [1, 2, 2, 2]; ATTN = [1]; NUM_RES_BLOCKS = 2
DROPOUT = 0.1; BETA_1 = 0.0001; BETA_T = 0.02

TIMESTEPS = [50, 100, 150, 200, 300, 400, 600, 800]
SITES = ["late_down", "mid_0"]
SEED = 42


def get_ckpt_sha(ckpt_path, prefix_len=12):
    h = hashlib.sha256()
    with open(ckpt_path, "rb") as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:prefix_len]


def parse_args():
    p = argparse.ArgumentParser(description="H1 Fine Temporal Grid v2")
    p.add_argument("--ckpt", required=True, help="Path to checkpoint .pt file")
    p.add_argument("--out", required=True, help="Output directory (relative to Research/ or absolute)")
    p.add_argument("--n-member", type=int, default=64, help="Number of member samples (default: 64)")
    p.add_argument("--n-nonmember", type=int, default=64, help="Number of nonmember samples (default: 64)")
    p.add_argument("--force", action="store_true", help="Delete existing cache and re-extract")
    return p.parse_args()


# ── Model ──

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


# ── Hook ──

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
}


# ── Feature extraction ──

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
    if not components:
        return None
    return np.concatenate(components, axis=1)


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
    best = {"auc": 0.5, "tpr_1pct": 0.0, "tpr_01pct": 0.0}
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


class SiteTimestepKnockoutHook:
    """Zero out ALL channels at a specific site during a specific timestep."""
    def __init__(self, site_name, knockout_t):
        self.site_name = site_name
        self.knockout_t = knockout_t
        self.current_t = None

    def set_t(self, t_val):
        self.current_t = t_val

    def __call__(self, module, inp, out):
        if self.current_t == self.knockout_t:
            return out * 0.0
        return out


def run_knockout(model, loader, hook, base_hooks, member_feats, nonmember_feats,
                 site, t_ko, all_sites, all_timesteps, label, n_member, n_nonmember):
    """Run full-site knockout at (site, t_ko), compute LR AUC."""
    ko_hook = SiteTimestepKnockoutHook(site, t_ko)
    target = model
    for p in SITE_PATHS[site]:
        if p.lstrip('-').isdigit():
            target = target[int(p)]
        else:
            target = getattr(target, p)
    h = target.register_forward_hook(ko_hook)

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
            for t_val in all_timesteps:
                hook.clear()
                for bh in base_hooks:
                    bh["hook_obj"].set_t(t_val)
                ko_hook.set_t(t_val)
                t_t = torch.full((B,), t_val, device=DEVICE, dtype=torch.long)
                noise = torch.randn_like(imgs)
                ac = model.alphas_cumprod[t_val]
                xt = ac.sqrt() * (imgs * 2 - 1) + (1 - ac).sqrt() * noise
                with torch.no_grad():
                    model(xt, t_t)
                for s in all_sites:
                    act = hook.data.get(s)
                    if act is None:
                        continue
                    key = f"{s}_t{t_val}"
                    for i in range(B):
                        batch_acts[i][key] = act[i:i+1].cpu()
            samples.extend(batch_acts)
            count += B
            if count % 16 == 0:
                print(f"  [{lbl}] {count}/{max_n}...")
        return samples[:max_n]

    m_ko = extract_ko(n_member, f"m_ko_{site}_t{t_ko}")
    nm_ko = extract_ko(n_nonmember, f"nm_ko_{site}_t{t_ko}")

    m_feats_ko = compute_features(m_ko)
    nm_feats_ko = compute_features(nm_ko)

    all_feats = m_feats_ko + nm_feats_ko
    y = np.concatenate([np.ones(len(m_feats_ko)), np.zeros(len(nm_feats_ko))])
    pca = PCA(n_components=min(6, len(all_feats) - 1), random_state=SEED)
    pc_arr = build_pca_matrix(all_feats, all_sites, all_timesteps, ["mu_abs", "var"])
    if pc_arr is not None and pc_arr.shape[0] > 6:
        pca.fit(pc_arr)
    else:
        pca = None

    X_ko = build_feature_matrix(all_feats, pca, all_sites, all_timesteps, ["mu_abs", "var"])
    lr = LogisticRegression(max_iter=5000, random_state=SEED, class_weight='balanced', solver='lbfgs')
    lr.fit(X_ko, y)

    X_m = build_feature_matrix(m_feats_ko, pca, all_sites, all_timesteps, ["mu_abs", "var"])
    X_nm = build_feature_matrix(nm_feats_ko, pca, all_sites, all_timesteps, ["mu_abs", "var"])
    m_scores = lr.predict_proba(X_m)[:, 1]
    nm_scores = lr.predict_proba(X_nm)[:, 1]

    h.remove()
    return compute_metrics(m_scores, nm_scores)


def main():
    args = parse_args()
    ckpt_path = args.ckpt
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = PROJECT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    ckpt_sha = get_ckpt_sha(ckpt_path)
    ckpt_name = Path(ckpt_path).parent.name
    cache_path = out_dir / f"h1_fine_grid_{ckpt_sha}_n{args.n_member}.pkl"

    if args.force and cache_path.exists():
        cache_path.unlink()
        print(f"  --force: deleted cache {cache_path.name}")

    t0 = time.time()
    n_member = args.n_member
    n_nonmember = args.n_nonmember

    print("=" * 60)
    print("H1 Fine Temporal Grid v2")
    print(f"  Checkpoint: {ckpt_path} ({ckpt_name})")
    print(f"  Sites: {SITES}  Timesteps: {TIMESTEPS}")
    print(f"  N: {n_member}m/{n_nonmember}nm")
    print("=" * 60)

    # Load model
    print("\n[1/4] Loading model...")
    model = load_model(ckpt_path)
    hook = HookManager()
    for name in SITES:
        hook.register(model, name, SITE_PATHS[name])
    print("  Model loaded.")

    # Load data
    print("\n[2/4] Loading CIFAR-10 split...")
    _, _, member_loader, nonmember_loader = load_member_data(
        dataset_name='CIFAR10', batch_size=64, shuffle=False, randaugment=False)

    # Extract or load
    if cache_path.exists() and not args.force:
        print(f"\n[3/4] Loading cached activations from {cache_path}...")
        with open(cache_path, "rb") as f:
            cache = pickle.load(f)
        member_raw = cache["member_raw"]
        nonmember_raw = cache["nonmember_raw"]
    else:
        print(f"\n[3/4] Extracting activations ({len(TIMESTEPS)} timesteps x {len(SITES)} sites)...")
        member_raw = extract_activations(model, member_loader, hook, SITES, TIMESTEPS, n_member, "member")
        nonmember_raw = extract_activations(model, nonmember_loader, hook, SITES, TIMESTEPS, n_nonmember, "nonmember")
        with open(cache_path, "wb") as f:
            pickle.dump({"member_raw": member_raw, "nonmember_raw": nonmember_raw}, f)
        print(f"  Cached to {cache_path}")

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
    base_m = lr_base.predict_proba(X_m)[:, 1]
    base_nm = lr_base.predict_proba(X_nm)[:, 1]
    base = compute_metrics(base_m, base_nm)
    print(f"\n  Baseline AUC={base['auc']:.4f} ({ckpt_name}, {len(TIMESTEPS)} timesteps)")

    # Per-timestep knockout hooks
    base_hook_objs = []
    for s in SITES:
        class TSetter:
            def __init__(self):
                self.current_t = None
            def set_t(self, tv):
                self.current_t = tv
            def __call__(self, module, inp, out):
                return out
        ts = TSetter()
        target = model
        for p in SITE_PATHS[s]:
            if p.lstrip('-').isdigit():
                target = target[int(p)]
            else:
                target = getattr(target, p)
        target.register_forward_hook(ts)
        base_hook_objs.append({"site": s, "hook_obj": ts})

    # Run knockout grid
    print("\n[4/4] Running knockout grid...")
    results = {"checkpoint": ckpt_name, "ckpt_sha": ckpt_sha,
               "baseline_auc": base["auc"],
               "timesteps": TIMESTEPS, "sites": SITES, "grid": {}}

    for site in SITES:
        for t_val in TIMESTEPS:
            label = f"{site}_t{t_val}"
            print(f"  {label}...", end=" ", flush=True)
            metrics = run_knockout(model,
                                   member_loader if n_member > 0 else nonmember_loader,
                                   hook, base_hook_objs, member_feats, nonmember_feats,
                                   site, t_val, SITES, TIMESTEPS, label, n_member, n_nonmember)
            delta = round(base["auc"] - metrics["auc"], 4)
            results["grid"][label] = {"auc": metrics["auc"], "delta": delta}
            print(f"AUC={metrics['auc']:.4f}  Delta={delta:+.4f}")

    hook.remove()

    out_path = out_dir / "h1_fine_grid_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults -> {out_path}")
    print(f"  Baseline: AUC={base['auc']:.4f}")
    print(f"  Time: {(time.time() - t0):.0f}s")

    # Summary table
    print("\n" + "=" * 60)
    print(f"Fine Temporal Grid — {ckpt_name}")
    print("=" * 60)
    header = f"{'Site':<12}" + "".join(f"{'t='+str(t):>10}" for t in TIMESTEPS)
    print(f"\n  {header}")
    for site in SITES:
        vals = []
        for t_val in TIMESTEPS:
            d = results["grid"][f"{site}_t{t_val}"]["delta"]
            vals.append(f"{d:+.4f}")
        print(f"  {site:<12}" + "".join(f"{v:>10}" for v in vals))

    # Max absolute deltas
    for site in SITES:
        max_d = max(abs(results["grid"][f"{site}_t{t}"]["delta"]) for t in TIMESTEPS)
        max_t = max(TIMESTEPS, key=lambda t: abs(results["grid"][f"{site}_t{t}"]["delta"]))
        print(f"  {site} max |Δ|: {max_d:.3f} (t={max_t})")


if __name__ == "__main__":
    main()
