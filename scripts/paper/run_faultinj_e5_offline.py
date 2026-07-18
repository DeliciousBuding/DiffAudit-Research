#!/usr/bin/env python3
"""faultinj-e5: offline positive-leak + pure-noise instrument controls.

Exploratory only. Labels: faultinj-e5-*. Does not touch formal run_labels,
0.55 gates, or confirmatory results tables.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def _auc(y_true: np.ndarray, scores: np.ndarray) -> float:
    y = np.asarray(y_true).astype(int)
    s = np.asarray(scores, dtype=float)
    if len(np.unique(y)) < 2:
        return float("nan")
    return float(roc_auc_score(y, s))


def _bootstrap_auc_ci(
    y_true: np.ndarray, scores: np.ndarray, n: int, rng: np.random.Generator
) -> tuple[float, float, float]:
    y = np.asarray(y_true).astype(int)
    s = np.asarray(scores, dtype=float)
    point = _auc(y, s)
    boots = []
    m = len(y)
    for _ in range(n):
        idx = rng.integers(0, m, size=m)
        # require both classes
        if len(np.unique(y[idx])) < 2:
            continue
        boots.append(_auc(y[idx], s[idx]))
    if not boots:
        return point, float("nan"), float("nan")
    lo, hi = np.quantile(boots, [0.025, 0.975])
    return point, float(lo), float(hi)


def _fit_score(x_cal, y_cal, x_eval, y_eval, rng_seed: int) -> dict:
    clf = make_pipeline(
        StandardScaler(with_mean=True, with_std=True),
        LogisticRegression(
            max_iter=2000,
            solver="lbfgs",
            random_state=rng_seed,
        ),
    )
    clf.fit(x_cal, y_cal)
    scores = clf.decision_function(x_eval)
    rng = np.random.default_rng(rng_seed)
    point, lo, hi = _bootstrap_auc_ci(y_eval, scores, n=400, rng=rng)
    return {
        "auc_point": point,
        "auc_ci95": [lo, hi],
        "n_cal": int(len(y_cal)),
        "n_eval": int(len(y_eval)),
        "n_pos_eval": int((y_eval == 1).sum()),
        "n_neg_eval": int((y_eval == 0).sum()),
    }


def load_packet(packet_dir: Path):
    man = json.loads((packet_dir / "manifest.json").read_text(encoding="utf-8"))
    z = np.load(packet_dir / "features.npz")
    rows = man["rows"]
    labels = np.array([int(r["label"]) for r in rows], dtype=int)
    splits = np.array([r["calibration_or_evaluation"] for r in rows])
    cal = splits == "calibration"
    ev = splits == "evaluation"
    return {
        "manifest": man,
        "labels": labels,
        "cal": cal,
        "eval": ev,
        "pca": z["pca_features"],
        "scalar": z["scalar_features"],
        "dataset_indices": z["dataset_indices"],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--packet-dir",
        type=Path,
        default=Path(
            "outputs/paper1-corrected-evidence/h1-packets/"
            "corrected-s1746574482-step100000"
        ),
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("outputs/paper1-corrected-evidence/fault-injection"),
    )
    ap.add_argument("--seed", type=int, default=20260718)
    args = ap.parse_args()

    t0 = time.time()
    pkt = load_packet(args.packet_dir)
    y = pkt["labels"]
    cal, ev = pkt["cal"], pkt["eval"]
    y_cal, y_eval = y[cal], y[ev]
    rng = np.random.default_rng(args.seed)

    # E5-P1 positive: perfect membership-bit feature (label itself)
    x_pos = y.astype(np.float32).reshape(-1, 1)
    # Add tiny noise so LR is well-defined but nearly perfect
    x_pos = np.concatenate(
        [x_pos, (y.astype(np.float32) * 10.0 + rng.normal(0, 1e-6, size=y.shape)).reshape(-1, 1)],
        axis=1,
    )
    pos = _fit_score(x_pos[cal], y_cal, x_pos[ev], y_eval, args.seed)

    # E5-P2 noise: i.i.d. Gaussian independent of membership (match scalar width)
    x_noise = rng.normal(0.0, 1.0, size=(len(y), 16)).astype(np.float32)
    noise = _fit_score(x_noise[cal], y_cal, x_noise[ev], y_eval, args.seed + 1)

    # Optional sanity: sealed scalar features under same offline LR path (not confirmatory)
    sealed_scalar = _fit_score(
        pkt["scalar"][cal], y_cal, pkt["scalar"][ev], y_eval, args.seed + 2
    )

    e5_p1_pass = pos["auc_point"] >= 0.99
    e5_p2_pass = (
        (0.45 <= noise["auc_point"] <= 0.55)
        and (noise["auc_ci95"][0] <= 0.50 <= noise["auc_ci95"][1])
    )

    receipt = {
        "protocol_label": "faultinj-e5-offline-positive-noise-2026-07-18",
        "evidence_class": "exploratory_non_confirmatory",
        "run_labels": ["faultinj-e5-positive-leak", "faultinj-e5-pure-noise"],
        "created_at_unix": int(time.time()),
        "random_seed": args.seed,
        "packet_dir": str(args.packet_dir).replace("\\", "/"),
        "packet_run_label": pkt["manifest"]["provenance"].get("run_label"),
        "packet_step": pkt["manifest"]["provenance"].get("step"),
        "training_protocol_hash": pkt["manifest"]["provenance"].get("protocol_hash"),
        "criteria": {
            "E5-P1": "positive membership-bit feature AUC_point >= 0.99 on eval",
            "E5-P2": "noise feature AUC_point in [0.45,0.55] and CI covers 0.50",
            "E5-P3": "offline on fixed sealed packet rows; no new training",
            "E5-P4": "labels faultinj-e5-* only",
        },
        "E5_positive_leak": {
            **pos,
            "criterion_E5_P1_pass": bool(e5_p1_pass),
        },
        "E5_pure_noise": {
            **noise,
            "criterion_E5_P2_pass": bool(e5_p2_pass),
        },
        "sealed_scalar_offline_lr_sanity_not_confirmatory": sealed_scalar,
        "assay_interpretation": {
            "both_pass": bool(e5_p1_pass and e5_p2_pass),
            "allowed_prose_if_both_pass": (
                "Sealed Stage-1/200k near-chance H1/PIA negatives are not explained "
                "by a totally dead scoring pipeline under this offline instrument assay."
            ),
            "forbidden_prose": [
                "weak membership recovery",
                "claim ceiling upgrade",
                "merge into main Results as confirmatory",
            ],
        },
        "elapsed_seconds": round(time.time() - t0, 3),
        "formal_hold": True,
        "claim_ceiling_unchanged": True,
    }

    raw = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    receipt["receipt_sha256"] = hashlib.sha256(raw).hexdigest()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / "faultinj_e5_receipt.json"
    out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out).replace("\\", "/"),
        "E5_P1_pass": e5_p1_pass,
        "E5_P2_pass": e5_p2_pass,
        "positive_auc": pos["auc_point"],
        "noise_auc": noise["auc_point"],
        "noise_ci": noise["auc_ci95"],
        "sha256": receipt["receipt_sha256"],
    }, indent=2))
    return 0 if (e5_p1_pass and e5_p2_pass) else 2


if __name__ == "__main__":
    raise SystemExit(main())
