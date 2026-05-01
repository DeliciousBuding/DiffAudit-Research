from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from diffaudit.attacks.h2_response_strength import (
    compute_lowpass_min_distances,
    evaluate_h2_response_cache,
    metric_delta,
)


def _sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
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
        description="Review lowpass cutoff sensitivity for an H2 response-strength cache."
    )
    parser.add_argument("--response-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cutoffs", type=float, nargs="+", default=[0.25, 0.35, 0.5, 0.65, 0.75, 0.9])
    parser.add_argument("--seed", type=int, default=176)
    parser.add_argument("--holdout-repeats", type=int, default=7)
    parser.add_argument("--bootstrap-iters", type=int, default=0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cache = np.load(args.response_cache)
    labels = cache["labels"].astype(np.int64)
    timesteps = cache["timesteps"].astype(np.int64)
    inputs = cache["inputs"].astype(np.float32)
    responses = cache["responses"].astype(np.float32)
    raw = evaluate_h2_response_cache(
        labels,
        timesteps,
        cache["min_distances_rmse"].astype(np.float32),
        seed=args.seed,
        holdout_repeats=args.holdout_repeats,
        bootstrap_iters=args.bootstrap_iters,
    )

    cutoffs: list[dict[str, Any]] = []
    for cutoff in args.cutoffs:
        distances = compute_lowpass_min_distances(inputs, responses, cutoff=float(cutoff))
        result = evaluate_h2_response_cache(
            labels,
            timesteps,
            distances,
            seed=args.seed + 500,
            holdout_repeats=args.holdout_repeats,
            bootstrap_iters=args.bootstrap_iters,
        )
        cutoffs.append(
            {
                "cutoff": float(cutoff),
                "logistic": result["logistic"]["aggregate_metrics"],
                "best_low": result["simple"]["best_by_low_fpr"],
                "delta_vs_raw_logistic": metric_delta(
                    result["logistic"]["aggregate_metrics"],
                    raw["logistic"]["aggregate_metrics"],
                ),
                "logistic_beats_simple_low_fpr": result["gates"]["logistic_beats_simple_low_fpr"],
            }
        )

    summary = {
        "status": "ready",
        "mode": "cpu-cache-cutoff-review",
        "cache": str(args.response_cache),
        "raw_logistic": raw["logistic"]["aggregate_metrics"],
        "raw_best_low": raw["simple"]["best_by_low_fpr"],
        "cutoffs": cutoffs,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(_sanitize(summary), indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(_sanitize(summary), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

