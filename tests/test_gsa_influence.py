from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np


def create_minimal_gsa_repo(repo_root: Path) -> None:
    ddpm_root = repo_root / "DDPM"
    ddpm_root.mkdir(parents=True)
    (ddpm_root / "gen_l2_gradients_DDPM.py").write_text("# gradient entrypoint\n", encoding="utf-8")
    (ddpm_root / "train_unconditional.py").write_text("# train entrypoint\n", encoding="utf-8")
    (repo_root / "test_attack_accuracy.py").write_text("# attack entrypoint\n", encoding="utf-8")


def create_minimal_influence_assets(assets_root: Path) -> None:
    for relative in (
        "datasets/target-member",
        "datasets/target-nonmember",
        "datasets/shadow-01-member",
        "datasets/shadow-01-nonmember",
        "checkpoints/target/checkpoint-9600",
        "checkpoints/shadow-01/checkpoint-9600",
        "manifests",
        "sources",
    ):
        (assets_root / relative).mkdir(parents=True, exist_ok=True)
    for relative in (
        "datasets/target-member/sample-a.png",
        "datasets/target-nonmember/sample-b.png",
        "datasets/shadow-01-member/sample-c.png",
        "datasets/shadow-01-nonmember/sample-d.png",
    ):
        (assets_root / relative).write_bytes(b"png")
    (assets_root / "manifests" / "split-manifest.json").write_text("{}", encoding="utf-8")
    (assets_root / "sources" / "cifar-10-python.tar.gz").write_bytes(b"archive")


class GsaInfluenceTests(unittest.TestCase):
    def test_fisher_scores_use_shadow_fit_and_do_not_persist_vectors(self) -> None:
        from diffaudit.attacks.gsa_influence import run_gsa_diagonal_fisher_feasibility

        calls: list[tuple[str, str, int]] = []

        def fake_extract_split_gradient_records(
            *,
            split,
            role,
            label,
            checkpoint_root,
            **kwargs,
        ):
            del kwargs
            calls.append((split, role, label))
            vector = np.asarray([2.0, 0.0], dtype=np.float64) if label == 1 else np.asarray([0.2, 0.0], dtype=np.float64)
            loss_score = 0.5 if label == 1 else 0.4
            raw_grad_l2_sq = float(np.dot(vector, vector))
            return (
                [
                    {
                        "split": split,
                        "role": role,
                        "label": label,
                        "dataset_relpath": f"{split}.png",
                        "checkpoint_dir": str(Path(checkpoint_root) / "checkpoint-9600"),
                        "layer_id": "mid_block.attentions.0.to_v",
                        "timesteps": [19],
                        "loss_score": loss_score,
                        "raw_grad_l2_sq": raw_grad_l2_sq,
                        "grad_vector": vector,
                        "grad_numel": 2,
                    }
                ],
                Path(checkpoint_root) / "checkpoint-9600",
                {"layer_id": "mid_block.attentions.0.to_v"},
            )

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo_root = root / "GSA"
            assets_root = root / "assets"
            workspace = root / "workspace"
            create_minimal_gsa_repo(repo_root)
            create_minimal_influence_assets(assets_root)

            with patch(
                "diffaudit.attacks.gsa_influence._extract_split_gradient_records",
                side_effect=fake_extract_split_gradient_records,
            ):
                payload = run_gsa_diagonal_fisher_feasibility(
                    workspace=workspace,
                    repo_root=repo_root,
                    assets_root=assets_root,
                    max_samples_per_split=1,
                    ddpm_num_steps=20,
                    sampling_frequency=1,
                    device="cpu",
                )
            records = [
                json.loads(line)
                for line in (workspace / "records.jsonl").read_text(encoding="utf-8").splitlines()
            ]

        self.assertEqual(payload["status"], "ready")
        self.assertEqual(payload["mode"], "diagonal-fisher-feasibility-microboard")
        self.assertEqual(payload["gpu_release"], "none")
        self.assertTrue(payload["checks"]["raw_gradient_vectors_not_persisted_by_default"])
        self.assertEqual(payload["runtime"]["shadow_sample_count"], 2)
        self.assertEqual(payload["runtime"]["target_sample_count"], 2)
        for score_name in ("diag_fisher_self_influence", "scalar_loss", "raw_grad_l2_sq"):
            self.assertEqual(
                payload["score_boards"]["target_transfer"][score_name]["score_direction"],
                payload["score_boards"]["shadow_calibration"][score_name]["score_direction"],
            )
        self.assertEqual({call[1] for call in calls}, {"shadow-calibration", "target-transfer"})
        self.assertEqual(len(records), 4)
        self.assertNotIn("grad_vector", records[0])
        self.assertIn("diag_fisher_self_influence", records[0])

    def test_blocks_non_cpu_device(self) -> None:
        from diffaudit.attacks.gsa_influence import run_gsa_diagonal_fisher_feasibility

        with self.assertRaisesRegex(ValueError, "CPU-only"):
            run_gsa_diagonal_fisher_feasibility(
                workspace="unused",
                repo_root="unused",
                assets_root="unused",
                device="cuda",
            )


if __name__ == "__main__":
    unittest.main()
