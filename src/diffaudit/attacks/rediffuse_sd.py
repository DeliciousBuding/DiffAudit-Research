"""Artifact probe for the collaborator-provided Stable Diffusion ReDiffuse run."""

from __future__ import annotations

import csv
import json
from pathlib import Path, PureWindowsPath
from typing import Any

import numpy as np

from diffaudit.utils.metrics import metric_bundle, round6, tpr_at_fpr_from_curve


REQUIRED_ARTIFACT_FILES = ("metrics.json", "result.csv", "roc_curve.csv")
REQUIRED_RESULT_COLUMNS = ("label", "score", "prediction", "correct")
REQUIRED_ARTIFACT_PATHS = {
    "metrics_json": "metrics.json",
    "result_csv": "result.csv",
    "roc_curve_csv": "roc_curve.csv",
}


def _path_tail(path_text: str) -> str:
    if "\\" in path_text:
        return PureWindowsPath(path_text).name
    return Path(path_text).name


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path.name} must contain a top-level JSON object")
    return payload


def _read_result_csv(path: Path) -> tuple[list[dict[str, str]], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    labels = np.asarray([int(row["label"]) for row in rows], dtype=np.int64)
    scores = np.asarray([float(row["score"]) for row in rows], dtype=np.float64)
    predictions = np.asarray([int(row["prediction"]) for row in rows], dtype=np.int64)
    correct = np.asarray([int(row["correct"]) for row in rows], dtype=np.int64)
    return rows, labels, scores, predictions, correct


def _read_curve_csv(path: Path) -> tuple[np.ndarray, np.ndarray]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    fpr = np.asarray([float(row["fpr"]) for row in rows], dtype=np.float64)
    tpr = np.asarray([float(row["tpr"]) for row in rows], dtype=np.float64)
    return fpr, tpr


def _build_missing_payload(
    artifact_dir: Path,
    file_checks: dict[str, bool],
) -> dict[str, Any]:
    missing = [key for key, ready in file_checks.items() if not ready]
    return {
        "status": "blocked",
        "track": "black-box",
        "method": "rediffuse_sd",
        "mode": "artifact-probe",
        "artifact_family": "stable-diffusion-rediffuse",
        "checks": {
            "artifact_dir": artifact_dir.exists(),
            **file_checks,
        },
        "paths": {
            "artifact_dir": str(artifact_dir),
            "metrics_json": str(artifact_dir / "metrics.json"),
            "result_csv": str(artifact_dir / "result.csv"),
            "roc_curve_csv": str(artifact_dir / "roc_curve.csv"),
            "metrics_csv": str(artifact_dir / "metrics.csv"),
            "roc_curve_png": str(artifact_dir / "roc_curve.png"),
        },
        "missing": [str(artifact_dir / REQUIRED_ARTIFACT_PATHS[key]) for key in missing],
        "missing_items": [REQUIRED_ARTIFACT_PATHS[key] for key in missing],
        "counts": {},
        "reported": {},
        "recomputed": {},
        "consistency": {},
        "boundary": {},
        "notes": [
            "This artifact bundle is incomplete for DiffAudit import until metrics.json, result.csv, and roc_curve.csv are all present."
        ],
    }


def probe_rediffuse_sd_artifacts(artifact_dir: str | Path) -> dict[str, Any]:
    root = Path(artifact_dir)
    file_checks = {
        key: (root / relative).exists()
        for key, relative in REQUIRED_ARTIFACT_PATHS.items()
    }
    if not root.exists() or not all(file_checks.values()):
        payload = _build_missing_payload(root, file_checks)
        payload["checks"]["artifact_dir"] = root.exists()
        return payload

    try:
        metrics_payload = _read_json(root / "metrics.json")
        rows, labels, scores, predictions, correct = _read_result_csv(root / "result.csv")
        fpr, tpr = _read_curve_csv(root / "roc_curve.csv")
    except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        return {
            **_build_missing_payload(root, file_checks),
            "status": "blocked",
            "checks": {
                "artifact_dir": True,
                **file_checks,
                "parsed": False,
            },
            "error": str(exc),
            "notes": [
                "The artifact directory exists, but one of the required files could not be parsed into the expected Stable Diffusion ReDiffuse schema."
            ],
        }

    try:
        fieldnames = tuple(rows[0].keys()) if rows else tuple()
        required_result_columns = all(column in fieldnames for column in REQUIRED_RESULT_COLUMNS)
        member_rows = int((labels == 1).sum())
        nonmember_rows = int((labels == 0).sum())
        balanced_split = member_rows > 0 and nonmember_rows > 0
        recomputed_metrics = metric_bundle(scores, labels)
        curve_tpr_at_1pct = round6(tpr_at_fpr_from_curve(fpr, tpr, 0.01))
        prediction_accuracy = round6(float((predictions == labels).mean())) if len(labels) else 0.0
        correct_accuracy = round6(float(correct.mean())) if len(labels) else 0.0
    except (ValueError, TypeError) as exc:
        return {
            **_build_missing_payload(root, file_checks),
            "status": "blocked",
            "checks": {
                "artifact_dir": True,
                **file_checks,
                "parsed": True,
                "metrics_recomputed": False,
            },
            "error": str(exc),
            "notes": [
                "The artifact files were parsed, but the score packet could not be recomputed into DiffAudit metrics."
            ],
        }

    reported_auc = float(metrics_payload.get("auc", float("nan")))
    reported_asr = float(metrics_payload.get("asr", float("nan")))
    reported_tpr_1pct = float(metrics_payload.get("tpr_at_fpr_1pct", float("nan")))
    reported_member_count = int(metrics_payload.get("num_member", -1))
    reported_nonmember_count = int(metrics_payload.get("num_nonmember", -1))

    reported_result_name = _path_tail(str(metrics_payload.get("result_csv", ""))) if metrics_payload.get("result_csv") else ""
    reported_curve_name = _path_tail(str(metrics_payload.get("roc_curve_csv", ""))) if metrics_payload.get("roc_curve_csv") else ""

    consistency = {
        "reported_auc_matches_recomputed": abs(reported_auc - recomputed_metrics["auc"]) <= 1e-6,
        "reported_asr_matches_recomputed": abs(reported_asr - recomputed_metrics["asr"]) <= 1e-6,
        "reported_tpr_1pct_close_to_curve": abs(reported_tpr_1pct - curve_tpr_at_1pct) <= 0.005,
        "reported_split_counts_match_result": (
            reported_member_count == member_rows and reported_nonmember_count == nonmember_rows
        ),
        "prediction_accuracy_matches_correct_column": abs(prediction_accuracy - correct_accuracy) <= 1e-6,
        "reported_result_name_matches_local_file": reported_result_name in {"", "result.csv"},
        "reported_curve_name_matches_local_file": reported_curve_name in {"", "roc_curve.csv"},
    }
    checks = {
        "artifact_dir": True,
        **file_checks,
        "required_result_columns": required_result_columns,
        "balanced_split": balanced_split,
        "prediction_accuracy_matches_correct_column": consistency["prediction_accuracy_matches_correct_column"],
        "reported_split_counts_match_result": consistency["reported_split_counts_match_result"],
        "reported_auc_matches_recomputed": consistency["reported_auc_matches_recomputed"],
        "reported_asr_matches_recomputed": consistency["reported_asr_matches_recomputed"],
    }
    status = "ready" if all(checks.values()) else "blocked"

    notes = [
        "This is a collaborator-transferred Stable Diffusion ReDiffuse artifact audit, not a new public replay packet.",
        "The run uses local Stable Diffusion pipeline queries and reconstruction similarity, so it is stronger than API-only black-box but still does not use training loss or gradients.",
    ]
    if not consistency["reported_tpr_1pct_close_to_curve"]:
        notes.append(
            "Reported TPR@1%FPR differs from exact curve replay by more than the allowed audit tolerance."
        )
    elif abs(reported_tpr_1pct - curve_tpr_at_1pct) > 1e-6:
        notes.append(
            "Reported TPR@1%FPR differs slightly from exact curve replay; treat it as threshold-grid rounding rather than a schema mismatch."
        )
    if not consistency["reported_result_name_matches_local_file"] or not consistency["reported_curve_name_matches_local_file"]:
        notes.append(
            "metrics.json still points at the collaborator's original local paths, so this bundle has been relocated and should be treated as imported evidence rather than a pristine original directory."
        )

    return {
        "status": status,
        "track": "black-box",
        "method": "rediffuse_sd",
        "mode": "artifact-probe",
        "artifact_family": "stable-diffusion-rediffuse",
        "checks": checks,
        "paths": {
            "artifact_dir": str(root),
            "metrics_json": str(root / "metrics.json"),
            "result_csv": str(root / "result.csv"),
            "roc_curve_csv": str(root / "roc_curve.csv"),
            "metrics_csv": str(root / "metrics.csv"),
            "roc_curve_png": str(root / "roc_curve.png"),
        },
        "counts": {
            "rows": int(len(rows)),
            "member_rows": member_rows,
            "nonmember_rows": nonmember_rows,
            "result_columns": list(fieldnames),
        },
        "reported": {
            "dataset": metrics_payload.get("dataset"),
            "attacker_name": metrics_payload.get("attacker_name"),
            "checkpoint": metrics_payload.get("checkpoint"),
            "feature_mode": metrics_payload.get("feature_mode"),
            "rediffuse_scorer": metrics_payload.get("rediffuse_scorer"),
            "auc": round6(reported_auc),
            "asr": round6(reported_asr),
            "tpr_at_fpr_1pct": round6(reported_tpr_1pct),
            "threshold_confidence": round6(float(metrics_payload.get("threshold_confidence", 0.0))),
            "threshold_low_score": round6(float(metrics_payload.get("threshold_low_score", 0.0))),
            "num_member": reported_member_count,
            "num_nonmember": reported_nonmember_count,
            "score_direction": metrics_payload.get("score_direction"),
            "prediction_rule": metrics_payload.get("prediction_rule"),
        },
        "recomputed": {
            **recomputed_metrics,
            "curve_tpr_at_1pct_fpr": curve_tpr_at_1pct,
            "prediction_accuracy": prediction_accuracy,
            "correct_column_accuracy": correct_accuracy,
        },
        "consistency": consistency,
        "boundary": {
            "paper_claim_black_box": True,
            "training_access": False,
            "gradient_access": False,
            "external_api_only": False,
            "observable_surface": "local_stable_diffusion_query_outputs_and_rediffuse_reconstructions",
        },
        "provenance": {
            "source": "collaborator-manual-transfer",
            "artifact_scope": "stable-diffusion-rediffuse-final-results",
        },
        "missing": [],
        "missing_items": [],
        "notes": notes,
    }
