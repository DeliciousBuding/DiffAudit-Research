# Tiny Overfit Gradient-Norm Scout

> Date: 2026-05-12
> Status: positive mechanism scout / no GPU release

## Question

Raw denoising MSE stayed weak even when a tiny denoiser was deliberately overfit
to `8` MNIST member images. This scout asks whether a different observable,
final-layer per-sample gradient norm, exposes membership on that same favorable
known-split target.

The point is not to create a new framework. The point is to decide whether
future known-split work should move away from simple MSE toward a
gradient-sensitive signal.

## Setup

- Target: tiny CPU convolutional denoiser trained from scratch.
- Members: first `8` MNIST train images.
- Nonmembers: first `64` MNIST test images.
- Training: `80` epochs, `4` updates per epoch, batch size `8`, CPU.
- Noise levels: `0.10`, `0.20`, `0.35`, `0.50`.
- Score:
  - raw denoising MSE, included as same-run reference,
  - final-layer per-sample gradient L2 norm.
- Membership rule: lower score is more member-like.

The gradient score uses only the final convolution layer to keep this a tiny
mechanism scout, not a new implementation surface.

## Result

| Score | Member mean | Nonmember mean | AUC, lower = member | Best ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw loss | `0.306236` | `0.319939` | `0.648438` | `0.888889` | `0.0` | `0.0` |
| final-layer gradient L2 | `0.520331` | `0.608139` | `0.734375` | `0.902778` | `0.125` | `0.125` |

On this imbalanced `8 / 64` board, the strict-tail value corresponds to
recovering `1 / 8` members at zero false positives. That is small, but it is
qualitatively different from the raw-MSE scouts, which had zero strict-tail
recovery.

## Verdict

`positive mechanism scout / no GPU release`.

This is the first useful signal in the current second-benchmark reset after the
Beans/SD1.5 semantic correction. It does not prove transfer, admission, or a
product row. It does show that, under true known-split membership semantics,
gradient-sensitive observables can expose overfit members better than simple
denoising MSE.

Route decision:

- Stop raw-MSE variants.
- Keep gradient-sensitive observables as the next mechanism candidate.
- Do not GPU-scale yet. A valid next step is a CPU-only stability check on a
  less extreme known-split target or a provenance-backed external benchmark.
- Do not turn this into a broad layer sweep unless a stability gate first
  shows the signal survives outside `8` deliberately overfit members.

## Platform and Runtime Impact

None. This is not admitted evidence and does not change exported product rows.
