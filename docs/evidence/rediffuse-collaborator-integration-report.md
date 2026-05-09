# ReDiffuse Collaborator Integration Report

> Date: 2026-05-09
> Status: integrated as a candidate gray-box baseline; not admitted evidence

## Plain-Language Summary

The collaborator package is useful, but it is not an attack result by itself.
It gives Research a runnable DDIM/ReDiffuse baseline path: external ReDiffuse
code, a CIFAR10 member/nonmember split, and a 750k DDIM checkpoint. Research
now has an adapter that can load those assets, instantiate the collaborator
`ReDiffuseAttacker`, and produce bounded membership-inference scores.

This does not replace the existing PIA/SecMI line. The current ReDiffuse packet
uses a direct first-step distance score, while the collaborator script also
contains a second-stage ResNet scoring path. Those scoring contracts are
different and must be reviewed before any direct comparison.

## Asset Placement

Raw collaborator assets stay outside Git.

| Asset | Location | Git policy |
| --- | --- | --- |
| `DDIMrediffuse` code bundle | `<DIFFAUDIT_ROOT>/Download/shared/supplementary/collaborator-ddim-rediffuse-20260509/raw/DDIMrediffuse` | not committed |
| `train1.py` collaborator script | `<DIFFAUDIT_ROOT>/Download/shared/supplementary/collaborator-ddim-rediffuse-20260509/raw/train1.py` | not committed |
| `DDIM-ckpt-step750000.pt` | `<DIFFAUDIT_ROOT>/Download/shared/weights/ddim-cifar10-step750000/raw/DDIM-ckpt-step750000.pt` | not committed |
| CIFAR10 dataset | `<DIFFAUDIT_ROOT>/Download/gray-box/supplementary/pia-upstream-assets/contents/datasets/cifar10` | not committed |

The Research repository commits only the adapter, CLI hooks, tests, and evidence
notes.

## What Was Integrated

- `diffaudit.attacks.rediffuse` probes asset readiness, required files, split
  hash, checkpoint metadata, and provenance caveats.
- `diffaudit.attacks.rediffuse_adapter` dynamically imports the external bundle,
  builds the bundled UNet, loads the 750k checkpoint, constructs
  `ReDiffuseAttacker`, and emits JSON summaries.
- The adapter supports two explicit scoring contracts:
  `first_step_distance_mean` for stable compatibility packets and `resnet` for
  the collaborator-style second-stage residual classifier.
- CLI commands now cover asset probe, runtime probe, tiny smoke, and bounded
  runtime packet.
- Tests cover asset probing, CLI probing, model/attacker construction, and a
  patched fake-CIFAR runtime smoke.

## Verified Facts

- The collaborator `CIFAR10_train_ratio0.5.npz` SHA256 is
  `aca922ecee25ef00dc6b6377ebaf7875dfcc77c2cdfe27c873b26a65134aa0c0`.
- That hash matches the existing PIA CIFAR10 ratio0.5 split used in Research.
- The 750k checkpoint is a dict with `ema_model`, `net_model`, `sched`,
  `optim`, `step`, and `x_T`.
- The checkpoint records `step = 750000`.
- The bundled UNet loads `ema_model` with zero missing keys and zero unexpected
  keys.
- CPU runtime probe can instantiate `ReDiffuseAttacker` and run a preview
  forward pass.
- CUDA is available in the project conda environment on this machine.

## Runtime Results

The CPU and CUDA smokes prove runtime compatibility only.

| Run | Size | Device | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| CPU smoke | 2 member + 2 nonmember | `cpu` | 0.75 | 0.75 | 0.5 | 0.5 |
| CUDA smoke | 8 member + 8 nonmember | `cuda` | 0.859375 | 0.875 | 0.125 | 0.125 |
| CUDA ResNet scorer smoke | 4 member + 4 nonmember held-out | `cuda` | 0.1875 | 0.5 | 0.0 | 0.0 |
| CUDA small packet | 64 member + 64 nonmember | `cuda` | 0.8125 | 0.773438 | 0.078125 | 0.078125 |

The small packet is positive as a compatibility result: ReDiffuse runs, loads
the transferred checkpoint, reads the shared split, and produces sane
member/nonmember scores. It is not a paper-faithful result yet.

## Caveats

- `seed = 42` is a collaborator statement. `train1.py` does not set it in code.
- `train1.py` defaults to `total_steps = 200000`, while the checkpoint records
  `step = 750000`.
- The recorded 2/2, 8/8, and 64/64 packets use `first_step_distance_mean`.
- The `resnet` scorer has passed one GPU-light real-asset smoke, but has not yet
  produced a recorded small packet.
- The transferred 750k checkpoint is collaborator-grounded, not independently
  traced to a published pretrained release.
- The existing 800k checkpoint remains the better-grounded PIA/SecMI mainline
  target until ReDiffuse parity is reviewed.

## Next Task

Run a bounded CPU-first or GPU-light parity packet with `--scoring-mode resnet`.
The decision after that review should be one of:

1. Treat ReDiffuse as paper-faithful enough for same-contract comparison against
   PIA/SecMI.
2. Keep the current direct-distance adapter as a separate Research baseline and
   do not compare it directly against PIA/SecMI admitted metrics.

No Platform or Runtime schema change is justified yet.
