"""Metrics for response-distribution stability across generation seeds."""

from __future__ import annotations

import math

import numpy as np
from sklearn.metrics import roc_auc_score


def mean_pairwise_cosine(embeddings: np.ndarray) -> float:
    """Return the mean cosine similarity over all unordered embedding pairs."""

    values = np.asarray(embeddings, dtype=float)
    if values.ndim != 2:
        raise ValueError("embeddings must be a 2D array")
    if values.shape[0] < 2:
        raise ValueError("at least two embeddings are required")

    norms = np.linalg.norm(values, axis=1, keepdims=True)
    normalized = np.divide(values, norms, out=np.zeros_like(values), where=norms != 0.0)
    pair_scores: list[float] = []
    for left in range(normalized.shape[0]):
        for right in range(left + 1, normalized.shape[0]):
            pair_scores.append(float(np.dot(normalized[left], normalized[right])))
    return float(np.mean(pair_scores))


def _best_asr(labels: np.ndarray, scores: np.ndarray) -> dict[str, float | int]:
    best: dict[str, float | int] = {
        "threshold": float(scores.max()) + 1.0,
        "tp": 0,
        "fp": 0,
        "tn": int((labels == 0).sum()),
        "fn": int((labels == 1).sum()),
        "asr": float((labels == 0).sum()) / float(labels.shape[0]),
    }
    for threshold in sorted({float(score) for score in scores}, reverse=True):
        preds = scores >= threshold
        tp = int(((preds == 1) & (labels == 1)).sum())
        fp = int(((preds == 1) & (labels == 0)).sum())
        tn = int(((preds == 0) & (labels == 0)).sum())
        fn = int(((preds == 0) & (labels == 1)).sum())
        asr = float(tp + tn) / float(labels.shape[0])
        if asr > float(best["asr"]):
            best = {
                "threshold": float(threshold),
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "asr": asr,
            }
    return best


def _tpr_at_fpr(labels: np.ndarray, scores: np.ndarray, max_fpr: float) -> dict[str, float | int | None]:
    nonmember_count = int((labels == 0).sum())
    member_count = int((labels == 1).sum())
    allowed_fp = int(math.floor(max_fpr * float(nonmember_count)))
    best: dict[str, float | int | None] = {
        "threshold": None,
        "tp": 0,
        "fp": 0,
        "allowed_fp": allowed_fp,
        "tpr": 0.0,
    }
    thresholds = [float(scores.max()) + 1.0] + sorted({float(score) for score in scores}, reverse=True)
    for threshold in thresholds:
        preds = scores >= threshold
        fp = int(((preds == 1) & (labels == 0)).sum())
        if fp > allowed_fp:
            continue
        tp = int(((preds == 1) & (labels == 1)).sum())
        tpr = float(tp) / max(float(member_count), 1.0)
        if tpr > float(best["tpr"]):
            best = {
                "threshold": float(threshold),
                "tp": tp,
                "fp": fp,
                "allowed_fp": allowed_fp,
                "tpr": tpr,
            }
    return best


def summarize_stability_scores(labels: np.ndarray, scores: np.ndarray) -> dict[str, float | dict[str, float | int | None]]:
    """Summarize higher-is-more-member stability scores."""

    label_values = np.asarray(labels, dtype=int)
    score_values = np.asarray(scores, dtype=float)
    if label_values.shape != score_values.shape:
        raise ValueError("labels and scores must have the same shape")
    if set(label_values.tolist()) != {0, 1}:
        raise ValueError("labels must contain both 0 and 1")

    tpr_1pct = _tpr_at_fpr(label_values, score_values, 0.01)
    tpr_0_1pct = _tpr_at_fpr(label_values, score_values, 0.001)
    best = _best_asr(label_values, score_values)
    return {
        "score_name": "clip_vit_l14_response_seed_stability_cosine",
        "score_direction": "higher_is_more_member",
        "auc": round(float(roc_auc_score(label_values, score_values)), 6),
        "asr": round(float(best["asr"]), 6),
        "best_threshold": best,
        "tpr_at_1pct_fpr": round(float(tpr_1pct["tpr"]), 6),
        "tpr_at_1pct_fpr_detail": tpr_1pct,
        "tpr_at_0_1pct_fpr": round(float(tpr_0_1pct["tpr"]), 6),
        "tpr_at_0_1pct_fpr_detail": tpr_0_1pct,
        "member_score_mean": round(float(score_values[label_values == 1].mean()), 6),
        "nonmember_score_mean": round(float(score_values[label_values == 0].mean()), 6),
    }
