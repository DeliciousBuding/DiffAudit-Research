# X-170 H1 Response-Cloud Cache Review

Date: 2026-04-29
Status: `negative but useful`

## Question

Does the X168 response cache contain a distinct H1 output-output response-cloud membership signal, independent of H2 original-to-output strength distance, strong enough to justify promotion or a new GPU validation rung?

## Inputs

- X168 response cache:
  - `workspaces/black-box/runs/x168-h2-strength-response-gpu-scout-20260429-r1/response-cache.npz`
- script:
  - `legacy/execution-log/2026-04-29/scripts/run_x170_blackbox_h1_response_cloud_cache_review.py`
- run:
  - `workspaces/black-box/runs/x170-h1-response-cloud-cache-review-20260429-r1/summary.json`

## Contract

This review is CPU-only and uses no original-to-output distance features.

H1 features:

- per-timestep repeat RMSE between generated outputs
- global output-cloud pairwise RMSE
- output-cloud variance
- timestep-centroid pairwise RMSE
- repeat-RMSE slope

Primary scorer:

- repeated stratified holdout logistic regression over output-output cloud features

Baselines:

- negative per-timestep repeat RMSE
- negative cloud pairwise RMSE
- negative cloud variance
- negative centroid pairwise RMSE
- negative repeat-RMSE slope

## Result

H1 logistic aggregate:

- `AUC = 0.848633`
- `ASR = 0.820312`
- `TPR@1%FPR = 0.000000`
- `TPR@0.1%FPR = 0.000000`

Best simple H1 AUC baseline:

- scorer: `negative_centroid_pairwise_rmse`
- `AUC = 0.714844`
- `ASR = 0.695312`
- `TPR@1%FPR = 0.062500`
- `TPR@0.1%FPR = 0.062500`

Best simple H1 low-FPR baseline:

- scorer: `negative_cloud_variance`
- `AUC = 0.687256`
- `ASR = 0.671875`
- `TPR@1%FPR = 0.078125`
- `TPR@0.1%FPR = 0.078125`

Primary delta versus best simple low-FPR H1 baseline:

- `AUC +0.161377`
- `ASR +0.148437`
- `TPR@1%FPR -0.078125`
- `TPR@0.1%FPR -0.078125`

## Interpretation

H1 output-output response-cloud geometry is not empty: it carries a clear AUC/ASR signal on the X168 cache. But the low-FPR tail is worse than the best simple cloud-variance baseline and far below the X168 H2 strength-response logistic low-FPR result.

This means H1 is useful as a diagnostic of response-cloud structure, but it should not become the next GPU validation driver. It also should not be fused into H2 before low-FPR behavior is stabilized.

## Verdict

`negative but useful`

H1 scorer reuse does not justify promotion, admitted evidence, Platform/Runtime handoff, or a new GPU rung. The next cheap cache-reuse question is H3 frequency filtering as a plug-in ablation on the X168 distance surface.

## Control State

- `active_gpu_question = none`
- `next_gpu_candidate = none until X171 H3 frequency-filter ablation decides whether the H2 surface deserves validation`
- `current_execution_lane = X171 H3 frequency-filter ablation on X168 cache`
- `cpu_sidecar = I-A / cross-box boundary maintenance`

## Handoff

- `Platform`: no handoff.
- `Runtime-Server`: no handoff.
- `Docs/materials`: no change. Keep H1 as negative-but-useful cache analysis only.
