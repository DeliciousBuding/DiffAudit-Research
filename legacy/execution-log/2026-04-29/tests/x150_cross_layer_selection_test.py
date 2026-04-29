import unittest
import importlib.util
from pathlib import Path

import torch


def _load_archived_script():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "run_x150_cross_layer_activation_stability_gpu_scout.py"
    spec = importlib.util.spec_from_file_location("archived_x150", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load archived script: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class X150CrossLayerSelectionTests(unittest.TestCase):
    def test_cross_layer_selector_requires_comparator_support(self) -> None:
        _select_cross_layer_stable_subspace = _load_archived_script()._select_cross_layer_stable_subspace

        primary_selector_member = torch.tensor(
            [
                [1.0, 0.9, 0.8, 0.1],
                [1.1, 1.0, 0.9, 0.2],
            ]
        )
        primary_selector_nonmember = torch.zeros((2, 4))
        primary_validation_member = torch.tensor(
            [
                [0.8, 0.7, 0.6, 0.0],
                [0.9, 0.8, 0.7, 0.0],
            ]
        )
        primary_validation_nonmember = torch.zeros((2, 4))
        q_validation_member = torch.tensor(
            [
                [0.4, -0.2, -0.1, 0.0],
                [0.5, -0.2, -0.1, 0.0],
            ]
        )
        k_validation_member = torch.tensor(
            [
                [-0.1, 0.5, -0.1, 0.0],
                [-0.1, 0.6, -0.1, 0.0],
            ]
        )

        selected = _select_cross_layer_stable_subspace(
            primary_selector_member_matrix=primary_selector_member,
            primary_selector_nonmember_matrix=primary_selector_nonmember,
            primary_validation_member_matrix=primary_validation_member,
            primary_validation_nonmember_matrix=primary_validation_nonmember,
            comparator_validation_matrices={
                "to_q": (q_validation_member, torch.zeros((2, 4))),
                "to_k": (k_validation_member, torch.zeros((2, 4))),
            },
            top_k=2,
            candidate_multiplier=2,
        )

        self.assertEqual(set(int(value) for value in selected["top_indices"].tolist()), {0, 1})
        self.assertEqual(selected["cross_layer_stable_count"], 2)
        self.assertEqual(sorted(sum(selected["support_labels"], [])), ["to_k", "to_q"])

    def test_cross_layer_selector_rejects_primary_only_signal(self) -> None:
        _select_cross_layer_stable_subspace = _load_archived_script()._select_cross_layer_stable_subspace

        primary_selector_member = torch.tensor([[1.0, 0.9], [1.1, 1.0]])
        primary_selector_nonmember = torch.zeros((2, 2))
        primary_validation_member = torch.tensor([[0.8, 0.7], [0.9, 0.8]])
        primary_validation_nonmember = torch.zeros((2, 2))
        comparator_member = torch.tensor([[-0.4, -0.3], [-0.5, -0.4]])

        with self.assertRaisesRegex(RuntimeError, "No cross-layer-stable"):
            _select_cross_layer_stable_subspace(
                primary_selector_member_matrix=primary_selector_member,
                primary_selector_nonmember_matrix=primary_selector_nonmember,
                primary_validation_member_matrix=primary_validation_member,
                primary_validation_nonmember_matrix=primary_validation_nonmember,
                comparator_validation_matrices={
                    "to_q": (comparator_member, torch.zeros((2, 2))),
                },
                top_k=2,
                candidate_multiplier=1,
            )


if __name__ == "__main__":
    unittest.main()
