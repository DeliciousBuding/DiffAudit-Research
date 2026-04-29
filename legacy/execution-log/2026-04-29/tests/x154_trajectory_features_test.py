import unittest
import importlib.util
from pathlib import Path

import torch


def _load_archived_script():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "run_x154_per_timestep_activation_trajectory_gpu_scout.py"
    spec = importlib.util.spec_from_file_location("archived_x154", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load archived script: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class X154TrajectoryFeatureTests(unittest.TestCase):
    def test_linear_slope_feature_keeps_channelwise_trajectory_signal(self) -> None:
        _build_trajectory_feature = _load_archived_script()._build_trajectory_feature

        trajectories = torch.tensor(
            [
                [[0.0, 3.0], [1.0, 2.0], [2.0, 1.0], [3.0, 0.0]],
                [[1.0, 4.0], [2.0, 3.0], [3.0, 2.0], [4.0, 1.0]],
            ]
        )

        slope = _build_trajectory_feature(trajectories, "linear_slope")

        self.assertTrue(torch.allclose(slope[:, 0], torch.tensor([3.0, 3.0]), atol=1e-6))
        self.assertTrue(torch.allclose(slope[:, 1], torch.tensor([-3.0, -3.0]), atol=1e-6))

    def test_feature_selector_uses_validation_not_holdout_for_choice(self) -> None:
        _select_trajectory_feature = _load_archived_script()._select_trajectory_feature

        def split(matrix: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
            return matrix[:2], matrix[2:4], matrix[4:]

        trajectory_member = torch.tensor(
            [
                [3.0, 0.0],
                [3.2, 0.0],
                [2.5, 0.0],
                [2.6, 0.0],
                [0.0, 10.0],
                [0.0, 11.0],
            ]
        )
        trajectory_nonmember = torch.zeros((6, 2))
        holdout_only_member = torch.tensor(
            [
                [0.0, 3.0],
                [0.0, 3.0],
                [0.0, -3.0],
                [0.0, -3.0],
                [0.0, 20.0],
                [0.0, 21.0],
            ]
        )
        holdout_only_nonmember = torch.zeros((6, 2))

        selected = _select_trajectory_feature(
            feature_matrices={
                "trajectory": {
                    "member": split(trajectory_member),
                    "nonmember": split(trajectory_nonmember),
                },
                "holdout_only": {
                    "member": split(holdout_only_member),
                    "nonmember": split(holdout_only_nonmember),
                },
            },
            feature_names=["trajectory", "holdout_only"],
            top_k=1,
            candidate_multiplier=2,
        )

        self.assertEqual(selected["selected"]["feature"], "trajectory")


if __name__ == "__main__":
    unittest.main()
