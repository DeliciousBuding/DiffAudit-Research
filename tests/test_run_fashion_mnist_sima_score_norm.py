import importlib.util
import unittest
from pathlib import Path

import numpy as np
import torch


def _load_script_module():
    script_path = Path("scripts/run_fashion_mnist_sima_score_norm.py")
    spec = importlib.util.spec_from_file_location("run_fashion_mnist_sima_score_norm", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FashionMnistSimaScoreNormTests(unittest.TestCase):
    def test_score_from_prediction_norm_prefers_smaller_norms(self) -> None:
        module = _load_script_module()
        eps_prediction = torch.tensor(
            [
                [[[1.0, 0.0], [0.0, 0.0]]],
                [[[2.0, 0.0], [0.0, 0.0]]],
            ]
        )

        scores = module._sima_scores_from_prediction(eps_prediction, p_norm=2)

        self.assertEqual(scores.shape, (2,))
        self.assertGreater(scores[0], scores[1])
        self.assertEqual(scores.tolist(), [-1.0, -2.0])

    def test_summary_reports_strict_tail_and_closing_verdict(self) -> None:
        module = _load_script_module()
        labels = np.asarray([1, 1, 0, 0], dtype=int)
        weak_scores = np.asarray([0.30, 0.20, 0.40, 0.10], dtype=float)

        metrics = module._summarize_scores(labels, weak_scores)
        verdict = module._verdict_from_metrics(metrics)

        self.assertAlmostEqual(metrics["auc"], 0.5)
        self.assertIn("tpr_at_0_1pct_fpr", metrics)
        self.assertEqual(verdict, "weak; close Fashion-MNIST SimA score-norm scout")


if __name__ == "__main__":
    unittest.main()
