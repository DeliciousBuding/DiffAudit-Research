from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from diffaudit.attacks.crossbox_pairboard import (
    PAIRBOARD_METRICS,
    REPEATED_HOLDOUT_SEED_STRIDE,
    _fit_logistic_2feature,
    _fit_standardizer,
    _metric_bundle,
    _orient_memberness,
    _round6,
    _series_summary,
    _split_positions,
    _weighted_average,
    load_pairboard_surface,
)


DEFAULT_SURFACES = (
    (
        "pia",
        "workspaces/gray-box/runs/pia-packet-score-export-gsa-full-overlap-20260418-r1/scores.json",
    ),
    (
        "gsa",
        "workspaces/white-box/runs/gsa-loss-score-export-targeted-full-overlap-20260418-r1/summary.json",
    ),
    (
        "sima",
        "workspaces/gray-box/runs/sima-packet-score-export-pia-full-overlap-20260421-r1/scores.json",
    ),
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _resolve(path: str | Path, root: Path) -> Path:
    path = Path(path)
    return path if path.is_absolute() else root / path


def _index_lookup(indices: list[int] | None, count: int) -> dict[int, int]:
    if indices is None:
        return {index: index for index in range(count)}
    return {int(index): position for position, index in enumerate(indices)}


def _align_three_surfaces(surfaces: list[dict[str, Any]]) -> dict[str, Any]:
    if len(surfaces) != 3:
        raise ValueError("X165 tri-surface consensus requires exactly three surfaces")

    def align_split(split_name: str) -> tuple[dict[str, np.ndarray], list[int], str]:
        score_key = f"{split_name}_scores"
        index_key = f"{split_name}_indices"
        lookups = [
            _index_lookup(surface[index_key], int(surface[score_key].shape[0]))
            for surface in surfaces
        ]
        shared_indices = sorted(set(lookups[0]).intersection(lookups[1]).intersection(lookups[2]))
        if not shared_indices:
            raise ValueError(f"No shared {split_name} indices across tri-surface inputs")
        aligned = {
            str(surface["name"]): surface[score_key][
                np.asarray([lookups[position][index] for index in shared_indices], dtype=int)
            ]
            for position, surface in enumerate(surfaces)
        }
        return aligned, shared_indices, "three-way-shared-index-intersection"

    member_scores, member_indices, member_strategy = align_split("member")
    nonmember_scores, nonmember_indices, nonmember_strategy = align_split("nonmember")
    return {
        "surface_names": [str(surface["name"]) for surface in surfaces],
        "member_scores": member_scores,
        "nonmember_scores": nonmember_scores,
        "member_indices": member_indices,
        "nonmember_indices": nonmember_indices,
        "alignment": {
            "member_strategy": member_strategy,
            "nonmember_strategy": nonmember_strategy,
            "shared_member_count": int(len(member_indices)),
            "shared_nonmember_count": int(len(nonmember_indices)),
        },
    }


def _transform_features(
    *,
    aligned: dict[str, Any],
    calibration_fraction: float,
    seed: int,
) -> dict[str, Any]:
    member_count = int(aligned["alignment"]["shared_member_count"])
    nonmember_count = int(aligned["alignment"]["shared_nonmember_count"])
    member_calibration, member_test = _split_positions(member_count, calibration_fraction, seed)
    nonmember_calibration, nonmember_test = _split_positions(nonmember_count, calibration_fraction, seed + 1)

    calibration_features: dict[str, np.ndarray] = {}
    test_features: dict[str, np.ndarray] = {}
    orientations: dict[str, str] = {}
    standardizers: dict[str, dict[str, float]] = {}

    for name in aligned["surface_names"]:
        member_scores = aligned["member_scores"][name]
        nonmember_scores = aligned["nonmember_scores"][name]
        calibration_member = member_scores[member_calibration]
        calibration_nonmember = nonmember_scores[nonmember_calibration]
        oriented_member, oriented_nonmember, orientation = _orient_memberness(
            calibration_member,
            calibration_nonmember,
        )
        standardizer = _fit_standardizer(oriented_member, oriented_nonmember)

        def transform(values: np.ndarray) -> np.ndarray:
            oriented = -values if orientation == "negated" else values
            return (oriented - float(standardizer["mean"])) / float(standardizer["std"])

        calibration_features[name] = np.concatenate(
            [
                transform(calibration_member),
                transform(calibration_nonmember),
            ]
        )
        test_features[name] = np.concatenate(
            [
                transform(member_scores[member_test]),
                transform(nonmember_scores[nonmember_test]),
            ]
        )
        orientations[name] = orientation
        standardizers[name] = {key: _round6(value) for key, value in standardizer.items()}

    calibration_labels = np.concatenate(
        [
            np.ones(member_calibration.shape[0], dtype=int),
            np.zeros(nonmember_calibration.shape[0], dtype=int),
        ]
    )
    test_labels = np.concatenate(
        [
            np.ones(member_test.shape[0], dtype=int),
            np.zeros(nonmember_test.shape[0], dtype=int),
        ]
    )

    return {
        "calibration_features": calibration_features,
        "test_features": test_features,
        "calibration_labels": calibration_labels,
        "test_labels": test_labels,
        "split": {
            "calibration_fraction": float(calibration_fraction),
            "member_calibration_count": int(member_calibration.shape[0]),
            "member_test_count": int(member_test.shape[0]),
            "nonmember_calibration_count": int(nonmember_calibration.shape[0]),
            "nonmember_test_count": int(nonmember_test.shape[0]),
        },
        "orientations": orientations,
        "standardizers": standardizers,
    }


def _choose_best_single(
    candidate_scores: dict[str, np.ndarray],
    labels: np.ndarray,
) -> tuple[str, dict[str, float]]:
    ranked = sorted(
        ((name, _metric_bundle(scores, labels)) for name, scores in candidate_scores.items()),
        key=lambda item: (
            item[1]["auc"],
            item[1]["tpr_at_0_1pct_fpr"],
            item[1]["tpr_at_1pct_fpr"],
            item[1]["asr"],
        ),
        reverse=True,
    )
    return ranked[0]


def _evaluate_once(aligned: dict[str, Any], calibration_fraction: float, seed: int) -> dict[str, Any]:
    features = _transform_features(
        aligned=aligned,
        calibration_fraction=calibration_fraction,
        seed=seed,
    )
    calibration_features = features["calibration_features"]
    test_features = features["test_features"]
    calibration_labels = features["calibration_labels"]
    test_labels = features["test_labels"]

    best_single_name, best_single_calibration_metrics = _choose_best_single(
        calibration_features,
        calibration_labels,
    )
    best_single_test_scores = test_features[best_single_name]

    weighted_calibration_scores, weighted_details = _weighted_average(
        calibration_features=calibration_features,
        calibration_labels=calibration_labels,
        evaluation_features=calibration_features,
    )
    weighted_test_scores, _ = _weighted_average(
        calibration_features=calibration_features,
        calibration_labels=calibration_labels,
        evaluation_features=test_features,
    )

    names = list(aligned["surface_names"])
    calibration_matrix = np.column_stack([calibration_features[name] for name in names])
    test_matrix = np.column_stack([test_features[name] for name in names])
    logistic_weights, logistic_bias = _fit_logistic_2feature(calibration_matrix, calibration_labels)
    logistic_calibration_scores = calibration_matrix @ logistic_weights + logistic_bias
    logistic_test_scores = test_matrix @ logistic_weights + logistic_bias

    consensus_min_calibration_scores = np.min(calibration_matrix, axis=1)
    consensus_min_test_scores = np.min(test_matrix, axis=1)
    consensus_mean_calibration_scores = np.mean(calibration_matrix, axis=1)
    consensus_mean_test_scores = np.mean(test_matrix, axis=1)

    calibration_candidates = {
        "best_single": best_single_calibration_metrics,
        "weighted_average_3feature": _metric_bundle(weighted_calibration_scores, calibration_labels),
        "logistic_3feature": _metric_bundle(logistic_calibration_scores, calibration_labels),
        "consensus_min": _metric_bundle(consensus_min_calibration_scores, calibration_labels),
        "consensus_mean": _metric_bundle(consensus_mean_calibration_scores, calibration_labels),
    }
    test_candidates = {
        "best_single": _metric_bundle(best_single_test_scores, test_labels),
        "weighted_average_3feature": _metric_bundle(weighted_test_scores, test_labels),
        "logistic_3feature": _metric_bundle(logistic_test_scores, test_labels),
        "consensus_min": _metric_bundle(consensus_min_test_scores, test_labels),
        "consensus_mean": _metric_bundle(consensus_mean_test_scores, test_labels),
    }

    return {
        "seed": int(seed),
        "split": features["split"],
        "calibration": {
            "best_single": {
                "selected_surface": best_single_name,
                "selection_metric": "auc",
            },
            "candidates": calibration_candidates,
        },
        "test": {
            "best_single": {
                "selected_surface": best_single_name,
            },
            "candidates": test_candidates,
        },
        "analysis": {
            "surface_orientations": features["orientations"],
            "surface_standardizers": features["standardizers"],
            "weighted_average_3feature": weighted_details,
            "logistic_3feature": {
                "weights": [_round6(value) for value in logistic_weights.tolist()],
                "bias": _round6(logistic_bias),
            },
        },
    }


def _summarize(runs: list[dict[str, Any]]) -> dict[str, Any]:
    candidate_names = list(runs[0]["test"]["candidates"].keys())
    candidate_metrics: dict[str, dict[str, dict[str, float]]] = {}
    best_single_comparison: dict[str, dict[str, dict[str, float | int]]] = {}
    selected_surface_counts: dict[str, int] = {}

    for run in runs:
        name = str(run["test"]["best_single"]["selected_surface"])
        selected_surface_counts[name] = selected_surface_counts.get(name, 0) + 1

    for candidate_name in candidate_names:
        candidate_metrics[candidate_name] = {}
        if candidate_name != "best_single":
            best_single_comparison[candidate_name] = {}
        for metric_name in PAIRBOARD_METRICS:
            values = [float(run["test"]["candidates"][candidate_name][metric_name]) for run in runs]
            candidate_metrics[candidate_name][metric_name] = _series_summary(values)
            if candidate_name == "best_single":
                continue
            deltas = np.asarray(
                [
                    float(run["test"]["candidates"][candidate_name][metric_name])
                    - float(run["test"]["candidates"]["best_single"][metric_name])
                    for run in runs
                ],
                dtype=float,
            )
            best_single_comparison[candidate_name][metric_name] = {
                "win_count": int((deltas > 1e-12).sum()),
                "tie_count": int((np.abs(deltas) <= 1e-12).sum()),
                "loss_count": int((deltas < -1e-12).sum()),
                "mean_delta": _round6(float(deltas.mean())),
                "std_delta": _round6(float(deltas.std())),
                "min_delta": _round6(float(deltas.min())),
                "max_delta": _round6(float(deltas.max())),
            }

    return {
        "repeats": int(len(runs)),
        "selected_surface_counts": selected_surface_counts,
        "candidate_metrics": candidate_metrics,
        "best_single_comparison": best_single_comparison,
    }


def _candidate_passes_low_fpr_gate(comparison: dict[str, dict[str, float | int]]) -> bool:
    tpr01 = comparison["tpr_at_0_1pct_fpr"]
    tpr1 = comparison["tpr_at_1pct_fpr"]
    auc = comparison["auc"]
    return (
        int(tpr01["loss_count"]) == 0
        and int(tpr01["win_count"]) >= 4
        and float(tpr01["mean_delta"]) > 0.0
        and int(tpr1["loss_count"]) <= 1
        and float(tpr1["mean_delta"]) >= 0.0
        and float(auc["mean_delta"]) >= 0.0
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    root = _repo_root()
    run_root = _resolve(args.run_root, root)
    run_root.mkdir(parents=True, exist_ok=True)

    surface_specs = [
        (name, _resolve(path, root))
        for name, path in DEFAULT_SURFACES
    ]
    surfaces = [
        load_pairboard_surface(path, name=name)
        for name, path in surface_specs
    ]
    aligned = _align_three_surfaces(surfaces)
    runs = [
        _evaluate_once(
            aligned=aligned,
            calibration_fraction=args.calibration_fraction,
            seed=int(args.seed) + int(index) * REPEATED_HOLDOUT_SEED_STRIDE,
        )
        for index in range(int(args.repeats))
    ]
    aggregate = _summarize(runs)

    gates = []
    for candidate_name, comparison in aggregate["best_single_comparison"].items():
        gates.append(
            {
                "candidate": candidate_name,
                "passed": _candidate_passes_low_fpr_gate(comparison),
                "rule": "no TPR@0.1%FPR losses, at least four low-FPR wins, nonnegative TPR@1%FPR and AUC mean deltas",
            }
        )

    passed_candidates = [gate["candidate"] for gate in gates if gate["passed"]]
    verdict = "positive but bounded" if passed_candidates else "negative but useful"
    decision = {
        "promotion_allowed": False,
        "gpu_release_allowed": False,
        "active_gpu_question": "none",
        "next_gpu_candidate": "none until a follow-up freezes a genuinely new surface-acquisition hypothesis",
        "next_live_lane": "X166 I-A / cross-box boundary hardening after tri-surface consensus review",
        "passed_candidates": passed_candidates,
    }

    payload = {
        "status": "ready",
        "task": "X-165 cross-box tri-surface low-FPR consensus packet",
        "mode": "cpu-repeated-holdout",
        "surfaces": [
            {
                "name": name,
                "path": str(path.relative_to(root)),
            }
            for name, path in surface_specs
        ],
        "alignment": aligned["alignment"],
        "calibration_fraction": float(args.calibration_fraction),
        "repeats": int(args.repeats),
        "seed_start": int(args.seed),
        "seed_stride": REPEATED_HOLDOUT_SEED_STRIDE,
        "runs": runs,
        "aggregate": aggregate,
        "gates": gates,
        "verdict": verdict,
        "decision": decision,
        "notes": [
            "This is a CPU-only consensus packet on existing shared score surfaces.",
            "It does not change admitted tables and does not authorize GPU by itself.",
            "Low-FPR repeated-holdout wins are required before any follow-up surface-acquisition work can be considered.",
        ],
    }
    (run_root / "summary.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-root",
        default="workspaces/cross-box/runs/x165-crossbox-trisurface-consensus-20260429-r1",
    )
    parser.add_argument("--calibration-fraction", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=23)
    parser.add_argument("--repeats", type=int, default=7)
    args = parser.parse_args()
    payload = run(args)
    print(json.dumps({"summary": payload["task"], "verdict": payload["verdict"], "decision": payload["decision"]}, indent=2))


if __name__ == "__main__":
    main()
