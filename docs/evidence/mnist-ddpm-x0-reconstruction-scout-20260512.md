# MNIST DDPM X0 Reconstruction Scout

> Date: 2026-05-12
> Status: weak / no GPU release

## Question

MNIST/DDPM has cleaner membership semantics than Beans/SD1.5: the target model
is `1aurent/ddpm-mnist`, members are MNIST train images, and nonmembers are
MNIST test images. Raw PIA-style noise-prediction loss was already weak.

This scout asks a different, still cheap question: even if raw loss is weak, do
members reconstruct to predicted `x0` with lower pixel or edge residual than
nonmembers?

## Setup

- Model: `1aurent/ddpm-mnist`
- Dataset: Hugging Face `mnist`
- Member split: first `16` train images
- Nonmember split: first `16` test images
- Timesteps: `50`, `100`, `200`, `350`, `500`, `650`, `800`
- Device: CPU
- Scorers:
  - raw noise-prediction MSE, included only as a same-run reference
  - predicted-`x0` pixel MSE
  - predicted-`x0` pixel L1
  - predicted-`x0` Sobel-edge L1
- Membership rule: lower residual is more member-like

The run was a one-off inline CPU scout, not a new CLI or validator. The useful
result is copied into this evidence note directly, so no ignored artifact needs
to be force-added.

## Result

| Score | Member mean | Nonmember mean | AUC, lower = member | Best ASR |
| --- | ---: | ---: | ---: | ---: |
| raw loss mean | `0.031127` | `0.031135` | `0.507812` | `0.593750` |
| `x0` MSE mean | `0.121056` | `0.124516` | `0.550781` | `0.625000` |
| `x0` L1 mean | `0.153724` | `0.158342` | `0.554688` | `0.625000` |
| `x0` edge L1 mean | `0.096276` | `0.099231` | `0.554688` | `0.593750` |

Best single-timestep values were small and unstable:

| Score | Best timestep | Best AUC, lower = member |
| --- | ---: | ---: |
| raw loss | `650` | `0.644531` |
| `x0` MSE | `650` | `0.644531` |
| `x0` L1 | `650` | `0.656250` |
| `x0` edge L1 | `800` | `0.636719` |

## Verdict

`weak / no GPU release`.

The `x0` reconstruction residuals are slightly above raw-loss mean AUC, but the
effect is still too small for GPU expansion or a larger same-scorer table. This
rules out a simple "members reconstruct cleaner to x0" explanation at this
tiny gate.

Route decision:

- Do not expand MNIST/DDPM raw loss or simple `x0` residual scorers.
- Do not build a new toolchain around this scorer.
- If MNIST/DDPM remains active, it needs a sharper mechanism than raw loss or
  simple reconstruction residual.
- The cleaner next route is likely a tiny known-split target where the project
  controls the target training data and can test one simple signal under true
  membership semantics.

## Platform and Runtime Impact

None. This is not admitted evidence and does not change exported product rows.
