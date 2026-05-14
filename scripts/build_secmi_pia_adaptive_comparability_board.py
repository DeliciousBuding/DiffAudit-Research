from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUTPUT = ROOT / "workspaces" / "gray-box" / "artifacts" / "secmi-pia-adaptive-comparability-board-20260515.json"

PIA_1024_SUMMARY = ROOT / "workspaces" / "gray-box" / "runs" / "pia-cifar10-runtime-mainline-20260415-gpu-1024-adaptive" / "summary.json"
PIA_1024_SCORES = ROOT / "workspaces" / "gray-box" / "runs" / "pia-cifar10-runtime-mainline-20260415-gpu-1024-adaptive" / "scores.json"
PIA_1024_ADAPTIVE = ROOT / "workspaces" / "gray-box" / "runs" / "pia-cifar10-runtime-mainline-20260415-gpu-1024-adaptive" / "adaptive-scores.json"

PIA_2048_SUMMARY = ROOT / "workspaces" / "gray-box" / "runs" / "pia-cifar10-runtime-mainline-20260416-gpu-2048-cdi-r1" / "summary.json"
PIA_2048_SCORES = ROOT / "workspaces" / "gray-box" / "runs" / "pia-cifar10-runtime-mainline-20260416-gpu-2048-cdi-r1" / "scores.json"
PIA_2048_ADAPTIVE = ROOT / "workspaces" / "gray-box" / "runs" / "pia-cifar10-runtime-mainline-20260416-gpu-2048-cdi-r1" / "adaptive-scores.json"

SECMI_FULL_SUMMARY = ROOT / "workspaces" / "gray-box" / "runs" / "secmi-cifar10-gpu-full-stat-20260415-r2" / "summary.json"
SECMI_4096_SUMMARY = ROOT / "workspaces" / "gray-box" / "runs" / "secmi-cifar10-gpu-4096-20260415-r1" / "summary.json"

DISAGREE_1024_SUMMARY = ROOT / "workspaces" / "gray-box" / "runs" / "secmi-pia-disagreement-20260415-r1" / "summary.json"
DISAGREE_1024_DETAILS = ROOT / "workspaces" / "gray-box" / "runs" / "secmi-pia-disagreement-20260415-r1" / "outputs" / "disagreement_analysis.json"
SECMI_1024_SCORES = ROOT / "workspaces" / "gray-box" / "runs" / "secmi-pia-disagreement-20260415-r1" / "outputs" / "secmi_scores_1024.json"

DISAGREE_2048_SUMMARY = ROOT / "workspaces" / "gray-box" / "runs" / "secmi-pia-disagreement-20260416-r3" / "summary.json"
SECMI_2048_MEMBER_SCORES = ROOT / "workspaces" / "gray-box" / "runs" / "secmi-pia-disagreement-20260416-r3" / "secmi_member_scores.npy"
SECMI_2048_NONMEMBER_SCORES = ROOT / "workspaces" / "gray-box" / "runs" / "secmi-pia-disagreement-20260416-r3" / "secmi_nonmember_scores.npy"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a CPU-only SecMI-vs-PIA adaptive comparability board from existing "
            "gray-box summaries and aligned score exports."
        )
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def finite_float(value: Any) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite numeric value: {value!r}")
    return number


def rounded(value: Any, digits: int = 6) -> float:
    return round(finite_float(value), digits)


def metric_subset(metrics: dict[str, Any]) -> dict[str, float]:
    fields = (
        "auc",
        "asr",
        "tpr_at_1pct_fpr",
        "tpr_at_0_1pct_fpr",
        "threshold",
        "member_score_mean",
        "nonmember_score_mean",
    )
    return {field: rounded(metrics[field]) for field in fields if field in metrics}


def rank_average(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    i = 0
    while i < len(values):
        j = i
        while j + 1 < len(values) and values[order[j + 1]] == values[order[i]]:
            j += 1
        ranks[order[i : j + 1]] = (i + j + 2) / 2.0
        i = j + 1
    return ranks


def auc_from_scores(member_scores: np.ndarray, nonmember_scores: np.ndarray) -> float:
    m = len(member_scores)
    n = len(nonmember_scores)
    scores = np.concatenate([member_scores, nonmember_scores])
    ranks = rank_average(scores)
    rank_sum = float(ranks[:m].sum())
    return (rank_sum - (m * (m + 1) / 2.0)) / float(m * n)


def best_asr_and_tail(member_scores: np.ndarray, nonmember_scores: np.ndarray) -> dict[str, float]:
    thresholds = np.concatenate(([np.inf], np.unique(np.concatenate([member_scores, nonmember_scores]))[::-1], [-np.inf]))
    best_asr = -1.0
    best_threshold = float("nan")
    tpr_at_1 = 0.0
    tpr_at_01 = 0.0
    for threshold in thresholds:
        tpr = float(np.mean(member_scores >= threshold))
        fpr = float(np.mean(nonmember_scores >= threshold))
        asr = (float(len(member_scores)) * tpr + float(len(nonmember_scores)) * (1.0 - fpr)) / float(
            len(member_scores) + len(nonmember_scores)
        )
        if asr > best_asr:
            best_asr = asr
            best_threshold = float(threshold)
        if fpr <= 0.01:
            tpr_at_1 = max(tpr_at_1, tpr)
        if fpr <= 0.001:
            tpr_at_01 = max(tpr_at_01, tpr)
    return {
        "asr": best_asr,
        "threshold": best_threshold,
        "tpr_at_1pct_fpr": tpr_at_1,
        "tpr_at_0_1pct_fpr": tpr_at_01,
    }


def orient_memberness(member_scores: np.ndarray, nonmember_scores: np.ndarray) -> tuple[np.ndarray, np.ndarray, str]:
    if float(np.mean(member_scores)) < float(np.mean(nonmember_scores)):
        return -member_scores, -nonmember_scores, "negated"
    return member_scores, nonmember_scores, "identity"


def score_metrics(member_raw: np.ndarray, nonmember_raw: np.ndarray) -> tuple[dict[str, float], str]:
    member_scores, nonmember_scores, orientation = orient_memberness(member_raw, nonmember_raw)
    metrics = best_asr_and_tail(member_scores, nonmember_scores)
    metrics |= {
        "auc": auc_from_scores(member_scores, nonmember_scores),
        "member_score_mean": float(np.mean(member_raw)),
        "nonmember_score_mean": float(np.mean(nonmember_raw)),
    }
    return {key: rounded(value) for key, value in metrics.items()}, orientation


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) != len(b):
        raise ValueError(f"length mismatch: {len(a)} vs {len(b)}")
    if len(a) == 0:
        raise ValueError("cannot correlate empty arrays")
    return float(np.corrcoef(a, b)[0, 1])


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    return pearson(rank_average(a), rank_average(b))


def topk_overlap(a: np.ndarray, b: np.ndarray, k: int) -> float:
    top_a = set(np.argsort(a)[-k:].tolist())
    top_b = set(np.argsort(b)[-k:].tolist())
    return len(top_a & top_b) / float(k)


def load_score_json(path: Path) -> tuple[np.ndarray, np.ndarray]:
    payload = load_json(path)
    return np.asarray(payload["member_scores"], dtype=float), np.asarray(payload["nonmember_scores"], dtype=float)


def adaptive_summary(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    member_std = np.asarray(payload.get("member_score_std", []), dtype=float)
    nonmember_std = np.asarray(payload.get("nonmember_score_std", []), dtype=float)
    return {
        "score_file": rel(path),
        "available": True,
        "query_repeats": int(payload["query_repeats"]),
        "aggregation": payload["aggregation"],
        "member_score_std_mean": rounded(float(np.mean(member_std))) if len(member_std) else None,
        "nonmember_score_std_mean": rounded(float(np.mean(nonmember_std))) if len(nonmember_std) else None,
        "score_std_max": rounded(float(max(np.max(member_std), np.max(nonmember_std)))) if len(member_std) and len(nonmember_std) else None,
    }


def aligned_check(
    *,
    row_id: str,
    samples_per_split: int,
    pia_score_path: Path,
    secmi_member_raw: np.ndarray,
    secmi_nonmember_raw: np.ndarray,
    summary_path: Path,
    detail_path: Path | None = None,
) -> dict[str, Any]:
    pia_member_raw, pia_nonmember_raw = load_score_json(pia_score_path)
    pia_member_raw = pia_member_raw[:samples_per_split]
    pia_nonmember_raw = pia_nonmember_raw[:samples_per_split]
    secmi_member_raw = secmi_member_raw[:samples_per_split]
    secmi_nonmember_raw = secmi_nonmember_raw[:samples_per_split]

    pia_metrics, pia_orientation = score_metrics(pia_member_raw, pia_nonmember_raw)
    secmi_metrics, secmi_orientation = score_metrics(secmi_member_raw, secmi_nonmember_raw)
    pia_memberness_member, pia_memberness_nonmember, _ = orient_memberness(pia_member_raw, pia_nonmember_raw)
    secmi_memberness_member, secmi_memberness_nonmember, _ = orient_memberness(secmi_member_raw, secmi_nonmember_raw)
    pia_combined = np.concatenate([pia_memberness_member, pia_memberness_nonmember])
    secmi_combined = np.concatenate([secmi_memberness_member, secmi_memberness_nonmember])
    topk = max(16, samples_per_split // 10)

    summary = load_json(summary_path)
    detail = load_json(detail_path) if detail_path is not None and detail_path.exists() else None
    disagreement_rate = None
    if detail is not None and "disagreement_rate" in detail:
        disagreement_rate = rounded(detail["disagreement_rate"])
    elif isinstance(summary.get("metrics"), dict) and "disagreement_rate" in summary["metrics"]:
        disagreement_rate = rounded(summary["metrics"]["disagreement_rate"])

    return {
        "row_id": row_id,
        "samples_per_split": samples_per_split,
        "score_sources": {
            "pia_scores": rel(pia_score_path),
            "secmi_summary": rel(summary_path),
            **({"secmi_detail": rel(detail_path)} if detail_path is not None else {}),
        },
        "pia_recomputed": {
            "orientation": pia_orientation,
            "metrics": pia_metrics,
        },
        "secmi_stat_recomputed": {
            "orientation": secmi_orientation,
            "metrics": secmi_metrics,
        },
        "secmi_minus_pia": {
            "auc": rounded(secmi_metrics["auc"] - pia_metrics["auc"]),
            "asr": rounded(secmi_metrics["asr"] - pia_metrics["asr"]),
            "tpr_at_1pct_fpr": rounded(secmi_metrics["tpr_at_1pct_fpr"] - pia_metrics["tpr_at_1pct_fpr"]),
            "tpr_at_0_1pct_fpr": rounded(secmi_metrics["tpr_at_0_1pct_fpr"] - pia_metrics["tpr_at_0_1pct_fpr"]),
        },
        "rank_alignment": {
            "pearson": rounded(pearson(secmi_combined, pia_combined)),
            "spearman": rounded(spearman(secmi_combined, pia_combined)),
            "topk": topk,
            "topk_overlap": rounded(topk_overlap(secmi_combined, pia_combined, topk)),
            "binary_disagreement_rate": disagreement_rate,
        },
        "interpretation": (
            "SecMI stat is stronger on AUC/ASR but closely rank-aligned with PIA; "
            "this supports research corroboration, not a separate admitted consumer row."
        ),
    }


def comparison_row_from_summary(
    *,
    row_id: str,
    method: str,
    head: str,
    summary_path: Path,
    metrics: dict[str, Any],
    samples_per_split: int,
    adaptive: dict[str, Any] | None,
    cost: dict[str, Any] | None,
    consumer_boundary: str,
) -> dict[str, Any]:
    return {
        "row_id": row_id,
        "method": method,
        "head": head,
        "summary": rel(summary_path),
        "samples_per_split": samples_per_split,
        "metrics": metric_subset(metrics),
        "adaptive_review": adaptive
        or {
            "available": False,
            "query_repeats": None,
            "aggregation": None,
            "reason": "no bounded repeated-query adaptive review is present for this SecMI score head",
        },
        "cost": cost
        or {
            "available": False,
            "reason": "SecMI summaries record runtime but not the admitted PIA cost schema",
        },
        "consumer_boundary": consumer_boundary,
    }


def build_board() -> dict[str, Any]:
    pia_1024 = load_json(PIA_1024_SUMMARY)
    pia_2048 = load_json(PIA_2048_SUMMARY)
    secmi_full = load_json(SECMI_FULL_SUMMARY)
    secmi_4096 = load_json(SECMI_4096_SUMMARY)

    secmi_1024_member, secmi_1024_nonmember = load_score_json(SECMI_1024_SCORES)
    secmi_2048_member = np.load(SECMI_2048_MEMBER_SCORES)
    secmi_2048_nonmember = np.load(SECMI_2048_NONMEMBER_SCORES)

    rows = [
        comparison_row_from_summary(
            row_id="pia-1024-runtime-adaptive",
            method="pia",
            head="runtime-mainline",
            summary_path=PIA_1024_SUMMARY,
            metrics=pia_1024["metrics"],
            samples_per_split=int(pia_1024["sample_count_per_split"]),
            adaptive=adaptive_summary(PIA_1024_ADAPTIVE),
            cost={
                "available": True,
                "model_queries_per_sample": int(pia_1024["cost"]["model_queries_per_sample"]),
                "adaptive_query_repeats": int(pia_1024["cost"]["adaptive_query_repeats"]),
                "wall_clock_seconds": rounded(pia_1024["cost"]["wall_clock_seconds"]),
            },
            consumer_boundary="admitted-compatible PIA baseline surface already used by downstream consumers",
        ),
        comparison_row_from_summary(
            row_id="pia-2048-runtime-adaptive",
            method="pia",
            head="runtime-mainline",
            summary_path=PIA_2048_SUMMARY,
            metrics=pia_2048["metrics"],
            samples_per_split=int(pia_2048["sample_count_per_split"]),
            adaptive=adaptive_summary(PIA_2048_ADAPTIVE),
            cost={
                "available": True,
                "model_queries_per_sample": int(pia_2048["cost"]["model_queries_per_sample"]),
                "adaptive_query_repeats": int(pia_2048["cost"]["adaptive_query_repeats"]),
                "wall_clock_seconds": rounded(pia_2048["cost"]["wall_clock_seconds"]),
            },
            consumer_boundary="larger PIA comparison surface; not a new admitted row",
        ),
        comparison_row_from_summary(
            row_id="secmi-full-stat",
            method="secmi",
            head="stat",
            summary_path=SECMI_FULL_SUMMARY,
            metrics=secmi_full["metrics"]["stat"],
            samples_per_split=int(secmi_full["runtime"]["member_samples"]),
            adaptive=None,
            cost=None,
            consumer_boundary="research-support-only; missing admitted adaptive/cost contract",
        ),
        comparison_row_from_summary(
            row_id="secmi-full-nns-auxiliary",
            method="secmi",
            head="nns",
            summary_path=SECMI_FULL_SUMMARY,
            metrics=secmi_full["metrics"]["nns"],
            samples_per_split=int(secmi_full["runtime"]["member_samples"]),
            adaptive=None,
            cost=None,
            consumer_boundary="research-support-only auxiliary head; no product-facing scorer contract",
        ),
        comparison_row_from_summary(
            row_id="secmi-4096-stat",
            method="secmi",
            head="stat",
            summary_path=SECMI_4096_SUMMARY,
            metrics=secmi_4096["metrics"]["stat"],
            samples_per_split=int(secmi_4096["runtime"]["member_samples"]),
            adaptive=None,
            cost=None,
            consumer_boundary="research-support-only subset scale check",
        ),
    ]

    aligned_checks = [
        aligned_check(
            row_id="aligned-1024-secmi-stat-vs-pia",
            samples_per_split=1024,
            pia_score_path=PIA_1024_SCORES,
            secmi_member_raw=secmi_1024_member,
            secmi_nonmember_raw=secmi_1024_nonmember,
            summary_path=DISAGREE_1024_SUMMARY,
            detail_path=DISAGREE_1024_DETAILS,
        ),
        aligned_check(
            row_id="aligned-2048-secmi-stat-vs-pia",
            samples_per_split=2048,
            pia_score_path=PIA_2048_SCORES,
            secmi_member_raw=secmi_2048_member,
            secmi_nonmember_raw=secmi_2048_nonmember,
            summary_path=DISAGREE_2048_SUMMARY,
        ),
    ]

    return {
        "schema": "diffaudit.secmi_pia_adaptive_comparability_board.v1",
        "date": "2026-05-15",
        "status": "supporting-reference-comparison-ready",
        "admitted": False,
        "gpu_release": "none",
        "question": (
            "Do existing SecMI score heads have enough adaptive/cost comparability with admitted PIA surfaces "
            "to become a Platform/Runtime admitted gray-box row without new GPU work?"
        ),
        "source_artifacts": {
            "pia_1024_summary": rel(PIA_1024_SUMMARY),
            "pia_2048_summary": rel(PIA_2048_SUMMARY),
            "secmi_full_summary": rel(SECMI_FULL_SUMMARY),
            "secmi_4096_summary": rel(SECMI_4096_SUMMARY),
            "secmi_pia_disagreement_1024": rel(DISAGREE_1024_SUMMARY),
            "secmi_pia_disagreement_2048": rel(DISAGREE_2048_SUMMARY),
        },
        "comparison_rows": rows,
        "aligned_score_checks": aligned_checks,
        "decision": {
            "verdict": "keep_secmi_as_supporting_reference",
            "changed_by_board": (
                "The board closes the comparability question for the current artifacts: SecMI is quantitatively "
                "strong and aligned with PIA on the same samples, but it still lacks the admitted PIA adaptive "
                "review and cost contract. No Platform/Runtime admission or GPU release follows."
            ),
            "primary_evidence": [
                "SecMI stat exceeds PIA AUC on aligned 1024/1024 and 2048/2048 score surfaces.",
                "Aligned rank correlations stay high, so SecMI mostly corroborates the same membership signal rather than opening a distinct consumer surface.",
                "PIA rows carry explicit repeated-query adaptive_check and cost fields; SecMI stat/NNS rows do not.",
                "SecMI NNS is stronger but remains an auxiliary head without a product-facing scorer contract.",
            ],
            "promotion_blockers": [
                "no bounded repeated-query adaptive review for SecMI stat or NNS",
                "no admitted-row cost schema for SecMI summaries",
                "NNS auxiliary head lacks product-facing scorer contract",
                "aligned SecMI stat is highly correlated with PIA and does not justify a separate admitted consumer row",
            ],
            "blocked_expansions": [
                "no larger SecMI full-split rerun",
                "no NNS product promotion",
                "no Platform/Runtime admitted-bundle change",
                "no SecMI GPU release",
                "no learned fusion or gating matrix",
            ],
        },
        "current_slots": {
            "active_gpu_question": "none",
            "next_gpu_candidate": "none",
            "CPU sidecar": "none selected after SecMI/PIA adaptive comparability board",
        },
    }


def main() -> int:
    args = parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    board = build_board()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
