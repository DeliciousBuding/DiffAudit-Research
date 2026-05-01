from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class ReviewSemanticAuxLowFprTests(unittest.TestCase):
    def test_project_review_is_negative_but_useful(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/review_semantic_aux_low_fpr.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=Path(__file__).resolve().parents[1],
        )

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["verdict"], "negative but useful")
        self.assertEqual(payload["source_mode"], "committed-summary")
        self.assertFalse(payload["gate"]["clears_auc_gain_gate"])
        self.assertEqual(payload["best_auc_gain_vs_mean_cos"], 0.001953)

    def test_review_rejects_gpu_followup_when_gain_is_too_small(self) -> None:
        records = []
        for label, base in ((1, 0.8), (1, 0.79), (0, 0.2), (0, 0.19)):
            records.append(
                {
                    "label": label,
                    "mean_cos": base,
                    "max_cos": base + 0.001,
                    "max_ssim": base - 0.001,
                }
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            records_path = Path(tmpdir) / "records.json"
            records_path.write_text(json.dumps(records), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/review_semantic_aux_low_fpr.py",
                    "--records",
                    str(records_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=Path(__file__).resolve().parents[1],
            )

        self.assertEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["verdict"], "negative but useful")
        self.assertEqual(payload["source_mode"], "raw-records")
        self.assertFalse(payload["gate"]["clears_auc_gain_gate"])


if __name__ == "__main__":
    unittest.main()
