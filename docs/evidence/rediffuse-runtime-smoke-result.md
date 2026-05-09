# ReDiffuse Runtime Smoke Result

> Date: 2026-05-09
> Status: CPU and CUDA compatibility smoke passed

## Contract

- Target: collaborator 750k DDIM checkpoint
- Bundle: collaborator `DDIMrediffuse`
- Dataset: CIFAR10
- Split: `CIFAR10_train_ratio0.5.npz`
- Split SHA256: `aca922ecee25ef00dc6b6377ebaf7875dfcc77c2cdfe27c873b26a65134aa0c0`
- Device used for passed smoke: `cpu`
- Smoke size: 2 member + 2 nonmember
- Smoke parameters: `attack_num = 1`, `interval = 1`, `average = 1`, `k = 1`
- Scoring mode: direct first-step distance mean

## Result

The CPU smoke passed and generated `summary.json` plus `scores.json` in a
temporary workspace.

Metrics on the 2/2 smoke:

- `AUC = 0.75`
- `ASR = 0.75`
- `TPR@1%FPR = 0.5`
- `TPR@0.1%FPR = 0.5`
- `member_score_mean = -0.007312`
- `nonmember_score_mean = -0.007909`

These numbers are only compatibility evidence. The packet is too small for a
research claim.

## CUDA Smoke

The planned `8/8` CUDA smoke passed under the `diffaudit-research` conda
environment.

- Workspace: `workspaces/gray-box/runs/rediffuse-cifar10-750k-runtime-smoke-20260509-gpu-8`
- Device: `cuda`
- Smoke size: 8 member + 8 nonmember
- Parameters: `attack_num = 1`, `interval = 200`, `average = 10`, `k = 100`

Metrics on the 8/8 CUDA smoke:

- `AUC = 0.859375`
- `ASR = 0.875`
- `TPR@1%FPR = 0.125`
- `TPR@0.1%FPR = 0.125`
- `member_score_mean = -0.045558`
- `nonmember_score_mean = -0.075506`

The system Python environment reported no CUDA, but the project conda
environment reported one CUDA device: `NVIDIA GeForce RTX 4070 Laptop GPU`.

## ResNet Scorer Smoke

After the collaborator-style second-stage scorer was integrated, a GPU-light
`resnet` scoring smoke also passed.

- Workspace: `workspaces/gray-box/runs/rediffuse-cifar10-750k-resnet-smoke-20260509-gpu-8-v2`
- Device: `cuda`
- Input size: 8 member + 8 nonmember
- Scorer split: 4 member + 4 nonmember train, 4 member + 4 nonmember test
- Parameters: `attack_num = 1`, `interval = 200`, `average = 10`, `k = 100`, `scorer_epochs = 1`

Metrics on the 4/4 held-out scorer split:

- `AUC = 0.1875`
- `ASR = 0.5`
- `TPR@1%FPR = 0.0`
- `TPR@0.1%FPR = 0.0`
- `member_score_mean = 0.063185`
- `nonmember_score_mean = 0.065497`

This is only an end-to-end scorer compatibility check. It is intentionally too
small and under-trained for a research claim.

## Caveats

- The CPU and first CUDA smokes use a direct distance scorer to validate the
  ReDiffuse path before any larger run.
- The ResNet scorer smoke proves the second-stage path runs, but does not yet
  establish parity with the collaborator script's expected metrics.
- `seed = 42` remains a collaborator statement, not script-level evidence.
- `train1.py` defaults to `total_steps = 200000`, while the checkpoint stores `step = 750000`.

## Verdict

Positive compatibility result. The Research adapter can load the collaborator
bundle, load the 750k checkpoint, instantiate `ReDiffuseAttacker`, read the
CIFAR10 ratio0.5 split, and score a tiny member/nonmember packet.

Do not promote ReDiffuse to admitted gray-box evidence until the direct-distance
surface is compared with the collaborator script's second-stage ResNet scoring
contract or explicitly scoped as a separate Research surface.
