"""
Select the best ReDiffuse scorer from saved per-step SSIM features.

Input is the scores NPZ produced by attack.py --scores_npz.  The selector does
not rerun Stable Diffusion; it evaluates cheap scalar aggregations over the
saved [N, steps] features and exports a detector config for the best AUC.
"""

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
from sklearn import metrics


def _as_scalar(value, default=None):
    if value is None:
        return default
    arr = np.asarray(value)
    if arr.shape == ():
        return arr.item()
    return arr.tolist()


def aggregate(features: np.ndarray, mode: str) -> np.ndarray:
    if features.ndim == 1:
        features = features.reshape(-1, 1)
    if mode == "first":
        return features[:, 0]
    if mode == "last":
        return features[:, -1]
    if mode == "mean":
        return features.mean(axis=1)
    if mode == "median":
        return np.median(features, axis=1)
    if mode == "max":
        return features.max(axis=1)
    if mode == "min":
        return features.min(axis=1)
    if mode.startswith("step"):
        idx = int(mode[4:])
        return features[:, idx]
    raise ValueError(f"unknown mode: {mode}")


def low_score_metrics(member_scores: np.ndarray, nonmember_scores: np.ndarray) -> Dict[str, float]:
    """
    Scores are low-is-member.  AUC is computed on the equivalent high-is-member
    confidence so sklearn's positive label convention is natural.
    """
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

    return {
        "auc": auc,
        "asr": best_asr,
        "tpr_1fpr": tpr_1fpr,
        "threshold": best_thr,
    }


def candidate_modes(n_steps: int, requested: str) -> List[str]:
    if requested.strip():
        return [m.strip() for m in requested.split(",") if m.strip()]
    modes = ["first", "last", "mean", "median", "max", "min"]
    modes.extend(f"step{i}" for i in range(n_steps))
    return list(dict.fromkeys(modes))


def evaluate(member_features: np.ndarray, nonmember_features: np.ndarray, modes: Iterable[str]):
    rows: List[Dict[str, float]] = []
    for mode in modes:
        mem_sim = aggregate(member_features, mode)
        non_sim = aggregate(nonmember_features, mode)
        result = low_score_metrics(-mem_sim, -non_sim)
        rows.append({"score_mode": mode, **result})
    rows.sort(key=lambda row: (row["auc"], row["asr"], row["tpr_1fpr"]), reverse=True)
    return rows


def write_csv(path: Path, rows: List[Dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["score_mode", "auc", "asr", "tpr_1fpr", "threshold"],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Select best ReDiffuse detector from saved scores.")
    parser.add_argument("--scores-npz", required=True)
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-csv", default="")
    parser.add_argument("--modes", default="", help="Comma-separated modes; default evaluates all simple modes.")
    parser.add_argument("--checkpoint", default="")
    args = parser.parse_args()

    npz_path = Path(args.scores_npz)
    data = np.load(npz_path, allow_pickle=True)
    member_features = data["member_features"].astype(np.float32)
    nonmember_features = data["nonmember_features"].astype(np.float32)
    modes = candidate_modes(member_features.shape[1], args.modes)
    rows = evaluate(member_features, nonmember_features, modes)
    best = rows[0]

    out_csv = Path(args.output_csv) if args.output_csv else npz_path.with_name("rediffuse_score_selection.csv")
    write_csv(out_csv, rows)

    checkpoint = args.checkpoint or str(_as_scalar(data.get("checkpoint"), "CompVis/stable-diffusion-v1-4"))
    detector = {
        "dataset": str(_as_scalar(data.get("dataset"), "laion5")),
        "attacker_name": "ReDiffuse",
        "checkpoint": checkpoint,
        "attack_num": int(_as_scalar(data.get("attack_num"), member_features.shape[1])),
        "interval": int(_as_scalar(data.get("interval"), 10)),
        "k": int(_as_scalar(data.get("k"), 10)),
        "average": int(_as_scalar(data.get("average"), 10)),
        "torch_dtype": str(_as_scalar(data.get("torch_dtype"), "auto")),
        "score_mode": best["score_mode"],
        "rediffuse_scorer": str(_as_scalar(data.get("rediffuse_scorer"), "unknown")),
        "auc": best["auc"],
        "asr": best["asr"],
        "tpr_1fpr": best["tpr_1fpr"],
        "threshold": best["threshold"],
        "decision_rule": "member_if_score_leq_threshold",
        "score_definition": "ReDiffuse: -aggregate(saved per-step member-likeness feature)",
        "selection_source": str(npz_path),
    }

    out_json = Path(args.output_json) if args.output_json else npz_path.with_name("mia_detector_rediffuse_best.json")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(detector, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[ok] evaluated {len(rows)} score modes")
    print(f"[ok] best: {best['score_mode']} AUC={best['auc']:.4f} ASR={best['asr']:.4f} threshold={best['threshold']:.6f}")
    print(f"[ok] wrote ranking: {out_csv}")
    print(f"[ok] wrote detector: {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
