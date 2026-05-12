# Tiny Overfit MSE Upperbound

> Date: 2026-05-12
> Status: weak upperbound / no GPU release

## Question

The tiny known-split denoiser sanity showed no raw-loss membership signal at
`64 / 64`. Before abandoning raw denoising MSE completely, this scout checks an
intentionally favorable upperbound:

If a tiny denoiser is deliberately overfit to only `8` MNIST member images, does
raw denoising MSE separate those members from `64` held-out MNIST test
nonmembers?

This is a mechanism check, not an ablation table. If the scorer is weak even in
this favorable setting, it should not receive more sample/epoch sweeps.

## Setup

- Target: tiny CPU convolutional denoiser trained from scratch.
- Members: first `8` MNIST train images.
- Nonmembers: first `64` MNIST test images.
- Training: `80` epochs, `4` updates per epoch, batch size `8`, CPU.
- Noise levels: `0.10`, `0.20`, `0.35`, `0.50`.
- Score: mean denoising noise-prediction MSE across the same noise levels.
- Membership rule: lower loss is more member-like.

Training loss did decrease strongly:

| Epoch | Train loss |
| ---: | ---: |
| `1` | `0.976294` |
| `2` | `0.923827` |
| `3` | `0.750090` |
| `5` | `0.675636` |
| `10` | `0.583112` |
| `20` | `0.461992` |
| `40` | `0.388998` |
| `80` | `0.316667` |

## Result

| Metric | Value |
| --- | ---: |
| member mean loss | `0.307776` |
| nonmember mean loss | `0.316257` |
| AUC, lower loss = member | `0.552734` |
| AUC, higher loss = member | `0.447266` |
| best ASR, lower loss = member | `0.875000` |
| TPR@1%FPR | `0.0` |
| TPR@0.1%FPR | `0.0` |

The high best-ASR value is not a promotion signal because this is an imbalanced
`8 / 64` board; the low-FPR tail is still zero.

## Verdict

`weak upperbound / no GPU release`.

Raw denoising MSE shows only a small member-lower-loss shift even when the
target is intentionally overfit to eight member images. It does not provide a
reliable strict-tail signal.

Route decision:

- Stop simple raw-denoising-MSE work on MNIST known-split targets.
- Do not run epoch/sample sweeps for this scorer.
- Future known-split work needs a different observable, not more raw MSE.

## Platform and Runtime Impact

None. This is not admitted evidence and does not change exported product rows.
