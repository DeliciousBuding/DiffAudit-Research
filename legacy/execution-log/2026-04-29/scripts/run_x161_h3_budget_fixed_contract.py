from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch

from diffaudit.attacks.pia_adapter import _compute_auc, _compute_threshold_metrics


LOW_FPR_KEYS = ("tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Freeze X-161 H3 budget-fixed adaptive-attacker contract from existing X157/X158 evidence."
    )
    parser.add_argument(
        "--x157-summary",
        type=Path,
        default=Path(
            "workspaces/gray-box/runs/x157-h3-selective-gate-cached-scout-20260429-r2-allsteps-primary/summary.json"
        ),
    )
    parser.add_argument(
        "--x158-summary",
        type=Path,
        default=Path("workspaces/gray-box/runs/x158-h3-gated-runtime-gpu-scout-20260429-r1/summary.json"),
    )
    parser.add_argument(
        "--x158-scores",
        type=Path,
        default=Path("workspaces/gray-box/runs/x158-h3-gated-runtime-gpu-scout-20260429-r1/scores.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("workspaces/gray-box/runs/x161-h3-budget-fixed-contract-20260429-r1/summary.json"),
    )
    parser.add_argument("--max-fixed-threshold-gate-fraction", type=float, default=0.22)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def metrics(member_scores: np.ndarray, nonmember_scores: np.ndarray) -> dict[str, float]:
    return {
        "auc": round(float(_compute_auc(torch.tensor(member_scores), torch.tensor(nonmember_scores))), 6),
        **_compute_threshold_metrics(member_scores, nonmember_scores),
        "member_score_mean": round(float(member_scores.mean()), 6),
        "nonmember_score_mean": round(float(nonmember_scores.mean()), 6),
    }


def metric_delta(left: dict[str, float], right: dict[str, float], keys: tuple[str, ...]) -> dict[str, float]:
    return {key: round(float(left[key]) - float(right[key]), 6) for key in keys}


def main() -> int:
    args = parse_args()
    x157 = load_json(args.x157_summary)
    x158_summary = load_json(args.x158_summary)
    x158_scores = load_json(args.x158_scores)

    fixed_threshold = float(x157["primary_selection"]["adaptive"]["gate_threshold"])

    baseline_member = np.array(x158_scores["baseline_member_scores"], dtype=float)
    baseline_nonmember = np.array(x158_scores["baseline_nonmember_scores"], dtype=float)
    all_steps_member = np.array(x158_scores["all_steps_member_scores"], dtype=float)
    all_steps_nonmember = np.array(x158_scores["all_steps_nonmember_scores"], dtype=float)

    member_gate = baseline_member >= fixed_threshold
    nonmember_gate = baseline_nonmember >= fixed_threshold

    fixed_member = np.where(member_gate, all_steps_member, baseline_member)
    fixed_nonmember = np.where(nonmember_gate, all_steps_nonmember, baseline_nonmember)

    oracle_member = np.where(member_gate, np.maximum(baseline_member, all_steps_member), baseline_member)
    oracle_nonmember = np.where(nonmember_gate, np.maximum(baseline_nonmember, all_steps_nonmember), baseline_nonmember)

    baseline_metrics = metrics(baseline_member, baseline_nonmember)
    all_steps_metrics = metrics(all_steps_member, all_steps_nonmember)
    fixed_metrics = metrics(fixed_member, fixed_nonmember)
    oracle_metrics = metrics(oracle_member, oracle_nonmember)

    fixed_gate_fraction = round(
        float((member_gate.sum() + nonmember_gate.sum()) / (len(member_gate) + len(nonmember_gate))),
        6,
    )
    fixed_threshold_low_fpr_match = all(
        float(fixed_metrics[key]) <= float(all_steps_metrics[key]) for key in LOW_FPR_KEYS
    )
    fixed_threshold_budget_ok = fixed_gate_fraction <= float(args.max_fixed_threshold_gate_fraction)
    oracle_recovers_baseline_tail = any(
        float(oracle_metrics[key]) >= float(baseline_metrics[key]) for key in LOW_FPR_KEYS
    )

    release_x162 = bool(fixed_threshold_low_fpr_match and fixed_threshold_budget_ok)
    summary = {
        "status": "ready",
        "task": "X-161 H3 budget-fixed adaptive-attacker contract freeze",
        "mode": "cpu-contract-freeze",
        "inputs": {
            "x157_summary": str(args.x157_summary),
            "x158_summary": str(args.x158_summary),
            "x158_scores": str(args.x158_scores),
            "fixed_gate_threshold_source": "X157 cached all-steps primary adaptive threshold",
        },
        "contract": {
            "packet_size": 64,
            "fixed_total_query_budget": 3,
            "gate_probe_queries": 1,
            "route_score_queries": 2,
            "gate_threshold": round(fixed_threshold, 6),
            "threshold_policy": "independent cached-calibration threshold; no same-packet quantile and no membership labels",
            "attacker": "budget-fixed defended-policy attacker: repeat the deployed gated policy under the same total query budget; no oracle access to the undefended route after routing",
            "mandatory_falsifier": "oracle-route escape must be reported separately and blocks promotion if it recovers the baseline low-FPR tail",
            "metrics": ["AUC", "ASR", "TPR@1%FPR", "TPR@0.1%FPR", "gate fractions", "score variance"],
            "host_fit": "one 64/64 scout only; no 128/128 expansion; use conda env diffaudit-research on cuda:0",
        },
        "preflight": {
            "baseline_metrics": baseline_metrics,
            "all_steps_metrics": all_steps_metrics,
            "fixed_threshold_selective_metrics": fixed_metrics,
            "fixed_threshold_selective_minus_all_steps": metric_delta(
                fixed_metrics,
                all_steps_metrics,
                ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr"),
            ),
            "fixed_gate": {
                "gate_fraction_actual": fixed_gate_fraction,
                "member_gate_fraction": round(float(member_gate.mean()), 6),
                "nonmember_gate_fraction": round(float(nonmember_gate.mean()), 6),
                "max_gate_fraction": round(float(args.max_fixed_threshold_gate_fraction), 6),
            },
            "oracle_route_escape": {
                "metrics": oracle_metrics,
                "oracle_minus_baseline": metric_delta(
                    oracle_metrics,
                    baseline_metrics,
                    ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr"),
                ),
                "recovers_baseline_tail": bool(oracle_recovers_baseline_tail),
            },
        },
        "gates": [
            {
                "name": "fixed_threshold_low_fpr_match",
                "passed": bool(fixed_threshold_low_fpr_match),
                "rule": "fixed-threshold selective route must not exceed all-steps dropout at both low-FPR metrics",
            },
            {
                "name": "fixed_threshold_gate_budget",
                "passed": bool(fixed_threshold_budget_ok),
                "rule": f"fixed-threshold gate fraction must be <= {args.max_fixed_threshold_gate_fraction}",
            },
            {
                "name": "oracle_route_escape_promotion_block",
                "passed": bool(oracle_recovers_baseline_tail),
                "rule": "oracle-route escape is expected to recover baseline tail; this blocks promotion but not the narrower fixed-budget scout",
            },
        ],
        "verdict": "positive contract freeze / one bounded GPU scout released" if release_x162 else "negative but useful",
        "decision": {
            "release_x162": release_x162,
            "active_gpu_question": "one bounded X162 H3 budget-fixed adaptive-attacker scout" if release_x162 else "none",
            "next_gpu_candidate": "none beyond X162" if release_x162 else "none",
            "promotion_allowed": False,
            "deployable_runner_allowed": False,
            "next_live_lane": "X162 H3 budget-fixed adaptive-attacker GPU scout" if release_x162 else "post-H3 non-graybox reselection",
            "cpu_sidecar": "I-A low-FPR / adaptive-attacker boundary maintenance",
        },
        "notes": [
            "The fixed cached threshold removes the same-packet top-quantile dependency from X158 and preserves the X158 low-FPR tail on cached scores.",
            "The oracle-route escape recovers the baseline tail, so H3 remains candidate-only even if X162 runs.",
            "X162, if run, must report both the fixed-budget defended-policy attacker and the oracle-route escape falsifier.",
        ],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
