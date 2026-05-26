# Direction B Draft: Output-Cloud Geometry Short Paper

## Assigned Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Mechanism lead | Response geometry lead | Defines the observable, hypothesis, and portability boundary. |
| Scorer engineer | Control implementation lead | Keeps feature extraction, controls, and metric reporting bounded and auditable. |
| Visual lead | Mechanism visualization lead | Builds response-cloud schematics, feature tables, and control panels. |
| Skeptical reviewer | Portability critic | Blocks feature-sweep inflation and single-family overclaiming. |

## Working Paper

| Field | Draft choice |
| --- | --- |
| Title | Output-Cloud Geometry in a Controlled H2 Diffusion Response Family |
| Target type | Mechanism-focused short paper or workshop paper |
| Venue posture | Strong workshop/short-paper candidate now; full CCF-B only after second independent response asset |
| Current artifact | Markdown draft only; no LaTeX fork unless go/no-go passes |

## Abstract

Repeated diffusion queries produce a cloud of outputs rather than a single
distance measurement. This paper studies whether membership signal can appear
in output-output geometry inside an audited H2 repeated-response cache. On the
H2 response-strength cache,
output-output features such as within-step repeat distance, timestep centroid
movement, and response-cloud spectra reach AUC `0.961529`, outperforming raw
and lowpass H2 distance baselines. Label-shuffle controls return random-level
behavior, shared-position seed controls preserve the signal, seed `177` remains
strong, and fold-disjoint same-family cross-cache transfer reaches mean AUC
`0.959755`. These results make response-cloud geometry an operationally
distinct H2 observable relative to the tested raw and lowpass H2 distance
baselines. However, an SD/CelebA img2img portability check is weaker, has zero
strict-tail recovery, and does not beat simple distance. We therefore present
output-cloud geometry as a Research-side H2 mechanism candidate, not a broadly
portable or product-ready attack.

## Controlling Thesis

Output-cloud geometry is a strong controlled H2 response-family signal with an
explicit failed portability boundary. In the audited H2 repeated-response
cache, membership signal is recoverable from relationships among repeated
responses, not only from the tested direct query-to-output or seed-to-output
similarity baselines. The current evidence supports a strong controlled H2
mechanism candidate. It does not support broad portability, cross-model
transfer, or product admission.

## Standalone Version Definition

This version is a deliberately narrow mechanism paper. It should read as:

> We found a strong and controlled response-cloud observable in one H2 diffusion
> response family, then used portability failure to define the boundary of that
> observable.

It should not read as:

> We built a new general diffusion membership attack.

The paper can stand alone only as a short/workshop paper unless a second
independent response asset appears. Its scientific value is the contrast between
positive within-family controls and negative portability evidence.

## Contribution Claims

| Claim | Evidence anchor | Boundary |
| --- | --- | --- |
| B-C1: Output-output geometry is operationally separated from the tested H2 distance baselines. | H2 feature family excludes direct seed-to-output distance and is compared with raw/lowpass H2 baselines. | Still engineered features and logistic scoring; not a causal mechanism claim. |
| B-C2: H2 evidence is strong under controls. | Main AUC `0.961529`, label shuffle `0.507595`, shared-position `0.967819` | One response-contract family. |
| B-C3: Same-family cache transfer is strong. | Transfer mean AUC `0.959755` | Not cross-model or cross-dataset transfer. |
| B-C4: Portability is unresolved and partly negative. | SD/CelebA img2img AUC `0.7888`, strict tail `0.0`, weaker than simple distance | Blocks full-paper portability claim. |

## Manuscript Spine

| Section | Draft content |
| --- | --- |
| Introduction | Motivate response clouds: repeated stochastic outputs form a distributional object that may reveal membership. |
| Observable | Define output-cloud geometry and contrast it with direct image distance, seed-distance, and response consistency. |
| Bounded Scorer | Describe feature families: within-timestep repeat RMSE, timestep centroid movement, Gram/PCA spectral summaries, and logistic metric reporting. |
| H2 Main Result | Compare output-cloud features with raw H2 and lowpass baselines. |
| Controls | Present label shuffle, shared-position seed-offset control, seed `177` stability, and fold-disjoint same-family cross-cache transfer. |
| Portability Boundary | Put SD/CelebA img2img failure in the main text, not an appendix. It is the scientific boundary. |
| Promotion Criteria | State what a second response asset must prove. |
| Limitations | Single-family H2 evidence, finite tails, feature-engineering risk, no product admission. |

## Section-Level Draft Skeleton

| Section | Claim to make | Required evidence | Text boundary |
| --- | --- | --- | --- |
| 1. Introduction | Repeated responses can be treated as a cloud, and this cloud can contain membership signal. | H2 main result and controls. | Say "can" in one audited family, not "generally does." |
| 2. Response-Cloud Observable | Output-output features are operationally different from direct input/output distance. | Feature definitions and exclusion of direct seed-to-output distance. | Do not claim causal mechanism. |
| 3. H2 Result | The H2 response-strength cache has strong separability. | AUC `0.961529`, TPR tails, raw/lowpass baseline comparison. | Report finite packet denominators. |
| 4. Controls | The signal survives same-family controls and fails label shuffle. | Label shuffle `0.507595`, shared-position `0.967819`, seed and cache-transfer rows. | Same-family robustness only. |
| 5. Boundary Result | SD/CelebA img2img weakens portability. | AUC `0.7888`, zero strict-tail recovery, negative delta vs distance. | Make this a main result, not a footnote. |
| 6. Promotion Test | A second response asset is required for full-paper claims. | Six-gate contract. | No product/admitted language. |

## Why This Is Not a General Attack

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
| Response-cloud schematic | Shows repeated responses as an analyzable cloud instead of isolated outputs. |
| Feature-family table | Makes the scorer understandable and limits hidden feature-sweep suspicion. |
| H2 result table | Compares output-cloud, raw H2, lowpass H2, and label shuffle. |
| Control panel | Shows shared-position seed policy, seed `177`, and same-family cross-cache transfer metrics. |
| Portability boundary panel | Contrasts H2 success with SD/CelebA img2img weakness. |
| Claim-boundary table | Prevents "mechanism candidate" from reading as "new admitted black-box row." |

## Allowed Wording

| Allowed | Evidence | Prohibited |
| --- | --- | --- |
| "strong Research-side H2 mechanism candidate" | H2 main, controls, and same-family transfer rows | "general diffusion membership attack" |
| "same-family cross-cache robustness" | seed `176 -> 177` and `177 -> 176` transfer | "cross-model transfer" or "cross-dataset transfer" |
| "portability boundary" | SD/CelebA img2img weakness and zero strict-tail recovery | "product-ready attack" or "admitted black-box row" |

## Team Work Order

| Team member | Next useful action | Explicit non-action |
| --- | --- | --- |
| Mechanism lead | Rewrite the introduction around "observable plus boundary" rather than "new attack." | Do not sell H2 as general diffusion evidence. |
| Scorer engineer | Freeze feature-family description, cite any existing best-single-feature evidence, and ensure every number maps to an existing metric artifact. | Do not run more H2 sweeps for symmetry. |
| Visual lead | Draw one schematic and one control panel from existing metrics. | Do not create decorative diagrams that hide the single-family boundary. |
| Skeptical reviewer | Check every sentence for cross-model, cross-dataset, or product-admission leakage. | Do not request new experiments unless they change standalone viability. |

## Review Risks and Fixes

| Risk | Fix |
| --- | --- |
| Reviewers read it as overfit feature engineering. | Freeze feature families, report controls, and do not add same-cache sweeps. |
| Cross-cache transfer is mistaken for cross-model transfer. | Call it H2 response-family robustness only. |
| "Mechanism" sounds causal. | Use "observable" or "mechanism candidate" unless a second asset proves portability. |
| img2img result weakens the story. | Make it the boundary result that defines honest scope. |

## Go / No-Go

| Decision | Condition |
| --- | --- |
| Keep as short-paper draft | Current state supports this. |
| Fork LaTeX as standalone short paper | Allowed if scoped explicitly as H2 mechanism case study with portability failure central. |
| Promote to full paper | Requires second independent response asset passing fixed target identity, exact split, row-level response/score coverage, metric provenance, hashable provenance/replay, and real surface delta. |
| Refuse more work | Do not fork for more H2 feature sweeps, 512/512 symmetry reruns, repeat-count tuning, KDE/shadow variants, or input-distance fusion. |
