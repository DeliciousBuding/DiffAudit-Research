# Direction B Draft: Output-Cloud Geometry Short Paper

## Assigned Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Mechanism lead | Response geometry lead | Defines the H2-only observable and writes the portability boundary into the thesis. |
| Scorer engineer | Control implementation lead | Freezes feature extraction, controls, and metric reporting against existing evidence only. |
| Visual lead | Mechanism visualization lead | Builds one schematic/control/boundary figure plan, not decorative diagrams. |
| Skeptical reviewer | Portability critic | Blocks cross-model claims, product admission, and extra same-cache feature sweeps. |

## Working Paper

| Field | Draft choice |
| --- | --- |
| Title | Response-Cloud Geometry Reveals an H2 Membership Signal |
| Subtitle | A bounded H2 response-family observable with a failed img2img portability gate |
| Target type | Mechanism-focused short paper or workshop paper |
| Venue posture | Strong workshop/short-paper candidate now; full CCF-B only after second independent response asset |
| Current artifact | Markdown draft only; no LaTeX fork unless go/no-go passes |

## Abstract

Repeated diffusion queries produce a cloud of outputs rather than a single
distance measurement. This paper asks a narrower question: can the geometry
among repeated H2 responses reveal membership when direct distance baselines
are not the whole story? On the H2 response-strength cache, output-output
features such as within-step repeat distance, timestep centroid movement, and
response-cloud spectra reach AUC `0.961529`, outperforming the tested raw and
lowpass H2 distance baselines. Label-shuffle controls return random-level
behavior, shared-position seed controls preserve the signal, seed `177` remains
strong, and fold-disjoint same-family cross-cache transfer reaches mean AUC
`0.959755`. These results make response-cloud geometry an operationally
distinct H2 observable within this response family. The boundary is equally
important: an SD/CelebA img2img portability check is weaker, has zero
strict-tail recovery, and does not beat simple distance. We therefore present
output-cloud geometry as a Research-side H2 mechanism candidate with a negative
portability result, not as a broadly portable or product-ready attack.

## Controlling Thesis

In one audited H2 repeated-response family, membership signal is recoverable
from relationships among generated responses, not only from the tested direct
query-to-output or seed-to-output similarity baselines. The paper's scientific
unit is the contrast between this positive controlled H2 result and the negative
SD/CelebA img2img portability check. It does not support broad portability,
cross-model transfer, cross-dataset transfer, or product admission.

## Standalone Version Definition

This version is a deliberately narrow mechanism paper. It should read as:

> We found a strong and controlled response-cloud observable in one H2 diffusion
> response family, then used an img2img portability failure to define the
> boundary of that observable.

It should not read as:

> We built a new general diffusion membership attack or admitted black-box row.

The paper can stand alone only as a short/workshop paper unless a second
independent response asset appears. Its scientific value is the contrast between
positive within-family controls and negative portability evidence.

## Contribution Claims

| Claim | Evidence anchor | Boundary |
| --- | --- | --- |
| B-C1: Response-cloud geometry is a distinct observable. | H2 feature family excludes direct seed-to-output distance and is compared with raw/lowpass H2 baselines. | Operational distinction only; no causal mechanism claim. |
| B-C2: The H2 signal is strong under bounded controls. | Main AUC `0.961529`, label shuffle `0.507595`, shared-position AUC `0.967819`, seed `177` stability. | One response-contract family; finite empirical tails. |
| B-C3: Same-family cache transfer is strong. | Transfer mean AUC `0.959755`. | Same H2 response family only; not cross-model or cross-dataset transfer. |
| B-C4: Portability is negative under the tested img2img gate. | SD/CelebA img2img AUC `0.7888`, strict tail `0.0`, weaker than simple distance. | Blocks full-paper portability and admitted/product claims. |
| B-C5: The boundary is a contribution, not a weakness to hide. | H2 controls and img2img failure are both in the main argument. | Do not bury negative portability in limitations. |

## Manuscript Spine

| Section | Draft content |
| --- | --- |
| Introduction | State the narrow question: whether repeated H2 responses separate through geometry. |
| Observable | Define output-cloud geometry and contrast it with direct image distance, seed-distance, and response consistency. |
| Bounded Scorer | Describe only frozen feature families: within-timestep repeat RMSE, timestep centroid movement, Gram/PCA spectral summaries, and logistic metric reporting. |
| H2 Positive Result | Compare output-cloud features with raw H2 and lowpass baselines inside H2 only. |
| Controls | Present label shuffle, shared-position seed-offset control, seed `177` stability, and fold-disjoint same-family cross-cache transfer. |
| Boundary Result | Put SD/CelebA img2img failure in the main text as the portability result. |
| Promotion Test | State what a second response asset must prove before full-paper or admitted claims. |
| Limitations | Single-family H2 evidence, finite tails, engineered features, no cross-model portability, no product admission. |

## Section-Level Draft Skeleton

| Section | Claim to make | Required evidence | Text boundary |
| --- | --- | --- | --- |
| 1. Introduction | Repeated responses can be treated as a response cloud, and one H2 cloud carries membership signal. | H2 main result and controls. | Say "can in this audited family," not "generally does." |
| 2. Response-Cloud Observable | Output-output features are operationally different from direct input/output distance. | Feature definitions and exclusion of direct seed-to-output distance. | Do not claim causal mechanism or universal geometry. |
| 3. H2 Positive Result | The H2 response-strength cache has strong separability. | AUC `0.961529`, TPR tails, raw/lowpass baseline comparison. | Report finite packet denominators; avoid calibrated sub-percent risk language. |
| 4. Controls | The signal survives same-family controls and fails label shuffle. | Label shuffle `0.507595`, shared-position `0.967819`, seed and cache-transfer rows. | Same-family robustness only. |
| 5. Boundary Result | SD/CelebA img2img does not validate portability. | AUC `0.7888`, zero strict-tail recovery, negative delta vs distance. | Make this a main result, not a footnote. |
| 6. Promotion Test | A second response asset is required for full-paper and admitted claims. | Six-gate contract. | No product/admitted language. |

## Reader Contract: Why This Is Not a General Attack

This version must include a compact boundary paragraph after the H2 result
table. The paragraph should state that the evidence comes from one H2
response-contract family, uses an engineered logistic scorer, has no second
independent response asset, is not admitted to the product/runtime bundle, and
has a negative SD/CelebA img2img portability boundary. If a best-single-feature
or feature-family ablation is not already available in the evidence bank, the
paper should avoid claiming that the fused feature family is intrinsically
better than every simpler H2 feature; the supported claim is separation from
the tested raw and lowpass H2 distance baselines.

## Figure and Table Plan

| Asset | Purpose |
| --- | --- |
| Response-cloud schematic | Shows repeated responses as the analyzable object instead of isolated outputs. |
| Feature-family table | Makes the frozen scorer understandable and limits hidden feature-sweep suspicion. |
| H2/control table | Compares output-cloud, raw H2, lowpass H2, label shuffle, seed policy, seed `177`, and same-family transfer. |
| Portability boundary panel | Contrasts H2 success with SD/CelebA img2img weakness. |
| Claim-boundary table | Prevents "mechanism candidate" from reading as "new admitted black-box row." |

## Allowed Wording

| Allowed | Evidence | Prohibited |
| --- | --- | --- |
| "strong Research-side H2 mechanism candidate" | H2 main, controls, and same-family transfer rows | "general diffusion membership attack" |
| "same-family cross-cache robustness" | seed `176 -> 177` and `177 -> 176` transfer | "cross-model transfer" or "cross-dataset transfer" |
| "portability boundary" | SD/CelebA img2img weakness and zero strict-tail recovery | "product-ready attack" or "admitted black-box row" |
| "negative img2img portability result" | AUC `0.7888`, zero strict-tail recovery, weaker than simple distance | "validated portability" |

## Team Work Order

| Team member | Next useful action | Explicit non-action |
| --- | --- | --- |
| Mechanism lead | Write introduction and thesis around "observable plus boundary" rather than "new attack." | Do not sell H2 as general diffusion evidence. |
| Scorer engineer | Freeze feature-family description and ensure every number maps to an existing metric artifact. | Do not run more H2 sweeps for symmetry. |
| Visual lead | Draw one schematic plus one combined H2/control/boundary panel from existing metrics. | Do not create diagrams that hide the single-family boundary. |
| Skeptical reviewer | Check every sentence for cross-model, cross-dataset, or product-admission leakage. | Do not request new experiments unless they change standalone viability. |

## Review Risks and Fixes

| Risk | Fix |
| --- | --- |
| Reviewers read it as overfit feature engineering. | Freeze feature families, report controls, and do not add same-cache sweeps. |
| Cross-cache transfer is mistaken for cross-model transfer. | Call it H2 response-family robustness only. |
| "Mechanism" sounds causal. | Use "observable" or "mechanism candidate" unless a second asset proves portability. |
| img2img result is read as a failed attack. | Make it the boundary result that defines honest scope. |
| Short paper looks too narrow. | Claim the narrowness explicitly: a positive controlled result plus a negative portability gate. |

## Go / No-Go

| Decision | Condition |
| --- | --- |
| Keep as short-paper draft | Current evidence supports a bounded H2 mechanism case study with a negative portability result. |
| Fork LaTeX as standalone short paper | Allowed only if scoped as H2 response-family observable plus img2img boundary; no product/admitted language. |
| Promote to full paper | Requires second independent response asset passing fixed target identity, exact split, row-level response/score coverage, metric provenance, hashable provenance/replay, and real surface delta. |
| Admit to product/runtime | No-go; H2 output-cloud remains Research-side candidate-only. |
| Refuse more work | Do not fork for more H2 feature sweeps, 512/512 symmetry reruns, repeat-count tuning, KDE/shadow variants, or input-distance fusion. |
