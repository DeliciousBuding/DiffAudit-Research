from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path


def load_export_module():
    from scripts import export_admitted_evidence_bundle

    return export_admitted_evidence_bundle


class ExportAdmittedEvidenceBundleTests(unittest.TestCase):
    def test_project_bundle_is_in_sync(self) -> None:
        module = load_export_module()
        exit_code = module.main(["--check"])
        self.assertEqual(exit_code, 0)

    def test_bundle_preserves_all_admitted_consumer_rows(self) -> None:
        research_root = Path(__file__).resolve().parents[1]
        bundle = json.loads(
            (
                research_root
                / "workspaces"
                / "implementation"
                / "artifacts"
                / "admitted-evidence-bundle.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(bundle["schema"], "diffaudit.admitted_evidence_bundle.v1")
        self.assertEqual(bundle["status"], "admitted-only")
        self.assertEqual(bundle["audience"], "platform-runtime")
        self.assertEqual(bundle["row_count"], 5)
        self.assertEqual(len(bundle["rows"]), 5)
        ids = {row["id"] for row in bundle["rows"]}
        self.assertIn("black-box::recon DDIM public-100 step30::none::runtime-mainline", ids)
        self.assertIn("gray-box::PIA GPU512 baseline::none::runtime-mainline", ids)
        self.assertIn(
            "gray-box::PIA GPU512 baseline::provisional G-1 = stochastic-dropout (all_steps)::runtime-mainline",
            ids,
        )
        self.assertIn("white-box::GSA 1k-3shadow::none::runtime-mainline", ids)
        self.assertIn("white-box::GSA 1k-3shadow::W-1 strong-v3 full-scale::runtime-smoke", ids)
        for row in bundle["rows"]:
            self.assertNotIn("GPU1024", row["method"]["attack"])
            self.assertNotIn("ReDiffuse", row["method"]["attack"])
            self.assertNotIn("CLiD", row["method"]["attack"])
            self.assertNotIn("TMIA-DM", row["method"]["attack"])
            self.assertNotIn("SecMI", row["method"]["attack"])

    def test_bundle_carries_boundary_and_provenance(self) -> None:
        research_root = Path(__file__).resolve().parents[1]
        bundle = json.loads(
            (
                research_root
                / "workspaces"
                / "implementation"
                / "artifacts"
                / "admitted-evidence-bundle.json"
            ).read_text(encoding="utf-8")
        )

        for row in bundle["rows"]:
            self.assertEqual(row["status"], "admitted")
            self.assertEqual(row["audience"], "platform-runtime")
            for metric in ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr"):
                value = row["metrics"][metric]
                self.assertIsInstance(value, (int, float))
                self.assertNotIsInstance(value, bool)
            self.assertEqual(row["low_fpr_interpretation"]["type"], "finite_empirical_tail")
            self.assertIn("continuous sub-percent", row["low_fpr_interpretation"]["summary"])
            self.assertTrue(row["boundary"]["summary"])
            self.assertIn("general conditional-diffusion result", row["boundary"]["blocked_claims"])
            self.assertEqual(
                row["provenance"]["table"],
                "workspaces/implementation/artifacts/unified-attack-defense-table.json",
            )
            self.assertFalse(Path(row["provenance"]["source"]).is_absolute())

    def test_gray_box_rows_preserve_adaptive_check(self) -> None:
        research_root = Path(__file__).resolve().parents[1]
        bundle = json.loads(
            (
                research_root
                / "workspaces"
                / "implementation"
                / "artifacts"
                / "admitted-evidence-bundle.json"
            ).read_text(encoding="utf-8")
        )

        gray_rows = [row for row in bundle["rows"] if row["track"] == "gray-box"]
        self.assertEqual(len(gray_rows), 2)
        for row in gray_rows:
            self.assertEqual(row["adaptive_check"]["status"], "completed")
            self.assertEqual(row["adaptive_check"]["query_repeats"], 3)
            self.assertEqual(row["cost"]["sample_count_per_split"], 512)
            self.assertTrue(
                any("full adaptive robustness" in claim for claim in row["boundary"]["blocked_claims"])
            )

    def test_export_rejects_missing_admitted_row(self) -> None:
        module = load_export_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            table_path = Path(tmpdir) / "table.json"
            output_path = Path(tmpdir) / "bundle.json"
            table_path.write_text(
                json.dumps(
                    {
                        "schema": "diffaudit.attack_defense_table.v1",
                        "updated_at": "2026-05-01T00:00:00+08:00",
                        "rows": [],
                    }
                ),
                encoding="utf-8",
            )

            exit_code = module.main(["--table", str(table_path), "--output", str(output_path)])

        self.assertEqual(exit_code, 2)


if __name__ == "__main__":
    unittest.main()
