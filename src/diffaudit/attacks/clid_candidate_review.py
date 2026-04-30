"""Candidate-level review for local CLiD score packets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from diffaudit.attacks.clid import (
    _auc_member_low,
    _extract_clid_features,
    _search_threshold,
    load_clid_score_matrix,
)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if raw_line.strip():
            row = json.loads(raw_line)
            if not isinstance(row, dict):
                raise ValueError(f"Expected JSON object row at {path}")
            rows.append(row)
    return rows


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _find_single(path: Path, pattern: str) -> Path:
    matches = sorted(path.glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one artifact for {pattern}, got {len(matches)}")
    return matches[0]


def _auc_best_orientation(member_values: np.ndarray, nonmember_values: np.ndarray) -> float:
    low = _auc_member_low(member_values, nonmember_values)
    return float(max(low, 1.0 - low))


def _permutation_p_value(
    member_scores: np.ndarray,
    nonmember_scores: np.ndarray,
    *,
    permutations: int = 512,
    seed: int = 20260501,
) -> float:
    observed = _auc_member_low(member_scores, nonmember_scores)
    combined = np.concatenate([member_scores, nonmember_scores])
    member_count = member_scores.shape[0]
    rng = np.random.default_rng(seed)
    wins = 0
    for _ in range(permutations):
        order = rng.permutation(combined.shape[0])
        shuffled_member = combined[order[:member_count]]
        shuffled_nonmember = combined[order[member_count:]]
        if _auc_member_low(shuffled_member, shuffled_nonmember) >= observed:
            wins += 1
    return float((wins + 1) / (permutations + 1))


def review_clid_candidate_packet(
    run_root: str | Path,
    *,
    permutations: int = 512,
) -> dict[str, Any]:
    """Review a local CLiD candidate before it can be admitted as evidence."""

    root = Path(run_root)
    member_dir = root / "datasets" / "member"
    nonmember_dir = root / "datasets" / "nonmember"
    output_dir = root / "outputs"
    score_summary_path = root / "score-summary-workspace" / "score-summary.json"

    member_rows = _read_jsonl(member_dir / "metadata.jsonl")
    nonmember_rows = _read_jsonl(nonmember_dir / "metadata.jsonl")
    member_hashes = [
        _sha256(member_dir / str(row["file_name"]))
        for row in member_rows
        if (member_dir / str(row.get("file_name", ""))).is_file()
    ]
    nonmember_hashes = [
        _sha256(nonmember_dir / str(row["file_name"]))
        for row in nonmember_rows
        if (nonmember_dir / str(row.get("file_name", ""))).is_file()
    ]
    member_texts = [str(row.get("text", "")) for row in member_rows]
    nonmember_texts = [str(row.get("text", "")) for row in nonmember_rows]

    member_score_path = _find_single(output_dir, "*TRTE_train*.txt")
    nonmember_score_path = _find_single(output_dir, "*TRTE_test*.txt")
    member_matrix = load_clid_score_matrix(member_score_path)
    nonmember_matrix = load_clid_score_matrix(nonmember_score_path)
    member_features = _extract_clid_features(member_matrix)
    nonmember_features = _extract_clid_features(nonmember_matrix)

    feature0_metrics = _search_threshold(member_features[:, 0], nonmember_features[:, 0])
    feature1_metrics = _search_threshold(member_features[:, 1], nonmember_features[:, 1])
    text_length_auc = _auc_best_orientation(
        np.asarray([len(text) for text in member_texts], dtype=float),
        np.asarray([len(text) for text in nonmember_texts], dtype=float),
    )
    prompt_overlap = len(set(member_texts) & set(nonmember_texts))
    image_overlap = len(set(member_hashes) & set(nonmember_hashes))
    feature1_p_value = _permutation_p_value(
        member_features[:, 1],
        nonmember_features[:, 1],
        permutations=permutations,
    )

    score_summary = json.loads(score_summary_path.read_text(encoding="utf-8")) if score_summary_path.exists() else {}
    checks = {
        "metadata_score_row_alignment": (
            len(member_rows) == int(member_matrix.shape[0])
            and len(nonmember_rows) == int(nonmember_matrix.shape[0])
        ),
        "balanced_split_rows": len(member_rows) == len(nonmember_rows) and len(member_rows) >= 100,
        "no_cross_split_image_duplicates": image_overlap == 0,
        "no_cross_split_prompt_duplicates": prompt_overlap == 0,
        "text_length_not_dominant": text_length_auc < 0.8,
        "score_summary_gate_passed": (
            score_summary.get("low_fpr_gate", {}).get("passed") is True
            and score_summary.get("method") == "clid"
        ),
        "feature1_permutation_significant": feature1_p_value <= 0.01,
    }
    blocking = [
        key
        for key in (
            "metadata_score_row_alignment",
            "balanced_split_rows",
            "no_cross_split_image_duplicates",
            "score_summary_gate_passed",
        )
        if not checks[key]
    ]
    warnings = [
        key
        for key in (
            "no_cross_split_prompt_duplicates",
            "text_length_not_dominant",
            "feature1_permutation_significant",
        )
        if not checks[key]
    ]
    if blocking:
        verdict = "candidate blocked by packet integrity review"
        next_action = "fix packet integrity before repeat or admission"
    elif warnings:
        verdict = "candidate needs adaptive review"
        next_action = "investigate warning surfaces before repeat GPU packet"
    else:
        verdict = "candidate survives first integrity review; repeat before admission"
        next_action = "run one independent repeat or perturbation before admitted evidence"

    return {
        "status": "ready" if not blocking else "blocked",
        "track": "black-box",
        "method": "clid",
        "mode": "candidate-integrity-review",
        "run_root": root.as_posix(),
        "checks": checks,
        "blocking": blocking,
        "warnings": warnings,
        "split_rows": {
            "member_metadata": len(member_rows),
            "nonmember_metadata": len(nonmember_rows),
            "member_scores": int(member_matrix.shape[0]),
            "nonmember_scores": int(nonmember_matrix.shape[0]),
        },
        "overlap": {
            "image_sha256": image_overlap,
            "prompt_text": prompt_overlap,
        },
        "nuisance_metrics": {
            "text_length_auc_best_orientation": round(text_length_auc, 6),
        },
        "feature_sanity": {
            "feature0": {
                "auc": round(float(feature0_metrics["auc"]), 6),
                "asr": round(float(feature0_metrics["asr"]), 6),
                "tpr_at_1pct_fpr": round(float(feature0_metrics["tpr_at_1pct_fpr"]), 6),
                "tpr_at_0_1pct_fpr": round(float(feature0_metrics["tpr_at_0_1pct_fpr"]), 6),
            },
            "feature1_clid_aux": {
                "auc": round(float(feature1_metrics["auc"]), 6),
                "asr": round(float(feature1_metrics["asr"]), 6),
                "tpr_at_1pct_fpr": round(float(feature1_metrics["tpr_at_1pct_fpr"]), 6),
                "tpr_at_0_1pct_fpr": round(float(feature1_metrics["tpr_at_0_1pct_fpr"]), 6),
                "permutation_p_value": round(feature1_p_value, 6),
                "permutations": int(permutations),
            },
        },
        "verdict": verdict,
        "next_action": next_action,
    }
