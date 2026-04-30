# Research Task Queue

> Last refreshed: 2026-05-01

This file classifies future research tasks by status and priority. It is not a
timeline. Historical run IDs and dated notes are in `legacy/`.

## Current State

- Active work: `Black-box response-strength comparator preflight`
- Next GPU task: `H2 response-strength 512 / 512 validation, pending GPU collection runner promotion`
- CPU work: `Public documentation sync`
- Gray-box: paused unless a new finding changes priorities
- Strongest recent candidate: response-strength black-box result on
  `DDPM/CIFAR10`; not yet verified, not a `recon` replacement
- Internal gray-box result: useful for research triage, not public evidence

## Active

### Black-box response-strength comparator preflight

- `mode`: CPU-only boundary work
- `status`: active
- `goal`: determine whether the response-strength surface has a compatible
  black-box comparator, query-budget contract, adaptive-attacker boundary, and
  low-FPR release gate
- `GPU`: no
- `integration`: no Platform or Runtime schema change unless a concrete
  mismatch is found

Cross-box boundary hardening closed as candidate-only: current packets show AUC
movement but not stable low-FPR gains. The next honest research step is to see
whether the strongest non-admitted black-box candidate can be given a real
comparator contract without borrowing higher-permission signals.

Preflight verdict: yes, as a candidate. H2 response-strength has repeated
non-overlap signal and a same-cache simple-scorer comparator. The cache scorer
is now stable; the immediate engineering step is GPU collection runner
promotion, followed by one bounded 512 / 512 validation.

## Ready

### Public documentation sync

- `mode`: CPU-only repository hygiene
- `why ready`: run only when docs or repository surface become stale.
- `release gate`: no model run; preserve CLI arguments, JSON output fields, and
  workspace artifact schemas.

## Hold

### Stable Diffusion / CelebA adapter contract watch

- `mode`: future black-box data acquisition
- `reason for hold`: closer to verified `recon` data than the current
  `DDPM/CIFAR10` candidate, but prompt, model, split, and query-budget
  contracts are not defined.
- `reopen trigger`: CPU preflight defines a compatible data contract and
  identifies one validation experiment.

### Cross-box successor-hypothesis watch

- `mode`: cross-track support
- `reason for hold`: existing two-feature support is promoted, while
  tri-surface consensus was AUC-positive but low-FPR-unstable.
- `reopen trigger`: a new shared-surface or calibration hypothesis with
  low-FPR as the primary gate.

### White-box distinct-family watch

- `mode`: distinct-family watch
- `reason for hold`: activation-subspace, cross-layer, and trajectory variants
  all failed release gates.
- `reopen trigger`: a genuinely different observable or paper-backed family,
  not another same-observable activation scout.

### Selective / suspicion-gated routing

- `mode`: defense candidate
- `reason for hold`: fixed-budget low-FPR tail matching is real, but gate-leak
  and oracle-route falsifiers block promotion.
- `reopen trigger`: new detector or adaptive-attacker contract that directly
  addresses both falsifiers.

### Response-strength black-box candidate

- `mode`: black-box candidate
- `reason for hold`: promoted into the active CPU preflight.
- `reopen trigger`: frozen compatible comparator contract or a CPU preflight
  that can justify one future validation experiment.

## Needs Data

### Cross-box transfer / portability

- `blocker`: missing paired model contracts, paired split contracts, and one
  shared-surface hypothesis.
- `data rule`: don't schedule execution until required paired data is present
  in `Download/` or documented through workspace data manifests.

### Conditional diffusion wider-family validation

- `blocker`: current `DDPM/CIFAR10` results cannot be generalized to
  conditional diffusion. Stable Diffusion / CelebA-style data needs explicit
  local contracts before any claim or GPU run.
- `data rule`: raw datasets, weights, and supplementary files belong under
  `<DIFFAUDIT_ROOT>/Download/`, not Git.

## Closed

| Task | Result |
| --- | --- |
| CLI package/dispatch split | `diffaudit.cli` is now a package with parser and dispatch separated. |
| Cross-box evidence boundary hardening | Candidate-only. Existing cross-box packets are useful for internal comparison but do not establish stable low-FPR gains. |
| Local data boundary cleanup | Raw data and generated run outputs were moved out of the working tree. |
| Architecture triage | Fixed dependency issues; added package initializers; aligned local checks with CI. |
| Shared utility extraction | Metrics, JSON I/O, Gaussian helpers, and schedule helpers now have a package home. |
| Information architecture reset | Public docs, internal docs, workspace archives, and data boundaries were reorganized. |
| Internal gray-box triage | Restored as internal auxiliary positive; not public evidence. |
| White-box same-observable scouts | Activation-subspace and per-timestep trajectory routes closed negative-but-useful. |
| Selective routing defense scout | Closed positive-but-bounded; gate-leak and oracle-route falsifiers block promotion. |
| Cross-box tri-surface shortcut | Closed negative-but-useful; AUC-positive but low-FPR-unstable. |
| Response-strength black-box validation | Progressed to strong validated candidate; comparator and promotion paths remain blocked. |

Closed entries are traceable through
[`legacy/execution-log/2026-04-29/README.md`](../../legacy/execution-log/2026-04-29/README.md).
