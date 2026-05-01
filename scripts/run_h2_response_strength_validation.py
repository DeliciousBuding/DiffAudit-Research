from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch

from diffaudit.attacks.h2_response_strength import (
    DEFAULT_TIMESTEPS,
    PRIMARY_SCORERS,
    build_alpha_bars,
    collect_strength_responses,
    compute_lowpass_min_distances,
    evaluate_h2_response_cache,
    evaluate_validation_gate,
    metric_delta,
    select_split_indices,
)
from diffaudit.attacks.pia import probe_pia_assets
from diffaudit.attacks.pia_adapter import _build_pia_packet_loader, load_pia_model, prepare_pia_runtime
from diffaudit.config import load_audit_config


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize(item) for item in value]
    if isinstance(value, np.ndarray):
        return _sanitize(value.tolist())
    if isinstance(value, np.generic):
        return _sanitize(value.item())
    if isinstance(value, Path):
        return str(value)
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one bounded black-box H2 response-strength validation packet."
    )
    parser.add_argument("--config", type=Path, default=Path("configs/attacks/pia_mainline_canonical.yaml"))
    parser.add_argument("--run-root", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, default=Path("external/PIA"))
    parser.add_argument("--member-split-root", type=Path, default=Path("external/PIA/DDPM"))
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--packet-size", type=int, default=512)
    parser.add_argument("--split-offset", type=int, default=512)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--timesteps", type=int, nargs="+", default=list(DEFAULT_TIMESTEPS))
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--denoise-stride", type=int, default=10)
    parser.add_argument("--seed", type=int, default=176)
    parser.add_argument("--holdout-repeats", type=int, default=7)
    parser.add_argument("--bootstrap-iters", type=int, default=200)
    parser.add_argument("--frequency-cutoff", type=float, default=0.5)
    parser.add_argument("--primary-scorer", choices=PRIMARY_SCORERS, default="raw_h2_logistic")
    parser.add_argument("--no-save-responses", action="store_true")
    return parser.parse_args()


def _validate_args(args: argparse.Namespace) -> list[int]:
    if args.packet_size <= 0:
        raise ValueError("--packet-size must be positive")
    if args.split_offset < 0:
        raise ValueError("--split-offset must be non-negative")
    if args.repeats <= 0:
        raise ValueError("--repeats must be positive")
    if args.denoise_stride <= 0:
        raise ValueError("--denoise-stride must be positive")
    timesteps = [int(value) for value in args.timesteps]
    if sorted(timesteps) != timesteps or len(set(timesteps)) != len(timesteps):
        raise ValueError("--timesteps must be sorted unique values")
    return timesteps


def main() -> int:
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = args.run_root or Path(f"workspaces/black-box/runs/h2-response-strength-validation-{timestamp}")
    run_root.mkdir(parents=True, exist_ok=True)
    started_at = time.perf_counter()

    try:
        timesteps = _validate_args(args)
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
        alpha_bars = build_alpha_bars(args.device)

        split_root = Path(args.member_split_root) if args.member_split_root else Path(args.repo_root) / "DDPM"
        asset_summary = probe_pia_assets(
            dataset=runtime_context.plan.dataset,
            dataset_root=runtime_context.plan.data_root,
            model_dir=runtime_context.plan.model_dir,
            member_split_root=split_root,
        )
        split_path = asset_summary["paths"]["member_split"]
        member_indices = select_split_indices(split_path, "member", args.split_offset, args.packet_size)
        nonmember_indices = select_split_indices(split_path, "nonmember", args.split_offset, args.packet_size)
        member_loader = _build_pia_packet_loader(
            dataset=runtime_context.plan.dataset,
            dataset_dir=asset_summary["paths"]["dataset_dir"],
            packet_indices=member_indices,
            batch_size=args.batch_size,
        )
        nonmember_loader = _build_pia_packet_loader(
            dataset=runtime_context.plan.dataset,
            dataset_dir=asset_summary["paths"]["dataset_dir"],
            packet_indices=nonmember_indices,
            batch_size=args.batch_size,
        )

        member_inputs, member_responses, member_distances = collect_strength_responses(
            model,
            member_loader,
            device=args.device,
            alpha_bars=alpha_bars,
            timesteps=timesteps,
            repeats=args.repeats,
            denoise_stride=args.denoise_stride,
            seed=args.seed,
            sample_offset=0,
        )
        nonmember_inputs, nonmember_responses, nonmember_distances = collect_strength_responses(
            model,
            nonmember_loader,
            device=args.device,
            alpha_bars=alpha_bars,
            timesteps=timesteps,
            repeats=args.repeats,
            denoise_stride=args.denoise_stride,
            seed=args.seed,
            sample_offset=len(member_indices),
        )

        labels = np.concatenate(
            [
                np.ones(len(member_indices), dtype=np.int64),
                np.zeros(len(nonmember_indices), dtype=np.int64),
            ]
        )
        inputs = np.concatenate(
            [
                member_inputs.numpy().astype(np.float32),
                nonmember_inputs.numpy().astype(np.float32),
            ],
            axis=0,
        )
        responses = np.concatenate([member_responses, nonmember_responses], axis=0).astype(np.float32)
        distances = np.concatenate([member_distances, nonmember_distances], axis=0).astype(np.float32)
        min_distances = distances.min(axis=2).astype(np.float32)
        lowpass_min_distances = compute_lowpass_min_distances(inputs, responses, cutoff=args.frequency_cutoff)

        raw_h2 = evaluate_h2_response_cache(
            labels,
            np.asarray(timesteps, dtype=np.int64),
            min_distances,
            seed=args.seed,
            holdout_repeats=args.holdout_repeats,
            bootstrap_iters=args.bootstrap_iters,
        )
        lowpass_h2 = evaluate_h2_response_cache(
            labels,
            np.asarray(timesteps, dtype=np.int64),
            lowpass_min_distances,
            seed=args.seed + 500,
            holdout_repeats=args.holdout_repeats,
            bootstrap_iters=args.bootstrap_iters,
        )

        response_cache_path = None
        if not args.no_save_responses:
            response_cache_path = run_root / "response-cache.npz"
            np.savez_compressed(
                response_cache_path,
                labels=labels.astype(np.int64),
                member_indices=np.asarray(member_indices, dtype=np.int64),
                nonmember_indices=np.asarray(nonmember_indices, dtype=np.int64),
                timesteps=np.asarray(timesteps, dtype=np.int64),
                split_offset=np.asarray([args.split_offset], dtype=np.int64),
                inputs=inputs.astype(np.float16),
                responses=responses.astype(np.float16),
                distances_rmse=distances.astype(np.float32),
                min_distances_rmse=min_distances.astype(np.float32),
                lowpass_cutoff=np.asarray([args.frequency_cutoff], dtype=np.float32),
                lowpass_min_distances_rmse=lowpass_min_distances.astype(np.float32),
            )

        raw_metrics = raw_h2["logistic"]["aggregate_metrics"]
        raw_best_simple_low = raw_h2["simple"]["best_by_low_fpr"]["metrics"]
        raw_best_simple_auc = raw_h2["simple"]["best_by_auc"]["metrics"]
        lowpass_metrics = lowpass_h2["logistic"]["aggregate_metrics"]
        validation_gate = evaluate_validation_gate(
            primary_scorer=args.primary_scorer,
            raw_metrics=raw_metrics,
            lowpass_metrics=lowpass_metrics,
            raw_best_simple_low=raw_best_simple_low,
            raw_best_simple_auc=raw_best_simple_auc,
        )
        validation_passed = bool(validation_gate["validation_passed"])
        summary = {
            "status": "ready",
            "task": "H2 response-strength validation",
            "mode": "bounded-gpu-validation",
            "track": "black-box",
            "method": "H2 response-strength curve with lowpass boundary check",
            "device": args.device,
            "admitted_change": "none",
            "inputs": {
                "config": str(args.config),
                "repo_root": str(args.repo_root),
                "member_split_root": str(args.member_split_root),
                "packet_size": int(args.packet_size),
                "split_offset": int(args.split_offset),
                "batch_size": int(args.batch_size),
                "timesteps": timesteps,
                "repeats": int(args.repeats),
                "denoise_stride": int(args.denoise_stride),
                "seed": int(args.seed),
                "frequency_cutoff": float(args.frequency_cutoff),
                "primary_scorer": args.primary_scorer,
            },
            "runtime": {
                "weights_key": weights_key,
                "member_indices": [int(value) for value in member_indices],
                "nonmember_indices": [int(value) for value in nonmember_indices],
                "wall_clock_seconds": round(time.perf_counter() - started_at, 6),
            },
            "artifact_paths": {
                "summary": str(run_root / "summary.json"),
                "response_cache": str(response_cache_path) if response_cache_path is not None else None,
            },
            "raw_h2": raw_h2,
            "lowpass_h2": lowpass_h2,
            "gates": {
                "raw_best_simple_by_low_fpr": raw_h2["simple"]["best_by_low_fpr"],
                "raw_logistic_minus_best_simple_by_low_fpr": metric_delta(raw_metrics, raw_best_simple_low),
                "lowpass_logistic_minus_raw_logistic": metric_delta(lowpass_metrics, raw_metrics),
                "validation_gate": validation_gate,
                "validation_passed": bool(validation_passed),
                "promotion_allowed": False,
            },
            "verdict": "positive but bounded validation" if validation_passed else "negative but useful",
            "notes": [
                "This runner is a stable successor to archived H2 X-run scripts.",
                "A positive result remains candidate evidence until cross-asset or stronger black-box comparator review.",
            ],
        }
    except Exception as exc:
        summary = {
            "status": "blocked",
            "task": "H2 response-strength validation",
            "mode": "bounded-gpu-validation",
            "track": "black-box",
            "device": args.device,
            "error": f"{type(exc).__name__}: {exc}",
            "verdict": "blocked",
        }
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    (run_root / "summary.json").write_text(json.dumps(_sanitize(summary), indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(_sanitize(summary), indent=2, ensure_ascii=False))
    return 0 if summary["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
