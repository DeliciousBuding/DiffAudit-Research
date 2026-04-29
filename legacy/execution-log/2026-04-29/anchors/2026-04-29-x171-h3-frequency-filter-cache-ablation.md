# X-171 H3 Frequency-Filter Cache Ablation

Date: 2026-04-29
Status: `positive boundary / H2 validation candidate released`

## Question

Does the `X-168` black-box H2 strength-response signal survive a cheap H3 frequency-domain ablation, or is it mostly a high-frequency artifact that should block a larger H2 validation rung?

## Inputs

- X168 response cache:
  - `workspaces/black-box/runs/x168-h2-strength-response-gpu-scout-20260429-r1/response-cache.npz`
- script:
  - `legacy/execution-log/2026-04-29/scripts/run_x171_blackbox_h3_frequency_filter_cache_ablation.py`
- run:
  - `workspaces/black-box/runs/x171-h3-frequency-filter-cache-ablation-20260429-r1/summary.json`
- features:
  - `workspaces/black-box/runs/x171-h3-frequency-filter-cache-ablation-20260429-r1/features.json`

## Contract

This review is CPU-only and acquires no new model responses.

Frequency masks:

- `raw_full`
- low-pass radial FFT masks at `0.25 / 0.50 / 0.75`
- high-pass radial FFT masks at `0.25 / 0.50 / 0.75`
- band-pass masks at `0.25-0.50` and `0.50-0.75`

Scorers:

- H2 original-to-output minimum RMSE per timestep, then repeated stratified holdout logistic regression
- H2 simple single-timestep / mean / slope baselines
- H1 output-output response-cloud features as diagnostic reuse only

Gate:

- pass the boundary check if a low/mid-frequency H2 view retains most of the raw low-FPR tail and high-pass-only views do not dominate
- do not promote H2 to admitted black-box evidence from this cache-only ablation

## Result

Raw full H2 logistic:

- `AUC = 0.926758`
- `ASR = 0.851562`
- `TPR@1%FPR = 0.250000`
- `TPR@0.1%FPR = 0.250000`

Best non-full H2 logistic:

- mask: `lowpass_0_5`
- `AUC = 0.929932`
- `ASR = 0.859375`
- `TPR@1%FPR = 0.218750`
- `TPR@0.1%FPR = 0.218750`

Best high-pass H2 logistic:

- mask: `highpass_0_25`
- `AUC = 0.872070`
- `ASR = 0.828125`
- `TPR@1%FPR = 0.015625`
- `TPR@0.1%FPR = 0.015625`

Best diagnostic H1 logistic:

- mask: `lowpass_0_25`
- `AUC = 0.831787`
- `ASR = 0.781250`
- `TPR@1%FPR = 0.093750`
- `TPR@0.1%FPR = 0.093750`

Gate fields:

- `low_or_mid_retains_h2_tail = true`
- `highpass_dominates_h2_tail = false`
- `filter_improves_h2_tail = false`
- `h1_tail_recovered_by_filtering = true`
- `validation_candidate_allowed = true`
- `promotion_allowed = false`

Runtime:

- `128` total cached samples (`64 / 64`)
- wall clock: `156.936306s`
- GPU release: `none`

## Interpretation

The H2 strength-response signal is not a high-frequency-only artifact on the X168 cache. The `lowpass_0_5` view keeps nearly the same low-FPR tail as raw full H2, while high-pass views collapse sharply. This supports one bounded validation rung for H2.

The H1 result is only diagnostic. Low-pass filtering recovers a small H1 low-FPR tail, but it remains far below H2 and does not independently drive promotion or validation.

## Verdict

`positive boundary / H2 validation candidate released`

H3 frequency filtering should remain a plug-in ablation, not a standalone admitted method. The next GPU candidate is one bounded `X172 128/128 H2 strength-response validation` on a non-overlapping packet, pending host-health check.

## Control State

- `active_gpu_question = none`
- `next_gpu_candidate = X172 bounded 128/128 H2 strength-response validation, pending host-health check`
- `current_execution_lane = X172 H2 validation gate / bounded GPU run if host is healthy`
- `cpu_sidecar = I-A / cross-box boundary maintenance`

## Handoff

- `Platform`: no schema, UI, dashboard, or public catalog change.
- `Runtime-Server`: no runner or task contract change.
- `Docs/materials`: note-level only. H2 may be described as a live positive-but-bounded black-box candidate whose first frequency ablation did not falsify it as high-frequency-only, but it is not admitted evidence.
