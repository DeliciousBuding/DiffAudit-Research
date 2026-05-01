from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path


def load_export_module():
    from scripts import export_recon_product_evidence_card

    return export_recon_product_evidence_card


class ExportReconProductEvidenceCardTests(unittest.TestCase):
    def test_project_card_is_in_sync(self) -> None:
        module = load_export_module()
        exit_code = module.main(["--check"])
        self.assertEqual(exit_code, 0)

    def test_card_preserves_recon_tail_provenance(self) -> None:
        research_root = Path(__file__).resolve().parents[1]
        card = json.loads(
            (
                research_root
                / "workspaces"
                / "implementation"
                / "artifacts"
                / "recon-product-evidence-card.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(card["schema"], "diffaudit.product_evidence_card.v1")
        self.assertEqual(card["status"], "admitted")
        self.assertEqual(card["method"]["attack"], "recon DDIM public-100 step30")
        self.assertEqual(card["metric_source"], "upstream_threshold_reimplementation")
        self.assertEqual(card["metrics"]["tpr_at_0_1pct_fpr"], 0.11)
        self.assertEqual(card["finite_tail"]["target_nonmember_count"], 100)
        self.assertEqual(card["finite_tail"]["gates"]["tpr_at_0_1pct_fpr"]["false_positives"], 0)
        self.assertEqual(card["provenance"]["source"], "docs/evidence/recon-product-validation-result.md")
        self.assertIn("fine-grained sub-percent FPR calibration", card["boundary"]["blocked_claims"])

    def test_export_rejects_missing_recon_row(self) -> None:
        module = load_export_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            table_path = Path(tmpdir) / "table.json"
            output_path = Path(tmpdir) / "card.json"
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
