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
        description="Run X-170 H1 response-cloud scorer review on the X168 cache."
    )
    parser.add_argument(
        "--response-cache",
        type=Path,
        default=Path("workspaces/black-box/runs/x168-h2-strength-response-gpu-scout-20260429-r1/response-cache.npz"),
    )
    parser.add_argument("--run-root", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=170)
    parser.add_argument("--cv-repeats", type=int, default=7)
    parser.add_argument("--bootstrap-iters", type=int, default=200)
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


def pairwise_rmse(vectors: np.ndarray) -> np.ndarray:
    pair_scores = []
    for left_idx in range(vectors.shape[1]):
        for right_idx in range(left_idx + 1, vectors.shape[1]):
            delta = vectors[:, left_idx] - vectors[:, right_idx]
            pair_scores.append(np.sqrt(np.mean(delta * delta, axis=tuple(range(1, delta.ndim)))))
    if not pair_scores:
        return np.zeros(vectors.shape[0], dtype=np.float32)
    return np.stack(pair_scores, axis=1).mean(axis=1).astype(np.float32)


def build_h1_features(responses: np.ndarray, timesteps: np.ndarray) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    del timesteps
    # responses: [sample, timestep, repeat, channel, height, width]
    response_f32 = responses.astype(np.float32)
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
        coefficients.append([round(float(value), 6) for value in classifier.named_steps["logisticregression"].coef_[0].tolist()])
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


def evaluate_simple_scores(
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
    for offset, name in enumerate(("cloud_pairwise_rmse", "cloud_variance", "centroid_pairwise_rmse", "repeat_rmse_slope"), start=20):
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
    run_root = args.run_root or Path(f"workspaces/black-box/runs/x170-h1-response-cloud-cache-review-{timestamp}")
    run_root.mkdir(parents=True, exist_ok=True)
    started_at = time.perf_counter()

    try:
        cache = np.load(args.response_cache)
        labels = cache["labels"].astype(np.int64)
        responses = cache["responses"]
        timesteps = cache["timesteps"].astype(np.int64)
        features, feature_map = build_h1_features(responses, timesteps)
        simple = evaluate_simple_scores(labels, feature_map, args.seed, args.bootstrap_iters)
        logistic = evaluate_logistic(labels, features, args.seed, args.cv_repeats, args.bootstrap_iters)

        best_simple = simple["best_by_low_fpr"]["metrics"]
        logistic_metrics = logistic["aggregate_metrics"]
        low_fpr_improved = (
            float(logistic_metrics["tpr_at_1pct_fpr"]) > float(best_simple["tpr_at_1pct_fpr"])
            and float(logistic_metrics["tpr_at_0_1pct_fpr"]) >= float(best_simple["tpr_at_0_1pct_fpr"])
        )
        auc_not_worse = float(logistic_metrics["auc"]) >= float(simple["best_by_auc"]["metrics"]["auc"])
        verdict = "positive but bounded" if low_fpr_improved and auc_not_worse else "negative but useful"

        feature_payload = {
            "labels": labels.tolist(),
            "timesteps": timesteps.tolist(),
            "features": features.round(8).tolist(),
            "feature_names": [
                *[f"repeat_rmse_timestep_{int(t)}" for t in timesteps.tolist()],
                "cloud_pairwise_rmse",
                "cloud_variance",
                "centroid_pairwise_rmse",
                "repeat_rmse_slope",
            ],
            "logistic_aggregate_scores": logistic["aggregate_scores"],
        }
        (run_root / "features.json").write_text(
            json.dumps(feature_payload, indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        summary = {
            "status": "ready",
            "task": "X-170 H1 response-cloud cache review",
            "mode": "cpu-scorer-reuse",
            "track": "black-box",
            "method": "H1 response-cloud geometry",
            "gpu_release": "none",
            "admitted_change": "none",
            "inputs": {
                "response_cache": str(args.response_cache),
                "seed": int(args.seed),
                "cv_repeats": int(args.cv_repeats),
                "bootstrap_iters": int(args.bootstrap_iters),
            },
            "runtime": {
                "sample_count": int(labels.shape[0]),
                "member_count": int((labels == 1).sum()),
                "nonmember_count": int((labels == 0).sum()),
                "timesteps": timesteps.tolist(),
                "response_shape": list(responses.shape),
                "wall_clock_seconds": round(time.perf_counter() - started_at, 6),
            },
            "artifact_paths": {
                "summary": str(run_root / "summary.json"),
                "features": str(run_root / "features.json"),
            },
            "simple_output_cloud_baselines": simple,
            "h1_logistic": logistic,
            "gates": {
                "best_simple_by_low_fpr": simple["best_by_low_fpr"],
                "logistic_minus_best_simple_by_low_fpr": metric_delta(logistic_metrics, best_simple),
                "low_fpr_improved": bool(low_fpr_improved),
                "auc_not_worse_than_best_simple_auc": bool(auc_not_worse),
                "promotion_allowed": False,
            },
            "verdict": verdict,
            "next_gpu_candidate": "none until H1/H3 cache reviews decide whether H2 validation is worth a bounded GPU rung",
            "notes": [
                "H1 uses only output-output response-cloud geometry from the X168 cache.",
                "No original-to-output distance features are included in the logistic scorer.",
                "This is a CPU-only scorer-reuse review and cannot promote black-box evidence by itself.",
            ],
        }
    except Exception as exc:
        summary = {
            "status": "blocked",
            "task": "X-170 H1 response-cloud cache review",
            "mode": "cpu-scorer-reuse",
            "track": "black-box",
            "error": f"{type(exc).__name__}: {exc}",
            "verdict": "blocked",
            "next_gpu_candidate": "none until the X170 cache-review blocker is cleared",
        }

    (run_root / "summary.json").write_text(
        json.dumps(sanitize(summary), indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    print(json.dumps(sanitize(summary), indent=2, ensure_ascii=False))
    return 0 if summary["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
