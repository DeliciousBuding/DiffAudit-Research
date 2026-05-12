"""Mid-frequency same-noise residual scoring and tiny cache utilities.

This module is still pre-admission infrastructure. It provides CPU scoring,
same-noise state collection helpers, and a synthetic tiny cache-contract runner;
it does not authorize a GPU packet or benchmark result.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from diffaudit.attacks.h2_response_strength import build_alpha_bars, build_frequency_mask
from diffaudit.utils.io import write_summary_json
from diffaudit.utils.metrics import metric_bundle, round6

DEFAULT_CUTOFF = 0.25
DEFAULT_CUTOFF_HIGH = 0.50


def _as_residual_arrays(x_t: np.ndarray, tilde_x_t: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x_arr = np.asarray(x_t, dtype=np.float32)
    tilde_arr = np.asarray(tilde_x_t, dtype=np.float32)
    if x_arr.shape != tilde_arr.shape:
        raise ValueError(f"x_t and tilde_x_t shapes differ: {x_arr.shape} vs {tilde_arr.shape}")
    if x_arr.ndim != 4:
        raise ValueError("x_t and tilde_x_t must have shape [sample, channel, height, width]")
    if x_arr.shape[0] == 0:
        raise ValueError("x_t and tilde_x_t must contain at least one sample")
    if x_arr.shape[-2] < 2 or x_arr.shape[-1] < 2:
        raise ValueError("height and width must both be at least 2")
    return x_arr, tilde_arr


def _validate_band(cutoff: float, cutoff_high: float) -> tuple[float, float]:
    low = float(cutoff)
    high = float(cutoff_high)
    if not np.isfinite(low) or not np.isfinite(high) or low < 0.0 or high > 1.0 or low >= high:
        raise ValueError("cutoff must satisfy 0 <= cutoff < cutoff_high <= 1")
    return low, high


def bandpass_residual_l2(
    x_t: np.ndarray,
    tilde_x_t: np.ndarray,
    *,
    cutoff: float = DEFAULT_CUTOFF,
    cutoff_high: float = DEFAULT_CUTOFF_HIGH,
) -> np.ndarray:
    """Return per-sample FFT band-pass L2 over ``tilde_x_t - x_t``.

    The FFT uses orthonormal scaling so scores are stable across image sizes.
    Lower distances are expected to be more member-like; use
    :func:`midfreq_member_scores` for the project-standard higher-is-member
    orientation.
    """

    x_arr, tilde_arr = _as_residual_arrays(x_t, tilde_x_t)
    low, high = _validate_band(cutoff, cutoff_high)
    mask = build_frequency_mask(
        int(x_arr.shape[-2]),
        int(x_arr.shape[-1]),
        "bandpass",
        cutoff=low,
        cutoff_high=high,
    ).astype(np.float32)
    residual = tilde_arr - x_arr
    spectrum = np.fft.fftn(residual, axes=(-2, -1), norm="ortho")
    masked = spectrum * mask
    distances = np.sqrt(np.mean(np.abs(masked) ** 2, axis=(1, 2, 3)))
    return distances.astype(np.float32)


def midfreq_member_scores(
    x_t: np.ndarray,
    tilde_x_t: np.ndarray,
    *,
    cutoff: float = DEFAULT_CUTOFF,
    cutoff_high: float = DEFAULT_CUTOFF_HIGH,
) -> np.ndarray:
    """Return higher-is-member scores from mid-frequency residual distances."""

    return -bandpass_residual_l2(x_t, tilde_x_t, cutoff=cutoff, cutoff_high=cutoff_high)


def summarize_midfreq_packet(
    labels: np.ndarray,
    x_t: np.ndarray,
    tilde_x_t: np.ndarray,
    *,
    cutoff: float = DEFAULT_CUTOFF,
    cutoff_high: float = DEFAULT_CUTOFF_HIGH,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Summarize a same-noise residual packet with project-standard metrics."""

    labels_i64 = np.asarray(labels, dtype=np.int64)
    x_arr, tilde_arr = _as_residual_arrays(x_t, tilde_x_t)
    if labels_i64.shape != (x_arr.shape[0],):
        raise ValueError(f"labels must have shape [{x_arr.shape[0]}], got {labels_i64.shape}")
    if int((labels_i64 == 1).sum()) == 0 or int((labels_i64 == 0).sum()) == 0:
        raise ValueError("labels must contain at least one member (1) and one nonmember (0)")
    distances = bandpass_residual_l2(x_arr, tilde_arr, cutoff=cutoff, cutoff_high=cutoff_high)
    scores = -distances
    metrics = metric_bundle(scores.astype(np.float64), labels_i64)
    member_mask = labels_i64 == 1
    nonmember_mask = labels_i64 == 0
    metrics["member_score_mean"] = round6(float(scores[member_mask].mean()))
    metrics["nonmember_score_mean"] = round6(float(scores[nonmember_mask].mean()))
    metrics["member_distance_mean"] = round6(float(distances[member_mask].mean()))
    metrics["nonmember_distance_mean"] = round6(float(distances[nonmember_mask].mean()))
    return {
        "method": "mid_frequency_same_noise_residual",
        "score_orientation": "negative_bandpass_l2_higher_is_member",
        "cutoff": round6(float(cutoff)),
        "cutoff_high": round6(float(cutoff_high)),
        "sample_count": int(labels_i64.shape[0]),
        "member_count": int(member_mask.sum()),
        "nonmember_count": int(nonmember_mask.sum()),
        "metrics": metrics,
        "metadata": {} if metadata is None else dict(metadata),
        "distances": [round6(float(value)) for value in distances.tolist()],
        "scores": [round6(float(value)) for value in scores.tolist()],
    }


def one_step_same_noise_state(
    model: Any,
    x0_pixels: Any,
    *,
    timestep: int,
    alpha_bars: Any,
    generator: Any,
    device: str,
) -> tuple[Any, Any]:
    """Return ``(x_t, tilde_x_t)`` for the one-step same-noise contract.

    ``x0_pixels`` is expected in ``[0, 1]`` pixel space. The returned tensors
    are in DDPM normalized ``[-1, 1]`` space so the residual is computed at the
    same diffusion state scale.
    """

    import torch

    x0 = x0_pixels.to(device) * 2.0 - 1.0
    strength_t = int(timestep)
    if strength_t <= 0:
        raise ValueError("timestep must be positive")
    if strength_t >= int(alpha_bars.shape[0]):
        raise ValueError(f"timestep must be < {alpha_bars.shape[0]}: {strength_t}")

    noise = torch.randn(x0.shape, generator=generator, device=device, dtype=x0.dtype)
    alpha_t = alpha_bars[strength_t].to(device).view(1, 1, 1, 1)
    x_t = alpha_t.sqrt() * x0 + (1.0 - alpha_t).sqrt() * noise

    t_tensor = torch.full((x_t.shape[0],), strength_t, device=device, dtype=torch.long)
    eps = model(x_t, t=t_tensor)
    x0_pred = (x_t - (1.0 - alpha_t).sqrt() * eps) / alpha_t.sqrt()
    x0_pred = torch.clamp(x0_pred, -1.0, 1.0)
    tilde_x_t = alpha_t.sqrt() * x0_pred + (1.0 - alpha_t).sqrt() * noise
    return x_t.detach().cpu(), tilde_x_t.detach().cpu()


def collect_midfreq_residual_states(
    model: Any,
    loader: Any,
    *,
    device: str,
    alpha_bars: Any,
    timestep: int,
    seed: int,
    sample_offset: int = 0,
) -> tuple[Any, np.ndarray, np.ndarray]:
    """Collect inputs plus matched ``x_t`` and ``tilde_x_t`` arrays.

    This is a state collector only. It does not decide whether a GPU packet is
    scientifically released; callers still need a frozen packet contract.
    """

    import torch

    inputs: list[Any] = []
    x_t_batches: list[np.ndarray] = []
    tilde_batches: list[np.ndarray] = []
    running_offset = int(sample_offset)
    model.eval()
    with torch.no_grad():
        generator = torch.Generator(device=device)
        for batch, _ in loader:
            batch = batch.detach().cpu()
            generator.manual_seed(int(seed) + int(running_offset))
            x_t, tilde_x_t = one_step_same_noise_state(
                model,
                batch,
                timestep=int(timestep),
                alpha_bars=alpha_bars,
                generator=generator,
                device=device,
            )
            inputs.append(batch)
            x_t_batches.append(x_t.numpy())
            tilde_batches.append(tilde_x_t.numpy())
            running_offset += int(batch.shape[0])
    return (
        torch.cat(inputs, dim=0),
        np.concatenate(x_t_batches, axis=0).astype(np.float32),
        np.concatenate(tilde_batches, axis=0).astype(np.float32),
    )


def run_midfreq_residual_tiny_cache(
    *,
    workspace: str | Path,
    member_count: int = 4,
    nonmember_count: int = 4,
    batch_size: int = 4,
    timestep: int = 80,
    seed: int = 0,
    cutoff: float = DEFAULT_CUTOFF,
    cutoff_high: float = DEFAULT_CUTOFF_HIGH,
    image_size: int = 32,
    channels: int = 3,
    device: str = "cpu",
    provenance_status: str = "synthetic-schema-preflight",
) -> dict[str, Any]:
    """Write a tiny CPU-only residual cache that proves the packet schema.

    This runner deliberately uses a synthetic model and synthetic inputs. It is
    a cache-contract preflight, not a benchmark or GPU release.
    """

    if device != "cpu":
        raise ValueError("run_midfreq_residual_tiny_cache is CPU-only; use device='cpu'")
    if int(member_count) <= 0 or int(nonmember_count) <= 0:
        raise ValueError("member_count and nonmember_count must be positive")
    if int(member_count) > 8 or int(nonmember_count) > 8:
        raise ValueError("tiny cache is capped at 8 members and 8 nonmembers")
    if int(batch_size) <= 0:
        raise ValueError("batch_size must be positive")
    if int(image_size) < 8:
        raise ValueError("image_size must be at least 8")
    if int(channels) <= 0:
        raise ValueError("channels must be positive")

    import torch

    class SyntheticEpsModel(torch.nn.Module):
        def forward(self, x, t):  # type: ignore[no-untyped-def]
            del t
            gate = (x.mean(dim=(1, 2, 3), keepdim=True) > 0.0).to(dtype=x.dtype)
            return x * (0.05 + 0.45 * gate)

    member_count_i = int(member_count)
    nonmember_count_i = int(nonmember_count)
    total = member_count_i + nonmember_count_i
    labels = np.asarray([1] * member_count_i + [0] * nonmember_count_i, dtype=np.int64)
    member_indices = np.arange(member_count_i, dtype=np.int64)
    nonmember_indices = np.arange(member_count_i, total, dtype=np.int64)

    input_generator = torch.Generator(device="cpu")
    input_generator.manual_seed(int(seed))
    inputs = torch.empty((total, int(channels), int(image_size), int(image_size)), dtype=torch.float32)
    inputs[:member_count_i].fill_(0.35)
    inputs[member_count_i:].fill_(0.65)
    inputs = torch.clamp(inputs + 0.01 * torch.rand(inputs.shape, generator=input_generator), 0.0, 1.0)

    dataset = torch.utils.data.TensorDataset(inputs, torch.from_numpy(labels))
    loader = torch.utils.data.DataLoader(dataset, batch_size=int(batch_size), shuffle=False)
    alpha_bars = build_alpha_bars("cpu", timesteps=1000)
    collected_inputs, x_t, tilde_x_t = collect_midfreq_residual_states(
        SyntheticEpsModel(),
        loader,
        device="cpu",
        alpha_bars=alpha_bars,
        timestep=int(timestep),
        seed=int(seed),
    )
    summary = summarize_midfreq_packet(
        labels,
        x_t,
        tilde_x_t,
        cutoff=float(cutoff),
        cutoff_high=float(cutoff_high),
        metadata={
            "packet_type": "synthetic_schema_preflight",
            "timestep": int(timestep),
            "seed": int(seed),
            "noise_provenance": {
                "collector_seed": int(seed),
                "batch_reseed_rule": "collector_seed + running_sample_offset",
                "sample_offset": 0,
            },
            "provenance_status": provenance_status,
        },
    )

    workspace_path = Path(workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)
    cache_path = workspace_path / "residual-cache.npz"
    summary_path = workspace_path / "summary.json"
    distances = np.asarray(summary["distances"], dtype=np.float32)
    scores = np.asarray(summary["scores"], dtype=np.float32)
    np.savez_compressed(
        cache_path,
        labels=labels,
        member_indices=member_indices,
        nonmember_indices=nonmember_indices,
        timestep=np.asarray([int(timestep)], dtype=np.int64),
        seed=np.asarray([int(seed)], dtype=np.int64),
        noise_seed=np.asarray([int(seed)], dtype=np.int64),
        inputs=collected_inputs.numpy().astype(np.float32),
        x_t=x_t.astype(np.float32),
        tilde_x_t=tilde_x_t.astype(np.float32),
        bandpass_l2=distances,
        scores=scores,
        cutoff=np.asarray([float(cutoff)], dtype=np.float32),
        cutoff_high=np.asarray([float(cutoff_high)], dtype=np.float32),
    )

    payload = {
        "status": "ready",
        "verdict": "tiny-runner-schema-ready",
        "method": "mid_frequency_same_noise_residual",
        "boundary": "synthetic cache-contract preflight; not a benchmark; no GPU release",
        "paths": {
            "workspace": str(workspace_path),
            "cache": str(cache_path),
            "summary": str(summary_path),
        },
        "cache_schema": {
            "format": "npz",
            "fields": [
                "labels",
                "member_indices",
                "nonmember_indices",
                "timestep",
                "seed",
                "noise_seed",
                "inputs",
                "x_t",
                "tilde_x_t",
                "bandpass_l2",
                "scores",
                "cutoff",
                "cutoff_high",
            ],
        },
        "packet": {
            "member_count": member_count_i,
            "nonmember_count": nonmember_count_i,
            "sample_count": total,
            "batch_size": int(batch_size),
            "device": "cpu",
            "gpu_released": False,
            "synthetic": True,
        },
        "summary": summary,
        "next_action": "Run a real-asset 4/4 or 8/8 cache preflight before any 64/64 sign-check packet.",
    }
    write_summary_json(summary_path, payload)
    return payload
