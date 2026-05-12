# Tiny Known-Split Denoising Sanity

> Date: 2026-05-12
> Status: negative-but-useful / no GPU release

## Question

MNIST/DDPM public raw-loss and `x0` residual scouts are weak. One possible
explanation is that the public checkpoint may not expose an easy signal at the
tiny gate. This sanity check asks a narrower question:

If the project controls the target training set, does a tiny MNIST denoising
target show membership separation under raw denoising loss?

This is not a promoted benchmark. It is a taste-check to decide whether "known
training set + simple denoising loss" is enough to justify larger work.

## Setup

- Target: tiny CPU convolutional denoiser trained from scratch.
- Dataset: Hugging Face `mnist`.
- Members: first `64` MNIST train images used for target training.
- Nonmembers: first `64` MNIST test images, held out.
- Training: `8` epochs, batch size `16`, AdamW, CPU.
- Noise levels: `0.10`, `0.20`, `0.35`, `0.50`.
- Score: mean denoising noise-prediction MSE across the same noise levels.
- Membership rule: lower loss is more member-like.

The run was a one-off inline CPU sanity check, not a new runner or package
format.

## Result

Training loss decreased, so the target did learn the denoising task at this
small scale:

```text
1.0002 -> 0.7177 over 8 epochs
```

But membership separation did not appear:

| Metric | Value |
| --- | ---: |
| member mean loss | `0.705544` |
| nonmember mean loss | `0.708101` |
| AUC, lower loss = member | `0.492676` |
| AUC, higher loss = member | `0.507324` |
| best ASR, lower loss = member | `0.546875` |
| TPR@1%FPR | `0.0` |
| TPR@0.1%FPR | `0.0` |

## Verdict

`negative-but-useful / no GPU release`.

This closes the easy hope that a known training set plus raw denoising loss will
automatically give a useful membership signal. The result does not prove that a
larger or better-trained known-split diffusion model has no signal. It does show
that the next step should not be "train a tiny model and reuse raw loss" unless
there is a sharper mechanism.

Route decision:

- Do not expand this tiny denoiser into an epoch/sample ablation table.
- Do not spend GPU on raw-loss known-split training from this result.
- A valid next route needs a mechanism beyond simple denoising MSE, or an
  external benchmark with documented member/nonmember provenance.

## Platform and Runtime Impact

None. This is not admitted evidence and does not change exported product rows.
