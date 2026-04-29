# DiffAudit Research ROADMAP

> Last updated: 2026-04-30
> Owner: `Researcher`
> Mode: post-governance sync, no active GPU task

This file is the hot-path steering document for DiffAudit Research. It should
stay short enough for a teammate or reviewer to read at session start. Long
execution history is archived under
[`legacy/execution-log/`](legacy/execution-log/).

## 1. Current Execution State

- `active_gpu_question = none`
- `next_gpu_candidate = none`
- `current_execution_item = post-governance repository hygiene`
- `next_cpu_sidecar = X-181 I-A / cross-box boundary maintenance`
- `gpu_policy = no release until a fresh bounded hypothesis passes CPU-first gates`
- `history_rewrite_policy = audit only; no force-push without separate approval`

The 2026-04-29 governance cleanup has merged. Fresh sessions should first keep
the public surface and hot-path state clean, then move to `X-181` as a CPU-first
boundary-maintenance task. Do not release a GPU packet or promote a new result
without a new roadmap gate.

## 2. Current Research Truth

### Admitted lines

- Black-box admitted headline remains `recon`.
- Gray-box admitted headline remains `PIA + stochastic-dropout`.
- White-box admitted headline remains `GSA + W-1`.
- Cross-box `PIA + GSA` remains promoted support evidence where status labels
  and low-FPR caveats are preserved.

### Candidate-only lines

- `G1-A / X-90` is now `two-seed internal auxiliary positive`, not a gray-box
  headline replacement. `headline_use_allowed = false` and
  `external_evidence_allowed = false` remain binding.
- `04-H3 selective / suspicion-gated all-steps routing` is
  `candidate-only positive-but-bounded / GPU hold`. Fixed-budget low-FPR tail
  matching is real, but gate-leak and oracle-route falsifiers block promotion.
- `01-H2 strength-response` is a strong validated DDPM/CIFAR10 candidate
  surface. It is not admitted, not a `recon` replacement, and not ready for
  Runtime or Platform consumer handoff.

### Negative or frozen lanes

- `03-H1 activation-subspace` mean-profile, validation-regularized,
  cross-layer stability, and per-timestep trajectory scouts are all closed
  `negative but useful`; another activation run requires a genuinely different
  observable.
- `PIA + GSA + SimA` tri-surface consensus improved AUC under one fused view but
  did not stabilize low-FPR lift, so it cannot reopen as a promoted line.
- Same-packet admitted `recon` comparison is blocked for X176 because the
  admitted `recon` protocol and the DDPM/CIFAR10 H2 response-surface packet are
  not compatible surfaces.

## 3. Latest Verdicts

- `X-176`: `positive but bounded validation`. Non-overlap `256 / 256` H2
  validation passed with raw H2 `AUC = 0.913940 / ASR = 0.851562 /
  TPR@1%FPR = 0.171875 / TPR@0.1%FPR = 0.062500`.
- `X-177`: `positive boundary / comparator-first hold`. H2 is a strong
  candidate, but promotion, `recon` replacement, more H2 GPU, and consumer
  handoff are blocked.
- `X-178`: `blocked but useful / comparator-blocked`. Direct admitted `recon`
  comparison is not implementable on the X176 packet.
- `X-179`: `positive contract review / no GPU release`. X176 sanity
  comparators are useful but not admitted `recon`.
- `X-180`: `positive reselection / GPU hold`. No non-H2 lane clears the
  immediate GPU-release bar.

Canonical X-141 to X-180 anchors now live in
[`legacy/execution-log/2026-04-29/`](legacy/execution-log/2026-04-29/).

## 4. Next Decision After Post-Governance Hygiene

The next research lane, if no newer fact supersedes this roadmap, is:

```text
X-181 I-A / cross-box boundary maintenance after H2 comparator block
```

Why this is first:

- It is CPU-only.
- It hardens low-FPR, adaptive-attacker, and provenance boundaries.
- It prevents H2 overclaim pressure while H2 remains candidate-only.
- It produces system-consumable wording without changing Platform or Runtime
  schema.

Do not make `X-181` a model run. The intended output is a verdict-bearing
boundary note plus updates to the canonical evidence surfaces.

## 5. Queue Pointer

Use
[`workspaces/implementation/challenger-queue.md`](workspaces/implementation/challenger-queue.md)
for the active / ready / hold / needs-assets / closed queue. That file is the
candidate-management surface; this file is only the current steering summary.

## 6. Governance Status

The 2026-04-29 governance cleanup was merged to `main` through PR #26. Ongoing
governance goals:

- Keep hot-path docs short and product/research-facing.
- Move execution logs and one-off X-run scripts out of the public start path.
- Keep large datasets, weights, generated images, raw tensors, and upstream
  clones out of Git.
- Make `Download/`, `external/`, and `third_party/` roles unambiguous.
- Keep the history rewrite audit as a separate decision surface; do not rewrite
  history from routine research or documentation cleanup.

Read
[`docs/research-governance.md`](docs/research-governance.md) for repository
boundaries and
[`docs/history-rewrite-audit.md`](docs/history-rewrite-audit.md) for the future
history-slimming decision.

## 7. Startup Contract

Fresh research sessions should read:

1. `<DIFFAUDIT_ROOT>/ROADMAP.md`
2. `<DIFFAUDIT_ROOT>/Research/README.md`
3. `<DIFFAUDIT_ROOT>/Research/ROADMAP.md`
4. `<DIFFAUDIT_ROOT>/Research/AGENTS.md`
5. `<DIFFAUDIT_ROOT>/Research/docs/research-governance.md`
6. `<DIFFAUDIT_ROOT>/Research/docs/comprehensive-progress.md`
7. `<DIFFAUDIT_ROOT>/Download/manifests/research-download-manifest.json`
8. lane-specific workspace docs only after the task is narrowed

## 8. Handoff Boundary

No Platform or Runtime schema change was required by the completed governance
cleanup. If future work promotes H2, changes admitted lines, changes exported
metadata, or changes recommendation semantics, create a separate handoff note
before changing sibling repositories.
