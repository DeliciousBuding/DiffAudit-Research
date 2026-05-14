from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DIFFAUDIT_ROOT = ROOT.parent
DEFAULT_UPSTREAM_ROOT = DIFFAUDIT_ROOT / "Download" / "shared" / "midst-ensemble-mia"
DEFAULT_LABEL_ROOT = (
    DIFFAUDIT_ROOT
    / "Download"
    / "shared"
    / "midst-challenge"
    / "codabench_bundles"
    / "midst_blackbox_single_table"
    / "data"
    / "tabddpm_black_box"
)
DEFAULT_OUTPUT = ROOT / "workspaces" / "black-box" / "artifacts" / "midst-blending-plus-plus-scout-20260515.json"

PHASES = ("train", "dev", "final")
KINDS = ("rmia_scores_k_5", "blending_plus_plus_prediction")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate the public CRCHUM-CITADEL ensemble-mia Blending++ MIDST "
            "TabDDPM black-box score exports against local dev/final labels."
        )
    )
    parser.add_argument("--upstream-root", type=Path, default=DEFAULT_UPSTREAM_ROOT)
    parser.add_argument("--label-root", type=Path, default=DEFAULT_LABEL_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def model_index(path: Path) -> int:
    return int(path.name.split("_")[1])


def iter_model_dirs(upstream_root: Path, phase: str) -> list[Path]:
    phase_root = upstream_root / "input" / "tabddpm_black_box" / phase
    if not phase_root.exists():
        raise FileNotFoundError(f"Missing phase input root: {phase_root}")
    dirs = sorted((p for p in phase_root.iterdir() if p.is_dir()), key=model_index)
    if not dirs:
        raise FileNotFoundError(f"No MIDST model folders found under {phase_root}")
    return dirs


def label_path(model_dir: Path, phase: str, label_root: Path) -> Path:
    if phase == "train":
        return model_dir / "challenge_label.csv"
    return label_root / phase / model_dir.name / "challenge_label.csv"


def score_path(upstream_root: Path, model_dir: Path, phase: str, kind: str) -> Path:
    if kind == "rmia_scores_k_5":
        return model_dir / "rmia_scores_k_5.csv"
    if kind == "blending_plus_plus_prediction":
        if phase == "train":
            return (
                upstream_root
                / "output"
                / "eval"
                / "tabddpm_black_box"
                / "blending_plus_plus"
                / model_dir.name
                / "prediction.csv"
            )
        return (
            upstream_root
            / "output"
            / "infer"
            / "blending_plus_plus"
            / "tabddpm_black_box"
            / phase
            / model_dir.name
            / "prediction.csv"
        )
    raise ValueError(f"unsupported score kind: {kind}")


def load_scores(path: Path, kind: str) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(path)
    if kind == "rmia_scores_k_5":
        frame = pd.read_csv(path)
        if "prob" not in frame.columns:
            raise ValueError(f"{path} must contain a prob column")
        return frame["prob"].to_numpy(dtype=float)
    return pd.read_csv(path, header=None).iloc[:, 0].to_numpy(dtype=float)


def load_labels(path: Path) -> np.ndarray:
    if not path.exists():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    if "is_train" not in frame.columns:
        raise ValueError(f"{path} must contain is_train")
    return frame["is_train"].astype(int).to_numpy()


def rank_average(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    i = 0
    while i < len(values):
        j = i
        while j + 1 < len(values) and values[order[j + 1]] == values[order[i]]:
            j += 1
        ranks[order[i : j + 1]] = (i + j + 2) / 2.0
        i = j + 1
    return ranks


def auc_from_scores(member_scores: np.ndarray, nonmember_scores: np.ndarray) -> float:
    m = len(member_scores)
    n = len(nonmember_scores)
    ranks = rank_average(np.concatenate([member_scores, nonmember_scores]))
    rank_sum = float(ranks[:m].sum())
    return (rank_sum - (m * (m + 1) / 2.0)) / float(m * n)


def orient_scores(labels: np.ndarray, scores: np.ndarray) -> tuple[np.ndarray, str]:
    member_scores = scores[labels == 1]
    nonmember_scores = scores[labels == 0]
    identity_auc = auc_from_scores(member_scores, nonmember_scores)
    negated_auc = auc_from_scores(-member_scores, -nonmember_scores)
    if negated_auc > identity_auc:
        return -scores, "negated"
    return scores, "identity"


def metric_payload(labels: np.ndarray, raw_scores: np.ndarray) -> dict[str, Any]:
    if len(labels) != len(raw_scores):
        raise ValueError(f"label/score length mismatch: {len(labels)} vs {len(raw_scores)}")
    scores, orientation = orient_scores(labels, raw_scores)
    member_scores = scores[labels == 1]
    nonmember_scores = scores[labels == 0]
    thresholds = np.concatenate(([np.inf], np.unique(scores)[::-1], [-np.inf]))
    best_asr = -1.0
    best_threshold = float("nan")
    tpr_at_1 = 0.0
    tpr_at_01 = 0.0
    for threshold in thresholds:
        predictions = scores >= threshold
        tp = int(np.sum(predictions & (labels == 1)))
        fp = int(np.sum(predictions & (labels == 0)))
        tn = int(np.sum((~predictions) & (labels == 0)))
        tpr = tp / float(np.sum(labels == 1))
        fpr = fp / float(np.sum(labels == 0))
        asr = (tp + tn) / float(len(labels))
        if asr > best_asr:
            best_asr = asr
            best_threshold = float(threshold)
        if fpr <= 0.01:
            tpr_at_1 = max(tpr_at_1, tpr)
        if fpr <= 0.001:
            tpr_at_01 = max(tpr_at_01, tpr)
    return {
        "auc": round(float(auc_from_scores(member_scores, nonmember_scores)), 6),
        "asr": round(float(best_asr), 6),
        "tpr_at_1pct_fpr": round(float(tpr_at_1), 6),
        "tpr_at_0_1pct_fpr": round(float(tpr_at_01), 6),
        "threshold": round(float(best_threshold), 6) if math.isfinite(best_threshold) else best_threshold,
        "member_score_mean_raw": round(float(np.mean(raw_scores[labels == 1])), 6),
        "nonmember_score_mean_raw": round(float(np.mean(raw_scores[labels == 0])), 6),
        "orientation": orientation,
    }


def git_head(path: Path) -> str | None:
    try:
        return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def safe_display_path(path: Path) -> str:
    try:
        return f"<DIFFAUDIT_ROOT>/{path.resolve().relative_to(DIFFAUDIT_ROOT).as_posix()}"
    except ValueError:
        return path.as_posix()


def collect_records(upstream_root: Path, label_root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for phase in PHASES:
        for model_dir in iter_model_dirs(upstream_root, phase):
            labels = load_labels(label_path(model_dir, phase, label_root))
            for kind in KINDS:
                path = score_path(upstream_root, model_dir, phase, kind)
                if not path.exists():
                    continue
                scores = load_scores(path, kind)
                records.append(
                    {
                        "phase": phase,
                        "model": model_dir.name,
                        "kind": kind,
                        "n": int(len(labels)),
                        "labels": labels,
                        "scores": scores,
                        "metrics": metric_payload(labels, scores),
                    }
                )
    return records


def aggregate(records: list[dict[str, Any]], kind: str, phases: tuple[str, ...]) -> dict[str, Any]:
    selected = [record for record in records if record["kind"] == kind and record["phase"] in phases]
    if not selected:
        raise ValueError(f"No records for {kind} phases={phases}")
    labels = np.concatenate([record["labels"] for record in selected])
    scores = np.concatenate([record["scores"] for record in selected])
    return {
        "kind": kind,
        "phases": list(phases),
        "model_count": len(selected),
        "rows": int(len(labels)),
        "members": int(np.sum(labels == 1)),
        "nonmembers": int(np.sum(labels == 0)),
        "metrics": metric_payload(labels, scores),
    }


def per_phase(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for kind in KINDS:
        for phase in PHASES:
            selected = [record for record in records if record["kind"] == kind and record["phase"] == phase]
            if not selected:
                continue
            labels = np.concatenate([record["labels"] for record in selected])
            scores = np.concatenate([record["scores"] for record in selected])
            output.append(
                {
                    "kind": kind,
                    "phase": phase,
                    "model_count": len(selected),
                    "rows": int(len(labels)),
                    "metrics": metric_payload(labels, scores),
                }
            )
    return output


def strip_arrays(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key not in {"labels", "scores"}}


def build_artifact(upstream_root: Path, label_root: Path) -> dict[str, Any]:
    if not upstream_root.exists():
        raise FileNotFoundError(f"Missing ensemble-mia checkout: {upstream_root}")
    records = collect_records(upstream_root, label_root)
    blending_dev_final = aggregate(records, "blending_plus_plus_prediction", ("dev", "final"))
    return {
        "schema": "diffaudit.midst_blending_plus_plus_scout.v1",
        "date": "2026-05-15",
        "status": "bounded_external_score_export_scout",
        "source": {
            "repo": "https://github.com/CRCHUM-CITADEL/ensemble-mia",
            "local_checkout": safe_display_path(upstream_root),
            "head": git_head(upstream_root),
            "method": "Blending++ MIDST black-box single-table score exports",
        },
        "inputs": {
            "label_root": safe_display_path(label_root),
            "score_exports": [
                "input/tabddpm_black_box/*/tabddpm_*/rmia_scores_k_5.csv",
                "output/eval/tabddpm_black_box/blending_plus_plus/tabddpm_*/prediction.csv",
                "output/infer/blending_plus_plus/tabddpm_black_box/{dev,final}/tabddpm_*/prediction.csv",
            ],
        },
        "aggregates": [
            aggregate(records, "rmia_scores_k_5", ("train",)),
            aggregate(records, "rmia_scores_k_5", ("dev", "final")),
            aggregate(records, "blending_plus_plus_prediction", ("train",)),
            blending_dev_final,
        ],
        "per_phase": per_phase(records),
        "best_dev_final": blending_dev_final,
        "decision": {
            "verdict": "borderline_best_midst_so_far_but_below_auc_reopen_gate",
            "summary": (
                "Official CITADEL/UQAM Blending++ score exports are materially stronger than prior MIDST nearest, "
                "shadow-distributional, and EPT scouts, especially in the low-FPR tail. The dev+final AUC remains "
                "below the 0.60 reopen floor, so MIDST is not promoted and no expansion is released."
            ),
            "blocked_expansions": [
                "no XGBoost/Optuna retraining grid",
                "no Gower feature-matrix expansion",
                "no TabSyn or multi-table MIDST",
                "no Platform/Runtime admitted row",
            ],
            "current_slots": {
                "active_gpu_question": "none",
                "next_gpu_candidate": "none",
                "CPU sidecar": "none selected after MIDST Blending++ official score-export scout",
            },
        },
        "sample_records": [strip_arrays(record) for record in records[:6]],
    }


def main() -> int:
    args = parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    artifact = build_artifact(args.upstream_root, args.label_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
