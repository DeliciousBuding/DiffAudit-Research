import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


def load_validate_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "validate_attack_defense_table.py"
    spec = importlib.util.spec_from_file_location("validate_attack_defense_table_module", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ValidateAttackDefenseTableTests(unittest.TestCase):
    def test_project_attack_defense_table_is_currently_valid(self) -> None:
        module = load_validate_module()
        research_root = Path(__file__).resolve().parents[1]

        exit_code = module.main(
            [
                "--table",
                str(research_root / "workspaces" / "implementation" / "artifacts" / "unified-attack-defense-table.json"),
            ]
        )

        self.assertEqual(exit_code, 0)

    def test_project_table_promotes_latest_gsa_rerun_as_mainline(self) -> None:
        research_root = Path(__file__).resolve().parents[1]
        payload = json.loads(
            (research_root / "workspaces" / "implementation" / "artifacts" / "unified-attack-defense-table.json").read_text(
                encoding="utf-8"
            )
        )

        gsa_row = next(
            row
            for row in payload["rows"]
            if row.get("track") == "white-box" and row.get("attack") == "GSA 1k-3shadow" and row.get("defense") == "none"
        )

        self.assertEqual(
            gsa_row["source"],
            "workspaces/white-box/runs/gsa-runtime-mainline-20260409-cifar10-1k-3shadow-epoch300-rerun1/summary.json",
        )
        self.assertEqual(gsa_row["auc"], 0.998192)
        self.assertEqual(gsa_row["asr"], 0.9895)
        self.assertEqual(gsa_row["tpr_at_1pct_fpr"], 0.987)
        self.assertEqual(gsa_row["tpr_at_0_1pct_fpr"], 0.432)
        self.assertIn("not a final paper-level benchmark", gsa_row["boundary"])

    def test_project_table_rows_expose_boundary(self) -> None:
        research_root = Path(__file__).resolve().parents[1]
        payload = json.loads(
            (research_root / "workspaces" / "implementation" / "artifacts" / "unified-attack-defense-table.json").read_text(
                encoding="utf-8"
            )
        )

        for row in payload["rows"]:
            self.assertIn("boundary", row)
            self.assertTrue(row["boundary"])

    def test_project_table_has_product_ready_recon_row(self) -> None:
        research_root = Path(__file__).resolve().parents[1]
        payload = json.loads(
            (research_root / "workspaces" / "implementation" / "artifacts" / "unified-attack-defense-table.json").read_text(
                encoding="utf-8"
            )
        )

        recon_rows = [
            row
            for row in payload["rows"]
            if row.get("track") == "black-box"
            and row.get("attack") == "recon DDIM public-100 step30"
            and row.get("defense") == "none"
            and row.get("evidence_level") == "runtime-mainline"
        ]
        self.assertEqual(len(recon_rows), 1, "Expected exactly one admitted recon product row")
        recon_row = recon_rows[0]

        self.assertEqual(recon_row["metric_source"], "upstream_threshold_reimplementation")
        self.assertEqual(recon_row["source"], "docs/evidence/recon-product-validation-result.md")
        self.assertEqual(recon_row["tpr_at_0_1pct_fpr"], 0.11)
        self.assertIn("zero-false-positive empirical tail", recon_row["boundary"])

    def test_project_table_has_expected_admitted_consumer_rows(self) -> None:
        research_root = Path(__file__).resolve().parents[1]
        payload = json.loads(
            (research_root / "workspaces" / "implementation" / "artifacts" / "unified-attack-defense-table.json").read_text(
                encoding="utf-8"
            )
        )

        selectors = [
            {
                "track": "black-box",
                "attack": "recon DDIM public-100 step30",
                "defense": "none",
                "evidence_level": "runtime-mainline",
            },
            {
                "track": "gray-box",
                "attack": "PIA GPU512 baseline",
                "defense": "none",
                "evidence_level": "runtime-mainline",
            },
            {
                "track": "gray-box",
                "attack": "PIA GPU512 baseline",
                "defense": "provisional G-1 = stochastic-dropout (all_steps)",
                "evidence_level": "runtime-mainline",
            },
            {
                "track": "white-box",
                "attack": "GSA 1k-3shadow",
                "defense": "none",
                "evidence_level": "runtime-mainline",
            },
            {
                "track": "white-box",
                "attack": "GSA 1k-3shadow",
                "defense": "W-1 strong-v3 full-scale",
                "evidence_level": "runtime-smoke",
            },
        ]

        for selector in selectors:
            matches = [
                row
                for row in payload["rows"]
                if all(row.get(key) == value for key, value in selector.items())
            ]
            self.assertEqual(len(matches), 1, f"Expected exactly one admitted consumer row for {selector}")
            row = matches[0]
            self.assertIsInstance(row["auc"], (int, float))
            self.assertIsInstance(row["asr"], (int, float))
            self.assertIsInstance(row["tpr_at_1pct_fpr"], (int, float))
            self.assertIsInstance(row["tpr_at_0_1pct_fpr"], (int, float))
            self.assertTrue(row["boundary"])
            self.assertTrue(row["quality_cost"])

    def test_validator_rejects_row_missing_required_field(self) -> None:
        module = load_validate_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            table_path = Path(tmpdir) / "table.json"
            table_path.write_text(
                json.dumps(
                    {
                        "schema": "diffaudit.attack_defense_table.v1",
                        "updated_at": "2026-04-09T12:05:00+08:00",
                        "rows": [
                            {
                                "track": "black-box",
                                "attack": "recon DDIM public-100 step30",
                                "defense": "none",
                                "model": "Stable Diffusion v1.5 + DDIM",
                                "evidence_level": "runtime-mainline",
                                "boundary": "controlled / public-subset / risk-exists",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            exit_code = module.main(["--table", str(table_path)])

        self.assertEqual(exit_code, 2)

    def test_validator_rejects_absolute_source_paths(self) -> None:
        module = load_validate_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            table_path = Path(tmpdir) / "table.json"
            absolute_source = str(
                (Path(tmpdir) / "Research" / "experiments" / "recon" / "summary.json").resolve()
            )
            table_path.write_text(
                json.dumps(
                    {
                        "schema": "diffaudit.attack_defense_table.v1",
                        "updated_at": "2026-04-09T12:05:00+08:00",
                        "rows": [
                            {
                                "track": "black-box",
                                "attack": "recon DDIM public-100 step30",
                                "defense": "none",
                                "model": "Stable Diffusion v1.5 + DDIM",
                                "evidence_level": "runtime-mainline",
                                "boundary": "controlled / public-subset / risk-exists",
                                "source": absolute_source,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            exit_code = module.main(["--table", str(table_path)])

        self.assertEqual(exit_code, 2)

    def test_validator_rejects_gray_box_row_without_adaptive_check(self) -> None:
        module = load_validate_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            table_path = Path(tmpdir) / "table.json"
            table_path.write_text(
                json.dumps(
                    {
                        "schema": "diffaudit.attack_defense_table.v1",
                        "updated_at": "2026-04-09T12:05:00+08:00",
                        "rows": [
                            {
                                "track": "gray-box",
                                "attack": "PIA GPU512 baseline",
                                "defense": "none",
                                "model": "CIFAR-10 DDPM",
                                "evidence_level": "runtime-mainline",
                                "boundary": "workspace-verified + adaptive-reviewed + paper-alignment blocked by checkpoint/source provenance",
                                "source": "workspaces/gray-box/runs/pia/summary.json",
                                "quality": {"suite": "pia-runtime-surrogate-v1"},
                                "cost": {"device": "cuda:0"},
                                "provenance_status": "workspace-verified",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            exit_code = module.main(["--table", str(table_path)])

        self.assertEqual(exit_code, 2)

    def test_validator_rejects_gray_box_row_without_provenance_status(self) -> None:
        module = load_validate_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            table_path = Path(tmpdir) / "table.json"
            table_path.write_text(
                json.dumps(
                    {
                        "schema": "diffaudit.attack_defense_table.v1",
                        "updated_at": "2026-04-09T12:05:00+08:00",
                        "rows": [
                            {
                                "track": "gray-box",
                                "attack": "PIA GPU512 baseline",
                                "defense": "none",
                                "model": "CIFAR-10 DDPM",
                                "evidence_level": "runtime-mainline",
                                "boundary": "workspace-verified + adaptive-reviewed + paper-alignment blocked by checkpoint/source provenance",
                                "source": "workspaces/gray-box/runs/pia/summary.json",
                                "quality": {"suite": "pia-runtime-surrogate-v1"},
                                "cost": {"device": "cuda:0"},
                                "adaptive_check": {
                                    "status": "completed",
                                    "query_repeats": 3,
                                    "aggregation": "mean",
                                    "metrics": {"auc": 0.84},
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            exit_code = module.main(["--table", str(table_path)])

        self.assertEqual(exit_code, 2)

    def test_validator_rejects_recon_product_row_missing_metric_source(self) -> None:
        module = load_validate_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            table_path = Path(tmpdir) / "table.json"
            table_path.write_text(
                json.dumps(
                    {
                        "schema": "diffaudit.attack_defense_table.v1",
                        "updated_at": "2026-05-01T00:00:00+08:00",
                        "rows": [
                            {
                                "track": "black-box",
                                "attack": "recon DDIM public-100 step30",
                                "defense": "none",
                                "model": "Stable Diffusion v1.5 + DDIM",
                                "auc": 0.837,
                                "asr": 0.74,
                                "tpr_at_1pct_fpr": 0.22,
                                "tpr_at_0_1pct_fpr": 0.11,
                                "evidence_level": "runtime-mainline",
                                "quality_cost": "100 public samples per split",
                                "note": "current black-box main evidence",
                                "boundary": "controlled / public-subset / proxy-shadow-member / zero-false-positive empirical tail / not a final exploit",
                                "source": "docs/evidence/recon-product-validation-result.md",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            exit_code = module.main(["--table", str(table_path)])

        self.assertEqual(exit_code, 2)

    def test_validator_rejects_bool_recon_metric(self) -> None:
        module = load_validate_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            table_path = Path(tmpdir) / "table.json"
            table_path.write_text(
                json.dumps(
                    {
                        "schema": "diffaudit.attack_defense_table.v1",
                        "updated_at": "2026-05-01T00:00:00+08:00",
                        "rows": [
                            {
                                "track": "black-box",
                                "attack": "recon DDIM public-100 step30",
                                "defense": "none",
                                "model": "Stable Diffusion v1.5 + DDIM",
                                "auc": True,
                                "asr": 0.74,
                                "tpr_at_1pct_fpr": 0.22,
                                "tpr_at_0_1pct_fpr": 0.11,
                                "evidence_level": "runtime-mainline",
                                "metric_source": "upstream_threshold_reimplementation",
                                "quality_cost": "100 public samples per split",
                                "note": "current black-box main evidence",
                                "boundary": "controlled / public-subset / proxy-shadow-member / zero-false-positive empirical tail / not a final exploit",
                                "source": "docs/evidence/recon-product-validation-result.md",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            exit_code = module.main(["--table", str(table_path)])

        self.assertEqual(exit_code, 2)

    def test_validator_rejects_missing_admitted_consumer_row(self) -> None:
        module = load_validate_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            table_path = Path(tmpdir) / "table.json"
            table_path.write_text(
                json.dumps(
                    {
                        "schema": "diffaudit.attack_defense_table.v1",
                        "updated_at": "2026-05-01T00:00:00+08:00",
                        "rows": [
                            {
                                "track": "black-box",
                                "attack": "recon DDIM public-100 step30",
                                "defense": "none",
                                "model": "Stable Diffusion v1.5 + DDIM",
                                "auc": 0.837,
                                "asr": 0.74,
                                "tpr_at_1pct_fpr": 0.22,
                                "tpr_at_0_1pct_fpr": 0.11,
                                "evidence_level": "runtime-mainline",
                                "metric_source": "upstream_threshold_reimplementation",
                                "quality_cost": "100 public samples per split",
                                "note": "current black-box main evidence",
                                "boundary": "controlled / public-subset / proxy-shadow-member / zero-false-positive empirical tail / not a final exploit",
                                "source": "docs/evidence/recon-product-validation-result.md",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            exit_code = module.main(["--table", str(table_path)])

        self.assertEqual(exit_code, 2)


if __name__ == "__main__":
    unittest.main()
