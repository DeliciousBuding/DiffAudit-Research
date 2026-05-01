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
        description="Evaluate a black-box H2 response-strength response-cache.npz file."
    )
    parser.add_argument("--response-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=176)
    parser.add_argument("--holdout-repeats", type=int, default=7)
    parser.add_argument("--bootstrap-iters", type=int, default=200)
    parser.add_argument("--frequency-cutoff", type=float, default=0.5)
    parser.add_argument("--no-lowpass", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cache = np.load(args.response_cache)
    labels = cache["labels"].astype(np.int64)
    timesteps = cache["timesteps"].astype(np.int64)
    raw_min_distances = cache["min_distances_rmse"].astype(np.float32)

    raw = evaluate_h2_response_cache(
        labels,
        timesteps,
        raw_min_distances,
        seed=args.seed,
        holdout_repeats=args.holdout_repeats,
        bootstrap_iters=args.bootstrap_iters,
    )

    lowpass = None
    if not args.no_lowpass:
        if "lowpass_min_distances_rmse" in cache.files:
            lowpass_min_distances = cache["lowpass_min_distances_rmse"].astype(np.float32)
        elif "inputs" in cache.files and "responses" in cache.files:
            lowpass_min_distances = compute_lowpass_min_distances(
                cache["inputs"].astype(np.float32),
                cache["responses"].astype(np.float32),
                cutoff=args.frequency_cutoff,
            )
        else:
            lowpass_min_distances = None

        if lowpass_min_distances is not None:
            lowpass = evaluate_h2_response_cache(
                labels,
                timesteps,
                lowpass_min_distances,
                seed=args.seed + 500,
                holdout_repeats=args.holdout_repeats,
                bootstrap_iters=args.bootstrap_iters,
            )

    summary: dict[str, Any] = {
        "status": "ready",
        "track": "black-box",
        "method": "H2 response-strength cache evaluation",
        "mode": "cpu-cache-eval",
        "inputs": {
            "response_cache": str(args.response_cache),
            "sample_count": int(labels.shape[0]),
            "member_count": int((labels == 1).sum()),
            "nonmember_count": int((labels == 0).sum()),
            "timesteps": [int(value) for value in timesteps.tolist()],
            "seed": int(args.seed),
            "holdout_repeats": int(args.holdout_repeats),
            "bootstrap_iters": int(args.bootstrap_iters),
            "frequency_cutoff": None if args.no_lowpass else float(args.frequency_cutoff),
        },
        "raw_h2": raw,
        "lowpass_h2": lowpass,
    }
    if lowpass is not None:
        summary["lowpass_minus_raw_logistic"] = metric_delta(
            lowpass["logistic"]["aggregate_metrics"],
            raw["logistic"]["aggregate_metrics"],
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(_sanitize(summary), indent=2, ensure_ascii=True), encoding="utf-8")
    print(json.dumps(_sanitize(summary), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

