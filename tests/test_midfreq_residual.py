import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import torch


class MidFrequencyResidualTests(unittest.TestCase):
    def test_bandpass_residual_l2_returns_per_sample_distances(self) -> None:
        from diffaudit.attacks.midfreq_residual import bandpass_residual_l2

        x_t = np.zeros((3, 1, 8, 8), dtype=np.float32)
        tilde_x_t = np.zeros_like(x_t)
        tilde_x_t[0, :, 2:6, 2:6] = 0.1
        tilde_x_t[1, :, 2:6, 2:6] = 0.2
        tilde_x_t[2, :, 2:6, 2:6] = 0.4

        distances = bandpass_residual_l2(x_t, tilde_x_t, cutoff=0.25, cutoff_high=0.75)

        self.assertEqual(distances.shape, (3,))
        self.assertLess(float(distances[0]), float(distances[1]))
        self.assertLess(float(distances[1]), float(distances[2]))

    def test_midfreq_member_scores_orients_lower_residual_as_member(self) -> None:
        from diffaudit.attacks.midfreq_residual import midfreq_member_scores

        x_t = np.zeros((2, 1, 8, 8), dtype=np.float32)
        tilde_x_t = np.zeros_like(x_t)
        tilde_x_t[0, :, 1:7, 1:7] = 0.1
        tilde_x_t[1, :, 1:7, 1:7] = 0.5

        scores = midfreq_member_scores(x_t, tilde_x_t, cutoff=0.25, cutoff_high=0.75)

        self.assertGreater(float(scores[0]), float(scores[1]))

    def test_summarize_midfreq_packet_reports_standard_metrics(self) -> None:
        from diffaudit.attacks.midfreq_residual import summarize_midfreq_packet

        labels = np.asarray([1, 1, 0, 0], dtype=np.int64)
        x_t = np.zeros((4, 1, 8, 8), dtype=np.float32)
        tilde_x_t = np.zeros_like(x_t)
        tilde_x_t[0, :, 2:6, 2:6] = 0.05
        tilde_x_t[1, :, 2:6, 2:6] = 0.10
        tilde_x_t[2, :, 2:6, 2:6] = 0.40
        tilde_x_t[3, :, 2:6, 2:6] = 0.50

        summary = summarize_midfreq_packet(
            labels,
            x_t,
            tilde_x_t,
            cutoff=0.25,
            cutoff_high=0.75,
            metadata={"timestep": 80},
        )

        self.assertEqual(summary["sample_count"], 4)
        self.assertEqual(summary["member_count"], 2)
        self.assertEqual(summary["nonmember_count"], 2)
        self.assertEqual(summary["score_orientation"], "negative_bandpass_l2_higher_is_member")
        self.assertEqual(summary["metrics"]["auc"], 1.0)
        self.assertEqual(summary["metadata"]["timestep"], 80)
        self.assertGreater(summary["metrics"]["member_score_mean"], summary["metrics"]["nonmember_score_mean"])

    def test_invalid_band_is_rejected(self) -> None:
        from diffaudit.attacks.midfreq_residual import bandpass_residual_l2

        x_t = np.zeros((1, 1, 8, 8), dtype=np.float32)
        with self.assertRaises(ValueError):
            bandpass_residual_l2(x_t, x_t, cutoff=0.8, cutoff_high=0.2)
        with self.assertRaises(ValueError):
            bandpass_residual_l2(x_t, x_t, cutoff=float("nan"), cutoff_high=0.5)

    def test_single_class_packet_is_rejected(self) -> None:
        from diffaudit.attacks.midfreq_residual import summarize_midfreq_packet

        labels = np.asarray([1, 1], dtype=np.int64)
        x_t = np.zeros((2, 1, 8, 8), dtype=np.float32)

        with self.assertRaises(ValueError):
            summarize_midfreq_packet(labels, x_t, x_t)

    def test_one_step_same_noise_state_returns_matched_shapes(self) -> None:
        from diffaudit.attacks.h2_response_strength import build_alpha_bars
        from diffaudit.attacks.midfreq_residual import one_step_same_noise_state

        class ZeroEps(torch.nn.Module):
            def forward(self, x, t):  # type: ignore[no-untyped-def]
                return torch.zeros_like(x)

        x0 = torch.full((2, 1, 8, 8), 0.5, dtype=torch.float32)
        alpha_bars = build_alpha_bars("cpu", timesteps=100)
        generator = torch.Generator(device="cpu")
        generator.manual_seed(123)

        x_t, tilde_x_t = one_step_same_noise_state(
            ZeroEps(),
            x0,
            timestep=10,
            alpha_bars=alpha_bars,
            generator=generator,
            device="cpu",
        )

        self.assertEqual(tuple(x_t.shape), (2, 1, 8, 8))
        self.assertEqual(tuple(tilde_x_t.shape), (2, 1, 8, 8))
        self.assertTrue(torch.isfinite(x_t).all())
        self.assertTrue(torch.isfinite(tilde_x_t).all())

    def test_collect_midfreq_residual_states_is_deterministic(self) -> None:
        from diffaudit.attacks.h2_response_strength import build_alpha_bars
        from diffaudit.attacks.midfreq_residual import collect_midfreq_residual_states

        class ZeroEps(torch.nn.Module):
            def forward(self, x, t):  # type: ignore[no-untyped-def]
                return torch.zeros_like(x)

        dataset = torch.utils.data.TensorDataset(
            torch.full((3, 1, 8, 8), 0.5, dtype=torch.float32),
            torch.zeros(3, dtype=torch.long),
        )
        loader = torch.utils.data.DataLoader(dataset, batch_size=2, shuffle=False)
        alpha_bars = build_alpha_bars("cpu", timesteps=100)

        _inputs_a, x_t_a, tilde_a = collect_midfreq_residual_states(
            ZeroEps(),
            loader,
            device="cpu",
            alpha_bars=alpha_bars,
            timestep=10,
            seed=99,
        )
        _inputs_b, x_t_b, tilde_b = collect_midfreq_residual_states(
            ZeroEps(),
            loader,
            device="cpu",
            alpha_bars=alpha_bars,
            timestep=10,
            seed=99,
        )

        np.testing.assert_allclose(x_t_a, x_t_b)
        np.testing.assert_allclose(tilde_a, tilde_b)
        self.assertEqual(x_t_a.shape, (3, 1, 8, 8))
        self.assertEqual(tilde_a.shape, (3, 1, 8, 8))

    def test_tiny_cache_runner_writes_required_schema(self) -> None:
        from diffaudit.attacks.midfreq_residual import run_midfreq_residual_tiny_cache

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir) / "midfreq-tiny"
            payload = run_midfreq_residual_tiny_cache(
                workspace=workspace,
                member_count=2,
                nonmember_count=2,
                batch_size=2,
                image_size=8,
                channels=1,
                seed=7,
            )

            self.assertEqual(payload["status"], "ready")
            self.assertFalse(payload["packet"]["gpu_released"])
            self.assertTrue((workspace / "summary.json").exists())
            self.assertTrue((workspace / "residual-cache.npz").exists())
            with np.load(workspace / "residual-cache.npz") as cache:
                for field in payload["cache_schema"]["fields"]:
                    self.assertIn(field, cache.files)
                self.assertEqual(cache["labels"].tolist(), [1, 1, 0, 0])
                self.assertEqual(tuple(cache["x_t"].shape), (4, 1, 8, 8))
                self.assertEqual(tuple(cache["tilde_x_t"].shape), (4, 1, 8, 8))
                self.assertEqual(tuple(cache["bandpass_l2"].shape), (4,))

    def test_tiny_cache_runner_rejects_non_tiny_packets(self) -> None:
        from diffaudit.attacks.midfreq_residual import run_midfreq_residual_tiny_cache

        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                run_midfreq_residual_tiny_cache(
                    workspace=tmpdir,
                    member_count=9,
                    nonmember_count=1,
                )

    def test_real_asset_preflight_writes_required_schema_with_stubbed_assets(self) -> None:
        from diffaudit.attacks.midfreq_residual import run_midfreq_residual_real_asset_preflight
        from tests.helpers import make_fake_cifar10

        class ZeroEps(torch.nn.Module):
            def forward(self, x, t):  # type: ignore[no-untyped-def]
                del t
                return torch.zeros_like(x)

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            split_path = root / "CIFAR10_train_ratio0.5.npz"
            np.savez(
                split_path,
                mia_train_idxs=np.asarray([0, 1, 2, 3], dtype=np.int64),
                mia_eval_idxs=np.asarray([4, 5, 6, 7], dtype=np.int64),
            )
            asset_probe = {
                "status": "ready",
                "checks": {
                    "bundle_root": True,
                    "required_files": True,
                    "split_hash": True,
                    "checkpoint": True,
                    "checkpoint_has_ema_model": True,
                    "dataset_root": True,
                },
                "paths": {
                    "bundle_root": str(root / "bundle"),
                    "checkpoint": str(root / "checkpoint.pt"),
                    "dataset_root": str(root / "datasets"),
                    "split": str(split_path),
                },
                "provenance": {"source": "unit-test"},
            }
            fake_modules = SimpleNamespace(model_unet=SimpleNamespace())
            FakeCIFAR10 = make_fake_cifar10((16, 32, 48, 64, 80, 96, 112, 128))
            workspace = root / "midfreq-real"

            with (
                patch("diffaudit.attacks.rediffuse.probe_rediffuse_assets", return_value=asset_probe),
                patch("diffaudit.attacks.rediffuse_adapter.load_rediffuse_modules", return_value=fake_modules),
                patch(
                    "diffaudit.attacks.rediffuse_adapter.load_rediffuse_model",
                    return_value=(ZeroEps(), {"weights_key": "ema_model", "checkpoint_step": 750000}),
                ),
                patch("torchvision.datasets.CIFAR10", FakeCIFAR10),
            ):
                payload = run_midfreq_residual_real_asset_preflight(
                    workspace=workspace,
                    sample_count_per_split=2,
                    batch_size=1,
                    timestep=10,
                    seed=5,
                )

            self.assertEqual(payload["status"], "ready")
            self.assertEqual(payload["verdict"], "real-asset-tiny-cache-ready")
            self.assertFalse(payload["packet"]["gpu_released"])
            self.assertFalse(payload["packet"]["synthetic"])
            self.assertEqual(payload["runtime"]["selected_member_indices"], [0, 1])
            self.assertEqual(payload["runtime"]["selected_nonmember_indices"], [4, 5])
            with np.load(workspace / "residual-cache.npz") as cache:
                for field in payload["cache_schema"]["fields"]:
                    self.assertIn(field, cache.files)
                self.assertEqual(cache["labels"].tolist(), [1, 1, 0, 0])
                self.assertEqual(cache["member_indices"].tolist(), [0, 1])
                self.assertEqual(cache["nonmember_indices"].tolist(), [4, 5])
                self.assertEqual(tuple(cache["x_t"].shape), (4, 3, 32, 32))

    def test_real_asset_preflight_writes_blocked_summary_when_assets_missing(self) -> None:
        from diffaudit.attacks.midfreq_residual import run_midfreq_residual_real_asset_preflight

        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir) / "blocked"
            with patch(
                "diffaudit.attacks.rediffuse.probe_rediffuse_assets",
                return_value={
                    "status": "blocked",
                    "checks": {"dataset_root": False},
                    "paths": {},
                    "missing": ["dataset"],
                },
            ):
                payload = run_midfreq_residual_real_asset_preflight(workspace=workspace)

            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["verdict"], "needs-assets")
            self.assertEqual(payload["paths"]["workspace"], str(workspace))
            self.assertIsNone(payload["paths"]["cache"])
            self.assertTrue((workspace / "summary.json").exists())

    def test_sign_check_reuses_real_asset_runner_and_classifies(self) -> None:
        from diffaudit.attacks.midfreq_residual import run_midfreq_residual_sign_check
        from tests.helpers import make_fake_cifar10

        class ZeroEps(torch.nn.Module):
            def forward(self, x, t):  # type: ignore[no-untyped-def]
                del t
                return torch.zeros_like(x)

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            split_path = root / "CIFAR10_train_ratio0.5.npz"
            np.savez(
                split_path,
                mia_train_idxs=np.asarray([0, 1, 2, 3], dtype=np.int64),
                mia_eval_idxs=np.asarray([4, 5, 6, 7], dtype=np.int64),
            )
            asset_probe = {
                "status": "ready",
                "checks": {
                    "bundle_root": True,
                    "required_files": True,
                    "split_hash": True,
                    "checkpoint": True,
                    "checkpoint_has_ema_model": True,
                    "dataset_root": True,
                },
                "paths": {
                    "bundle_root": str(root / "bundle"),
                    "checkpoint": str(root / "checkpoint.pt"),
                    "dataset_root": str(root / "datasets"),
                    "split": str(split_path),
                },
                "provenance": {"source": "unit-test"},
            }
            fake_modules = SimpleNamespace(model_unet=SimpleNamespace())
            FakeCIFAR10 = make_fake_cifar10((16, 32, 48, 64, 80, 96, 112, 128))

            with (
                patch("diffaudit.attacks.rediffuse.probe_rediffuse_assets", return_value=asset_probe),
                patch("diffaudit.attacks.rediffuse_adapter.load_rediffuse_modules", return_value=fake_modules),
                patch(
                    "diffaudit.attacks.rediffuse_adapter.load_rediffuse_model",
                    return_value=(ZeroEps(), {"weights_key": "ema_model", "checkpoint_step": 750000}),
                ),
                patch("torchvision.datasets.CIFAR10", FakeCIFAR10),
            ):
                payload = run_midfreq_residual_sign_check(
                    workspace=root / "midfreq-sign",
                    sample_count_per_split=2,
                    batch_size=1,
                    timestep=10,
                    seed=5,
                    device="cpu",
                )

            self.assertEqual(payload["status"], "ready")
            self.assertEqual(payload["mode"], "bounded-sign-check")
            self.assertIn(payload["verdict"], {"candidate-only", "negative-but-useful"})
            self.assertEqual(payload["packet"]["sample_count"], 4)
            self.assertFalse(payload["packet"]["gpu_released"])
            self.assertIn("release_gate", payload["decision"])

    def test_sign_check_rejects_over_cap_packets(self) -> None:
        from diffaudit.attacks.midfreq_residual import run_midfreq_residual_sign_check

        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                run_midfreq_residual_sign_check(
                    workspace=tmpdir,
                    sample_count_per_split=65,
                    device="cpu",
                )

    def test_cli_parser_accepts_midfreq_tiny_cache_command(self) -> None:
        from diffaudit.cli import build_parser

        args = build_parser().parse_args(
            [
                "run-midfreq-residual-tiny-cache",
                "--workspace",
                "tmp/midfreq",
                "--member-count",
                "2",
                "--nonmember-count",
                "2",
            ]
        )

        self.assertEqual(args.command, "run-midfreq-residual-tiny-cache")
        self.assertEqual(args.member_count, 2)
        self.assertEqual(args.nonmember_count, 2)

    def test_cli_parser_accepts_midfreq_real_asset_preflight_command(self) -> None:
        from diffaudit.cli import build_parser

        args = build_parser().parse_args(
            [
                "run-midfreq-residual-real-asset-preflight",
                "--workspace",
                "tmp/midfreq-real",
                "--sample-count-per-split",
                "2",
            ]
        )

        self.assertEqual(args.command, "run-midfreq-residual-real-asset-preflight")
        self.assertEqual(args.sample_count_per_split, 2)

    def test_cli_parser_accepts_midfreq_sign_check_command(self) -> None:
        from diffaudit.cli import build_parser

        args = build_parser().parse_args(
            [
                "run-midfreq-residual-sign-check",
                "--workspace",
                "tmp/midfreq-sign",
                "--sample-count-per-split",
                "16",
            ]
        )

        self.assertEqual(args.command, "run-midfreq-residual-sign-check")
        self.assertEqual(args.sample_count_per_split, 16)
        self.assertEqual(args.device, "cuda")


if __name__ == "__main__":
    unittest.main()
