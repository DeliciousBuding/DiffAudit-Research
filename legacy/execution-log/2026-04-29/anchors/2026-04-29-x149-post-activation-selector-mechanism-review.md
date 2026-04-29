# X-149: Post-Activation Selector / Mechanism Review

## Question

After `X-145 / X-146 / X-148`, does the activation-subspace line have a new honest successor hypothesis, or should `03-H1` freeze below GPU release?

## Evidence Reviewed

- `X-145`: first top-delta scout on `8 / 8` packet.
  - holdout `AUC = 0.625`
  - low-FPR fields `0.0`
  - train metrics perfect
- `X-146`: same selector on `16 / 16` packet.
  - holdout `AUC = 0.3125`
  - `ASR = 0.6875`
  - low-FPR fields `0.0`
  - train metrics perfect
- `X-148`: validation-regularized selector on `16 / 16`.
  - holdout `AUC = 0.625`
  - same-split top-delta baseline holdout `AUC = 0.4375`
  - selector split still perfect
  - validation split only `AUC = 0.625`
  - low-FPR read is too coarse at `4 / 4`

## Failure Pattern

The useful part is not "activation-subspace works". The useful part is narrower:

1. activation profiles can be extracted and scored under a GPU-safe admitted-asset contract;
2. naive selector overfits badly;
3. validation filtering improves the failure mode but does not produce a strong held-out signal;
4. single-layer mean-profile deltas are probably under-identified.

## Candidate Successors

| Candidate | Decision | Reason |
| --- | --- | --- |
| larger same-layer validation-regularized packet | reject | It would mostly test sample count, not a new mechanism. |
| same layer with different `top_k` | reject | Parameter churn after overfit. |
| cross-layer stability selector | select for CPU contract freeze | A channel or feature should survive across at least two related attention projections or block families before another GPU packet is honest. |
| independent noise-seed validation | select as supporting gate | A feature that only survives `noise_seed = 0` should not get another GPU release. |
| per-timestep trajectory features | hold as second option | More mechanistic than mean profile, but needs a stricter feature contract before GPU. |
| layer-ensemble scorer | hold | Higher implementation cost and easy to overfit without the cross-layer stability gate. |

## Next Candidate Contract

`X-150 cross-layer activation-stability contract freeze`

Minimum CPU-first contract:

- freeze layer set before execution:
  - primary: `mid_block.attentions.0.to_v`
  - comparator candidates: `mid_block.attentions.0.to_q`, `mid_block.attentions.0.to_k`, `down_blocks.4.attentions.0.to_v`, `up_blocks.1.attentions.0.to_v`
- define a selector that requires:
  - selector split direction
  - validation split direction
  - at least one independent layer-family confirmation
  - optional independent `noise_seed` confirmation before any GPU release
- define a hard no-go:
  - if the CPU contract cannot freeze a non-leaky selection rule, do not run GPU
  - if the rule still uses only one layer and one mean profile, do not run GPU

## Verdict

`positive / GPU hold`

`03-H1` should not be frozen completely, but it must move from "same-layer activation-subspace" to "cross-layer activation-stability" before another GPU run is honest. The next task is CPU-first contract freeze, not execution.

## Next State

- `active_gpu_question = none`
- `next_gpu_candidate = provisional X-150 cross-layer activation-stability scout, pending CPU contract freeze`
- `current_cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance`
- Platform / Runtime handoff: none
- Materials handoff: none
