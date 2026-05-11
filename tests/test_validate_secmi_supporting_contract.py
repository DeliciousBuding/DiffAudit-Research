from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts import validate_secmi_supporting_contract


class ValidateSecmiSupportingContractTests(unittest.TestCase):
    def _artifact(self) -> dict:
        root = Path(__file__).resolve().parents[1]
        return json.loads(
            (
                root
                / "workspaces"
                / "gray-box"
                / "artifacts"
                / "secmi-full-split-admission-boundary-20260511.json"
            ).read_text(encoding="utf-8")
        )

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

    def test_cli_rejects_invalid_artifact_file(self) -> None:
        artifact = self._artifact()
        artifact["gpu_release"] = "cuda"
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "secmi.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")
            exit_code = validate_secmi_supporting_contract.main(["--artifact", str(path)])
        self.assertEqual(exit_code, 2)


if __name__ == "__main__":
    unittest.main()
