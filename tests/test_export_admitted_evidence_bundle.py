from __future__ import annotations

import json
import os
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
            self.assertIsInstance(row["low_fpr_interpretation"]["nonmember_denominator"], int)
            self.assertGreater(row["low_fpr_interpretation"]["nonmember_denominator"], 0)
            self.assertIn("false_positive_budget", row["low_fpr_interpretation"])
            self.assertGreater(row["low_fpr_interpretation"]["minimum_nonzero_fpr"], 0.0)
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
            self.assertEqual(row["low_fpr_interpretation"]["nonmember_denominator"], 512)
            self.assertTrue(
                any("full adaptive robustness" in claim for claim in row["boundary"]["blocked_claims"])
            )

    def test_tail_denominators_are_explicit_for_all_admitted_rows(self) -> None:
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

        denominators = {
            row["id"]: row["low_fpr_interpretation"]["nonmember_denominator"]
            for row in bundle["rows"]
        }
        self.assertEqual(
            denominators["black-box::recon DDIM public-100 step30::none::runtime-mainline"],
            100,
        )
        self.assertEqual(
            denominators["white-box::GSA 1k-3shadow::none::runtime-mainline"],
            2000,
        )
        self.assertEqual(
            denominators["white-box::GSA 1k-3shadow::W-1 strong-v3 full-scale::runtime-smoke"],
            2000,
        )
        for row in bundle["rows"]:
            tail = row["low_fpr_interpretation"]
            self.assertAlmostEqual(tail["false_positive_budget"]["at_1pct_fpr"], tail["nonmember_denominator"] * 0.01)
            self.assertAlmostEqual(
                tail["false_positive_budget"]["at_0_1pct_fpr"],
                tail["nonmember_denominator"] * 0.001,
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

    def test_export_rejects_unrecoverable_tail_denominator(self) -> None:
        module = load_export_module()
        research_root = Path(__file__).resolve().parents[1]
        table_path = research_root / "workspaces" / "implementation" / "artifacts" / "unified-attack-defense-table.json"
        table = json.loads(table_path.read_text(encoding="utf-8"))
        admitted_row = next(
            row
            for row in table["rows"]
            if row["track"] == "black-box"
            and row["attack"] == "recon DDIM public-100 step30"
            and row["defense"] == "none"
            and row["evidence_level"] == "runtime-mainline"
        )
        admitted_row["quality_cost"] = "packet scale not recorded"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_table = Path(tmpdir) / "table.json"
            tmp_output = Path(tmpdir) / "bundle.json"
            tmp_table.write_text(json.dumps(table), encoding="utf-8")

            exit_code = module.main(["--table", str(tmp_table), "--output", str(tmp_output)])

        self.assertEqual(exit_code, 2)

    def test_tail_denominator_extraction_fails_closed_on_zero_count(self) -> None:
        module = load_export_module()
        with self.assertRaisesRegex(ValueError, "black-box::zero-count::none::runtime-mainline"):
            module._tail_nonmember_count(
                {
                    "track": "black-box",
                    "attack": "zero-count",
                    "defense": "none",
                    "evidence_level": "runtime-mainline",
                    "quality_cost": "0 public samples per split",
                }
            )

    def test_cli_relative_paths_resolve_from_current_working_directory(self) -> None:
        module = load_export_module()
        research_root = Path(__file__).resolve().parents[1]
        table_source = research_root / "workspaces" / "implementation" / "artifacts" / "unified-attack-defense-table.json"
        original_cwd = Path.cwd()

        with tempfile.TemporaryDirectory(dir=research_root) as tmpdir:
            tmp_path = Path(tmpdir)
            table_path = tmp_path / "table.json"
            output_path = tmp_path / "bundle.json"
            table_path.write_text(table_source.read_text(encoding="utf-8"), encoding="utf-8")
            os.chdir(tmp_path)
            try:
                exit_code = module.main(["--table", "table.json", "--output", "bundle.json"])
            finally:
                os.chdir(original_cwd)

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
