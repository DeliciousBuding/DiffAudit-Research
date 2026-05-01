import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


class ReviewH2Img2ImgSimpleDistanceScriptTests(unittest.TestCase):
    def test_reviews_strength_axis_and_finite_tail(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cache = tmp / "response-cache.npz"
            summary = tmp / "summary.json"
            output = tmp / "simple-review.json"
            np.savez_compressed(
                cache,
                labels=np.asarray([1, 1, 1, 0, 0, 0], dtype=np.int64),
                strengths=np.asarray([0.35, 0.75], dtype=np.float32),
                min_distances_rmse=np.asarray(
                    [
                        [0.40, 0.10],
                        [0.42, 0.11],
                        [0.50, 0.12],
                        [0.39, 0.30],
                        [0.46, 0.31],
                        [0.47, 0.32],
                    ],
                    dtype=np.float32,
                ),
            )
            summary.write_text(
                json.dumps(
                    {
                        "raw_h2": {"logistic": {"aggregate_metrics": {"auc": 0.5}}},
                        "lowpass_h2": {"logistic": {"aggregate_metrics": {"auc": 0.6}}},
                    }
                ),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    "-X",
                    "utf8",
                    "scripts/review_h2_img2img_simple_distance.py",
                    "--response-cache",
                    str(cache),
                    "--evaluation-summary",
                    str(summary),
                    "--output",
                    str(output),
                    "--bootstrap-iters",
                    "5",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["inputs"]["sample_count"], 6)
        self.assertEqual(payload["best_simple_distance"]["strength"], 0.75)
        self.assertEqual(payload["best_simple_distance"]["metrics"]["zero_fp_tp_count"], 3)
        self.assertFalse(payload["finite_sample_boundary"]["calibrated_subpercent_fpr"])
        self.assertIn("candidate simple-distance signal", payload["verdict"])

    def test_requires_strength_axis(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cache = tmp / "response-cache.npz"
            np.savez_compressed(
                cache,
                labels=np.asarray([1, 0], dtype=np.int64),
                timesteps=np.asarray([40], dtype=np.int64),
                min_distances_rmse=np.asarray([[0.1], [0.2]], dtype=np.float32),
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-X",
                    "utf8",
                    "scripts/review_h2_img2img_simple_distance.py",
                    "--response-cache",
                    str(cache),
                    "--output",
                    str(tmp / "out.json"),
                ],
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("strengths", result.stderr)

    def test_rejects_empty_strength_axis(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cache = tmp / "response-cache.npz"
            np.savez_compressed(
                cache,
                labels=np.asarray([1, 0], dtype=np.int64),
                strengths=np.asarray([], dtype=np.float32),
                min_distances_rmse=np.empty((2, 0), dtype=np.float32),
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-X",
                    "utf8",
                    "scripts/review_h2_img2img_simple_distance.py",
                    "--response-cache",
                    str(cache),
                    "--output",
                    str(tmp / "out.json"),
                ],
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("strengths array is empty", result.stderr)


if __name__ == "__main__":
    unittest.main()
