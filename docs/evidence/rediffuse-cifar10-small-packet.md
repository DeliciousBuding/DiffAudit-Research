# ReDiffuse CIFAR10 Small Packet

> Date: 2026-05-09
> Status: positive compatibility packet; not admitted benchmark evidence

## Contract

- Target: collaborator 750k DDIM checkpoint
- Bundle: collaborator `DDIMrediffuse`
- Dataset: CIFAR10
- Split: `CIFAR10_train_ratio0.5.npz`
- Split SHA256: `aca922ecee25ef00dc6b6377ebaf7875dfcc77c2cdfe27c873b26a65134aa0c0`
- Workspace: `workspaces/gray-box/runs/rediffuse-cifar10-750k-runtime-packet-20260509-gpu-64`
- Device: `cuda`
- Packet size: 64 member + 64 nonmember
- Parameters: `attack_num = 1`, `interval = 200`, `average = 10`, `k = 100`
- Scoring mode: direct first-step distance mean

## Result

- `AUC = 0.8125`
- `ASR = 0.773438`
- `TPR@1%FPR = 0.078125`
- `TPR@0.1%FPR = 0.078125`
- `member_score_mean = -0.046432`
- `nonmember_score_mean = -0.070725`
- `elapsed_seconds = 10.51633`

## Interpretation

The packet confirms that the collaborator ReDiffuse bundle is runnable in the
Research environment against the 750k checkpoint and the shared CIFAR10
ratio0.5 split.

This is not yet a paper-faithful ReDiffuse reproduction. The Research adapter
uses a direct first-step distance score to establish a stable compatibility
surface. The adapter now also exposes a `resnet` scoring mode that follows the
collaborator script's second-stage residual-classifier contract, but this 64/64
packet did not use it. Those two scoring contracts must not be collapsed.

## Next Decision

The next CPU/GPU-light task is to run a bounded parity packet with
`--scoring-mode resnet`, or explicitly keep the direct-distance surface as a
separate Research baseline. Do not compare this packet directly against PIA or
SecMI admitted metrics without marking the scoring-mode difference.

## Verdict

Positive but bounded. ReDiffuse is now runnable as a Research candidate baseline
on 750k/CIFAR10, but it is not admitted gray-box evidence and not ready for a
production report.
