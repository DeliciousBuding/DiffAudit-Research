"""Diffusion schedule helpers."""

from __future__ import annotations

import numpy as np


def alpha_bar_schedule(num_timesteps: int, *, beta_start: float = 1e-4, beta_end: float = 0.02) -> np.ndarray:
    betas = np.linspace(float(beta_start), float(beta_end), int(num_timesteps), dtype=float)
    return np.cumprod(1.0 - betas)

