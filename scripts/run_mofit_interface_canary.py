from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from diffaudit.attacks.mofit_scaffold import execute_mofit_sample, initialize_mofit_scaffold
from scripts.run_structural_memorization_smoke import StructuralMemorizationRunner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a bounded MoFit interface scaffold.")
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--member-dir", type=Path, required=True)
    parser.add_argument("--nonmember-dir", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--lora-dir", type=Path, required=True)
    parser.add_argument("--blip-dir", type=Path, required=True)
    parser.add_argument("--member-limit", type=int, default=1)
    parser.add_argument("--member-offset", type=int, default=0)
    parser.add_argument("--nonmember-limit", type=int, default=1)
    parser.add_argument("--nonmember-offset", type=int, default=0)
    parser.add_argument("--device", type=str, default="cpu")
    parser.add_argument("--surrogate-steps", type=int, default=8)
    parser.add_argument("--embedding-steps", type=int, default=12)
    parser.add_argument("--surrogate-lr", type=float, default=1e-2)
    parser.add_argument("--embedding-lr", type=float, default=5e-3)
    parser.add_argument("--guidance-scale", type=float, default=3.5)
    parser.add_argument("--max-timestep", type=int, default=140)
    parser.add_argument("--record-trace", action="store_true")
    return parser.parse_args()


def load_rows(split_dir: Path, subset_limit: int, offset: int = 0) -> list[dict]:
    rows: list[dict] = []
    metadata_path = split_dir / "metadata.jsonl"
    loaded = 0
    for raw_line in metadata_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        if loaded < offset:
            loaded += 1
            continue
        rows.append(json.loads(raw_line))
        loaded += 1
        if len(rows) >= subset_limit:
            break
    return rows


class MoFitCanaryRunner(StructuralMemorizationRunner):
    def execute_row(
        self,
        *,
        split_name: str,
        split_dir: Path,
        row: dict,
        run_root: Path,
        args: argparse.Namespace,
    ) -> dict:
        image = Image.open(split_dir / row["file_name"]).convert("RGB")
        prompt_text = self.caption_for_image(row, image)
        _, latent = self.encode_image(image)
        cond_embedding, uncond_embedding = self.encode_prompt(prompt_text)

        def caption_fallback_fn(current_row: dict) -> str:
            del current_row
            return prompt_text

        def unet_forward_fn(
            latent_value: torch.Tensor,
            timestep_value: torch.Tensor,
            embedding_value: torch.Tensor,
        ):
            latent_input = latent_value.to(device=self.device, dtype=self.dtype)
            timestep_input = timestep_value.to(device=self.device, dtype=torch.long)
            embedding_input = embedding_value.to(device=self.device, dtype=self.dtype)
            with torch.autocast(
                device_type=self.device.type,
                dtype=self.dtype,
                enabled=self.device.type == "cuda",
            ):
                return self.unet(latent_input, timestep_input, embedding_input)

        return execute_mofit_sample(
            run_root=run_root,
            split=split_name,
            row=row,
            latent=latent.detach(),
            timestep=args.max_timestep,
            cond_embedding=cond_embedding.detach(),
            uncond_embedding=uncond_embedding.detach(),
            unet_forward_fn=unet_forward_fn,
            guidance_scale=args.guidance_scale,
            surrogate_steps=args.surrogate_steps,
            surrogate_lr=args.surrogate_lr,
            embedding_steps=args.embedding_steps,
            embedding_lr=args.embedding_lr,
            initial_surrogate_latent=torch.zeros_like(latent),
            initial_embedding=torch.zeros_like(cond_embedding),
            caption_fallback_fn=caption_fallback_fn,
        )


def run_split(
    *,
    runner,
    split_name: str,
    split_dir: Path,
    rows: list[dict],
    run_root: Path,
    args: argparse.Namespace,
) -> list[dict]:
    records: list[dict] = []
    for index, row in enumerate(rows, start=1):
        result = runner.execute_row(
            split_name=split_name,
            split_dir=split_dir,
            row=row,
            run_root=run_root,
            args=args,
        )
        result["index"] = index
        records.append(result)
        print(
            f"[{split_name}] {index}/{len(rows)} {row['file_name']} "
            f"mofit_score={result['mofit_score']:.6f} "
            f"l_cond={result['l_cond']:.6f} l_uncond={result['l_uncond']:.6f}"
        )
    return records


def run_canary(args: argparse.Namespace, runner=None) -> dict:
    payload = initialize_mofit_scaffold(
        run_root=args.run_root,
        target_family="sd15-plus-celeba_partial_target-checkpoint-25000",
        caption_source="metadata-with-blip-fallback",
        surrogate_steps=args.surrogate_steps,
        embedding_steps=args.embedding_steps,
        member_count=args.member_limit,
        nonmember_count=args.nonmember_limit,
    )
    payload.update(
        {
            "status": "scaffold_only",
            "member_dir": args.member_dir.as_posix(),
            "nonmember_dir": args.nonmember_dir.as_posix(),
            "model_dir": args.model_dir.as_posix(),
            "lora_dir": args.lora_dir.as_posix(),
            "blip_dir": args.blip_dir.as_posix(),
            "device": args.device,
            "surrogate_lr": args.surrogate_lr,
            "embedding_lr": args.embedding_lr,
            "guidance_scale": args.guidance_scale,
            "max_timestep": args.max_timestep,
            "record_trace": args.record_trace,
        }
    )
    member_rows = load_rows(args.member_dir, subset_limit=args.member_limit, offset=args.member_offset)
    nonmember_rows = load_rows(args.nonmember_dir, subset_limit=args.nonmember_limit, offset=args.nonmember_offset)
    active_runner = runner if runner is not None else MoFitCanaryRunner(args)
    member_records = run_split(
        runner=active_runner,
        split_name="member",
        split_dir=args.member_dir,
        rows=member_rows,
        run_root=args.run_root,
        args=args,
    )
    nonmember_records = run_split(
        runner=active_runner,
        split_name="nonmember",
        split_dir=args.nonmember_dir,
        rows=nonmember_rows,
        run_root=args.run_root,
        args=args,
    )

    summary_path = args.run_root / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary.update(
        {
            "status": "canary_executed",
            "notes": (
                "Bounded MoFit canary executed on the local target-family path. "
                "This remains a CPU-first canary and not yet a promoted smoke."
            ),
            "next_step": "evaluate whether the current canary is stable enough for a bounded real-asset smoke gate",
            "member_dir": args.member_dir.as_posix(),
            "nonmember_dir": args.nonmember_dir.as_posix(),
            "model_dir": args.model_dir.as_posix(),
            "lora_dir": args.lora_dir.as_posix(),
            "blip_dir": args.blip_dir.as_posix(),
            "device": args.device,
            "surrogate_lr": args.surrogate_lr,
            "embedding_lr": args.embedding_lr,
            "guidance_scale": args.guidance_scale,
            "max_timestep": args.max_timestep,
            "record_trace": args.record_trace,
            "executed_member_count": len(member_records),
            "executed_nonmember_count": len(nonmember_records),
        }
    )
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    payload.update(
        {
            "status": "canary_executed",
            "executed_member_count": len(member_records),
            "executed_nonmember_count": len(nonmember_records),
            "member_rows": member_rows,
            "nonmember_rows": nonmember_rows,
            "summary_path": summary_path.as_posix(),
        }
    )
    return payload


def main() -> int:
    args = parse_args()
    args.run_root.mkdir(parents=True, exist_ok=True)
    payload = run_canary(args)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
