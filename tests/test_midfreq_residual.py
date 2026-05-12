import unittest

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


if __name__ == "__main__":
    unittest.main()
