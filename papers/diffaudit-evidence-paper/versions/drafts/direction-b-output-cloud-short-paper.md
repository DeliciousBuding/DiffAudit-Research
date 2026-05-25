# Direction B Draft: Output-Cloud Geometry Short Paper

## Assigned Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Mechanism lead | opus | Defines the observable, hypothesis, and portability boundary. |
| Scorer engineer | haiku | Keeps feature extraction, controls, and metric reporting bounded and auditable. |
| Visual lead | sonnet | Builds response-cloud schematics, feature tables, and control panels. |
| Skeptical reviewer | opus | Blocks feature-sweep inflation and single-family overclaiming. |

## Working Paper

| Field | Draft choice |
| --- | --- |
| Title | Output Clouds Remember: Membership Signals in Diffusion Response Geometry |
| Target type | Mechanism-focused short paper or workshop paper |
| Venue posture | Strong workshop/short-paper candidate now; full CCF-B only after second independent response asset |
| Current artifact | Markdown draft only; no LaTeX fork unless go/no-go passes |

## Abstract

Repeated diffusion queries produce a cloud of outputs rather than a single
distance measurement. This paper studies whether membership signal can appear
in the geometry among repeated responses. On the H2 response-strength cache,
output-output features such as within-step repeat distance, timestep centroid
movement, and response-cloud spectra reach AUC `0.961529`, outperforming raw
and lowpass H2 distance baselines. Label-shuffle controls return random-level
behavior, shared-position seed controls preserve the signal, seed `177` remains
strong, and fold-disjoint cross-cache transfer reaches mean AUC `0.959755`.
These results make response-cloud geometry a distinct membership observable in
one controlled H2 response family. However, an SD/CelebA img2img portability
check is weaker, has zero strict-tail recovery, and does not beat simple
distance. We therefore present output-cloud geometry as a mechanism candidate,
not a broadly portable or product-ready attack.

## Controlling Thesis

Membership leakage can be visible in relationships among repeated diffusion
responses, not only in direct query-to-output or seed-to-output similarity. The
current evidence supports a strong controlled H2 mechanism candidate. It does
not yet support a full portability claim.

## Contribution Claims

| Claim | Evidence anchor | Boundary |
| --- | --- | --- |
| B-C1: Output-output geometry is a distinct observable. | H2 feature family excludes direct seed-to-output distance. | Still engineered features and logistic scoring. |
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
| Controls | Present label shuffle, shared-position seed-offset control, seed `177` stability, and fold-disjoint cross-cache transfer. |
| Portability Boundary | Put SD/CelebA img2img failure in the main text, not an appendix. It is the scientific boundary. |
| Promotion Criteria | State what a second response asset must prove. |
| Limitations | Single-family H2 evidence, finite tails, feature-engineering risk, no product admission. |

## Figure and Table Plan

| Asset | Purpose |
| --- | --- |
| Response-cloud schematic | Shows repeated responses as an analyzable cloud instead of isolated outputs. |
| Feature-family table | Makes the scorer understandable and limits hidden feature-sweep suspicion. |
| H2 result table | Compares output-cloud, raw H2, lowpass H2, and label shuffle. |
| Control panel | Shows shared-position seed policy, seed `177`, and transfer metrics. |
| Portability boundary panel | Contrasts H2 success with SD/CelebA img2img weakness. |
| Claim-boundary table | Prevents "mechanism candidate" from reading as "new admitted black-box row." |

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
