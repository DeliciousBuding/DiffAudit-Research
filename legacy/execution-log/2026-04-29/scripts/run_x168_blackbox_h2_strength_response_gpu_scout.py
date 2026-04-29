from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from diffaudit.attacks.pia import probe_pia_assets
from diffaudit.attacks.pia_adapter import (
    _build_pia_subset_loader,
    _compute_auc,
    _compute_threshold_metrics,
    load_pia_model,
    prepare_pia_runtime,
)
from diffaudit.config import load_audit_config


DEFAULT_TIMESTEPS = (40, 80, 120, 160)
METRIC_KEYS = ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run X-168 black-box H2 strength-response bounded GPU scout."
    )
    parser.add_argument("--config", type=Path, default=Path("configs/attacks/pia_mainline_canonical.yaml"))
    parser.add_argument("--run-root", type=Path, default=None)
    parser.add_argument("--repo-root", type=Path, default=Path("external/PIA"))
    parser.add_argument("--member-split-root", type=Path, default=Path("external/PIA/DDPM"))
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--packet-size", type=int, default=64)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--timesteps", type=int, nargs="+", default=list(DEFAULT_TIMESTEPS))
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--denoise-stride", type=int, default=10)
    parser.add_argument("--seed", type=int, default=168)
    parser.add_argument("--holdout-splits", type=int, default=7)
    parser.add_argument("--holdout-test-size", type=float, default=0.5)
    parser.add_argument("--bootstrap-iters", type=int, default=200)
    parser.add_argument("--no-save-responses", action="store_true")
    return parser.parse_args()


def metric_delta(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    return {key: round(float(left[key]) - float(right[key]), 6) for key in METRIC_KEYS}


def score_metrics(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    member_scores = scores[labels == 1]
    nonmember_scores = scores[labels == 0]
    return {
        "auc": round(float(_compute_auc(torch.tensor(member_scores), torch.tensor(nonmember_scores))), 6),
        **_compute_threshold_metrics(member_scores.astype(float), nonmember_scores.astype(float)),
        "member_score_mean": round(float(np.mean(member_scores)), 6),
        "nonmember_score_mean": round(float(np.mean(nonmember_scores)), 6),
    }


def bootstrap_metric_ci(
    labels: np.ndarray,
    scores: np.ndarray,
    seed: int,
    iters: int,
) -> dict[str, dict[str, float]]:
    if iters <= 0:
        return {}
    rng = np.random.default_rng(seed)
    member_scores = scores[labels == 1]
    nonmember_scores = scores[labels == 0]
    values: dict[str, list[float]] = {key: [] for key in METRIC_KEYS}
    for _ in range(iters):
        boot_member = rng.choice(member_scores, size=member_scores.shape[0], replace=True)
        boot_nonmember = rng.choice(nonmember_scores, size=nonmember_scores.shape[0], replace=True)
        boot_labels = np.concatenate(
            [
                np.ones(boot_member.shape[0], dtype=np.int64),
                np.zeros(boot_nonmember.shape[0], dtype=np.int64),
            ]
        )
        boot_scores = np.concatenate([boot_member, boot_nonmember])
        metrics = score_metrics(boot_labels, boot_scores)
        for key in METRIC_KEYS:
            values[key].append(float(metrics[key]))
    return {
        key: {
            "p025": round(float(np.percentile(items, 2.5)), 6),
            "p975": round(float(np.percentile(items, 97.5)), 6),
        }
        for key, items in values.items()
    }


def build_alpha_bars(device: str, timesteps: int = 1000) -> torch.Tensor:
    betas = torch.linspace(0.0001, 0.02, timesteps, device=device, dtype=torch.float32)
    return torch.cumprod(1.0 - betas, dim=0)


def partial_ddim_denoise(
    model: torch.nn.Module,
    x0_pixels: torch.Tensor,
    timestep: int,
    alpha_bars: torch.Tensor,
    generator: torch.Generator,
    stride: int,
    device: str,
) -> torch.Tensor:
    x0 = x0_pixels.to(device) * 2.0 - 1.0
    strength_t = int(timestep)
    if strength_t <= 0:
        return torch.clamp(x0_pixels, 0.0, 1.0).detach().cpu()
    if strength_t >= int(alpha_bars.shape[0]):
        raise ValueError(f"timestep must be < {alpha_bars.shape[0]}: {strength_t}")

    noise = torch.randn(x0.shape, generator=generator, device=device, dtype=x0.dtype)
    alpha_t = alpha_bars[strength_t].view(1, 1, 1, 1)
    x_t = alpha_t.sqrt() * x0 + (1.0 - alpha_t).sqrt() * noise

    current_t = strength_t
    step = max(int(stride), 1)
    while current_t > 0:
        previous_t = max(current_t - step, 0)
        t_tensor = torch.full((x_t.shape[0],), current_t, device=device, dtype=torch.long)
        eps = model(x_t, t=t_tensor)

        alpha_cur = alpha_bars[current_t].view(1, 1, 1, 1)
        alpha_prev = alpha_bars[previous_t].view(1, 1, 1, 1)
        x0_pred = (x_t - (1.0 - alpha_cur).sqrt() * eps) / alpha_cur.sqrt()
        x0_pred = torch.clamp(x0_pred, -1.0, 1.0)
        if previous_t == 0:
            x_t = x0_pred
        else:
            x_t = alpha_prev.sqrt() * x0_pred + (1.0 - alpha_prev).sqrt() * eps
        current_t = previous_t

    return torch.clamp((x_t + 1.0) / 2.0, 0.0, 1.0).detach().cpu()


def collect_strength_responses(
    model: torch.nn.Module,
    loader,
    device: str,
    alpha_bars: torch.Tensor,
    timesteps: list[int],
    repeats: int,
    denoise_stride: int,
    seed: int,
    sample_offset: int,
) -> tuple[torch.Tensor, np.ndarray, np.ndarray]:
    inputs: list[torch.Tensor] = []
    response_batches: list[np.ndarray] = []
    distance_batches: list[np.ndarray] = []
    running_offset = sample_offset
    model.eval()
    with torch.no_grad():
        for batch, _ in loader:
            batch = batch.detach().cpu()
            batch_responses = np.zeros(
                (batch.shape[0], len(timesteps), repeats, batch.shape[1], batch.shape[2], batch.shape[3]),
                dtype=np.float16,
            )
            batch_distances = np.zeros((batch.shape[0], len(timesteps), repeats), dtype=np.float32)
            for strength_idx, timestep in enumerate(timesteps):
                for repeat_idx in range(repeats):
                    generator = torch.Generator(device=device)
                    generator.manual_seed(
                        int(seed)
                        + int(timestep) * 100_000
                        + int(repeat_idx) * 10_000
                        + int(running_offset)
                    )
                    output = partial_ddim_denoise(
                        model=model,
                        x0_pixels=batch,
                        timestep=int(timestep),
                        alpha_bars=alpha_bars,
                        generator=generator,
                        stride=denoise_stride,
                        device=device,
                    )
                    distances = torch.sqrt(((output - batch) ** 2).mean(dim=(1, 2, 3)))
                    batch_responses[:, strength_idx, repeat_idx] = output.numpy().astype(np.float16)
                    batch_distances[:, strength_idx, repeat_idx] = distances.numpy().astype(np.float32)
            inputs.append(batch)
            response_batches.append(batch_responses)
            distance_batches.append(batch_distances)
            running_offset += int(batch.shape[0])
    return (
        torch.cat(inputs, dim=0),
        np.concatenate(response_batches, axis=0),
        np.concatenate(distance_batches, axis=0),
    )


def evaluate_simple_baselines(
    labels: np.ndarray,
    min_distances: np.ndarray,
    timesteps: list[int],
    seed: int,
    bootstrap_iters: int,
) -> dict[str, Any]:
    baselines: dict[str, Any] = {}
    single_strengths: list[dict[str, Any]] = []
    for idx, timestep in enumerate(timesteps):
        scores = -min_distances[:, idx]
        metrics = score_metrics(labels, scores)
        single_strengths.append(
            {
                "timestep": int(timestep),
                "score_orientation": "negative_min_distance_higher_is_member",
                "metrics": metrics,
                "ci95": bootstrap_metric_ci(labels, scores, seed + idx, bootstrap_iters),
            }
        )
    baselines["single_strengths"] = single_strengths

    mean_scores = -min_distances.mean(axis=1)
    if len(timesteps) > 1:
        slope = np.polyfit(np.asarray(timesteps, dtype=float), min_distances.T, deg=1)[0]
    else:
        slope = np.zeros(min_distances.shape[0], dtype=float)
    slope_scores = -slope
    baselines["mean_min_distance"] = {
        "score_orientation": "negative_mean_min_distance_higher_is_member",
        "metrics": score_metrics(labels, mean_scores),
        "ci95": bootstrap_metric_ci(labels, mean_scores, seed + 101, bootstrap_iters),
    }
    baselines["negative_slope"] = {
        "score_orientation": "negative_distance_slope_higher_is_member",
        "metrics": score_metrics(labels, slope_scores),
        "ci95": bootstrap_metric_ci(labels, slope_scores, seed + 102, bootstrap_iters),
    }

    flat_candidates = single_strengths + [
        {"name": "mean_min_distance", "metrics": baselines["mean_min_distance"]["metrics"]},
        {"name": "negative_slope", "metrics": baselines["negative_slope"]["metrics"]},
    ]
    best_by_auc = max(flat_candidates, key=lambda item: float(item["metrics"]["auc"]))
    best_by_low_fpr = max(
        flat_candidates,
        key=lambda item: (
            float(item["metrics"]["tpr_at_1pct_fpr"]),
            float(item["metrics"]["tpr_at_0_1pct_fpr"]),
            float(item["metrics"]["auc"]),
        ),
    )
    baselines["best_by_auc"] = {
        "name": best_by_auc.get("name", f"single_timestep_{best_by_auc.get('timestep')}"),
        "metrics": best_by_auc["metrics"],
    }
    baselines["best_by_low_fpr"] = {
        "name": best_by_low_fpr.get("name", f"single_timestep_{best_by_low_fpr.get('timestep')}"),
        "metrics": best_by_low_fpr["metrics"],
    }
    return baselines


def evaluate_logistic_holdout(
    labels: np.ndarray,
    features: np.ndarray,
    seed: int,
    split_count: int,
    test_size: float,
    bootstrap_iters: int,
) -> dict[str, Any]:
    del test_size
    per_class_count = int(min((labels == 1).sum(), (labels == 0).sum()))
    fold_count = max(2, min(4, per_class_count))
    splitter = RepeatedStratifiedKFold(
        n_splits=fold_count,
        n_repeats=split_count,
        random_state=seed,
    )
    prediction_sum = np.zeros(labels.shape[0], dtype=np.float64)
    prediction_count = np.zeros(labels.shape[0], dtype=np.int64)
    fold_metrics: list[dict[str, Any]] = []
    fold_coefficients: list[list[float]] = []
    for fold_idx, (train_idx, test_idx) in enumerate(splitter.split(features, labels)):
        classifier = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000, class_weight="balanced", random_state=seed + fold_idx),
        )
        classifier.fit(features[train_idx], labels[train_idx])
        fold_scores = classifier.predict_proba(features[test_idx])[:, 1]
        prediction_sum[test_idx] += fold_scores
        prediction_count[test_idx] += 1
        fold_metrics.append(
            {
                "fold": int(fold_idx),
                "train_size": int(train_idx.shape[0]),
                "test_size": int(test_idx.shape[0]),
                "metrics": score_metrics(labels[test_idx], fold_scores),
            }
        )
        logreg = classifier.named_steps["logisticregression"]
        fold_coefficients.append([round(float(value), 6) for value in logreg.coef_[0].tolist()])

    if not np.all(prediction_count > 0):
        missing = np.where(prediction_count == 0)[0].tolist()
        raise RuntimeError(f"Some samples were never evaluated by holdout splits: {missing[:8]}")
    aggregate_scores = prediction_sum / prediction_count
    aggregate_metrics = score_metrics(labels, aggregate_scores)
    return {
        "score_orientation": "holdout_predicted_member_probability",
        "features": "4-D vector of min seed-to-output RMSE per timestep",
        "splitter": {
            "name": "RepeatedStratifiedKFold",
            "n_splits": int(fold_count),
            "n_repeats": int(split_count),
            "random_state": int(seed),
        },
        "aggregate_metrics": aggregate_metrics,
        "aggregate_ci95": bootstrap_metric_ci(labels, aggregate_scores, seed + 301, bootstrap_iters),
        "fold_metrics": fold_metrics,
        "mean_coefficients": [
            round(float(value), 6)
            for value in np.asarray(fold_coefficients, dtype=float).mean(axis=0).tolist()
        ],
        "prediction_count": {
            "min": int(prediction_count.min()),
            "max": int(prediction_count.max()),
            "mean": round(float(prediction_count.mean()), 6),
        },
        "aggregate_scores": [round(float(value), 6) for value in aggregate_scores.tolist()],
    }


def json_sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): json_sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [json_sanitize(item) for item in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def main() -> int:
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = args.run_root or Path(f"workspaces/black-box/runs/x168-h2-strength-response-gpu-scout-{timestamp}")
    run_root.mkdir(parents=True, exist_ok=True)
    started_at = time.perf_counter()
    summary: dict[str, Any]

    try:
        if args.repeats <= 0:
            raise ValueError("--repeats must be positive")
        if args.packet_size <= 0:
            raise ValueError("--packet-size must be positive")
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
        alpha_bars = build_alpha_bars(args.device)

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

        member_inputs, member_responses, member_distances = collect_strength_responses(
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
        nonmember_inputs, nonmember_responses, nonmember_distances = collect_strength_responses(
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
        distances = np.concatenate([member_distances, nonmember_distances], axis=0)
        min_distances = distances.min(axis=2)
        features = min_distances.astype(np.float32)

        baselines = evaluate_simple_baselines(
            labels=labels,
            min_distances=min_distances,
            timesteps=timesteps,
            seed=args.seed,
            bootstrap_iters=args.bootstrap_iters,
        )
        logistic = evaluate_logistic_holdout(
            labels=labels,
            features=features,
            seed=args.seed,
            split_count=args.holdout_splits,
            test_size=args.holdout_test_size,
            bootstrap_iters=args.bootstrap_iters,
        )

        best_simple = baselines["best_by_low_fpr"]["metrics"]
        logistic_metrics = logistic["aggregate_metrics"]
        low_fpr_improved = (
            float(logistic_metrics["tpr_at_1pct_fpr"]) > float(best_simple["tpr_at_1pct_fpr"])
            and float(logistic_metrics["tpr_at_0_1pct_fpr"]) >= float(best_simple["tpr_at_0_1pct_fpr"])
        )
        auc_not_worse = float(logistic_metrics["auc"]) >= float(baselines["best_by_auc"]["metrics"]["auc"])
        verdict = "positive but bounded" if low_fpr_improved and auc_not_worse else "negative but useful"

        scores_payload = {
            "labels": labels.tolist(),
            "member_indices": [int(value) for value in member_indices],
            "nonmember_indices": [int(value) for value in nonmember_indices],
            "timesteps": timesteps,
            "distances_rmse": distances.round(8).tolist(),
            "min_distances_rmse": min_distances.round(8).tolist(),
            "features": features.round(8).tolist(),
            "logistic_aggregate_scores": logistic["aggregate_scores"],
        }
        (run_root / "scores.json").write_text(
            json.dumps(scores_payload, indent=2, ensure_ascii=True),
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
                inputs=np.concatenate(
                    [
                        member_inputs.numpy().astype(np.float16),
                        nonmember_inputs.numpy().astype(np.float16),
                    ],
                    axis=0,
                ),
                responses=np.concatenate([member_responses, nonmember_responses], axis=0),
                distances_rmse=distances.astype(np.float32),
                min_distances_rmse=min_distances.astype(np.float32),
            )

        summary = {
            "status": "ready",
            "task": "X-168 black-box H2 strength-response GPU scout",
            "mode": "bounded-gpu-scout",
            "track": "black-box",
            "method": "H2 strength-response curve",
            "device": args.device,
            "gpu_release": "one bounded 64/64 response-surface scout",
            "admitted_change": "none",
            "inputs": {
                "config": str(args.config),
                "repo_root": str(args.repo_root),
                "member_split_root": str(args.member_split_root),
                "packet_size": int(args.packet_size),
                "batch_size": int(args.batch_size),
                "timesteps": timesteps,
                "repeats": int(args.repeats),
                "denoise_stride": int(args.denoise_stride),
                "seed": int(args.seed),
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
            "baselines": baselines,
            "h2_logistic": logistic,
            "gates": {
                "best_simple_by_low_fpr": baselines["best_by_low_fpr"],
                "logistic_minus_best_simple_by_low_fpr": metric_delta(logistic_metrics, best_simple),
                "low_fpr_improved": bool(low_fpr_improved),
                "auc_not_worse_than_best_simple_auc": bool(auc_not_worse),
                "promotion_allowed": False,
            },
            "verdict": verdict,
            "next_gpu_candidate": "none until X168 post-run review selects a new bounded hypothesis",
            "cpu_sidecar": "H1 response-cloud and H3 frequency-filter scorer reuse on the cached response surface",
            "notes": [
                "This is a bounded DDPM/CIFAR10 response-surface scout, not admitted black-box evidence.",
                "The output cache is intentionally reusable by H1/H3 scorer-only follow-ups before any second GPU pass.",
                "AUC-only improvement is not enough for promotion; low-FPR behavior controls the verdict.",
            ],
        }
    except Exception as exc:
        summary = {
            "status": "blocked",
            "task": "X-168 black-box H2 strength-response GPU scout",
            "mode": "bounded-gpu-scout",
            "track": "black-box",
            "device": args.device,
            "error": f"{type(exc).__name__}: {exc}",
            "verdict": "blocked",
            "next_gpu_candidate": "none until the X168 runtime blocker is cleared",
        }
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    (run_root / "summary.json").write_text(
        json.dumps(json_sanitize(summary), indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    print(json.dumps(json_sanitize(summary), indent=2, ensure_ascii=False))
    return 0 if summary["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
