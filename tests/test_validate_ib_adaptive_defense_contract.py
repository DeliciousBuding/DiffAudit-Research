from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts import validate_ib_adaptive_defense_contract


class ValidateIbAdaptiveDefenseContractTests(unittest.TestCase):
    def _artifact(self) -> dict:
        root = Path(__file__).resolve().parents[1]
        return json.loads(
            (root / validate_ib_adaptive_defense_contract.DEFAULT_ARTIFACT).read_text(encoding="utf-8")
        )

    def test_project_artifact_is_valid(self) -> None:
        exit_code = validate_ib_adaptive_defense_contract.main([])
        self.assertEqual(exit_code, 0)

    def test_rejects_admitted_promotion(self) -> None:
        artifact = self._artifact()
        artifact["admitted"] = True
        errors = validate_ib_adaptive_defense_contract.validate(artifact)
        self.assertIn("I-B adaptive defense contract must not mark the row admitted", errors)

    def test_rejects_gpu_release(self) -> None:
        artifact = self._artifact()
        artifact["gpu_release"] = "cuda"
        errors = validate_ib_adaptive_defense_contract.validate(artifact)
        self.assertIn("I-B adaptive defense contract must not release GPU work", errors)

    def test_rejects_adaptive_claim(self) -> None:
        artifact = self._artifact()
        artifact["observed_boundary"] = copy.deepcopy(artifact["observed_boundary"])
        artifact["observed_boundary"]["defense_aware_attacker_used"] = True
        errors = validate_ib_adaptive_defense_contract.validate(artifact)
        self.assertIn("observed_boundary.defense_aware_attacker_used must be false", errors)

    def test_rejects_missing_reopen_requirement(self) -> None:
        artifact = self._artifact()
        artifact["required_reopen_contract"] = copy.deepcopy(artifact["required_reopen_contract"])
        artifact["required_reopen_contract"]["adaptive_attacker_protocol"] = "optional"
        errors = validate_ib_adaptive_defense_contract.validate(artifact)
        self.assertIn("required_reopen_contract.adaptive_attacker_protocol must be required", errors)

    def test_rejects_bad_delta(self) -> None:
        artifact = self._artifact()
        artifact["reviewed_runs"] = copy.deepcopy(artifact["reviewed_runs"])
        artifact["reviewed_runs"][0]["delta_auc"] = "small"
        errors = validate_ib_adaptive_defense_contract.validate(artifact)
        self.assertIn("reviewed_runs[0].delta_auc must be numeric, got 'small'", errors)

    def test_rejects_missing_blocked_claim(self) -> None:
        artifact = self._artifact()
        artifact["blocked_claims"] = [
            claim for claim in artifact["blocked_claims"] if claim != "adaptive robustness"
        ]
        errors = validate_ib_adaptive_defense_contract.validate(artifact)
        self.assertIn("missing blocked claim: adaptive robustness", errors)

    def test_rejects_missing_contract_evidence_doc(self) -> None:
        artifact = self._artifact()
        artifact["evidence_docs"] = [
            doc
            for doc in artifact["evidence_docs"]
            if doc != "docs/evidence/ib-adaptive-defense-contract-20260511.md"
        ]
        errors = validate_ib_adaptive_defense_contract.validate(artifact)
        self.assertIn(
            "missing evidence doc: docs/evidence/ib-adaptive-defense-contract-20260511.md",
            errors,
        )

    def test_rejects_non_object_root(self) -> None:
        errors = validate_ib_adaptive_defense_contract.validate([])
        self.assertEqual(errors, ["artifact must be a JSON object"])

    def test_cli_rejects_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "ib.json"
            path.write_text("{bad json", encoding="utf-8")
            exit_code = validate_ib_adaptive_defense_contract.main(["--artifact", str(path)])
        self.assertEqual(exit_code, 2)


if __name__ == "__main__":
    unittest.main()
