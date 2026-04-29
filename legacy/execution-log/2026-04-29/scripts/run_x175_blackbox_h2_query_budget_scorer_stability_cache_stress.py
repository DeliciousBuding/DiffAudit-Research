from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

import run_x168_blackbox_h2_strength_response_gpu_scout as x168
import run_x171_blackbox_h3_frequency_filter_cache_ablation as x171


METRIC_KEYS = ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run X-175 H2 query-budget and scorer-stability cache stress on the X172 cache."
    )
    parser.add_argument(
        "--response-cache",
        type=Path,
        default=Path("workspaces/black-box/runs/x172-h2-strength-response-validation-20260429-r1/response-cache.npz"),
    )
    parser.add_argument("--run-root", type=Path, default=None)
    parser.add_argument("--seed", type=int, default=175)
    parser.add_argument("--holdout-splits", type=int, default=7)
    parser.add_argument("--bootstrap-iters", type=int, default=200)
    parser.add_argument("--frequency-cutoff", type=float, default=0.5)
    return parser.parse_args()


def metric_delta(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    return {key: round(float(left[key]) - float(right[key]), 6) for key in METRIC_KEYS}


def low_fpr_pair(metrics: dict[str, float]) -> tuple[float, float]:
    return (float(metrics["tpr_at_1pct_fpr"]), float(metrics["tpr_at_0_1pct_fpr"]))


def beats_low_fpr(logistic_metrics: dict[str, float], simple_metrics: dict[str, float]) -> bool:
    logistic_1pct, logistic_01pct = low_fpr_pair(logistic_metrics)
    simple_1pct, simple_01pct = low_fpr_pair(simple_metrics)
    return logistic_1pct > simple_1pct and logistic_01pct > simple_01pct


def not_both_low_fpr_zero(metrics: dict[str, float]) -> bool:
    tpr_1pct, tpr_01pct = low_fpr_pair(metrics)
    return tpr_1pct > 0.0 or tpr_01pct > 0.0


def compute_lowpass_distances(
    inputs: np.ndarray,
    responses: np.ndarray,
    cutoff: float,
) -> np.ndarray:
    mask = x171.build_mask(int(inputs.shape[-2]), int(inputs.shape[-1]), "lowpass", cutoff=float(cutoff))
    filtered_inputs = x171.apply_frequency_mask(inputs.astype(np.float32), mask)
    filtered_responses = x171.apply_frequency_mask(responses.astype(np.float32), mask)
    delta = filtered_responses - filtered_inputs[:, None, None, :, :, :]
    return np.sqrt(np.mean(delta * delta, axis=(3, 4, 5))).astype(np.float32)


def evaluate_scorer(
    labels: np.ndarray,
    features: np.ndarray,
    timesteps: list[int],
    seed: int,
    holdout_splits: int,
    bootstrap_iters: int,
    feature_label: str,
) -> dict[str, Any]:
    simple = x168.evaluate_simple_baselines(
        labels=labels,
        min_distances=features.astype(np.float32),
        timesteps=timesteps,
        seed=seed,
        bootstrap_iters=bootstrap_iters,
    )
    logistic = x168.evaluate_logistic_holdout(
        labels=labels,
        features=features.astype(np.float32),
        seed=seed,
        split_count=holdout_splits,
        test_size=0.5,
        bootstrap_iters=bootstrap_iters,
    )
    logistic["features"] = feature_label
    return {
        "simple_baselines": simple,
        "logistic": logistic,
        "gates": {
            "best_simple_by_low_fpr": simple["best_by_low_fpr"],
            "logistic_minus_best_simple_by_low_fpr": metric_delta(
                logistic["aggregate_metrics"], simple["best_by_low_fpr"]["metrics"]
            ),
            "logistic_beats_best_simple_on_both_low_fpr": beats_low_fpr(
                logistic["aggregate_metrics"], simple["best_by_low_fpr"]["metrics"]
            ),
            "logistic_not_both_low_fpr_zero": not_both_low_fpr_zero(logistic["aggregate_metrics"]),
        },
    }


def evaluate_logistic_only(
    labels: np.ndarray,
    features: np.ndarray,
    seed: int,
    holdout_splits: int,
    bootstrap_iters: int,
    feature_label: str,
) -> dict[str, Any]:
    logistic = x168.evaluate_logistic_holdout(
        labels=labels,
        features=features.astype(np.float32),
        seed=seed,
        split_count=holdout_splits,
        test_size=0.5,
        bootstrap_iters=bootstrap_iters,
    )
    logistic["features"] = feature_label
    return {
        "logistic": logistic,
        "gates": {
            "logistic_not_both_low_fpr_zero": not_both_low_fpr_zero(logistic["aggregate_metrics"]),
        },
    }


def summarize_low_fpr(logistic: dict[str, Any]) -> dict[str, float]:
    metrics = logistic["aggregate_metrics"]
    return {
        "auc": float(metrics["auc"]),
        "asr": float(metrics["asr"]),
        "tpr_at_1pct_fpr": float(metrics["tpr_at_1pct_fpr"]),
        "tpr_at_0_1pct_fpr": float(metrics["tpr_at_0_1pct_fpr"]),
    }


def score_stress_gate(full: dict[str, Any], one_repeat: dict[str, Any], leave_one_out: dict[str, Any]) -> dict[str, Any]:
    one_repeat_not_collapsed = all(
        bool(repeat_payload["gates"]["logistic_not_both_low_fpr_zero"])
        for repeat_payload in one_repeat.values()
    )
    loso_not_collapsed = all(
        bool(drop_payload["gates"]["logistic_not_both_low_fpr_zero"])
        for drop_payload in leave_one_out.values()
    )
    passes = (
        bool(full["gates"]["logistic_beats_best_simple_on_both_low_fpr"])
        and one_repeat_not_collapsed
        and loso_not_collapsed
    )
    return {
        "beats_best_simple_on_both_low_fpr": bool(full["gates"]["logistic_beats_best_simple_on_both_low_fpr"]),
        "one_repeat_not_collapsed": one_repeat_not_collapsed,
        "leave_one_strength_out_not_collapsed": loso_not_collapsed,
        "stress_gate_passed": passes,
    }


def main() -> int:
    args = parse_args()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = args.run_root or Path(f"workspaces/black-box/runs/x175-h2-query-budget-scorer-stability-{timestamp}")
    run_root.mkdir(parents=True, exist_ok=True)
    started_at = time.perf_counter()

    try:
        cache = np.load(args.response_cache)
        labels = cache["labels"].astype(np.int64)
        timesteps = [int(value) for value in cache["timesteps"].tolist()]
        inputs = cache["inputs"].astype(np.float32)
        responses = cache["responses"].astype(np.float32)
        raw_repeat_distances = cache["distances_rmse"].astype(np.float32)
        raw_full_features = raw_repeat_distances.min(axis=2).astype(np.float32)
        lowpass_repeat_distances = compute_lowpass_distances(inputs, responses, cutoff=args.frequency_cutoff)
        lowpass_full_features = lowpass_repeat_distances.min(axis=2).astype(np.float32)

        repeat_count = int(raw_repeat_distances.shape[2])
        if repeat_count < 2:
            raise ValueError(f"X175 expects at least two repeats in the cache, got {repeat_count}")

        full_budget = {
            "raw_h2": evaluate_scorer(
                labels=labels,
                features=raw_full_features,
                timesteps=timesteps,
                seed=args.seed,
                holdout_splits=args.holdout_splits,
                bootstrap_iters=args.bootstrap_iters,
                feature_label="raw H2 two-repeat minimum RMSE per timestep",
            ),
            "lowpass_0_5_h2": evaluate_scorer(
                labels=labels,
                features=lowpass_full_features,
                timesteps=timesteps,
                seed=args.seed + 500,
                holdout_splits=args.holdout_splits,
                bootstrap_iters=args.bootstrap_iters,
                feature_label=f"lowpass_{args.frequency_cutoff:g} H2 two-repeat minimum RMSE per timestep",
            ),
        }

        one_repeat: dict[str, dict[str, Any]] = {"raw_h2": {}, "lowpass_0_5_h2": {}}
        for repeat_idx in range(repeat_count):
            one_repeat["raw_h2"][f"repeat_{repeat_idx}"] = evaluate_logistic_only(
                labels=labels,
                features=raw_repeat_distances[:, :, repeat_idx],
                seed=args.seed + 1000 + repeat_idx,
                holdout_splits=args.holdout_splits,
                bootstrap_iters=args.bootstrap_iters,
                feature_label=f"raw H2 one-repeat RMSE per timestep, repeat {repeat_idx}",
            )
            one_repeat["lowpass_0_5_h2"][f"repeat_{repeat_idx}"] = evaluate_logistic_only(
                labels=labels,
                features=lowpass_repeat_distances[:, :, repeat_idx],
                seed=args.seed + 1500 + repeat_idx,
                holdout_splits=args.holdout_splits,
                bootstrap_iters=args.bootstrap_iters,
                feature_label=f"lowpass_{args.frequency_cutoff:g} H2 one-repeat RMSE per timestep, repeat {repeat_idx}",
            )

        leave_one_out: dict[str, dict[str, Any]] = {"raw_h2": {}, "lowpass_0_5_h2": {}}
        for drop_idx, timestep in enumerate(timesteps):
            keep_indices = [idx for idx in range(len(timesteps)) if idx != drop_idx]
            kept_timesteps = [timesteps[idx] for idx in keep_indices]
            leave_one_out["raw_h2"][f"drop_timestep_{timestep}"] = evaluate_logistic_only(
                labels=labels,
                features=raw_full_features[:, keep_indices],
                seed=args.seed + 2000 + drop_idx,
                holdout_splits=args.holdout_splits,
                bootstrap_iters=args.bootstrap_iters,
                feature_label=f"raw H2 leave-one-strength-out, kept timesteps {kept_timesteps}",
            )
            leave_one_out["lowpass_0_5_h2"][f"drop_timestep_{timestep}"] = evaluate_logistic_only(
                labels=labels,
                features=lowpass_full_features[:, keep_indices],
                seed=args.seed + 2500 + drop_idx,
                holdout_splits=args.holdout_splits,
                bootstrap_iters=args.bootstrap_iters,
                feature_label=f"lowpass_{args.frequency_cutoff:g} H2 leave-one-strength-out, kept timesteps {kept_timesteps}",
            )

        raw_gate = score_stress_gate(full_budget["raw_h2"], one_repeat["raw_h2"], leave_one_out["raw_h2"])
        lowpass_gate = score_stress_gate(
            full_budget["lowpass_0_5_h2"],
            one_repeat["lowpass_0_5_h2"],
            leave_one_out["lowpass_0_5_h2"],
        )

        if raw_gate["stress_gate_passed"]:
            selected_future_scorer = "raw_h2"
            scorer_selection_rule = (
                "Keep raw H2 as primary for any future GPU rung; lowpass_0_5 remains mandatory secondary."
            )
            verdict = "positive stress / raw-primary GPU candidate released"
            next_gpu_candidate = (
                "provisional X176 H2 non-overlap 256/256 validation at split offset 192 with raw H2 primary"
            )
        elif lowpass_gate["stress_gate_passed"]:
            selected_future_scorer = "lowpass_0_5_h2"
            scorer_selection_rule = (
                "Promote only the X174-predeclared lowpass_0_5 secondary to primary for the next GPU rung; "
                "do not sweep additional frequency cutoffs on the future packet."
            )
            verdict = "positive stress / lowpass-primary GPU candidate released"
            next_gpu_candidate = (
                "provisional X176 H2 non-overlap 256/256 validation at split offset 192 with lowpass_0_5 primary"
            )
        else:
            selected_future_scorer = "none"
            scorer_selection_rule = (
                "No H2 scorer clears the X174 stress gate; hold larger H2 GPU expansion and pivot to comparator or new-surface review."
            )
            verdict = "negative but useful / GPU hold"
            next_gpu_candidate = "none"

        compact_scores = {
            "full_budget": {
                name: summarize_low_fpr(payload["logistic"])
                for name, payload in full_budget.items()
            },
            "one_repeat": {
                scorer: {
                    repeat: summarize_low_fpr(payload["logistic"])
                    for repeat, payload in scorer_payload.items()
                }
                for scorer, scorer_payload in one_repeat.items()
            },
            "leave_one_strength_out": {
                scorer: {
                    dropped: summarize_low_fpr(payload["logistic"])
                    for dropped, payload in scorer_payload.items()
                }
                for scorer, scorer_payload in leave_one_out.items()
            },
        }
        (run_root / "compact-scores.json").write_text(
            json.dumps(x168.json_sanitize(compact_scores), indent=2, ensure_ascii=True),
            encoding="utf-8",
        )

        summary = {
            "status": "ready",
            "task": "X-175 H2 query-budget and scorer-stability cache stress",
            "mode": "cpu-cache-stress",
            "track": "black-box",
            "method": "H2 strength-response cache stress over raw and X174-predeclared lowpass_0_5 scorers",
            "admitted_change": "none",
            "inputs": {
                "response_cache": str(args.response_cache),
                "seed": int(args.seed),
                "holdout_splits": int(args.holdout_splits),
                "bootstrap_iters": int(args.bootstrap_iters),
                "timesteps": timesteps,
                "frequency_cutoff": float(args.frequency_cutoff),
                "samples": int(labels.shape[0]),
                "member_count": int((labels == 1).sum()),
                "nonmember_count": int((labels == 0).sum()),
                "repeat_count": repeat_count,
            },
            "artifact_paths": {
                "summary": str(run_root / "summary.json"),
                "compact_scores": str(run_root / "compact-scores.json"),
            },
            "full_budget": full_budget,
            "one_repeat_budget": one_repeat,
            "leave_one_strength_out": leave_one_out,
            "gates": {
                "raw_h2": raw_gate,
                "lowpass_0_5_h2": lowpass_gate,
                "selected_future_scorer": selected_future_scorer,
                "scorer_selection_rule": scorer_selection_rule,
                "larger_gpu_candidate_released": selected_future_scorer != "none",
                "promotion_allowed": False,
            },
            "runtime": {
                "wall_clock_seconds": round(float(time.perf_counter() - started_at), 6),
            },
            "verdict": verdict,
            "next_gpu_candidate": next_gpu_candidate,
            "cpu_sidecar": "I-A / cross-box boundary maintenance",
            "notes": [
                "This is a CPU-only stress of the X172 response cache; it does not add model calls.",
                "Lowpass_0_5 is the only alternate scorer considered because X174 predeclared it as the mandatory secondary.",
                "A positive stress gate can release a bounded larger H2 validation candidate, but still cannot admit H2 or replace recon.",
            ],
        }
    except Exception as exc:
        summary = {
            "status": "error",
            "task": "X-175 H2 query-budget and scorer-stability cache stress",
            "error": repr(exc),
            "runtime": {
                "wall_clock_seconds": round(float(time.perf_counter() - started_at), 6),
            },
            "verdict": "blocked",
            "next_gpu_candidate": "none",
        }
        (run_root / "summary.json").write_text(
            json.dumps(x168.json_sanitize(summary), indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        raise

    (run_root / "summary.json").write_text(
        json.dumps(x168.json_sanitize(summary), indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    print(json.dumps(x168.json_sanitize(summary), indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
