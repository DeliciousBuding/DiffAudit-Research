from __future__ import annotations

import copy
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts import validate_ib_defended_shadow_reopen_protocol


class ValidateIbDefendedShadowReopenProtocolTests(unittest.TestCase):
    def _artifact(self) -> dict:
        root = Path(__file__).resolve().parents[1]
        return json.loads(
            (root / validate_ib_defended_shadow_reopen_protocol.DEFAULT_ARTIFACT).read_text(
                encoding="utf-8"
            )
        )

    def test_project_artifact_is_valid(self) -> None:
        self.assertEqual(validate_ib_defended_shadow_reopen_protocol.main([]), 0)

    def test_rejects_gpu_release(self) -> None:
        artifact = self._artifact()
        artifact["gpu_release"] = "cuda"

        errors = validate_ib_defended_shadow_reopen_protocol.validate(artifact)

        self.assertIn("protocol must not release GPU work", errors)

    def test_rejects_missing_defended_shadow_entrypoint(self) -> None:
        artifact = self._artifact()
        artifact["defended_shadow_training_protocol"] = copy.deepcopy(
            artifact["defended_shadow_training_protocol"]
        )
        artifact["defended_shadow_training_protocol"]["entrypoint"] = ""

        errors = validate_ib_defended_shadow_reopen_protocol.validate(artifact)

        self.assertIn("defended_shadow_training_protocol.entrypoint must be non-empty", errors)

    def test_rejects_undefended_shadow_reference(self) -> None:
        artifact = self._artifact()
        artifact["adaptive_attacker_protocol"] = copy.deepcopy(artifact["adaptive_attacker_protocol"])
        artifact["adaptive_attacker_protocol"]["threshold_reference"] = "undefended-shadows"

        errors = validate_ib_defended_shadow_reopen_protocol.validate(artifact)

        self.assertIn(
            "adaptive_attacker_protocol.threshold_reference must be defended-shadows",
            errors,
        )

    def test_rejects_missing_low_fpr_metric(self) -> None:
        artifact = self._artifact()
        artifact["primary_metrics"] = [
            metric for metric in artifact["primary_metrics"] if metric != "TPR@0.1%FPR"
        ]

        errors = validate_ib_defended_shadow_reopen_protocol.validate(artifact)

        self.assertIn("missing primary metric: TPR@0.1%FPR", errors)

    def test_rejects_bad_stop_condition(self) -> None:
        artifact = self._artifact()
        artifact["stop_conditions"] = copy.deepcopy(artifact["stop_conditions"])
        artifact["stop_conditions"]["no_strict_tail_improvement"] = "continue"

        errors = validate_ib_defended_shadow_reopen_protocol.validate(artifact)

        self.assertIn(
            "stop_conditions.no_strict_tail_improvement must be close-line",
            errors,
        )

    def test_rejects_missing_evidence_doc(self) -> None:
        artifact = self._artifact()
        artifact["evidence_docs"] = [
            doc
            for doc in artifact["evidence_docs"]
            if doc != "docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md"
        ]

        errors = validate_ib_defended_shadow_reopen_protocol.validate(artifact)

        self.assertIn(
            "missing evidence doc: docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md",
            errors,
        )

    def test_rejects_missing_undefended_gpu_blocker(self) -> None:
        artifact = self._artifact()
        artifact["blocked_claims"] = [
            claim
            for claim in artifact["blocked_claims"]
            if claim != "old undefended threshold-transfer GPU packet"
        ]

        errors = validate_ib_defended_shadow_reopen_protocol.validate(artifact)

        self.assertIn(
            "missing blocked claim: old undefended threshold-transfer GPU packet",
            errors,
        )

    def test_cli_rejects_malformed_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "protocol.json"
            path.write_text("{bad json", encoding="utf-8")
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exit_code = validate_ib_defended_shadow_reopen_protocol.main(
                    ["--artifact", str(path)]
                )

        self.assertEqual(exit_code, 2)
        self.assertIn("failed to load artifact", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
