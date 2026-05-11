from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts import validate_clid_identity_boundary


class ValidateClidIdentityBoundaryTests(unittest.TestCase):
    def _artifact(self) -> dict:
        root = Path(__file__).resolve().parents[1]
        return json.loads(
            (
                root
                / "workspaces"
                / "black-box"
                / "artifacts"
                / "clid-image-identity-boundary-20260511.json"
            ).read_text(encoding="utf-8")
        )

    def test_project_artifact_is_valid(self) -> None:
        exit_code = validate_clid_identity_boundary.main([])
        self.assertEqual(exit_code, 0)

    def test_rejects_admitted_promotion(self) -> None:
        artifact = self._artifact()
        artifact["admitted"] = True
        errors = validate_clid_identity_boundary.validate(artifact)
        self.assertIn("CLiD identity boundary must not mark the row admitted", errors)

    def test_rejects_gpu_release(self) -> None:
        artifact = self._artifact()
        artifact["gpu_release"] = "cuda"
        errors = validate_clid_identity_boundary.validate(artifact)
        self.assertIn("CLiD identity boundary must not release GPU work", errors)

    def test_rejects_missing_image_identity_blocker(self) -> None:
        artifact = self._artifact()
        artifact["promotion_blockers"] = [
            blocker
            for blocker in artifact["promotion_blockers"]
            if blocker != "no independent image-identity contract"
        ]
        errors = validate_clid_identity_boundary.validate(artifact)
        self.assertIn("missing promotion blocker: no independent image-identity contract", errors)

    def test_rejects_non_numeric_control_metric(self) -> None:
        artifact = self._artifact()
        artifact["controls"] = copy.deepcopy(artifact["controls"])
        artifact["controls"][0]["auc"] = "0.5"
        errors = validate_clid_identity_boundary.validate(artifact)
        self.assertIn("controls[0].auc must be numeric, got '0.5'", errors)

    def test_rejects_boundary_max_mismatch(self) -> None:
        artifact = self._artifact()
        artifact["identity_boundary"] = copy.deepcopy(artifact["identity_boundary"])
        artifact["identity_boundary"]["max_control_tpr_at_0_1pct_fpr"] = 0.12
        errors = validate_clid_identity_boundary.validate(artifact)
        self.assertIn(
            "identity_boundary.max_control_tpr_at_0_1pct_fpr must match max control strict tail",
            errors,
        )

    def test_rejects_high_control_strict_tail_for_hold_candidate(self) -> None:
        artifact = self._artifact()
        artifact["controls"] = copy.deepcopy(artifact["controls"])
        artifact["controls"][0]["tpr_at_0_1pct_fpr"] = 0.4
        artifact["identity_boundary"] = copy.deepcopy(artifact["identity_boundary"])
        artifact["identity_boundary"]["max_control_tpr_at_0_1pct_fpr"] = 0.4
        errors = validate_clid_identity_boundary.validate(artifact)
        self.assertIn(
            "identity_boundary.max_control_tpr_at_0_1pct_fpr is too high for hold-candidate boundary",
            errors,
        )

    def test_rejects_non_object_json_root(self) -> None:
        errors = validate_clid_identity_boundary.validate(None)
        self.assertEqual(errors, ["artifact must be a JSON object"])

    def test_cli_rejects_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "clid.json"
            path.write_text("{bad json", encoding="utf-8")
            exit_code = validate_clid_identity_boundary.main(["--artifact", str(path)])
        self.assertEqual(exit_code, 2)


if __name__ == "__main__":
    unittest.main()
