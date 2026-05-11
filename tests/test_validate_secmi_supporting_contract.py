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

    def _hardening_artifact(self) -> dict:
        metrics = {
            "auc": 0.8,
            "asr": 0.7,
            "tpr_at_1pct_fpr": 0.1,
            "tpr_at_0_1pct_fpr": 0.01,
        }
        base_row = {
            "consumer_decision": "research-support-only",
            "admission_decision": "blocked",
            "metrics": copy.deepcopy(metrics),
            "missing_for_admission": [
                "admitted-consumer boundary contract",
                "structured adaptive_check comparable to admitted PIA rows",
                "bounded repeated-query adaptive review",
            ],
        }
        stat_row = copy.deepcopy(base_row)
        stat_row.update({"id": "stat", "head": "stat"})
        nns_row = copy.deepcopy(base_row)
        nns_row.update({"id": "nns", "head": "nns"})
        nns_row["missing_for_admission"].append("explicit product-facing auxiliary-head contract")
        return {
            "schema": "diffaudit.secmi_admission_contract_hardening.v1",
            "status": "supporting-reference-hardened",
            "admitted": False,
            "gpu_release": "none",
            "candidate_rows": [stat_row, nns_row],
            "blocked_claims": [
                "admitted Platform/Runtime row",
                "PIA replacement",
                "product-facing NNS auxiliary head",
                "adaptive robustness",
            ],
            "next_reopen_contract": {
                "mode": "CPU-first",
                "required_before_gpu": [
                    "define a SecMI consumer row schema separate from the admitted PIA rows",
                    "decide whether NNS may ever be product-facing or must remain Research-only",
                    "freeze an adaptive repeated-query review protocol",
                    "freeze low-FPR finite-tail denominator semantics",
                ],
                "gpu_cap": "none until the CPU contract is reviewed",
            },
            "evidence_docs": [
                "docs/evidence/secmi-full-split-admission-boundary-review.md",
                "docs/evidence/secmi-admission-contract-hardening-20260511.md",
            ],
        }
    def test_project_artifact_is_valid(self) -> None:
        exit_code = validate_secmi_supporting_contract.main([])
        self.assertEqual(exit_code, 0)

    def test_project_hardening_artifact_is_valid(self) -> None:
        path = Path("workspaces/gray-box/artifacts/secmi-admission-contract-hardening-20260511.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        errors = validate_secmi_supporting_contract.validate_hardening(payload)
        self.assertEqual(errors, [])

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

    def test_hardening_rejects_nns_without_auxiliary_contract_blocker(self) -> None:
        artifact = self._hardening_artifact()
        nns_row = artifact["candidate_rows"][1]
        nns_row["missing_for_admission"] = [
            blocker
            for blocker in nns_row["missing_for_admission"]
            if blocker != "explicit product-facing auxiliary-head contract"
        ]
        errors = validate_secmi_supporting_contract.validate_hardening(artifact)
        self.assertIn("NNS row must require an explicit product-facing auxiliary-head contract", errors)

    def test_hardening_rejects_gpu_release(self) -> None:
        artifact = self._hardening_artifact()
        artifact["gpu_release"] = "cuda"
        errors = validate_secmi_supporting_contract.validate_hardening(artifact)
        self.assertIn("SecMI hardening contract must not release GPU work", errors)

    def test_hardening_rejects_missing_contract_doc(self) -> None:
        artifact = self._hardening_artifact()
        artifact["evidence_docs"] = ["docs/evidence/secmi-full-split-admission-boundary-review.md"]
        errors = validate_secmi_supporting_contract.validate_hardening(artifact)
        self.assertIn(
            "missing evidence doc: docs/evidence/secmi-admission-contract-hardening-20260511.md",
            errors,
        )

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
