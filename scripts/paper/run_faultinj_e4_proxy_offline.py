#!/usr/bin/env python3
"""faultinj-e4 offline PROXY: invalid membership labels on sealed features.

This is NOT the full short-train E4 micro-demo. It tests whether polluted
membership labels alone can lift held-out H1-like LR AUC relative to correct
labels on the same sealed feature matrix.

Labels: faultinj-e4-*-proxy. Exploratory only.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def fit_auc(X_cal, y_cal, X_eval, y_eval) -> float:
    clf = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=2000, solver="lbfgs", random_state=0),
    )
    clf.fit(X_cal, y_cal)
    scores = clf.decision_function(X_eval)
    return float(roc_auc_score(y_eval, scores))


def main() -> int:
    packet = Path(
        "outputs/paper1-corrected-evidence/h1-packets/"
        "corrected-s1746574482-step100000"
    )
    man = json.loads((packet / "manifest.json").read_text(encoding="utf-8"))
    z = np.load(packet / "features.npz")
    rows = man["rows"]
    y_true = np.array([int(r["label"]) for r in rows], dtype=int)
    split = np.array([r["calibration_or_evaluation"] for r in rows])
    idx = np.array([int(r["dataset_index"]) for r in rows])
    cal = split == "calibration"
    ev = split == "evaluation"
    X = z["scalar_features"]

    # Invalid GT: flip half of true members to nonmember by dataset_index parity.
    y_invalid = y_true.copy()
    member_mask = y_true == 1
    y_invalid[member_mask & (idx % 2 == 0)] = 0

    auc_correct = fit_auc(X[cal], y_true[cal], X[ev], y_true[ev])
    auc_invalid = fit_auc(X[cal], y_invalid[cal], X[ev], y_invalid[ev])

    rng = np.random.default_rng(20260718)
    deltas = []
    Xc, Xe = X[cal], X[ev]
    yt_c, yi_c = y_true[cal], y_invalid[cal]
    yt_e, yi_e = y_true[ev], y_invalid[ev]
    for _ in range(200):
        b = rng.integers(0, len(yt_e), size=len(yt_e))
        if len(np.unique(yt_e[b])) < 2 or len(np.unique(yi_e[b])) < 2:
            continue
        a_t = fit_auc(Xc, yt_c, Xe[b], yt_e[b])
        a_i = fit_auc(Xc, yi_c, Xe[b], yi_e[b])
        deltas.append(a_i - a_t)
    if deltas:
        lo_f, hi_f = np.quantile(np.asarray(deltas, dtype=float), [0.025, 0.975])
        lo, hi = float(lo_f), float(hi_f)
    else:
        lo, hi = float("nan"), float("nan")

    receipt = {
        "protocol_label": "faultinj-e4-offline-invalid-label-proxy-2026-07-18",
        "evidence_class": "exploratory_non_confirmatory",
        "note": (
            "PROXY offline assay: invalid membership labels on sealed features "
            "(not full-train micro model). Full short-train E4 may still run on GPU."
        ),
        "run_labels": [
            "faultinj-e4-invalid-gt-proxy",
            "faultinj-e4-member-only-control-proxy",
        ],
        "created_at_unix": int(time.time()),
        "packet": str(packet).as_posix() if False else str(packet).replace("\\", "/"),
        "auc_correct_labels_heldout": auc_correct,
        "auc_invalid_labels_heldout": auc_invalid,
        "delta_invalid_minus_correct": auc_invalid - auc_correct,
        "delta_boot_ci95_eval_resample": [lo, hi],
        "E4_P3_style_gate_invalid_ge_0.55_and_control_not": bool(
            auc_invalid >= 0.55 and auc_correct < 0.55
        ),
        "formal_hold": True,
        "claim_ceiling_unchanged": True,
    }
    raw = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
    receipt["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    out = Path(
        "outputs/paper1-corrected-evidence/fault-injection/faultinj_e4_proxy_receipt.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "wrote": str(out).replace("\\", "/"),
                "auc_correct": auc_correct,
                "auc_invalid": auc_invalid,
                "delta": auc_invalid - auc_correct,
                "E4_P3_style": receipt["E4_P3_style_gate_invalid_ge_0.55_and_control_not"],
                "sha256": receipt["receipt_sha256"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
