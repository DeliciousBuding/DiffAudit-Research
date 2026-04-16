import argparse
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import torch


def _load_script_module():
    root = Path(__file__).resolve().parents[1]
    script_path = root / "scripts" / "run_mofit_interface_canary.py"
    spec = importlib.util.spec_from_file_location("run_mofit_interface_canary", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MoFitInterfaceCanaryTests(unittest.TestCase):
    def test_load_rows_honors_offset_and_limit(self) -> None:
        module = _load_script_module()

        with tempfile.TemporaryDirectory() as tmpdir:
            split_dir = Path(tmpdir) / "member"
            split_dir.mkdir(parents=True, exist_ok=True)
            metadata_path = split_dir / "metadata.jsonl"
            metadata_path.write_text(
                "\n".join(
                    [
                        json.dumps({"file_name": "a.png", "text": "a"}),
                        json.dumps({"file_name": "b.png", "text": "b"}),
                        json.dumps({"file_name": "c.png", "text": "c"}),
                    ]
                ),
                encoding="utf-8",
            )

            rows = module.load_rows(split_dir, subset_limit=1, offset=1)

            self.assertEqual(rows, [{"file_name": "b.png", "text": "b"}])

    def test_run_canary_executes_bounded_rows_and_updates_summary(self) -> None:
        module = _load_script_module()
        from diffaudit.attacks.mofit_scaffold import execute_mofit_sample

        class FakeRunner:
            def execute_row(self, *, split_name: str, split_dir: Path, row: dict, run_root: Path, args) -> dict:
                del split_dir

                def unet_forward(
                    latent_value: torch.Tensor,
                    timestep_value: torch.Tensor,
                    embedding_value: torch.Tensor,
                ) -> SimpleNamespace:
                    del timestep_value
                    embed_scalar = embedding_value.mean(dim=-1, keepdim=True).to(dtype=latent_value.dtype)
                    return SimpleNamespace(sample=latent_value + embed_scalar)

                return execute_mofit_sample(
                    run_root=run_root,
                    split=split_name,
                    row=row,
                    latent=torch.tensor([[1.0]], dtype=torch.float32),
                    timestep=args.max_timestep,
                    cond_embedding=torch.tensor([[2.0]], dtype=torch.float32),
                    uncond_embedding=torch.tensor([[0.5]], dtype=torch.float32),
                    unet_forward_fn=unet_forward,
                    guidance_scale=1.0,
                    surrogate_steps=2,
                    surrogate_lr=0.5,
                    embedding_steps=4,
                    embedding_lr=0.1,
                    initial_surrogate_latent=torch.tensor([[0.0]], dtype=torch.float32),
                    initial_embedding=torch.tensor([[0.0]], dtype=torch.float32),
                    caption_fallback_fn=lambda current_row: f"fallback:{current_row['file_name']}",
                )

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            member_dir = root / "member"
            nonmember_dir = root / "nonmember"
            member_dir.mkdir(parents=True, exist_ok=True)
            nonmember_dir.mkdir(parents=True, exist_ok=True)
            (member_dir / "metadata.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps({"file_name": "m0.png", "text": "skip member"}),
                        json.dumps({"file_name": "m1.png", "text": "member prompt"}),
                    ]
                ),
                encoding="utf-8",
            )
            (nonmember_dir / "metadata.jsonl").write_text(
                "\n".join(
                    [
                        json.dumps({"file_name": "n0.png", "text": "skip nonmember"}),
                        json.dumps({"file_name": "n1.png", "text": "   "}),
                    ]
                ),
                encoding="utf-8",
            )

            args = argparse.Namespace(
                run_root=root / "run",
                member_dir=member_dir,
                nonmember_dir=nonmember_dir,
                model_dir=root / "model",
                lora_dir=root / "lora",
                blip_dir=root / "blip",
                member_limit=1,
                member_offset=1,
                nonmember_limit=1,
                nonmember_offset=1,
                device="cpu",
                surrogate_steps=2,
                embedding_steps=4,
                surrogate_lr=0.5,
                embedding_lr=0.1,
                guidance_scale=1.0,
                max_timestep=10,
                record_trace=True,
            )

            payload = module.run_canary(args, runner=FakeRunner())

            self.assertEqual(payload["status"], "canary_executed")
            self.assertEqual(payload["executed_member_count"], 1)
            self.assertEqual(payload["executed_nonmember_count"], 1)
            self.assertEqual(payload["member_rows"][0]["file_name"], "m1.png")
            self.assertEqual(payload["nonmember_rows"][0]["file_name"], "n1.png")

            summary = json.loads((args.run_root / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["status"], "canary_executed")
            self.assertEqual(summary["executed_member_count"], 1)
            self.assertEqual(summary["executed_nonmember_count"], 1)

            records = [
                json.loads(line)
                for line in (args.run_root / "records.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(records), 2)
            self.assertEqual(records[0]["file_name"], "m1.png")
            self.assertEqual(records[1]["prompt_source"], "blip-fallback")


if __name__ == "__main__":
    unittest.main()
