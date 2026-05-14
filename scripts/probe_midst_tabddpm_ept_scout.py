from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[1]
DIFFAUDIT_ROOT = ROOT.parent
DEFAULT_DATA_ROOT = DIFFAUDIT_ROOT / "Download" / "shared" / "midst-data" / "tabddpm_black_box"
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
DEFAULT_OUTPUT = ROOT / "workspaces" / "black-box" / "artifacts" / "midst-tabddpm-ept-scout-20260515.json"

PHASES = ("train", "dev", "final")
ID_COLUMNS = ("trans_id", "account_id")
EXCLUDED_TARGET_COLUMNS = ("account",)
CLASSIFICATION_UNIQUE_THRESHOLD = 20


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a bounded MIA-EPT-style error-prediction profile scout on "
            "local MIDST TabDDPM black-box single-table assets."
        )
    )
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--label-root", type=Path, default=DEFAULT_LABEL_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--seed", type=int, default=20260515)
    parser.add_argument("--n-estimators", type=int, default=48)
    parser.add_argument("--max-depth", type=int, default=14)
    parser.add_argument("--min-samples-leaf", type=int, default=5)
    parser.add_argument("--synthetic-sample-size", type=int, default=20000)
    parser.add_argument("--max-models-per-phase", type=int, default=None)
    parser.add_argument("--include-account-feature", action="store_true")
    parser.add_argument("--reopen-auc-floor", type=float, default=0.60)
    parser.add_argument("--strict-tail-floor", type=float, default=0.02)
    return parser.parse_args()


def model_index(path: Path) -> int:
    match = re.search(r"_(\d+)$", path.name)
    if match is None:
        raise ValueError(f"Could not parse model index from {path}")
    return int(match.group(1))


def iter_model_dirs(data_root: Path, phase: str, max_models: int | None) -> list[Path]:
    phase_root = data_root / phase
    if not phase_root.exists():
        raise FileNotFoundError(f"Missing phase directory: {phase_root}")
    dirs = sorted((p for p in phase_root.iterdir() if p.is_dir()), key=model_index)
    if max_models is not None:
        dirs = dirs[:max_models]
    if not dirs:
        raise FileNotFoundError(f"No model directories found in {phase_root}")
    return dirs


def label_path(model_dir: Path, phase: str, label_root: Path) -> Path:
    if phase == "train":
        return model_dir / "challenge_label.csv"
    return label_root / phase / model_dir.name / "challenge_label.csv"


def load_model_frame(model_dir: Path, phase: str, label_root: Path, sample_size: int, seed: int) -> tuple[pd.DataFrame, np.ndarray, pd.DataFrame]:
    challenge_path = model_dir / "challenge_with_id.csv"
    synthetic_path = model_dir / "trans_synthetic.csv"
    labels_path = label_path(model_dir, phase, label_root)
    for path in (challenge_path, synthetic_path, labels_path):
        if not path.exists():
            raise FileNotFoundError(f"Missing required MIDST file: {path}")

    challenge = pd.read_csv(challenge_path)
    synthetic = pd.read_csv(synthetic_path)
    labels = pd.read_csv(labels_path)
    if "is_train" not in labels.columns:
        raise ValueError(f"{labels_path} does not contain is_train")
    y = labels["is_train"].astype(int).to_numpy()
    if len(challenge) != len(y):
        raise ValueError(f"Challenge/label length mismatch in {model_dir}: {len(challenge)} vs {len(y)}")

    if sample_size and len(synthetic) > sample_size:
        synthetic = synthetic.sample(n=sample_size, random_state=seed + model_index(model_dir)).reset_index(drop=True)
    return challenge, y, synthetic


def shared_generated_columns(challenge: pd.DataFrame, synthetic: pd.DataFrame) -> list[str]:
    shared = [col for col in synthetic.columns if col in challenge.columns]
    return [col for col in shared if col not in ID_COLUMNS]


def target_columns(columns: Iterable[str]) -> list[str]:
    return [col for col in columns if col not in EXCLUDED_TARGET_COLUMNS]


def is_classification_target(series: pd.Series) -> bool:
    return int(series.nunique(dropna=True)) <= CLASSIFICATION_UNIQUE_THRESHOLD


def predictor_features(columns: list[str], target_col: str, include_account: bool) -> list[str]:
    features = [col for col in columns if col != target_col]
    if not include_account:
        features = [col for col in features if col != "account"]
    if not features:
        raise ValueError(f"No predictor features remain for target {target_col}")
    return features


def fit_predict_target(
    synthetic: pd.DataFrame,
    challenge: pd.DataFrame,
    columns: list[str],
    target_col: str,
    args: argparse.Namespace,
) -> tuple[np.ndarray, np.ndarray, str]:
    features = predictor_features(columns, target_col, args.include_account_feature)
    task_type = "classification" if is_classification_target(synthetic[target_col]) else "regression"
    model_seed = args.seed + sum(ord(ch) for ch in target_col)

    if task_type == "classification":
        estimator = RandomForestClassifier(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            min_samples_leaf=args.min_samples_leaf,
            random_state=model_seed,
            n_jobs=1,
        )
    else:
        estimator = RandomForestRegressor(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            min_samples_leaf=args.min_samples_leaf,
            random_state=model_seed,
            n_jobs=1,
        )

    pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("model", estimator),
        ]
    )
    x_train = synthetic[features].apply(pd.to_numeric, errors="coerce")
    y_train = synthetic[target_col].apply(pd.to_numeric, errors="coerce")
    x_test = challenge[features].apply(pd.to_numeric, errors="coerce")
    y_test = challenge[target_col].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)

    pipeline.fit(x_train, y_train)
    predictions = pipeline.predict(x_test).astype(float)
    return y_test, predictions, task_type


def extract_error_profile(challenge: pd.DataFrame, synthetic: pd.DataFrame, args: argparse.Namespace) -> pd.DataFrame:
    columns = shared_generated_columns(challenge, synthetic)
    output: dict[str, np.ndarray] = {}

    for target_col in target_columns(columns):
        actual, prediction, task_type = fit_predict_target(synthetic, challenge, columns, target_col, args)
        output[f"{target_col}_actual"] = actual
        output[f"{target_col}_prediction"] = prediction
        if task_type == "classification":
            output[f"{target_col}_accuracy"] = (prediction == actual).astype(float)
        else:
            error = np.abs(prediction - actual)
            denom = np.maximum(np.abs(actual), 1e-6)
            output[f"{target_col}_error"] = error
            output[f"{target_col}_error_ratio"] = np.clip(error / denom, 0.0, 1e6)

    features = pd.DataFrame(output)
    return features.replace([np.inf, -np.inf], np.nan)


def build_phase_features(phase: str, args: argparse.Namespace) -> tuple[pd.DataFrame, np.ndarray, list[int]]:
    frames: list[pd.DataFrame] = []
    labels: list[np.ndarray] = []
    model_ids: list[int] = []
    model_dirs = iter_model_dirs(args.data_root, phase, args.max_models_per_phase)

    for model_dir in model_dirs:
        challenge, y, synthetic = load_model_frame(
            model_dir=model_dir,
            phase=phase,
            label_root=args.label_root,
            sample_size=args.synthetic_sample_size,
            seed=args.seed,
        )
        features = extract_error_profile(challenge, synthetic, args)
        features.insert(0, "model_index", float(model_index(model_dir)))
        frames.append(features)
        labels.append(y)
        model_ids.append(model_index(model_dir))
        print(f"{phase}/{model_dir.name}: rows={len(y)} features={features.shape[1]}")

    return pd.concat(frames, ignore_index=True), np.concatenate(labels), model_ids


def asr_score(y_true: np.ndarray, scores: np.ndarray) -> float:
    thresholds = np.concatenate(([-np.inf], np.unique(scores), [np.inf]))
    best = 0.0
    for threshold in thresholds:
        pred = (scores >= threshold).astype(int)
        best = max(best, float((pred == y_true).mean()))
    return best


def metrics_for(y_true: np.ndarray, scores: np.ndarray) -> dict[str, float | int]:
    fpr, tpr, _ = roc_curve(y_true, scores)

    def tpr_at(max_fpr: float) -> float:
        mask = fpr <= max_fpr
        if not np.any(mask):
            return 0.0
        return float(np.max(tpr[mask]))

    return {
        "n": int(len(y_true)),
        "members": int(np.sum(y_true == 1)),
        "nonmembers": int(np.sum(y_true == 0)),
        "auc": float(roc_auc_score(y_true, scores)),
        "asr": asr_score(y_true, scores),
        "tpr_at_10pct_fpr": tpr_at(0.10),
        "tpr_at_1pct_fpr": tpr_at(0.01),
        "tpr_at_0_1pct_fpr": tpr_at(0.001),
    }


def train_attack_classifier(x_train: pd.DataFrame, y_train: np.ndarray, seed: int) -> Pipeline:
    classifier = HistGradientBoostingClassifier(
        learning_rate=0.04,
        max_iter=220,
        max_leaf_nodes=15,
        l2_regularization=0.01,
        random_state=seed,
    )
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("classifier", classifier),
        ]
    ).fit(x_train, y_train)


def predict_scores(model: Pipeline, features: pd.DataFrame) -> np.ndarray:
    return model.predict_proba(features)[:, 1].astype(float)


def main() -> None:
    args = parse_args()
    phase_features: dict[str, pd.DataFrame] = {}
    phase_labels: dict[str, np.ndarray] = {}
    phase_model_ids: dict[str, list[int]] = {}

    for phase in PHASES:
        features, labels, model_ids = build_phase_features(phase, args)
        phase_features[phase] = features
        phase_labels[phase] = labels
        phase_model_ids[phase] = model_ids

    attack_model = train_attack_classifier(phase_features["train"], phase_labels["train"], args.seed)
    phase_scores = {phase: predict_scores(attack_model, features) for phase, features in phase_features.items()}

    dev_final_labels = np.concatenate((phase_labels["dev"], phase_labels["final"]))
    dev_final_scores = np.concatenate((phase_scores["dev"], phase_scores["final"]))
    all_labels = np.concatenate(tuple(phase_labels[phase] for phase in PHASES))
    all_scores = np.concatenate(tuple(phase_scores[phase] for phase in PHASES))

    metrics = {phase: metrics_for(phase_labels[phase], phase_scores[phase]) for phase in PHASES}
    metrics["dev_final"] = metrics_for(dev_final_labels, dev_final_scores)
    metrics["all"] = metrics_for(all_labels, all_scores)

    dev_final = metrics["dev_final"]
    passes_reopen_gate = bool(
        dev_final["auc"] >= args.reopen_auc_floor and dev_final["tpr_at_1pct_fpr"] >= args.strict_tail_floor
    )
    verdict = "promising_cpu_signal" if passes_reopen_gate else "negative_or_weak"

    payload = {
        "artifact_type": "scout_result",
        "created_at": "2026-05-15",
        "lane": "midst-tabddpm-black-box-single-table",
        "question": (
            "Can a MIA-EPT-style error-prediction profile recover MIDST TabDDPM "
            "membership after nearest-neighbor and marginal-distributional scouts were weak?"
        ),
        "upstream_method": {
            "name": "MIA-EPT",
            "repo": "https://github.com/eyalgerman/MIA-EPT",
            "observed_head": "6890ee833ad90b9fd8b3b3b06abd41613a4b316d",
            "adaptation": (
                "For each target TabDDPM synthetic table, train bounded random-forest "
                "attribute predictors on trans_synthetic.csv, extract per-row actual, "
                "prediction, accuracy/error/error-ratio profiles on challenge rows, "
                "then train one fixed HistGradientBoosting attack classifier on train "
                "shadow labels and evaluate dev/final transfer."
            ),
        },
        "asset": {
            "source": "MIDST SaTML 2025 black-box single-table starter-kit data",
            "local_extract_root": "<DOWNLOAD_ROOT>/shared/midst-data/tabddpm_black_box",
            "label_source": {
                "train": "downloaded challenge_label.csv files",
                "dev_final": "local Codabench bundle challenge_label.csv files from the cloned MIDST repository",
            },
            "model_family": "TabDDPM",
            "task": "black-box membership inference over diffusion-model-based synthetic tabular data",
        },
        "data_contract": {
            "phases": {
                phase: {
                    "models": len(phase_model_ids[phase]),
                    "model_indices": phase_model_ids[phase],
                    "challenge_rows": int(len(phase_labels[phase])),
                    "members": int(np.sum(phase_labels[phase] == 1)),
                    "nonmembers": int(np.sum(phase_labels[phase] == 0)),
                }
                for phase in PHASES
            },
            "synthetic_rows_per_model_used": args.synthetic_sample_size,
            "target_columns": target_columns(
                shared_generated_columns(
                    pd.read_csv(iter_model_dirs(args.data_root, "train", 1)[0] / "challenge_with_id.csv"),
                    pd.read_csv(iter_model_dirs(args.data_root, "train", 1)[0] / "trans_synthetic.csv", nrows=10),
                )
            ),
            "excluded_challenge_only_fields": list(ID_COLUMNS),
            "excluded_target_columns": list(EXCLUDED_TARGET_COLUMNS),
        },
        "scorer": {
            "name": "mia_ept_error_prediction_profile_shadow_attack",
            "direction": "higher_is_more_member",
            "attribute_predictor": {
                "classification_or_regression": f"nunique <= {CLASSIFICATION_UNIQUE_THRESHOLD} uses classification",
                "model": "RandomForestClassifier/RandomForestRegressor",
                "n_estimators": args.n_estimators,
                "max_depth": args.max_depth,
                "min_samples_leaf": args.min_samples_leaf,
                "include_account_feature": args.include_account_feature,
            },
            "attack_classifier": "sklearn HistGradientBoostingClassifier fixed seed 20260515",
            "feature_count": int(phase_features["train"].shape[1]),
            "train_phase": "train only",
            "evaluation_phase": "dev and final labels used only for evaluation",
            "implementation_note": (
                "Single bounded mechanism scout; no classifier sweep, feature sweep, "
                "TabSyn expansion, white-box MIDST expansion, or new long-lived pipeline."
            ),
        },
        "metrics": metrics,
        "verdict": verdict,
        "decision": {
            "admitted_promotion": False,
            "platform_runtime_impact": "none",
            "next_gpu_candidate": "none",
            "passes_reopen_gate": passes_reopen_gate,
            "reopen_gate": {
                "dev_final_auc_floor": args.reopen_auc_floor,
                "dev_final_tpr_at_1pct_fpr_floor": args.strict_tail_floor,
            },
        },
    }
    payload["decision"]["stop_reason"] = (
        "The EPT profile passes the bounded CPU reopen gate and needs a separate "
        "follow-up before any admitted promotion."
        if passes_reopen_gate
        else "The EPT profile does not beat the bounded MIDST reopen gate on dev+final transfer; close without sweeps."
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=False), encoding="utf-8")
    print(f"wrote {args.output}")
    print(json.dumps(metrics["dev_final"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
