from __future__ import annotations

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

from scripts import validate_secmi_supporting_contract


class ValidateSecmiSupportingContractTests(unittest.TestCase):
    def _artifact(self) -> dict:
        metrics = {
            "auc": 0.5,
            "asr": 0.5,
            "tpr_at_1pct_fpr": 0.1,
            "tpr_at_0_1pct_fpr": 0.01,
        }
        return {
            "schema": "diffaudit.secmi_admission_boundary_review.v1",
            "status": "evidence-ready-supporting-reference",
            "admitted": False,
            "gpu_release": "none",
            "secmi_runtime": {
                "member_samples": 25000,
                "nonmember_samples": 25000,
                "t_sec": 100,
                "k": 10,
                "batch_size": 64,
            },
            "secmi_stat": copy.deepcopy(metrics),
            "secmi_nns": copy.deepcopy(metrics),
            "pia_admitted_baseline": copy.deepcopy(metrics),
            "verdict": {
                "promotion_blockers": [
                    "missing admitted-consumer boundary contract",
                    "missing structured admitted-row cost/adaptive_check fields",
                    "NNS auxiliary head needs an explicit product-facing scorer contract",
                    "no bounded repeated-query adaptive review",
                ],
                "blocked_claims": ["admitted Platform/Runtime row"],
            },
        }

    def test_project_artifact_is_valid(self) -> None:
        exit_code = validate_secmi_supporting_contract.main([])
        self.assertEqual(exit_code, 0)

    def test_rejects_admitted_promotion_without_contract(self) -> None:
        artifact = self._artifact()
        artifact["admitted"] = True
        errors = validate_secmi_supporting_contract.validate(artifact)
        self.assertIn("SecMI supporting contract must not mark the row admitted", errors)

    def test_rejects_missing_nns_product_facing_blocker(self) -> None:
        artifact = self._artifact()
        artifact["verdict"]["promotion_blockers"] = [
            blocker
            for blocker in artifact["verdict"]["promotion_blockers"]
            if blocker != "NNS auxiliary head needs an explicit product-facing scorer contract"
        ]
        errors = validate_secmi_supporting_contract.validate(artifact)
        self.assertIn(
            "missing promotion blocker: NNS auxiliary head needs an explicit product-facing scorer contract",
            errors,
        )

    def test_rejects_non_numeric_metrics(self) -> None:
        artifact = self._artifact()
        artifact["secmi_nns"] = copy.deepcopy(artifact["secmi_nns"])
        artifact["secmi_nns"]["auc"] = "0.94"
        errors = validate_secmi_supporting_contract.validate(artifact)
        self.assertIn("secmi_nns.auc must be numeric, got '0.94'", errors)

    def test_rejects_out_of_range_metrics(self) -> None:
        artifact = self._artifact()
        artifact["secmi_stat"] = copy.deepcopy(artifact["secmi_stat"])
        artifact["secmi_stat"]["tpr_at_1pct_fpr"] = 1.1
        errors = validate_secmi_supporting_contract.validate(artifact)
        self.assertIn("secmi_stat.tpr_at_1pct_fpr must be in [0, 1], got 1.1", errors)

    def test_rejects_non_finite_metrics(self) -> None:
        artifact = self._artifact()
        artifact["pia_admitted_baseline"] = copy.deepcopy(artifact["pia_admitted_baseline"])
        artifact["pia_admitted_baseline"]["auc"] = math.inf
        errors = validate_secmi_supporting_contract.validate(artifact)
        self.assertIn("pia_admitted_baseline.auc must be finite, got inf", errors)

    def test_rejects_non_object_json_root(self) -> None:
        errors = validate_secmi_supporting_contract.validate([])
        self.assertEqual(errors, ["artifact must be a JSON object"])

    def test_cli_rejects_invalid_artifact_file(self) -> None:
        artifact = self._artifact()
        artifact["gpu_release"] = "cuda"
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "secmi.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")
            exit_code = validate_secmi_supporting_contract.main(["--artifact", str(path)])
        self.assertEqual(exit_code, 2)

    def test_cli_rejects_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "secmi.json"
            path.write_text("{not json", encoding="utf-8")
            exit_code = validate_secmi_supporting_contract.main(["--artifact", str(path)])
        self.assertEqual(exit_code, 2)

    def test_cli_rejects_directory_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = validate_secmi_supporting_contract.main(["--artifact", tmpdir])
        self.assertEqual(exit_code, 2)


if __name__ == "__main__":
    unittest.main()
