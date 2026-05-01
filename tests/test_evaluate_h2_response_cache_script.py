import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


class EvaluateH2ResponseCacheScriptTests(unittest.TestCase):
    def test_script_writes_summary_from_npz_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache_path = root / "response-cache.npz"
            output_path = root / "summary.json"
            labels = np.asarray([1] * 6 + [0] * 6, dtype=np.int64)
            timesteps = np.asarray([40, 80], dtype=np.int64)
            member_distances = np.stack(
                [np.linspace(0.1, 0.2, 6), np.linspace(0.2, 0.3, 6)],
                axis=1,
            )
            nonmember_distances = np.stack(
                [np.linspace(0.8, 0.9, 6), np.linspace(0.9, 1.0, 6)],
                axis=1,
            )
            np.savez_compressed(
                cache_path,
                labels=labels,
                timesteps=timesteps,
                min_distances_rmse=np.concatenate([member_distances, nonmember_distances], axis=0).astype(np.float32),
            )

            subprocess.run(
                [
                    sys.executable,
                    "-X",
                    "utf8",
                    "scripts/evaluate_h2_response_cache.py",
                    "--response-cache",
                    str(cache_path),
                    "--output",
                    str(output_path),
                    "--bootstrap-iters",
                    "0",
                    "--no-lowpass",
                ],
                check=True,
                cwd=Path(__file__).resolve().parents[1],
                stdout=subprocess.DEVNULL,
            )

            summary = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "ready")
            self.assertEqual(summary["inputs"]["sample_count"], 12)
            self.assertIn("logistic", summary["raw_h2"])


if __name__ == "__main__":
    unittest.main()

