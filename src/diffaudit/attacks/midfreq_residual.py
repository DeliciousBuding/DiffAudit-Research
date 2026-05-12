"""Mid-frequency same-noise residual scoring utilities.

This module covers CPU scoring only. It does not collect diffusion states or
authorize a GPU packet; callers must provide matched ``x_t`` and
``tilde_x_t`` tensors from a frozen residual collection contract.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from diffaudit.attacks.h2_response_strength import build_frequency_mask
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
    if low < 0.0 or high > 1.0 or low >= high:
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
    masked = spectrum * mask[None, :, :, :]
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
