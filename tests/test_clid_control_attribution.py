import json
import tempfile
import unittest
from pathlib import Path


def _write_run(root: Path, *, auc: float, tpr: float, member_offset: float, nonmember_offset: float) -> None:
    outputs = root / "outputs"
    summary_dir = root / "score-summary-workspace"
    outputs.mkdir(parents=True, exist_ok=True)
    summary_dir.mkdir(parents=True, exist_ok=True)
    (outputs / "scores_TRTE_train.txt").write_text(
        "\n".join(
            [
                "header",
                f"{0.1 + member_offset}\t{-1.0 - member_offset}",
                f"{0.2 + member_offset}\t{-1.1 - member_offset}",
                f"{0.3 + member_offset}\t{-1.2 - member_offset}",
            ]
        ),
        encoding="utf-8",
    )
    (outputs / "scores_TRTE_test.txt").write_text(
        "\n".join(
            [
                "header",
                f"{0.8 + nonmember_offset}\t{1.0 + nonmember_offset}",
                f"{0.9 + nonmember_offset}\t{1.1 + nonmember_offset}",
                f"{1.0 + nonmember_offset}\t{1.2 + nonmember_offset}",
            ]
        ),
        encoding="utf-8",
    )
    (summary_dir / "summary.json").write_text(
        json.dumps(
            {
                "metrics": {
                    "auc": auc,
                    "asr": auc,
                    "tpr_at_1pct_fpr": tpr,
                    "tpr_at_0_1pct_fpr": tpr,
                    "best_alpha": 1.0,
                }
            }
        ),
        encoding="utf-8",
    )


class ClidControlAttributionTests(unittest.TestCase):
    def test_compare_control_packets_reports_retention_and_correlations(self) -> None:
        from diffaudit.attacks.clid_control_attribution import compare_clid_control_packets

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            baseline = root / "baseline"
            control = root / "control"
            _write_run(baseline, auc=1.0, tpr=1.0, member_offset=0.0, nonmember_offset=0.0)
            _write_run(control, auc=0.5, tpr=0.25, member_offset=0.1, nonmember_offset=0.2)

            payload = compare_clid_control_packets(
                ("baseline", baseline),
                [("control", control)],
            )

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["controls"][0]["metric_delta_vs_baseline"]["tpr_at_0_1pct_fpr_retention"], 0.25)
        self.assertIn("member", payload["controls"][0]["feature_correlation_vs_baseline"])
        self.assertEqual(payload["verdict"], "controls degrade CLiD strict-tail signal; no control admits CLiD")


if __name__ == "__main__":
    unittest.main()
