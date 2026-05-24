from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from diffaudit.attacks.h2_response_strength import evaluate_logistic_holdout, metric_delta, score_metrics


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


def _slope(values: np.ndarray, axis_values: np.ndarray) -> np.ndarray:
    if values.shape[1] <= 1:
        return np.zeros(values.shape[0], dtype=np.float32)
    return np.polyfit(axis_values.astype(np.float64), values.T.astype(np.float64), deg=1)[0].astype(np.float32)


def _cloud_eigen_features(flat_responses: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    centered = flat_responses - flat_responses.mean(axis=1, keepdims=True)
    # Eigenvalues of the response Gram matrix give the non-zero PCA spectrum of
    # each small response cloud without building a huge pixel covariance matrix.
    gram = np.einsum("nrd,nsd->nrs", centered, centered, optimize=True)
    gram /= max(flat_responses.shape[1] - 1, 1)
    eigvals = np.linalg.eigvalsh(gram).astype(np.float64)
    eigvals = np.clip(eigvals, 0.0, None)
    trace = eigvals.sum(axis=1)
    top_share = np.divide(
        eigvals[:, -1],
        trace,
        out=np.zeros_like(trace),
        where=trace > 0,
    )
    return trace.astype(np.float32), top_share.astype(np.float32)


def compute_output_cloud_features(responses: np.ndarray, axis_values: np.ndarray) -> tuple[np.ndarray, list[str]]:
    responses_f32 = np.asarray(responses, dtype=np.float32)
    if responses_f32.ndim != 6:
        raise ValueError("responses must have shape [sample, timestep, repeat, channel, height, width]")
    if responses_f32.shape[2] < 2:
        raise ValueError("output-cloud geometry needs at least two repeats per timestep")

    sample_count, timestep_count, repeat_count = responses_f32.shape[:3]
    flat = responses_f32.reshape(sample_count, timestep_count, repeat_count, -1)
    names: list[str] = []
    columns: list[np.ndarray] = []

    pair_distances = []
    for left in range(repeat_count):
        for right in range(left + 1, repeat_count):
            pair_distances.append(np.sqrt(np.mean((flat[:, :, left] - flat[:, :, right]) ** 2, axis=2)))
    pair_rmse = np.stack(pair_distances, axis=2).mean(axis=2).astype(np.float32)
    for idx, axis_value in enumerate(axis_values.tolist()):
        names.append(f"within_timestep_pair_rmse_{int(axis_value)}")
        columns.append(pair_rmse[:, idx])
    names.extend(
        [
            "within_timestep_pair_rmse_mean",
            "within_timestep_pair_rmse_std",
            "within_timestep_pair_rmse_slope",
        ]
    )
    columns.extend([pair_rmse.mean(axis=1), pair_rmse.std(axis=1), _slope(pair_rmse, axis_values)])

    centroids = flat.mean(axis=2)
    centroid_pairs: list[np.ndarray] = []
    centroid_pair_names: list[str] = []
    for left in range(timestep_count):
        for right in range(left + 1, timestep_count):
            distance = np.sqrt(np.mean((centroids[:, left] - centroids[:, right]) ** 2, axis=1)).astype(np.float32)
            centroid_pairs.append(distance)
            centroid_pair_names.append(
                f"centroid_rmse_{int(axis_values[left])}_{int(axis_values[right])}"
            )
    centroid_pair_matrix = np.stack(centroid_pairs, axis=1)
    names.extend(centroid_pair_names)
    columns.extend(centroid_pairs)
    names.extend(["centroid_rmse_mean", "centroid_rmse_std"])
    columns.extend([centroid_pair_matrix.mean(axis=1), centroid_pair_matrix.std(axis=1)])

    cloud_flat = flat.reshape(sample_count, timestep_count * repeat_count, -1)
    cloud_trace, cloud_top_share = _cloud_eigen_features(cloud_flat)
    names.extend(["cloud_pca_trace", "cloud_pca_top_share"])
    columns.extend([cloud_trace, cloud_top_share])

    features = np.stack(columns, axis=1).astype(np.float32)
    return features, names


def _simple_candidates(labels: np.ndarray, features: np.ndarray, names: list[str], *, seed: int) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for idx, name in enumerate(names):
        raw_scores = features[:, idx]
        for orientation, scores in (
            ("negative_higher_is_member", -raw_scores),
            ("positive_higher_is_member", raw_scores),
        ):
            candidates.append(
                {
                    "name": name,
                    "orientation": orientation,
                    "metrics": score_metrics(labels, scores),
                }
            )
    return candidates


def _best_by_low_fpr(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        candidates,
        key=lambda item: (
            float(item["metrics"]["tpr_at_1pct_fpr"]),
            float(item["metrics"]["tpr_at_0_1pct_fpr"]),
            float(item["metrics"]["auc"]),
        ),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review output-output cloud geometry on an existing H2 response-cache.npz."
    )
    parser.add_argument("--response-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=176)
    parser.add_argument("--holdout-repeats", type=int, default=7)
    parser.add_argument("--bootstrap-iters", type=int, default=200)
    parser.add_argument(
        "--shuffle-labels",
        action="store_true",
        help="Run the scorer after a seeded label permutation as a leakage sanity check.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cache = np.load(args.response_cache)
    labels = cache["labels"].astype(np.int64)
    label_mode = "original"
    if args.shuffle_labels:
        labels = np.random.default_rng(args.seed).permutation(labels)
        label_mode = f"shuffled_seed_{args.seed}"
    if "timesteps" not in cache.files:
        raise KeyError("output-cloud geometry review expects a timestep-based H2 cache")
    timesteps = cache["timesteps"].astype(np.int64)
    responses = cache["responses"].astype(np.float32)
    features, feature_names = compute_output_cloud_features(responses, timesteps)

    simple = _simple_candidates(labels, features, feature_names, seed=args.seed)
    best_auc = max(simple, key=lambda item: float(item["metrics"]["auc"]))
    best_low = _best_by_low_fpr(simple)
    logistic = evaluate_logistic_holdout(
        labels,
        features,
        seed=args.seed,
        repeats=args.holdout_repeats,
        bootstrap_iters=args.bootstrap_iters,
    )

    raw_h2_metrics = None
    lowpass_h2_metrics = None
    summary_path = args.response_cache.with_name("summary.json")
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        raw_h2_metrics = summary.get("raw_h2", {}).get("logistic", {}).get("aggregate_metrics")
        lowpass_h2_metrics = summary.get("lowpass_h2", {}).get("logistic", {}).get("aggregate_metrics")

    logistic_metrics = logistic["aggregate_metrics"]
    verdict = "weak_non_complementary_output_cloud_geometry"
    if args.shuffle_labels:
        verdict = "label_shuffle_sanity_random_level"
    elif (
        float(logistic_metrics["tpr_at_0_1pct_fpr"]) > 0
        and raw_h2_metrics is not None
        and float(logistic_metrics["auc"]) >= float(raw_h2_metrics["auc"]) - 0.03
    ):
        verdict = "candidate_complementary_output_cloud_geometry"

    result: dict[str, Any] = {
        "status": "ready",
        "track": "black-box",
        "method": "H2 output-cloud geometry scorer",
        "mode": "cpu-cache-review",
        "response_cache": str(args.response_cache),
        "inputs": {
            "sample_count": int(labels.shape[0]),
            "member_count": int((labels == 1).sum()),
            "nonmember_count": int((labels == 0).sum()),
            "timesteps": [int(value) for value in timesteps.tolist()],
            "repeat_count": int(responses.shape[2]),
            "feature_count": int(features.shape[1]),
            "feature_names": feature_names,
            "seed": int(args.seed),
            "label_mode": label_mode,
            "holdout_repeats": int(args.holdout_repeats),
            "bootstrap_iters": int(args.bootstrap_iters),
        },
        "simple": {
            "best_by_auc": {
                "name": best_auc["name"],
                "orientation": best_auc["orientation"],
                "metrics": best_auc["metrics"],
            },
            "best_by_low_fpr": {
                "name": best_low["name"],
                "orientation": best_low["orientation"],
                "metrics": best_low["metrics"],
            },
        },
        "logistic": {
            "aggregate_metrics": logistic_metrics,
            "aggregate_ci95": logistic["aggregate_ci95"],
            "mean_coefficients": logistic["mean_coefficients"],
            "prediction_count": logistic["prediction_count"],
        },
        "comparison": {
            "raw_h2_logistic": raw_h2_metrics if not args.shuffle_labels else None,
            "lowpass_h2_logistic": lowpass_h2_metrics if not args.shuffle_labels else None,
            "output_cloud_minus_raw_h2": metric_delta(logistic_metrics, raw_h2_metrics)
            if raw_h2_metrics is not None and not args.shuffle_labels
            else None,
            "output_cloud_minus_lowpass_h2": metric_delta(logistic_metrics, lowpass_h2_metrics)
            if lowpass_h2_metrics is not None and not args.shuffle_labels
            else None,
        },
        "decision_gate": {
            "uses_only_output_output_geometry": True,
            "does_not_generate_new_responses": True,
            "nonzero_strict_tail": bool(float(logistic_metrics["tpr_at_0_1pct_fpr"]) > 0),
            "beats_best_simple_low_fpr": bool(
                float(logistic_metrics["tpr_at_1pct_fpr"])
                > float(best_low["metrics"]["tpr_at_1pct_fpr"])
                and float(logistic_metrics["tpr_at_0_1pct_fpr"])
                >= float(best_low["metrics"]["tpr_at_0_1pct_fpr"])
            ),
            "reopen_allowed": False,
            "requires_reseeded_or_interleaved_cache_before_promotion": True,
        },
        "verdict": verdict,
        "notes": [
            "This is a CPU-only scorer review on an existing H2 response cache.",
            "It intentionally excludes seed-to-output distance features so it cannot collapse back into H2 simple distance.",
            "A positive result is candidate-only until reseeded or interleaved response-cache controls rule out class-ordered sampling effects.",
            "Do not expand this cache into KDE, shadow density, repeat-count, or same-cache feature sweeps.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(_sanitize(result), indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(_sanitize(result), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
