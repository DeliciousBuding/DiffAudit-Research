"""Shared numeric and evaluation metrics for attack surfaces."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve


def round6(value: float) -> float:
    return round(float(value), 6)


def rounded_array(values: list[float] | np.ndarray) -> np.ndarray:
    return np.asarray([round6(value) for value in np.asarray(values, dtype=float).tolist()], dtype=float)


def zscore(values: np.ndarray, *, zero_mode: str = "zeros") -> np.ndarray:
    std = float(values.std(ddof=0))
    if std == 0.0:
        if zero_mode == "centered":
            return values - float(values.mean())
        if zero_mode == "zeros":
            return np.zeros_like(values, dtype=float)
        raise ValueError(f"Unknown zero_mode: {zero_mode}")
    return (values - float(values.mean())) / std


def rankdata(values: np.ndarray) -> np.ndarray:
    """Return stable 0-indexed average ranks.

    Ties receive the average 0-indexed rank for their tie group. This preserves
    the historical helper behavior and intentionally differs from
    scipy.stats.rankdata's default 1-indexed output.
    """
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.shape[0], dtype=float)
    sorted_values = values[order]
    start = 0
    while start < len(sorted_values):
        end = start + 1
        while end < len(sorted_values) and sorted_values[end] == sorted_values[start]:
            end += 1
        average_rank = (start + end - 1) / 2.0
        ranks[order[start:end]] = average_rank
        start = end
    return ranks


def spearman(values_a: np.ndarray, values_b: np.ndarray) -> float:
    rank_a = rankdata(values_a)
    rank_b = rankdata(values_b)
    std_a = rank_a.std(ddof=0)
    std_b = rank_b.std(ddof=0)
    if std_a == 0.0 or std_b == 0.0:
        return 0.0
    corr = np.corrcoef(rank_a, rank_b)[0, 1]
    return float(corr)


def orient_member_nonmember(
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, str]:
    if float(member_scores.mean()) < float(nonmember_scores.mean()):
        return -member_scores, -nonmember_scores, "negated"
    return member_scores, nonmember_scores, "identity"


def orient_scores_by_labels(values: np.ndarray, labels: np.ndarray) -> np.ndarray:
    member_mean = float(values[labels == 1].mean())
    nonmember_mean = float(values[labels == 0].mean())
    if member_mean < nonmember_mean:
        return -values
    return values


def roc_curve_points(scores: np.ndarray, labels: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    order = np.argsort(-scores, kind="mergesort")
    scores_sorted = scores[order]
    labels_sorted = labels[order]
    positives = float(labels.sum())
    negatives = float(labels.shape[0] - labels.sum())
    tps = np.cumsum(labels_sorted == 1)
    fps = np.cumsum(labels_sorted == 0)
    distinct = np.r_[True, scores_sorted[1:] != scores_sorted[:-1]]
    tpr = np.r_[0.0, tps[distinct] / positives, 1.0]
    fpr = np.r_[0.0, fps[distinct] / negatives, 1.0]
    return fpr, tpr


def auc_score(scores: np.ndarray, labels: np.ndarray) -> float:
    fpr, tpr = roc_curve_points(scores, labels)
    return float(np.sum((fpr[1:] - fpr[:-1]) * (tpr[1:] + tpr[:-1]) * 0.5))


def accuracy_best_threshold(scores: np.ndarray, labels: np.ndarray) -> float:
    sorted_scores = np.sort(scores)
    thresholds = np.r_[
        sorted_scores[0] - 1e-6,
        (sorted_scores[:-1] + sorted_scores[1:]) / 2.0,
        sorted_scores[-1] + 1e-6,
    ]
    best = 0.0
    for threshold in thresholds:
        predictions = (scores >= threshold).astype(int)
        best = max(best, float((predictions == labels).mean()))
    return best


def tpr_at_fpr_from_curve(fpr: np.ndarray, tpr: np.ndarray, target_fpr: float) -> float:
    valid = tpr[fpr <= float(target_fpr)]
    if valid.size == 0:
        return 0.0
    return float(valid.max())


def tpr_at_fpr(scores: np.ndarray, labels: np.ndarray, target_fpr: float) -> float:
    fpr, tpr = roc_curve_points(scores, labels)
    return tpr_at_fpr_from_curve(fpr, tpr, target_fpr)


def metric_bundle(scores: np.ndarray, labels: np.ndarray) -> dict[str, float]:
    return {
        "auc": round6(auc_score(scores, labels)),
        "asr": round6(accuracy_best_threshold(scores, labels)),
        "tpr_at_1pct_fpr": round6(tpr_at_fpr(scores, labels, 0.01)),
        "tpr_at_0_1pct_fpr": round6(tpr_at_fpr(scores, labels, 0.001)),
    }


def threshold_metrics_grid(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    auc = float(roc_auc_score(labels, scores))
    fpr, tpr, _thresholds = roc_curve(labels, scores)
    tpr_at_1pct = tpr_at_fpr_from_curve(fpr, tpr, 0.01)

    best_asr = -1.0
    best_threshold = float(scores.min())
    best_tpr = 0.0
    best_fpr = 1.0
    for threshold in np.linspace(float(scores.min()), float(scores.max()), num=2000, endpoint=True):
        preds = (scores >= threshold).astype(np.int64)
        tp = float(((preds == 1) & (labels == 1)).sum())
        tn = float(((preds == 0) & (labels == 0)).sum())
        current_asr = (tp + tn) / float(len(labels))
        if current_asr > best_asr:
            best_asr = current_asr
            best_threshold = float(threshold)
            best_tpr = tp / max(float((labels == 1).sum()), 1.0)
            best_fpr = float(((preds == 1) & (labels == 0)).sum()) / max(float((labels == 0).sum()), 1.0)
    return {
        "auc": auc,
        "asr": float(best_asr),
        "tpr_at_1pct_fpr": float(tpr_at_1pct),
        "threshold": best_threshold,
        "best_tpr": best_tpr,
        "best_fpr": best_fpr,
    }
