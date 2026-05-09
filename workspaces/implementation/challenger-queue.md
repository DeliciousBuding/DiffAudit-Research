# Research Task Queue

> Last refreshed: 2026-05-10

This file classifies future research tasks by status and priority. It is not a
timeline. Historical run IDs and dated notes are in `legacy/`.

## Current State

| Field | Value |
| --- | --- |
| Active work | `ReDiffuse scoring-contract parity review` |
| Active GPU task | none running |
| Next GPU candidate | `ReDiffuse 750k ResNet 64/64 parity packet` |
| CPU sidecar | `ReDiffuse 800k probe evidence sync`; CLiD/variation boundary maintenance |
| Gray-box status | reopened only for bounded ReDiffuse baseline alignment; PIA remains admitted |
| Non-gray-box GPU | none selected |

## Decision Inbox

| Candidate | Track | Mode | Gate | Blocker | Next action |
| --- | --- | --- | --- | --- | --- |
| ReDiffuse 750k ResNet parity | gray-box | GPU-light | 64/64 packet, `--scoring-mode resnet`, four metrics, split hash, scorer counts | none after CPU/runtime probes | run one bounded GPU packet |
| ReDiffuse 800k sanity | gray-box | CPU/GPU-light | 800k runtime probe passed; metrics not run | wait for 750k ResNet verdict | run direct-distance 64/64 only if 750k parity is interpretable |
| CLiD boundary maintenance | black-box | CPU-only | keep prompt-conditioned diagnostic claim honest | no new image-identity protocol | maintain docs, no GPU |
| Variation real-query line | black-box | CPU/API-only | query-contract audit | missing member/nonmember query images and endpoint | hold until assets exist |
| Simple-distance portability | black-box | needs assets | second image-to-image or repeated-response contract | no valid second asset contract | hold |
| White-box distinct family | white-box | CPU-first | genuinely new observable, not same-family rescue | no new hypothesis | hold |

## Active

### ReDiffuse Scoring-Contract Parity Review

- `mode`: GPU-light after CPU/runtime probes
- `status`: active
- `goal`: decide whether collaborator ReDiffuse can be compared with existing
  PIA/SecMI gray-box evidence under a paper-faithful scorer.
- `hypothesis`: the collaborator-style second-stage ResNet scorer will produce
  an interpretable 64/64 membership signal on the 750k checkpoint. If it does
  not, the direct-distance scorer remains a separate Research baseline only.
- `GPU cap`: one 750k `64/64` ResNet parity packet. Do not auto-scale to
  `128/128` or `512/512`.
- `integration`: no Platform or Runtime schema change.

Command released by the roadmap:

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit run-rediffuse-runtime-packet `
  --workspace workspaces/gray-box/runs/rediffuse-cifar10-750k-resnet-parity-20260510-gpu-64 `
  --device cuda `
  --max-samples 64 `
  --batch-size 8 `
  --attack-num 1 `
  --interval 200 `
  --average 10 `
  --k 100 `
  --scoring-mode resnet `
  --scorer-train-portion 0.2 `
  --scorer-epochs 15 `
  --scorer-batch-size 128
```

Required evidence update after the packet:

- create `docs/evidence/rediffuse-resnet-parity-packet.md`
- update `ROADMAP.md`
- update this queue
- update `workspaces/gray-box/plan.md`
- update `docs/evidence/reproduction-status.md` only if the status stage changes

Stop triggers:

- CUDA unavailable or memory pressure
- missing low-FPR fields
- missing split hash / checkpoint step / scorer contract fields
- ResNet score orientation is reversed or near-random at 64/64
- result interpretation would require Platform/Runtime schema changes

## Ready

### ReDiffuse 800k Runtime-Probe Evidence Sync

- `mode`: CPU-only
- `status`: ready
- `result`: `runtime-probe-rediffuse` can load the existing PIA 800k checkpoint
  with the collaborator ReDiffuse bundle and run a CPU preview forward pass.
- `next action`: keep as evidence note; do not run metrics until the 750k
  ResNet parity result is interpretable.

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
