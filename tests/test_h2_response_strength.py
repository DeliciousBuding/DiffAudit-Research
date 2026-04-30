import unittest

import numpy as np


class H2ResponseStrengthTests(unittest.TestCase):
    def test_frequency_mask_full_is_identity(self) -> None:
        from diffaudit.attacks.h2_response_strength import apply_frequency_mask, build_frequency_mask

        images = np.arange(2 * 3 * 4 * 4, dtype=np.float32).reshape(2, 3, 4, 4)
        mask = build_frequency_mask(4, 4, "full")

        np.testing.assert_allclose(apply_frequency_mask(images, mask), images)

    def test_lowpass_min_distances_shape(self) -> None:
        from diffaudit.attacks.h2_response_strength import compute_lowpass_min_distances

        inputs = np.zeros((3, 1, 4, 4), dtype=np.float32)
        responses = np.zeros((3, 2, 2, 1, 4, 4), dtype=np.float32)
        responses[:, 0, 0] = 1.0
        responses[:, 0, 1] = 0.5
        responses[:, 1, 0] = 0.25
        responses[:, 1, 1] = 0.125

        distances = compute_lowpass_min_distances(inputs, responses, cutoff=1.0)

        self.assertEqual(distances.shape, (3, 2))
        np.testing.assert_allclose(distances[:, 0], 0.5)
        np.testing.assert_allclose(distances[:, 1], 0.125)

    def test_h2_simple_scores_selects_low_fpr_candidate(self) -> None:
        from diffaudit.attacks.h2_response_strength import evaluate_h2_simple_scores

        labels = np.asarray([1, 1, 1, 1, 0, 0, 0, 0], dtype=np.int64)
        min_distances = np.asarray(
            [
                [0.1, 0.4],
                [0.2, 0.5],
                [0.3, 0.6],
                [0.4, 0.7],
                [0.5, 0.1],
                [0.6, 0.2],
                [0.7, 0.3],
                [0.8, 0.4],
            ],
            dtype=np.float32,
        )

        result = evaluate_h2_simple_scores(
            labels,
            min_distances,
            np.asarray([40, 80], dtype=np.int64),
            seed=7,
            bootstrap_iters=0,
        )

        self.assertEqual(result["best_by_auc"]["name"], "single_timestep_40")
        self.assertGreaterEqual(result["best_by_low_fpr"]["metrics"]["tpr_at_1pct_fpr"], 0.0)

    def test_logistic_holdout_covers_every_sample(self) -> None:
        from diffaudit.attacks.h2_response_strength import evaluate_logistic_holdout

        labels = np.asarray([1] * 6 + [0] * 6, dtype=np.int64)
        member_features = np.stack([np.linspace(0.0, 0.5, 6), np.linspace(0.2, 0.7, 6)], axis=1)
        nonmember_features = np.stack([np.linspace(1.5, 2.0, 6), np.linspace(1.7, 2.2, 6)], axis=1)
        features = np.concatenate([member_features, nonmember_features], axis=0).astype(np.float32)
        features = -features

        result = evaluate_logistic_holdout(labels, features, seed=11, repeats=2, bootstrap_iters=0)

        self.assertGreaterEqual(result["aggregate_metrics"]["auc"], 0.9)
        self.assertGreaterEqual(result["prediction_count"]["min"], 1)


if __name__ == "__main__":
    unittest.main()

