# X-152: I-A Low-FPR / Adaptive-Attacker Boundary Refresh

## Question

After `X-151` held the GPU slot and moved the live lane back to `I-A`, do the current public, system-facing, and hot-path Research surfaces still preserve the intended `PIA + stochastic-dropout` boundary?

The boundary to preserve is:

- `PIA` exposes `epsilon-trajectory consistency`
- `stochastic-dropout(all_steps)` is an inference-time randomization defense prototype
- the claim is `workspace-verified + bounded repeated-query adaptive-reviewed`
- every higher-layer read must keep `AUC / ASR / TPR@1%FPR / TPR@0.1%FPR` together
- no surface may turn the packet into validated privacy protection, full adaptive-attacker closure, or paper-aligned release

## Scope Reviewed

Reviewed current hot-path surfaces with targeted searches for `PIA + stochastic`, `bounded repeated-query`, `adaptive`, `low-FPR`, `TPR@1%FPR`, `TPR@0.1%FPR`, `AUC-only`, `validated privacy`, and defense-success wording:

- `README.md`
- `docs/README.md`
- `docs/internal/comprehensive-progress.md`
- `docs/internal/mainline-narrative.md`
- `docs/evidence/admitted-results-summary.md`
- `docs/evidence/research-boundary-card.md`
- `docs/internal/research-autonomous-execution-prompt.md`
- `docs/internal/codex-roadmap-execution-prompt.md`
- `docs/internal/future-phase-e-intake.md`
- `workspaces/implementation/challenger-queue.md`

## Findings

No current hot-path surface reintroduced `AUC-only` defense storytelling.

The admitted gray-box summary already carries the correct four-metric row for both `PIA GPU512 baseline` and `PIA GPU512 + stochastic-dropout(all_steps)`, with explicit `paper-aligned blocked by checkpoint/source provenance` and `not validated privacy protection` boundary language.

The short boundary card already blocks the unsafe readings:

- do not call the defended line reproduced, public, or validated privacy protection
- repeated-query review is only a bounded adaptive boundary
- low-FPR fields must travel with headline metrics

The current prompt and queue surfaces were still correctly steering away from same-contract GPU reruns and toward a CPU-first boundary refresh. The only required change after this review is control-plane progression: close `X-152` and move the live lane to a CPU contract freeze for the provisional per-timestep activation-trajectory GPU candidate.

## Verdict

`positive but stabilizing`

`I-A` remains stable and correctly bounded in the active public/system-facing Research surfaces. No admitted table change, metric change, Runtime endpoint change, Platform snapshot change, or competition-material rewrite is required.

## Control State After X-152

- `active_gpu_question = none`
- `next_gpu_candidate = provisional per-timestep activation-trajectory scout, pending X-153 CPU contract freeze`
- `current_execution_lane = X-153 per-timestep activation-trajectory CPU contract freeze`
- `cpu_sidecar = I-A boundary maintenance plus 04-defense successor-hypothesis watch`

## Handoff

- `Platform`: no schema or UI change.
- `Runtime-Server`: no runner or endpoint change.
- `Docs/materials`: no immediate public rewrite required; keep using the four-metric plus bounded-adaptive wording already present in admitted summaries and boundary cards.
