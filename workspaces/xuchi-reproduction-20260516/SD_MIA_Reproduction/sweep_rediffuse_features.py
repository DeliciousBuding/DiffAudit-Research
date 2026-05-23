"""
Sweep simple two-step ReDiffuse feature combinations from a merged scores NPZ.

This is a cheap post-processing pass: it does not rerun Stable Diffusion.  It
searches deterministic scalar detectors built from the saved per-step features.
"""

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def low_score_metrics(member_scores: np.ndarray, nonmember_scores: np.ndarray) -> Dict[str, float]:
    y_true = np.concatenate(
        [np.ones(len(member_scores), dtype=np.int32), np.zeros(len(nonmember_scores), dtype=np.int32)]
    )
    low_scores = np.concatenate([member_scores, nonmember_scores]).astype(np.float64)
    confidence = -low_scores
    auc = float(metrics.roc_auc_score(y_true, confidence))
    fpr, tpr, _ = metrics.roc_curve(y_true, confidence)
    tpr_1fpr = float(tpr[np.argmin(np.abs(fpr - 0.01))])

    thresholds = np.unique(low_scores)
    best_asr = -1.0
    best_thr = float(thresholds[0])
    for thr in thresholds:
        tp = np.count_nonzero(member_scores <= thr)
        tn = np.count_nonzero(nonmember_scores > thr)
        asr = (tp + tn) / (len(member_scores) + len(nonmember_scores))
        if asr > best_asr:
            best_asr = float(asr)
            best_thr = float(thr)

    return {"auc": auc, "asr": best_asr, "tpr_1fpr": tpr_1fpr, "threshold": best_thr}


def scalar(data, key, default=None):
    if key not in data:
        return default
    value = np.asarray(data[key])
    if value.shape == ():
        return value.item()
    return value.tolist()


def candidates(member: np.ndarray, nonmember: np.ndarray, angle_steps: int) -> Iterable[Tuple[str, np.ndarray, np.ndarray, Dict[str, float]]]:
    simple = {
        "first": (member[:, 0], nonmember[:, 0], {}),
        "last": (member[:, -1], nonmember[:, -1], {}),
        "mean": (member.mean(axis=1), nonmember.mean(axis=1), {}),
        "min": (member.min(axis=1), nonmember.min(axis=1), {}),
        "max": (member.max(axis=1), nonmember.max(axis=1), {}),
        "median": (np.median(member, axis=1), np.median(nonmember, axis=1), {}),
    }
    for idx in range(member.shape[1]):
        simple[f"step{idx}"] = (member[:, idx], nonmember[:, idx], {})
    for name, (m_score, n_score, params) in simple.items():
        yield name, m_score, n_score, params

    if member.shape[1] == 2:
        m0, m1 = member[:, 0], member[:, 1]
        n0, n1 = nonmember[:, 0], nonmember[:, 1]
        extra = {
            "diff_s0_s1": (m0 - m1, n0 - n1, {}),
            "diff_s1_s0": (m1 - m0, n1 - n0, {}),
            "product": (m0 * m1, n0 * n1, {}),
            "ratio_s0_s1": (m0 / (m1 + 1e-9), n0 / (n1 + 1e-9), {}),
            "ratio_s1_s0": (m1 / (m0 + 1e-9), n1 / (n0 + 1e-9), {}),
        }
        for name, (m_score, n_score, params) in extra.items():
            yield name, m_score, n_score, params

        for theta in np.linspace(-np.pi, np.pi, angle_steps, endpoint=False):
            a = float(np.cos(theta))
            b = float(np.sin(theta))
            yield (
                f"linear_angle_{theta:.6f}",
                a * m0 + b * m1,
                a * n0 + b * n1,
                {"a": a, "b": b, "theta": float(theta)},
            )


def logistic_candidates(member: np.ndarray, nonmember: np.ndarray):
    x = np.vstack([member, nonmember])
    y = np.concatenate([np.ones(len(member), dtype=np.int32), np.zeros(len(nonmember), dtype=np.int32)])
    for c_value in [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0, 100.0]:
        clf = make_pipeline(
            StandardScaler(),
            LogisticRegression(C=c_value, penalty="l2", solver="liblinear", random_state=0),
        )
        clf.fit(x, y)
        confidence = clf.decision_function(x)
        lr = clf.named_steps["logisticregression"]
        scaler = clf.named_steps["standardscaler"]
        yield (
            f"logistic_l2_C{c_value:g}",
            confidence[: len(member)],
            confidence[len(member):],
            {
                "c": float(c_value),
                "coef": lr.coef_.reshape(-1).tolist(),
                "intercept": float(lr.intercept_[0]),
                "scaler_mean": scaler.mean_.tolist(),
                "scaler_scale": scaler.scale_.tolist(),
            },
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Sweep ReDiffuse feature combinations.")
    parser.add_argument("--scores-npz", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--angle-steps", type=int, default=1440)
    args = parser.parse_args()

    data = np.load(args.scores_npz, allow_pickle=True)
    member = data["member_features"].astype(np.float64)
    nonmember = data["nonmember_features"].astype(np.float64)
    if member.ndim != 2:
        raise SystemExit(f"expected 2D member_features, got {member.shape}")
    if nonmember.shape != member.shape:
        raise SystemExit(f"member/nonmember shape mismatch: {member.shape} vs {nonmember.shape}")

    rows: List[Dict[str, float]] = []
    best_payload = None
    all_candidates = list(candidates(member, nonmember, args.angle_steps))
    all_candidates.extend(logistic_candidates(member, nonmember))
    for name, mem_conf, non_conf, params in all_candidates:
        result = low_score_metrics(-mem_conf.astype(np.float32), -non_conf.astype(np.float32))
        row = {"feature_mode": name, **result, **params}
        rows.append(row)
        if best_payload is None or (row["auc"], row["asr"], row["tpr_1fpr"]) > (
            best_payload["auc"],
            best_payload["asr"],
            best_payload["tpr_1fpr"],
        ):
            best_payload = row

    rows.sort(key=lambda row: (row["auc"], row["asr"], row["tpr_1fpr"]), reverse=True)
    csv_path = Path(args.output_csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["feature_mode", "auc", "asr", "tpr_1fpr", "threshold", "a", "b", "theta", "c"]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    detector = {
        "dataset": str(scalar(data, "dataset", "laion5_blip")),
        "attacker_name": "ReDiffuse",
        "checkpoint": str(scalar(data, "checkpoint", "CompVis/stable-diffusion-v1-4")),
        "attack_num": int(scalar(data, "attack_num", member.shape[1])),
        "interval": int(scalar(data, "interval", 10)),
        "k": int(scalar(data, "k", 10)),
        "average": int(scalar(data, "average", 3)),
        "torch_dtype": str(scalar(data, "torch_dtype", "auto")),
        "rediffuse_scorer": str(scalar(data, "rediffuse_scorer", "vae_ssim")),
        "feature_mode": best_payload["feature_mode"],
        "auc": best_payload["auc"],
        "asr": best_payload["asr"],
        "tpr_1fpr": best_payload["tpr_1fpr"],
        "threshold": best_payload["threshold"],
        "linear_weights": {
            "step0": best_payload.get("a"),
            "step1": best_payload.get("b"),
            "theta": best_payload.get("theta"),
        },
        "logistic": {
            "c": best_payload.get("c"),
            "coef": best_payload.get("coef"),
            "intercept": best_payload.get("intercept"),
            "scaler_mean": best_payload.get("scaler_mean"),
            "scaler_scale": best_payload.get("scaler_scale"),
        },
        "decision_rule": "member_if_score_leq_threshold",
        "score_definition": "score = -feature_confidence; linear confidence = a*step0 + b*step1",
        "selection_source": str(Path(args.scores_npz)),
    }
    json_path = Path(args.output_json)
    json_path.write_text(json.dumps(detector, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[ok] evaluated {len(rows)} feature modes")
    print(
        f"[ok] best: {best_payload['feature_mode']} "
        f"AUC={best_payload['auc']:.4f} ASR={best_payload['asr']:.4f} "
        f"threshold={best_payload['threshold']:.6f}"
    )
    print(f"[ok] wrote ranking: {csv_path}")
    print(f"[ok] wrote detector: {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
