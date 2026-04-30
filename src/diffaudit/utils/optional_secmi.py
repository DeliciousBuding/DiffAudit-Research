from __future__ import annotations

from typing import Callable

import torch


def fallback_ssim(
    x: torch.Tensor,
    y: torch.Tensor,
    *,
    data_range: float,
    size_average: bool = True,
) -> torch.Tensor:
    del data_range
    mse = torch.mean((x.float() - y.float()) ** 2, dim=tuple(range(1, x.ndim)))
    score = 1.0 / (1.0 + mse)
    return score.mean() if size_average else score


def load_secmi_ssim() -> Callable[..., torch.Tensor]:
    try:
        from external.SecMI.mia_evals.measures.ssim import ssim
    except ImportError:
        return fallback_ssim
    return ssim
