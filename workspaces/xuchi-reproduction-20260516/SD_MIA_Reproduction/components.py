"""
Attacker implementations for membership inference attack on diffusion models.
Paper: "Towards Black-Box Membership Inference Attack for Diffusion Models" (ICML 2025)

Classes:
  ReDiffuseAttacker  — Algorithm 1 (our method, black-box)
  SecMIAttacker      — baseline (Duan et al., 2023)
  PIA                — baseline (Kong et al., 2023)
  PIAN               — baseline (Kong et al., 2023)
  NaiveAttacker      — random-noise baseline
"""

import torch
from typing import Callable


class EpsGetter:
    def __init__(self, model):
        self.model = model

    def __call__(self, xt: torch.Tensor, condition=None, noise_level=None, t=None) -> torch.Tensor:
        raise NotImplementedError


class Attacker:
    def __init__(self, betas, interval, average, attack_num, k,
                 eps_getter: EpsGetter, normalize: Callable = None,
                 denormalize: Callable = None):
        self.eps_getter  = eps_getter
        self.betas       = betas
        # noise_level[t] = ᾱ_t = ∏_{i=0}^{t} (1 - β_i)
        self.noise_level = torch.cumprod(1 - betas, dim=0).float()
        self.interval    = interval
        self.k           = k
        self.average     = average
        self.attack_num  = attack_num
        self.normalize   = normalize
        self.denormalize = denormalize
        self.T           = len(self.noise_level)

    def __call__(self, x0, condition=None):
        raise NotImplementedError

    def get_xt_coefficient(self, step):
        return self.noise_level[step] ** 0.5, (1 - self.noise_level[step]) ** 0.5

    def get_xt(self, x0, step, eps):
        a, b = self.get_xt_coefficient(step)
        return a * x0 + b * eps

    def _normalize(self, x):
        return self.normalize(x) if self.normalize is not None else x

    def _denormalize(self, x):
        return self.denormalize(x) if self.denormalize is not None else x


class DDIMAttacker(Attacker):
    """Base class for DDIM-based attackers."""

    def get_y(self, x, step):
        return x / self.noise_level[step] ** 0.5

    def get_x(self, y, step):
        return y * self.noise_level[step] ** 0.5

    def get_p(self, step):
        return (1 / self.noise_level[step] - 1) ** 0.5

    def __call__(self, x0, condition=None):
        x0 = self._normalize(x0)
        intermediates        = self.ddim_reverse(x0, condition)
        intermediates_denoise = self.ddim_denoise(x0, intermediates, condition)
        return torch.stack(intermediates), torch.stack(intermediates_denoise)

    def distance(self, x0, x1):
        return ((x0 - x1).abs() ** 2).flatten(2).sum(dim=-1)

    def ddim_reverse(self, x0, condition):
        raise NotImplementedError

    def ddim_denoise(self, x0, intermediates, condition):
        raise NotImplementedError


class ReDiffuseAttacker(DDIMAttacker):
    """
    Algorithm 1 — REDIFFUSE (Section 4.2 & 4.3)

    Variation API for Stable Diffusion (Section 4.3):
      z_t = sqrt(ᾱ_t) * z + sqrt(1 - ᾱ_t) * ε        (forward, step t)
      z_0 = Φ_θ(z_t, 0)                                 (DDIM reverse, k steps)

    Run n=`average` independent reconstructions, then average in pixel space
    (done in decode_reconstruction_images in attack.py).
    """

    def ddim_reverse(self, x0, condition):
        # Store x0 once per attack step (only used as pass-through reference)
        terminal_step = self.interval * self.attack_num
        return [x0 for _ in range(0, terminal_step, self.interval)]

    def ddim_denoise(self, x0, intermediates, condition):
        """
        For each attack step t, independently sample n=average reconstructions.
        Each reconstruction:
          1. Add noise:  z_t = sqrt(ᾱ_t)*z + sqrt(1-ᾱ_t)*ε  (fresh ε each time)
          2. DDIM denoise from t → 0 in k-step increments
        Returns a list of tensors, each of shape [average, B, C, H, W].
        """
        intermediates_denoise = []
        terminal_step = self.interval * self.attack_num

        for step in range(self.interval, terminal_step + self.interval, self.interval):
            alpha_bar_t = self.noise_level[step]

            x_all = []
            for _ in range(self.average):
                # Forward process: z_t = sqrt(ᾱ_t)*z + sqrt(1-ᾱ_t)*ε
                epsilon = torch.randn_like(x0)
                x_t = alpha_bar_t.sqrt() * x0 + (1 - alpha_bar_t).sqrt() * epsilon

                # DDIM reverse: t → 0 in steps of k
                # Formula (Section 3):
                #   x_{t-k} = sqrt(ᾱ_{t-k}) * (x_t - sqrt(1-ᾱ_t)*ε_θ) / sqrt(ᾱ_t)
                #             + sqrt(1-ᾱ_{t-k}) * ε_θ
                for j in range(step, 0, -self.k):
                    alpha_t      = self.noise_level[j]
                    alpha_t_prev = self.noise_level[j - self.k]

                    eps_pred = self.eps_getter(x_t, condition, self.noise_level, j)

                    x_t = (
                        (x_t - (1 - alpha_t).sqrt() * eps_pred) / alpha_t.sqrt()
                        * alpha_t_prev.sqrt()
                        + (1 - alpha_t_prev).sqrt() * eps_pred
                    )

                x_all.append(x_t)

            intermediates_denoise.append(torch.stack(x_all, dim=0))  # [n, B, C, H, W]

        return intermediates_denoise


class SecMIAttacker(DDIMAttacker):
    """SecMI (Duan et al., 2023) — requires U-Net access."""

    def ddim_reverse(self, x0, condition):
        intermediates = [x0]
        terminal_step = self.interval * self.attack_num
        x = x0
        for step in range(0, terminal_step, self.interval):
            y_next = (self.eps_getter(x, condition, self.noise_level, step)
                      * (self.get_p(step + self.interval) - self.get_p(step))
                      + self.get_y(x, step))
            x = self.get_x(y_next, step + self.interval)
            intermediates.append(x)
        return intermediates

    def ddim_denoise(self, x0, intermediates, condition):
        intermediates_denoise = []
        terminal_step = self.interval * self.attack_num
        for idx, step in enumerate(range(self.interval, terminal_step + self.interval, self.interval), 1):
            x = intermediates[idx]
            y_prev = (self.eps_getter(x, condition, self.noise_level, step)
                      * (self.get_p(step - self.interval) - self.get_p(step))
                      + self.get_y(x, step))
            x_prev = self.get_x(y_prev, step - self.interval)
            intermediates_denoise.append(x_prev)
            if idx == len(intermediates) - 1:
                del intermediates[-1]
        return intermediates_denoise


class PIA(DDIMAttacker):
    """PIA (Kong et al., 2023) — requires U-Net access."""

    def ddim_reverse(self, x0, condition):
        terminal_step = self.interval * self.attack_num
        eps = self.eps_getter(x0, condition, self.noise_level, 0)
        return [eps for _ in reversed(range(0, terminal_step, self.interval))]

    def ddim_denoise(self, x0, intermediates, condition):
        intermediates_denoise = []
        terminal_step = self.interval * self.attack_num
        for idx, step in enumerate(range(self.interval, terminal_step + self.interval, self.interval)):
            eps      = intermediates[idx]
            eps_back = self.eps_getter(self.get_xt(x0, step, eps), condition, self.noise_level, step)
            intermediates_denoise.append(eps_back)
        return intermediates_denoise


class PIAN(DDIMAttacker):
    """PIAN (Kong et al., 2023) — requires U-Net access."""

    def ddim_reverse(self, x0, condition):
        terminal_step = self.interval * self.attack_num
        eps = self.eps_getter(x0, condition, self.noise_level, 0)
        eps = eps / eps.abs().mean(list(range(1, eps.ndim)), keepdim=True) * (2 / torch.pi) ** 0.5
        return [eps for _ in reversed(range(0, terminal_step, self.interval))]

    def ddim_denoise(self, x0, intermediates, condition):
        intermediates_denoise = []
        terminal_step = self.interval * self.attack_num
        for idx, step in enumerate(range(self.interval, terminal_step + self.interval, self.interval)):
            eps      = intermediates[idx]
            eps_back = self.eps_getter(self.get_xt(x0, step, eps), condition, self.noise_level, step)
            intermediates_denoise.append(eps_back)
        return intermediates_denoise


class NaiveAttacker(DDIMAttacker):
    """Random-noise baseline."""

    def ddim_reverse(self, x0, condition):
        terminal_step = self.interval * self.attack_num
        return [torch.randn_like(x0) for _ in reversed(range(0, terminal_step, self.interval))]

    def ddim_denoise(self, x0, intermediates, condition):
        intermediates_denoise = []
        terminal_step = self.interval * self.attack_num
        for idx, step in enumerate(range(self.interval, terminal_step + self.interval, self.interval)):
            eps      = intermediates[idx]
            eps_back = self.eps_getter(self.get_xt(x0, step, eps), condition, self.noise_level, step)
            intermediates_denoise.append(eps_back)
        return intermediates_denoise
