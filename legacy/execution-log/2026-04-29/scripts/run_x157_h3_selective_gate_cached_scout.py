from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a cached X-157 scout for H3 selective / suspicion-gated "
            "late-step perturbation using existing PIA score surfaces."
        )
    )
    parser.add_argument(
        "--run-root",
        type=Path,
        default=None,
        help="Optional explicit output directory. Defaults to a timestamped x157 run.",
    )
    parser.add_argument(
        "--baseline-run",
        type=Path,
        default=Path("workspaces/gray-box/runs/pia-cifar10-runtime-mainline-20260409-gpu-512-adaptive"),
    )
    parser.add_argument(
        "--allsteps-run",
        type=Path,
        default=Path("workspaces/gray-box/runs/pia-cifar10-runtime-mainline-dropout-defense-20260409-gpu-512-allsteps-adaptive"),
    )
    parser.add_argument(
        "--latesteps-run",
        type=Path,
        default=Path("workspaces/gray-box/runs/pia-cifar10-runtime-mainline-dropout-defense-20260409-gpu-512-latesteps-adaptive"),
    )
    parser.add_argument(
        "--gate-fractions",
        type=float,
        nargs="+",
        default=[0.05, 0.10, 0.20, 0.50],
        help="Global top-risk fractions selected by the baseline PIA score.",
    )
    parser.add_argument(
        "--primary-defense",
        choices=["late_steps_only", "all_steps"],
        default="late_steps_only",
        help="Defended score surface used for the primary selective route.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def score_payload(run: Path, adaptive: bool) -> dict[str, list[float]]:
    filename = "adaptive-scores.json" if adaptive else "scores.json"
    payload = load_json(run / filename)
    return {
        "member_scores": [float(value) for value in payload["member_scores"]],
        "nonmember_scores": [float(value) for value in payload["nonmember_scores"]],
    }


def compute_auc(member_scores: np.ndarray, nonmember_scores: np.ndarray) -> float:
    wins = member_scores[:, None] > nonmember_scores[None, :]
    ties = member_scores[:, None] == nonmember_scores[None, :]
    return float((wins.astype(float) + (ties.astype(float) * 0.5)).mean())


def compute_threshold_metrics(member_scores: np.ndarray, nonmember_scores: np.ndarray) -> dict[str, float]:
    scores = np.concatenate([member_scores, nonmember_scores])
    labels = np.concatenate(
        [
            np.ones(member_scores.shape[0], dtype=np.int64),
            np.zeros(nonmember_scores.shape[0], dtype=np.int64),
        ]
    )
    thresholds = np.unique(scores)[::-1]
    if thresholds.size == 0:
        thresholds = np.asarray([0.0], dtype=float)

    best_asr = -1.0
    best_threshold = float(thresholds[0])
    best_tpr_at_1pct = 0.0
    best_tpr_at_0_1pct = 0.0
    for threshold in thresholds:
        predictions = (scores >= threshold).astype(np.int64)
        tp = int(((predictions == 1) & (labels == 1)).sum())
        tn = int(((predictions == 0) & (labels == 0)).sum())
        fp = int(((predictions == 1) & (labels == 0)).sum())
        fn = int(((predictions == 0) & (labels == 1)).sum())
        asr = float((tp + tn) / labels.shape[0])
        if asr > best_asr:
            best_asr = asr
            best_threshold = float(threshold)
        tpr = float(tp / (tp + fn)) if (tp + fn) else 0.0
        fpr = float(fp / (fp + tn)) if (fp + tn) else 0.0
        if fpr <= 0.01:
            best_tpr_at_1pct = max(best_tpr_at_1pct, tpr)
        if fpr <= 0.001:
            best_tpr_at_0_1pct = max(best_tpr_at_0_1pct, tpr)

    return {
        "auc": round(compute_auc(member_scores, nonmember_scores), 6),
        "asr": round(best_asr, 6),
        "threshold": round(best_threshold, 6),
        "tpr_at_1pct_fpr": round(best_tpr_at_1pct, 6),
        "tpr_at_0_1pct_fpr": round(best_tpr_at_0_1pct, 6),
        "member_score_mean": round(float(member_scores.mean()), 6),
        "nonmember_score_mean": round(float(nonmember_scores.mean()), 6),
    }


def as_arrays(payload: dict[str, list[float]]) -> tuple[np.ndarray, np.ndarray]:
    return (
        np.asarray(payload["member_scores"], dtype=float),
        np.asarray(payload["nonmember_scores"], dtype=float),
    )


def select_gate(
    baseline_member: np.ndarray,
    baseline_nonmember: np.ndarray,
    fraction: float,
) -> tuple[np.ndarray, np.ndarray, float]:
    combined = np.concatenate([baseline_member, baseline_nonmember])
    selected_count = max(1, min(int(math.ceil(combined.shape[0] * float(fraction))), combined.shape[0]))
    threshold = float(np.sort(combined)[::-1][selected_count - 1])
    return baseline_member >= threshold, baseline_nonmember >= threshold, threshold


def mix_scores(
    baseline_member: np.ndarray,
    baseline_nonmember: np.ndarray,
    defense_member: np.ndarray,
    defense_nonmember: np.ndarray,
    member_gate: np.ndarray,
    nonmember_gate: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    mixed_member = np.where(member_gate, defense_member, baseline_member)
    mixed_nonmember = np.where(nonmember_gate, defense_nonmember, baseline_nonmember)
    return mixed_member, mixed_nonmember


def metric_delta(lhs: dict[str, float], rhs: dict[str, float]) -> dict[str, float]:
    fields = ["auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr"]
    return {field: round(float(lhs[field]) - float(rhs[field]), 6) for field in fields}


def main() -> int:
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = args.run_root or Path(f"workspaces/gray-box/runs/x157-h3-selective-gate-cached-scout-{timestamp}")
    run_root.mkdir(parents=True, exist_ok=True)

    raw_surfaces = {
        "baseline": score_payload(args.baseline_run, adaptive=False),
        "all_steps": score_payload(args.allsteps_run, adaptive=False),
        "late_steps_only": score_payload(args.latesteps_run, adaptive=False),
    }
    adaptive_surfaces = {
        "baseline": score_payload(args.baseline_run, adaptive=True),
        "all_steps": score_payload(args.allsteps_run, adaptive=True),
        "late_steps_only": score_payload(args.latesteps_run, adaptive=True),
    }

    surface_metrics: dict[str, Any] = {"raw": {}, "adaptive": {}}
    for mode, surfaces in (("raw", raw_surfaces), ("adaptive", adaptive_surfaces)):
        for name, payload in surfaces.items():
            member, nonmember = as_arrays(payload)
            surface_metrics[mode][name] = compute_threshold_metrics(member, nonmember)

    selective_results: list[dict[str, Any]] = []
    for gate_fraction in args.gate_fractions:
        for defense_name in ("late_steps_only", "all_steps"):
            per_mode: dict[str, Any] = {}
            for mode, surfaces in (("raw", raw_surfaces), ("adaptive", adaptive_surfaces)):
                baseline_member, baseline_nonmember = as_arrays(surfaces["baseline"])
                defense_member, defense_nonmember = as_arrays(surfaces[defense_name])
                member_gate, nonmember_gate, gate_threshold = select_gate(
                    baseline_member,
                    baseline_nonmember,
                    gate_fraction,
                )
                mixed_member, mixed_nonmember = mix_scores(
                    baseline_member,
                    baseline_nonmember,
                    defense_member,
                    defense_nonmember,
                    member_gate,
                    nonmember_gate,
                )
                metrics = compute_threshold_metrics(mixed_member, mixed_nonmember)
                per_mode[mode] = {
                    "gate_threshold": round(float(gate_threshold), 6),
                    "gate_fraction_requested": float(gate_fraction),
                    "gate_fraction_actual": round(
                        float((member_gate.sum() + nonmember_gate.sum()) / (member_gate.shape[0] + nonmember_gate.shape[0])),
                        6,
                    ),
                    "member_gate_fraction": round(float(member_gate.mean()), 6),
                    "nonmember_gate_fraction": round(float(nonmember_gate.mean()), 6),
                    "metrics": metrics,
                    "delta_vs_baseline": metric_delta(metrics, surface_metrics[mode]["baseline"]),
                    "delta_vs_all_steps": metric_delta(metrics, surface_metrics[mode]["all_steps"]),
                    "delta_vs_late_steps_only": metric_delta(metrics, surface_metrics[mode]["late_steps_only"]),
                }
            selective_results.append(
                {
                    "defense_surface": defense_name,
                    "gate_fraction": float(gate_fraction),
                    "raw": per_mode["raw"],
                    "adaptive": per_mode["adaptive"],
                }
            )

    max_gate_fraction = 0.20
    total_score_count = len(raw_surfaces["baseline"]["member_scores"]) + len(raw_surfaces["baseline"]["nonmember_scores"])
    gate_fraction_tolerance = 1.0 / max(total_score_count, 1)
    primary_candidates = [
        item
        for item in selective_results
        if item["defense_surface"] == args.primary_defense and item["gate_fraction"] <= max_gate_fraction
    ]
    best_primary = min(
        primary_candidates,
        key=lambda item: (
            item["adaptive"]["metrics"]["tpr_at_1pct_fpr"],
            item["adaptive"]["metrics"]["tpr_at_0_1pct_fpr"],
            item["adaptive"]["metrics"]["auc"],
            item["adaptive"]["gate_fraction_actual"],
        ),
    )
    all_steps_adaptive = surface_metrics["adaptive"]["all_steps"]
    best_adaptive = best_primary["adaptive"]["metrics"]
    clears_gpu_release_gate = (
        best_adaptive["tpr_at_1pct_fpr"] <= all_steps_adaptive["tpr_at_1pct_fpr"]
        and best_adaptive["tpr_at_0_1pct_fpr"] <= all_steps_adaptive["tpr_at_0_1pct_fpr"]
        and best_primary["adaptive"]["gate_fraction_actual"] <= max_gate_fraction + gate_fraction_tolerance
    )

    summary = {
        "status": "ready",
        "task": "X-157 H3 selective / suspicion-gated cached scout",
        "mode": "cached-score scout",
        "gpu_release": "none",
        "admitted_change": "none",
        "inputs": {
            "baseline_run": str(args.baseline_run),
            "allsteps_run": str(args.allsteps_run),
            "latesteps_run": str(args.latesteps_run),
            "selection_signal": "baseline PIA score tail",
            "primary_defense": args.primary_defense,
            "gate_fractions": [float(value) for value in args.gate_fractions],
        },
        "surface_metrics": surface_metrics,
        "selective_results": selective_results,
        "primary_selection": best_primary,
        "verdict": "gpu_candidate_released" if clears_gpu_release_gate else "gpu_hold",
        "release_gate": {
            "clears_gpu_release_gate": bool(clears_gpu_release_gate),
            "max_gate_fraction": max_gate_fraction,
            "gate_fraction_tolerance": round(gate_fraction_tolerance, 6),
            "rule": (
                "primary adaptive selective route must not exceed all_steps dropout on "
                "TPR@1%FPR or TPR@0.1%FPR while defending <=20% of samples"
            ),
        },
        "notes": [
            "This is a cached score-level scout, not an admitted defense result.",
            "The detector is baseline PIA score tail, not SimA, because current local SimA remains auxiliary.",
            "A positive result only authorizes an actual gated runtime implementation scout; it does not promote H3.",
        ],
    }
    (run_root / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
