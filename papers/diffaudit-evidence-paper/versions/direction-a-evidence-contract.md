# Version A: Evidence-Contracted Auditing

## Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Lead PI | Framework lead | Thesis, venue fit, claim boundaries, rebuttal posture. |
| Evidence engineer | Metric audit lead | Recompute admitted rows, check finite-tail denominators, verify scripts. |
| Figures editor | Visualization lead | Evidence-contract diagram, admitted-row plots, candidate boundary visuals. |
| Internal critic | Validity critic | Reject governance-only writing and require measurement insight. |

## Target Paper

| Field | Choice |
| --- | --- |
| Working title | DiffAudit: Evidence-Contracted Membership Leakage Auditing for Diffusion Models |
| Paper type | Security/privacy measurement paper |
| Venue posture | RAID / ACSAC / SaTML / measurement-oriented CCF-B target |
| Current status | Active main manuscript in `../main.tex` |

## Abstract Draft

Membership inference results for diffusion models are usually presented as
scalar metrics, but audit evidence needs a stronger contract: fixed target
identity, exact member and nonmember semantics, row-level score or response
coverage, reproducible metrics, consumer-boundary language, and surface-delta
evidence. We propose DiffAudit, an evidence-contracted methodology for
diffusion membership auditing. DiffAudit admits only rows that satisfy the
contract, keeps promising signals as candidates when portability is not proven,
and uses bounded negative results to rule out weak scientific routes. On the
current bundle, DiffAudit admits five rows spanning black-box reconstruction,
gray-box PIA, stochastic-dropout comparison, white-box GSA, and a DPDM defense
comparator. It also identifies a strong H2 output-cloud geometry candidate, but
keeps it non-admitted after a weak SD/CelebA img2img portability check. The
result is a measurement paper about when diffusion MIA scores become reusable
privacy evidence, and when they should not.

## Core Thesis

The publishable contribution is not "we have the highest AUC." The contribution
is that diffusion privacy evidence must be contracted before it can be consumed.
This turns scattered positive, candidate, and negative results into a
scientific measurement framework.

## Main Claims

| Claim | Evidence | Boundary |
| --- | --- | --- |
| A1: Five admitted rows can be compared under one audit contract. | `../evidence_bank.md`, admitted bundle JSON | Only within recorded workspace/runtime semantics. |
| A2: Access level matters. | recon AUC `0.837`, PIA AUC `0.841339`, GSA AUC `0.998192` | Not a universal benchmark across all diffusion models. |
| A3: Output-cloud geometry is promising but not yet portable. | H2 AUC `0.961529`, transfer mean `0.959755`, img2img AUC `0.7888` | Candidate only. |
| A4: Negative gates are evidence, not filler. | ReDiffuse, CommonCanvas, MIDST, Tracing Roots, SD ReDiffuse | Use to explain exclusions, not to attack original papers. |

## Section Spine

| Section | Job |
| --- | --- |
| Introduction | Establish why score-only reporting is insufficient for privacy auditing. |
| Evidence Contract | Define the six gates and finite-tail metric semantics. |
| Admitted Bundle | Present five admitted rows with cost and limitations. |
| H2 Case Study | Show discovery of a strong candidate and why it remains candidate. |
| Artifact Boundary Study | Explain weak/support-only routes as contract failures or bounded negatives. |
| Discussion | Defend the methodology as scientific measurement, not paperwork. |

## Minimum Next Work

| Work | Why it matters |
| --- | --- |
| Freeze a broader artifact-corpus protocol for Direction C reuse. | Prevents reviewer objection that negative/support routes are anecdotal. |
| Strengthen venue framing and reviewer-facing contribution wording. | Keeps the paper from reading like internal governance. |
| Add more method detail for admitted bundle generation and finite-tail metrics. | Makes the measurement protocol easier to reproduce. |

## Refused Work

| Refused | Reason |
| --- | --- |
| Full GPU reruns for table symmetry | Low decision value; current gate is paperization. |
| Promoting H2 to admitted row | Portability boundary is unresolved and partly negative. |
| New validator/CLI surface | Would be stationery unless a reviewer-facing artifact needs it. |

## Decision

Continue as the primary paper. This version best uses all current evidence
without pretending the project has solved broad cross-asset generalization.
