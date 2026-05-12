# Tiny Known-Split Gradient Prototype Alignment

> Date: 2026-05-13
> Status: negative-or-weak / close same-family gradient observable by default

## Question

The previous `16 / 64` stability gate weakened final-layer gradient L2 to
near-random AUC. This test asks whether a stronger gradient-sensitive observable
can still rescue the known-split MNIST direction:

> Do member per-sample final-layer gradients align more with a member-gradient
> prototype than nonmember gradients do?

This is deliberately optimistic: the prototype is built from the known member
set, with leave-one-out scoring for members. If this oracle-style mechanism
scout is weak, there is no reason to keep polishing final-layer gradient
variants.

## Setup

- Target: tiny convolutional MNIST denoiser trained from scratch.
- Device: local CUDA (`RTX 4070 Laptop GPU`), `torch = 2.5.1+cu121`.
- Members: first `64` MNIST train images.
- Nonmembers: first `64` MNIST test images.
- Training: `8` epochs, batch size `16`.
- Noise levels: `0.10`, `0.20`, `0.35`, `0.50`.
- Score: `final_layer_gradient_prototype_cosine`, higher is more member-like.
- Reference only: raw denoising loss from the same run.

Training loss decreased clearly:

```text
0.118300 -> 0.022374
```

## Result

| Score | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| final-layer gradient prototype cosine | `0.500977` | `0.562500` | `0.0` | `0.0` |
| raw loss reference | `0.549072` | `0.593750` | `0.0` | `0.0` |

The gradient-prototype score is effectively random despite the optimistic
prototype construction. The raw-loss reference is also weak and has no
strict-tail recovery.

Artifact:

```text
workspaces/black-box/artifacts/tiny-known-split-gradient-prototype-alignment-20260513.json
```

## Verdict

`negative-or-weak / no GPU release / close same-family gradient observable by default`.

This result does not say gradient information can never work. It says the
current tiny known-split path has now failed under raw loss, final-layer
gradient norm stability, and an oracle-style final-layer gradient direction
prototype. Continuing with more final-layer gradient variants would be
low-value ablation filling.

Route decision:

- Do not run layer sweeps, seed sweeps, or more final-layer gradient variants.
- Do not promote this to admitted evidence or Platform/Runtime consumption.
- Reopen only with a genuinely different mechanism, not another norm/cosine
  wrapper over the same final-layer gradient surface.

## Platform and Runtime Impact

None. This is Research-only negative evidence and does not change exported
product rows.
