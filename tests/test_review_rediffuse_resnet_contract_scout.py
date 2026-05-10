from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


COLLABORATOR_ATTACK_SNIPPET = """
import torch
import resnet

def nns_attack(device, member_diffusion, member_sample, nonmember_diffusion, nonmember_sample, norm, train_portion):
    member_concat = member_diffusion
    nonmember_concat = nonmember_diffusion
    num_train = int(member_concat.size(0) * train_portion)
    train_member_concat = member_concat[:num_train]
    test_member_concat = member_concat[num_train:]
    train_nonmember_concat = nonmember_concat[:num_train]
    test_nonmember_concat = nonmember_concat[num_train:]
    model = resnet.ResNet18(num_channels=3 * 1, num_classes=1).to(device)
    optim = torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.9, weight_decay=5e-4)
    test_acc_best_ckpt = None
    test_acc_best = 0
    for epoch in range(15):
        logit = model(train_member_concat)
        label = torch.ones_like(logit)
        loss = ((logit - label) ** 2).mean()
        test_acc = 0.5
        if test_acc > test_acc_best:
            test_acc_best_ckpt = model.state_dict()
    member *= -1
    nonmember *= -1

def roc(member_scores, nonmember_scores):
    threshold = 0.0
    TP = (member_scores <= threshold).sum()
    return TP
"""


class ReDiffuseResNetContractScoutTests(unittest.TestCase):
    def test_detects_contract_mismatch_from_collaborator_attack_py(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=repo_root) as tmpdir:
            root = Path(tmpdir)
            bundle = root / "bundle"
            bundle.mkdir()
            (bundle / "attack.py").write_text(COLLABORATOR_ATTACK_SNIPPET, encoding="utf-8")
            output = root / "summary.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/review_rediffuse_resnet_contract_scout.py",
                    "--bundle-root",
                    bundle.relative_to(repo_root).as_posix(),
                    "--output",
                    output.relative_to(repo_root).as_posix(),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=repo_root,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["verdict"], "blocked-by-contract-mismatch")
            self.assertFalse(payload["release_gate"]["passed"])
            self.assertFalse(payload["release_gate"]["exact_replay_ready"])
            self.assertGreaterEqual(payload["release_gate"]["semantic_mismatch_count"], 2)
            self.assertTrue(payload["collaborator_features"]["best_checkpoint_counter_not_updated"])
            self.assertTrue(payload["collaborator_features"]["negates_scores_before_roc"])

    def test_missing_attack_py_returns_needs_assets(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=repo_root) as tmpdir:
            root = Path(tmpdir)
            bundle = root / "bundle"
            bundle.mkdir()
            output = root / "summary.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/review_rediffuse_resnet_contract_scout.py",
                    "--bundle-root",
                    bundle.relative_to(repo_root).as_posix(),
                    "--output",
                    output.relative_to(repo_root).as_posix(),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=repo_root,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["verdict"], "needs-assets")
            self.assertEqual(payload["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
