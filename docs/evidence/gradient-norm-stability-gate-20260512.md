# Gradient-Norm Stability Gate

> Date: 2026-05-12
> Status: weakened / no GPU release

## Question

The `8 / 64` tiny overfit scout found a positive final-layer gradient-norm
signal. This gate asks whether that signal survives a less extreme known-split
target:

- more member identities: `16` instead of `8`,
- fewer training epochs: `40` instead of `80`,
- same held-out `64` MNIST test nonmembers,
- same final-layer per-sample gradient L2 score.

This is a stability gate, not a layer sweep or ablation table.

## Setup

- Target: tiny CPU convolutional denoiser trained from scratch.
- Members: first `16` MNIST train images.
- Nonmembers: first `64` MNIST test images.
- Training: `40` epochs, `4` updates per epoch, batch size `16`, CPU.
- Noise levels: `0.10`, `0.20`, `0.35`, `0.50`.
- Scores:
  - raw denoising MSE,
  - final-layer per-sample gradient L2 norm.
- Membership rule: lower score is more member-like.

Training loss still decreased:

```text
0.9825 -> 0.3767 over 40 epochs
```

## Result

| Score | Member mean | Nonmember mean | AUC, lower = member | Best ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw loss | `0.379741` | `0.385097` | `0.535156` | `0.800000` | `0.0` | `0.0` |
| final-layer gradient L2 | `0.510482` | `0.523350` | `0.535156` | `0.812500` | `0.062500` | `0.062500` |

The gradient strict-tail value corresponds to `1 / 16` members recovered at zero
false positives. The AUC advantage from the `8 / 64` overfit scout does not
survive this less extreme gate.

## Verdict

`weakened / no GPU release`.

Gradient norm remains directionally member-lower and retains one zero-FP member,
but the main separation collapses to near-random AUC. This means the previous
positive result was likely tied to extreme overfitting, not a stable second
benchmark signal yet.

Route decision:

- Do not GPU-scale gradient norm.
- Do not run a layer sweep from this result.
- Keep gradient-sensitive observables as a mechanism hint, not a release
  candidate.
- The higher-value next step is provenance acquisition or a sharper observable
  that is not just final-layer gradient L2.

## Platform and Runtime Impact

None. This is not admitted evidence and does not change exported product rows.
