import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts import validate_ib_shadow_local_identity_scout


def _load_default_artifact() -> dict:
    root = Path(__file__).resolve().parents[1]
    return json.loads((root / validate_ib_shadow_local_identity_scout.DEFAULT_ARTIFACT).read_text(encoding="utf-8"))


class ValidateIBShadowLocalIdentityScoutTests(unittest.TestCase):
    def test_default_artifact_is_valid(self) -> None:
        self.assertEqual(validate_ib_shadow_local_identity_scout.main([]), 0)

    def test_rejects_ready_status(self) -> None:
        artifact = _load_default_artifact()
        artifact["status"] = "ready"
        errors = validate_ib_shadow_local_identity_scout.validate(artifact)
        self.assertIn("status must remain blocked because this scout is not true shadow-local risk scoring", errors)

    def test_rejects_true_shadow_local_claim(self) -> None:
        artifact = _load_default_artifact()
        artifact["risk_record_provenance"] = copy.deepcopy(artifact["risk_record_provenance"])
        artifact["risk_record_provenance"]["true_shadow_local_risk_scoring"] = True
        errors = validate_ib_shadow_local_identity_scout.validate(artifact)
        self.assertIn("true_shadow_local_risk_scoring must be false", errors)

    def test_rejects_candidate_contract_with_one_shadow(self) -> None:
        artifact = _load_default_artifact()
        artifact["mechanically_possible_shadows"] = artifact["mechanically_possible_shadows"][:1]
        errors = validate_ib_shadow_local_identity_scout.validate(artifact)
        self.assertIn("candidate-contract mechanical_status requires at least two mechanically possible shadows", errors)

    def test_rejects_missing_semantic_blocker(self) -> None:
        artifact = _load_default_artifact()
        artifact["blocked_claims"] = [
            claim
            for claim in artifact["blocked_claims"]
            if claim != "true shadow-local risk scoring"
        ]
        errors = validate_ib_shadow_local_identity_scout.validate(artifact)
        self.assertIn("missing blocked claim: true shadow-local risk scoring", errors)

    def test_cli_reports_missing_doc(self) -> None:
        artifact = _load_default_artifact()
        artifact["evidence_docs"] = [
            doc
            for doc in artifact["evidence_docs"]
            if doc != "docs/evidence/ib-shadow-local-identity-scout-20260512.md"
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "artifact.json"
            path.write_text(json.dumps(artifact), encoding="utf-8")
            exit_code = validate_ib_shadow_local_identity_scout.main(["--artifact", str(path)])
        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
