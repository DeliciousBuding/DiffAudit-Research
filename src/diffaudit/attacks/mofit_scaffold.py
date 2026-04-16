from __future__ import annotations

import json
from pathlib import Path
import torch


def build_mofit_summary(
    *,
    target_family: str,
    caption_source: str,
    surrogate_steps: int,
    embedding_steps: int,
    member_count: int,
    nonmember_count: int,
) -> dict:
    return {
        "task": "mofit-interface-canary",
        "status": "scaffold_only",
        "target_family": target_family,
        "caption_source": caption_source,
        "surrogate_steps": surrogate_steps,
        "embedding_steps": embedding_steps,
        "member_count": member_count,
        "nonmember_count": nonmember_count,
        "artifact_schema_version": "mofit-interface-canary.v1",
        "notes": (
            "Dedicated MoFit scaffold initialized. "
            "This artifact does not run surrogate or fitted-embedding optimization yet."
        ),
        "next_step": "implement surrogate and embedding optimization loops",
    }


def initialize_mofit_scaffold(
    *,
    run_root: Path,
    target_family: str,
    caption_source: str,
    surrogate_steps: int,
    embedding_steps: int,
    member_count: int,
    nonmember_count: int,
) -> dict[str, str]:
    run_root.mkdir(parents=True, exist_ok=True)
    traces_root = run_root / "traces"
    surrogate_trace_dir = traces_root / "surrogate"
    embedding_trace_dir = traces_root / "embedding"
    surrogate_trace_dir.mkdir(parents=True, exist_ok=True)
    embedding_trace_dir.mkdir(parents=True, exist_ok=True)

    summary_path = run_root / "summary.json"
    records_path = run_root / "records.jsonl"

    summary = build_mofit_summary(
        target_family=target_family,
        caption_source=caption_source,
        surrogate_steps=surrogate_steps,
        embedding_steps=embedding_steps,
        member_count=member_count,
        nonmember_count=nonmember_count,
    )
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    records_path.write_text("", encoding="utf-8")

    return {
        "summary_path": summary_path.as_posix(),
        "records_path": records_path.as_posix(),
        "surrogate_trace_dir": surrogate_trace_dir.as_posix(),
        "embedding_trace_dir": embedding_trace_dir.as_posix(),
    }


def append_mofit_record(
    *,
    run_root: Path,
    split: str,
    file_name: str,
    prompt_source: str,
    prompt_text: str,
) -> dict:
    traces_root = run_root / "traces"
    surrogate_trace_dir = traces_root / "surrogate"
    embedding_trace_dir = traces_root / "embedding"
    surrogate_trace_dir.mkdir(parents=True, exist_ok=True)
    embedding_trace_dir.mkdir(parents=True, exist_ok=True)

    safe_stem = Path(file_name).stem
    record_key = f"{split}-{safe_stem}"
    surrogate_trace_path = surrogate_trace_dir / f"{record_key}.json"
    embedding_trace_path = embedding_trace_dir / f"{record_key}.json"
    surrogate_trace_path.write_text("[]", encoding="utf-8")
    embedding_trace_path.write_text("[]", encoding="utf-8")

    record = {
        "split": split,
        "file_name": file_name,
        "prompt_source": prompt_source,
        "prompt_text": prompt_text,
        "surrogate_trace_path": surrogate_trace_path.as_posix(),
        "embedding_trace_path": embedding_trace_path.as_posix(),
        "l_cond": None,
        "l_uncond": None,
        "mofit_score": None,
    }

    records_path = run_root / "records.jsonl"
    with records_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")
    return record


def finalize_mofit_record(
    *,
    run_root: Path,
    file_name: str,
    split: str,
    l_cond: float,
    l_uncond: float,
    mofit_score: float,
    surrogate_trace: list[dict],
    embedding_trace: list[dict],
) -> dict:
    safe_stem = Path(file_name).stem
    record_key = f"{split}-{safe_stem}"
    surrogate_trace_path = run_root / "traces" / "surrogate" / f"{record_key}.json"
    embedding_trace_path = run_root / "traces" / "embedding" / f"{record_key}.json"
    surrogate_trace_path.write_text(json.dumps(surrogate_trace, indent=2), encoding="utf-8")
    embedding_trace_path.write_text(json.dumps(embedding_trace, indent=2), encoding="utf-8")

    records_path = run_root / "records.jsonl"
    updated_rows: list[dict] = []
    for raw_line in records_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip():
            continue
        row = json.loads(raw_line)
        if row.get("split") == split and row.get("file_name") == file_name:
            row["l_cond"] = l_cond
            row["l_uncond"] = l_uncond
            row["mofit_score"] = mofit_score
        updated_rows.append(row)

    records_path.write_text(
        "".join(json.dumps(row) + "\n" for row in updated_rows),
        encoding="utf-8",
    )

    for row in updated_rows:
        if row.get("split") == split and row.get("file_name") == file_name:
            return row
    raise ValueError(f"Could not find record for split={split!r}, file_name={file_name!r}")


def run_surrogate_optimization(
    *,
    initial_value: torch.Tensor,
    loss_fn,
    steps: int,
    lr: float,
) -> tuple[torch.Tensor, list[dict]]:
    current = initial_value.detach().clone().requires_grad_(True)
    trace: list[dict] = []
    for step in range(steps):
        loss = loss_fn(current)
        loss.backward()
        grad = current.grad
        if grad is None:
            raise RuntimeError("Surrogate optimization produced no gradient.")
        with torch.no_grad():
            current -= lr * grad.sign()
        trace.append({"step": step, "loss": float(loss.detach().item())})
        current = current.detach().requires_grad_(True)
    return current.detach(), trace


def run_embedding_optimization(
    *,
    initial_value: torch.Tensor,
    loss_fn,
    steps: int,
    lr: float,
) -> tuple[torch.Tensor, list[dict]]:
    current = torch.nn.Parameter(initial_value.detach().clone())
    optimizer = torch.optim.Adam([current], lr=lr)
    trace: list[dict] = []
    for step in range(steps):
        optimizer.zero_grad(set_to_none=True)
        loss = loss_fn(current)
        loss.backward()
        optimizer.step()
        trace.append({"step": step, "loss": float(loss.detach().item())})
    return current.detach(), trace


def compute_mofit_loss_terms(
    *,
    latent: torch.Tensor,
    timestep: int,
    target_noise: torch.Tensor,
    cond_embedding: torch.Tensor,
    uncond_embedding: torch.Tensor,
    predict_noise_fn,
) -> dict[str, float]:
    cond_prediction = predict_noise_fn(latent, timestep, cond_embedding)
    uncond_prediction = predict_noise_fn(latent, timestep, uncond_embedding)
    l_cond = torch.mean((cond_prediction - target_noise) ** 2)
    l_uncond = torch.mean((uncond_prediction - target_noise) ** 2)
    return {
        "l_cond": float(l_cond.detach().item()),
        "l_uncond": float(l_uncond.detach().item()),
        "mofit_score": float((l_cond - l_uncond).detach().item()),
    }


def build_surrogate_loss_fn(
    *,
    timestep: int,
    target_noise: torch.Tensor,
    uncond_embedding: torch.Tensor,
    predict_noise_fn,
):
    def loss_fn(current_latent: torch.Tensor) -> torch.Tensor:
        prediction = predict_noise_fn(current_latent, timestep, uncond_embedding)
        return torch.mean((prediction - target_noise) ** 2)

    return loss_fn


def build_embedding_loss_fn(
    *,
    latent: torch.Tensor,
    timestep: int,
    target_noise: torch.Tensor,
    predict_noise_fn,
):
    def loss_fn(current_embedding: torch.Tensor) -> torch.Tensor:
        prediction = predict_noise_fn(latent, timestep, current_embedding)
        return torch.mean((prediction - target_noise) ** 2)

    return loss_fn
