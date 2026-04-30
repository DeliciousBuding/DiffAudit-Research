"""Prompt-text-only review for CLiD candidate packets."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

from diffaudit.attacks.clid import _auc_member_low, _search_threshold


TOKEN_RE = re.compile(r"[a-z0-9]+")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.strip():
            row = json.loads(raw_line)
            if not isinstance(row, dict):
                raise ValueError(f"Expected JSON object row at {path}")
            rows.append(row)
    return rows


def _tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def _build_vocabulary(texts: list[str], *, min_count: int, max_features: int) -> list[str]:
    counts: Counter[str] = Counter()
    for text in texts:
        counts.update(set(_tokenize(text)))
    candidates = [
        (token, count)
        for token, count in counts.items()
        if count >= min_count
    ]
    candidates.sort(key=lambda item: (-item[1], item[0]))
    return [token for token, _ in candidates[:max_features]]


def _vectorize(texts: list[str], vocabulary: list[str]) -> np.ndarray:
    index = {token: offset for offset, token in enumerate(vocabulary)}
    matrix = np.zeros((len(texts), len(vocabulary)), dtype=float)
    for row, text in enumerate(texts):
        tokens = set(_tokenize(text))
        for token in tokens:
            column = index.get(token)
            if column is not None:
                matrix[row, column] = 1.0
    return matrix


def _safe_centroid(matrix: np.ndarray) -> np.ndarray:
    if matrix.shape[0] == 0:
        return np.zeros(matrix.shape[1], dtype=float)
    return matrix.mean(axis=0)


def _centroid_scores(member_vectors: np.ndarray, nonmember_vectors: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    member_centroid = _safe_centroid(member_vectors)
    nonmember_centroid = _safe_centroid(nonmember_vectors)
    member_scores: list[float] = []
    nonmember_scores: list[float] = []
    for vector in member_vectors:
        member_scores.append(float(np.linalg.norm(vector - nonmember_centroid) - np.linalg.norm(vector - member_centroid)))
    for vector in nonmember_vectors:
        nonmember_scores.append(float(np.linalg.norm(vector - nonmember_centroid) - np.linalg.norm(vector - member_centroid)))
    return np.asarray(member_scores, dtype=float), np.asarray(nonmember_scores, dtype=float)


def _best_oriented_metrics(member_scores: np.ndarray, nonmember_scores: np.ndarray) -> dict[str, float | str]:
    low_metrics = _search_threshold(member_scores, nonmember_scores)
    high_metrics = _search_threshold(-member_scores, -nonmember_scores)
    if float(high_metrics["auc"]) > float(low_metrics["auc"]):
        metrics = dict(high_metrics)
        metrics["orientation"] = "member_high"
        return metrics
    metrics = dict(low_metrics)
    metrics["orientation"] = "member_low"
    return metrics


def _auc_best_orientation(member_values: np.ndarray, nonmember_values: np.ndarray) -> float:
    low = _auc_member_low(member_values, nonmember_values)
    return float(max(low, 1.0 - low))


def review_clid_prompt_text_only(
    run_root: str | Path,
    *,
    min_count: int = 2,
    max_features: int = 256,
) -> dict[str, Any]:
    """Review whether CLiD split membership is separable from prompt text alone."""

    root = Path(run_root)
    member_rows = _read_jsonl(root / "datasets" / "member" / "metadata.jsonl")
    nonmember_rows = _read_jsonl(root / "datasets" / "nonmember" / "metadata.jsonl")
    member_texts = [str(row.get("text", "")) for row in member_rows]
    nonmember_texts = [str(row.get("text", "")) for row in nonmember_rows]
    all_texts = member_texts + nonmember_texts

    vocabulary = _build_vocabulary(all_texts, min_count=min_count, max_features=max_features)
    if not vocabulary:
        member_scores = np.zeros(len(member_texts), dtype=float)
        nonmember_scores = np.zeros(len(nonmember_texts), dtype=float)
    else:
        member_vectors = _vectorize(member_texts, vocabulary)
        nonmember_vectors = _vectorize(nonmember_texts, vocabulary)
        member_scores, nonmember_scores = _centroid_scores(member_vectors, nonmember_vectors)

    metrics = _best_oriented_metrics(member_scores, nonmember_scores)
    text_length_auc = _auc_best_orientation(
        np.asarray([len(text) for text in member_texts], dtype=float),
        np.asarray([len(text) for text in nonmember_texts], dtype=float),
    )
    token_count_auc = _auc_best_orientation(
        np.asarray([len(_tokenize(text)) for text in member_texts], dtype=float),
        np.asarray([len(_tokenize(text)) for text in nonmember_texts], dtype=float),
    )
    prompt_overlap = len(set(member_texts) & set(nonmember_texts))
    status = "ready"
    if len(member_texts) != len(nonmember_texts) or len(member_texts) < 100:
        status = "blocked"

    auc = float(metrics["auc"])
    if status == "blocked":
        verdict = "prompt-text-only review blocked by split size"
    elif auc >= 0.8:
        verdict = "prompt text alone is a strong split separator"
    elif auc >= 0.65:
        verdict = "prompt text alone is a moderate split separator"
    else:
        verdict = "prompt text alone is not a strong split separator"

    return {
        "status": status,
        "track": "black-box",
        "method": "clid",
        "mode": "prompt-text-only-review",
        "run_root": root.as_posix(),
        "split_rows": {
            "member_metadata": len(member_texts),
            "nonmember_metadata": len(nonmember_texts),
        },
        "prompt_overlap": prompt_overlap,
        "vocabulary": {
            "min_count": min_count,
            "max_features": max_features,
            "selected_features": len(vocabulary),
            "sample": vocabulary[:20],
        },
        "metrics": {
            "scorer": "binary_token_split_centroid_resubstitution",
            "auc": round(float(metrics["auc"]), 6),
            "asr": round(float(metrics["asr"]), 6),
            "tpr_at_1pct_fpr": round(float(metrics.get("tpr_at_1pct_fpr", 0.0)), 6),
            "tpr_at_0_1pct_fpr": round(float(metrics.get("tpr_at_0_1pct_fpr", 0.0)), 6),
            "orientation": str(metrics["orientation"]),
        },
        "nuisance_metrics": {
            "text_length_auc_best_orientation": round(text_length_auc, 6),
            "token_count_auc_best_orientation": round(token_count_auc, 6),
        },
        "verdict": verdict,
        "boundary": (
            "This is a prompt-text-only nuisance baseline. It does not use images, CLiD score "
            "matrices, or generated artifacts, and it cannot admit CLiD by itself."
        ),
    }
