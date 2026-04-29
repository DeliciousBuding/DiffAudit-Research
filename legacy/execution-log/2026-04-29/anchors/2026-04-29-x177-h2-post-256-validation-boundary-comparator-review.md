# X-177 H2 Post-256 Validation Boundary And Comparator Review

Date: 2026-04-29
Status: `positive boundary / comparator-first hold`

## Question

After `X-176` passed a frozen non-overlap `256 / 256` H2 validation rung, should H2 be promoted, should another GPU rung be released, or should the mainline move to same-packet comparator and calibration work first?

## Inputs

- X168 first scout:
  - `workspaces/implementation/2026-04-29-x168-blackbox-h2-strength-response-gpu-scout.md`
- X171 frequency boundary:
  - `workspaces/implementation/2026-04-29-x171-h3-frequency-filter-cache-ablation.md`
- X172 non-overlap `128 / 128` validation:
  - `workspaces/implementation/2026-04-29-x172-h2-strength-response-validation.md`
- X174 contract:
  - `workspaces/implementation/2026-04-29-x174-h2-comparator-adaptive-validation-contract.md`
- X175 cache stress:
  - `workspaces/implementation/2026-04-29-x175-h2-query-budget-scorer-stability-cache-stress.md`
- X176 non-overlap `256 / 256` validation:
  - `workspaces/implementation/2026-04-29-x176-h2-nonoverlap-256-validation.md`

## Evidence Stack

H2 now has three positive packet levels plus one positive CPU stress gate:

| Stage | Packet | Primary raw H2 AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | Read |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `X-168` | `64 / 64` | `0.928955` | `0.859375` | `0.218750` | `0.218750` | first scout positive |
| `X-172` | `128 / 128` | `0.887756` | `0.808594` | `0.093750` | `0.062500` | non-overlap validation positive |
| `X-175` | cache stress | `0.885742` | `0.808594` | `0.078125` | `0.054688` | query/scorer stress positive |
| `X-176` | `256 / 256` | `0.913940` | `0.851562` | `0.171875` | `0.062500` | larger non-overlap validation positive |

Mandatory secondary `lowpass_0_5` status:

- `X-171`: did not falsify H2 as high-frequency-only
- `X-172`: `0.195312 / 0.078125`
- `X-175`: stress gate passed; raw stayed primary
- `X-176`: still positive at `0.140625 / 0.050781`

## Decision Review

| Candidate decision | Decision | Reason |
| --- | --- | --- |
| Promote H2 to admitted black-box evidence | hold | H2 now has scale and stress support, but still lacks a same-packet `recon` comparator, threshold calibration, and system consumer contract. |
| Replace `recon` with H2 in the main black-box story | reject | `recon` remains the admitted black-box main evidence. H2 is a strong candidate surface, not a replacement. |
| Run another H2 GPU packet immediately | reject | The validation stack is no longer bottlenecked on sample count; the next blocker is comparator/calibration truth. |
| Promote `lowpass_0_5` to primary | reject | X176 supports raw as primary. `lowpass_0_5` remains mandatory secondary/boundary check. |
| Start same-packet `recon` comparator feasibility | select | This is the shortest honest path toward admission or a hard candidate-only boundary. |
| Start Runtime/Platform handoff | reject | No runner schema, report field, or UI contract should consume H2 before comparator/calibration review. |

## Required Next Contract

`X-178` should be CPU-first and decide whether a same-packet `recon` comparator is implementable on the PIA DDPM/CIFAR10 packet family.

Minimum fields:

- packet identity:
  - use X176 member/nonmember canonical indices if possible
  - otherwise freeze the reason same-packet comparison is impossible
- comparator:
  - `recon` score extraction path
  - score orientation
  - low-FPR metrics under the same labels
- comparison:
  - raw H2 primary
  - `lowpass_0_5` H2 secondary
  - `recon` baseline
  - optional simple H2 baselines retained as sanity checks
- output:
  - machine-readable summary
  - verdict on `comparator-implementable`, `comparator-blocked`, or `candidate-only freeze`

## Verdict

`positive boundary / comparator-first hold`

H2 should now be described as:

- `strong validated DDPM/CIFAR10 black-box candidate surface`
- not admitted evidence
- not a `recon` replacement
- not a Runtime/Platform contract
- not conditional-diffusion, Stable Diffusion, DiT, or commercial-model evidence

## Control State

- `active_gpu_question = none`
- `next_gpu_candidate = none until X178 same-packet recon comparator feasibility review`
- `current_execution_lane = X178 same-packet recon comparator feasibility review`
- `cpu_sidecar = I-A / cross-box boundary maintenance`

## Handoff

- `Platform`: no handoff.
- `Runtime-Server`: no handoff.
- `Docs/materials`: note-level only. If mentioned, H2 must be framed as a strong internal candidate requiring same-packet comparator review.
