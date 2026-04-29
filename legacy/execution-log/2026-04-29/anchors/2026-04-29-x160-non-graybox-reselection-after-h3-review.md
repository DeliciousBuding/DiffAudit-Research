# X-160: Non-Graybox Next-Lane Reselection After H3 Review

## Question

After X159 freezes H3 as candidate-only and returns GPU state to hold, what is the highest-value next Research lane that can create real progress without reopening stale same-contract GPU work?

## Inputs Reviewed

- `ROADMAP.md`
- `workspaces/implementation/challenger-queue.md`
- `workspaces/implementation/2026-04-29-x159-h3-post-gpu-review.md`
- `workspaces/gray-box/runs/x159-h3-post-gpu-review-20260429-r1/summary.json`
- `docs/comprehensive-progress.md`
- `docs/mainline-narrative.md`
- `docs/future-phase-e-intake.md`

## Candidate Review

| Candidate | Decision | Reason |
| --- | --- | --- |
| Larger H3 same-rule packet | reject | X159 failed deployable-gate and budget-fixed-adaptive gates; larger same-rule packet would be mechanical scale-up |
| H3 deployable runner | reject | current detector is same-packet baseline PIA score tail, not a clean runtime detector |
| H3 budget-fixed adaptive-attacker contract | select as CPU-first next lane | this directly addresses the strongest X159 blocker without releasing GPU yet |
| H3 SimA detector | hold | SimA remains execution-feasible but weak / auxiliary, so using it as primary detector would mix detector uncertainty into H3 |
| `05-cross-box` rerun | hold | promoted `logistic_2feature` and auxiliary `H4` are already landed; no new shared-surface hypothesis is frozen |
| `03-white-box` activation continuation | reject | mean-profile, validation-regularized, cross-layer, and trajectory routes are all below release |
| `02-gray-box` sidecar rerun | hold | `PIA + SimA` has no stable `TPR@0.1%FPR` lift; no new low-FPR signal is frozen |
| `I-A` boundary maintenance | keep as CPU sidecar | mandatory low-FPR / adaptive-attacker truth maintenance, but not the main lane while X159 exposes a concrete attacker-model blocker |

## Selected Next Lane

`X-161 H3 budget-fixed adaptive-attacker contract freeze`

This is CPU-first. It must define an attacker-aware review contract before any GPU release:

- fixed total query budget shared across baseline, all-steps, and gated policy
- explicit attacker strategy for reallocating queries after observing or inferring gate behavior
- no leakage of membership labels or post-hoc thresholds
- same packet identity and same low-FPR metrics as X158
- kill gate requiring selective gating to retain the full all-steps low-FPR tail under the fixed-budget attacker
- host-fit budget for at most one small scout if X161 passes

## Verdict

`positive reselection / GPU hold`

The next move is not a GPU run. It is a CPU contract freeze that can either authorize exactly one stricter H3 GPU scout or close H3 without further compute.

## Control State After X-160

- `active_gpu_question = none`
- `next_gpu_candidate = provisional X162 H3 budget-fixed adaptive-attacker scout, only if X161 freezes a no-leak host-fit contract`
- `next live lane = X-161 H3 budget-fixed adaptive-attacker contract freeze`
- `cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance`

## Handoff

- `Platform`: no change.
- `Runtime-Server`: no change. X161 is a research contract review, not a runner implementation task.
- `Docs/materials`: no public claim change. Keep H3 candidate-only until a stricter adaptive-attacker packet exists.
