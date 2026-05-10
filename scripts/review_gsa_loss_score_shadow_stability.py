"""Review leave-one-shadow-out stability for GSA loss-score scorers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from diffaudit.utils.gaussian import fit_univariate_gaussian, gaussian_log_likelihood_ratio
from diffaudit.utils.io import torch_load_safe, write_summary_json
from diffaudit.utils.metrics import auc_score, roc_curve_points, round6, tpr_at_fpr_from_curve


def _resolve_repo_path(path: str, *, repo_root: Path) -> Path:
    return Path(path.replace("<DIFFAUDIT_RESEARCH>", str(repo_root))).resolve()


def _load_scores(path: str, *, repo_root: Path) -> np.ndarray:
    tensor = torch_load_safe(_resolve_repo_path(path, repo_root=repo_root), map_location="cpu")
    return np.asarray(tensor.reshape(-1).tolist(), dtype=float)


def _best_threshold(scores: np.ndarray, labels: np.ndarray) -> float:
    from sklearn.metrics import roc_curve

    fpr, tpr, thresholds = roc_curve(labels, scores)
    valid = np.flatnonzero(np.isfinite(thresholds))
    if valid.size == 0:
        valid = np.arange(thresholds.shape[0])
    return float(thresholds[int(valid[np.argmax((tpr - fpr)[valid])])])


def _metrics(member_scores: np.ndarray, nonmember_scores: np.ndarray, *, threshold: float | None = None) -> dict[str, Any]:
    labels = np.concatenate(
        [
            np.ones(member_scores.size, dtype=np.int64),
            np.zeros(nonmember_scores.size, dtype=np.int64),
        ]
    )
    scores = np.concatenate([member_scores, nonmember_scores])
    fpr, tpr = roc_curve_points(scores, labels)
    applied_threshold = _best_threshold(scores, labels) if threshold is None else float(threshold)
    predictions = (scores >= applied_threshold).astype(np.int64)
    return {
        "auc": round6(auc_score(scores, labels)),
        "asr": round6(float(np.mean(predictions == labels))),
        "tpr_at_1pct_fpr": round6(tpr_at_fpr_from_curve(fpr, tpr, 0.01)),
        "tpr_at_0_1pct_fpr": round6(tpr_at_fpr_from_curve(fpr, tpr, 0.001)),
        "member_mean_score": round6(float(member_scores.mean())),
        "nonmember_mean_score": round6(float(nonmember_scores.mean())),
        "member_eval_size": int(member_scores.size),
        "nonmember_eval_size": int(nonmember_scores.size),
        "applied_threshold": applied_threshold,
    }


def _macro_average(rows: list[dict[str, Any]]) -> dict[str, float]:
    keys = ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")
    return {key: round6(float(np.mean([float(row[key]) for row in rows]))) for key in keys}


def _orient_raw_scores(
    train_member: np.ndarray,
    train_nonmember: np.ndarray,
    eval_member: np.ndarray,
    eval_nonmember: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, str]:
    if float(train_member.mean()) < float(train_nonmember.mean()):
        return -train_member, -train_nonmember, -eval_member, -eval_nonmember, "member-lower"
    return train_member, train_nonmember, eval_member, eval_nonmember, "member-higher"


def review_shadow_stability(packet_summary: Path, output: Path, *, repo_root: Path) -> dict[str, Any]:
    payload = json.loads(packet_summary.read_text(encoding="utf-8"))
    if payload.get("mode") != "loss-score-export":
        raise ValueError("packet summary must have mode=loss-score-export")

    exports = payload["exports"]
    shadow_specs = payload.get("artifact_paths", {}).get("shadow_specs", [])
    if len(shadow_specs) < 3:
        raise ValueError("leave-one-shadow-out review requires at least 3 shadow groups")

    groups: list[dict[str, Any]] = []
    for spec in shadow_specs:
        prefix = spec["name"].replace("-", "_")
        groups.append(
            {
                "name": spec["name"],
                "member": _load_scores(exports[f"{prefix}_member"]["output_path"], repo_root=repo_root),
                "nonmember": _load_scores(exports[f"{prefix}_non_member"]["output_path"], repo_root=repo_root),
            }
        )

    target_member = _load_scores(exports["target_member"]["output_path"], repo_root=repo_root)
    target_nonmember = _load_scores(exports["target_non_member"]["output_path"], repo_root=repo_root)

    folds: list[dict[str, Any]] = []
    for heldout_index, heldout in enumerate(groups):
        train_groups = [group for index, group in enumerate(groups) if index != heldout_index]
        train_member_raw = np.concatenate([group["member"] for group in train_groups])
        train_nonmember_raw = np.concatenate([group["nonmember"] for group in train_groups])

        train_member, train_nonmember, heldout_member, heldout_nonmember, direction = _orient_raw_scores(
            train_member_raw,
            train_nonmember_raw,
            heldout["member"],
            heldout["nonmember"],
        )
        _tm, _tn, target_member_oriented, target_nonmember_oriented, _ = _orient_raw_scores(
            train_member_raw,
            train_nonmember_raw,
            target_member,
            target_nonmember,
        )
        threshold = _best_threshold(
            np.concatenate([train_member, train_nonmember]),
            np.concatenate([np.ones(train_member.size, dtype=np.int64), np.zeros(train_nonmember.size, dtype=np.int64)]),
        )

        member_fit = fit_univariate_gaussian(train_member_raw, min_variance=1e-6)
        nonmember_fit = fit_univariate_gaussian(train_nonmember_raw, min_variance=1e-6)
        train_member_lr = gaussian_log_likelihood_ratio(
            train_member_raw,
            member_params=member_fit,
            nonmember_params=nonmember_fit,
        )
        train_nonmember_lr = gaussian_log_likelihood_ratio(
            train_nonmember_raw,
            member_params=member_fit,
            nonmember_params=nonmember_fit,
        )
        lr_threshold = _best_threshold(
            np.concatenate([train_member_lr, train_nonmember_lr]),
            np.concatenate(
                [np.ones(train_member_lr.size, dtype=np.int64), np.zeros(train_nonmember_lr.size, dtype=np.int64)]
            ),
        )

        heldout_member_lr = gaussian_log_likelihood_ratio(
            heldout["member"],
            member_params=member_fit,
            nonmember_params=nonmember_fit,
        )
        heldout_nonmember_lr = gaussian_log_likelihood_ratio(
            heldout["nonmember"],
            member_params=member_fit,
            nonmember_params=nonmember_fit,
        )
        target_member_lr = gaussian_log_likelihood_ratio(
            target_member,
            member_params=member_fit,
            nonmember_params=nonmember_fit,
        )
        target_nonmember_lr = gaussian_log_likelihood_ratio(
            target_nonmember,
            member_params=member_fit,
            nonmember_params=nonmember_fit,
        )

        folds.append(
            {
                "heldout_shadow_name": heldout["name"],
                "train_shadows": [group["name"] for group in train_groups],
                "threshold_direction": direction,
                "heldout_shadow": {
                    "threshold_transfer": _metrics(heldout_member, heldout_nonmember, threshold=threshold),
                    "gaussian_lr_transfer": _metrics(heldout_member_lr, heldout_nonmember_lr, threshold=lr_threshold),
                },
                "target_transfer": {
                    "threshold_transfer": _metrics(
                        target_member_oriented,
                        target_nonmember_oriented,
                        threshold=threshold,
                    ),
                    "gaussian_lr_transfer": _metrics(target_member_lr, target_nonmember_lr, threshold=lr_threshold),
                },
            }
        )

    heldout_threshold = [fold["heldout_shadow"]["threshold_transfer"] for fold in folds]
    heldout_lr = [fold["heldout_shadow"]["gaussian_lr_transfer"] for fold in folds]
    target_threshold = [fold["target_transfer"]["threshold_transfer"] for fold in folds]
    target_lr = [fold["target_transfer"]["gaussian_lr_transfer"] for fold in folds]
    heldout_lr_beats_threshold = sum(
        int(lr["auc"] > threshold["auc"] and lr["tpr_at_1pct_fpr"] >= threshold["tpr_at_1pct_fpr"])
        for lr, threshold in zip(heldout_lr, heldout_threshold)
    )
    target_lr_beats_threshold = sum(
        int(lr["auc"] > threshold["auc"] and lr["tpr_at_1pct_fpr"] >= threshold["tpr_at_1pct_fpr"])
        for lr, threshold in zip(target_lr, target_threshold)
    )
    release_gate = {
        "heldout_lr_beats_threshold_folds": heldout_lr_beats_threshold,
        "target_lr_beats_threshold_folds": target_lr_beats_threshold,
        "required_folds": 2,
        "passed": heldout_lr_beats_threshold >= 2 and target_lr_beats_threshold >= 2,
    }
    verdict = "cpu-preflight-positive" if release_gate["passed"] else "negative-but-useful"
    result = {
        "status": "ready",
        "track": "white-box",
        "method": "gsa-loss-score-shadow-stability",
        "mode": "leave-one-shadow-out-review",
        "packet_summary": str(packet_summary),
        "output": str(output),
        "verdict": verdict,
        "hypothesis": "Gaussian LR transfer is a stable distinct scorer over existing GSA loss-score exports.",
        "falsifier": "LR fails to beat threshold transfer in at least 2/3 held-out shadow and target folds.",
        "release_gate": release_gate,
        "macro": {
            "heldout_shadow": {
                "threshold_transfer": _macro_average(heldout_threshold),
                "gaussian_lr_transfer": _macro_average(heldout_lr),
            },
            "target_transfer": {
                "threshold_transfer": _macro_average(target_threshold),
                "gaussian_lr_transfer": _macro_average(target_lr),
            },
        },
        "folds": folds,
        "notes": [
            "CPU-only review over existing loss-score exports; no GPU task is released.",
            "Held-out shadow folds test whether the scorer generalizes across shadow checkpoints.",
            "Target-transfer rows reuse each fold's shadow-only orientation, density fit, and threshold.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    write_summary_json(output, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--packet-summary",
        default="workspaces/white-box/runs/gsa-loss-score-export-bounded-bm0-gpu-20260417-r1/summary.json",
    )
    parser.add_argument(
        "--output",
        default="workspaces/white-box/runs/gsa-loss-score-shadow-stability-20260510-cpu/summary.json",
    )
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    result = review_shadow_stability(Path(args.packet_summary), Path(args.output), repo_root=repo_root)
    print(json.dumps({"status": result["status"], "verdict": result["verdict"], "output": result["output"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
