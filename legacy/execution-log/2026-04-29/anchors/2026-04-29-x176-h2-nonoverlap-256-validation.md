# X-176 H2 Non-Overlap 256/256 Validation

Date: 2026-04-29
Status: `positive but bounded validation`

## Question

After `X-175` passed the CPU query-budget and scorer-stability stress gate, does raw H2 strength-response survive the frozen non-overlap `256 / 256` DDPM/CIFAR10 validation rung at split offset `192`?

## Inputs

- X174 contract:
  - `workspaces/implementation/2026-04-29-x174-h2-comparator-adaptive-validation-contract.md`
- X175 stress gate:
  - `workspaces/implementation/2026-04-29-x175-h2-query-budget-scorer-stability-cache-stress.md`
- script:
  - `legacy/execution-log/2026-04-29/scripts/run_x172_blackbox_h2_strength_response_validation_gpu.py`
- run:
  - `workspaces/black-box/runs/x176-h2-nonoverlap-256-validation-20260429-r1/summary.json`
- response cache:
  - `workspaces/black-box/runs/x176-h2-nonoverlap-256-validation-20260429-r1/response-cache.npz`

## Contract

- packet:
  - `256` PIA members
  - `256` PIA nonmembers
  - split offset `192`
  - no overlap with the first `64 / 64` X168 scout or the next `128 / 128` X172 validation packet
- asset family:
  - canonical PIA DDPM/CIFAR10 checkpoint and split
- response acquisition:
  - timesteps `40 / 80 / 120 / 160`
  - two repeats per timestep
  - fixed `8` model-response calls per sample
  - DDIM-style partial denoise stride `10`
- primary scorer:
  - raw H2 repeated stratified holdout logistic regression over per-timestep minimum original-to-output RMSE
- mandatory secondary:
  - X174/X175-predeclared `lowpass_0_5` H2 logistic

## Result

Primary raw H2 logistic:

- `AUC = 0.913940`
- `ASR = 0.851562`
- `TPR@1%FPR = 0.171875`
- `TPR@0.1%FPR = 0.062500`

Best raw simple low-FPR baseline:

- scorer: `single_timestep_120`
- `AUC = 0.754715`
- `ASR = 0.687500`
- `TPR@1%FPR = 0.039062`
- `TPR@0.1%FPR = 0.000000`

Raw delta versus best simple low-FPR baseline:

- `AUC +0.159225`
- `ASR +0.164062`
- `TPR@1%FPR +0.132813`
- `TPR@0.1%FPR +0.062500`

Secondary `lowpass_0_5` H2 logistic:

- `AUC = 0.898392`
- `ASR = 0.816406`
- `TPR@1%FPR = 0.140625`
- `TPR@0.1%FPR = 0.050781`

Low-pass delta versus raw logistic:

- `AUC -0.015548`
- `ASR -0.035156`
- `TPR@1%FPR -0.031250`
- `TPR@0.1%FPR -0.011719`

Gate fields:

- `raw_beats_simple_low_fpr = true`
- `raw_auc_not_worse_than_best_simple_auc = true`
- `lowpass_tail_retained = true`
- `validation_passed = true`
- `promotion_allowed = false`

Run cost:

- device: `cuda:0`
- wall clock: `303.624904s`
- effective GPU task count: one bounded validation rung

## Interpretation

The larger non-overlap validation strengthens H2 substantially: raw H2 improves over the simple low-FPR baseline on AUC, ASR, and both low-FPR tails, and the mandatory `lowpass_0_5` secondary remains positive. The `lowpass_0_5` secondary is weaker than raw on this packet, so the X175 decision to keep raw H2 as primary is supported.

This result upgrades H2 from a merely validated candidate to a strong validated black-box candidate surface inside the DDPM/CIFAR10 PIA contract. It still does not admit H2 as a main black-box result because:

- no same-packet `recon` comparator is attached
- no threshold calibration or deployment contract is frozen
- evidence remains DDPM/CIFAR10 only
- no Runtime runner or Platform consumer schema exists
- no claim has been tested on conditional diffusion, Stable Diffusion, DiT, or commercial models

## Verdict

`positive but bounded validation`

H2 strength-response is now a strong validated black-box candidate surface, not admitted evidence. The next task is `X-177 H2 post-256 validation boundary and comparator review`, not another GPU packet.

## Control State

- `active_gpu_question = none`
- `next_gpu_candidate = none until X177 post-256 validation review decides whether a same-packet comparator or calibrated follow-up is justified`
- `current_execution_lane = X177 H2 post-256 validation boundary and comparator review`
- `cpu_sidecar = I-A / cross-box boundary maintenance`

## Handoff

- `Platform`: no handoff yet.
- `Runtime-Server`: no handoff yet.
- `Docs/materials`: note-level only. H2 can be described internally as a strong validated DDPM/CIFAR10 black-box candidate, but not admitted evidence and not a `recon` replacement.
