import csv
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from diffaudit.utils.metrics import metric_bundle, roc_curve_points
from tests.helpers import capture_cli_json


def _write_rediffuse_sd_artifact_dir(root: Path) -> Path:
    artifact_dir = root / "stable-diffusion-rediffuse-artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    rows = [
        {
            "image_path": "member-000.png",
            "label": 1,
            "label_name": "member",
            "score": 0.91,
        },
        {
            "image_path": "member-001.png",
            "label": 1,
            "label_name": "member",
            "score": 0.74,
        },
        {
            "image_path": "member-002.png",
            "label": 1,
            "label_name": "member",
            "score": 0.67,
        },
        {
            "image_path": "member-003.png",
            "label": 1,
            "label_name": "member",
            "score": 0.58,
        },
        {
            "image_path": "nonmember-000.png",
            "label": 0,
            "label_name": "nonmember",
            "score": 0.42,
        },
        {
            "image_path": "nonmember-001.png",
            "label": 0,
            "label_name": "nonmember",
            "score": 0.28,
        },
        {
            "image_path": "nonmember-002.png",
            "label": 0,
            "label_name": "nonmember",
            "score": 0.14,
        },
        {
            "image_path": "nonmember-003.png",
            "label": 0,
            "label_name": "nonmember",
            "score": 0.09,
        },
    ]
    labels = np.asarray([int(row["label"]) for row in rows], dtype=np.int64)
    scores = np.asarray([float(row["score"]) for row in rows], dtype=np.float64)
    metrics = metric_bundle(scores, labels)
    threshold = 0.5

    for row in rows:
        prediction = int(float(row["score"]) >= threshold)
        row["prediction"] = prediction
        row["prediction_name"] = "member" if prediction == 1 else "nonmember"
        row["correct"] = int(prediction == int(row["label"]))

    result_path = artifact_dir / "result.csv"
    with result_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "image_path",
                "label",
                "label_name",
                "score",
                "prediction",
                "prediction_name",
                "correct",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    fpr, tpr = roc_curve_points(scores, labels)
    roc_path = artifact_dir / "roc_curve.csv"
    with roc_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["fpr", "tpr"])
        writer.writeheader()
        for fpr_value, tpr_value in zip(fpr.tolist(), tpr.tolist(), strict=True):
            writer.writerow({"fpr": fpr_value, "tpr": tpr_value})

    reported_payload = {
        "auc": float(metrics["auc"]),
        "asr": float(metrics["asr"]),
        "tpr_at_fpr_1pct": float(metrics["tpr_at_1pct_fpr"]),
        "threshold_confidence": threshold,
        "threshold_low_score": -threshold,
        "dataset": "laion5_blip",
        "attacker_name": "ReDiffuse",
        "checkpoint": "CompVis/stable-diffusion-v1-4",
        "feature_mode": "logistic_l2_C3",
        "rediffuse_scorer": "combined",
        "num_member": int(labels.sum()),
        "num_nonmember": int((labels == 0).sum()),
        "result_csv": r"E:\stable_diffusion\coco_data_like_submit_20260516\artifacts\result.csv",
        "roc_curve_csv": r"E:\stable_diffusion\coco_data_like_submit_20260516\artifacts\roc_curve.csv",
        "roc_curve_plot": r"E:\stable_diffusion\coco_data_like_submit_20260516\artifacts\roc_curve.png",
        "score_direction": "higher score means more likely member",
        "prediction_rule": "member_if_score_geq_threshold",
    }
    (artifact_dir / "metrics.json").write_text(
        json.dumps(reported_payload, indent=2),
        encoding="utf-8",
    )
    (artifact_dir / "metrics.csv").write_text(
        "metric,value\nauc,{auc}\nasr,{asr}\n".format(
            auc=reported_payload["auc"],
            asr=reported_payload["asr"],
        ),
        encoding="utf-8",
    )
    (artifact_dir / "roc_curve.png").write_bytes(b"fake-png")
    return artifact_dir


class StableDiffusionReDiffuseArtifactTests(unittest.TestCase):
    def test_probe_rediffuse_sd_artifacts_reports_ready(self) -> None:
        from diffaudit.attacks.rediffuse_sd import probe_rediffuse_sd_artifacts

        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = _write_rediffuse_sd_artifact_dir(Path(tmpdir))
            payload = probe_rediffuse_sd_artifacts(artifact_dir)

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["track"], "black-box")
        self.assertEqual(payload["method"], "rediffuse_sd")
        self.assertTrue(payload["checks"]["metrics_json"])
        self.assertTrue(payload["checks"]["result_csv"])
        self.assertTrue(payload["checks"]["roc_curve_csv"])
        self.assertTrue(payload["checks"]["required_result_columns"])
        self.assertTrue(payload["consistency"]["reported_auc_matches_recomputed"])
        self.assertTrue(payload["consistency"]["reported_asr_matches_recomputed"])
        self.assertTrue(payload["consistency"]["reported_split_counts_match_result"])
        self.assertEqual(payload["counts"]["member_rows"], 4)
        self.assertEqual(payload["counts"]["nonmember_rows"], 4)
        self.assertEqual(payload["reported"]["checkpoint"], "CompVis/stable-diffusion-v1-4")
        self.assertFalse(payload["boundary"]["external_api_only"])

    def test_probe_rediffuse_sd_artifacts_blocks_missing_metrics(self) -> None:
        from diffaudit.attacks.rediffuse_sd import probe_rediffuse_sd_artifacts

        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = _write_rediffuse_sd_artifact_dir(Path(tmpdir))
            (artifact_dir / "metrics.json").unlink()
            payload = probe_rediffuse_sd_artifacts(artifact_dir)

        self.assertEqual(payload["status"], "blocked")
        self.assertFalse(payload["checks"]["metrics_json"])
        self.assertIn("metrics.json", payload["missing_items"])

    def test_cli_probe_rediffuse_sd_artifacts_reports_ready(self) -> None:
        from diffaudit.cli import main

        with tempfile.TemporaryDirectory() as tmpdir:
            artifact_dir = _write_rediffuse_sd_artifact_dir(Path(tmpdir))
            exit_code, payload = capture_cli_json(
                main,
                ["probe-rediffuse-sd-artifacts", "--artifact-dir", str(artifact_dir)],
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["reported"]["dataset"], "laion5_blip")


if __name__ == "__main__":
    unittest.main()
