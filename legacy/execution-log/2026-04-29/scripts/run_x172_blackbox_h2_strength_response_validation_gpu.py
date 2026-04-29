from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch

import run_x168_blackbox_h2_strength_response_gpu_scout as x168
import run_x171_blackbox_h3_frequency_filter_cache_ablation as x171
from diffaudit.attacks.pia import probe_pia_assets
from diffaudit.attacks.pia_adapter import _build_pia_packet_loader, load_pia_model, prepare_pia_runtime
from diffaudit.config import load_audit_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run X-172 black-box H2 strength-response bounded non-overlap validation."
    )
    parser.add_argument("--config", type=Path, default=Path("configs/attacks/pia_mainline_canonical.yaml"))
    parser.add_argument("--run-root", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, default=Path("external/PIA"))
    parser.add_argument("--member-split-root", type=Path, default=Path("external/PIA/DDPM"))
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--packet-size", type=int, default=128)
    parser.add_argument("--split-offset", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--timesteps", type=int, nargs="+", default=list(x168.DEFAULT_TIMESTEPS))
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--denoise-stride", type=int, default=10)
    parser.add_argument("--seed", type=int, default=172)
    parser.add_argument("--holdout-splits", type=int, default=7)
    parser.add_argument("--bootstrap-iters", type=int, default=200)
    parser.add_argument("--frequency-cutoff", type=float, default=0.5)
    parser.add_argument("--no-save-responses", action="store_true")
    parser.add_argument("--task-label", default="X-172 black-box H2 strength-response non-overlap validation")
    parser.add_argument("--gpu-release-label", default="one bounded non-overlap 128/128 H2 validation rung")
    parser.add_argument(
        "--next-gpu-candidate-label",
        default="none until X173 post-validation review decides whether an independent 256/256 or comparator rung is justified",
    )
    parser.add_argument(
        "--cpu-sidecar-label",
        default="X173 post-validation boundary review plus I-A / cross-box boundary maintenance",
    )
    return parser.parse_args()


def select_split_indices(member_split_path: str | Path, membership: str, offset: int, packet_size: int) -> list[int]:
    split_payload = np.load(member_split_path)
    if membership == "member":
        raw_indices = split_payload["mia_train_idxs"].tolist()
    elif membership == "nonmember":
        raw_indices = split_payload["mia_eval_idxs"].tolist()
    else:
        raise ValueError(f"Unknown membership: {membership}")
    start = int(offset)
    end = start + int(packet_size)
    selected = [int(value) for value in raw_indices[start:end]]
    if len(selected) != int(packet_size):
        raise ValueError(
            f"Requested {packet_size} {membership} samples at offset {offset}, but only got {len(selected)}"
        )
    return selected


def compute_lowpass_min_distances(
    inputs: np.ndarray,
    responses: np.ndarray,
    cutoff: float,
) -> np.ndarray:
    mask = x171.build_mask(int(inputs.shape[-2]), int(inputs.shape[-1]), "lowpass", cutoff=float(cutoff))
    filtered_inputs = x171.apply_frequency_mask(inputs.astype(np.float32), mask)
    filtered_responses = x171.apply_frequency_mask(responses.astype(np.float32), mask)
    delta = filtered_responses - filtered_inputs[:, None, None, :, :, :]
    distances = np.sqrt(np.mean(delta * delta, axis=(3, 4, 5))).astype(np.float32)
    return distances.min(axis=2).astype(np.float32)


def sanitize(value: Any) -> Any:
    return x168.json_sanitize(value)


def main() -> int:
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = args.run_root or Path(f"workspaces/black-box/runs/x172-h2-strength-response-validation-{timestamp}")
    run_root.mkdir(parents=True, exist_ok=True)
    started_at = time.perf_counter()

    try:
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
        alpha_bars = x168.build_alpha_bars(args.device)

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

        member_inputs, member_responses, member_distances = x168.collect_strength_responses(
            model=model,
            loader=member_loader,
            device=args.device,
            alpha_bars=alpha_bars,
            timesteps=timesteps,
            repeats=args.repeats,
            denoise_stride=args.denoise_stride,
            seed=args.seed,
            sample_offset=0,
        )
        nonmember_inputs, nonmember_responses, nonmember_distances = x168.collect_strength_responses(
            model=model,
            loader=nonmember_loader,
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

        raw_simple = x168.evaluate_simple_baselines(
            labels=labels,
            min_distances=min_distances,
            timesteps=timesteps,
            seed=args.seed,
            bootstrap_iters=args.bootstrap_iters,
        )
        raw_logistic = x168.evaluate_logistic_holdout(
            labels=labels,
            features=min_distances.astype(np.float32),
            seed=args.seed,
            split_count=args.holdout_splits,
            test_size=0.5,
            bootstrap_iters=args.bootstrap_iters,
        )

        lowpass_min_distances = compute_lowpass_min_distances(inputs, responses, args.frequency_cutoff)
        lowpass_simple = x171.evaluate_h2_simple_scores(
            labels=labels,
            min_distances=lowpass_min_distances,
            timesteps=np.asarray(timesteps, dtype=np.int64),
            seed=args.seed + 500,
            bootstrap_iters=args.bootstrap_iters,
        )
        lowpass_logistic = x171.evaluate_logistic(
            labels=labels,
            features=lowpass_min_distances.astype(np.float32),
            seed=args.seed + 500,
            repeats=args.holdout_splits,
            bootstrap_iters=args.bootstrap_iters,
        )

        raw_metrics = raw_logistic["aggregate_metrics"]
        lowpass_metrics = lowpass_logistic["aggregate_metrics"]
        raw_best_simple_low = raw_simple["best_by_low_fpr"]["metrics"]
        raw_best_simple_auc = raw_simple["best_by_auc"]["metrics"]
        lowpass_tail_retained = (
            float(lowpass_metrics["tpr_at_1pct_fpr"]) >= 0.75 * float(raw_metrics["tpr_at_1pct_fpr"])
            and float(lowpass_metrics["tpr_at_0_1pct_fpr"]) >= 0.75 * float(raw_metrics["tpr_at_0_1pct_fpr"])
        )
        raw_beats_simple_low = (
            float(raw_metrics["tpr_at_1pct_fpr"]) > float(raw_best_simple_low["tpr_at_1pct_fpr"])
            and float(raw_metrics["tpr_at_0_1pct_fpr"]) >= float(raw_best_simple_low["tpr_at_0_1pct_fpr"])
        )
        raw_auc_not_worse = float(raw_metrics["auc"]) >= float(raw_best_simple_auc["auc"])
        validation_passed = raw_beats_simple_low and raw_auc_not_worse and lowpass_tail_retained
        verdict = "positive but bounded validation" if validation_passed else "negative but useful"

        scores_payload = {
            "labels": labels.tolist(),
            "member_indices": [int(value) for value in member_indices],
            "nonmember_indices": [int(value) for value in nonmember_indices],
            "timesteps": timesteps,
            "raw_min_distances_rmse": min_distances.round(8).tolist(),
            "lowpass_min_distances_rmse": lowpass_min_distances.round(8).tolist(),
            "raw_logistic_aggregate_scores": raw_logistic["aggregate_scores"],
            "lowpass_logistic_aggregate_scores": lowpass_logistic["aggregate_scores"],
        }
        (run_root / "scores.json").write_text(
            json.dumps(sanitize(scores_payload), indent=2, ensure_ascii=True),
            encoding="utf-8",
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

        summary = {
            "status": "ready",
            "task": args.task_label,
            "mode": "bounded-gpu-validation",
            "track": "black-box",
            "method": "H2 strength-response curve with H3 lowpass boundary check",
            "device": args.device,
            "gpu_release": args.gpu_release_label,
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
            },
            "runtime": {
                "weights_key": weights_key,
                "member_indices": [int(value) for value in member_indices],
                "nonmember_indices": [int(value) for value in nonmember_indices],
                "wall_clock_seconds": round(time.perf_counter() - started_at, 6),
            },
            "artifact_paths": {
                "summary": str(run_root / "summary.json"),
                "scores": str(run_root / "scores.json"),
                "response_cache": str(response_cache_path) if response_cache_path is not None else None,
            },
            "raw_h2_baselines": raw_simple,
            "raw_h2_logistic": raw_logistic,
            "lowpass_h2_baselines": lowpass_simple,
            "lowpass_h2_logistic": lowpass_logistic,
            "gates": {
                "raw_best_simple_by_low_fpr": raw_simple["best_by_low_fpr"],
                "raw_logistic_minus_best_simple_by_low_fpr": x168.metric_delta(raw_metrics, raw_best_simple_low),
                "raw_beats_simple_low_fpr": bool(raw_beats_simple_low),
                "raw_auc_not_worse_than_best_simple_auc": bool(raw_auc_not_worse),
                "lowpass_tail_retained": bool(lowpass_tail_retained),
                "lowpass_logistic_minus_raw_logistic": x168.metric_delta(lowpass_metrics, raw_metrics),
                "validation_passed": bool(validation_passed),
                "promotion_allowed": False,
            },
            "verdict": verdict,
            "next_gpu_candidate": args.next_gpu_candidate_label,
            "cpu_sidecar": args.cpu_sidecar_label,
            "notes": [
                f"This validation packet starts at split offset {int(args.split_offset)}.",
                "The primary scorer remains raw H2 strength-response logistic; lowpass H3 is a boundary check.",
                "A positive validation result still does not promote H2 to admitted evidence without comparator and larger validation review.",
            ],
        }
    except Exception as exc:
        summary = {
            "status": "blocked",
            "task": args.task_label,
            "mode": "bounded-gpu-validation",
            "track": "black-box",
            "device": args.device,
            "error": f"{type(exc).__name__}: {exc}",
            "verdict": "blocked",
            "next_gpu_candidate": args.next_gpu_candidate_label,
        }
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    (run_root / "summary.json").write_text(
        json.dumps(sanitize(summary), indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    print(json.dumps(sanitize(summary), indent=2, ensure_ascii=False))
    return 0 if summary["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
