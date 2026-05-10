from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import torch

from diffaudit.attacks.rediffuse import EXPECTED_CIFAR10_SPLIT_SHA256


class ReviewReDiffuseCheckpointPortabilityGateTests(unittest.TestCase):
    def _write_checkpoint(self, path: Path, *, step: int, key_count: int = 2) -> None:
        state = {f"layer.{index}": torch.tensor([float(index)]) for index in range(key_count)}
        torch.save({"step": step, "ema_model": state, "x_T": torch.zeros(1, 3, 32, 32)}, path)

    def test_blocks_gpu_even_when_metadata_is_compatible(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=repo_root) as tmpdir:
            root = Path(tmpdir)
            collaborator = root / "750k.pt"
            comparison = root / "800k.pt"
            split = root / "split.npz"
            output = root / "summary.json"
            self._write_checkpoint(collaborator, step=750000)
            self._write_checkpoint(comparison, step=800000)
            np.savez(split, mia_train_idxs=np.array([0, 1]), mia_eval_idxs=np.array([2, 3]))

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/review_rediffuse_checkpoint_portability_gate.py",
                    "--collaborator-checkpoint",
                    collaborator.relative_to(repo_root).as_posix(),
                    "--comparison-checkpoint",
                    comparison.relative_to(repo_root).as_posix(),
                    "--split-path",
                    split.relative_to(repo_root).as_posix(),
                    "--output",
                    output.relative_to(repo_root).as_posix(),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=repo_root,
            )
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(payload["verdict"], "blocked-by-scoring-contract")
        self.assertTrue(payload["release_gate"]["architecture_compatible"])
        self.assertFalse(payload["release_gate"]["scoring_contract_resolved"])
        self.assertFalse(payload["release_gate"]["passed"])

    def test_records_expected_split_hash_constant(self) -> None:
        self.assertEqual(
            EXPECTED_CIFAR10_SPLIT_SHA256,
            "aca922ecee25ef00dc6b6377ebaf7875dfcc77c2cdfe27c873b26a65134aa0c0",
        )


if __name__ == "__main__":
    unittest.main()
