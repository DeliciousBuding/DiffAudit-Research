from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.review_graybox_triscore_truth_hardening import review_triscore_truth_hardening


class GrayboxTriscoreTruthHardeningReviewTests(unittest.TestCase):
    def _write_summary(self, path: Path, packets: list[dict]) -> None:
        payload = {
            "claim_boundary": {
                "headline_use_allowed": False,
                "external_evidence_allowed": False,
            },
            "admitted_comparator": {
                "auc": 0.84,
                "asr": 0.78,
                "tpr_at_1pct_fpr": 0.05,
                "tpr_at_0_1pct_fpr": 0.01,
            },
            "packets": packets,
        }
        path.write_text(json.dumps(payload), encoding="utf-8")

    def test_positive_bounded_when_auc_and_tpr1_beat_in_two_packets(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = Path(tmpdir) / "summary.json"
            self._write_summary(
                summary,
                [
                    {"label": "a", "auc": 0.86, "asr": 0.79, "tpr_at_1pct_fpr": 0.13, "tpr_at_0_1pct_fpr": 0.04},
                    {"label": "b", "auc": 0.85, "asr": 0.77, "tpr_at_1pct_fpr": 0.07, "tpr_at_0_1pct_fpr": 0.02},
                    {"label": "c", "auc": 0.83, "asr": 0.78, "tpr_at_1pct_fpr": 0.04, "tpr_at_0_1pct_fpr": 0.0},
                ],
            )
            result = review_triscore_truth_hardening(summary)

        self.assertEqual(result["verdict"], "positive-but-bounded")
        self.assertTrue(result["gates"]["auc_beats_in_at_least_2_of_3"])
        self.assertTrue(result["gates"]["tpr_at_1pct_fpr_beats_in_at_least_2_of_3"])
        self.assertFalse(result["gates"]["gpu_release"])
        self.assertTrue(result["gates"]["internal_only_contract_preserved"])

    def test_negative_when_tpr1_lift_is_not_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = Path(tmpdir) / "summary.json"
            self._write_summary(
                summary,
                [
                    {"label": "a", "auc": 0.86, "asr": 0.79, "tpr_at_1pct_fpr": 0.13, "tpr_at_0_1pct_fpr": 0.04},
                    {"label": "b", "auc": 0.85, "asr": 0.77, "tpr_at_1pct_fpr": 0.03, "tpr_at_0_1pct_fpr": 0.02},
                    {"label": "c", "auc": 0.83, "asr": 0.78, "tpr_at_1pct_fpr": 0.04, "tpr_at_0_1pct_fpr": 0.0},
                ],
            )
            result = review_triscore_truth_hardening(summary)

        self.assertEqual(result["verdict"], "negative-but-useful")
        self.assertFalse(result["gates"]["tpr_at_1pct_fpr_beats_in_at_least_2_of_3"])

    def test_missing_metrics_raise_targeted_value_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = Path(tmpdir) / "summary.json"
            self._write_summary(
                summary,
                [
                    {"label": "a", "auc": 0.86, "asr": 0.79, "tpr_at_1pct_fpr": 0.13},
                    {"label": "b", "auc": 0.85, "asr": 0.77, "tpr_at_1pct_fpr": 0.07, "tpr_at_0_1pct_fpr": 0.02},
                    {"label": "c", "auc": 0.83, "asr": 0.78, "tpr_at_1pct_fpr": 0.04, "tpr_at_0_1pct_fpr": 0.0},
                ],
            )
            with self.assertRaisesRegex(ValueError, "packet 0 missing required metrics"):
                review_triscore_truth_hardening(summary)

    def test_missing_or_open_contract_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = Path(tmpdir) / "summary.json"
            packets = [
                {"label": "a", "auc": 0.86, "asr": 0.79, "tpr_at_1pct_fpr": 0.13, "tpr_at_0_1pct_fpr": 0.04},
                {"label": "b", "auc": 0.85, "asr": 0.77, "tpr_at_1pct_fpr": 0.07, "tpr_at_0_1pct_fpr": 0.02},
                {"label": "c", "auc": 0.83, "asr": 0.78, "tpr_at_1pct_fpr": 0.04, "tpr_at_0_1pct_fpr": 0.0},
            ]
            self._write_summary(summary, packets)
            payload = json.loads(summary.read_text(encoding="utf-8"))
            payload["claim_boundary"]["external_evidence_allowed"] = True
            summary.write_text(json.dumps(payload), encoding="utf-8")

            result = review_triscore_truth_hardening(summary)

        self.assertEqual(result["verdict"], "negative-but-useful")
        self.assertFalse(result["gates"]["internal_only_contract_preserved"])

    def test_cli_writes_review_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            summary = root / "summary.json"
            output = root / "review.json"
            self._write_summary(
                summary,
                [
                    {"label": "a", "auc": 0.86, "asr": 0.79, "tpr_at_1pct_fpr": 0.13, "tpr_at_0_1pct_fpr": 0.04},
                    {"label": "b", "auc": 0.85, "asr": 0.77, "tpr_at_1pct_fpr": 0.07, "tpr_at_0_1pct_fpr": 0.02},
                    {"label": "c", "auc": 0.83, "asr": 0.78, "tpr_at_1pct_fpr": 0.04, "tpr_at_0_1pct_fpr": 0.0},
                ],
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/review_graybox_triscore_truth_hardening.py",
                    "--summary",
                    str(summary),
                    "--output",
                    str(output),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=Path(__file__).resolve().parents[1],
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(output.read_text())["verdict"], "positive-but-bounded")


if __name__ == "__main__":
    unittest.main()
