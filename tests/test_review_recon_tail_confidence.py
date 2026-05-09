from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


class ReviewReconTailConfidenceTests(unittest.TestCase):
    def test_wilson_interval_bounds_zero_false_positive_tail(self) -> None:
        from scripts.review_recon_tail_confidence import wilson_interval

        interval = wilson_interval(0, 100)

        self.assertEqual(interval["estimate"], 0.0)
        self.assertEqual(interval["lower_95"], 0.0)
        self.assertGreater(interval["upper_95"], 0.03)

    def test_project_card_is_admitted_finite_tail_only(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/review_recon_tail_confidence.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=Path(__file__).resolve().parents[1],
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        strict_gate = payload["gates"]["tpr_at_0_1pct_fpr"]

        self.assertEqual(payload["verdict"], "admitted-finite-tail-only")
        self.assertEqual(strict_gate["true_positives"], 11)
        self.assertEqual(strict_gate["false_positives"], 0)
        self.assertFalse(strict_gate["calibrated_to_target_fpr"])
        self.assertEqual(payload["next_gpu_candidate"].split(";")[0], "none selected")


if __name__ == "__main__":
    unittest.main()
