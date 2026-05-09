import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import torch

from tests.helpers import make_fake_cifar10

from diffaudit.attacks.rediffuse import default_bundle_root, default_checkpoint_path


def local_rediffuse_assets_ready() -> bool:
    return default_bundle_root().exists() and default_checkpoint_path().exists()


class ReDiffuseAdapterUnitTests(unittest.TestCase):
    def test_cli_rediffuse_runtime_smoke_defaults_cpu_first(self) -> None:
        from diffaudit.cli import build_parser

        args = build_parser().parse_args(["run-rediffuse-runtime-smoke", "--workspace", "tmp"])

        self.assertEqual(args.device, "cpu")
        self.assertEqual(args.scoring_mode, "first_step_distance_mean")

    def test_resnet_scorer_keeps_member_high_orientation(self) -> None:
        from diffaudit.attacks.rediffuse_adapter import _score_resnet_scorer

        class MeanScorer(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.bias = torch.nn.Parameter(torch.zeros(1))

            def forward(self, data: torch.Tensor) -> torch.Tensor:
                return data.flatten(1).mean(dim=1, keepdim=True) + self.bias

        resnet_module = SimpleNamespace(ResNet18=lambda num_channels, num_classes: MeanScorer())
        member_features = torch.ones(6, 3, 32, 32)
        nonmember_features = torch.zeros(6, 3, 32, 32)

        member_scores, nonmember_scores, scorer_info = _score_resnet_scorer(
            resnet_module,
            member_features=member_features,
            nonmember_features=nonmember_features,
            device="cpu",
            train_portion=0.5,
            epochs=1,
            lr=0.001,
            batch_size=4,
        )

        self.assertEqual(member_scores.shape, nonmember_scores.shape)
        self.assertGreater(float(member_scores.mean()), float(nonmember_scores.mean()))
        self.assertEqual(scorer_info["resnet_train_count_per_split"], 3)
        self.assertEqual(scorer_info["resnet_test_count_per_split"], 3)


@unittest.skipUnless(local_rediffuse_assets_ready(), "local ReDiffuse collaborator assets are not present")
class ReDiffuseAdapterTests(unittest.TestCase):
    def test_runtime_probe_loads_model_and_attacker(self) -> None:
        from diffaudit.attacks.rediffuse_adapter import probe_rediffuse_runtime

        exit_code, payload = probe_rediffuse_runtime(
            device="cpu",
            attack_num=1,
            interval=1,
            average=1,
            k=1,
        )

        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "ready")
        self.assertTrue(payload["checks"]["modules_loaded"])
        self.assertTrue(payload["checks"]["model_loaded"])
        self.assertTrue(payload["checks"]["attacker_instantiated"])
        self.assertEqual(payload["load_info"]["missing_keys"], 0)
        self.assertEqual(payload["load_info"]["unexpected_keys"], 0)
        self.assertEqual(payload["preview"]["intermediates_shape"], [1, 1, 3, 32, 32])

    def test_cli_runtime_probe_rediffuse_reports_ready(self) -> None:
        from diffaudit.cli import main

        stdout = StringIO()
        with redirect_stdout(stdout):
            exit_code = main(
                [
                    "runtime-probe-rediffuse",
                    "--device",
                    "cpu",
                    "--attack-num",
                    "1",
                    "--interval",
                    "1",
                    "--average",
                    "1",
                    "--k",
                    "1",
                ]
            )

        payload = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "ready")
        self.assertTrue(payload["checks"]["preview_forward"])

    def test_run_rediffuse_runtime_smoke_writes_summary(self) -> None:
        from diffaudit.attacks.rediffuse_adapter import run_rediffuse_runtime_smoke

        FakeCIFAR10 = make_fake_cifar10((16, 24, 32, 40))
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir) / "rediffuse-smoke"
            with patch("torchvision.datasets.CIFAR10", FakeCIFAR10):
                with patch(
                    "diffaudit.attacks.rediffuse_adapter._load_split_indices",
                    return_value=([0, 1], [2, 3]),
                ):
                    payload = run_rediffuse_runtime_smoke(
                        workspace=workspace,
                        dataset_root=tmpdir,
                        device="cpu",
                        max_samples=2,
                        batch_size=1,
                        attack_num=1,
                        interval=1,
                        average=1,
                        k=1,
                    )

            summary_path = workspace / "summary.json"
            scores_path = workspace / "scores.json"
            self.assertTrue(summary_path.exists())
            self.assertTrue(scores_path.exists())

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["mode"], "runtime-smoke")
        self.assertEqual(payload["sample_count_per_split"], 2)
        self.assertIn("auc", payload["metrics"])
        self.assertIn("tpr_at_1pct_fpr", payload["metrics"])
        self.assertEqual(payload["runtime"]["scoring_mode"], "first_step_distance_mean")

    def test_run_rediffuse_runtime_smoke_supports_resnet_scorer(self) -> None:
        from diffaudit.attacks.rediffuse_adapter import run_rediffuse_runtime_smoke

        FakeCIFAR10 = make_fake_cifar10((16, 24, 32, 40, 48, 56, 64, 72))
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir) / "rediffuse-resnet-smoke"
            with patch("torchvision.datasets.CIFAR10", FakeCIFAR10):
                with patch(
                    "diffaudit.attacks.rediffuse_adapter._load_split_indices",
                    return_value=([0, 1, 2, 3], [4, 5, 6, 7]),
                ):
                    payload = run_rediffuse_runtime_smoke(
                        workspace=workspace,
                        dataset_root=tmpdir,
                        device="cpu",
                        max_samples=4,
                        batch_size=2,
                        attack_num=1,
                        interval=1,
                        average=1,
                        k=1,
                        scoring_mode="resnet",
                        scorer_train_portion=0.5,
                        scorer_epochs=1,
                        scorer_batch_size=2,
                    )

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["runtime"]["scoring_mode"], "resnet")
        self.assertEqual(payload["runtime"]["resnet_train_count_per_split"], 2)
        self.assertEqual(payload["runtime"]["resnet_test_count_per_split"], 2)
        self.assertIn("auc", payload["metrics"])


if __name__ == "__main__":
    unittest.main()
