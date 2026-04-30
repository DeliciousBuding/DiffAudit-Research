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
- `current_execution_item = code governance / CLI dispatch registry split`
- `next_cpu_sidecar = X-181 I-A / cross-box boundary maintenance after H2 comparator block`
- `gray_box_slot = yield`
- `H2_strength_response = strong validated DDPM/CIFAR10 candidate-only`
- `G1-A / X-90 = two-seed internal auxiliary positive`

## Active

### Code governance / CLI dispatch registry split

- `mode`: CPU-only architecture cleanup
- `status`: active
- `verdict target`: `main()` becomes parser + registry dispatch; the remaining
  command bodies are grouped by category without changing command names,
  arguments, JSON fields, exit behavior, or workspace artifact schemas.
- `GPU`: no
- `handoff`: no Platform or Runtime schema change

This item continues the repository cleanup lane after the local asset-boundary
cleanup and first CLI package split were merged.

### X-181 I-A / cross-box boundary maintenance after H2 comparator block

- `mode`: CPU-only boundary hardening
- `status`: ready after CLI governance PR closes
- `verdict target`: formal statement / adaptive-attacker / low-FPR boundary
  note plus updates to current evidence summaries
- `GPU`: no
- `handoff`: no Platform or Runtime schema change unless a concrete consumer
  mismatch is found

H2 is strong enough to create overclaim pressure but remains candidate-only.
This active item hardens I-A wording and cross-box surfaces before any future
GPU release.

## Ready

### Public-surface / hot-path sync

- `mode`: CPU-only repository hygiene
- `why ready`: run only when docs, guards, or repository surface become stale.
- `release gate`: no model run; preserve CLI arguments, JSON output fields, and
  workspace artifact schemas.

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
| `2026-04-30 architecture triage` | Corrected the external audit packet into a durable governance note; fixed `src -> scripts` DDPM factory dependency; added package initializers; aligned local checks with CI guards. |
| `2026-04-30 Phase 0 utils` | Shared utility extraction merged; metrics, JSON I/O, Gaussian helpers, and schedule helpers now have a package home. |
| `2026-04-30 IA reset` | Information architecture reset merged; public docs, internal docs, workspace archives, and asset boundaries reorganized. |
| `X-141` to `X-143` | G1-A / X-90 restored as two-seed internal auxiliary positive; not headline evidence. |
| `X-144` to `X-155` | Activation-subspace and per-timestep trajectory routes closed negative-but-useful; GPU hold. |
| `X-156` to `X-163` | H3 selective routing closed candidate-only positive-but-bounded; gate-leak and oracle-route falsifiers block promotion. |
| `X-164` to `X-166` | Cross-box tri-surface consensus closed negative-but-useful; boundary hardening completed. |
| `X-167` to `X-180` | H2 strength-response progressed to strong validated candidate-only surface; comparator and promotion paths remain blocked. |

Closed entries are traceable through
[`legacy/execution-log/2026-04-29/README.md`](../../legacy/execution-log/2026-04-29/README.md).
