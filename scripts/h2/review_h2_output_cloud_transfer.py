from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from diffaudit.attacks.h2_response_strength import bootstrap_metric_ci, score_metrics
from review_h2_output_cloud_geometry import compute_output_cloud_features


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


def _load_features(path: Path) -> dict[str, Any]:
    cache = np.load(path)
    if "timesteps" not in cache.files:
        raise KeyError(f"{path} is not a timestep-based H2 response cache")
    labels = cache["labels"].astype(np.int64)
    timesteps = cache["timesteps"].astype(np.int64)
    responses = cache["responses"].astype(np.float32)
    features, names = compute_output_cloud_features(responses, timesteps)
    return {
        "path": path,
        "labels": labels,
        "timesteps": timesteps,
        "responses_shape": [int(value) for value in responses.shape],
        "features": features.astype(np.float32),
        "feature_names": names,
    }


def _transfer_holdout(
    *,
    source_name: str,
    target_name: str,
    source_features: np.ndarray,
    target_features: np.ndarray,
    labels: np.ndarray,
    feature_names: list[str],
    seed: int,
    repeats: int,
    bootstrap_iters: int,
) -> dict[str, Any]:
    labels_i64 = np.asarray(labels, dtype=np.int64)
    per_class_count = int(min((labels_i64 == 1).sum(), (labels_i64 == 0).sum()))
    if per_class_count < 2:
        raise ValueError("labels must contain at least two members and two nonmembers")
    fold_count = max(2, min(4, per_class_count))
    splitter = RepeatedStratifiedKFold(
        n_splits=fold_count,
        n_repeats=int(repeats),
        random_state=int(seed),
    )
    prediction_sum = np.zeros(labels_i64.shape[0], dtype=np.float64)
    prediction_count = np.zeros(labels_i64.shape[0], dtype=np.int64)
    fold_metrics: list[dict[str, Any]] = []
    coefficients: list[list[float]] = []

    for fold_idx, (train_idx, test_idx) in enumerate(splitter.split(source_features, labels_i64)):
        classifier = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000, class_weight="balanced", random_state=int(seed) + fold_idx),
        )
        classifier.fit(source_features[train_idx], labels_i64[train_idx])
        scores = classifier.predict_proba(target_features[test_idx])[:, 1]
        prediction_sum[test_idx] += scores
        prediction_count[test_idx] += 1
        fold_metrics.append(
            {
                "fold": int(fold_idx),
                "train_size": int(train_idx.shape[0]),
                "test_size": int(test_idx.shape[0]),
                "metrics": score_metrics(labels_i64[test_idx], scores),
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
        raise RuntimeError(f"Some samples were never evaluated by transfer folds: {missing[:8]}")
    aggregate_scores = prediction_sum / prediction_count
    aggregate_metrics = score_metrics(labels_i64, aggregate_scores)
    mean_coefficients = np.asarray(coefficients, dtype=float).mean(axis=0)
    top_coefficients = sorted(
        [
            {
                "feature": feature_names[idx],
                "coefficient": round(float(value), 6),
                "abs_coefficient": round(abs(float(value)), 6),
            }
            for idx, value in enumerate(mean_coefficients.tolist())
        ],
        key=lambda item: item["abs_coefficient"],
        reverse=True,
    )[:8]
    return {
        "source": source_name,
        "target": target_name,
        "mode": "fold_disjoint_cross_cache_transfer",
        "splitter": {
            "name": "RepeatedStratifiedKFold",
            "n_splits": int(fold_count),
            "n_repeats": int(repeats),
            "random_state": int(seed),
        },
        "aggregate_metrics": aggregate_metrics,
        "aggregate_ci95": bootstrap_metric_ci(
            labels_i64,
            aggregate_scores,
            seed=int(seed) + 100,
            iters=bootstrap_iters,
        ),
        "fold_metrics": fold_metrics,
        "prediction_count": {
            "min": int(prediction_count.min()),
            "max": int(prediction_count.max()),
            "mean": round(float(prediction_count.mean()), 6),
        },
        "top_mean_coefficients": top_coefficients,
    }


def _same_sample_transfer(
    *,
    source_name: str,
    target_name: str,
    source_features: np.ndarray,
    target_features: np.ndarray,
    labels: np.ndarray,
    seed: int,
) -> dict[str, Any]:
    labels_i64 = np.asarray(labels, dtype=np.int64)
    classifier = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=2000, class_weight="balanced", random_state=int(seed)),
    )
    classifier.fit(source_features, labels_i64)
    scores = classifier.predict_proba(target_features)[:, 1]
    return {
        "source": source_name,
        "target": target_name,
        "mode": "same_sample_all_train_all_test_diagnostic",
        "metrics": score_metrics(labels_i64, scores),
        "note": "Diagnostic only: source and target caches contain the same sample identities.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate H2 output-cloud logistic transfer across existing response caches."
    )
    parser.add_argument("--source-a", type=Path, required=True)
    parser.add_argument("--name-a", default="shared_position_seed176")
    parser.add_argument("--source-b", type=Path, required=True)
    parser.add_argument("--name-b", default="shared_position_seed177")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=176)
    parser.add_argument("--holdout-repeats", type=int, default=7)
    parser.add_argument("--bootstrap-iters", type=int, default=200)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    left = _load_features(args.source_a)
    right = _load_features(args.source_b)
    if not np.array_equal(left["labels"], right["labels"]):
        raise ValueError("source caches must share label order for fold-aligned transfer")
    if not np.array_equal(left["timesteps"], right["timesteps"]):
        raise ValueError("source caches must share timestep values")
    if left["feature_names"] != right["feature_names"]:
        raise ValueError("source caches produced different output-cloud feature sets")

    labels = left["labels"]
    feature_names = left["feature_names"]
    left_to_right = _transfer_holdout(
        source_name=args.name_a,
        target_name=args.name_b,
        source_features=left["features"],
        target_features=right["features"],
        labels=labels,
        feature_names=feature_names,
        seed=args.seed,
        repeats=args.holdout_repeats,
        bootstrap_iters=args.bootstrap_iters,
    )
    right_to_left = _transfer_holdout(
        source_name=args.name_b,
        target_name=args.name_a,
        source_features=right["features"],
        target_features=left["features"],
        labels=labels,
        feature_names=feature_names,
        seed=args.seed + 1,
        repeats=args.holdout_repeats,
        bootstrap_iters=args.bootstrap_iters,
    )
    diagnostic = [
        _same_sample_transfer(
            source_name=args.name_a,
            target_name=args.name_b,
            source_features=left["features"],
            target_features=right["features"],
            labels=labels,
            seed=args.seed,
        ),
        _same_sample_transfer(
            source_name=args.name_b,
            target_name=args.name_a,
            source_features=right["features"],
            target_features=left["features"],
            labels=labels,
            seed=args.seed + 1,
        ),
    ]
    transfer_metrics = [left_to_right["aggregate_metrics"], right_to_left["aggregate_metrics"]]
    mean_auc = float(np.mean([float(item["auc"]) for item in transfer_metrics]))
    min_tpr_1pct = float(min(float(item["tpr_at_1pct_fpr"]) for item in transfer_metrics))
    min_tpr_0_1pct = float(min(float(item["tpr_at_0_1pct_fpr"]) for item in transfer_metrics))
    verdict = "cross_cache_transfer_weak"
    if mean_auc >= 0.80 and min_tpr_1pct > 0.05:
        verdict = "cross_cache_transfer_positive"
    if mean_auc >= 0.90 and min_tpr_0_1pct > 0.0:
        verdict = "cross_cache_transfer_strong_candidate"

    result: dict[str, Any] = {
        "status": "ready",
        "track": "black-box",
        "method": "H2 output-cloud geometry cross-cache transfer",
        "mode": "cpu-existing-cache-review",
        "inputs": {
            "source_a": str(args.source_a),
            "source_b": str(args.source_b),
            "name_a": args.name_a,
            "name_b": args.name_b,
            "sample_count": int(labels.shape[0]),
            "member_count": int((labels == 1).sum()),
            "nonmember_count": int((labels == 0).sum()),
            "timesteps": [int(value) for value in left["timesteps"].tolist()],
            "source_a_response_shape": left["responses_shape"],
            "source_b_response_shape": right["responses_shape"],
            "feature_count": int(left["features"].shape[1]),
            "feature_names": feature_names,
            "seed": int(args.seed),
            "holdout_repeats": int(args.holdout_repeats),
            "bootstrap_iters": int(args.bootstrap_iters),
        },
        "primary_transfer": [left_to_right, right_to_left],
        "same_sample_diagnostic": diagnostic,
        "decision_gate": {
            "uses_existing_response_caches_only": True,
            "generates_new_responses": False,
            "fold_disjoint_primary_transfer": True,
            "mean_auc": round(mean_auc, 6),
            "min_tpr_at_1pct_fpr": round(min_tpr_1pct, 6),
            "min_tpr_at_0_1pct_fpr": round(min_tpr_0_1pct, 6),
            "reopen_allowed": False,
            "requires_second_public_asset_before_product_promotion": True,
        },
        "verdict": verdict,
        "notes": [
            "Primary transfer trains on one response cache and scores held-out sample identities from the other cache.",
            "The all-train/all-test transfer is diagnostic only because both caches share sample identities.",
            "This review does not generate responses, run GPU work, download assets, or change Platform/Runtime admission.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(_sanitize(result), indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(_sanitize(result), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
