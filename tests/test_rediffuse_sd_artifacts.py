import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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


def _write_rediffuse_sd_bundle(root: Path) -> Path:
    bundle_root = root / "collaborator-stable-diffusion-rediffuse"
    source_root = bundle_root / "SD_MIA_Reproduction"
    source_root.mkdir(parents=True, exist_ok=True)

    for name in (
        "attack.py",
        "components.py",
        "dataset.py",
        "score_single_image.py",
        "select_rediffuse_detector.py",
        "validate_rediffuse_detector.py",
        "coco-2500-random.yaml",
    ):
        (source_root / name).write_text(f"# {name}\n", encoding="utf-8")

    artifact_dir = _write_rediffuse_sd_artifact_dir(bundle_root / "runs")
    artifact_target = bundle_root / "runs" / "final_rediffuse_combined"
    artifact_target.parent.mkdir(parents=True, exist_ok=True)
    if artifact_dir != artifact_target:
        artifact_dir.rename(artifact_target)
    artifact_dir = artifact_target

    detector_dir = bundle_root / "论文复现攻击材料_20260516"
    detector_dir.mkdir(parents=True, exist_ok=True)
    detector_payload = {
        "dataset": "laion5_blip",
        "attacker_name": "ReDiffuse",
        "checkpoint": "CompVis/stable-diffusion-v1-4",
        "attack_num": 5,
        "interval": 10,
        "k": 10,
        "average": 3,
        "torch_dtype": "auto",
        "feature_mode": "logistic_l2",
        "rediffuse_scorer": "vae_ssim",
        "auc": 0.71031888,
        "asr": 0.6846,
        "tpr_1fpr": 0.0716,
        "threshold": -0.123456,
        "decision_rule": "member_if_score_leq_threshold",
        "selection_source": str(detector_dir / "merged_rediffuse_scores_a2_a5_combined.npz"),
        "logistic": {
            "coef": [0.1, -0.2, 0.3, -0.4, 0.5, -0.6, 0.7],
            "intercept": 0.8,
            "scaler_mean": [0.0] * 7,
            "scaler_scale": [1.0] * 7,
        },
    }
    (detector_dir / "mia_detector_rediffuse_sweep_best_a2_a5_combined.json").write_text(
        json.dumps(detector_payload, indent=2),
        encoding="utf-8",
    )
    np.savez(
        detector_dir / "merged_rediffuse_scores_a2_a5_combined.npz",
        member_features=np.ones((4, 7), dtype=np.float32),
        nonmember_features=np.zeros((4, 7), dtype=np.float32),
        dataset=np.asarray("laion5_blip"),
        checkpoint=np.asarray("CompVis/stable-diffusion-v1-4"),
        attack_num=np.asarray(5),
        interval=np.asarray(10),
        k=np.asarray(10),
        average=np.asarray(3),
        torch_dtype=np.asarray("auto"),
        rediffuse_scorer=np.asarray("vae_ssim"),
    )
    (artifact_dir / "rediffuse_holdout_validation_a2_a5_combined.json").write_text(
        json.dumps(
            {
                "holdout": {"test_auc": 0.7046},
                "cross_validation": {"mean_test_auc": 0.7080, "std_test_auc": 0.0116},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return bundle_root


def _write_rediffuse_sd_parent_bundle(root: Path) -> Path:
    bundle_root = _write_rediffuse_sd_bundle(root)
    parent_root = root / "collaborator-stable-diffusion-rediffuse-parent"
    parent_root.mkdir(parents=True, exist_ok=True)
    bundle_root.rename(parent_root / "raw")
    return parent_root


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

    def test_probe_rediffuse_sd_assets_reports_ready(self) -> None:
        from diffaudit.attacks.rediffuse_sd import probe_rediffuse_sd_assets

        with tempfile.TemporaryDirectory() as tmpdir:
            bundle_root = _write_rediffuse_sd_bundle(Path(tmpdir))
            payload = probe_rediffuse_sd_assets(bundle_root)

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["method"], "rediffuse_sd")
        self.assertTrue(payload["checks"]["source_root"])
        self.assertTrue(payload["checks"]["required_source_files"])
        self.assertTrue(payload["checks"]["detector_json"])
        self.assertTrue(payload["checks"]["score_npz"])
        self.assertTrue(payload["checks"]["artifact_probe_ready"])
        self.assertEqual(payload["detector"]["feature_mode"], "logistic_l2")
        self.assertEqual(payload["score_npz"]["member_shape"], [4, 7])

    def test_probe_rediffuse_sd_assets_accepts_parent_with_raw_child(self) -> None:
        from diffaudit.attacks.rediffuse_sd import probe_rediffuse_sd_assets

        with tempfile.TemporaryDirectory() as tmpdir:
            parent_root = _write_rediffuse_sd_parent_bundle(Path(tmpdir))
            payload = probe_rediffuse_sd_assets(parent_root)

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["paths"]["bundle_root"], str(parent_root / "raw"))
        self.assertTrue(payload["checks"]["source_root"])
        self.assertTrue(payload["checks"]["artifact_probe_ready"])

    def test_cli_probe_rediffuse_sd_assets_reports_ready(self) -> None:
        from diffaudit.cli import main

        with tempfile.TemporaryDirectory() as tmpdir:
            bundle_root = _write_rediffuse_sd_bundle(Path(tmpdir))
            exit_code, payload = capture_cli_json(
                main,
                ["probe-rediffuse-sd-assets", "--bundle-root", str(bundle_root)],
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["paths"]["bundle_root"], str(bundle_root))

    def test_score_rediffuse_sd_image_wraps_collaborator_script(self) -> None:
        from diffaudit.cli import main

        with tempfile.TemporaryDirectory() as tmpdir:
            bundle_root = _write_rediffuse_sd_bundle(Path(tmpdir))
            image_path = Path(tmpdir) / "sample.png"
            image_path.write_bytes(b"fake-image")

            completed = type(
                "CompletedProcess",
                (),
                {
                    "returncode": 0,
                    "stdout": json.dumps({"prediction": 1, "score": 0.91}),
                    "stderr": "",
                },
            )()

            with patch("diffaudit.attacks.rediffuse_sd.subprocess.run", return_value=completed) as run_mock:
                exit_code, payload = capture_cli_json(
                    main,
                    [
                        "score-rediffuse-sd-image",
                        "--bundle-root",
                        str(bundle_root),
                        "--image",
                        str(image_path),
                        "--prompt",
                        "a flower crown portrait",
                    ],
                )

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["score"]["prediction"], 1)
        command = run_mock.call_args.kwargs["args"]
        self.assertIn("score_single_image.py", command[1])
        self.assertEqual(command[3], str(image_path))


if __name__ == "__main__":
    unittest.main()
