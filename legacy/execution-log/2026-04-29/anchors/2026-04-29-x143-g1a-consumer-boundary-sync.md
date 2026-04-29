# X-143: G1-A Consumer Boundary Sync After X-142

## Question

After `X-141 / X-142` turned `G1-A / X-90` from a `TMIA-DM 512-sample gap` into a two-seed internal auxiliary positive, are the active consumer-facing Research surfaces aligned to the correct boundary?

## Boundary To Preserve

- `G1-A / X-90` is now `two-seed internal auxiliary positive` on matched `512 / 512` PIA/TMIA-DM surfaces.
- It is not an admitted gray-box headline replacement.
- `PIA + stochastic-dropout` remains the admitted gray-box headline.
- `headline_use_allowed = false`.
- `external_evidence_allowed = false`.
- A third same-contract G1-A seed is not justified without a new stability or story-delta hypothesis.
- No Platform or Runtime schema change is required.

## Sync Review

Reviewed active Research entry surfaces for stale live steering around:

- `active_gpu_question`
- `next_gpu_candidate`
- `G1-A`
- `TMIA-DM 512-sample gap`
- `deferred-needs-assets`
- `future-phase-e-intake`
- `challenger-queue`

The main stale active wording was in `docs/future-phase-e-intake.md`, where `06-g1a` still read like the current closest blocker-resolution slot even though the blocker had already been resolved by `X-141 / X-142`.

## Changes

- Updated `docs/future-phase-e-intake.md` so `06-g1a` is described as resolved internal-only auxiliary evidence, not a current near-term slot.
- Advanced `workspaces/implementation/challenger-queue.md` from `G1-A boundary sync pending` to fresh non-graybox/GPU-candidate reselection.
- Updated `ROADMAP.md` with this verdict and the next lane state.

## Verdict

`positive`

The G1-A consumer boundary is now synchronized across active Research surfaces. Historical notes that recorded the old blocker state remain archival context and should not be rewritten as if they were current steering.

## Next State

- `active_gpu_question = none`
- `next_gpu_candidate = none until X-144 selects a fresh bounded candidate`
- `current_execution_lane = X-144 non-graybox next-lane / GPU-candidate reselection`
- `cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance`
- Platform / Runtime handoff: none
- Materials handoff: optional wording only; if mentioned, use `two-seed internal auxiliary G1-A positive on matched 512 surfaces`, not admitted headline language
