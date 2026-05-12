import unittest

import numpy as np


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


if __name__ == "__main__":
    unittest.main()
