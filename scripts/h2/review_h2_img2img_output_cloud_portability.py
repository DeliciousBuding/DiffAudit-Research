from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from diffaudit.attacks.h2_response_strength import (
    evaluate_logistic_holdout,
    metric_delta,
    score_metrics,
)


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


def _axis_name(value: float) -> str:
    text = f"{float(value):.3f}".rstrip("0").rstrip(".")
    return text.replace(".", "p").replace("-", "neg")


def _slope(values: np.ndarray, axis_values: np.ndarray) -> np.ndarray:
    if values.shape[1] <= 1:
        return np.zeros(values.shape[0], dtype=np.float32)
    return np.polyfit(axis_values.astype(np.float64), values.T.astype(np.float64), deg=1)[0].astype(np.float32)


def _cloud_eigen_features(flat_responses: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    centered = flat_responses - flat_responses.mean(axis=1, keepdims=True)
    gram = np.einsum("nrd,nsd->nrs", centered, centered, optimize=True)
    gram /= max(flat_responses.shape[1] - 1, 1)
    eigvals = np.linalg.eigvalsh(gram).astype(np.float64)
    eigvals = np.clip(eigvals, 0.0, None)
    trace = eigvals.sum(axis=1)
    top_share = np.divide(eigvals[:, -1], trace, out=np.zeros_like(trace), where=trace > 0)
    return trace.astype(np.float32), top_share.astype(np.float32)


def _prune_degenerate_features(
    features: np.ndarray,
    names: list[str],
    *,
    atol: float = 1e-8,
) -> tuple[np.ndarray, list[str], list[dict[str, Any]]]:
    kept_columns: list[np.ndarray] = []
    kept_names: list[str] = []
    dropped: list[dict[str, Any]] = []
    for idx, name in enumerate(names):
        column = np.asarray(features[:, idx], dtype=np.float32)
        if not np.all(np.isfinite(column)):
            dropped.append({"name": name, "reason": "non_finite"})
            continue
        span = float(column.max() - column.min())
        if span <= atol:
            dropped.append({"name": name, "reason": "constant", "span": round(span, 12)})
            continue
        duplicate_of = None
        for kept_name, kept_column in zip(kept_names, kept_columns, strict=True):
            if np.allclose(column, kept_column, rtol=0.0, atol=atol):
                duplicate_of = kept_name
                break
        if duplicate_of is not None:
            dropped.append({"name": name, "reason": "duplicate", "duplicate_of": duplicate_of})
            continue
        kept_columns.append(column)
        kept_names.append(name)
    if not kept_columns:
        raise ValueError("all output-cloud features were degenerate")
    return np.stack(kept_columns, axis=1).astype(np.float32), kept_names, dropped


def compute_img2img_output_cloud_features(
    responses: np.ndarray,
    strengths: np.ndarray,
) -> tuple[np.ndarray, list[str]]:
    responses_f32 = np.asarray(responses, dtype=np.float32)
    if responses_f32.ndim != 6:
        raise ValueError("responses must have shape [sample, strength, repeat, channel, height, width]")
    if responses_f32.shape[2] < 2:
        raise ValueError("output-cloud geometry needs at least two repeats per strength")
    if responses_f32.shape[1] != strengths.shape[0]:
        raise ValueError("strengths length must match responses strength axis")

    sample_count, strength_count, repeat_count = responses_f32.shape[:3]
    flat = responses_f32.reshape(sample_count, strength_count, repeat_count, -1)
    names: list[str] = []
    columns: list[np.ndarray] = []

    pair_distances: list[np.ndarray] = []
    for left in range(repeat_count):
        for right in range(left + 1, repeat_count):
            pair_distances.append(np.sqrt(np.mean((flat[:, :, left] - flat[:, :, right]) ** 2, axis=2)))
    pair_rmse = np.stack(pair_distances, axis=2).mean(axis=2).astype(np.float32)
    for idx, strength in enumerate(strengths.tolist()):
        names.append(f"within_strength_pair_rmse_{_axis_name(float(strength))}")
        columns.append(pair_rmse[:, idx])
    names.extend(
        [
            "within_strength_pair_rmse_mean",
            "within_strength_pair_rmse_std",
            "within_strength_pair_rmse_slope",
        ]
    )
    columns.extend([pair_rmse.mean(axis=1), pair_rmse.std(axis=1), _slope(pair_rmse, strengths)])

    if strength_count > 1:
        centroids = flat.mean(axis=2)
        centroid_pairs: list[np.ndarray] = []
        for left in range(strength_count):
            for right in range(left + 1, strength_count):
                distance = np.sqrt(np.mean((centroids[:, left] - centroids[:, right]) ** 2, axis=1)).astype(np.float32)
                centroid_pairs.append(distance)
                names.append(
                    "centroid_rmse_"
                    f"{_axis_name(float(strengths[left]))}_{_axis_name(float(strengths[right]))}"
                )
                columns.append(distance)
        centroid_pair_matrix = np.stack(centroid_pairs, axis=1)
        names.extend(["centroid_rmse_mean", "centroid_rmse_std"])
        columns.extend([centroid_pair_matrix.mean(axis=1), centroid_pair_matrix.std(axis=1)])

    cloud_flat = flat.reshape(sample_count, strength_count * repeat_count, -1)
    cloud_trace, cloud_top_share = _cloud_eigen_features(cloud_flat)
    names.extend(["cloud_pca_trace", "cloud_pca_top_share"])
    columns.extend([cloud_trace, cloud_top_share])

    features = np.stack(columns, axis=1).astype(np.float32)
    return features, names


def _simple_candidates(labels: np.ndarray, features: np.ndarray, names: list[str]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for idx, name in enumerate(names):
        raw_scores = features[:, idx]
        for orientation, scores in (
            ("negative_higher_is_member", -raw_scores),
            ("positive_higher_is_member", raw_scores),
        ):
            candidates.append({"name": name, "orientation": orientation, "metrics": score_metrics(labels, scores)})
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


def _load_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _reference_metrics(run_root: Path) -> dict[str, Any]:
    summary = _load_json_if_exists(run_root / "summary.json")
    simple = _load_json_if_exists(run_root / "simple-distance-review.json")
    return {
        "raw_h2_logistic": summary.get("raw_h2", {}).get("logistic", {}).get("aggregate_metrics") if summary else None,
        "lowpass_h2_logistic": summary.get("lowpass_h2", {}).get("logistic", {}).get("aggregate_metrics")
        if summary
        else None,
        "best_simple_distance": simple.get("best_simple_distance", {}).get("metrics") if simple else None,
    }


def _review_one(
    *,
    response_cache: Path,
    name: str,
    seed: int,
    holdout_repeats: int,
    bootstrap_iters: int,
) -> dict[str, Any]:
    cache = np.load(response_cache)
    labels = cache["labels"].astype(np.int64)
    strengths = cache["strengths"].astype(np.float32)
    responses = cache["responses"].astype(np.float32)
    raw_features, raw_feature_names = compute_img2img_output_cloud_features(responses, strengths)
    features, feature_names, dropped_features = _prune_degenerate_features(raw_features, raw_feature_names)

    simple = _simple_candidates(labels, features, feature_names)
    best_auc = max(simple, key=lambda item: float(item["metrics"]["auc"]))
    best_low = _best_by_low_fpr(simple)
    logistic = evaluate_logistic_holdout(
        labels,
        features,
        seed=seed,
        repeats=holdout_repeats,
        bootstrap_iters=bootstrap_iters,
    )
    logistic_metrics = logistic["aggregate_metrics"]
    references = _reference_metrics(response_cache.parent)
    best_simple_distance = references["best_simple_distance"]

    simple_distance_delta = (
        metric_delta(logistic_metrics, best_simple_distance) if isinstance(best_simple_distance, dict) else None
    )
    if float(logistic_metrics["auc"]) >= 0.8 and float(logistic_metrics["tpr_at_0_1pct_fpr"]) > 0:
        verdict = "img2img_output_cloud_positive_but_not_distinct"
    else:
        verdict = "img2img_output_cloud_weak"
    if simple_distance_delta is not None and float(simple_distance_delta["auc"]) > 0.03:
        verdict = "img2img_output_cloud_distinct_positive"

    top_coefficients = sorted(
        [
            {
                "feature": feature_names[idx],
                "coefficient": round(float(value), 6),
                "abs_coefficient": round(abs(float(value)), 6),
            }
            for idx, value in enumerate(logistic["mean_coefficients"])
        ],
        key=lambda item: item["abs_coefficient"],
        reverse=True,
    )[:8]

    return {
        "name": name,
        "response_cache": str(response_cache),
        "inputs": {
            "sample_count": int(labels.shape[0]),
            "member_count": int((labels == 1).sum()),
            "nonmember_count": int((labels == 0).sum()),
            "strengths": [round(float(value), 6) for value in strengths.tolist()],
            "repeat_count": int(responses.shape[2]),
            "raw_feature_count": int(raw_features.shape[1]),
            "feature_count": int(features.shape[1]),
            "feature_names": feature_names,
            "dropped_features": dropped_features,
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
            "prediction_count": logistic["prediction_count"],
            "top_mean_coefficients": top_coefficients,
        },
        "references": references,
        "comparison": {
            "output_cloud_minus_best_simple_distance": simple_distance_delta,
            "output_cloud_minus_raw_h2_logistic": metric_delta(logistic_metrics, references["raw_h2_logistic"])
            if isinstance(references["raw_h2_logistic"], dict)
            else None,
            "output_cloud_minus_lowpass_h2_logistic": metric_delta(
                logistic_metrics,
                references["lowpass_h2_logistic"],
            )
            if isinstance(references["lowpass_h2_logistic"], dict)
            else None,
        },
        "verdict": verdict,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review whether H2 output-cloud geometry ports to existing img2img response caches."
    )
    parser.add_argument("--admission-cache", type=Path, required=True)
    parser.add_argument("--stability-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=176)
    parser.add_argument("--holdout-repeats", type=int, default=7)
    parser.add_argument("--bootstrap-iters", type=int, default=200)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    packets = [
        _review_one(
            response_cache=args.admission_cache,
            name="img2img_admission_25_25_strength_0p75",
            seed=args.seed,
            holdout_repeats=args.holdout_repeats,
            bootstrap_iters=args.bootstrap_iters,
        ),
        _review_one(
            response_cache=args.stability_cache,
            name="img2img_stability_10_10_strength_0p75",
            seed=args.seed + 1,
            holdout_repeats=args.holdout_repeats,
            bootstrap_iters=args.bootstrap_iters,
        ),
    ]
    admission_metrics = packets[0]["logistic"]["aggregate_metrics"]
    stability_metrics = packets[1]["logistic"]["aggregate_metrics"]
    min_auc = min(float(admission_metrics["auc"]), float(stability_metrics["auc"]))
    min_strict_tail = min(
        float(admission_metrics["tpr_at_0_1pct_fpr"]),
        float(stability_metrics["tpr_at_0_1pct_fpr"]),
    )
    max_simple_distance_auc_delta = max(
        float(packet["comparison"]["output_cloud_minus_best_simple_distance"]["auc"])
        for packet in packets
        if packet["comparison"]["output_cloud_minus_best_simple_distance"] is not None
    )
    overall_verdict = "img2img_output_cloud_not_distinct_from_simple_distance"
    if min_auc < 0.7 or min_strict_tail <= 0:
        overall_verdict = "img2img_output_cloud_weak_or_unstable"
    if min_auc >= 0.8 and min_strict_tail > 0 and max_simple_distance_auc_delta > 0.03:
        overall_verdict = "img2img_output_cloud_distinct_portability_candidate"

    result = {
        "status": "ready",
        "track": "black-box",
        "method": "H2 img2img output-cloud portability review",
        "mode": "cpu-existing-cache-review",
        "packets": packets,
        "decision_gate": {
            "uses_existing_response_caches_only": True,
            "generates_new_responses": False,
            "uses_only_output_output_geometry": True,
            "excludes_input_to_output_distance": True,
            "admission_auc": admission_metrics["auc"],
            "stability_auc": stability_metrics["auc"],
            "min_auc": round(min_auc, 6),
            "min_tpr_at_0_1pct_fpr": round(min_strict_tail, 6),
            "max_auc_delta_vs_best_simple_distance": round(max_simple_distance_auc_delta, 6),
            "reopen_allowed": False,
            "requires_second_public_asset_before_product_promotion": True,
        },
        "verdict": overall_verdict,
        "notes": [
            "This review tests whether output-output cloud geometry remains useful in the existing SD/CelebA img2img caches.",
            "It intentionally excludes input-to-output simple distance, which is the known stronger img2img baseline.",
            "A positive-but-not-distinct result does not expand H2; it narrows output-cloud geometry to a Research-side diagnostic.",
            "No response generation, model download, or GPU work is performed.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(_sanitize(result), indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(_sanitize(result), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
