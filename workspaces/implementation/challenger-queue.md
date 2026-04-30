# DiffAudit Research Challenger Queue

> Last refreshed: 2026-04-30
> Purpose: Maintain the candidate funnel without turning the queue into an
> execution log.

This file classifies future research candidates by status and product value.
It is not a timeline. Historical run IDs and dated verdicts live under
`legacy/` and should not be used as the hot-path navigation system.

## Queue Truth

- Active work: `Cross-box evidence boundary hardening`
- Next GPU candidate: `none`
- CPU sidecar: `Public-surface / hot-path sync`
- Gray-box slot: yield unless a new boundary-changing fact appears
- Strongest recent candidate surface: response-strength black-box candidate on
  `DDPM/CIFAR10`; not admitted and not a `recon` replacement
- Internal auxiliary gray-box result: useful for Research triage, not headline
  evidence

## Active

### Cross-box evidence boundary hardening

- `mode`: CPU-only boundary hardening
- `status`: active
- `verdict target`: formal statement / adaptive-attacker / low-FPR boundary
  note plus updates to current evidence summaries
- `GPU`: no
- `handoff`: no Platform or Runtime schema change unless a concrete consumer
  mismatch is found

The response-strength candidate is strong enough to create overclaim pressure
but remains candidate-only. This active item hardens cross-box wording and
product-consumable status before any future GPU release.

## Ready

### Public-surface / hot-path sync

- `mode`: CPU-only repository hygiene
- `why ready`: run only when docs, guards, or repository surface become stale.
- `release gate`: no model run; preserve CLI arguments, JSON output fields, and
  workspace artifact schemas.

## Hold

### Stable Diffusion / CelebA adapter contract watch

- `mode`: future black-box surface-acquisition contract
- `reason for hold`: closer to admitted `recon` assets than the current
  `DDPM/CIFAR10` candidate surface, but prompt, model, split, and query-budget
  contracts are not frozen.
- `reopen trigger`: CPU preflight freezes a compatible surface-acquisition
  contract and identifies one bounded validation packet.

### Cross-box successor-hypothesis watch

- `mode`: cross-box support line
- `reason for hold`: existing two-feature support is promoted, while
  tri-surface consensus was AUC-positive but low-FPR-unstable.
- `reopen trigger`: a new shared-surface, surface-acquisition, or calibration
  hypothesis with low-FPR as the primary gate.

### White-box distinct-family watch

- `mode`: distinct-family watch
- `reason for hold`: activation-subspace mean-profile, validation-stable,
  cross-layer, and trajectory variants all failed release gates.
- `reopen trigger`: a genuinely different observable or paper-backed family,
  not another same-observable activation scout.

### Selective / suspicion-gated routing

- `mode`: defense candidate-only sidecar
- `reason for hold`: fixed-budget low-FPR tail matching is real, but gate-leak
  and oracle-route falsifiers block deployable or admitted reading.
- `reopen trigger`: new detector or adaptive-attacker contract that directly
  addresses both falsifiers.

### Response-strength black-box candidate

- `mode`: black-box candidate surface
- `reason for hold`: non-overlap validation passed, but compatible admitted
  comparator and adaptive/query-budget contracts are not available.
- `reopen trigger`: frozen compatible comparator-acquisition contract or a
  CPU preflight that can justify one bounded future validation packet.

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

| Workstream | Verdict |
| --- | --- |
| CLI package/dispatch split | `diffaudit.cli` is now a package with parser and dispatch separated; dispatch uses a command registry with parser-vs-handler contract coverage. |
| Local asset boundary cleanup | Local raw assets and generated run payloads were moved out of the Research working tree; `Download/` remains raw intake and `Archive/research-local-artifacts/` holds generated local artifacts. |
| Architecture triage | Corrected the external audit packet into a durable governance note; fixed `src -> scripts` DDPM factory dependency; added package initializers; aligned local checks with CI guards. |
| Shared utility extraction | Metrics, JSON I/O, Gaussian helpers, and schedule helpers now have a package home. |
| Information architecture reset | Public docs, internal docs, workspace archives, and asset boundaries were reorganized. |
| Internal auxiliary gray-box triage | Restored as internal auxiliary positive; not headline evidence. |
| White-box same-observable scouts | Activation-subspace and per-timestep trajectory routes closed negative-but-useful. |
| Selective routing defense scout | Closed positive-but-bounded; gate-leak and oracle-route falsifiers block promotion. |
| Cross-box tri-surface shortcut | Closed negative-but-useful; AUC-positive but low-FPR-unstable. |
| Response-strength black-box validation | Progressed to strong validated candidate-only surface; comparator and promotion paths remain blocked. |

Closed entries are traceable through
[`legacy/execution-log/2026-04-29/README.md`](../../legacy/execution-log/2026-04-29/README.md).
