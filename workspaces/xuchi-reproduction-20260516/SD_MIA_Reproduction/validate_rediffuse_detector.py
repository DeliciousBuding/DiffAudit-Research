"""
Validate ReDiffuse detectors with held-out splits and cross validation.

This script uses the saved per-step features from attack.py. It does not rerun
Stable Diffusion. Candidate score rules are selected on a validation split, and
the reported test metrics are computed on held-out samples only.
"""

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def classifier_metrics(
    member_conf: np.ndarray,
    nonmember_conf: np.ndarray,
    threshold_conf: Optional[float] = None,
) -> Dict[str, float]:
    y_true = np.concatenate(
        [np.ones(len(member_conf), dtype=np.int32), np.zeros(len(nonmember_conf), dtype=np.int32)]
    )
    conf = np.concatenate([member_conf, nonmember_conf]).astype(np.float64)
    auc = float(metrics.roc_auc_score(y_true, conf))
    fpr, tpr, _ = metrics.roc_curve(y_true, conf)
    tpr_1fpr = float(tpr[np.argmin(np.abs(fpr - 0.01))])

    if threshold_conf is None:
        thresholds = np.unique(conf)
        best_asr = -1.0
        best_thr = float(thresholds[0])
        for thr in thresholds:
            tp = np.count_nonzero(member_conf >= thr)
            tn = np.count_nonzero(nonmember_conf < thr)
            asr = (tp + tn) / (len(member_conf) + len(nonmember_conf))
            if asr > best_asr:
                best_asr = float(asr)
                best_thr = float(thr)
        threshold_conf = best_thr
        asr = best_asr
    else:
        tp = np.count_nonzero(member_conf >= threshold_conf)
        tn = np.count_nonzero(nonmember_conf < threshold_conf)
        asr = float((tp + tn) / (len(member_conf) + len(nonmember_conf)))

    return {
        "auc": auc,
        "asr": asr,
        "tpr_1fpr": tpr_1fpr,
        "threshold_confidence": float(threshold_conf),
        "threshold_score": float(-threshold_conf),
    }


def feature_candidates(features: np.ndarray, angle_steps: int) -> Iterable[Tuple[str, np.ndarray, Dict[str, float]]]:
    if features.ndim != 2:
        raise ValueError(f"expected 2D features, got {features.shape}")

    n_steps = features.shape[1]
    simple = {
        "first": features[:, 0],
        "last": features[:, -1],
        "mean": features.mean(axis=1),
        "median": np.median(features, axis=1),
        "min": features.min(axis=1),
        "max": features.max(axis=1),
    }
    for idx in range(n_steps):
        simple[f"step{idx}"] = features[:, idx]

    for name, conf in simple.items():
        yield name, conf, {}

    if n_steps == 2:
        s0 = features[:, 0]
        s1 = features[:, 1]
        extra = {
            "diff_s0_s1": s0 - s1,
            "diff_s1_s0": s1 - s0,
            "product": s0 * s1,
            "ratio_s0_s1": s0 / (s1 + 1e-9),
            "ratio_s1_s0": s1 / (s0 + 1e-9),
        }
        for name, conf in extra.items():
            yield name, conf, {}

        for theta in np.linspace(-np.pi, np.pi, angle_steps, endpoint=False):
            a = float(np.cos(theta))
            b = float(np.sin(theta))
            yield (
                f"linear_angle_{theta:.6f}",
                a * s0 + b * s1,
                {"a": a, "b": b, "theta": float(theta)},
            )


def select_fixed_rule(
    member: np.ndarray,
    nonmember: np.ndarray,
    train_idx: np.ndarray,
    val_idx: np.ndarray,
    test_idx: np.ndarray,
    angle_steps: int,
) -> Dict[str, float]:
    all_features = np.vstack([member, nonmember])
    n_member = len(member)
    best = None

    for mode, conf_all, params in feature_candidates(all_features, angle_steps):
        mem_conf = conf_all[:n_member]
        non_conf = conf_all[n_member:]
        val_metrics = classifier_metrics(mem_conf[val_idx], non_conf[val_idx])
        row = {"feature_mode": mode, "val_metrics": val_metrics, "params": params}
        key = (val_metrics["auc"], val_metrics["asr"], val_metrics["tpr_1fpr"])
        if best is None or key > best["key"]:
            row["key"] = key
            best = row

    mode, params = best["feature_mode"], best["params"]
    for cand_mode, conf_all, cand_params in feature_candidates(all_features, angle_steps):
        if cand_mode == mode and cand_params == params:
            mem_conf = conf_all[:n_member]
            non_conf = conf_all[n_member:]
            break
    else:
        raise RuntimeError("selected fixed rule could not be reconstructed")

    train_metrics = classifier_metrics(mem_conf[train_idx], non_conf[train_idx])
    val_metrics = best["val_metrics"]
    test_metrics = classifier_metrics(
        mem_conf[test_idx],
        non_conf[test_idx],
        threshold_conf=val_metrics["threshold_confidence"],
    )

    return {
        "method": "fixed_rule_sweep",
        "feature_mode": mode,
        **params,
        "train_auc": train_metrics["auc"],
        "train_asr": train_metrics["asr"],
        "val_auc": val_metrics["auc"],
        "val_asr": val_metrics["asr"],
        "val_tpr_1fpr": val_metrics["tpr_1fpr"],
        "test_auc": test_metrics["auc"],
        "test_asr": test_metrics["asr"],
        "test_tpr_1fpr": test_metrics["tpr_1fpr"],
        "threshold_confidence": val_metrics["threshold_confidence"],
        "threshold_score": val_metrics["threshold_score"],
    }


def make_xy(member: np.ndarray, nonmember: np.ndarray, indices: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    x = np.vstack([member[indices], nonmember[indices]])
    y = np.concatenate([np.ones(len(indices), dtype=np.int32), np.zeros(len(indices), dtype=np.int32)])
    return x, y


def select_logistic(
    member: np.ndarray,
    nonmember: np.ndarray,
    train_idx: np.ndarray,
    val_idx: np.ndarray,
    test_idx: np.ndarray,
) -> Dict[str, float]:
    x_train, y_train = make_xy(member, nonmember, train_idx)
    x_val, _ = make_xy(member, nonmember, val_idx)
    c_values = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0]
    best = None

    for c_value in c_values:
        clf = make_pipeline(
            StandardScaler(),
            LogisticRegression(C=c_value, penalty="l2", solver="liblinear", random_state=0),
        )
        clf.fit(x_train, y_train)
        val_conf_all = clf.decision_function(x_val)
        val_member = val_conf_all[: len(val_idx)]
        val_nonmember = val_conf_all[len(val_idx):]
        val_metrics = classifier_metrics(val_member, val_nonmember)
        row = {"clf": clf, "c": c_value, "val_metrics": val_metrics}
        key = (val_metrics["auc"], val_metrics["asr"], val_metrics["tpr_1fpr"])
        if best is None or key > best["key"]:
            row["key"] = key
            best = row

    clf = best["clf"]
    train_conf_all = clf.decision_function(x_train)
    val_metrics = best["val_metrics"]
    x_test, _ = make_xy(member, nonmember, test_idx)
    test_conf_all = clf.decision_function(x_test)
    train_metrics = classifier_metrics(train_conf_all[: len(train_idx)], train_conf_all[len(train_idx):])
    test_metrics = classifier_metrics(
        test_conf_all[: len(test_idx)],
        test_conf_all[len(test_idx):],
        threshold_conf=val_metrics["threshold_confidence"],
    )

    final_lr = clf.named_steps["logisticregression"]
    scaler = clf.named_steps["standardscaler"]
    return {
        "method": "logistic_l2",
        "feature_mode": "all_steps",
        "c": best["c"],
        "train_auc": train_metrics["auc"],
        "train_asr": train_metrics["asr"],
        "val_auc": val_metrics["auc"],
        "val_asr": val_metrics["asr"],
        "val_tpr_1fpr": val_metrics["tpr_1fpr"],
        "test_auc": test_metrics["auc"],
        "test_asr": test_metrics["asr"],
        "test_tpr_1fpr": test_metrics["tpr_1fpr"],
        "threshold_confidence": val_metrics["threshold_confidence"],
        "threshold_score": val_metrics["threshold_score"],
        "coef": final_lr.coef_.reshape(-1).tolist(),
        "intercept": float(final_lr.intercept_[0]),
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
    }


def split_indices(n: int, seed: int, train_frac: float, val_frac: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    train_end = int(round(n * train_frac))
    val_end = train_end + int(round(n * val_frac))
    return perm[:train_end], perm[train_end:val_end], perm[val_end:]


def cross_validation_indices(n: int, seed: int, folds: int) -> Iterable[Tuple[int, np.ndarray, np.ndarray, np.ndarray]]:
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    fold_parts = np.array_split(perm, folds)
    for fold_id, test_idx in enumerate(fold_parts):
        remain = np.concatenate([part for idx, part in enumerate(fold_parts) if idx != fold_id])
        remain = rng.permutation(remain)
        val_size = max(1, len(remain) // (folds - 1))
        val_idx = remain[:val_size]
        train_idx = remain[val_size:]
        yield fold_id, train_idx, val_idx, test_idx


def summarize(rows: List[Dict[str, float]], method: str) -> Dict[str, float]:
    selected = [row for row in rows if row["split_kind"] == "cv" and row["method"] == method]
    values = np.asarray([row["test_auc"] for row in selected], dtype=np.float64)
    return {
        "method": method,
        "folds": int(len(values)),
        "mean_test_auc": float(values.mean()),
        "std_test_auc": float(values.std(ddof=1)) if len(values) > 1 else 0.0,
        "min_test_auc": float(values.min()),
        "max_test_auc": float(values.max()),
    }


def json_default(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Held-out validation for saved ReDiffuse features.")
    parser.add_argument("--scores-npz", required=True)
    parser.add_argument("--output-csv", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--train-frac", type=float, default=0.6)
    parser.add_argument("--val-frac", type=float, default=0.2)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--angle-steps", type=int, default=1440)
    args = parser.parse_args()

    data = np.load(args.scores_npz, allow_pickle=True)
    member = data["member_features"].astype(np.float64)
    nonmember = data["nonmember_features"].astype(np.float64)
    if member.shape != nonmember.shape:
        raise SystemExit(f"member/nonmember shape mismatch: {member.shape} vs {nonmember.shape}")

    rows: List[Dict[str, float]] = []
    train_idx, val_idx, test_idx = split_indices(len(member), args.seed, args.train_frac, args.val_frac)
    for selector in (select_fixed_rule, select_logistic):
        if selector is select_fixed_rule:
            row = selector(member, nonmember, train_idx, val_idx, test_idx, args.angle_steps)
        else:
            row = selector(member, nonmember, train_idx, val_idx, test_idx)
        row.update({"split_kind": "holdout", "fold": -1, "train_n": len(train_idx), "val_n": len(val_idx), "test_n": len(test_idx)})
        rows.append(row)

    for fold_id, fold_train, fold_val, fold_test in cross_validation_indices(len(member), args.seed, args.folds):
        for selector in (select_fixed_rule, select_logistic):
            if selector is select_fixed_rule:
                row = selector(member, nonmember, fold_train, fold_val, fold_test, args.angle_steps)
            else:
                row = selector(member, nonmember, fold_train, fold_val, fold_test)
            row.update(
                {
                    "split_kind": "cv",
                    "fold": fold_id,
                    "train_n": len(fold_train),
                    "val_n": len(fold_val),
                    "test_n": len(fold_test),
                }
            )
            rows.append(row)

    csv_path = Path(args.output_csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "split_kind",
        "fold",
        "method",
        "feature_mode",
        "train_n",
        "val_n",
        "test_n",
        "train_auc",
        "train_asr",
        "val_auc",
        "val_asr",
        "val_tpr_1fpr",
        "test_auc",
        "test_asr",
        "test_tpr_1fpr",
        "threshold_confidence",
        "threshold_score",
        "a",
        "b",
        "theta",
        "c",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "scores_npz": str(Path(args.scores_npz)),
        "shape": {"member_features": list(member.shape), "nonmember_features": list(nonmember.shape)},
        "seed": args.seed,
        "holdout": [row for row in rows if row["split_kind"] == "holdout"],
        "cv_summary": [
            summarize(rows, "fixed_rule_sweep"),
            summarize(rows, "logistic_l2"),
        ],
        "cv_rows": [row for row in rows if row["split_kind"] == "cv"],
    }
    json_path = Path(args.output_json)
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")

    print(f"[ok] wrote rows: {csv_path}")
    print(f"[ok] wrote summary: {json_path}")
    for row in summary["holdout"]:
        print(
            f"[holdout] {row['method']} mode={row['feature_mode']} "
            f"val_auc={row['val_auc']:.4f} test_auc={row['test_auc']:.4f} test_asr={row['test_asr']:.4f}"
        )
    for row in summary["cv_summary"]:
        print(
            f"[cv] {row['method']} mean_auc={row['mean_test_auc']:.4f} "
            f"std={row['std_test_auc']:.4f} min={row['min_test_auc']:.4f} max={row['max_test_auc']:.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
