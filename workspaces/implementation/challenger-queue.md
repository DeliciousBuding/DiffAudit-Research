# Research Task Queue

> Last refreshed: 2026-05-10

This file classifies future research tasks by status and priority. It is not a
timeline. Historical run IDs and dated notes are in `legacy/`.

## Current State

| Field | Value |
| --- | --- |
| Active work | `I-A truth-hardening CPU review` |
| Active GPU task | none running |
| Next GPU candidate | none selected |
| CPU sidecar | CLiD/variation boundary maintenance; non-gray-box reselection watch |
| Gray-box status | ReDiffuse is candidate-only / hold; PIA remains admitted |
| Non-gray-box GPU | none selected |

## Decision Inbox

| Candidate | Track | Mode | Gate | Blocker | Next action |
| --- | --- | --- | --- | --- | --- |
| I-A truth-hardening | gray-box / defense | CPU-only | admitted PIA + stochastic-dropout needs formal, adaptive-aware, low-FPR-aware wording | no active inconsistency identified yet | audit admitted summary and innovation map |
| ReDiffuse future reopen | gray-box | needs hypothesis | 750k direct-distance positive; 750k ResNet parity negative; 800k runtime probe passed | no paper-faithful scoring parity | hold until new scorer or checkpoint-portability contract exists |
| CLiD boundary maintenance | black-box | CPU-only | keep prompt-conditioned diagnostic claim honest | no new image-identity protocol | maintain docs, no GPU |
| Variation real-query line | black-box | CPU/API-only | query-contract audit | missing member/nonmember query images and endpoint | hold until assets exist |
| Simple-distance portability | black-box | needs assets | second image-to-image or repeated-response contract | no valid second asset contract | hold |
| White-box distinct family | white-box | CPU-first | genuinely new observable, not same-family rescue | no new hypothesis | hold |

## Active

### I-A Truth-Hardening CPU Review

- `mode`: CPU-only
- `status`: active
- `goal`: keep the admitted gray-box `PIA + stochastic-dropout` claim rigorous:
  formal boundary, adaptive-attacker caveat, low-FPR metric discipline, and
  finite-sample wording.
- `latest trigger`: ReDiffuse is closed as candidate-only, so the active slot
  returns to the strongest admitted innovation line.
- `GPU cap`: no GPU released.
- `integration`: no Platform or Runtime schema change.

Required next evidence update:

- create or update an I-A truth-hardening evidence note if the audit finds stale
  or overbroad wording.
- otherwise record a no-change review and select the next CPU-first lane.

## Ready

### Public Documentation Sync

- `mode`: CPU-only repository hygiene
- `why ready`: run only when docs or repository surface become stale.
- `release gate`: no model run; preserve CLI arguments, JSON output fields, and
  workspace artifact schemas.

## Hold

### CLiD Prompt-Conditioned Diagnostic Lane

- `mode`: black-box candidate
- `reason for hold`: original prompt-conditioned packet is strong, but fixed
  prompt, swapped-prompt, within-split shuffle, prompt-text-only, and control
  attribution reviews show prompt-conditioned auxiliary instability.
- `reopen trigger`: new protocol that isolates image identity from
  prompt-conditioned auxiliary behavior and keeps low-FPR metrics primary.

### Stable Diffusion / CelebA Adapter Contract Watch

- `mode`: future black-box data acquisition
- `reason for hold`: current assets do not provide a second valid
  image-to-image or repeated-response portability contract.
- `reopen trigger`: image-to-image or unconditional-state endpoint contract
  with fixed repeats, response images, split source, and low-FPR gate.

### Cross-Box Successor-Hypothesis Watch

- `mode`: cross-track support
- `reason for hold`: existing score-sharing packets are useful internally, but
  do not establish stable low-FPR gains.
- `reopen trigger`: a new shared-surface or calibration hypothesis with
  low-FPR as the primary gate.

### White-Box Distinct-Family Watch

- `mode`: distinct-family watch
- `reason for hold`: activation-subspace, cross-layer, and trajectory variants
  all failed release gates.
- `reopen trigger`: a genuinely different observable or paper-backed family,
  not another same-observable activation scout.

### Selective / Suspicion-Gated Routing

- `mode`: defense candidate
- `reason for hold`: fixed-budget low-FPR tail matching is real, but gate-leak
  and oracle-route falsifiers block promotion.
- `reopen trigger`: new detector or adaptive-attacker contract that directly
  addresses both falsifiers.

### Response-Strength Black-Box Candidate

- `mode`: black-box candidate
- `reason for hold`: positive-but-bounded on `DDPM/CIFAR10`, but not admitted
  or portable.
- `reopen trigger`: a cross-asset black-box contract with dataset, model, split,
  and query-budget boundaries.

### Variation Real-Query Line

- `mode`: API-only black-box
- `reason for hold`: missing real query-image set and real endpoint.
- `reopen trigger`: `Download/black-box/datasets/variation-query-set` contains
  member/nonmember images and a real endpoint contract is available.

## Needs Data

| Need | Blocker | Data rule |
| --- | --- | --- |
| Cross-box transfer / portability | missing paired model contracts, paired split contracts, and one shared-surface hypothesis | do not schedule execution until required paired data is present in `Download/` or documented through workspace manifests |
| Conditional diffusion wider-family validation | current `DDPM/CIFAR10` results cannot generalize to conditional diffusion | raw datasets, weights, and supplementary files belong under `<DIFFAUDIT_ROOT>/Download/`, not Git |
| Simple-distance second asset | no valid second image-to-image or repeated-response contract | preflight before GPU |

## Closed

| Task | Result |
| --- | --- |
| ReDiffuse collaborator bundle intake | Positive intake; complete enough for bounded compatibility review, not admitted evidence. |
| ReDiffuse 750k direct-distance packet | Positive compatibility packet at 64/64; not comparable with PIA/SecMI without scoring-mode caveat. |
| Recon tail confidence review | Admitted-finite-tail-only; recon remains black-box product row. |
| Semantic-auxiliary low-FPR review | Negative-but-useful; no GPU packet selected. |
| Variation query-contract audit | Blocked by missing real query images and endpoint. |
| H2 simple-distance product bridge comparison | Recon remains product row; simple-distance remains Research evidence only. |
| CLiD prompt-conditioned probing | Hold-candidate; strong original packet but prompt controls block admission. |
| Cross-box evidence boundary hardening | Candidate-only; current packets do not establish stable low-FPR gains. |
| Shared utility extraction | Metrics, JSON I/O, Gaussian helpers, and schedule helpers now have a package home. |
| Information architecture reset | Public docs, internal docs, workspace archives, and data boundaries were reorganized. |

Older closed entries are traceable through
[`legacy/execution-log/2026-04-29/README.md`](../../legacy/execution-log/2026-04-29/README.md).
