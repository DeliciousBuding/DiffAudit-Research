from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from diffaudit.utils.metrics import orient_scores_by_labels as _orient_memberness
from diffaudit.utils.metrics import rankdata as _rankdata
from diffaudit.utils.metrics import spearman as _spearman
from diffaudit.utils.metrics import threshold_metrics_grid as _threshold_metrics
from diffaudit.utils.metrics import zscore as _shared_zscore


def load_semantic_aux_records(path: str | Path) -> list[dict[str, object]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("semantic-aux records payload must be a list")
    return payload


def _zscore(values: np.ndarray) -> np.ndarray:
    return _shared_zscore(values, zero_mode="centered")


def analyze_semantic_aux_fusion(records: list[dict[str, object]]) -> dict[str, object]:
    labels = np.asarray([int(row["label"]) for row in records], dtype=int)
    mean_cos = np.asarray([float(row["mean_cos"]) for row in records], dtype=float)
    max_cos = np.asarray([float(row["max_cos"]) for row in records], dtype=float)
    max_ssim = np.asarray([float(row["max_ssim"]) for row in records], dtype=float)

    oriented_mean_cos = _orient_memberness(mean_cos, labels)
    oriented_max_cos = _orient_memberness(max_cos, labels)
    oriented_max_ssim = _orient_memberness(max_ssim, labels)

    candidate_scores = {
        "mean_cos": oriented_mean_cos,
        "max_cos": oriented_max_cos,
        "cosine_pair_zmean": (_zscore(oriented_mean_cos) + _zscore(oriented_max_cos)) / 2.0,
        "cosine_ssim_triplet_zmean": (
            _zscore(oriented_mean_cos) + _zscore(oriented_max_cos) + _zscore(oriented_max_ssim)
        )
        / 3.0,
        "cosine_ssim_rank_fusion": (
            _rankdata(oriented_mean_cos) + _rankdata(oriented_max_cos) + _rankdata(oriented_max_ssim)
        )
        / 3.0,
    }

    candidates: dict[str, dict[str, float]] = {}
    for name, scores in candidate_scores.items():
        metrics = _threshold_metrics(labels, scores)
        metrics["spearman_vs_mean_cos"] = (
            1.0 if name == "mean_cos" else _spearman(candidate_scores["mean_cos"], scores)
        )
        candidates[name] = {key: round(float(value), 6) for key, value in metrics.items()}

    ranked = sorted(
        (
            {
                "name": name,
                "auc": payload["auc"],
                "asr": payload["asr"],
                "spearman_vs_mean_cos": payload["spearman_vs_mean_cos"],
            }
            for name, payload in candidates.items()
        ),
        key=lambda item: (item["auc"], item["asr"]),
        reverse=True,
    )
    best = ranked[0]
    mean_cos_auc = candidates["mean_cos"]["auc"]
    best_auc_gain = round(float(best["auc"] - mean_cos_auc), 6)
    return {
        "sample_count": int(labels.shape[0]),
        "member_rows": int((labels == 1).sum()),
        "nonmember_rows": int((labels == 0).sum()),
        "candidates": candidates,
        "ranked_candidates": ranked,
        "best_candidate": best["name"],
        "best_auc_gain_vs_mean_cos": best_auc_gain,
    }
