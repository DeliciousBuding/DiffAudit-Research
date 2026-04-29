# X-156: 04 Defense Successor-Hypothesis Expansion Review

## Question

After `04-H1` scalar follow-ups, `04-H2` minimal packet follow-up, and the `03` activation-scout sequence all closed below promotion, is there one genuinely new `04-defense` successor hypothesis worth freezing before any more GPU work?

## Inputs Reviewed

- `docs/report-bundles/gpt54/round2-results/04.md`
- `docs/report-bundles/gpt54/round2-results/e2.md`
- `docs/report-bundles/gpt54/round2-results/global.md`
- `workspaces/implementation/2026-04-18-x114-04-defense-post-h1-family-review.md`
- `workspaces/implementation/2026-04-21-x139-04-h2-4x4-bounded-followup-review.md`
- `workspaces/implementation/2026-04-29-x155-post-trajectory-reselection.md`
- `workspaces/gray-box/runs/pia-cifar10-runtime-mainline-20260409-gpu-512-adaptive/summary.json`
- `workspaces/gray-box/runs/pia-cifar10-runtime-mainline-dropout-defense-20260409-gpu-512-allsteps-adaptive/summary.json`
- `workspaces/gray-box/runs/pia-cifar10-runtime-mainline-dropout-defense-20260409-gpu-512-latesteps-adaptive/summary.json`
- `workspaces/gray-box/runs/sima-packet-score-export-pia-full-overlap-20260421-r1/summary.json`

## Finding

`H3 selective / suspicion-gated perturbation` is genuinely different enough to freeze, but only under a narrow contract.

The honest local form is not "use SimA as the detector" yet. Local `SimA` is execution-feasible and pairboard-ready, but still weak/auxiliary, so using it as the primary defense gate would mix detector uncertainty into the defense verdict. The frozen near-term detector is therefore the existing PIA score tail, interpreted only as an owner-side suspicion signal on the same admitted `DDPM/CIFAR10` surface.

## Frozen H3 Contract

- `defense family`: selective / suspicion-gated inference-time perturbation
- `detector`: baseline PIA score tail, not SimA
- `route`: apply the existing all-steps stochastic-dropout surface only to the top risk tail
- `initial gate fraction`: `<= 20%` of the evaluated packet, allowing one-sample discretization tolerance
- `primary comparator`: full all-steps stochastic-dropout on the same packet
- `must report`: `AUC`, `ASR`, `TPR@1%FPR`, `TPR@0.1%FPR`, gate fractions, repeated-query adaptive metrics, and quality/cost boundary
- `not allowed`: privacy overclaim, conditional-diffusion extrapolation, detector promotion, or replacing the admitted `PIA + stochastic-dropout` story

## Kill Gate

Stop the branch if any of the following hold:

- selective routing fails to match full all-steps dropout at `TPR@1%FPR` and `TPR@0.1%FPR`
- the route must defend most samples to preserve tail metrics
- repeated-query aggregation restores the baseline tail
- the only win is AUC-only or ASR-only
- a deployable gate would require SimA or another detector before that detector has a stronger local contract

## Verdict

`positive / bounded successor contract frozen`

This freezes one narrow H3 contract and authorizes a cache-level X-157 scout. It does not authorize promotion or direct larger-packet GPU expansion.

## Control State After X-156

- `active_gpu_question = none`
- `next_gpu_candidate = provisional X-158 bounded H3 gated runtime scout, only if X-157 cached scout clears the release gate`
- `cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance`

## Handoff

- `Platform`: no schema or UI change.
- `Runtime-Server`: no runner change yet; a future implementation should be treated as candidate-only.
- `Docs/materials`: no public claim change; do not describe H3 as validated privacy.
