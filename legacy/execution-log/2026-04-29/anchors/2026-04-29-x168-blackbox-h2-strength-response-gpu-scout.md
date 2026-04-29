# X-168 Black-Box H2 Strength-Response GPU Scout

Date: 2026-04-29
Status: `positive but bounded`

## Question

Can a bounded `01-black-box H2 strength-response` scout acquire a new DDPM/CIFAR10 response surface and beat simple seed-to-output distance baselines at low FPR without reopening H3, tri-surface fusion, activation salvage, or G1-A stability work?

## Contract

- script:
  - `legacy/execution-log/2026-04-29/scripts/run_x168_blackbox_h2_strength_response_gpu_scout.py`
- run:
  - `workspaces/black-box/runs/x168-h2-strength-response-gpu-scout-20260429-r1/summary.json`
- response cache:
  - `workspaces/black-box/runs/x168-h2-strength-response-gpu-scout-20260429-r1/response-cache.npz`
- packet:
  - `64` PIA members
  - `64` PIA nonmembers
- asset family:
  - canonical PIA DDPM/CIFAR10 checkpoint and split
- response acquisition:
  - four moderate timesteps: `40 / 80 / 120 / 160`
  - two noise repeats per timestep
  - forward-noise followed by bounded deterministic DDIM-style partial denoise with stride `10`
- primary scorer:
  - repeated stratified holdout logistic regression over the 4-D vector of per-timestep minimum seed-to-output RMSE
- mandatory metrics:
  - `AUC`
  - `ASR`
  - `TPR@1%FPR`
  - `TPR@0.1%FPR`

## Result

Primary H2 logistic aggregate:

- `AUC = 0.928955`
- `ASR = 0.859375`
- `TPR@1%FPR = 0.218750`
- `TPR@0.1%FPR = 0.218750`

Best simple low-FPR baseline:

- scorer: `single_timestep_120`
- `AUC = 0.713623`
- `ASR = 0.695312`
- `TPR@1%FPR = 0.062500`
- `TPR@0.1%FPR = 0.062500`

Best simple AUC baseline:

- scorer: `negative_slope`
- `AUC = 0.806885`
- `ASR = 0.789062`
- `TPR@1%FPR = 0.046875`
- `TPR@0.1%FPR = 0.046875`

Primary delta versus the best simple low-FPR baseline:

- `AUC +0.215332`
- `ASR +0.164063`
- `TPR@1%FPR +0.156250`
- `TPR@0.1%FPR +0.156250`

Run cost:

- wall clock: `64.157820s`
- response cache size: about `5.2 MB`
- final GPU state after run: no active Research compute observed

## Interpretation

This is the first positive `01-black-box H2 strength-response` response-surface scout on the current DDPM/CIFAR10 asset family.

The positive part is real:

- the result comes from a fresh response surface, not from PIA/GSA/SimA score recombination
- the logistic 4-D strength vector beats both the best simple low-FPR scorer and the best simple AUC scorer
- the low-FPR lift is not merely AUC-only
- the response cache is reusable by H1 response-cloud geometry and H3 frequency-filter scorer-only follow-ups

The bounded part is also mandatory:

- this is still a `64 / 64` scout, not a 128/256 validation rung
- it uses DDPM/CIFAR10 only and must not be extrapolated to conditional diffusion, Stable Diffusion, or DiT
- it is a Research script/cache surface, not a Runtime runner or Platform consumer contract
- recon comparator rung is still not frozen inside this packet
- the logistic scorer is repeated-holdout evaluated on one packet, not yet an independent held-out validation packet

## Verdict

`positive but bounded`

`H2 strength-response` is now a live black-box candidate surface and should not be treated as parked-only. It still cannot be promoted to admitted black-box evidence or external claim without a follow-up review and a validation rung.

## Control State

- `active_gpu_question = none`
- `next_gpu_candidate = none until X169 post-run review selects a validation or scorer-reuse step`
- `current_execution_lane = X169 H2 post-run boundary review and H1/H3 scorer-reuse selection`
- `cpu_sidecar = I-A / cross-box boundary maintenance plus H1/H3 scorer-reuse on X168 cache`

## Handoff

- `Platform`: no schema, UI, dashboard, or public catalog change.
- `Runtime-Server`: no runner or task contract change.
- `Docs/materials`: note-level only. If referenced, call it a bounded black-box response-surface scout with positive low-FPR signal, not admitted evidence.
