import importlib.util
import unittest
from pathlib import Path

import numpy as np
import torch


def _load_script_module():
    script_path = Path("scripts/run_fashion_mnist_score_jacobian_sensitivity.py")
    spec = importlib.util.spec_from_file_location(
        "run_fashion_mnist_score_jacobian_sensitivity", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FashionMnistScoreJacobianSensitivityTests(unittest.TestCase):
    def test_directional_sensitivity_prefers_smaller_prediction_change(self) -> None:
        module = _load_script_module()
        base_prediction = torch.zeros((2, 1, 2, 2))
        perturbed_prediction = torch.tensor(
            [
                [[[0.25, 0.0], [0.0, 0.0]]],
                [[[0.75, 0.0], [0.0, 0.0]]],
            ]
        )

        scores = module._score_jacobian_sensitivity_scores(
            base_prediction,
            perturbed_prediction,
            perturbation_scale=0.5,
            p_norm=2,
        )

        self.assertEqual(scores.shape, (2,))
        self.assertGreater(scores[0], scores[1])
        self.assertEqual(scores.tolist(), [-0.5, -1.5])

    def test_summary_reports_directional_derivative_means_and_verdict(self) -> None:
        module = _load_script_module()
        labels = np.asarray([1, 1, 0, 0], dtype=int)
        weak_scores = np.asarray([0.30, 0.20, 0.40, 0.10], dtype=float)

        metrics = module._summarize_scores(labels, weak_scores)
        verdict = module._verdict_from_metrics(metrics)

        self.assertAlmostEqual(metrics["auc"], 0.5)
        self.assertEqual(metrics["member_directional_derivative_norm_mean"], -0.25)
        self.assertEqual(metrics["nonmember_directional_derivative_norm_mean"], -0.25)
        self.assertEqual(
            verdict,
            "weak; close Fashion-MNIST score-Jacobian sensitivity scout",
        )


if __name__ == "__main__":
    unittest.main()
