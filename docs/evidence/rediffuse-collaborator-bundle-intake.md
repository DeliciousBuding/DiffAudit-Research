# ReDiffuse Collaborator Bundle Intake

> Date: 2026-05-09
> Status: candidate baseline bundle; not admitted evidence yet

## What Arrived

A collaborator provided a `DDIMrediffuse` folder containing:

- `attack.py`
- `components.py`
- `model_unet.py`
- `dataset_utils.py`
- `resnet.py`
- `diffusion.py`
- `train.py`
- `environment.yml`
- `CIFAR10_train_ratio0.5.npz`
- `CIFAR100_train_ratio0.5.npz`

The collaborator later provided `train1.py` as the training script and stated
that the split follows the paper's ratio0.5 npz setting with random seed `42`.

The raw bundle is stored outside Git at:

`<DIFFAUDIT_ROOT>/Download/shared/supplementary/collaborator-ddim-rediffuse-20260509/`

The collaborator-provided 750k checkpoint is stored outside Git at:

`<DIFFAUDIT_ROOT>/Download/shared/weights/ddim-cifar10-step750000/`

## Immediate Findings

- The earlier single-file `attack.py` transfer was incomplete; this bundle now supplies the missing modules.
- `components.py` defines `ReDiffuseAttacker`, plus `SecMIAttacker`, `PIA`, `PIAN`, and `NaiveAttacker`.
- `CIFAR10_train_ratio0.5.npz` has SHA256 `aca922ecee25ef00dc6b6377ebaf7875dfcc77c2cdfe27c873b26a65134aa0c0`, matching the current PIA CIFAR10 ratio0.5 split.
- `model_unet.py` can load the collaborator 750k checkpoint `ema_model` with zero missing keys and zero unexpected keys.
- A CPU forward probe on the 750k checkpoint produced output shape `[1, 3, 32, 32]`.
- `train1.py` uses `FLAGS.dataset = "CIFAR10"`, loads `./CIFAR10_train_ratio0.5.npz`, reads `mia_train_idxs`, and filters torchvision CIFAR10 train data to those indices before training.
- A Research-side runtime adapter now passes CPU 2/2 and CUDA 8/8 ReDiffuse compatibility smokes. See [rediffuse-runtime-smoke-result.md](rediffuse-runtime-smoke-result.md).
- A CUDA 64/64 small packet has run on the direct-distance scoring surface. See [rediffuse-cifar10-small-packet.md](rediffuse-cifar10-small-packet.md).

## Interpretation

This bundle is useful. It is not just a loose script; it is a candidate baseline implementation that can align the Research repo with the collaborator's current DDIM/ReDiffuse experiment path.

It is still not admitted evidence because no metric parity has been checked against collaborator-reported results. The current Research packets use a direct first-step distance scorer rather than the collaborator script's second-stage ResNet classifier.

The 750k checkpoint is now better grounded as a CIFAR10 ratio0.5-member-trained
target model by collaborator statement plus training-script evidence. Two
provenance gaps remain: `train1.py` does not set seed `42` in code, and its
default `total_steps = 200000` does not match the checkpoint's stored
`step = 750000`. Treat seed `42` and the 750k training length as collaborator
statements until the exact runtime override or final training script is
confirmed.

## Mainline Decision

Keep the existing 800k PIA CIFAR10 checkpoint as the current gray-box mainline target because its provenance is already workspace-verified through the PIA upstream README-linked pretrained bundle.

Use the 750k checkpoint and `DDIMrediffuse` bundle for a bounded compatibility review:

1. Run a minimal ReDiffuse smoke on 750k with a tiny CIFAR10 subset.
2. If the runner works, map the same protocol onto the existing 800k checkpoint when path layout permits.
3. Compare ReDiffuse with the existing PIA/SecMI baselines under the same CIFAR10 ratio0.5 split.
4. Promote only reproduced metrics and low-FPR fields into admitted evidence.

## Open Questions

- Was `train1.py` run with a command-line or manual override changing `total_steps` from `200000` to `750000` or `800000`?
- Where was seed `42` set during training?
- Does `train.py` reproduce the transferred 750k checkpoint configuration?
- What metric values does the collaborator expect for ReDiffuse on this checkpoint?

## Verdict

Positive intake. The bundle is complete enough to justify a CPU/GPU-light compatibility task, but not enough to replace the existing PIA/SecMI gray-box baseline or to generate a production report.
