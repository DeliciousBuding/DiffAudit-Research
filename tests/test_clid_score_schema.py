import json
import tempfile
import unittest
from pathlib import Path


class ClidScoreSchemaTests(unittest.TestCase):
    def _write_summary(
        self,
        root: Path,
        *,
        member_rows: int = 128,
        nonmember_rows: int = 128,
        tpr_at_0_1pct_fpr: float = 0.015625,
        passed: bool = True,
    ) -> Path:
        summary = {
            "status": "ready",
            "track": "black-box",
            "method": "clid",
            "mode": "score-summary",
            "split_identity": {
                "member_rows": member_rows,
                "nonmember_rows": nonmember_rows,
                "alignment": "metadata_row_order",
                "held_out_target_split": True,
            },
            "score_outputs": {
                "scorer_family": "clid_clip",
                "raw_score_matrices": "artifacts/raw-score-matrices/",
                "threshold_summary": "summary.json",
            },
            "metrics": {
                "auc": 0.625,
                "asr": 0.59375,
                "tpr_at_1pct_fpr": 0.0625,
                "tpr_at_0_1pct_fpr": tpr_at_0_1pct_fpr,
            },
            "low_fpr_gate": {
                "minimum_samples_per_split": 100,
                "strict_tail_metric": "tpr_at_0_1pct_fpr",
                "promotion_requires": "nonzero_strict_tail_on_held_out_target",
                "passed": passed,
            },
        }
        path = root / "summary.json"
        path.write_text(json.dumps(summary), encoding="utf-8")
        return path

    def test_valid_schema_with_strict_tail_is_promotion_eligible(self) -> None:
        from diffaudit.attacks.clid_score_schema import validate_clid_score_summary

        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = self._write_summary(Path(tmpdir))
            payload = validate_clid_score_summary(summary_path)

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["promotion_status"], "eligible")
        self.assertEqual(payload["promotion_missing"], [])

    def test_valid_schema_without_strict_tail_is_not_promotion_eligible(self) -> None:
        from diffaudit.attacks.clid_score_schema import validate_clid_score_summary

        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = self._write_summary(
                Path(tmpdir),
                tpr_at_0_1pct_fpr=0.0,
                passed=False,
            )
            payload = validate_clid_score_summary(summary_path)

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["promotion_status"], "not_eligible")
        self.assertIn("strict_tail_nonzero", payload["promotion_missing"])

    def test_absolute_artifact_reference_blocks_schema(self) -> None:
        from diffaudit.attacks.clid_score_schema import validate_clid_score_summary

        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = self._write_summary(Path(tmpdir))
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["score_outputs"]["raw_score_matrices"] = "D:/local/run/raw"
            summary_path.write_text(json.dumps(summary), encoding="utf-8")
            payload = validate_clid_score_summary(summary_path)

        self.assertEqual(payload["status"], "blocked")
        self.assertIn("portable_artifact_references", payload["missing"])

    def test_inconsistent_gate_blocks_schema(self) -> None:
        from diffaudit.attacks.clid_score_schema import validate_clid_score_summary

        with tempfile.TemporaryDirectory() as tmpdir:
            summary_path = self._write_summary(
                Path(tmpdir),
                member_rows=16,
                nonmember_rows=16,
                passed=True,
            )
            payload = validate_clid_score_summary(summary_path)

        self.assertEqual(payload["status"], "blocked")
        self.assertIn("low_fpr_gate_consistent", payload["missing"])


if __name__ == "__main__":
    unittest.main()
