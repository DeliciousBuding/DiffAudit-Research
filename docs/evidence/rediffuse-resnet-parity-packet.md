# ReDiffuse ResNet Parity Packet

> Date: 2026-05-10
> Status: negative-but-useful; scoring-contract parity unresolved

## Question

Can the collaborator-style second-stage ResNet scorer produce an interpretable
ReDiffuse membership signal on the collaborator 750k CIFAR10 checkpoint?

This packet tests scoring-contract parity. It is not an admitted benchmark and
does not change the admitted PIA/SecMI gray-box evidence.

## Command

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit run-rediffuse-runtime-packet `
  --workspace workspaces/gray-box/runs/rediffuse-cifar10-750k-resnet-parity-20260510-gpu-64 `
  --device cuda `
  --max-samples 64 `
  --batch-size 8 `
  --attack-num 1 `
  --interval 200 `
  --average 10 `
  --k 100 `
  --scoring-mode resnet `
  --scorer-train-portion 0.2 `
  --scorer-epochs 15 `
  --scorer-batch-size 128
```

Canonical run anchor:
`workspaces/gray-box/runs/rediffuse-cifar10-750k-resnet-parity-20260510-gpu-64/summary.json`.

## Contract

- Dataset: CIFAR10.
- Split: collaborator `CIFAR10_train_ratio0.5.npz`.
- Split hash:
  `aca922ecee25ef00dc6b6377ebaf7875dfcc77c2cdfe27c873b26a65134aa0c0`.
- Checkpoint: collaborator DDIM 750k checkpoint.
- Checkpoint step: `750000`.
- Device: CUDA.
- Scoring mode: `resnet`.
- Packet cap: requested `64/64`; effective held-out scoring count `52/52`
  because `12/12` samples per split were used to train the scorer.

## Result

| Metric | Value |
| --- | --- |
| AUC | `0.411982` |
| ASR | `0.538462` |
| TPR@1%FPR | `0.0` |
| TPR@0.1%FPR | `0.0` |
| Member score mean | `-0.014624` |
| Nonmember score mean | `-0.014467` |
| ResNet train accuracy, last epoch | `1.0` |
| ResNet test accuracy, best | `0.5` |
| Elapsed seconds | `11.595808` |

All runtime readiness checks passed: bundle files, split hash, checkpoint, EMA
weights, dataset root, module loading, model loading, attacker construction,
preview forward, and member/nonmember score generation.

## Interpretation

The ResNet scorer ran, but it did not produce a usable membership signal under
the frozen `64/64` parity gate. The held-out AUC is below random, the best
ResNet held-out accuracy is random, and both low-FPR metrics are zero.

This blocks the direct claim that the current Research adapter has recovered a
paper-faithful ReDiffuse scoring contract comparable with PIA/SecMI. The
earlier `first_step_distance_mean` packet remains a candidate Research surface,
not a collaborator-style or admitted gray-box baseline.

The effective `52/52` scoring count also means the packet should not be scaled
blindly. A larger ResNet training split might be a different hypothesis, but it
would need a new CPU contract explaining why the second-stage scorer should
generalize instead of overfitting a tiny score table.

## Verdict

Negative but useful.

- Do not promote ReDiffuse to admitted evidence.
- Do not compare this ResNet packet against PIA/SecMI as an equivalent
  paper-faithful baseline.
- Do not release an automatic 800k ReDiffuse metrics packet from this result.
- Keep the 800k checkpoint note as runtime compatibility only.
- If ReDiffuse continues, the next step must be a CPU contract review for the
  direct-distance surface or a better-scoped second-stage scorer hypothesis.

## Platform and Runtime Impact

No Platform or Runtime changes are needed.
