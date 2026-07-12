"""Shared numeric and evaluation metrics for attack surfaces."""

from __future__ import annotations

import math
from statistics import NormalDist

import numpy as np


def round6(value: float) -> float:
    return round(float(value), 6)


def rounded_array(values: list[float] | np.ndarray) -> np.ndarray:
    return np.asarray(
        [round6(value) for value in np.asarray(values, dtype=float).tolist()], dtype=float
    )


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


def _require_binary_labels(labels: np.ndarray) -> None:
    if int((labels == 1).sum()) == 0 or int((labels == 0).sum()) == 0:
        raise ValueError("labels must contain at least one member (1) and one nonmember (0)")


def orient_member_nonmember(
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, str]:
    if float(member_scores.mean()) < float(nonmember_scores.mean()):
        return -member_scores, -nonmember_scores, "negated"
    return member_scores, nonmember_scores, "identity"


def orient_scores_by_labels(values: np.ndarray, labels: np.ndarray) -> np.ndarray:
    _require_binary_labels(labels)
    member_mean = float(values[labels == 1].mean())
    nonmember_mean = float(values[labels == 0].mean())
    if member_mean < nonmember_mean:
        return -values
    return values


def roc_curve_points(scores: np.ndarray, labels: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    _require_binary_labels(labels)
    order = np.argsort(-scores, kind="mergesort")
    scores_sorted = scores[order]
    labels_sorted = labels[order]
    positives = float(labels.sum())
    negatives = float(labels.shape[0] - labels.sum())
    tps = np.cumsum(labels_sorted == 1)
    fps = np.cumsum(labels_sorted == 0)
    group_ends = np.r_[scores_sorted[:-1] != scores_sorted[1:], True]
    tpr = np.r_[0.0, tps[group_ends] / positives]
    fpr = np.r_[0.0, fps[group_ends] / negatives]
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


def wilson_interval(
    successes: int,
    total: int,
    *,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Return a two-sided Wilson score interval for a binomial proportion."""

    if type(successes) is not int or type(total) is not int:
        raise ValueError("successes and total must be integers")
    if total <= 0 or not 0 <= successes <= total:
        raise ValueError("Wilson counts must satisfy 0 <= successes <= total and total > 0")
    if type(confidence) is not float or not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be a float strictly between zero and one")
    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    proportion = successes / total
    denominator = 1.0 + z * z / total
    center = (proportion + z * z / (2.0 * total)) / denominator
    radius = (
        z
        * math.sqrt(proportion * (1.0 - proportion) / total + z * z / (4.0 * total * total))
        / denominator
    )
    lower = max(0.0, center - radius)
    upper = min(1.0, center + radius)
    if successes == 0:
        lower = 0.0
    if successes == total:
        upper = 1.0
    return float(lower), float(upper)


def tpr_at_fpr_with_wilson(
    scores: np.ndarray,
    labels: np.ndarray,
    *,
    target_fpr: float = 0.01,
) -> dict[str, object]:
    """Return a tie-safe empirical TPR at an FPR cap and its Wilson interval."""

    score_values = np.asarray(scores, dtype=float)
    label_values = np.asarray(labels, dtype=np.int64)
    if score_values.ndim != 1 or label_values.shape != score_values.shape:
        raise ValueError("scores and labels must be matching vectors")
    if not np.isfinite(score_values).all():
        raise ValueError("scores must contain only finite values")
    _require_binary_labels(label_values)
    estimate = tpr_at_fpr(score_values, label_values, target_fpr)
    positives = int((label_values == 1).sum())
    raw_successes = estimate * positives
    successes = int(round(raw_successes))
    if not math.isclose(raw_successes, successes, rel_tol=0.0, abs_tol=1e-9):
        raise RuntimeError("TPR helper returned a value that is not an exact empirical count")
    lower, upper = wilson_interval(successes, positives)
    return {
        "estimate": float(estimate),
        "wilson_95_ci": [lower, upper],
        "member_successes": successes,
        "member_total": positives,
        "fpr_cap": float(target_fpr),
    }


def metric_bundle(scores: np.ndarray, labels: np.ndarray) -> dict[str, float]:
    return {
        "auc": round6(auc_score(scores, labels)),
        "asr": round6(accuracy_best_threshold(scores, labels)),
        "tpr_at_1pct_fpr": round6(tpr_at_fpr(scores, labels, 0.01)),
        "tpr_at_0_1pct_fpr": round6(tpr_at_fpr(scores, labels, 0.001)),
    }


def threshold_metrics_grid(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    from sklearn.metrics import roc_auc_score, roc_curve

    _require_binary_labels(labels)
    auc = float(roc_auc_score(labels, scores))
    fpr, tpr, _thresholds = roc_curve(labels, scores)
    tpr_at_1pct = tpr_at_fpr_from_curve(fpr, tpr, 0.01)
    tpr_at_0_1pct = tpr_at_fpr_from_curve(fpr, tpr, 0.001)

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
            best_fpr = float(((preds == 1) & (labels == 0)).sum()) / max(
                float((labels == 0).sum()), 1.0
            )
    return {
        "auc": auc,
        "asr": float(best_asr),
        "tpr_at_1pct_fpr": float(tpr_at_1pct),
        "tpr_at_0_1pct_fpr": float(tpr_at_0_1pct),
        "threshold": best_threshold,
        "best_tpr": best_tpr,
        "best_fpr": best_fpr,
    }
