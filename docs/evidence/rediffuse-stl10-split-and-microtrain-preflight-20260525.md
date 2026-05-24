# ReDiffuse STL-10 Split and Microtrain Preflight

> Date: 2026-05-25
> Status: split preflight passed / resource-feasible scout candidate / no membership metric yet / no admitted row

## Question

Does the official ReDiffuse OpenReview STL-10 split justify moving beyond
metadata-only asset review into a bounded DDPM/STL-10 model-pipeline scout?

This is a gate-setting preflight, not a benchmark result. It checks the split
semantics, low-level label leakage, and local CUDA resource envelope for the
official ReDiffuse DDPM code path. It does not train a checkpoint to convergence,
save a checkpoint, sample images, run a membership attack, or promote
Platform/Runtime evidence.

## Assets

| Field | Value |
| --- | --- |
| Paper line | `Towards Black-Box Membership Inference Attack for Diffusion Models` / ReDiffuse |
| Split file | `Rediffuse/DDPM/STL10_train_ratio0.5.npz` |
| Split SHA256 | `14a06133f36c74e7d3cb97dbe74385fb42c22335a7cb955fd9944ca503baca52` |
| Local STL-10 payload | `<DOWNLOAD_ROOT>/shared/datasets/stl10_binary/unlabeled_X.bin` |
| Official code surface | `Rediffuse/DDPM/` |
| CUDA environment | `conda run -n diffaudit-research python` |
| GPU observed | NVIDIA GeForce RTX 4070 Laptop GPU, `7.996 GB` total VRAM |

The default PATH Python is CPU-only for this workspace. The CUDA-capable
surface for this preflight is the `diffaudit-research` conda environment.

## Split Semantics

| Check | Result |
| --- | ---: |
| Member count | `50000` |
| Nonmember count | `50000` |
| Member/nonmember overlap | `0` |
| Union coverage | `0..99999` |
| STL-10 payload rows | `100000` unlabeled images |

The STL-10 split is mechanically valid for a `50k / 50k` member/nonmember
experiment over the STL-10 unlabeled payload. This is materially stronger than
paper-only watch evidence because the exact index arrays are public and
hashable.

One provenance caveat remains: `STL10_train_ratio0.5.npz` and
`TINY-IN_train_ratio0.5.npz` are byte-identical and contain identical indices.
That weakens independent split-provenance interpretation for the supplement,
but it does not by itself invalidate the STL-10 split because the indices still
bind cleanly to the `100000` STL-10 unlabeled rows.

## Low-Level Leakage Preflight

A CPU-only image-statistics probe used all `100000` STL-10 unlabeled images and
`208` low-level features. The goal was to catch trivial source/statistics
confounding before releasing any model-pipeline work.

| Check | Result |
| --- | ---: |
| Feature matrix | `100000 x 208` |
| Top univariate absolute AUC | about `0.502` |
| Linear probe train AUC | `0.556014935` |
| Linear probe test AUC | `0.4994776215625` on an `80000` holdout |

Decision implication: the split does not show obvious low-level source or
image-statistics leakage. Unlike the collaborator Stable Diffusion ReDiffuse
packet, the member label is not trivially explained by a source column or
low-level image-statistics split.

## CUDA Pipeline Calibration

The official DDPM dependencies were checked before running model code. The
`diffaudit-research` environment has CUDA Torch, `torchvision`, `sklearn`, and
`absl`, but does not currently have `tensorboardX` or `pynvml`. Therefore the
official `main.py` was not run unmodified. Temporary calibration scripts
imported the official `UNet` and `GaussianDiffusionTrainer` directly and
bypassed logging/GPU-monitoring dependencies.

| Calibration | Batch | Steps | Status | Elapsed | Peak allocated VRAM | Notes |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| Microtrain pipeline smoke | `4` | `20` | `ready` | `2.823s` | `0.833 GB` | official model/trainer path executes |
| Batch envelope check | `64` | `10` | `ready` | `10.247s` | `4.419 GB` | no checkpoint, no sampling, no MIA metric |

Batch `64` is resource-feasible on the local RTX 4070 Laptop GPU for a bounded
scout. The batch-envelope check observed `0.616 GB` free after completion, so a
longer scout should still use an explicit memory guard, checkpoint cadence, and
stop condition rather than assuming the full training recipe is safe.

## Gate Result

| Gate | Result |
| --- | --- |
| Target identity | Still missing for public replay. No trained third-party STL-10 checkpoint or score packet is public. |
| Split contract | Pass for STL-10. Exact public `50k / 50k` split binds to the local STL-10 unlabeled payload. |
| Low-level leakage | Pass for preflight. Simple image statistics do not separate member/nonmember labels. |
| Official code path | Partial pass. Official `UNet` and `GaussianDiffusionTrainer` run under the CUDA conda environment; official `main.py` still has missing logging/monitoring deps. |
| Resource envelope | Pass for bounded scout. Batch `64` fits within local VRAM for calibration. |
| Metric contract | Not run. No MIA score, ROC, AUC, ASR, or low-FPR metric exists from this preflight. |

## Decision

`split preflight passed / resource-feasible scout candidate / no membership
metric yet / no admitted row`.

The ReDiffuse DDPM/STL-10 route is now eligible for exactly one bounded
model-pipeline scout because it is the clearest available second-dataset route:
the split is exact and public, the local STL-10 payload is present, low-level
leakage was not detected, and the official DDPM model/trainer path is
resource-feasible on the local GPU.

This does not release long training by default. The next run must be a bounded
scout with a frozen hypothesis, command, maximum wall-clock/step budget, memory
guard, checkpoint/output target, and stop condition. It must report whether a
short STL-10 DDPM target can produce a scoreable attack packet; it must not be
an `800k`-step or full-paper reproduction attempt.

## Stop Condition

- Do not claim any membership-inference result from the `20`-step or `10`-step
  calibration runs.
- Do not run full DDPM training or broad hyperparameter sweeps from this note.
- Do not download Tiny-ImageNet or Stable Diffusion assets because the current
  gate is specifically STL-10.
- Do not add new CLI, validators, or long scaffolding before a bounded scout
  actually produces a decision-changing artifact.

## Platform and Runtime Impact

None. This is Research-only preflight evidence. The admitted Platform/Runtime
bundle remains the existing five rows.
