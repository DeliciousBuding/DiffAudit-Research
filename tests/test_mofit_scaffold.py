import json
import tempfile
import unittest
from pathlib import Path
import torch


class MoFitScaffoldTests(unittest.TestCase):
    def test_initialize_mofit_scaffold_creates_expected_artifacts(self) -> None:
        from diffaudit.attacks.mofit_scaffold import initialize_mofit_scaffold

        with tempfile.TemporaryDirectory() as tmpdir:
            run_root = Path(tmpdir) / "mofit-scaffold"
            result = initialize_mofit_scaffold(
                run_root=run_root,
                target_family="sd15-plus-celeba_partial_target-checkpoint-25000",
                caption_source="metadata-with-blip-fallback",
                surrogate_steps=8,
                embedding_steps=12,
                member_count=1,
                nonmember_count=1,
            )

            summary_path = run_root / "summary.json"
            records_path = run_root / "records.jsonl"
            surrogate_trace_dir = run_root / "traces" / "surrogate"
            embedding_trace_dir = run_root / "traces" / "embedding"

            self.assertEqual(result["summary_path"], summary_path.as_posix())
            self.assertTrue(summary_path.exists())
            self.assertTrue(records_path.exists())
            self.assertTrue(surrogate_trace_dir.exists())
            self.assertTrue(embedding_trace_dir.exists())
            self.assertEqual(records_path.read_text(encoding="utf-8"), "")

            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["artifact_schema_version"], "mofit-interface-canary.v1")
            self.assertEqual(summary["status"], "scaffold_only")
            self.assertEqual(summary["target_family"], "sd15-plus-celeba_partial_target-checkpoint-25000")
            self.assertEqual(summary["caption_source"], "metadata-with-blip-fallback")
            self.assertEqual(summary["surrogate_steps"], 8)
            self.assertEqual(summary["embedding_steps"], 12)
            self.assertEqual(summary["member_count"], 1)
            self.assertEqual(summary["nonmember_count"], 1)

    def test_append_mofit_record_creates_trace_placeholders(self) -> None:
        from diffaudit.attacks.mofit_scaffold import append_mofit_record, initialize_mofit_scaffold

        with tempfile.TemporaryDirectory() as tmpdir:
            run_root = Path(tmpdir) / "mofit-scaffold"
            initialize_mofit_scaffold(
                run_root=run_root,
                target_family="sd15-plus-celeba_partial_target-checkpoint-25000",
                caption_source="metadata-with-blip-fallback",
                surrogate_steps=8,
                embedding_steps=12,
                member_count=1,
                nonmember_count=1,
            )

            record = append_mofit_record(
                run_root=run_root,
                split="member",
                file_name="sample.png",
                prompt_source="metadata",
                prompt_text="face portrait",
            )

            records_path = run_root / "records.jsonl"
            lines = records_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)

            row = json.loads(lines[0])
            self.assertEqual(row["split"], "member")
            self.assertEqual(row["file_name"], "sample.png")
            self.assertEqual(row["prompt_source"], "metadata")
            self.assertEqual(row["prompt_text"], "face portrait")
            self.assertIsNone(row["l_cond"])
            self.assertIsNone(row["l_uncond"])
            self.assertIsNone(row["mofit_score"])

            surrogate_trace = Path(row["surrogate_trace_path"])
            embedding_trace = Path(row["embedding_trace_path"])
            self.assertTrue(surrogate_trace.exists())
            self.assertTrue(embedding_trace.exists())
            self.assertEqual(json.loads(surrogate_trace.read_text(encoding="utf-8")), [])
            self.assertEqual(json.loads(embedding_trace.read_text(encoding="utf-8")), [])

            self.assertEqual(record["surrogate_trace_path"], surrogate_trace.as_posix())
            self.assertEqual(record["embedding_trace_path"], embedding_trace.as_posix())

    def test_finalize_mofit_record_updates_scores_and_traces(self) -> None:
        from diffaudit.attacks.mofit_scaffold import (
            append_mofit_record,
            finalize_mofit_record,
            initialize_mofit_scaffold,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            run_root = Path(tmpdir) / "mofit-scaffold"
            initialize_mofit_scaffold(
                run_root=run_root,
                target_family="sd15-plus-celeba_partial_target-checkpoint-25000",
                caption_source="metadata-with-blip-fallback",
                surrogate_steps=8,
                embedding_steps=12,
                member_count=1,
                nonmember_count=1,
            )
            record = append_mofit_record(
                run_root=run_root,
                split="member",
                file_name="sample.png",
                prompt_source="metadata",
                prompt_text="face portrait",
            )

            finalized = finalize_mofit_record(
                run_root=run_root,
                file_name="sample.png",
                split="member",
                l_cond=1.25,
                l_uncond=0.75,
                mofit_score=0.5,
                surrogate_trace=[{"step": 0, "loss": 1.0}, {"step": 1, "loss": 0.8}],
                embedding_trace=[{"step": 0, "loss": 0.6}, {"step": 1, "loss": 0.4}],
            )

            self.assertEqual(finalized["l_cond"], 1.25)
            self.assertEqual(finalized["l_uncond"], 0.75)
            self.assertEqual(finalized["mofit_score"], 0.5)

            lines = (run_root / "records.jsonl").read_text(encoding="utf-8").splitlines()
            row = json.loads(lines[0])
            self.assertEqual(row["l_cond"], 1.25)
            self.assertEqual(row["l_uncond"], 0.75)
            self.assertEqual(row["mofit_score"], 0.5)

            surrogate_trace = Path(record["surrogate_trace_path"])
            embedding_trace = Path(record["embedding_trace_path"])
            self.assertEqual(
                json.loads(surrogate_trace.read_text(encoding="utf-8")),
                [{"step": 0, "loss": 1.0}, {"step": 1, "loss": 0.8}],
            )
            self.assertEqual(
                json.loads(embedding_trace.read_text(encoding="utf-8")),
                [{"step": 0, "loss": 0.6}, {"step": 1, "loss": 0.4}],
            )

    def test_run_surrogate_optimization_reduces_toy_loss(self) -> None:
        from diffaudit.attacks.mofit_scaffold import run_surrogate_optimization

        initial = torch.tensor([2.0], dtype=torch.float32)

        def loss_fn(current: torch.Tensor) -> torch.Tensor:
            return ((current - 0.5) ** 2).mean()

        optimized, trace = run_surrogate_optimization(
            initial_value=initial,
            loss_fn=loss_fn,
            steps=4,
            lr=0.25,
        )

        self.assertEqual(len(trace), 4)
        self.assertLess(trace[-1]["loss"], trace[0]["loss"])
        self.assertLess(abs(float(optimized.item()) - 0.5), abs(float(initial.item()) - 0.5))

    def test_run_embedding_optimization_reduces_toy_loss(self) -> None:
        from diffaudit.attacks.mofit_scaffold import run_embedding_optimization

        initial = torch.tensor([1.5], dtype=torch.float32)

        def loss_fn(current: torch.Tensor) -> torch.Tensor:
            return ((current + 0.25) ** 2).mean()

        optimized, trace = run_embedding_optimization(
            initial_value=initial,
            loss_fn=loss_fn,
            steps=5,
            lr=0.2,
        )

        self.assertEqual(len(trace), 5)
        self.assertLess(trace[-1]["loss"], trace[0]["loss"])
        self.assertLess(abs(float(optimized.item()) + 0.25), abs(float(initial.item()) + 0.25))


if __name__ == "__main__":
    unittest.main()
