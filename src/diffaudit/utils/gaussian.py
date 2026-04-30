"""Gaussian scoring helpers shared by attack modules."""

from __future__ import annotations

import math

import numpy as np


def fit_univariate_gaussian(values: np.ndarray, *, min_variance: float = 1e-12) -> tuple[float, float]:
    mean = float(np.asarray(values, dtype=float).mean())
    variance = float(np.asarray(values, dtype=float).var())
    return mean, max(variance, float(min_variance))


def gaussian_log_likelihood_ratio(
    values: np.ndarray,
    *,
    member_params: tuple[float, float],
    nonmember_params: tuple[float, float],
) -> np.ndarray:
    member_mean, member_var = member_params
    nonmember_mean, nonmember_var = nonmember_params
    values = np.asarray(values, dtype=float)
    member_ll = -0.5 * (np.log(2.0 * math.pi * member_var) + ((values - member_mean) ** 2) / member_var)
    nonmember_ll = -0.5 * (np.log(2.0 * math.pi * nonmember_var) + ((values - nonmember_mean) ** 2) / nonmember_var)
    return member_ll - nonmember_ll

