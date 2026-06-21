"""
Bootstrap confidence intervals for CLiD and scnet ΔAUC in DiffAudit Paper 1.

Computes paired bootstrap CIs (10,000 resamples, 95% CI, bias-corrected) for:
- CLiD:  ΔAUC between prompt-conditioned (full) and prompt-neutral (knockout) conditions
- scnet: ΔAUC between TC64 (0.78M params) and TC192 (42.97M params) conditions

Methodology replicates the CLiD scoring pipeline from diffaudit/attacks/clid.py:
  _extract_clid_features → _robust_fit → _robust_transform → _weighted_score

For scnet, per-sample scores are not available in the cached results;
we report existing bootstrap CIs from the paper and recompute what we can
from the available aggregated data.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import stats

# ── Paths ──────────────────────────────────────────────────────────────────
RESEARCH_ROOT = Path("D:/Code/DiffAudit/Research")
OUTPUT_DIR = Path("D:/Code/DiffAudit/Research/outputs")
OUTPUT_PATH = OUTPUT_DIR / "bootstrap_results.json"

# CLiD raw score files — prompt-conditioned (full) condition
CLID_FULL_DIR = RESEARCH_ROOT / "workspaces/black-box/runs/clid-local-bridge-100-20260501-r1/outputs"
CLID_FULL_MEMBER = CLID_FULL_DIR / "Atk_clid_clip_M_local_paper_align_DATA_member_TRTE_train_MAXsmp_1_T_0501_032645.txt"
CLID_FULL_NONMEMBER = CLID_FULL_DIR / "Atk_clid_clip_M_local_paper_align_DATA_member_TRTE_test_MAXsmp_1_T_0501_032645.txt"

# CLiD raw score files — prompt-neutral (knockout) condition
CLID_KO_DIR = RESEARCH_ROOT / "workspaces/black-box/runs/clid-local-bridge-100-prompt-neutral-20260501-r1/outputs"
CLID_KO_MEMBER = CLID_KO_DIR / "Atk_clid_clip_M_local_paper_align_DATA_member_TRTE_train_MAXsmp_1_T_0501_041251.txt"
CLID_KO_NONMEMBER = CLID_KO_DIR / "Atk_clid_clip_M_local_paper_align_DATA_member_TRTE_test_MAXsmp_1_T_0501_041251.txt"

# scnet result files
SCNET_DIR = Path("D:/Code/DiffAudit/scnet/output/cancon-results")
SCNET_TC64 = SCNET_DIR / "ddim_secmi_tc64_s42_e15.json"
SCNET_TC128 = SCNET_DIR / "ddim_secmi_tc128_s42_e50.json"
SCNET_TC192 = SCNET_DIR / "ddim_secmi_tc192_s42_e18.json"

# ── Constants ──────────────────────────────────────────────────────────────
RNG_SEED = 42
N_BOOT = 10_000
CI_LEVEL = 0.95
ALPHA_SWEEP = np.linspace(0.0, 1.0, num=11)


# ── CLiD scoring helpers (replicated from clid.py) ─────────────────────────
def load_clid_score_matrix(path: Path) -> np.ndarray:
    """Load tab-separated CLiD score matrix, skipping the header line."""
    rows: list[list[float]] = []
    with path.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            try:
                rows.append([float(v) for v in line.split("\t")])
            except ValueError:
                continue
    if not rows:
        raise ValueError(f"No numeric data in {path}")
    return np.asarray(rows, dtype=float)


def extract_clid_features(matrix: np.ndarray) -> np.ndarray:
    """Extract 2 features from raw 5-column matrix:
    feature0 = column 0;
    feature1 (clid_aux) = -mean(columns 1..N-1).
    """
    if matrix.ndim != 2 or matrix.shape[1] < 2:
        raise ValueError("Need at least 2 columns")
    clid_avg = -matrix[:, 1:].mean(axis=1)
    return np.column_stack((matrix[:, 0], clid_avg))


def robust_fit(features: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Robust location/scale via median and IQR."""
    center = np.median(features, axis=0)
    q1 = np.percentile(features, 25, axis=0)
    q3 = np.percentile(features, 75, axis=0)
    scale = q3 - q1
    scale[scale == 0] = 1.0
    return center, scale


def robust_transform(features: np.ndarray, center: np.ndarray, scale: np.ndarray) -> np.ndarray:
    return (features - center) / scale


def weighted_score(features: np.ndarray, alpha: float) -> np.ndarray:
    """(1-alpha) * feature0 + alpha * feature1"""
    return (1.0 - alpha) * features[:, 0] + alpha * features[:, 1]


def auc_member_low(train_scores: np.ndarray, test_scores: np.ndarray) -> float:
    """AUC with direction: member scores LOW = positive (<= threshold)."""
    wins = (train_scores[:, None] < test_scores[None, :]).astype(float)
    ties = (train_scores[:, None] == test_scores[None, :]).astype(float) * 0.5
    return float((wins + ties).mean())


def compute_auc(member_scores: np.ndarray, nonmember_scores: np.ndarray) -> float:
    """AUC for a single pair of score arrays."""
    return auc_member_low(member_scores, nonmember_scores)


# ── Paired bootstrap for CLiD ──────────────────────────────────────────────
def bootstrap_clid(n_boot: int = N_BOOT, seed: int = RNG_SEED) -> dict:
    """
    Paired bootstrap CI for CLiD ΔAUC between full (prompt-conditioned)
    and knockout (prompt-neutral) conditions.

    The pairing is preserved by resampling indices: each bootstrap sample
    draws N indices with replacement from {0..N-1}, then takes the
    corresponding rows from both conditions.
    """
    rng = np.random.default_rng(seed)

    # ── Load and extract features for both conditions ──
    # Full condition
    full_member_raw = load_clid_score_matrix(CLID_FULL_MEMBER)
    full_nonmember_raw = load_clid_score_matrix(CLID_FULL_NONMEMBER)
    full_member_feat = extract_clid_features(full_member_raw)
    full_nonmember_feat = extract_clid_features(full_nonmember_raw)

    # Knockout (prompt-neutral) condition
    ko_member_raw = load_clid_score_matrix(CLID_KO_MEMBER)
    ko_nonmember_raw = load_clid_score_matrix(CLID_KO_NONMEMBER)
    ko_member_feat = extract_clid_features(ko_member_raw)
    ko_nonmember_feat = extract_clid_features(ko_nonmember_raw)

    # Verify dimensions
    n_member = full_member_feat.shape[0]
    n_nonmember = full_nonmember_feat.shape[0]
    assert ko_member_feat.shape[0] == n_member, "Member count mismatch between conditions"
    assert ko_nonmember_feat.shape[0] == n_nonmember, "Nonmember count mismatch between conditions"

    print(f"  CLiD: {n_member} members, {n_nonmember} nonmembers")

    # ── Fit robust normalization on combined full-condition data ──
    all_full = np.vstack((full_member_feat, full_nonmember_feat))
    center, scale = robust_fit(all_full)

    # Transform all data with the same (full-condition) normalization
    full_member_scaled = robust_transform(full_member_feat, center, scale)
    full_nonmember_scaled = robust_transform(full_nonmember_feat, center, scale)
    ko_member_scaled = robust_transform(ko_member_feat, center, scale)
    ko_nonmember_scaled = robust_transform(ko_nonmember_feat, center, scale)

    # ── Compute point estimates ─────────────────────────────────
    # Alpha sweep on full condition to find best alpha
    best_alpha, best_auc = 0.0, -1.0
    for alpha in ALPHA_SWEEP:
        full_member_s = weighted_score(full_member_scaled, float(alpha))
        full_nonmember_s = weighted_score(full_nonmember_scaled, float(alpha))
        auc_val = compute_auc(full_member_s, full_nonmember_s)
        if auc_val > best_auc:
            best_auc = auc_val
            best_alpha = float(alpha)

    # Full condition AUC at best_alpha
    full_member_scores = weighted_score(full_member_scaled, best_alpha)
    full_nonmember_scores = weighted_score(full_nonmember_scaled, best_alpha)
    full_auc = compute_auc(full_member_scores, full_nonmember_scores)

    # Knockout condition AUC at the SAME alpha
    ko_member_scores = weighted_score(ko_member_scaled, best_alpha)
    ko_nonmember_scores = weighted_score(ko_nonmember_scaled, best_alpha)
    ko_auc = compute_auc(ko_member_scores, ko_nonmember_scores)

    delta_auc_point = full_auc - ko_auc
    print(f"  Best alpha: {best_alpha}")
    print(f"  Full AUC:   {full_auc:.6f}")
    print(f"  KO AUC:     {ko_auc:.6f}")
    print(f"  ΔAUC point: {delta_auc_point:.6f}")

    # ── Bootstrap ────────────────────────────────────────────────
    # Stack member and nonmember data for paired resampling
    # Member: [full_member_scaled, ko_member_scaled]  (n_member rows, 2 feature_cols, 2 conditions)
    # Nonmember: [full_nonmember_scaled, ko_nonmember_scaled]
    member_stack = np.stack([full_member_scaled, ko_member_scaled], axis=0)      # (2, n_member, 2)
    nonmember_stack = np.stack([full_nonmember_scaled, ko_nonmember_scaled], axis=0)  # (2, n_nonmem, 2)

    boot_deltas = np.empty(n_boot, dtype=float)

    t0 = time.time()
    for i in range(n_boot):
        # Resample indices with replacement
        m_idx = rng.integers(0, n_member, size=n_member)
        nm_idx = rng.integers(0, n_nonmember, size=n_nonmember)

        # Bootstrap samples for both conditions
        # Shape: (n_samples, n_features)
        boot_full_member = member_stack[0, m_idx]
        boot_ko_member = member_stack[1, m_idx]
        boot_full_nonmember = nonmember_stack[0, nm_idx]
        boot_ko_nonmember = nonmember_stack[1, nm_idx]

        # Re-fit robust normalization on each bootstrap sample (full condition only)
        # Following CLiD pipeline: fit on combined shadow-like data, apply to both
        boot_all_full = np.vstack((boot_full_member, boot_full_nonmember))
        boot_center, boot_scale = robust_fit(boot_all_full)

        boot_full_member_t = robust_transform(boot_full_member, boot_center, boot_scale)
        boot_full_nonmember_t = robust_transform(boot_full_nonmember, boot_center, boot_scale)
        boot_ko_member_t = robust_transform(boot_ko_member, boot_center, boot_scale)
        boot_ko_nonmember_t = robust_transform(boot_ko_nonmember, boot_center, boot_scale)

        # Re-run alpha sweep on bootstrap full condition
        boot_best_alpha = 0.0
        boot_best_auc_val = -1.0
        for alpha in ALPHA_SWEEP:
            bm_s = weighted_score(boot_full_member_t, float(alpha))
            bnm_s = weighted_score(boot_full_nonmember_t, float(alpha))
            auc_val = compute_auc(bm_s, bnm_s)
            if auc_val > boot_best_auc_val:
                boot_best_auc_val = auc_val
                boot_best_alpha = float(alpha)

        # AUCs at best bootstrap alpha
        bf_s = weighted_score(boot_full_member_t, boot_best_alpha)
        bfnm_s = weighted_score(boot_full_nonmember_t, boot_best_alpha)
        boot_full_auc = compute_auc(bf_s, bfnm_s)

        bk_s = weighted_score(boot_ko_member_t, boot_best_alpha)
        bknm_s = weighted_score(boot_ko_nonmember_t, boot_best_alpha)
        boot_ko_auc = compute_auc(bk_s, bknm_s)

        boot_deltas[i] = boot_full_auc - boot_ko_auc

        if (i + 1) % 2000 == 0:
            elapsed = time.time() - t0
            print(f"    Bootstrap {i+1}/{n_boot} ({elapsed:.1f}s)")

    elapsed = time.time() - t0
    print(f"  Bootstrap complete in {elapsed:.1f}s")

    # ── Compute CIs ──────────────────────────────────────────────
    # Percentile CI
    lower_pct = (1.0 - CI_LEVEL) / 2
    upper_pct = 1.0 - lower_pct
    ci_percentile = tuple(np.percentile(boot_deltas, [lower_pct * 100, upper_pct * 100]))

    # Bias-corrected (BC) CI
    z0 = stats.norm.ppf(np.mean(boot_deltas < delta_auc_point))
    z_alpha = stats.norm.ppf(lower_pct)
    bc_lower = stats.norm.cdf(2 * z0 + z_alpha)
    bc_upper = stats.norm.cdf(2 * z0 - z_alpha)
    ci_bc = tuple(np.percentile(boot_deltas, [bc_lower * 100, bc_upper * 100]))

    # Standard error
    se = float(np.std(boot_deltas, ddof=1))

    return {
        "method": "CLiD",
        "condition_full": "prompt-conditioned",
        "condition_knockout": "prompt-neutral",
        "n_member": int(n_member),
        "n_nonmember": int(n_nonmember),
        "n_bootstrap": n_boot,
        "ci_level": CI_LEVEL,
        "best_alpha": best_alpha,
        "full_auc": round(float(full_auc), 6),
        "knockout_auc": round(float(ko_auc), 6),
        "delta_auc_point_estimate": round(float(delta_auc_point), 6),
        "delta_auc_std_error": round(float(se), 6),
        "ci_percentile": [round(float(v), 6) for v in ci_percentile],
        "ci_bias_corrected": [round(float(v), 6) for v in ci_bc],
        "z0": round(float(z0), 6),
        "bootstrap_samples": len(boot_deltas),
    }


# ── scnet analysis (aggregated, no per-sample scores) ──────────────────────
def analyze_scnet() -> dict:
    """
    scnet per-sample scores are not available in cached results.
    Reconstruct what we can from published summary statistics.

    The paper already reports:
      TC64:  AUC=0.514, 95% CI [0.495, 0.531], K=2000
      TC128: AUC=0.518, 95% CI [0.501, 0.536], K=2000
      TC192: AUC=0.517, 95% CI [0.499, 0.535], K=2000
      ΔAUC (TC192-TC64): 0.003, approx 95% CI [-0.0225, 0.0285], approx p=0.82
    """
    results = {}

    # Load available JSON summaries
    for label, path in [("tc64", SCNET_TC64), ("tc128", SCNET_TC128), ("tc192", SCNET_TC192)]:
        if path.exists():
            with path.open("r") as f:
                data = json.load(f)
            results[label] = {
                "ch": data.get("ch"),
                "params": data.get("params"),
                "total_epochs": data.get("total_epochs"),
                "K": data.get("K"),
                "n_boot": data.get("n_boot"),
                "best_auc": data.get("best", {}).get("auc"),
                "best_auc_ci": data.get("best", {}).get("ci"),
            }
        else:
            results[label] = {"error": f"File not found: {path}"}

    # Compute pooled ΔAUC estimate using Welch's approximation
    # TC64: AUC=0.514, CI width ≈ 0.036 → SE ≈ 0.0092 (from CI width / (2*1.96))
    # TC192: AUC=0.517, CI width ≈ 0.036 → SE ≈ 0.0092
    # For ΔAUC, SE = sqrt(SE1^2 + SE2^2) ≈ 0.013
    # 95% CI ≈ Δ ± 1.96*SE ≈ 0.003 ± 0.0255
    tc64_auc = 0.514
    tc192_auc = 0.517
    delta_point = tc192_auc - tc64_auc

    # CI widths from paper
    tc64_ci = [0.495, 0.531]
    tc192_ci = [0.499, 0.535]

    tc64_se = (tc64_ci[1] - tc64_ci[0]) / (2 * 1.96)
    tc192_se = (tc192_ci[1] - tc192_ci[0]) / (2 * 1.96)
    delta_se = np.sqrt(tc64_se**2 + tc192_se**2)
    delta_ci = [delta_point - 1.96 * delta_se, delta_point + 1.96 * delta_se]

    results["delta_analysis"] = {
        "method": "scnet",
        "comparison": "TC192 (42.97M params) vs TC64 (0.78M params)",
        "capacity_ratio": "54x",
        "delta_auc_point_estimate": round(float(delta_point), 6),
        "delta_auc_std_error": round(float(delta_se), 6),
        "delta_auc_ci_approx_95pct": [round(float(v), 6) for v in delta_ci],
        "tc64_auc": tc64_auc,
        "tc64_ci_95pct": tc64_ci,
        "tc192_auc": tc192_auc,
        "tc192_ci_95pct": tc192_ci,
        "note": (
            "Per-sample score vectors not found in cached results. "
            "Only summary AUCs and CIs are available from the DCU experiment JSON files. "
            "Existing CIs from paper: K=2000, n_boot=10000. "
            "Delta CI computed via Welch approximation from reported marginal CIs. "
            "Paper also reports: approx 95% CI [-0.0225, 0.0285], approx p=0.82."
        ),
        "raw_scores_available": False,
    }

    return results


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("Bootstrap CI Computation for DiffAudit Paper 1")
    print("=" * 70)
    print()

    results = {
        "metadata": {
            "generated_by": "Research/analysis/bootstrap_ci.py",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "n_bootstrap": N_BOOT,
            "ci_level": CI_LEVEL,
            "seed": RNG_SEED,
            "python_version": sys.version,
            "numpy_version": np.__version__,
        }
    }

    # ── 1. CLiD paired bootstrap ──
    print("[1/2] CLiD: paired bootstrap ΔAUC (prompt-conditioned vs prompt-neutral)")
    print("-" * 60)
    clid_results = bootstrap_clid()
    results["CLiD"] = clid_results
    print()
    print(f"  ΔAUC point estimate:      {clid_results['delta_auc_point_estimate']:.6f}")
    print(f"  ΔAUC SE:                   {clid_results['delta_auc_std_error']:.6f}")
    print(f"  95% CI (percentile):       [{clid_results['ci_percentile'][0]:.6f}, {clid_results['ci_percentile'][1]:.6f}]")
    print(f"  95% CI (bias-corrected):   [{clid_results['ci_bias_corrected'][0]:.6f}, {clid_results['ci_bias_corrected'][1]:.6f}]")
    print()

    # ── 2. scnet analysis ──
    print("[2/2] scnet: capacity-scaling ΔAUC (TC64 vs TC192)")
    print("-" * 60)
    scnet_results = analyze_scnet()
    results["scnet"] = scnet_results
    print()
    d = scnet_results.get("delta_analysis", {})
    print(f"  ΔAUC point estimate:      {d.get('delta_auc_point_estimate', 'N/A')}")
    print(f"  ΔAUC approximate 95% CI:  {d.get('delta_auc_ci_approx_95pct', 'N/A')}")
    print(f"  Raw per-sample scores:     {d.get('raw_scores_available', False)}")
    print()

    # ── Save ──
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results saved to: {OUTPUT_PATH}")
    print("Done.")


if __name__ == "__main__":
    main()
