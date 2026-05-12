import unittest

import numpy as np


class ResponseSeedStabilityTests(unittest.TestCase):
    def test_mean_pairwise_cosine_scores_identical_embeddings_as_stable(self) -> None:
        from diffaudit.attacks.response_seed_stability import mean_pairwise_cosine

        embeddings = np.asarray(
            [
                [1.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
            ],
            dtype=float,
        )

        self.assertAlmostEqual(mean_pairwise_cosine(embeddings), 1.0 / 3.0)

    def test_summarize_stability_reports_auc_and_low_fpr_recovery(self) -> None:
        from diffaudit.attacks.response_seed_stability import summarize_stability_scores

        labels = np.asarray([1, 1, 0, 0], dtype=int)
        scores = np.asarray([0.95, 0.85, 0.20, 0.10], dtype=float)

        metrics = summarize_stability_scores(labels, scores)

        self.assertEqual(metrics["auc"], 1.0)
        self.assertEqual(metrics["asr"], 1.0)
        self.assertEqual(metrics["tpr_at_1pct_fpr"], 1.0)
        self.assertEqual(metrics["tpr_at_0_1pct_fpr"], 1.0)


if __name__ == "__main__":
    unittest.main()
