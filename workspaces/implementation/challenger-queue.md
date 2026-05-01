# Research Task Queue

> Last refreshed: 2026-05-01

This file classifies future research tasks by status and priority. It is not a
timeline. Historical run IDs and dated notes are in `legacy/`.

## Current State

- Active work: `post-recon next-lane selection`
- Next GPU task: `none selected`
- CPU work: `product-bridge sync and next black-box/innovation lane selection`
- Gray-box: paused unless a new finding changes priorities
- Strongest recent candidate: response-strength black-box result on
  `DDPM/CIFAR10`; positive-but-bounded, not a `recon` replacement
- Internal gray-box result: useful for research triage, not public evidence

## Active

### Post-recon next-lane selection

- `mode`: CPU-first research selection
- `status`: active
- `goal`: choose the next bounded research lane after recon was promoted with coherent four-metric reporting
- `GPU`: no
- `integration`: no Platform or Runtime schema change unless a concrete
  mismatch is found

The CPU-only reselection is recorded in
[../../docs/evidence/non-clid-blackbox-reselection.md](../../docs/evidence/non-clid-blackbox-reselection.md).
CLiD moved to hold-candidate after prompt-control attribution. The recon
product-validation packet is now the admitted black-box row with coherent
four-metric reporting. The result is recorded in
[../../docs/evidence/recon-product-validation-result.md](../../docs/evidence/recon-product-validation-result.md)
and the product boundary is recorded in
[../../docs/product-bridge/recon-product-validation-handoff.md](../../docs/product-bridge/recon-product-validation-handoff.md).

## Ready

### Public documentation sync

- `mode`: CPU-only repository hygiene
- `why ready`: run only when docs or repository surface become stale.
- `release gate`: no model run; preserve CLI arguments, JSON output fields, and
  workspace artifact schemas.

## Hold

### CLiD prompt-conditioned diagnostic lane

- `mode`: black-box candidate
- `reason for hold`: original prompt-conditioned packet is strong, but fixed
  prompt, swapped-prompt, within-split shuffle, prompt-text-only, and control
  attribution reviews show prompt-conditioned auxiliary instability.
- `reopen trigger`: new protocol that isolates image identity from
  prompt-conditioned auxiliary behavior and keeps low-FPR metrics primary.

CLiD was selected after H2 text-to-image transfer was blocked by protocol
mismatch. The bridge preparation, schema gate, 100/100 score packet, integrity
review, and independent repeat all succeeded under the original
prompt-conditioned contract. Admission is blocked because prompt-neutral,
swapped-prompt, within-split shuffle, prompt-text-only, and attribution controls
show that the strict-tail signal is degraded and auxiliary-feature stability is
not robust. The canonical boundary is recorded in
[../../docs/evidence/clid-prompt-conditioning-boundary.md](../../docs/evidence/clid-prompt-conditioning-boundary.md).
No next CLiD GPU task is selected.

### Stable Diffusion / CelebA adapter contract watch

- `mode`: future black-box data acquisition
- `reason for hold`: assets are ready, but prompt-only text-to-image is not an
  H2-compatible contract.
- `reopen trigger`: image-to-image or unconditional-state endpoint contract
  with fixed repeats, response images, split source, and low-FPR gate.

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
- `reason for hold`: positive-but-bounded on `DDPM/CIFAR10`, but not admitted
  or portable.
- `reopen trigger`: a cross-asset black-box contract with dataset, model, split,
  and query-budget boundaries.

### Variation real-query line

- `mode`: API-only black-box
- `reason for hold`: missing real query-image set and real endpoint.
- `reopen trigger`: `Download/black-box/datasets/variation-query-set` contains
  member/nonmember images and a real endpoint contract is available.

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
| H2 raw-primary 512 / 512 validation | Negative-but-useful. Raw H2 kept AUC signal but failed `TPR@0.1%FPR`; lowpass tail review remains active. |
| H2 lowpass follow-up 512 / 512 validation | Positive-but-bounded. Cutoff-0.50 lowpass passed the frozen candidate gate; H2 remains candidate-only and needs portability evidence before promotion. |
| H2 SD/CelebA text-to-image preflight | Negative-but-useful. Assets are ready, but prompt-only text-to-image is not H2-compatible. |
| Black-box next-lane reselection, first pass | CLiD selected for bounded prompt-conditioned probing. Recon stayed admitted baseline; variation lacked real query assets; H2 portability needed image-conditioned protocol. |
| CLiD prompt-conditioned probing | Hold-candidate. Strong original packet, but prompt controls and attribution block admission as general black-box evidence. |
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
