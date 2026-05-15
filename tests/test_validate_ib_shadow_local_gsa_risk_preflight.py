import copy
import json
import unittest
from pathlib import Path

from scripts import validate_ib_shadow_local_gsa_risk_preflight


def _load_default_artifact() -> dict:
    root = Path(__file__).resolve().parents[1]
    return json.loads((root / validate_ib_shadow_local_gsa_risk_preflight.DEFAULT_ARTIFACT).read_text(encoding="utf-8"))


class ValidateIBShadowLocalGSARiskPreflightTests(unittest.TestCase):
    def test_default_artifact_is_valid(self) -> None:
        self.assertEqual(validate_ib_shadow_local_gsa_risk_preflight.main([]), 0)

    def test_rejects_ready_status(self) -> None:
        artifact = _load_default_artifact()
        artifact["status"] = "ready"
        errors = validate_ib_shadow_local_gsa_risk_preflight.validate(artifact)
        self.assertIn("status must remain blocked because PIA shadow-local risk is missing", errors)

    def test_requires_true_gsa_only_and_false_pia_gsa_claims(self) -> None:
        artifact = _load_default_artifact()
        artifact["risk_record_provenance"] = copy.deepcopy(artifact["risk_record_provenance"])
        artifact["risk_record_provenance"]["true_shadow_local_gsa_risk_scoring"] = False
        artifact["risk_record_provenance"]["true_shadow_local_pia_gsa_risk_scoring"] = True
        errors = validate_ib_shadow_local_gsa_risk_preflight.validate(artifact)
        self.assertIn("true_shadow_local_gsa_risk_scoring must be true", errors)
        self.assertIn("true_shadow_local_pia_gsa_risk_scoring must be false", errors)

    def test_rejects_missing_pia_blocker(self) -> None:
        artifact = _load_default_artifact()
        artifact["blocked_claims"] = [
            claim
            for claim in artifact["blocked_claims"]
            if claim != "true shadow-local PIA/GSA risk scoring"
        ]
        errors = validate_ib_shadow_local_gsa_risk_preflight.validate(artifact)
        self.assertIn("missing blocked claim: true shadow-local PIA/GSA risk scoring", errors)

    def test_rejects_overlapping_forget_and_matched_nonmember_ids(self) -> None:
        artifact = _load_default_artifact()
        artifact["shadow_risk_preflight"] = copy.deepcopy(artifact["shadow_risk_preflight"])
        entry = artifact["shadow_risk_preflight"][0]
        entry["candidate_matched_nonmember_indices"][0] = entry["candidate_forget_member_indices"][0]
        errors = validate_ib_shadow_local_gsa_risk_preflight.validate(artifact)
        self.assertIn("shadow_risk_preflight[0] candidate forget and matched nonmember IDs must be disjoint", errors)


if __name__ == "__main__":
    unittest.main()
