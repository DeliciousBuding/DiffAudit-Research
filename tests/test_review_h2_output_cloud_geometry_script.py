from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


def _load_script_module():
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "review_h2_output_cloud_geometry.py"
    spec = importlib.util.spec_from_file_location("review_h2_output_cloud_geometry", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load review_h2_output_cloud_geometry.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReviewH2OutputCloudGeometryScriptTests(unittest.TestCase):
    def test_compute_features_uses_all_repeat_pairs(self) -> None:
        module = _load_script_module()
        responses = np.asarray(
            [
                [
                    [[[0.0]], [[2.0]], [[4.0]]],
                    [[[1.0]], [[1.0]], [[1.0]]],
                ],
                [
                    [[[1.0]], [[3.0]], [[9.0]]],
                    [[[4.0]], [[8.0]], [[12.0]]],
                ],
            ],
            dtype=np.float32,
        )
        responses = responses.reshape(2, 2, 3, 1, 1, 1)

        features, names = module.compute_output_cloud_features(responses, np.asarray([10, 20]))

        self.assertEqual(features.shape, (2, 10))
        self.assertEqual(names[0], "within_timestep_pair_rmse_10")
        self.assertEqual(names[1], "within_timestep_pair_rmse_20")
        self.assertEqual(names[-2:], ["cloud_pca_trace", "cloud_pca_top_share"])
        np.testing.assert_allclose(features[:, 0], np.asarray([8.0 / 3.0, 16.0 / 3.0]), rtol=1e-6)
        np.testing.assert_allclose(features[:, 1], np.asarray([0.0, 16.0 / 3.0]), rtol=1e-6)

    def test_compute_features_rejects_single_repeat_cache(self) -> None:
        module = _load_script_module()
        responses = np.zeros((2, 2, 1, 1, 1, 1), dtype=np.float32)

        with self.assertRaisesRegex(ValueError, "at least two repeats"):
            module.compute_output_cloud_features(responses, np.asarray([10, 20]))

    def test_shuffle_label_mode_writes_sanity_payload(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            cache = tmp / "response-cache.npz"
            summary = tmp / "summary.json"
            output = tmp / "shuffle-review.json"
            labels = np.asarray([1] * 8 + [0] * 8, dtype=np.int64)
            responses = np.zeros((16, 2, 2, 1, 1, 1), dtype=np.float32)
            responses[:, 0, 0, 0, 0, 0] = np.linspace(0.0, 1.5, 16)
            responses[:, 0, 1, 0, 0, 0] = np.linspace(0.2, 1.7, 16)
            responses[:, 1, 0, 0, 0, 0] = np.linspace(0.4, 1.9, 16)
            responses[:, 1, 1, 0, 0, 0] = np.linspace(0.7, 2.2, 16)
            np.savez_compressed(cache, labels=labels, timesteps=np.asarray([40, 80]), responses=responses)
            summary.write_text(
                json.dumps({"raw_h2": {"logistic": {"aggregate_metrics": {"auc": 0.9}}}}),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "-X",
                    "utf8",
                    "scripts/review_h2_output_cloud_geometry.py",
                    "--response-cache",
                    str(cache),
                    "--output",
                    str(output),
                    "--seed",
                    "176",
                    "--holdout-repeats",
                    "2",
                    "--bootstrap-iters",
                    "0",
                    "--shuffle-labels",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=repo_root,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["inputs"]["label_mode"], "shuffled_seed_176")
            self.assertEqual(payload["verdict"], "label_shuffle_sanity_random_level")
            self.assertIsNone(payload["comparison"]["raw_h2_logistic"])
            self.assertIsNone(payload["comparison"]["output_cloud_minus_raw_h2"])


if __name__ == "__main__":
    unittest.main()
