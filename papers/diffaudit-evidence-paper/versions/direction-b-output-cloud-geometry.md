# Version B: Output-Cloud Geometry Mechanism

## Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Mechanism lead | opus | State the scientific hypothesis and portability boundary. |
| Scorer engineer | haiku | Keep scorer/control code bounded and auditable. |
| Visual explanation lead | sonnet | Draw response-cloud geometry, controls, and portability panels. |
| Skeptical reviewer | opus | Block feature-sweep inflation and single-cache overclaiming. |

## Target Paper

| Field | Choice |
| --- | --- |
| Working title | Output Clouds Remember: Membership Signals in Diffusion Response Geometry |
| Paper type | Mechanism-focused ML security paper |
| Venue posture | Strong workshop or short paper now; full CCF-B only with a second independent response asset |
| Current status | Candidate paper, not active main manuscript |

## Abstract Draft

Repeated diffusion queries produce a cloud of responses, not just a single
image-to-image distance. This paper studies whether geometry within that
response cloud can reveal training membership. On the H2 response-strength
cache, output-output features such as within-step repeat distance, timestep
centroid movement, and response-cloud Gram spectra reach AUC `0.961529`,
outperforming raw and lowpass H2 distance baselines. Label-shuffle controls
return random-level behavior, shared-position seed-offset controls preserve the
signal, seed `177` remains strong, and fold-disjoint cross-cache transfer
reaches mean AUC `0.959755`. The mechanism is therefore not explained by a
trivial label leak or class-ordered seed offset. However, an SD/CelebA img2img
portability check is weaker and not distinct from simple distance. We present
output-cloud geometry as a promising membership observable with an explicit
portability boundary rather than as a product-ready attack.

## Core Thesis

Membership leakage can live in the geometry among repeated diffusion outputs,
not only in direct query-to-output similarity. The current evidence is strong
inside one controlled response family, but the paper cannot claim broad
portability until a second asset confirms the mechanism.

## Main Claims

| Claim | Evidence | Boundary |
| --- | --- | --- |
| B1: Output-output geometry is a distinct observable. | Feature design excludes seed-to-output distance. | Still learned logistic fusion over engineered features. |
| B2: H2 evidence is strong and controlled. | AUC `0.961529`, label-shuffle `0.507595`, shared-position `0.967819` | One response-contract family. |
| B3: Signal transfers across controlled caches. | 176 -> 177 AUC `0.948990`, 177 -> 176 AUC `0.970520` | Cache-family transfer, not cross-model transfer. |
| B4: Portability is unresolved. | SD/CelebA img2img AUC `0.7888`, strict-tail `0.0`, below simple distance | Blocks full-paper claim unless a second asset appears. |

## Section Spine

| Section | Job |
| --- | --- |
| Introduction | Motivate response clouds as a different black-box observable. |
| Method | Define output-cloud features and the bounded scorer. |
| H2 Results | Report main metrics and simple-feature insufficiency. |
| Controls | Label shuffle, shared-position seed policy, seed stability, transfer. |
| Portability Boundary | Explain SD/CelebA img2img failure and why it matters. |
| Implications | State what a second-asset confirmation would need to prove. |

## Minimum Next Work

| Work | Why it matters |
| --- | --- |
| Find one second independent response asset with exact member/nonmember semantics. | Converts this from strong case study to full mechanism paper. |
| Add a method schematic and feature table. | Makes the mechanism reviewer-legible. |
| Pre-register one repeat-count or response-budget sensitivity only after second asset exists. | Avoids single-family feature tuning. |

## Refused Work

| Refused | Reason |
| --- | --- |
| Same-cache feature-family sweeps | Will look like overfit feature engineering. |
| Full 512/512 rerun just for symmetry | Does not resolve portability. |
| Product admission | Current consumer contract is absent. |

## Decision

Keep as the strongest technical follow-up. Do not make it the main paper until
a second response asset exists.
