# X-147: Fresh Non-Graybox Candidate Expansion After Activation Overfit

## Question

After `X-145 / X-146` closed the first `03-H1 activation-subspace` GPU scout as overfit, is there any honest fresh non-graybox candidate that should receive the next GPU slot?

## Inputs

- `X-141 / X-142`: `G1-A / X-90` is now two-seed internal auxiliary evidence, not a gray-box headline and not a default third-seed request.
- `X-143`: consumer-boundary sync completed for `G1-A / X-90`.
- `X-144`: selected `03-H1 activation-subspace` as the only plausible fresh GPU-preflight direction.
- `X-145 / X-146`: the GPU-safe activation-subspace scout is reusable infrastructure, but the train-selected top-`16` selector overfits and inverts on the larger held-out read.
- Read-only subagent recommendation: no raw candidate clears GPU release; only a new selector / regularization / validation contract can reopen `03-H1`.

## Candidate Review

| Candidate | Decision | Reason |
| --- | --- | --- |
| third same-contract `G1-A / X-90` seed | reject | Two seeds already make it internal auxiliary; a third seed does not change headline eligibility. |
| larger same-rule activation-subspace scout | reject | `X-145 / X-146` directly show selector overfit. |
| `03-H1` selector redesign with validation filter | release one bounded scout | This is a new validation hypothesis, not a same-rule expansion. |
| larger same-contract `04-H2` | reject | The `4 / 4` follow-up still has zero baseline-vs-defended deltas. |
| `05-cross-box` rerun | reject | Current value is system-consumable read-path hardening, not GPU rerun. |
| `02-gray-box` sidecar | reject for GPU | `PIA + SimA` is auxiliary and lacks stable `TPR@0.1%FPR` lift. |
| `I-D` conditional branch | reject | Current evidence is seed-sensitive / negative under low-FPR and adaptive boundaries; no extrapolation to conditional diffusion. |
| black-box parked pool | reject | No new assets or bounded family contract. |

## Released GPU Packet

`X-147` released exactly one bounded GPU scout:

- script: `legacy/execution-log/2026-04-29/scripts/run_x148_activation_subspace_regularized_gpu_scout.py`
- packet: `X-148 activation-subspace validation-regularized scout`
- assets: admitted `GSA / DDPM / CIFAR10`
- selector: `mid_block.attentions.0.to_v`
- split: `8 selector / 4 validation / 4 holdout` per role on a `16 / 16` packet
- rule: choose top selector channels only if validation split preserves the direction sign, then report holdout metrics
- budget: one `cuda:0` run, no sweep, no larger packet

## Verdict

`positive reselection / one bounded GPU scout released`

The raw non-graybox queue had no ready GPU candidate after `X-146`. However, the activation-subspace line had a legitimate new hypothesis: validation-stable channel selection. That made one small `X-148` scout honest to release. This does not reopen same-rule activation-subspace scaling, and it does not affect admitted results.

## Next State

- `active_gpu_question = X-148 during release; none after X-148 completion`
- `next_gpu_candidate = none after X-148`
- `current_cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance`
- next CPU-first lane: post-`X-148` selector / mechanism review, with no GPU release unless a new cross-layer or independent-validation hypothesis is frozen
- Platform / Runtime handoff: none
- Materials handoff: none
