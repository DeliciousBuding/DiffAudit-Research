# Fashion-MNIST DDPM PIA-Loss Scout

Date: 2026-05-13

## Question

After CommonCanvas and final-layer gradient-prototype results were weak, can a
small public Fashion-MNIST DDPM give a cleaner second split for a PIA-style
training-loss signal?

## Contract

- Target model: `ynwag9/fashion_mnist_ddpm_32`.
- Target type: diffusers `DDPMPipeline`.
- Member split: torchvision Fashion-MNIST train split, first `64` samples.
- Nonmember split: torchvision Fashion-MNIST test split, first `64` samples.
- Score: negative mean epsilon-MSE over fixed timesteps
  `[50, 100, 200, 400, 700, 900]`; higher means more member-like.
- Device: local CUDA, RTX 4070.

Important boundary: the Hugging Face repo has no README/model card, so this is
only a scout. It assumes the model was trained on the standard Fashion-MNIST
train split because of the repository identity and pipeline content. It is not
admitted provenance.

## Result

Artifact:

`workspaces/black-box/artifacts/fashion-mnist-ddpm-pia-loss-scout-20260513.json`

Metrics:

| Metric | Value |
| --- | ---: |
| AUC | `0.535889` |
| ASR | `0.570312` |
| TPR@1%FPR | `0.03125` |
| TPR@0.1%FPR | `0.03125` |

Per-timestep AUC:

| Timestep | AUC |
| --- | ---: |
| `50` | `0.533936` |
| `100` | `0.520996` |
| `200` | `0.515869` |
| `400` | `0.496582` |
| `700` | `0.498291` |
| `900` | `0.552246` |

## Decision

Close this candidate by default.

The result is weak and the provenance is not strong enough to justify seed
repeats, timestep sweeps, or a larger Fashion-MNIST packet. This does not
produce transferable evidence for the current PIA-style loss signal. The next
move still needs either a genuinely cleaner asset package or a genuinely
different mechanism.
