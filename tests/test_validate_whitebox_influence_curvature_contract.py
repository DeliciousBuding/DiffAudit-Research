from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class WhiteboxInfluenceCurvatureContractTests(unittest.TestCase):
    def _artifact(self) -> dict:
        return {
            "schema": "diffaudit.whitebox_influence_curvature_feasibility.v1",
            "status": "cpu-contract-ready",
            "verdict": "selected-cpu-first",
            "admitted": False,
            "gpu_release": "none",
            "asset_probe": {
                "status": "ready",
                "repo_root": "workspaces/white-box/external/GSA",
                "assets_root": "workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1",
                "known_bad_default": {"repo_root": "external/GSA"},
            },
            "candidate_observable": {
                "required_raw_signal": "per-sample gradient vector",
                "minimum_implementation_scope": "selected-layer raw parameter gradients",
                "score_family": "g^T (F + lambda)^-1 g",
            },
            "distinctness_gate": {
                "must_not_be": [
                    "scalar diffusion reconstruction loss under a new name",
                    "plain gradient norm under a new name",
                    "per-parameter gradient-norm dump from _extract_gsa_gradients_with_fixed_mask",
                    "GSA loss-score threshold transfer",
                    "GSA loss-score Gaussian likelihood-ratio transfer",
                    "prior activation-subspace or channel-mask observable under a new name",
                ],
                "required_baselines": [
                    "scalar loss",
                    "raw gradient norm",
                    "GSA loss-score LR",
                    "activation-subspace or masked-observability packet when available",
                ],
                "release_rule": "GPU stays blocked until a CPU micro-board passes.",
            },
            "cpu_micro_board_contract": {
                "mode": "CPU-first",
                "target_sample_cap": {"member": 4, "nonmember": 4},
                "shadow_sample_cap_per_shadow": {"member": 4, "nonmember": 4},
                "required_outputs": [
                    "extractor provenance",
                    "feature dimensionality after truncation or projection",
                    "score direction",
                    "AUC",
                    "ASR",
                    "TPR@1%FPR",
                    "TPR@0.1%FPR",
                    "baseline comparison table",
                    "runtime seconds",
                    "failure reason if not runnable",
                ],
                "raw_artifact_policy": "do not persist raw gradient tensors by default",
                "promotion_floor": {
                    "heldout_shadow_folds_improving_over_baselines": 2,
                    "total_shadow_folds": 3,
                    "target_must_not_regress_all_low_fpr_fields": True,
                },
            },
            "blocked_claims": [
                "admitted Platform/Runtime white-box row",
                "new white-box family established",
                "GPU packet authorized",
                "paper-level benchmark",
                "conditional diffusion generalization",
            ],
            "evidence_docs": [
                "docs/evidence/post-secmi-next-lane-reselection-20260511.md",
                "docs/evidence/whitebox-influence-curvature-feasibility-scout-20260511.md",
            ],
        }

    def test_accepts_minimal_valid_contract(self) -> None:
        from scripts.validate_whitebox_influence_curvature_contract import validate

        self.assertEqual(validate(self._artifact()), [])

    def test_rejects_gpu_release(self) -> None:
        from scripts.validate_whitebox_influence_curvature_contract import validate

        artifact = self._artifact()
        artifact["gpu_release"] = "cuda-small-packet"

        self.assertIn("white-box influence/curvature scout must not release GPU", validate(artifact))

    def test_cli_validates_written_artifact(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=repo_root) as tmpdir:
            artifact_path = Path(tmpdir) / "contract.json"
            artifact_path.write_text(json.dumps(self._artifact(), indent=2), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/validate_whitebox_influence_curvature_contract.py",
                    "--artifact",
                    artifact_path.relative_to(repo_root).as_posix(),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=repo_root,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("OK", completed.stdout)


if __name__ == "__main__":
    unittest.main()
