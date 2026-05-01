"""Compare CLiD prompt-control packets against one baseline packet."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from diffaudit.attacks.clid import _extract_clid_features, load_clid_score_matrix


def _find_single(path: Path, pattern: str) -> Path:
    matches = sorted(path.glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one artifact for {pattern}, got {len(matches)}")
    return matches[0]


def _load_summary(run_root: Path) -> dict[str, Any]:
    path = run_root / "score-summary-workspace" / "summary.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing CLiD score summary: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_features(run_root: Path) -> dict[str, np.ndarray]:
    output_dir = run_root / "outputs"
    member_path = _find_single(output_dir, "*TRTE_train*.txt")
    nonmember_path = _find_single(output_dir, "*TRTE_test*.txt")
    return {
        "member": _extract_clid_features(load_clid_score_matrix(member_path)),
        "nonmember": _extract_clid_features(load_clid_score_matrix(nonmember_path)),
    }


def _corr(left: np.ndarray, right: np.ndarray) -> float | None:
    if left.shape != right.shape or left.size == 0:
        return None
    if float(np.std(left)) == 0.0 or float(np.std(right)) == 0.0:
        return None
    return float(np.corrcoef(left, right)[0, 1])


def _feature_comparison(baseline: dict[str, np.ndarray], control: dict[str, np.ndarray]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for split in ("member", "nonmember"):
        split_result: dict[str, Any] = {}
        for feature_index, feature_name in ((0, "feature0"), (1, "feature1_clid_aux")):
            baseline_values = baseline[split][:, feature_index]
            control_values = control[split][:, feature_index]
            if baseline_values.shape != control_values.shape:
                split_result[feature_name] = {"status": "shape_mismatch"}
                continue
            split_result[feature_name] = {
                "pearson": None if _corr(baseline_values, control_values) is None else round(float(_corr(baseline_values, control_values)), 6),
                "mean_abs_delta": round(float(np.mean(np.abs(control_values - baseline_values))), 6),
            }
        result[split] = split_result
    return result


def _metric_delta(baseline_metrics: dict[str, Any], control_metrics: dict[str, Any]) -> dict[str, float]:
    keys = ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")
    result = {}
    for key in keys:
        baseline_value = float(baseline_metrics.get(key, 0.0))
        control_value = float(control_metrics.get(key, 0.0))
        result[f"{key}_delta"] = round(control_value - baseline_value, 6)
        result[f"{key}_retention"] = round(control_value / baseline_value, 6) if baseline_value else 0.0
    return result


def compare_clid_control_packets(
    baseline: tuple[str, str | Path],
    controls: list[tuple[str, str | Path]],
) -> dict[str, Any]:
    """Compare CLiD prompt-control packets against one baseline packet."""

    baseline_label, baseline_path_raw = baseline
    baseline_path = Path(baseline_path_raw)
    baseline_summary = _load_summary(baseline_path)
    baseline_features = _load_features(baseline_path)
    baseline_metrics = baseline_summary["metrics"]

    control_payloads: list[dict[str, Any]] = []
    for label, path_raw in controls:
        path = Path(path_raw)
        summary = _load_summary(path)
        metrics = summary["metrics"]
        features = _load_features(path)
        control_payloads.append(
            {
                "label": label,
                "run_root": path.as_posix(),
                "metrics": {
                    "auc": round(float(metrics["auc"]), 6),
                    "asr": round(float(metrics["asr"]), 6),
                    "tpr_at_1pct_fpr": round(float(metrics["tpr_at_1pct_fpr"]), 6),
                    "tpr_at_0_1pct_fpr": round(float(metrics["tpr_at_0_1pct_fpr"]), 6),
                    "best_alpha": round(float(metrics.get("best_alpha", 0.0)), 6),
                },
                "metric_delta_vs_baseline": _metric_delta(baseline_metrics, metrics),
                "feature_correlation_vs_baseline": _feature_comparison(baseline_features, features),
            }
        )

    strict_tail_values = [
        float(control["metrics"]["tpr_at_0_1pct_fpr"])
        for control in control_payloads
    ]
    verdict = "controls degrade CLiD strict-tail signal; no control admits CLiD"
    if strict_tail_values and max(strict_tail_values) >= float(baseline_metrics["tpr_at_0_1pct_fpr"]):
        verdict = "a control matches or exceeds baseline strict-tail signal; review before admission"

    return {
        "status": "ready",
        "track": "black-box",
        "method": "clid",
        "mode": "control-attribution",
        "baseline": {
            "label": baseline_label,
            "run_root": baseline_path.as_posix(),
            "metrics": {
                "auc": round(float(baseline_metrics["auc"]), 6),
                "asr": round(float(baseline_metrics["asr"]), 6),
                "tpr_at_1pct_fpr": round(float(baseline_metrics["tpr_at_1pct_fpr"]), 6),
                "tpr_at_0_1pct_fpr": round(float(baseline_metrics["tpr_at_0_1pct_fpr"]), 6),
                "best_alpha": round(float(baseline_metrics.get("best_alpha", 0.0)), 6),
            },
        },
        "controls": control_payloads,
        "verdict": verdict,
        "boundary": (
            "This compares already generated CLiD score packets. It does not admit CLiD, "
            "does not run a model, and does not commit raw score matrices."
        ),
    }
