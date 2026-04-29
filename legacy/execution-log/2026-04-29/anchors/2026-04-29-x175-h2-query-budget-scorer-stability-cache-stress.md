# X-175 H2 Query-Budget And Scorer-Stability Cache Stress

Date: 2026-04-29
Status: `positive stress / raw-primary GPU candidate released`

## Question

After `X-174` froze the comparator/adaptive/query-budget contract, does the `X-172` H2 validation cache survive the required CPU-only stress gates before any larger `256 / 256` GPU validation rung is allowed?

## Inputs

- X174 contract:
  - `workspaces/implementation/2026-04-29-x174-h2-comparator-adaptive-validation-contract.md`
- script:
  - `legacy/execution-log/2026-04-29/scripts/run_x175_blackbox_h2_query_budget_scorer_stability_cache_stress.py`
- source cache:
  - `workspaces/black-box/runs/x172-h2-strength-response-validation-20260429-r1/response-cache.npz`
- run:
  - `workspaces/black-box/runs/x175-h2-query-budget-scorer-stability-20260429-r1/summary.json`
- compact scores:
  - `workspaces/black-box/runs/x175-h2-query-budget-scorer-stability-20260429-r1/compact-scores.json`

## Contract

- no new model calls
- CPU-only analysis of the `X-172` non-overlap `128 / 128` cache
- fixed timesteps: `40 / 80 / 120 / 160`
- fixed available responses: two repeats per timestep
- stress tests:
  - full two-repeat budget
  - repeat-0 one-repeat budget
  - repeat-1 one-repeat budget
  - leave-one-strength-out logistic features
  - raw H2 versus X174-predeclared `lowpass_0_5` H2

## Result

Full two-repeat budget:

| Scorer | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| raw H2 logistic | `0.885742` | `0.808594` | `0.078125` | `0.054688` |
| `lowpass_0_5` H2 logistic | `0.876099` | `0.796875` | `0.218750` | `0.085938` |

One-repeat stress:

| Scorer | Repeat | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | --- | ---: | ---: | ---: | ---: |
| raw H2 logistic | `0` | `0.843506` | `0.761719` | `0.101562` | `0.078125` |
| raw H2 logistic | `1` | `0.886230` | `0.812500` | `0.179688` | `0.101562` |
| `lowpass_0_5` H2 logistic | `0` | `0.834900` | `0.761719` | `0.093750` | `0.054688` |
| `lowpass_0_5` H2 logistic | `1` | `0.881531` | `0.812500` | `0.242188` | `0.125000` |

Leave-one-strength-out stress:

| Scorer | Dropped timestep | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | --- | ---: | ---: | ---: | ---: |
| raw H2 logistic | `40` | `0.791992` | `0.734375` | `0.015625` | `0.000000` |
| raw H2 logistic | `80` | `0.884460` | `0.812500` | `0.101562` | `0.070312` |
| raw H2 logistic | `120` | `0.876709` | `0.800781` | `0.093750` | `0.062500` |
| raw H2 logistic | `160` | `0.881531` | `0.812500` | `0.109375` | `0.070312` |
| `lowpass_0_5` H2 logistic | `40` | `0.797546` | `0.742188` | `0.015625` | `0.015625` |
| `lowpass_0_5` H2 logistic | `80` | `0.873474` | `0.789062` | `0.257812` | `0.101562` |
| `lowpass_0_5` H2 logistic | `120` | `0.871338` | `0.812500` | `0.085938` | `0.070312` |
| `lowpass_0_5` H2 logistic | `160` | `0.866272` | `0.800781` | `0.125000` | `0.109375` |

Gate fields:

- `raw_h2.stress_gate_passed = true`
- `lowpass_0_5_h2.stress_gate_passed = true`
- `selected_future_scorer = raw_h2`
- `larger_gpu_candidate_released = true`
- `promotion_allowed = false`

## Interpretation

The X174 CPU stress gate passes. Raw H2 remains the selected future primary scorer because it clears the stress gate without needing a post-hoc scorer swap. The `lowpass_0_5` secondary also clears the same stress gate and should remain mandatory on any future GPU rung, but it should not replace raw H2 as primary unless a later predeclared contract changes that rule.

The one-repeat budget does not collapse low-FPR signal. Leave-one-strength-out shows that dropping timestep `40` weakens the strictest raw tail, but does not zero both low-FPR metrics and is less fragile under `lowpass_0_5`. This supports running one bounded larger validation, not promotion.

## Verdict

`positive stress / raw-primary GPU candidate released`

`X-176 H2 non-overlap 256/256 validation` is released as the next bounded GPU candidate, with:

- split offset `192`
- raw H2 logistic as primary
- `lowpass_0_5` H2 logistic as mandatory secondary
- no admitted evidence claim
- no `recon` replacement claim

## Control State

- `active_gpu_question = provisional X176 H2 non-overlap 256/256 validation`
- `next_gpu_candidate = X176 H2 non-overlap 256/256 validation at split offset 192 with raw H2 primary`
- `current_execution_lane = X176 H2 non-overlap 256/256 validation`
- `cpu_sidecar = I-A / cross-box boundary maintenance`

## Handoff

- `Platform`: no handoff.
- `Runtime-Server`: no handoff.
- `Docs/materials`: note-level only. H2 is still candidate-only until a larger rung and comparator review are complete.
