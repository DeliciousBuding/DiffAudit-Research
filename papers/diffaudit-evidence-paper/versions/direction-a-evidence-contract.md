# Version A: Evidence-Contracted Measurement

## Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Lead PI | Framework lead | Thesis, venue fit, claim boundaries, rebuttal posture. |
| Evidence engineer | Metric audit lead | Recompute reportable rows, check finite-tail denominators, verify scripts. |
| Figures editor | Visualization lead | Evidence-contract diagram, reportable-row plots, candidate boundary visuals. |
| Internal critic | Validity critic | Reject governance-only writing and require measurement insight. |

## Target Paper

| Field | Choice |
| --- | --- |
| Working title | When Do Diffusion Membership-Inference Scores Become Audit Evidence? An Evidence-Contracted Measurement Study |
| Paper type | Security/privacy measurement paper |
| Venue posture | RAID / ACSAC / SaTML / measurement-oriented CCF-B target |
| Current status | Active main manuscript in `../main.tex` |

## Abstract Draft

Membership inference against diffusion models is often reported as a scalar
attack score. For a security or privacy audit, the harder measurement question
is which evidence packets survive replay, finite-tail, and consumer-boundary
checks well enough to support a specific target, split, observable, metric, and
consumer claim. This version studies evidence sufficiency for audit reports as
a measurement endpoint: given a proposed claim and an evidence packet, determine
whether the claim is being escalated beyond its observable support, and identify
the strongest wording plus first missing surface that the packet can support.
Applying the C1-C15 claim trace yields three replay-admitted packets, two
bounded source-documented point comparators, one high-AUC repeated-response
candidate that remains candidate-only after SD/CelebA img2img and
consumer-boundary gates fail, and boundary-case metadata/source-query/artifact
controls, including thirteen selected C14 public-surface stress rows. The
result is claim-bound evidence measurement.

## Core Thesis

The publishable contribution is a claim-bound measurement protocol for
consumable diffusion privacy evidence.
The paper turns scattered positive, candidate, and negative results into a
scientific measurement framework: each claim has a trace row, a first missing
surface when blocked, and an allowed wording that a reviewer can inspect.

## Main Claims

| Claim | Evidence | Boundary |
| --- | --- | --- |
| A1: Five reportable rows can be reported side by side under one audit contract only after replay tier is attached. | `../evidence_bank.md`, reportable bundle inputs, and `../data/claim_trace.csv` | Three rows are replay-admitted; two are source-documented point estimates; no cross-access ranking. |
| A2: Five role-separated rows can be reported only when replay/source tier is visible. | recon AUC `0.837`, PIA AUC `0.841339`, GSA AUC `0.998192`, DPDM W-1 AUC `0.488783` | Three rows are replay-admitted; two are source-documented point estimates; no homogeneous benchmark, interval, dominance, or access-level leaderboard claim. |
| A3: Output-cloud geometry is strong but non-admitted. | H2 AUC `0.961529`, same-family cache-robustness mean `0.959755`, img2img AUC `0.7888` | Candidate only; same-family robustness is not portability. |
| A4: Negative gates are evidence, not filler. | ReDiffuse, CommonCanvas, MIDST, Tracing Roots, SD ReDiffuse | Use to explain exclusions, not to attack original papers. |

## Section Spine

| Section | Job |
| --- | --- |
| Introduction | Establish why score-only reporting is insufficient for privacy auditing. |
| Evidence Contract | Define the six gates and finite-tail metric semantics. |
| Reportable Bundle | Present five role-separated reportable rows with cost, replay tier, and limitations. |
| H2 Case Study | Show discovery of a strong candidate and why it remains candidate. |
| Artifact Boundary Study | Explain weak/support-only routes as contract failures or bounded negatives. |
| Discussion | Defend the methodology as scientific measurement, not paperwork. |

## Minimum Next Work

| Work | Why it matters |
| --- | --- |
| Use the current Direction C corpus, fixed-search batch, and broader-source API pass carefully; add a larger distinct-surface corpus for standalone aggregate claims and external label audit only for reliability/adjudication claims. | Prevents reviewer objection that negative/support routes are anecdotal without pretending the current corpus is field-wide or reliability-scored. |
| Keep strengthening venue framing and reviewer-facing contribution wording. | Keeps the paper from reading like internal governance. |
| Preserve the evidence-sufficiency protocol in the LaTeX draft: state the audit claim template, bind the minimum evidence packet, replay or record metrics, assign gates, then choose the strongest allowed state and first missing surface. | Keeps the measurement method reproducible and falsifiable. The active main draft now states this endpoint explicitly in the Introduction. |
| Keep selected-corpus search rows inspectable but non-pooled with replay rows. | Lets Direction C support boundary-case framing without becoming a weak prevalence claim. |

## Refused Work

| Refused | Reason |
| --- | --- |
| Full GPU reruns for table symmetry | Low decision value; current gate is paperization. |
| Promoting H2 to admitted row | Portability boundary is unresolved and partly negative. |
| New validator/CLI surface | Would be stationery unless a reviewer-facing artifact needs it. |

## Decision

Continue as the primary paper. This version best uses all current evidence
without pretending the project has solved broad cross-asset generalization.
