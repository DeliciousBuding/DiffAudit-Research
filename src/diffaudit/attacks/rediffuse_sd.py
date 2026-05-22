"""Artifact probe for the collaborator-provided Stable Diffusion ReDiffuse run."""

from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path, PureWindowsPath
from typing import Any

import numpy as np

from diffaudit.utils.metrics import metric_bundle, round6, tpr_at_fpr_from_curve


DEFAULT_BUNDLE_RELATIVE = Path("Download/shared/supplementary/collaborator-stable-diffusion-rediffuse-20260516/raw")
DEFAULT_SOURCE_SUBDIR = Path("SD_MIA_Reproduction")
DEFAULT_ARTIFACT_SUBDIR = Path("runs/final_rediffuse_combined")
DEFAULT_DETECTOR_SUBPATH = Path(
    "论文复现攻击材料_20260516/mia_detector_rediffuse_sweep_best_a2_a5_combined.json"
)
DEFAULT_SCORE_NPZ_SUBPATH = Path("论文复现攻击材料_20260516/merged_rediffuse_scores_a2_a5_combined.npz")
DEFAULT_VALIDATION_SUBPATH = Path("runs/final_rediffuse_combined/rediffuse_holdout_validation_a2_a5_combined.json")
REQUIRED_SOURCE_FILES = (
    "attack.py",
    "components.py",
    "dataset.py",
    "score_single_image.py",
    "select_rediffuse_detector.py",
    "validate_rediffuse_detector.py",
    "coco-2500-random.yaml",
)
REQUIRED_ARTIFACT_FILES = ("metrics.json", "result.csv", "roc_curve.csv")
REQUIRED_RESULT_COLUMNS = ("label", "score", "prediction", "correct")
REQUIRED_ARTIFACT_PATHS = {
    "metrics_json": "metrics.json",
    "result_csv": "result.csv",
    "roc_curve_csv": "roc_curve.csv",
}


def diffaudit_root() -> Path:
    return Path(__file__).resolve().parents[4]


def default_rediffuse_sd_bundle_root() -> Path:
    return diffaudit_root() / DEFAULT_BUNDLE_RELATIVE


def default_rediffuse_sd_artifact_dir(bundle_root: str | Path | None = None) -> Path:
    root = Path(bundle_root) if bundle_root else default_rediffuse_sd_bundle_root()
    return root / DEFAULT_ARTIFACT_SUBDIR


def default_rediffuse_sd_detector_json(bundle_root: str | Path | None = None) -> Path:
    root = Path(bundle_root) if bundle_root else default_rediffuse_sd_bundle_root()
    return root / DEFAULT_DETECTOR_SUBPATH


def default_rediffuse_sd_score_npz(bundle_root: str | Path | None = None) -> Path:
    root = Path(bundle_root) if bundle_root else default_rediffuse_sd_bundle_root()
    return root / DEFAULT_SCORE_NPZ_SUBPATH


def default_rediffuse_sd_validation_json(bundle_root: str | Path | None = None) -> Path:
    root = Path(bundle_root) if bundle_root else default_rediffuse_sd_bundle_root()
    return root / DEFAULT_VALIDATION_SUBPATH


def _path_tail(path_text: str) -> str:
    if "\\" in path_text:
        return PureWindowsPath(path_text).name
    return Path(path_text).name


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path.name} must contain a top-level JSON object")
    return payload


def _as_scalar(value: Any, default: Any = None) -> Any:
    if value is None:
        return default
    arr = np.asarray(value)
    if arr.shape == ():
        return arr.item()
    return arr.tolist()


def _tail_text(text: str, limit: int = 2000) -> str:
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[-limit:]


def _module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _checkpoint_runtime_summary(checkpoint: str | None) -> dict[str, Any]:
    checkpoint_text = str(checkpoint or "")
    if not checkpoint_text:
        return {
            "requested": "",
            "is_local_path": False,
            "exists": False,
            "cache_candidates": [],
        }
    checkpoint_path = Path(checkpoint_text)
    if checkpoint_path.exists():
        return {
            "requested": checkpoint_text,
            "is_local_path": True,
            "exists": True,
            "cache_candidates": [checkpoint_text],
        }
    cache_candidates = []
    if checkpoint_text == "CompVis/stable-diffusion-v1-4":
        cache_candidates.append(str(Path.home() / ".cache" / "huggingface" / "hub" / "models--CompVis--stable-diffusion-v1-4"))
    exists = any(Path(path).exists() for path in cache_candidates)
    return {
        "requested": checkpoint_text,
        "is_local_path": False,
        "exists": exists,
        "cache_candidates": cache_candidates,
    }


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


def _detector_summary(path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    logistic = payload.get("logistic") or {}
    coef = logistic.get("coef")
    return {
        "feature_mode": payload.get("feature_mode"),
        "checkpoint": payload.get("checkpoint"),
        "dataset": payload.get("dataset"),
        "rediffuse_scorer": payload.get("rediffuse_scorer"),
        "threshold_low_score": round6(float(payload.get("threshold", 0.0))),
        "decision_rule": payload.get("decision_rule"),
        "selection_source": payload.get("selection_source"),
        "logistic_dim": len(coef) if isinstance(coef, list) else None,
    }


def _score_npz_summary(path: Path) -> dict[str, Any]:
    data = np.load(path, allow_pickle=True)
    member_features = data["member_features"]
    nonmember_features = data["nonmember_features"]
    return {
        "member_shape": list(member_features.shape),
        "nonmember_shape": list(nonmember_features.shape),
        "feature_dim": int(member_features.shape[1]) if member_features.ndim == 2 else None,
        "dataset": str(_as_scalar(data.get("dataset"), "")),
        "checkpoint": str(_as_scalar(data.get("checkpoint"), "")),
        "attack_num": int(_as_scalar(data.get("attack_num"), 0)),
        "interval": int(_as_scalar(data.get("interval"), 0)),
        "k": int(_as_scalar(data.get("k"), 0)),
        "average": int(_as_scalar(data.get("average"), 0)),
        "torch_dtype": str(_as_scalar(data.get("torch_dtype"), "")),
        "rediffuse_scorer": str(_as_scalar(data.get("rediffuse_scorer"), "")),
    }


def _validation_summary(path: Path) -> dict[str, Any]:
    payload = _read_json(path)
    holdout = payload.get("holdout") or {}
    if isinstance(holdout, list):
        holdout = next((row for row in holdout if row.get("method") == "logistic_l2"), holdout[0] if holdout else {})
    cross_validation = payload.get("cross_validation") or payload.get("cv_summary") or {}
    if isinstance(cross_validation, list):
        cross_validation = next(
            (row for row in cross_validation if row.get("method") == "logistic_l2"),
            cross_validation[0] if cross_validation else {},
        )
    return {
        "holdout_test_auc": holdout.get("test_auc"),
        "cv_mean_test_auc": cross_validation.get("mean_test_auc"),
        "cv_std_test_auc": cross_validation.get("std_test_auc"),
        "shape": payload.get("shape"),
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


def probe_rediffuse_sd_assets(
    bundle_root: str | Path | None = None,
    artifact_dir: str | Path | None = None,
    detector_json: str | Path | None = None,
    score_npz: str | Path | None = None,
    validation_json: str | Path | None = None,
) -> dict[str, Any]:
    bundle = Path(bundle_root) if bundle_root else default_rediffuse_sd_bundle_root()
    source_root = bundle / DEFAULT_SOURCE_SUBDIR
    artifact_path = Path(artifact_dir) if artifact_dir else default_rediffuse_sd_artifact_dir(bundle)
    detector_path = Path(detector_json) if detector_json else default_rediffuse_sd_detector_json(bundle)
    score_npz_path = Path(score_npz) if score_npz else default_rediffuse_sd_score_npz(bundle)
    validation_path = Path(validation_json) if validation_json else default_rediffuse_sd_validation_json(bundle)

    source_checks = {name: (source_root / name).exists() for name in REQUIRED_SOURCE_FILES}
    detector_exists = detector_path.exists()
    score_npz_exists = score_npz_path.exists()
    validation_exists = validation_path.exists()
    artifact_probe = probe_rediffuse_sd_artifacts(artifact_path) if artifact_path.exists() else _build_missing_payload(
        artifact_path,
        {key: False for key in REQUIRED_ARTIFACT_PATHS},
    )

    detector = _detector_summary(detector_path) if detector_exists else {}
    score_packet = _score_npz_summary(score_npz_path) if score_npz_exists else {}
    validation = _validation_summary(validation_path) if validation_exists else {}
    local_runtime = {
        "python_exe": sys.executable,
        "modules": {
            "fire": _module_available("fire"),
            "pytorch_lightning": _module_available("pytorch_lightning"),
            "skimage": _module_available("skimage"),
            "omegaconf": _module_available("omegaconf"),
            "diffusers": _module_available("diffusers"),
            "torchvision": _module_available("torchvision"),
        },
        "checkpoint": _checkpoint_runtime_summary(detector.get("checkpoint")),
    }

    detector_matches_score_npz = True
    if detector_exists and score_npz_exists:
        logistic_dim = detector.get("logistic_dim")
        feature_dim = score_packet.get("feature_dim")
        if logistic_dim is not None and feature_dim is not None:
            detector_matches_score_npz = int(logistic_dim) == int(feature_dim)

    checks = {
        "bundle_root": bundle.exists(),
        "source_root": source_root.exists(),
        "required_source_files": all(source_checks.values()),
        "detector_json": detector_exists,
        "score_npz": score_npz_exists,
        "artifact_dir": artifact_path.exists(),
        "artifact_probe_ready": artifact_probe.get("status") == "ready",
        "detector_matches_score_npz": detector_matches_score_npz,
        "validation_json": validation_exists,
    }
    status = (
        "ready"
        if all(
            checks[key]
            for key in (
                "bundle_root",
                "source_root",
                "required_source_files",
                "detector_json",
                "score_npz",
                "artifact_dir",
                "artifact_probe_ready",
                "detector_matches_score_npz",
            )
        )
        else "blocked"
    )
    missing = []
    if not checks["bundle_root"]:
        missing.append(str(bundle))
    if not checks["source_root"]:
        missing.append(str(source_root))
    missing.extend(str(source_root / name) for name, ready in source_checks.items() if not ready)
    if not checks["detector_json"]:
        missing.append(str(detector_path))
    if not checks["score_npz"]:
        missing.append(str(score_npz_path))
    if not checks["artifact_dir"]:
        missing.append(str(artifact_path))
    if not checks["validation_json"]:
        missing.append(str(validation_path))

    notes = [
        "This bundle adds a candidate-only single-image scoring surface on top of the audited Stable Diffusion ReDiffuse result packet.",
        "It remains non-admitted mainline evidence because the bundle is collaborator-transferred, not a public immutable replay asset.",
        "Single-image scoring still depends on a local Stable Diffusion v1-4 runtime plus the collaborator source tree; it is not an external API-only black-box surface.",
    ]
    if not checks["validation_json"]:
        notes.append(
            "Held-out validation JSON is missing, so the bundle can still be wrapped for scoring but loses one piece of detector-selection evidence."
        )
    if not detector_matches_score_npz:
        notes.append(
            "Detector logistic dimension does not match the saved combined feature packet, so this bundle should not be used for single-image scoring until the detector and NPZ agree."
        )
    missing_runtime_modules = [name for name, ready in local_runtime["modules"].items() if not ready]
    if missing_runtime_modules:
        notes.append(
            "Current interpreter is missing runtime packages for score_single_image.py: "
            + ", ".join(missing_runtime_modules)
        )
    if not local_runtime["checkpoint"]["exists"]:
        notes.append(
            "CompVis/stable-diffusion-v1-4 is not present at a known local path or Hugging Face cache candidate, so direct single-image scoring still needs a local checkpoint source."
        )

    return {
        "status": status,
        "track": "black-box",
        "method": "rediffuse_sd",
        "mode": "asset-probe",
        "artifact_family": "stable-diffusion-rediffuse",
        "checks": checks,
        "paths": {
            "bundle_root": str(bundle),
            "source_root": str(source_root),
            "artifact_dir": str(artifact_path),
            "detector_json": str(detector_path),
            "score_npz": str(score_npz_path),
            "validation_json": str(validation_path),
            "score_script": str(source_root / "score_single_image.py"),
        },
        "required_source_files": source_checks,
        "detector": detector,
        "score_npz": score_packet,
        "validation": validation,
        "local_runtime": local_runtime,
        "artifact_probe": artifact_probe,
        "provenance": {
            "source": "collaborator-manual-transfer",
            "asset_scope": "stable-diffusion-rediffuse-source-plus-detector",
        },
        "missing": missing,
        "missing_items": [Path(item).name for item in missing],
        "recommended_feature_plan": "a2_a5_combined",
        "notes": notes,
    }


def score_rediffuse_sd_image(
    image: str | Path,
    prompt: str,
    bundle_root: str | Path | None = None,
    artifact_dir: str | Path | None = None,
    detector_json: str | Path | None = None,
    score_npz: str | Path | None = None,
    python_exe: str | None = None,
    feature_plan: str = "a2_a5_combined",
    checkpoint: str = "CompVis/stable-diffusion-v1-4",
    torch_dtype: str = "auto",
    output_json: str | Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    image_path = Path(image)
    asset_probe = probe_rediffuse_sd_assets(
        bundle_root=bundle_root,
        artifact_dir=artifact_dir,
        detector_json=detector_json,
        score_npz=score_npz,
    )
    if asset_probe["status"] != "ready":
        return {
            **asset_probe,
            "status": "blocked",
            "mode": "single-image-score",
            "notes": asset_probe["notes"]
            + [
                "Single-image scoring is blocked until the Stable Diffusion ReDiffuse source bundle, detector, and artifact packet all pass the asset probe."
            ],
        }
    if not image_path.exists():
        return {
            **asset_probe,
            "status": "blocked",
            "mode": "single-image-score",
            "error": f"image not found: {image_path}",
            "notes": asset_probe["notes"] + ["Single-image scoring requires a local input image path."],
        }

    detector_path = Path(detector_json) if detector_json else Path(asset_probe["paths"]["detector_json"])
    source_root = Path(asset_probe["paths"]["source_root"])
    score_script = source_root / "score_single_image.py"
    output_path = Path(output_json) if output_json else None
    resolved_python = python_exe or sys.executable
    command = [
        resolved_python,
        str(score_script),
        "--image",
        str(image_path),
        "--prompt",
        prompt,
        "--detector-json",
        str(detector_path),
        "--feature-plan",
        feature_plan,
        "--checkpoint",
        checkpoint,
        "--torch-dtype",
        torch_dtype,
    ]
    if output_path is not None:
        command.extend(["--output-json", str(output_path)])

    if dry_run:
        return {
            "status": "ready",
            "track": "black-box",
            "method": "rediffuse_sd",
            "mode": "single-image-score-dry-run",
            "paths": {
                "image": str(image_path),
                "bundle_root": asset_probe["paths"]["bundle_root"],
                "source_root": str(source_root),
                "detector_json": str(detector_path),
                "score_script": str(score_script),
                "output_json": str(output_path) if output_path is not None else "",
            },
            "runtime": {
                "python_exe": resolved_python,
                "command": command,
                "feature_plan": feature_plan,
                "checkpoint": checkpoint,
                "torch_dtype": torch_dtype,
            },
            "notes": asset_probe["notes"]
            + [
                "Dry-run only: no Stable Diffusion runtime call was made.",
            ],
        }

    completed = subprocess.run(
        args=command,
        cwd=str(source_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    if completed.returncode != 0:
        return {
            "status": "blocked",
            "track": "black-box",
            "method": "rediffuse_sd",
            "mode": "single-image-score",
            "paths": {
                "image": str(image_path),
                "bundle_root": asset_probe["paths"]["bundle_root"],
                "source_root": str(source_root),
                "detector_json": str(detector_path),
                "score_script": str(score_script),
                "output_json": str(output_path) if output_path is not None else "",
            },
            "runtime": {
                "python_exe": resolved_python,
                "command": command,
                "feature_plan": feature_plan,
                "checkpoint": checkpoint,
                "torch_dtype": torch_dtype,
                "returncode": int(completed.returncode),
                "stdout_tail": _tail_text(stdout),
                "stderr_tail": _tail_text(stderr),
            },
            "notes": asset_probe["notes"]
            + [
                "The collaborator single-image scoring script failed under the selected Python interpreter. Use stderr_tail to fix missing runtime packages or checkpoint/model-path issues."
            ],
        }

    try:
        score_payload = json.loads(stdout.strip())
    except json.JSONDecodeError as exc:
        return {
            "status": "blocked",
            "track": "black-box",
            "method": "rediffuse_sd",
            "mode": "single-image-score",
            "error": f"score script did not emit JSON: {exc}",
            "runtime": {
                "python_exe": resolved_python,
                "command": command,
                "stdout_tail": _tail_text(stdout),
                "stderr_tail": _tail_text(stderr),
            },
            "notes": asset_probe["notes"]
            + [
                "The collaborator score script returned non-JSON stdout, so DiffAudit cannot safely ingest the result."
            ],
        }

    return {
        "status": "ready",
        "track": "black-box",
        "method": "rediffuse_sd",
        "mode": "single-image-score",
        "paths": {
            "image": str(image_path),
            "bundle_root": asset_probe["paths"]["bundle_root"],
            "source_root": str(source_root),
            "detector_json": str(detector_path),
            "score_script": str(score_script),
            "output_json": str(output_path) if output_path is not None else "",
        },
        "runtime": {
            "python_exe": resolved_python,
            "command": command,
            "feature_plan": feature_plan,
            "checkpoint": checkpoint,
            "torch_dtype": torch_dtype,
        },
        "score": score_payload,
        "asset_probe": asset_probe,
        "notes": asset_probe["notes"]
        + [
            "This score is candidate-only research output from a collaborator-transferred detector and should not be promoted to an admitted mainline row without the stronger public-asset boundary.",
        ],
    }
