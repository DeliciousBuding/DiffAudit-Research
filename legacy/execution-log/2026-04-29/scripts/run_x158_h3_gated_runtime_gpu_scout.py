from __future__ import annotations

import argparse
import json
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch

from diffaudit.attacks.pia_adapter import (
    _build_pia_attacker,
    _build_pia_subset_loader,
    _compute_auc,
    _compute_threshold_metrics,
    _resolve_late_step_threshold,
    _score_loader,
    load_pia_model,
    prepare_pia_runtime,
)
from diffaudit.attacks.pia import probe_pia_assets
from diffaudit.config import load_audit_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run X-158 bounded GPU scout for H3 suspicion-gated all-steps dropout."
    )
    parser.add_argument("--config", type=Path, default=Path("configs/attacks/pia_mainline_canonical.yaml"))
    parser.add_argument("--run-root", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, default=Path("external/PIA"))
    parser.add_argument("--member-split-root", type=Path, default=Path("external/PIA/DDPM"))
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--packet-size", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--adaptive-query-repeats", type=int, default=3)
    parser.add_argument("--gate-fraction", type=float, default=0.20)
    parser.add_argument("--dropout-activation-schedule", choices=["all_steps"], default="all_steps")
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


def select_gate(
    baseline_member: torch.Tensor,
    baseline_nonmember: torch.Tensor,
    gate_fraction: float,
) -> tuple[torch.Tensor, torch.Tensor, float, int]:
    combined = torch.cat([baseline_member.detach().cpu(), baseline_nonmember.detach().cpu()]).numpy()
    selected_count = max(1, min(int(math.ceil(combined.shape[0] * float(gate_fraction))), combined.shape[0]))
    threshold = float(np.sort(combined)[::-1][selected_count - 1])
    member_gate = baseline_member.detach().cpu() >= threshold
    nonmember_gate = baseline_nonmember.detach().cpu() >= threshold
    return member_gate, nonmember_gate, threshold, selected_count


def mix_scores(
    baseline_member: torch.Tensor,
    baseline_nonmember: torch.Tensor,
    defense_member: torch.Tensor,
    defense_nonmember: torch.Tensor,
    member_gate: torch.Tensor,
    nonmember_gate: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    return (
        torch.where(member_gate, defense_member.detach().cpu(), baseline_member.detach().cpu()),
        torch.where(nonmember_gate, defense_nonmember.detach().cpu(), baseline_nonmember.detach().cpu()),
    )


def score_surface(
    runtime_context,
    model: torch.nn.Module,
    member_loader,
    nonmember_loader,
    device: str,
    adaptive_query_repeats: int,
    dropout_activation_schedule: str,
    late_step_threshold: int,
) -> dict[str, Any]:
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
    member_scores, member_adaptive_scores, member_score_std = _score_loader(
        attacker,
        member_loader,
        device=device,
        adaptive_query_repeats=adaptive_query_repeats,
    )
    nonmember_scores, nonmember_adaptive_scores, nonmember_score_std = _score_loader(
        attacker,
        nonmember_loader,
        device=device,
        adaptive_query_repeats=adaptive_query_repeats,
    )
    return {
        "raw": {
            "member": member_scores,
            "nonmember": nonmember_scores,
            "metrics": tensor_metrics(member_scores, nonmember_scores),
        },
        "adaptive": {
            "member": member_adaptive_scores,
            "nonmember": nonmember_adaptive_scores,
            "metrics": tensor_metrics(member_adaptive_scores, nonmember_adaptive_scores),
            "score_std": {
                "member_mean": round(float(member_score_std.mean().item()), 6),
                "nonmember_mean": round(float(nonmember_score_std.mean().item()), 6),
            },
        },
    }


def serializable_scores(scores: torch.Tensor) -> list[float]:
    return [round(float(value), 6) for value in scores.detach().cpu().tolist()]


def main() -> int:
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = args.run_root or Path(f"workspaces/gray-box/runs/x158-h3-gated-runtime-gpu-scout-{timestamp}")
    run_root.mkdir(parents=True, exist_ok=True)
    started_at = time.perf_counter()

    try:
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

        baseline = score_surface(
            runtime_context=runtime_context,
            model=model,
            member_loader=member_loader,
            nonmember_loader=nonmember_loader,
            device=args.device,
            adaptive_query_repeats=args.adaptive_query_repeats,
            dropout_activation_schedule="off",
            late_step_threshold=late_step_threshold,
        )
        defended = score_surface(
            runtime_context=runtime_context,
            model=model,
            member_loader=member_loader,
            nonmember_loader=nonmember_loader,
            device=args.device,
            adaptive_query_repeats=args.adaptive_query_repeats,
            dropout_activation_schedule=args.dropout_activation_schedule,
            late_step_threshold=late_step_threshold,
        )

        mixed: dict[str, Any] = {}
        gate_info: dict[str, Any] = {}
        for mode in ("raw", "adaptive"):
            member_gate, nonmember_gate, gate_threshold, selected_count = select_gate(
                baseline[mode]["member"],
                baseline[mode]["nonmember"],
                args.gate_fraction,
            )
            mixed_member, mixed_nonmember = mix_scores(
                baseline[mode]["member"],
                baseline[mode]["nonmember"],
                defended[mode]["member"],
                defended[mode]["nonmember"],
                member_gate,
                nonmember_gate,
            )
            mixed[mode] = {
                "metrics": tensor_metrics(mixed_member, mixed_nonmember),
                "delta_vs_baseline": {
                    key: round(float(tensor_metrics(mixed_member, mixed_nonmember)[key]) - float(baseline[mode]["metrics"][key]), 6)
                    for key in ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")
                },
                "delta_vs_all_steps": {
                    key: round(float(tensor_metrics(mixed_member, mixed_nonmember)[key]) - float(defended[mode]["metrics"][key]), 6)
                    for key in ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")
                },
            }
            gate_info[mode] = {
                "gate_threshold": round(float(gate_threshold), 6),
                "selected_count": int(selected_count),
                "gate_fraction_actual": round(
                    float((member_gate.sum().item() + nonmember_gate.sum().item()) / (member_gate.shape[0] + nonmember_gate.shape[0])),
                    6,
                ),
                "member_gate_fraction": round(float(member_gate.float().mean().item()), 6),
                "nonmember_gate_fraction": round(float(nonmember_gate.float().mean().item()), 6),
            }

        adaptive_mixed = mixed["adaptive"]["metrics"]
        adaptive_defended = defended["adaptive"]["metrics"]
        verdict = (
            "positive but bounded"
            if adaptive_mixed["tpr_at_1pct_fpr"] <= adaptive_defended["tpr_at_1pct_fpr"]
            and adaptive_mixed["tpr_at_0_1pct_fpr"] <= adaptive_defended["tpr_at_0_1pct_fpr"]
            else "negative but useful"
        )

        summary = {
            "status": "ready",
            "task": "X-158 H3 suspicion-gated all-steps dropout runtime GPU scout",
            "mode": "bounded-gpu-scout",
            "device": args.device,
            "gpu_release": "one bounded 64/64 scout",
            "admitted_change": "none",
            "inputs": {
                "config": str(args.config),
                "repo_root": str(args.repo_root),
                "member_split_root": str(args.member_split_root),
                "packet_size": int(args.packet_size),
                "batch_size": int(args.batch_size),
                "adaptive_query_repeats": int(args.adaptive_query_repeats),
                "gate_fraction": float(args.gate_fraction),
                "dropout_activation_schedule": args.dropout_activation_schedule,
                "selection_signal": "same-packet baseline PIA score tail",
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
            "baseline": {
                "raw_metrics": baseline["raw"]["metrics"],
                "adaptive_metrics": baseline["adaptive"]["metrics"],
                "adaptive_score_std": baseline["adaptive"]["score_std"],
            },
            "all_steps": {
                "raw_metrics": defended["raw"]["metrics"],
                "adaptive_metrics": defended["adaptive"]["metrics"],
                "adaptive_score_std": defended["adaptive"]["score_std"],
            },
            "gate": gate_info,
            "selective_gated": mixed,
            "verdict": verdict,
            "promotion_allowed": False,
            "next_gpu_candidate": "none until X-159 review freezes a stronger implementation reason",
            "notes": [
                "This scout scores both baseline and all-steps surfaces on one fresh 64/64 packet, then routes only the top PIA-risk tail through defended scores.",
                "It is not a deployed gated runner and does not prove privacy; it only tests whether a real GPU packet preserves the cached low-FPR pattern.",
                "Promotion requires a larger packet plus budget-fixed repeated-query attacker and quality/cost audit.",
            ],
        }
        (run_root / "scores.json").write_text(
            json.dumps(
                {
                    "member_indices": [int(value) for value in member_indices],
                    "nonmember_indices": [int(value) for value in nonmember_indices],
                    "baseline_member_scores": serializable_scores(baseline["adaptive"]["member"]),
                    "baseline_nonmember_scores": serializable_scores(baseline["adaptive"]["nonmember"]),
                    "all_steps_member_scores": serializable_scores(defended["adaptive"]["member"]),
                    "all_steps_nonmember_scores": serializable_scores(defended["adaptive"]["nonmember"]),
                },
                indent=2,
                ensure_ascii=True,
            ),
            encoding="utf-8",
        )
    except RuntimeError as exc:
        summary = {
            "status": "blocked",
            "task": "X-158 H3 suspicion-gated all-steps dropout runtime GPU scout",
            "mode": "bounded-gpu-scout",
            "device": args.device,
            "error": f"{type(exc).__name__}: {exc}",
            "verdict": "blocked",
            "next_gpu_candidate": "none until GPU memory or runtime blocker is cleared",
            "notes": [
                "The scout is intentionally small; if it fails on memory, do not expand the packet.",
            ],
        }
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    (run_root / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
