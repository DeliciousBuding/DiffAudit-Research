# X-172 H2 Strength-Response Non-Overlap Validation

Date: 2026-04-29
Status: `positive but bounded validation`

## Question

After `X-171` showed that the `X-168` H2 signal is not high-frequency-only, does `01-black-box H2 strength-response` survive a larger non-overlapping `128 / 128` DDPM/CIFAR10 validation rung?

## Inputs

- X171 boundary:
  - `workspaces/implementation/2026-04-29-x171-h3-frequency-filter-cache-ablation.md`
- script:
  - `legacy/execution-log/2026-04-29/scripts/run_x172_blackbox_h2_strength_response_validation_gpu.py`
- run:
  - `workspaces/black-box/runs/x172-h2-strength-response-validation-20260429-r1/summary.json`
- response cache:
  - `workspaces/black-box/runs/x172-h2-strength-response-validation-20260429-r1/response-cache.npz`

## Contract

- packet:
  - `128` PIA members
  - `128` PIA nonmembers
  - split offset `64`, so this validation skips the first `64 / 64` split entries used by `X-168`
- asset family:
  - canonical PIA DDPM/CIFAR10 checkpoint and split
- response acquisition:
  - four moderate timesteps: `40 / 80 / 120 / 160`
  - two noise repeats per timestep
  - forward-noise followed by bounded deterministic DDIM-style partial denoise with stride `10`
- primary scorer:
  - raw H2 repeated stratified holdout logistic regression over the 4-D vector of per-timestep minimum seed-to-output RMSE
- secondary boundary check:
  - H3 `lowpass_0_5` frequency-filtered H2 logistic
- mandatory metrics:
  - `AUC`
  - `ASR`
  - `TPR@1%FPR`
  - `TPR@0.1%FPR`

## Result

Primary raw H2 logistic:

- `AUC = 0.887756`
- `ASR = 0.808594`
- `TPR@1%FPR = 0.093750`
- `TPR@0.1%FPR = 0.062500`

Best raw simple low-FPR baseline:

- scorer: `negative_slope`
- `AUC = 0.820679`
- `ASR = 0.761719`
- `TPR@1%FPR = 0.031250`
- `TPR@0.1%FPR = 0.007812`

Primary raw delta versus best simple low-FPR baseline:

- `AUC +0.067077`
- `ASR +0.046875`
- `TPR@1%FPR +0.062500`
- `TPR@0.1%FPR +0.054688`

Secondary H3 `lowpass_0_5` H2 logistic:

- `AUC = 0.879333`
- `ASR = 0.796875`
- `TPR@1%FPR = 0.195312`
- `TPR@0.1%FPR = 0.078125`

Low-pass delta versus raw logistic:

- `AUC -0.008423`
- `ASR -0.011719`
- `TPR@1%FPR +0.101562`
- `TPR@0.1%FPR +0.015625`

Gate fields:

- `raw_beats_simple_low_fpr = true`
- `raw_auc_not_worse_than_best_simple_auc = true`
- `lowpass_tail_retained = true`
- `validation_passed = true`
- `promotion_allowed = false`

Run cost:

- device: `cuda:0`
- wall clock: `141.342878s`
- effective GPU task count: one bounded validation rung

## Interpretation

The non-overlap validation supports the H2 candidate surface: the raw H2 logistic remains above the best simple baseline on AUC, ASR, and both low-FPR tails. The result is weaker than the `X-168` `64 / 64` scout, which is expected under a larger non-overlap packet and should prevent overclaiming.

The low-pass boundary remains favorable. `lowpass_0_5` trades small AUC/ASR loss for stronger low-FPR tails, which reinforces the `X-171` reading that H2 is not merely a high-frequency artifact.

This still does not promote H2 to admitted black-box evidence:

- no frozen same-packet recon comparator is attached
- no independent `256 / 256` rung is attached
- no query-budget/adaptive stress test is attached
- the evidence is still DDPM/CIFAR10 only
- no Runtime or Platform consumer contract exists for this surface

## Verdict

`positive but bounded validation`

H2 strength-response remains a live black-box candidate and now has one positive non-overlap validation rung. The next step is `X-173 post-validation boundary review`, not immediate GPU expansion.

## Control State

- `active_gpu_question = none`
- `next_gpu_candidate = none until X173 post-validation review decides whether an independent 256/256 or comparator rung is justified`
- `current_execution_lane = X173 post-validation boundary review`
- `cpu_sidecar = I-A / cross-box boundary maintenance`

## Handoff

- `Platform`: no schema, UI, dashboard, or public catalog change.
- `Runtime-Server`: no runner or task contract change.
- `Docs/materials`: note-level only. H2 may be described internally as a validated positive-but-bounded black-box candidate, not admitted evidence and not a replacement for `recon`.
