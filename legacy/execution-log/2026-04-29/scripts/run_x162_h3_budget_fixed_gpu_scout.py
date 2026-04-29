from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch

from diffaudit.attacks.pia import probe_pia_assets
from diffaudit.attacks.pia_adapter import (
    _build_pia_attacker,
    _build_pia_subset_loader,
    _compute_auc,
    _compute_threshold_metrics,
    _resolve_late_step_threshold,
    _score_batch_once,
    load_pia_model,
    prepare_pia_runtime,
)
from diffaudit.config import load_audit_config


LOW_FPR_KEYS = ("tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run X-162 H3 fixed-budget adaptive-attacker GPU scout."
    )
    parser.add_argument("--config", type=Path, default=Path("configs/attacks/pia_mainline_canonical.yaml"))
    parser.add_argument("--run-root", type=Path, default=None)
    parser.add_argument("--x161-summary", type=Path, default=Path("workspaces/gray-box/runs/x161-h3-budget-fixed-contract-20260429-r1/summary.json"))
    parser.add_argument("--repo-root", type=Path, default=Path("external/PIA"))
    parser.add_argument("--member-split-root", type=Path, default=Path("external/PIA/DDPM"))
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--packet-size", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--fixed-total-query-budget", type=int, default=3)
    parser.add_argument("--route-score-queries", type=int, default=2)
    parser.add_argument("--max-gate-fraction", type=float, default=0.22)
    parser.add_argument("--late-step-threshold", type=int, default=None)
    return parser.parse_args()


def tensor_metrics(member_scores: torch.Tensor, nonmember_scores: torch.Tensor) -> dict[str, float]:
    return {
        "auc": round(float(_compute_auc(member_scores, nonmember_scores)), 6),
        **_compute_threshold_metrics(
            member_scores.detach().cpu().numpy(),
            nonmember_scores.detach().cpu().numpy(),
        ),
        "member_score_mean": round(float(member_scores.detach().cpu().mean().item()), 6),
        "nonmember_score_mean": round(float(nonmember_scores.detach().cpu().mean().item()), 6),
    }


def score_repeats(
    runtime_context,
    model: torch.nn.Module,
    loader,
    device: str,
    repeats: int,
    dropout_activation_schedule: str,
    late_step_threshold: int,
) -> torch.Tensor:
    attacker = _build_pia_attacker(
        components_module=runtime_context.components_module,
        model=model,
        attacker_name=runtime_context.plan.attacker_name,
        attack_num=runtime_context.plan.attack_num,
        interval=runtime_context.plan.interval,
        device=device,
        dropout_activation_schedule=dropout_activation_schedule,
        late_step_threshold=late_step_threshold,
    )
    by_repeat: list[list[torch.Tensor]] = [[] for _ in range(repeats)]
    with torch.no_grad():
        for batch, _ in loader:
            for repeat_idx in range(repeats):
                by_repeat[repeat_idx].append(_score_batch_once(attacker, batch, device=device))
    return torch.stack([torch.cat(parts).detach().cpu() for parts in by_repeat])


def mean_head(scores: torch.Tensor, count: int) -> torch.Tensor:
    return scores[:count].mean(dim=0)


def mean_tail(scores: torch.Tensor, start: int, count: int) -> torch.Tensor:
    return scores[start : start + count].mean(dim=0)


def serializable_matrix(scores: torch.Tensor) -> list[list[float]]:
    return [
        [round(float(value), 6) for value in row.detach().cpu().tolist()]
        for row in scores
    ]


def metric_delta(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    return {
        key: round(float(left[key]) - float(right[key]), 6)
        for key in ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")
    }


def main() -> int:
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = args.run_root or Path(f"workspaces/gray-box/runs/x162-h3-budget-fixed-gpu-scout-{timestamp}")
    run_root.mkdir(parents=True, exist_ok=True)
    started_at = time.perf_counter()

    try:
        x161 = json.loads(args.x161_summary.read_text(encoding="utf-8"))
        gate_threshold = float(x161["contract"]["gate_threshold"])

        config = load_audit_config(args.config)
        runtime_context = prepare_pia_runtime(
            config,
            repo_root=args.repo_root,
            member_split_root=args.member_split_root,
            device=args.device,
        )
        model, weights_key = load_pia_model(
            runtime_context.checkpoint_path,
            runtime_context.model_module,
            device=args.device,
        )
        model.eval()
        late_step_threshold = _resolve_late_step_threshold(
            attack_num=runtime_context.plan.attack_num,
            interval=runtime_context.plan.interval,
            late_step_threshold=args.late_step_threshold,
        )
        split_root = Path(args.member_split_root) if args.member_split_root else Path(args.repo_root) / "DDPM"
        asset_summary = probe_pia_assets(
            dataset=runtime_context.plan.dataset,
            dataset_root=runtime_context.plan.data_root,
            model_dir=runtime_context.plan.model_dir,
            member_split_root=split_root,
        )
        member_loader, member_indices = _build_pia_subset_loader(
            dataset=runtime_context.plan.dataset,
            dataset_dir=asset_summary["paths"]["dataset_dir"],
            member_split_path=asset_summary["paths"]["member_split"],
            batch_size=args.batch_size,
            max_samples=args.packet_size,
            membership="member",
        )
        nonmember_loader, nonmember_indices = _build_pia_subset_loader(
            dataset=runtime_context.plan.dataset,
            dataset_dir=asset_summary["paths"]["dataset_dir"],
            member_split_path=asset_summary["paths"]["member_split"],
            batch_size=args.batch_size,
            max_samples=args.packet_size,
            membership="nonmember",
        )

        baseline_member_repeats = score_repeats(
            runtime_context,
            model,
            member_loader,
            args.device,
            args.fixed_total_query_budget,
            "off",
            late_step_threshold,
        )
        baseline_nonmember_repeats = score_repeats(
            runtime_context,
            model,
            nonmember_loader,
            args.device,
            args.fixed_total_query_budget,
            "off",
            late_step_threshold,
        )
        all_steps_member_repeats = score_repeats(
            runtime_context,
            model,
            member_loader,
            args.device,
            args.fixed_total_query_budget,
            "all_steps",
            late_step_threshold,
        )
        all_steps_nonmember_repeats = score_repeats(
            runtime_context,
            model,
            nonmember_loader,
            args.device,
            args.fixed_total_query_budget,
            "all_steps",
            late_step_threshold,
        )

        baseline_member = mean_head(baseline_member_repeats, args.fixed_total_query_budget)
        baseline_nonmember = mean_head(baseline_nonmember_repeats, args.fixed_total_query_budget)
        all_steps_member = mean_head(all_steps_member_repeats, args.fixed_total_query_budget)
        all_steps_nonmember = mean_head(all_steps_nonmember_repeats, args.fixed_total_query_budget)

        member_gate = baseline_member_repeats[0] >= gate_threshold
        nonmember_gate = baseline_nonmember_repeats[0] >= gate_threshold
        selective_member = torch.where(
            member_gate,
            mean_head(all_steps_member_repeats, args.route_score_queries),
            mean_tail(baseline_member_repeats, 1, args.route_score_queries),
        )
        selective_nonmember = torch.where(
            nonmember_gate,
            mean_head(all_steps_nonmember_repeats, args.route_score_queries),
            mean_tail(baseline_nonmember_repeats, 1, args.route_score_queries),
        )
        gate_leak_member = torch.where(
            member_gate,
            (baseline_member_repeats[0] + all_steps_member_repeats[: args.route_score_queries].sum(dim=0))
            / float(args.fixed_total_query_budget),
            baseline_member,
        )
        gate_leak_nonmember = torch.where(
            nonmember_gate,
            (baseline_nonmember_repeats[0] + all_steps_nonmember_repeats[: args.route_score_queries].sum(dim=0))
            / float(args.fixed_total_query_budget),
            baseline_nonmember,
        )
        oracle_member = torch.where(member_gate, torch.maximum(baseline_member, all_steps_member), baseline_member)
        oracle_nonmember = torch.where(nonmember_gate, torch.maximum(baseline_nonmember, all_steps_nonmember), baseline_nonmember)

        baseline_metrics = tensor_metrics(baseline_member, baseline_nonmember)
        all_steps_metrics = tensor_metrics(all_steps_member, all_steps_nonmember)
        selective_metrics = tensor_metrics(selective_member, selective_nonmember)
        gate_leak_metrics = tensor_metrics(gate_leak_member, gate_leak_nonmember)
        oracle_metrics = tensor_metrics(oracle_member, oracle_nonmember)

        gate_fraction = round(
            float((member_gate.sum().item() + nonmember_gate.sum().item()) / (member_gate.shape[0] + nonmember_gate.shape[0])),
            6,
        )
        low_fpr_match = all(
            float(selective_metrics[key]) <= float(all_steps_metrics[key])
            for key in LOW_FPR_KEYS
        )
        gate_budget_ok = gate_fraction <= float(args.max_gate_fraction)
        verdict = "positive but bounded" if low_fpr_match and gate_budget_ok else "negative but useful"

        summary = {
            "status": "ready",
            "task": "X-162 H3 budget-fixed adaptive-attacker GPU scout",
            "mode": "bounded-gpu-scout",
            "device": args.device,
            "gpu_release": "one bounded 64/64 fixed-budget scout",
            "admitted_change": "none",
            "inputs": {
                "config": str(args.config),
                "repo_root": str(args.repo_root),
                "member_split_root": str(args.member_split_root),
                "x161_summary": str(args.x161_summary),
                "packet_size": int(args.packet_size),
                "batch_size": int(args.batch_size),
                "fixed_total_query_budget": int(args.fixed_total_query_budget),
                "route_score_queries": int(args.route_score_queries),
                "gate_threshold": round(float(gate_threshold), 6),
            },
            "runtime": {
                "weights_key": weights_key,
                "attack_num": int(runtime_context.plan.attack_num),
                "interval": int(runtime_context.plan.interval),
                "late_step_threshold": int(late_step_threshold),
                "member_indices": [int(value) for value in member_indices],
                "nonmember_indices": [int(value) for value in nonmember_indices],
                "wall_clock_seconds": round(time.perf_counter() - started_at, 6),
            },
            "baseline_budget": {"metrics": baseline_metrics},
            "all_steps_budget": {"metrics": all_steps_metrics},
            "fixed_budget_selective": {
                "metrics": selective_metrics,
                "delta_vs_baseline": metric_delta(selective_metrics, baseline_metrics),
                "delta_vs_all_steps": metric_delta(selective_metrics, all_steps_metrics),
            },
            "gate_leak_falsifier": {
                "metrics": gate_leak_metrics,
                "delta_vs_baseline": metric_delta(gate_leak_metrics, baseline_metrics),
                "delta_vs_all_steps": metric_delta(gate_leak_metrics, all_steps_metrics),
            },
            "oracle_route_escape": {
                "metrics": oracle_metrics,
                "delta_vs_baseline": metric_delta(oracle_metrics, baseline_metrics),
                "delta_vs_all_steps": metric_delta(oracle_metrics, all_steps_metrics),
            },
            "gate": {
                "gate_fraction_actual": gate_fraction,
                "member_gate_fraction": round(float(member_gate.float().mean().item()), 6),
                "nonmember_gate_fraction": round(float(nonmember_gate.float().mean().item()), 6),
                "max_gate_fraction": round(float(args.max_gate_fraction), 6),
            },
            "verdict": verdict,
            "promotion_allowed": False,
            "next_gpu_candidate": "none",
            "notes": [
                "This tests the fixed-budget defended-policy attacker from X161, not an oracle that can choose the undefended route after routing.",
                "Gate-leak and oracle-route falsifiers are reported explicitly and continue to block promotion.",
                "No admitted table, Runtime endpoint, Platform view, or public claim should change from this scout.",
            ],
        }
        (run_root / "scores.json").write_text(
            json.dumps(
                {
                    "member_indices": [int(value) for value in member_indices],
                    "nonmember_indices": [int(value) for value in nonmember_indices],
                    "baseline_member_repeats": serializable_matrix(baseline_member_repeats),
                    "baseline_nonmember_repeats": serializable_matrix(baseline_nonmember_repeats),
                    "all_steps_member_repeats": serializable_matrix(all_steps_member_repeats),
                    "all_steps_nonmember_repeats": serializable_matrix(all_steps_nonmember_repeats),
                },
                indent=2,
                ensure_ascii=True,
            ),
            encoding="utf-8",
        )
    except RuntimeError as exc:
        summary = {
            "status": "blocked",
            "task": "X-162 H3 budget-fixed adaptive-attacker GPU scout",
            "mode": "bounded-gpu-scout",
            "device": args.device,
            "error": f"{type(exc).__name__}: {exc}",
            "verdict": "blocked",
            "next_gpu_candidate": "none until GPU memory or runtime blocker is cleared",
        }
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    (run_root / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
