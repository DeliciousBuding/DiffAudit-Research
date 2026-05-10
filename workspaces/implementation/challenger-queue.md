# Research Task Queue

> Last refreshed: 2026-05-10

This file classifies future research tasks by status and priority. It is not a
timeline. Historical run IDs and dated notes are in `legacy/`.

## Current State

| Field | Value |
| --- | --- |
| Active work | `post-response-contract discovery reselection` |
| Active GPU task | none running |
| Next GPU candidate | none selected |
| CPU sidecar | none; response-contract discovery closed as needs-assets |
| Gray-box status | ReDiffuse candidate-only; PIA remains admitted |
| Non-gray-box GPU | none selected |

## Decision Inbox

| Candidate | Track | Mode | Gate | Blocker | Next action |
| --- | --- | --- | --- | --- | --- |
| black-box second response-contract acquisition | black-box | needs-assets | post-ReDiffuse reselection selected this lane; repository-level discovery found no ready package | missing second compatible response contract package | acquire or construct package matching `BB-DS-01` and `BB-SUP-03`, then rerun discovery and package preflight |
| Kandinsky/Pokemon response-contract package | black-box | CPU-only | package preflight executable; supplementary root present | missing query split, endpoint contract, response manifest, and responses | build/acquire package; do not GPU-scale |
| ReDiffuse future reopen | gray-box | hold | exact replay shows modest AUC but weak strict-tail evidence | no admitted promotion; 800k shortcut remains blocked | reopen only with new scorer hypothesis or stricter paper-faithful contract |
| GSA loss-score LR stability | white-box | CPU-only | leave-one-shadow-out review failed release gate | LR did not beat threshold in enough held-out/target folds | closed; do not GPU-scale |
| CLiD boundary maintenance | black-box | CPU-only | keep prompt-conditioned diagnostic claim honest | no new image-identity protocol | maintain docs, no GPU |
| Variation real-query line | black-box | CPU/API-only | query-contract audit | missing member/nonmember query images and endpoint | hold until assets exist |
| Simple-distance portability | black-box | needs assets | second image-to-image or repeated-response contract | no valid second asset contract | hold |
| White-box distinct family | white-box | CPU-first | genuinely new observable, not same-family rescue | no new hypothesis | hold |

## Active

### Post-Response-Contract Discovery Reselection

- `mode`: CPU-only
- `status`: active
- `goal`: choose the next bounded research lane after black-box second
  response-contract discovery closed as `needs-assets`.
- `latest trigger`: repository-level response-contract discovery found no
  ready paired package under `Download/black-box`.
- `GPU cap`: none
- `integration`: none

Current evidence:

- [../../docs/evidence/rediffuse-checkpoint-portability-gate.md](../../docs/evidence/rediffuse-checkpoint-portability-gate.md)
- [../../docs/evidence/rediffuse-resnet-contract-scout.md](../../docs/evidence/rediffuse-resnet-contract-scout.md)
- [../../docs/evidence/rediffuse-exact-replay-preflight.md](../../docs/evidence/rediffuse-exact-replay-preflight.md)
- [../../docs/evidence/rediffuse-exact-replay-packet.md](../../docs/evidence/rediffuse-exact-replay-packet.md)
- [../../docs/evidence/post-rediffuse-next-lane-reselection.md](../../docs/evidence/post-rediffuse-next-lane-reselection.md)
- [../../docs/evidence/blackbox-response-contract-acquisition-audit.md](../../docs/evidence/blackbox-response-contract-acquisition-audit.md)
- [../../docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](../../docs/evidence/blackbox-response-contract-asset-acquisition-spec.md)
- [../../docs/evidence/blackbox-response-contract-package-preflight.md](../../docs/evidence/blackbox-response-contract-package-preflight.md)
- [../../docs/evidence/blackbox-response-contract-discovery.md](../../docs/evidence/blackbox-response-contract-discovery.md)
- [../../docs/evidence/research-resting-state-audit-20260510.md](../../docs/evidence/research-resting-state-audit-20260510.md)
- [../../docs/evidence/gsa-loss-score-shadow-stability-review.md](../../docs/evidence/gsa-loss-score-shadow-stability-review.md)

Restart conditions:

- continue scouting or constructing a second response-contract asset package,
  or reselect a non-blocked CPU-first research lane.
- do not run 800k ReDiffuse metrics as an automatic shortcut.
- do not run larger ReDiffuse packets without a new scorer hypothesis and CPU
  preflight.
- do not GPU-scale GSA loss-score LR from the current stability review.
- open a new scorer, protocol, or observable only if it has a falsifier and CPU
  preflight.

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
| Simple-distance second asset | no valid second image-to-image or repeated-response contract | follow [../../docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](../../docs/evidence/blackbox-response-contract-asset-acquisition-spec.md) before GPU |

## Closed

| Task | Result |
| --- | --- |
| ReDiffuse checkpoint-portability gate | blocked-by-scoring-contract; 800k checkpoint compatibility is not enough to release metrics. |
| ReDiffuse ResNet contract scout | blocked-by-contract-mismatch; current Research `resnet` mode is not exact collaborator replay. |
| ReDiffuse exact replay preflight | CPU preflight passed; `resnet_collaborator_replay` mode is available, no GPU release yet. |
| ReDiffuse 750k exact replay | Candidate-only; modest AUC but weak strict-tail evidence, no admitted promotion. |
| Kandinsky/Pokemon response-contract package preflight | needs-assets; supplementary root exists, but no member/nonmember query package or response contract exists. |
| GSA loss-score shadow stability | negative-but-useful; leave-one-shadow-out LR failed the distinct-scorer release gate. |
| Research resting-state audit | No active GPU candidate or reducible CPU sidecar until assets or a new hypothesis arrive. |
| Black-box response-contract asset-acquisition spec | needs-assets; minimum second-asset package defined; no GPU release. |
| Black-box response-contract discovery | needs-assets; discovery found no paired second response-contract package under black-box dataset/supplementary roots. |
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
