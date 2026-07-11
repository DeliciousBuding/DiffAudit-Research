"""First-party canonical DDPM PIA scorer (Kong et al., ICLR 2024, Eq. 9)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import torch

EpsilonOracle = Callable[[torch.Tensor, torch.Tensor], torch.Tensor]
CANONICAL_TIMESTEP = 200
CANONICAL_LP_ORDER = 4
CANONICAL_NUM_DIFFUSION_STEPS = 1000


def _validate_inputs(x0: torch.Tensor, betas: torch.Tensor) -> None:
    if not isinstance(x0, torch.Tensor) or not x0.is_floating_point():
        raise TypeError("x0 must be a floating point torch.Tensor")
    if x0.ndim != 4:
        raise ValueError("x0 must be four-dimensional BCHW input")
    if x0.shape[0] == 0:
        raise ValueError("x0 batch must not be empty")
    if not bool(torch.isfinite(x0).all()):
        raise ValueError("x0 must contain only finite values")
    if float(x0.min()) < -1.0 or float(x0.max()) > 1.0:
        raise ValueError("x0 must be in the target training domain [-1, 1]")
    if not isinstance(betas, torch.Tensor) or not betas.is_floating_point():
        raise TypeError("betas must be a floating point torch.Tensor")
    if betas.ndim != 1 or betas.numel() != CANONICAL_NUM_DIFFUSION_STEPS:
        raise ValueError("betas must contain exactly 1000 diffusion steps")
    if betas.device != x0.device:
        raise ValueError("betas and x0 must be on the same device")
    if not bool(torch.isfinite(betas).all()) or bool(((betas <= 0) | (betas >= 1)).any()):
        raise ValueError("betas must be finite values strictly between zero and one")


def score_pia_canonical(
    epsilon_oracle: EpsilonOracle,
    x0: torch.Tensor,
    betas: torch.Tensor,
    *,
    timestep: int = CANONICAL_TIMESTEP,
    lp_order: int = CANONICAL_LP_ORDER,
    diagnostics: bool = False,
) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor]:
    """Return one member-positive score per row using exactly queries ``[0, 200]``."""

    if timestep != CANONICAL_TIMESTEP:
        raise ValueError("canonical PIA timestep must be 200")
    if lp_order != CANONICAL_LP_ORDER:
        raise ValueError("canonical PIA lp_order must be 4")
    _validate_inputs(x0, betas)
    batch_size = x0.shape[0]
    t0 = torch.zeros(batch_size, dtype=torch.long, device=x0.device)
    tt = torch.full((batch_size,), timestep, dtype=torch.long, device=x0.device)
    e0 = epsilon_oracle(x0, t0)
    if e0.shape != x0.shape or e0.device != x0.device or e0.dtype != x0.dtype:
        raise ValueError("epsilon oracle output must match x0 shape, device, and dtype")
    alpha_bar_t = torch.cumprod(1.0 - betas, dim=0)[timestep]
    xt = alpha_bar_t.sqrt() * x0 + (1.0 - alpha_bar_t).sqrt() * e0
    et = epsilon_oracle(xt, tt)
    if et.shape != x0.shape or et.device != x0.device or et.dtype != x0.dtype:
        raise ValueError("epsilon oracle output must match x0 shape, device, and dtype")
    residual = torch.linalg.vector_norm((e0 - et).flatten(start_dim=1), ord=lp_order, dim=1)
    scores = -residual
    return (scores, residual) if diagnostics else scores


def calibrate_membership_threshold(scores: np.ndarray, labels: np.ndarray) -> float:
    """Select a threshold on calibration rows only by BA, then FPR, then conservatism."""

    scores = np.asarray(scores, dtype=float)
    labels = np.asarray(labels, dtype=np.int64)
    if scores.ndim != 1 or labels.shape != scores.shape or set(np.unique(labels)) != {0, 1}:
        raise ValueError("calibration scores and binary labels must be matching vectors")
    candidates = np.concatenate(([np.inf], np.unique(scores)[::-1], [-np.inf]))
    best: tuple[float, float, float] | None = None
    best_threshold = float("inf")
    for threshold in candidates:
        predictions = scores >= threshold
        tpr = float(predictions[labels == 1].mean())
        fpr = float(predictions[labels == 0].mean())
        key = ((tpr + (1.0 - fpr)) / 2.0, -fpr, float(threshold))
        if best is None or key > best:
            best, best_threshold = key, float(threshold)
    return best_threshold


def apply_membership_threshold(
    scores: np.ndarray, labels: np.ndarray, threshold: float
) -> dict[str, Any]:
    """Apply a frozen calibration threshold to evaluation rows without reselection."""

    scores = np.asarray(scores, dtype=float)
    labels = np.asarray(labels, dtype=np.int64)
    predictions = (scores >= threshold).astype(np.int64)
    tpr = float(predictions[labels == 1].mean())
    fpr = float(predictions[labels == 0].mean())
    return {
        "threshold": float(threshold),
        "balanced_accuracy": (tpr + (1.0 - fpr)) / 2.0,
        "fpr": fpr,
        "predictions": predictions,
    }


def evaluate_calibrated_packets(
    calibration_scores: np.ndarray,
    calibration_labels: np.ndarray,
    calibration_indices: np.ndarray,
    evaluation_scores: np.ndarray,
    evaluation_labels: np.ndarray,
    evaluation_indices: np.ndarray,
) -> dict[str, Any]:
    """Calibrate on one packet and apply to a disjoint evaluation packet."""

    calibration_indices = np.asarray(calibration_indices)
    evaluation_indices = np.asarray(evaluation_indices)
    overlap = np.intersect1d(calibration_indices, evaluation_indices)
    if overlap.size:
        raise ValueError("calibration and evaluation rows must be disjoint")
    threshold = calibrate_membership_threshold(calibration_scores, calibration_labels)
    return apply_membership_threshold(evaluation_scores, evaluation_labels, threshold)
