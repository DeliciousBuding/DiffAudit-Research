# ReDiffuse 750k Exact-Replay Packet

> Date: 2026-05-10
> Status: candidate-only; weak strict-tail; no admitted promotion

## Question

Does the collaborator ReDiffuse 750k checkpoint show a usable membership signal
when Research uses the explicit collaborator checkpoint-selection contract?

## Contract

This packet uses:

- checkpoint: collaborator 750k DDIM checkpoint
- dataset: CIFAR10 train split
- split: collaborator `CIFAR10_train_ratio0.5.npz`, SHA256
  `aca922ecee25ef00dc6b6377ebaf7875dfcc77c2cdfe27c873b26a65134aa0c0`,
  hash-checked against the known PIA/ReDiffuse split
- scoring mode: `resnet_collaborator_replay`
- checkpoint policy: `collaborator_counter`
- metric convention: raw logits as higher-is-member, equivalent to the
  collaborator negated-logit plus member-lower ROC convention

Command:

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit run-rediffuse-runtime-packet `
  --workspace workspaces/gray-box/runs/rediffuse-cifar10-750k-exact-replay-20260510-gpu-64 `
  --device cuda `
  --max-samples 64 `
  --batch-size 8 `
  --attack-num 1 `
  --interval 200 `
  --average 10 `
  --k 100 `
  --scoring-mode resnet_collaborator_replay `
  --scorer-train-portion 0.2 `
  --scorer-epochs 15 `
  --scorer-batch-size 128
```

## Result

The packet completed on CUDA.

| Metric | Value |
| --- | --- |
| Packet status | `ready` |
| Checkpoint step | `750000` |
| Max samples requested | `64 / 64` |
| Scorer train count per split | `12` |
| Scorer test count per split | `52` |
| AUC | `0.702293` |
| ASR | `0.682692` |
| TPR@1%FPR | `0.019231` |
| TPR@0.1%FPR | `0.019231` |
| Member score mean | `0.386715` |
| Nonmember score mean | `0.383157` |
| Selected held-out accuracy | `0.5` |
| Best held-out accuracy | `0.5` |

## Verdict

`candidate-only`.

The exact-replay packet has a real but modest AUC signal. It does not provide a
strong strict-tail result: with 52 held-out samples per split, both low-FPR
fields correspond to one empirical member hit and remain finite-count evidence,
not calibrated sub-percent FPR. The ResNet scorer's held-out accuracy is `0.5`,
so the second-stage classifier itself is not a strong discriminator.

This result is useful for collaborator baseline alignment, but it is not
admitted evidence and should not replace the admitted PIA gray-box line.

## Decision

- Do not promote ReDiffuse to admitted.
- Do not run 800k as an automatic shortcut.
- Keep 750k exact replay as collaborator-grounded candidate evidence.
- Reopen only if there is a new scorer hypothesis or a paper-faithful
  reproduction contract that addresses strict-tail weakness.

## Platform and Runtime Impact

No Platform or Runtime changes are needed.
