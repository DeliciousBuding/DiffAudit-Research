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
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from diffaudit.attacks.pia_adapter import _compute_auc, _compute_threshold_metrics


METRIC_KEYS = ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run X-171 H3 frequency-filter ablation on the X168 response cache."
    )
    parser.add_argument(
        "--response-cache",
        type=Path,
        default=Path("workspaces/black-box/runs/x168-h2-strength-response-gpu-scout-20260429-r1/response-cache.npz"),
    )
    parser.add_argument("--run-root", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=171)
    parser.add_argument("--cv-repeats", type=int, default=7)
    parser.add_argument("--bootstrap-iters", type=int, default=200)
    parser.add_argument(
        "--cutoffs",
        type=float,
        nargs="+",
        default=[0.25, 0.50, 0.75],
        help="Normalized radial FFT cutoff values in [0, 1].",
    )
    return parser.parse_args()


def score_metrics(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    member_scores = scores[labels == 1]
    nonmember_scores = scores[labels == 0]
    return {
        "auc": round(float(_compute_auc(torch.tensor(member_scores), torch.tensor(nonmember_scores))), 6),
        **_compute_threshold_metrics(member_scores.astype(float), nonmember_scores.astype(float)),
        "member_score_mean": round(float(np.mean(member_scores)), 6),
        "nonmember_score_mean": round(float(np.mean(nonmember_scores)), 6),
    }


def bootstrap_metric_ci(labels: np.ndarray, scores: np.ndarray, seed: int, iters: int) -> dict[str, dict[str, float]]:
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


def metric_delta(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    return {key: round(float(left[key]) - float(right[key]), 6) for key in METRIC_KEYS}


def radial_radius(height: int, width: int) -> np.ndarray:
    fy = np.fft.fftfreq(height)[:, None]
    fx = np.fft.fftfreq(width)[None, :]
    max_radius = float(np.sqrt(0.5**2 + 0.5**2))
    return (np.sqrt(fx * fx + fy * fy) / max_radius).astype(np.float32)


def build_mask(height: int, width: int, kind: str, cutoff: float | None = None, cutoff_high: float | None = None) -> np.ndarray:
    radius = radial_radius(height, width)
    if kind == "full":
        mask = np.ones((height, width), dtype=np.float32)
    elif kind == "lowpass":
        if cutoff is None:
            raise ValueError("lowpass requires cutoff")
        mask = (radius <= cutoff).astype(np.float32)
    elif kind == "highpass":
        if cutoff is None:
            raise ValueError("highpass requires cutoff")
        mask = (radius > cutoff).astype(np.float32)
    elif kind == "bandpass":
        if cutoff is None or cutoff_high is None:
            raise ValueError("bandpass requires cutoff and cutoff_high")
        mask = ((radius > cutoff) & (radius <= cutoff_high)).astype(np.float32)
    else:
        raise ValueError(f"Unknown mask kind: {kind}")
    return mask[None, :, :]


def apply_frequency_mask(images: np.ndarray, mask: np.ndarray) -> np.ndarray:
    images_f32 = images.astype(np.float32, copy=False)
    if float(mask.min()) == 1.0 and float(mask.max()) == 1.0:
        return images_f32.copy()
    spectrum = np.fft.fftn(images_f32, axes=(-2, -1))
    filtered = np.fft.ifftn(spectrum * mask, axes=(-2, -1)).real
    return filtered.astype(np.float32)


def pairwise_rmse(vectors: np.ndarray) -> np.ndarray:
    pair_scores = []
    for left_idx in range(vectors.shape[1]):
        for right_idx in range(left_idx + 1, vectors.shape[1]):
            delta = vectors[:, left_idx] - vectors[:, right_idx]
            pair_scores.append(np.sqrt(np.mean(delta * delta, axis=tuple(range(1, delta.ndim)))))
    if not pair_scores:
        return np.zeros(vectors.shape[0], dtype=np.float32)
    return np.stack(pair_scores, axis=1).mean(axis=1).astype(np.float32)


def build_h1_features(responses: np.ndarray) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    response_f32 = responses.astype(np.float32, copy=False)
    sample_count, timestep_count, repeat_count = response_f32.shape[:3]
    flat_cloud = response_f32.reshape(sample_count, timestep_count * repeat_count, *response_f32.shape[3:])

    repeat_rmse = np.zeros((sample_count, timestep_count), dtype=np.float32)
    for timestep_idx in range(timestep_count):
        repeat_rmse[:, timestep_idx] = pairwise_rmse(response_f32[:, timestep_idx])

    cloud_pairwise_rmse = pairwise_rmse(flat_cloud)
    cloud_variance = flat_cloud.var(axis=1).mean(axis=(1, 2, 3)).astype(np.float32)
    timestep_centroids = response_f32.mean(axis=2)
    centroid_pairwise_rmse = pairwise_rmse(timestep_centroids)
    if timestep_count > 1:
        repeat_slope = np.polyfit(np.arange(timestep_count, dtype=float), repeat_rmse.T, deg=1)[0].astype(np.float32)
    else:
        repeat_slope = np.zeros(sample_count, dtype=np.float32)

    feature_map = {
        "repeat_rmse_per_timestep": repeat_rmse,
        "cloud_pairwise_rmse": cloud_pairwise_rmse,
        "cloud_variance": cloud_variance,
        "centroid_pairwise_rmse": centroid_pairwise_rmse,
        "repeat_rmse_slope": repeat_slope,
    }
    full_features = np.concatenate(
        [
            repeat_rmse,
            cloud_pairwise_rmse[:, None],
            cloud_variance[:, None],
            centroid_pairwise_rmse[:, None],
            repeat_slope[:, None],
        ],
        axis=1,
    ).astype(np.float32)
    return full_features, feature_map


def evaluate_logistic(
    labels: np.ndarray,
    features: np.ndarray,
    seed: int,
    repeats: int,
    bootstrap_iters: int,
) -> dict[str, Any]:
    per_class_count = int(min((labels == 1).sum(), (labels == 0).sum()))
    fold_count = max(2, min(4, per_class_count))
    splitter = RepeatedStratifiedKFold(n_splits=fold_count, n_repeats=repeats, random_state=seed)
    prediction_sum = np.zeros(labels.shape[0], dtype=np.float64)
    prediction_count = np.zeros(labels.shape[0], dtype=np.int64)
    fold_metrics: list[dict[str, Any]] = []
    coefficients: list[list[float]] = []
    for fold_idx, (train_idx, test_idx) in enumerate(splitter.split(features, labels)):
        classifier = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000, class_weight="balanced", random_state=seed + fold_idx),
        )
        classifier.fit(features[train_idx], labels[train_idx])
        scores = classifier.predict_proba(features[test_idx])[:, 1]
        prediction_sum[test_idx] += scores
        prediction_count[test_idx] += 1
        fold_metrics.append(
            {
                "fold": int(fold_idx),
                "train_size": int(train_idx.shape[0]),
                "test_size": int(test_idx.shape[0]),
                "metrics": score_metrics(labels[test_idx], scores),
            }
        )
        coefficients.append(
            [
                round(float(value), 6)
                for value in classifier.named_steps["logisticregression"].coef_[0].tolist()
            ]
        )

    if not np.all(prediction_count > 0):
        missing = np.where(prediction_count == 0)[0].tolist()
        raise RuntimeError(f"Some samples were never evaluated by holdout splits: {missing[:8]}")
    aggregate_scores = prediction_sum / prediction_count
    aggregate_metrics = score_metrics(labels, aggregate_scores)
    return {
        "score_orientation": "holdout_predicted_member_probability",
        "splitter": {
            "name": "RepeatedStratifiedKFold",
            "n_splits": int(fold_count),
            "n_repeats": int(repeats),
            "random_state": int(seed),
        },
        "aggregate_metrics": aggregate_metrics,
        "aggregate_ci95": bootstrap_metric_ci(labels, aggregate_scores, seed + 100, bootstrap_iters),
        "fold_metrics": fold_metrics,
        "mean_coefficients": [
            round(float(value), 6)
            for value in np.asarray(coefficients, dtype=float).mean(axis=0).tolist()
        ],
        "prediction_count": {
            "min": int(prediction_count.min()),
            "max": int(prediction_count.max()),
            "mean": round(float(prediction_count.mean()), 6),
        },
        "aggregate_scores": [round(float(value), 6) for value in aggregate_scores.tolist()],
    }


def evaluate_h2_simple_scores(
    labels: np.ndarray,
    min_distances: np.ndarray,
    timesteps: np.ndarray,
    seed: int,
    bootstrap_iters: int,
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for idx, timestep in enumerate(timesteps.tolist()):
        scores = -min_distances[:, idx]
        candidates.append(
            {
                "name": f"single_timestep_{int(timestep)}",
                "score_orientation": "negative_min_distance_higher_is_member",
                "metrics": score_metrics(labels, scores),
                "ci95": bootstrap_metric_ci(labels, scores, seed + idx, bootstrap_iters),
            }
        )
    mean_scores = -min_distances.mean(axis=1)
    if min_distances.shape[1] > 1:
        slope = np.polyfit(timesteps.astype(float), min_distances.T, deg=1)[0]
    else:
        slope = np.zeros(min_distances.shape[0], dtype=float)
    candidates.append(
        {
            "name": "mean_min_distance",
            "score_orientation": "negative_mean_min_distance_higher_is_member",
            "metrics": score_metrics(labels, mean_scores),
            "ci95": bootstrap_metric_ci(labels, mean_scores, seed + 20, bootstrap_iters),
        }
    )
    candidates.append(
        {
            "name": "negative_slope",
            "score_orientation": "negative_distance_slope_higher_is_member",
            "metrics": score_metrics(labels, -slope),
            "ci95": bootstrap_metric_ci(labels, -slope, seed + 21, bootstrap_iters),
        }
    )
    best_by_auc = max(candidates, key=lambda item: float(item["metrics"]["auc"]))
    best_by_low_fpr = max(
        candidates,
        key=lambda item: (
            float(item["metrics"]["tpr_at_1pct_fpr"]),
            float(item["metrics"]["tpr_at_0_1pct_fpr"]),
            float(item["metrics"]["auc"]),
        ),
    )
    return {
        "candidates": candidates,
        "best_by_auc": {"name": best_by_auc["name"], "metrics": best_by_auc["metrics"]},
        "best_by_low_fpr": {"name": best_by_low_fpr["name"], "metrics": best_by_low_fpr["metrics"]},
    }


def evaluate_h1_simple_scores(
    labels: np.ndarray,
    feature_map: dict[str, np.ndarray],
    seed: int,
    bootstrap_iters: int,
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for timestep_idx in range(feature_map["repeat_rmse_per_timestep"].shape[1]):
        scores = -feature_map["repeat_rmse_per_timestep"][:, timestep_idx]
        candidates.append(
            {
                "name": f"negative_repeat_rmse_timestep_{timestep_idx}",
                "score_orientation": "negative_output_output_rmse_higher_is_member",
                "metrics": score_metrics(labels, scores),
                "ci95": bootstrap_metric_ci(labels, scores, seed + timestep_idx, bootstrap_iters),
            }
        )
    for offset, name in enumerate(
        ("cloud_pairwise_rmse", "cloud_variance", "centroid_pairwise_rmse", "repeat_rmse_slope"),
        start=30,
    ):
        scores = -feature_map[name]
        candidates.append(
            {
                "name": f"negative_{name}",
                "score_orientation": "negative_output_cloud_measure_higher_is_member",
                "metrics": score_metrics(labels, scores),
                "ci95": bootstrap_metric_ci(labels, scores, seed + offset, bootstrap_iters),
            }
        )
    best_by_auc = max(candidates, key=lambda item: float(item["metrics"]["auc"]))
    best_by_low_fpr = max(
        candidates,
        key=lambda item: (
            float(item["metrics"]["tpr_at_1pct_fpr"]),
            float(item["metrics"]["tpr_at_0_1pct_fpr"]),
            float(item["metrics"]["auc"]),
        ),
    )
    return {
        "candidates": candidates,
        "best_by_auc": {"name": best_by_auc["name"], "metrics": best_by_auc["metrics"]},
        "best_by_low_fpr": {"name": best_by_low_fpr["name"], "metrics": best_by_low_fpr["metrics"]},
    }


def mask_specs(cutoffs: list[float], height: int, width: int) -> list[dict[str, Any]]:
    normalized_cutoffs = sorted({round(float(value), 4) for value in cutoffs})
    specs: list[dict[str, Any]] = [
        {
            "name": "raw_full",
            "kind": "full",
            "cutoff": None,
            "cutoff_high": None,
            "mask": build_mask(height, width, "full"),
        }
    ]
    for cutoff in normalized_cutoffs:
        specs.append(
            {
                "name": f"lowpass_{str(cutoff).replace('.', '_')}",
                "kind": "lowpass",
                "cutoff": cutoff,
                "cutoff_high": None,
                "mask": build_mask(height, width, "lowpass", cutoff=cutoff),
            }
        )
        specs.append(
            {
                "name": f"highpass_{str(cutoff).replace('.', '_')}",
                "kind": "highpass",
                "cutoff": cutoff,
                "cutoff_high": None,
                "mask": build_mask(height, width, "highpass", cutoff=cutoff),
            }
        )
    for low, high in zip(normalized_cutoffs, normalized_cutoffs[1:]):
        specs.append(
            {
                "name": f"bandpass_{str(low).replace('.', '_')}_{str(high).replace('.', '_')}",
                "kind": "bandpass",
                "cutoff": low,
                "cutoff_high": high,
                "mask": build_mask(height, width, "bandpass", cutoff=low, cutoff_high=high),
            }
        )
    return specs


def low_fpr_rank(item: dict[str, Any]) -> tuple[float, float, float, float]:
    metrics = item["h2_logistic"]["aggregate_metrics"]
    return (
        float(metrics["tpr_at_1pct_fpr"]),
        float(metrics["tpr_at_0_1pct_fpr"]),
        float(metrics["auc"]),
        float(metrics["asr"]),
    )


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [sanitize(item) for item in value]
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
    run_root = args.run_root or Path(f"workspaces/black-box/runs/x171-h3-frequency-filter-cache-ablation-{timestamp}")
    run_root.mkdir(parents=True, exist_ok=True)
    started_at = time.perf_counter()

    try:
        cache = np.load(args.response_cache)
        labels = cache["labels"].astype(np.int64)
        inputs = cache["inputs"].astype(np.float32)
        responses = cache["responses"].astype(np.float32)
        timesteps = cache["timesteps"].astype(np.int64)
        raw_distances = cache["distances_rmse"].astype(np.float32)
        raw_min_distances = cache["min_distances_rmse"].astype(np.float32)

        if inputs.ndim != 4 or responses.ndim != 6:
            raise ValueError(f"Unexpected cache shapes: inputs={inputs.shape}, responses={responses.shape}")
        if responses.shape[0] != inputs.shape[0]:
            raise ValueError("Input and response sample counts do not match")

        height, width = int(inputs.shape[-2]), int(inputs.shape[-1])
        specs = mask_specs(args.cutoffs, height, width)
        evaluations: list[dict[str, Any]] = []
        feature_payload: dict[str, Any] = {
            "labels": labels.tolist(),
            "timesteps": timesteps.tolist(),
            "feature_names": [f"min_distance_timestep_{int(timestep)}" for timestep in timesteps.tolist()],
            "masks": {},
        }

        for spec_idx, spec in enumerate(specs):
            mask = spec["mask"]
            if spec["name"] == "raw_full":
                filtered_inputs = inputs
                filtered_responses = responses
                distances = raw_distances
                min_distances = raw_min_distances
            else:
                filtered_inputs = apply_frequency_mask(inputs, mask)
                filtered_responses = apply_frequency_mask(responses, mask)
                delta = filtered_responses - filtered_inputs[:, None, None, :, :, :]
                distances = np.sqrt(np.mean(delta * delta, axis=(3, 4, 5))).astype(np.float32)
                min_distances = distances.min(axis=2).astype(np.float32)

            h2_simple = evaluate_h2_simple_scores(
                labels=labels,
                min_distances=min_distances,
                timesteps=timesteps,
                seed=args.seed + spec_idx * 100,
                bootstrap_iters=args.bootstrap_iters,
            )
            h2_logistic = evaluate_logistic(
                labels=labels,
                features=min_distances.astype(np.float32),
                seed=args.seed + spec_idx * 100,
                repeats=args.cv_repeats,
                bootstrap_iters=args.bootstrap_iters,
            )

            h1_features, h1_feature_map = build_h1_features(filtered_responses)
            h1_simple = evaluate_h1_simple_scores(
                labels=labels,
                feature_map=h1_feature_map,
                seed=args.seed + spec_idx * 100 + 50,
                bootstrap_iters=args.bootstrap_iters,
            )
            h1_logistic = evaluate_logistic(
                labels=labels,
                features=h1_features,
                seed=args.seed + spec_idx * 100 + 50,
                repeats=args.cv_repeats,
                bootstrap_iters=args.bootstrap_iters,
            )

            evaluation = {
                "name": spec["name"],
                "kind": spec["kind"],
                "cutoff": spec["cutoff"],
                "cutoff_high": spec["cutoff_high"],
                "mask_density": round(float(mask.mean()), 6),
                "h2_simple": h2_simple,
                "h2_logistic": h2_logistic,
                "h1_simple": h1_simple,
                "h1_logistic": h1_logistic,
            }
            evaluations.append(evaluation)
            feature_payload["masks"][spec["name"]] = {
                "kind": spec["kind"],
                "cutoff": spec["cutoff"],
                "cutoff_high": spec["cutoff_high"],
                "mask_density": round(float(mask.mean()), 6),
                "h2_features_min_distances": min_distances.round(8).tolist(),
                "h2_logistic_aggregate_scores": h2_logistic["aggregate_scores"],
                "h1_logistic_aggregate_scores": h1_logistic["aggregate_scores"],
            }

        raw_full = next(item for item in evaluations if item["name"] == "raw_full")
        non_full = [item for item in evaluations if item["name"] != "raw_full"]
        low_or_mid = [item for item in non_full if item["kind"] in {"lowpass", "bandpass"}]
        highpass = [item for item in non_full if item["kind"] == "highpass"]
        best_non_full = max(non_full, key=low_fpr_rank)
        best_low_or_mid = max(low_or_mid, key=low_fpr_rank)
        best_highpass = max(highpass, key=low_fpr_rank)
        best_h1 = max(evaluations, key=lambda item: (
            float(item["h1_logistic"]["aggregate_metrics"]["tpr_at_1pct_fpr"]),
            float(item["h1_logistic"]["aggregate_metrics"]["tpr_at_0_1pct_fpr"]),
            float(item["h1_logistic"]["aggregate_metrics"]["auc"]),
        ))

        raw_metrics = raw_full["h2_logistic"]["aggregate_metrics"]
        best_non_full_metrics = best_non_full["h2_logistic"]["aggregate_metrics"]
        best_low_or_mid_metrics = best_low_or_mid["h2_logistic"]["aggregate_metrics"]
        best_highpass_metrics = best_highpass["h2_logistic"]["aggregate_metrics"]
        h1_best_metrics = best_h1["h1_logistic"]["aggregate_metrics"]

        low_or_mid_retains_tail = (
            float(best_low_or_mid_metrics["tpr_at_1pct_fpr"]) >= 0.75 * float(raw_metrics["tpr_at_1pct_fpr"])
            and float(best_low_or_mid_metrics["tpr_at_0_1pct_fpr"]) >= 0.75 * float(raw_metrics["tpr_at_0_1pct_fpr"])
            and float(best_low_or_mid_metrics["auc"]) >= 0.85
        )
        highpass_dominates = (
            float(best_highpass_metrics["tpr_at_1pct_fpr"]) > float(best_low_or_mid_metrics["tpr_at_1pct_fpr"]) + 0.05
            and float(best_highpass_metrics["tpr_at_0_1pct_fpr"]) >= float(best_low_or_mid_metrics["tpr_at_0_1pct_fpr"])
        )
        filter_improves_h2_tail = (
            float(best_non_full_metrics["tpr_at_1pct_fpr"]) > float(raw_metrics["tpr_at_1pct_fpr"])
            and float(best_non_full_metrics["tpr_at_0_1pct_fpr"]) >= float(raw_metrics["tpr_at_0_1pct_fpr"])
        )
        h1_tail_recovered = (
            float(h1_best_metrics["tpr_at_1pct_fpr"]) > 0.078125
            and float(h1_best_metrics["tpr_at_0_1pct_fpr"]) >= 0.078125
        )

        if low_or_mid_retains_tail and not highpass_dominates:
            verdict = "positive boundary / H2 validation candidate released"
            next_gpu_candidate = "X172 bounded 128/128 H2 strength-response validation, pending host-health check"
        elif filter_improves_h2_tail:
            verdict = "positive but bounded / filter-sensitive"
            next_gpu_candidate = "hold until post-X171 review freezes whether filtered H2 or raw H2 is the validation target"
        else:
            verdict = "negative but useful"
            next_gpu_candidate = "none until a new bounded black-box scorer or validation argument appears"

        (run_root / "features.json").write_text(
            json.dumps(sanitize(feature_payload), indent=2, ensure_ascii=True),
            encoding="utf-8",
        )

        compact_table = []
        for item in evaluations:
            compact_table.append(
                {
                    "name": item["name"],
                    "kind": item["kind"],
                    "cutoff": item["cutoff"],
                    "cutoff_high": item["cutoff_high"],
                    "mask_density": item["mask_density"],
                    "h2_logistic": item["h2_logistic"]["aggregate_metrics"],
                    "h2_best_simple_low_fpr": item["h2_simple"]["best_by_low_fpr"],
                    "h1_logistic": item["h1_logistic"]["aggregate_metrics"],
                    "h1_best_simple_low_fpr": item["h1_simple"]["best_by_low_fpr"],
                }
            )

        summary = {
            "status": "ready",
            "task": "X-171 H3 frequency-filter ablation on X168 cache",
            "mode": "cpu-scorer-reuse",
            "track": "black-box",
            "method": "H3 frequency-sliced stability plug-in for H2/H1",
            "gpu_release": "none",
            "admitted_change": "none",
            "inputs": {
                "response_cache": str(args.response_cache),
                "seed": int(args.seed),
                "cv_repeats": int(args.cv_repeats),
                "bootstrap_iters": int(args.bootstrap_iters),
                "cutoffs": [float(value) for value in sorted(args.cutoffs)],
            },
            "runtime": {
                "sample_count": int(labels.shape[0]),
                "member_count": int((labels == 1).sum()),
                "nonmember_count": int((labels == 0).sum()),
                "timesteps": timesteps.tolist(),
                "input_shape": list(inputs.shape),
                "response_shape": list(responses.shape),
                "wall_clock_seconds": round(time.perf_counter() - started_at, 6),
            },
            "artifact_paths": {
                "summary": str(run_root / "summary.json"),
                "features": str(run_root / "features.json"),
            },
            "compact_results": compact_table,
            "frequency_evaluations": evaluations,
            "gates": {
                "raw_full_h2_logistic": {
                    "name": raw_full["name"],
                    "metrics": raw_metrics,
                },
                "best_non_full_h2_logistic": {
                    "name": best_non_full["name"],
                    "kind": best_non_full["kind"],
                    "cutoff": best_non_full["cutoff"],
                    "cutoff_high": best_non_full["cutoff_high"],
                    "metrics": best_non_full_metrics,
                    "delta_vs_raw_full": metric_delta(best_non_full_metrics, raw_metrics),
                },
                "best_low_or_mid_h2_logistic": {
                    "name": best_low_or_mid["name"],
                    "kind": best_low_or_mid["kind"],
                    "cutoff": best_low_or_mid["cutoff"],
                    "cutoff_high": best_low_or_mid["cutoff_high"],
                    "metrics": best_low_or_mid_metrics,
                    "delta_vs_raw_full": metric_delta(best_low_or_mid_metrics, raw_metrics),
                },
                "best_highpass_h2_logistic": {
                    "name": best_highpass["name"],
                    "kind": best_highpass["kind"],
                    "cutoff": best_highpass["cutoff"],
                    "metrics": best_highpass_metrics,
                    "delta_vs_raw_full": metric_delta(best_highpass_metrics, raw_metrics),
                },
                "best_h1_logistic": {
                    "name": best_h1["name"],
                    "kind": best_h1["kind"],
                    "metrics": h1_best_metrics,
                },
                "low_or_mid_retains_h2_tail": bool(low_or_mid_retains_tail),
                "highpass_dominates_h2_tail": bool(highpass_dominates),
                "filter_improves_h2_tail": bool(filter_improves_h2_tail),
                "h1_tail_recovered_by_filtering": bool(h1_tail_recovered),
                "promotion_allowed": False,
                "validation_candidate_allowed": bool(verdict == "positive boundary / H2 validation candidate released"),
            },
            "verdict": verdict,
            "next_gpu_candidate": next_gpu_candidate,
            "cpu_sidecar": "post-X171 validation gate review plus I-A / cross-box boundary maintenance",
            "notes": [
                "H3 is evaluated only as a Fourier-domain plug-in ablation over the X168 response cache.",
                "This run does not acquire new model responses and does not promote H2 to admitted black-box evidence.",
                "Low-FPR retention in low/mid bands is treated as a boundary check against high-frequency-only artifacts.",
                "H1 filtering is diagnostic only; H1 remains below promotion unless low-FPR tail is recovered.",
            ],
        }
    except Exception as exc:
        summary = {
            "status": "blocked",
            "task": "X-171 H3 frequency-filter ablation on X168 cache",
            "mode": "cpu-scorer-reuse",
            "track": "black-box",
            "error": f"{type(exc).__name__}: {exc}",
            "verdict": "blocked",
            "next_gpu_candidate": "none until the X171 cache-ablation blocker is cleared",
        }

    (run_root / "summary.json").write_text(
        json.dumps(sanitize(summary), indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    print(json.dumps(sanitize(summary), indent=2, ensure_ascii=False))
    return 0 if summary["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
