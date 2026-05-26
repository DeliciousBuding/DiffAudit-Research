# Version B: Output-Cloud Geometry Mechanism

## Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Mechanism lead | Response geometry lead | Define the H2-only observable and keep the portability boundary in the thesis. |
| Scorer engineer | Control implementation lead | Freeze the bounded scorer description and map every metric to existing evidence. |
| Visual explanation lead | Mechanism visualization lead | Build one geometry/control/boundary figure plan from existing metrics only. |
| Skeptical reviewer | Portability critic | Block cross-model wording, product admission, and same-cache feature-sweep inflation. |

## Short-Paper Package

| Field | Choice |
| --- | --- |
| Working title | Output-Cloud Geometry as an H2-Only Membership Observable |
| One-line hook | Repeated H2 responses leak through response-cloud geometry, but the same observable fails an img2img portability gate. |
| Paper type | Mechanism-focused ML security short/workshop paper |
| Venue posture | Standalone short paper now; full CCF-B mechanism paper only with a second independent response asset |
| Current status | Candidate paper, not active main manuscript |

## Abstract Draft

Repeated diffusion queries produce a cloud of responses, not just a single
image-to-image distance. This short paper asks whether geometry inside an
audited H2 response cloud is itself a membership observable. On the H2
response-strength cache, output-output features such as within-step repeat
distance, timestep centroid movement, and response-cloud Gram spectra reach
AUC `0.961529`, outperforming the tested raw and lowpass H2 distance
baselines. Label-shuffle controls return random-level behavior,
shared-position seed-offset controls preserve the signal, seed `177` remains
strong, and fold-disjoint same-family cross-cache transfer reaches mean AUC
`0.959755`. These controls make the signal hard to dismiss as a trivial label
leak, class-ordered seed artifact, or single-seed accident inside this H2
response family. The same observable does not port cleanly to an SD/CelebA
img2img cache, where strict-tail recovery is zero and simple distance is
stronger. We therefore present output-cloud geometry as an H2-only mechanism
candidate with a negative portability result, not as a broadly portable or
product-ready diffusion MIA.

## Core Thesis

Membership signal can be recoverable from relationships among repeated H2
responses, not only from tested direct query-to-output distance baselines.
The claim stops there: current evidence supports a controlled H2 response-family
observable and a failed img2img portability boundary. It does not support
cross-model portability, cross-dataset portability, product admission, or a new
general diffusion membership attack.

## Contribution Claims

| Claim | Evidence | Boundary |
| --- | --- | --- |
| B1: A response-cloud observable. | Feature design excludes direct seed-to-output distance and uses output-output geometry: repeat distances, centroid motion, and cloud spectra. | Operational separation only; no causal mechanism claim. |
| B2: A controlled H2 positive result. | Main AUC `0.961529`, label-shuffle `0.507595`, shared-position AUC `0.967819`, seed `177` stability. | One H2 response-contract family; finite empirical tails. |
| B3: Same-family transfer, not portability. | 176 -> 177 AUC `0.948990`, 177 -> 176 AUC `0.970520`, mean `0.959755`. | Same H2 response family only; not cross-model or cross-dataset transfer. |
| B4: A negative portability boundary. | SD/CelebA img2img AUC `0.7888`, TPR@1%FPR `0.0`, TPR@0.1%FPR `0.0`, weaker than simple distance. | Blocks admitted/product/full-paper portability claims. |

## Section Spine

| Section | Job |
| --- | --- |
| Introduction | State the narrow question: can repeated H2 responses leak through their geometry? |
| Observable | Define output-cloud geometry and separate it from direct input/output distance. |
| Bounded Scorer | Freeze the feature families and logistic reporting without adding new sweeps. |
| H2 Positive Result | Report AUC/tail metrics and distance-baseline comparison inside H2 only. |
| Controls | Present label shuffle, shared-position seed policy, seed `177`, and same-family cross-cache transfer. |
| Portability Boundary | Put the SD/CelebA img2img weakness in the main argument as a result, not a caveat. |
| Go/No-Go | Define the second-asset gate required before any full-paper or admitted claim. |

## Figure/Table Spine

| Asset | Purpose |
| --- | --- |
| One response-cloud schematic | Shows repeated responses as the object of measurement, not decorative model art. |
| One feature-family table | Makes the bounded scorer inspectable and limits hidden feature-sweep suspicion. |
| One H2/control table | Combines main AUC/tails, label shuffle, seed policy, seed `177`, and same-family transfer. |
| One portability panel | Places SD/CelebA img2img weakness beside H2 success to define scope. |

## Go / No-Go

| Decision | Condition |
| --- | --- |
| Go as short/workshop paper | Current H2 positive result, controls, same-family transfer, and negative portability boundary are enough if written as a bounded mechanism case study. |
| Do not fork as full mechanism paper | No second independent response asset has validated the observable. |
| Promote to full paper | Requires a second response asset with fixed target identity, exact member/nonmember split, row-level response or score coverage, metric provenance, hashable provenance/replay, and a real surface delta over simple distance. |
| Product/admitted claim | Not allowed; H2 output-cloud remains Research-side candidate-only. |
| Refuse more H2 polishing experiments | Same-cache feature sweeps, 512/512 symmetry reruns, repeat-count tuning, KDE/shadow variants, and input-distance fusion do not resolve portability. |

## Decision

Keep Direction B as the sharpest technical short-paper candidate. Its publishable
unit is the honest contrast: strong controlled H2 response-cloud signal plus
failed img2img portability. Do not make it the main/full paper until a second
independent response asset exists.
