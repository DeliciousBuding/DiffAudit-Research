# X-164 Nongraybox Reselection After H3 Closure

Date: 2026-04-29
Status: `positive reselection / CPU packet released`

## Question

After `X-163` froze H3 selective all-steps gating as candidate-only evidence, what is the highest-value non-graybox next lane?

## Inputs

- `workspaces/gray-box/runs/x163-h3-post-fixed-budget-review-20260429-r1/summary.json`
- `workspaces/implementation/2026-04-29-x163-h3-post-fixed-budget-review.md`
- current challenger queue and ROADMAP priority ladder
- existing shared surfaces:
  - `workspaces/gray-box/runs/pia-packet-score-export-gsa-full-overlap-20260418-r1/scores.json`
  - `workspaces/white-box/runs/gsa-loss-score-export-targeted-full-overlap-20260418-r1/summary.json`
  - `workspaces/gray-box/runs/sima-packet-score-export-pia-full-overlap-20260421-r1/scores.json`

## Reselection

Rejected immediate lanes:

- larger H3 or deployable H3: blocked by `X-163` gate-leak and oracle-route falsifiers
- same-rule activation-subspace or trajectory scouts: already closed negative under `X-150` and `X-154`
- third same-contract G1-A seed: would only strengthen internal auxiliary evidence, not a new project claim
- plain SimA rerun: current `PIA + SimA` support is auxiliary and lacks stable `TPR@0.1%FPR` lift
- `I-D` widening: no new bounded conditional-diffusion successor is frozen
- black-box parked routes: still need assets or a paper-faithful execution contract

Selected lane:

- `X-165 cross-box tri-surface low-FPR consensus packet`

Rationale:

- It is nongraybox and uses already aligned surfaces, so it can test a real cross-family hypothesis without GPU cost.
- It directly stresses low-FPR behavior, not only AUC.
- It can either create a new surface-acquisition hypothesis or close a tempting but under-tested fusion path.

## Verdict

`positive reselection / CPU packet released`

`X-165` is authorized as a CPU-only repeated-holdout packet. It does not authorize GPU by itself.

## Control State

- `active_gpu_question = none`
- `next_gpu_candidate = none until X165 produces a genuinely new surface-acquisition hypothesis`
- `cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance`
- `handoff = none`

Canonical follow-up anchor:

- `workspaces/cross-box/runs/x165-crossbox-trisurface-consensus-20260429-r1/summary.json`
