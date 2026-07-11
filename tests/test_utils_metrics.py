import unittest

import numpy as np


class MetricsUtilsTests(unittest.TestCase):
    def test_rankdata_uses_zero_indexed_average_tie_ranks(self) -> None:
        from diffaudit.utils.metrics import rankdata

        self.assertEqual(rankdata(np.asarray([3.0, 1.0, 1.0, 5.0])).tolist(), [2.0, 0.5, 0.5, 3.0])

    def test_orient_scores_by_labels_rejects_single_class_labels(self) -> None:
        from diffaudit.utils.metrics import orient_scores_by_labels

        with self.assertRaisesRegex(ValueError, "one member .* one nonmember"):
            orient_scores_by_labels(np.asarray([0.1, 0.2]), np.asarray([1, 1]))

    def test_metric_bundle_rejects_single_class_labels(self) -> None:
        from diffaudit.utils.metrics import metric_bundle

        with self.assertRaisesRegex(ValueError, "one member .* one nonmember"):
            metric_bundle(np.asarray([0.1, 0.2]), np.asarray([0, 0]))

    def test_threshold_metrics_grid_reports_strict_tail_metric(self) -> None:
        from diffaudit.utils.metrics import threshold_metrics_grid

        labels = np.asarray([1, 1, 0, 0])
        scores = np.asarray([0.9, 0.8, 0.2, 0.1])

        metrics = threshold_metrics_grid(labels, scores)

        self.assertIn("tpr_at_0_1pct_fpr", metrics)
        self.assertEqual(metrics["tpr_at_0_1pct_fpr"], 1.0)

    def test_auc_groups_tied_scores_at_the_group_endpoint(self) -> None:
        from diffaudit.utils.metrics import auc_score

        scores = np.asarray([3.0, 2.0, 2.0, 1.0])
        labels = np.asarray([1, 1, 1, 0])

        self.assertEqual(auc_score(scores, labels), 1.0)

    def test_constant_scores_are_chance_auc_and_zero_tpr_below_one_percent_fpr(self) -> None:
        from diffaudit.utils.metrics import auc_score, tpr_at_fpr

        scores = np.zeros(1024, dtype=float)
        labels = np.asarray([0, 1] * 512)

        self.assertEqual(auc_score(scores, labels), 0.5)
        self.assertEqual(tpr_at_fpr(scores, labels, 0.01), 0.0)


if __name__ == "__main__":
    unittest.main()
