# DiffAudit Research Challenger Queue

> Last refreshed: 2026-04-30
> Purpose: Maintain the candidate funnel without turning the queue into an
> execution log.

This file classifies future research candidates. It does not promote a result,
replace the roadmap, or preserve full historical timelines. Archived X-141 to
X-180 anchors live under
[`legacy/execution-log/2026-04-29/`](../../legacy/execution-log/2026-04-29/).

## Queue Truth

- `active_gpu_question = none`
- `next_gpu_candidate = none`
- `current_execution_item = Architecture audit triage cleanups`
- `gray_box_slot = yield`
- `H2_strength_response = strong validated DDPM/CIFAR10 candidate-only`
- `G1-A / X-90 = two-seed internal auxiliary positive`

## Active

### Architecture audit triage cleanups

- `mode`: CPU-only repository governance
- `status`: active
- `verdict target`: corrected architecture-audit record plus low-risk package
  boundary fixes from admitted findings
- `GPU`: no
- `handoff`: no Platform or Runtime schema change

This active item temporarily blocks research expansion. It must finish with a
small PR that keeps raw reviewer packets out of public docs and preserves CLI
arguments, JSON output fields, and workspace artifact schemas.

## Ready

### X-181 I-A / cross-box boundary maintenance after H2 comparator block

- `mode`: CPU-only boundary hardening
- `why ready`: H2 is strong enough to create overclaim pressure but remains
  candidate-only; I-A wording and cross-box surfaces should be hardened before
  any future GPU release.
- `expected output`: verdict-bearing boundary note plus updates to current
  evidence summaries.
- `release gate`: no model run, no Platform/Runtime schema change unless the
  boundary review finds a concrete consumer mismatch.

## Hold

### Stable Diffusion / CelebA H2-adapter contract watch

- `mode`: future black-box surface-acquisition contract
- `reason for hold`: closer to admitted `recon` assets than DDPM/CIFAR10 H2,
  but prompt, model, split, and query-budget contracts are not frozen.
- `reopen trigger`: CPU preflight freezes a compatible surface-acquisition
  contract and identifies one bounded validation packet.

### 05-cross-box successor-hypothesis watch

- `mode`: cross-box support line
- `reason for hold`: existing `logistic_2feature` support is promoted, while
  tri-surface consensus was AUC-positive but low-FPR-unstable.
- `reopen trigger`: a new shared-surface, surface-acquisition, or calibration
  hypothesis with low-FPR as the primary gate.

### 03-white-box distinct-family watch

- `mode`: distinct-family watch
- `reason for hold`: activation-subspace mean-profile, validation-stable,
  cross-layer, and trajectory variants all failed release gates.
- `reopen trigger`: a genuinely different observable or paper-backed family,
  not another same-observable activation scout.

### 04-H3 selective / suspicion-gated routing

- `mode`: defense candidate-only sidecar
- `reason for hold`: fixed-budget low-FPR tail matching is real, but gate-leak
  and oracle-route falsifiers block deployable or admitted reading.
- `reopen trigger`: new detector or adaptive-attacker contract that directly
  addresses both falsifiers.

### 01-H2 strength-response

- `mode`: black-box candidate surface
- `reason for hold`: non-overlap `256 / 256` validation passed, but compatible
  admitted comparator and adaptive/query-budget contracts are not available.
- `reopen trigger`: frozen compatible comparator-acquisition contract or a
  CPU-first preflight that can justify one bounded future validation packet.

## Needs Assets

### Cross-box transfer / portability

- `blocker`: missing paired model contracts, paired split contracts, and one
  bounded shared-surface hypothesis.
- `asset rule`: do not schedule execution until required paired assets are
  present in `Download/` or documented through workspace asset manifests.

### Conditional diffusion wider-family validation

- `blocker`: current `DDPM/CIFAR10` evidence cannot be generalized to
  conditional diffusion. Stable Diffusion / CelebA-style assets need explicit
  local contracts before any claim or GPU run.
- `asset rule`: raw datasets, weights, and supplementary bundles belong under
  `<DIFFAUDIT_ROOT>/Download/`, not Git.

## Closed

| Range | Verdict |
| --- | --- |
| `2026-04-30 Phase 0 utils` | Shared utility extraction merged; metrics, JSON I/O, Gaussian helpers, and schedule helpers now have a package home. |
| `2026-04-30 IA reset` | Information architecture reset merged; public docs, internal docs, workspace archives, and asset boundaries reorganized. |
| `X-141` to `X-143` | G1-A / X-90 restored as two-seed internal auxiliary positive; not headline evidence. |
| `X-144` to `X-155` | Activation-subspace and per-timestep trajectory routes closed negative-but-useful; GPU hold. |
| `X-156` to `X-163` | H3 selective routing closed candidate-only positive-but-bounded; gate-leak and oracle-route falsifiers block promotion. |
| `X-164` to `X-166` | Cross-box tri-surface consensus closed negative-but-useful; boundary hardening completed. |
| `X-167` to `X-180` | H2 strength-response progressed to strong validated candidate-only surface; comparator and promotion paths remain blocked. |

Closed entries are traceable through
[`legacy/execution-log/2026-04-29/README.md`](../../legacy/execution-log/2026-04-29/README.md).
