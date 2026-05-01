from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from diffaudit.utils.metrics import metric_bundle, round6, spearman


METRIC_KEYS = ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")


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
        return value.as_posix()
    return value


def _score_metrics(labels: np.ndarray, scores: np.ndarray) -> dict[str, Any]:
    labels_i64 = np.asarray(labels, dtype=np.int64)
    scores_f64 = np.asarray(scores, dtype=np.float64)
    member_scores = scores_f64[labels_i64 == 1]
    nonmember_scores = scores_f64[labels_i64 == 0]
    if member_scores.size == 0 or nonmember_scores.size == 0:
        raise ValueError("labels must include member=1 and nonmember=0 samples")
    nonmember_max = float(nonmember_scores.max())
    zero_fp_tp = int((member_scores > nonmember_max).sum())
    payload: dict[str, Any] = {
        **metric_bundle(scores_f64, labels_i64),
        "member_score_mean": round6(float(member_scores.mean())),
        "nonmember_score_mean": round6(float(nonmember_scores.mean())),
        "zero_fp_tp_count": zero_fp_tp,
        "zero_fp_tpr_empirical": round6(zero_fp_tp / float(member_scores.size)),
        "zero_fp_nonmember_count": int(nonmember_scores.size),
    }
    return payload


def _bootstrap_ci(
    labels: np.ndarray,
    scores: np.ndarray,
    *,
    seed: int,
    iters: int,
) -> dict[str, dict[str, float]]:
    if iters <= 0:
        return {}
    labels_i64 = np.asarray(labels, dtype=np.int64)
    scores_f64 = np.asarray(scores, dtype=np.float64)
    rng = np.random.default_rng(int(seed))
    member_scores = scores_f64[labels_i64 == 1]
    nonmember_scores = scores_f64[labels_i64 == 0]
    values: dict[str, list[float]] = {key: [] for key in METRIC_KEYS}
    values["zero_fp_tpr_empirical"] = []
    for _ in range(int(iters)):
        boot_member = rng.choice(member_scores, size=member_scores.shape[0], replace=True)
        boot_nonmember = rng.choice(nonmember_scores, size=nonmember_scores.shape[0], replace=True)
        boot_labels = np.concatenate(
            [
                np.ones(boot_member.shape[0], dtype=np.int64),
                np.zeros(boot_nonmember.shape[0], dtype=np.int64),
            ]
        )
        boot_scores = np.concatenate([boot_member, boot_nonmember])
        metrics = _score_metrics(boot_labels, boot_scores)
        for key in values:
            values[key].append(float(metrics[key]))
    return {
        key: {
            "p025": round6(float(np.percentile(items, 2.5))),
            "p975": round6(float(np.percentile(items, 97.5))),
        }
        for key, items in values.items()
    }


def _load_optional_logistic(summary_path: Path | None) -> dict[str, Any] | None:
    if summary_path is None:
        return None
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    raw = payload.get("raw_h2", {}).get("logistic", {}).get("aggregate_metrics")
    lowpass = payload.get("lowpass_h2", {}).get("logistic", {}).get("aggregate_metrics")
    return {"raw_h2_logistic": raw, "lowpass_h2_logistic": lowpass}


def _stability_matrix(scores_by_strength: list[np.ndarray], strength_values: list[float]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for left_idx, left_scores in enumerate(scores_by_strength):
        for right_idx in range(left_idx + 1, len(scores_by_strength)):
            rows.append(
                {
                    "left_strength": strength_values[left_idx],
                    "right_strength": strength_values[right_idx],
                    "spearman": round6(spearman(left_scores, scores_by_strength[right_idx])),
                }
            )
    return rows


def _verdict(best: dict[str, Any], logistic_reference: dict[str, Any] | None) -> str:
    metrics = best["metrics"]
    has_signal = (
        float(metrics["auc"]) >= 0.8
        and int(metrics["zero_fp_tp_count"]) >= 2
        and float(metrics["member_score_mean"]) > float(metrics["nonmember_score_mean"])
    )
    beats_h2_curve = False
    if logistic_reference:
        candidates = [
            item for item in logistic_reference.values() if isinstance(item, dict) and "auc" in item
        ]
        beats_h2_curve = bool(candidates) and all(float(metrics["auc"]) > float(item["auc"]) for item in candidates)
    if has_signal and beats_h2_curve:
        return "candidate simple-distance signal; needs independent split or seed stability before any GPU scale-up"
    if has_signal:
        return "candidate simple-distance signal; H2 curve comparison unavailable or inconclusive"
    return "no stable simple-distance signal"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review simple-distance stability for an H2 image-to-image response cache."
    )
    parser.add_argument("--response-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evaluation-summary", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=176)
    parser.add_argument("--bootstrap-iters", type=int, default=200)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with np.load(args.response_cache) as cache:
        if "strengths" not in cache.files:
            raise KeyError("response cache must include strengths for image-to-image review")
        labels = cache["labels"].astype(np.int64)
        strengths = [float(value) for value in cache["strengths"].astype(np.float32).tolist()]
        if not strengths:
            raise ValueError("response cache strengths array is empty")
        min_distances = cache["min_distances_rmse"].astype(np.float32)
        if min_distances.shape != (labels.shape[0], len(strengths)):
            raise ValueError("min_distances_rmse must have shape [sample, strength]")

    candidates: list[dict[str, Any]] = []
    scores_by_strength: list[np.ndarray] = []
    for idx, strength in enumerate(strengths):
        scores = -min_distances[:, idx].astype(np.float64)
        scores_by_strength.append(scores)
        candidates.append(
            {
                "name": f"simple_distance_strength_{strength:.3f}",
                "strength": strength,
                "score_orientation": "negative_min_distance_higher_is_member",
                "metrics": _score_metrics(labels, scores),
                "ci95": _bootstrap_ci(
                    labels,
                    scores,
                    seed=int(args.seed) + idx,
                    iters=int(args.bootstrap_iters),
                ),
            }
        )

    best = max(
        candidates,
        key=lambda item: (
            float(item["metrics"]["tpr_at_0_1pct_fpr"]),
            float(item["metrics"]["auc"]),
            float(item["metrics"]["asr"]),
        ),
    )
    logistic_reference = _load_optional_logistic(args.evaluation_summary)
    summary = {
        "status": "ready",
        "mode": "cpu-cache-simple-distance-review",
        "track": "black-box",
        "method": "H2 image-to-image simple response-distance review",
        "inputs": {
            "response_cache": args.response_cache,
            "evaluation_summary": args.evaluation_summary,
            "sample_count": int(labels.shape[0]),
            "member_count": int((labels == 1).sum()),
            "nonmember_count": int((labels == 0).sum()),
            "strengths": strengths,
            "seed": int(args.seed),
            "bootstrap_iters": int(args.bootstrap_iters),
        },
        "finite_sample_boundary": {
            "low_fpr_fields_mean": "zero-false-positive empirical tail on this split",
            "nonmember_count": int((labels == 0).sum()),
            "calibrated_subpercent_fpr": False,
        },
        "candidates": candidates,
        "best_simple_distance": {
            "name": best["name"],
            "strength": best["strength"],
            "metrics": best["metrics"],
            "ci95": best["ci95"],
        },
        "strength_rank_stability": _stability_matrix(scores_by_strength, strengths),
        "h2_logistic_reference": logistic_reference,
        "verdict": _verdict(best, logistic_reference),
        "next_action": "do not scale H2; choose CPU-first split/seed stability design if pursuing simple img2img distance",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sanitized_payload = _sanitize(summary)
    args.output.write_text(json.dumps(sanitized_payload, indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(sanitized_payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
