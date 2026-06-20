# Direction B Draft: Output-Cloud Geometry Short Paper

## Assigned Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Observable lead | Response geometry lead | Defines the H2-only observable and writes the portability boundary into the thesis. |
| Scorer engineer | Control implementation lead | Freezes feature extraction, controls, and metric reporting against existing evidence only. |
| Visual lead | Mechanism visualization lead | Builds one schematic/control/boundary figure plan, not decorative diagrams. |
| Skeptical reviewer | Portability critic | Blocks cross-model claims, reportable admission, and extra same-cache feature sweeps. |

## Working Paper

| Field | Draft choice |
| --- | --- |
| Title | H2-Only Response-Cloud Geometry and the Failed Img2img Portability Gate |
| Subtitle | A bounded response-family observable, not a general admitted attack |
| Target type | Response-cloud observable short paper or workshop paper |
| Venue posture | Strong workshop/short-paper candidate now; full CCF-B only after second independent response asset |
| Current artifact | Markdown draft only; no LaTeX fork unless go/no-go passes |

## Abstract

Repeated diffusion queries produce a cloud of outputs rather than a single
distance measurement. This paper asks a narrower question: can the geometry
among repeated H2 responses reveal membership when direct distance baselines
are not the whole story? On the H2 response-strength cache, output-output
features such as within-step repeat distance, timestep centroid movement, and
response-cloud spectra reach AUC `0.961529`, a higher point-estimate AUC on
this frozen H2 cache than the tested raw and lowpass H2 distance diagnostics.
Label-shuffle controls return random-level
behavior, shared-position seed controls preserve the signal, seed `177` remains
strong, and fold-disjoint same-family cache-robustness checks reach mean AUC
`0.959755`. These results make response-cloud geometry operationally separate
from the tested raw/lowpass H2 diagnostics on this frozen packet, without a
best-single-feature or universal feature-family dominance claim. The boundary is
equally important: an SD/CelebA img2img portability check is weaker, has zero
empirical strict-tail recovery over 25 nonmembers, and does not beat simple distance. This img2img result is
a failed validation gate for this packet, not proof that response-cloud
geometry can never be portable. We therefore present output-cloud geometry as a
Research-side H2-family observable with a negative portability result, not as a
broadly portable or downstream-admitted attack. This is a candidate H2
response-family observable; it is not an admitted black-box row, operational
attack, or cross-model portability claim.

## Short-Paper Introduction Draft

Diffusion membership-inference evaluations usually reduce a query to one
distance, score, or likelihood trace. The H2 cache asks a narrower response-side
question: when the same target is queried repeatedly, can the relationships
among returned samples form a membership observable that is not simply the
tested raw or lowpass distance baseline? This paper treats repeated outputs as
a response cloud and evaluates only that frozen H2 response family.

The positive result is intentionally bounded. Output-output geometry separates
members from nonmembers on the H2 response-strength cache and survives the
recorded label-shuffle, shared-position, seed-stability, and same-family
cache-robustness checks. These checks support an H2-family observable. They do
not establish a causal mechanism, cross-model portability, cross-dataset
portability, or consumer-boundary audit evidence.

The negative result is part of the paper's thesis. The SD/CelebA img2img packet
does not validate portability: the output-cloud scorer is weaker than simple
distance and has zero empirical strict-tail recovery over 25 nonmembers, a
finite packet readout rather than calibrated sub-percent risk. A standalone short paper
therefore reports a positive controlled H2 observable together with a failed
img2img portability/admission gate. Hiding that failure would turn the paper
into an overclaim; foregrounding it makes the scientific object precise.

## Controlling Thesis

In one audited H2 repeated-response family, membership signal is recoverable
from relationships among generated responses, not only from the tested direct
query-to-output or seed-to-output similarity baselines. The paper's scientific
unit is the contrast between this positive controlled H2 result and the negative
SD/CelebA img2img portability check. It does not support broad portability,
cross-model portability, cross-dataset portability, or reportable admission.

## Standalone Version Definition

This version is a deliberately narrow observable paper. It should read as:

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
| B-C1: Response-cloud geometry is operationally separate from tested raw/lowpass diagnostics. | H2 feature family excludes direct seed-to-output distance and is compared with raw/lowpass H2 baselines. | Operational distinction only; no causal mechanism, best-single-feature, or universal feature-family dominance claim. |
| B-C2: The H2 signal is strong under bounded controls. | Main AUC `0.961529`, label shuffle `0.507595`, shared-position AUC `0.967819`, seed `177` stability. | One response-contract family; finite empirical tails. |
| B-C3: Same-family cache robustness is strong. | Cache-robustness mean AUC `0.959755`. | Same H2 response family only; not cross-model or cross-dataset portability. |
| B-C4: Portability is negative under the tested img2img gate. | SD/CelebA img2img AUC `0.7888`, strict tail `0.0`, weaker than simple distance. | Blocks full-paper portability and reportable-admission claims. |
| B-C5: The boundary is a contribution, not a weakness to hide. | H2 controls and img2img failure are both in the main argument. | Do not bury negative portability in limitations. |

## Response Contract Box

| Contract field | Frozen value for this draft |
| --- | --- |
| Discovery surface | H2 response-strength cache with repeated responses. |
| Observable | Output-output geometry: repeat distances, timestep centroid movement, and response-cloud spectral summaries. |
| Explicit exclusions | No direct seed-to-output distance and no input-to-output fusion in the claimed H2 observable. |
| Scorer | Logistic readout over frozen feature families; report as a packet-level diagnostic, not a causal mechanism. |
| Controls | Label shuffle, shared-position seed-offset control, seed `177` stability, and fold-disjoint same-family cache-robustness checks. |
| Failed validation gate | Fixed SD/CelebA img2img portability packet: output-cloud AUC `0.7888`, zero empirical strict-tail recovery over 25 nonmembers, below simple-distance AUC `0.8768`. |
| Promotion condition | A second independent response asset must pass the canonical six gates: target identity, split semantics, score/response coverage, metric provenance/provenance replay, consumer boundary, and non-adjacent response-surface delta. |

## Manuscript Spine

| Section | Draft content |
| --- | --- |
| Introduction | State the narrow question: whether repeated H2 responses separate through geometry. |
| Observable | Define output-cloud geometry and contrast it with direct image distance, seed-distance, and response consistency. |
| Bounded Scorer | Describe only frozen feature families: within-timestep repeat RMSE, timestep centroid movement, Gram/PCA spectral summaries, and logistic metric reporting. |
| H2 Positive Result | Compare output-cloud features with raw H2 and lowpass baselines inside H2 only. |
| Controls | Present label shuffle, shared-position seed-offset control, seed `177` stability, and fold-disjoint same-family cache-robustness checks. |
| Boundary Result | Put SD/CelebA img2img failure in the main text as the portability result. |
| Promotion Test | State what a second response asset must prove before full-paper or admitted claims. |
| Limitations | Single-family H2 evidence, finite tails, engineered features, no cross-model portability, no reportable admission. |

## Central Results: H2 Signal and Img2img Boundary

The short paper should expose both the positive H2 result and the failed
portability gate as main-result tables, not as appendix material.
Table 1 is the within-family result: it compares the frozen output-cloud packet
with the tested raw/lowpass H2 diagnostics and controls. Table 2 is the
promotion gate: it reports the SD/CelebA img2img packet that blocks portability
and candidate-to-admitted framing.

| H2 packet | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | Paper role |
| --- | ---: | ---: | ---: | ---: | --- |
| Output-cloud `512/512` | `0.961529` | `0.900391` | `0.333984` | `0.117188` | Candidate observable |
| Raw H2 logistic | `0.905693` | `0.841797` | `0.134766` | `0.000000` | Tested baseline |
| Lowpass H2 logistic | `0.895679` | `0.831055` | `0.148438` | `0.025391` | Tested baseline |
| Label shuffle | `0.507595` | `0.521484` | `0.011719` | `0.003906` | Sanity check |
| Shared-position seed `176` | `0.967819` | `0.923828` | `0.410156` | `0.132812` | Order control |
| Shared-position seed `177` | `0.956192` | `0.896484` | `0.285156` | `0.109375` | Seed stability |
| Cache robustness `176 -> 177` | `0.948990` | `0.884766` | `0.375000` | `0.058594` | Same-family robustness |
| Cache robustness `177 -> 176` | `0.970520` | `0.935547` | `0.390625` | `0.074219` | Same-family robustness |

| Portability packet | Output-cloud AUC | Best simple-distance AUC | Strict-tail result | Boundary decision |
| --- | ---: | ---: | --- | --- |
| SD/CelebA img2img fixed `25/25` boundary packet | `0.7888` | `0.8768` | `0.0` at `n0=25` | Failed portability/admission gate |

The text immediately below these tables must say that logistic output-cloud
scoring is a packet-level diagnostic. It does not prove a causal mechanism, and
without a second independent response asset it cannot become a downstream-admitted
attack, admitted black-box row, cross-model portability claim, or cross-dataset
portability result.
The smaller SD/CelebA img2img diagnostic `10/10` row (`0.9600` output-cloud
AUC versus `0.9900` simple-distance AUC) is recorded only as a diagnostic and is
excluded from the main portability gate.
All tail metrics in these tables are finite empirical packet readouts. H2
intervals are recorded aggregate candidate-side intervals and do not change the
admission state.

Reader-facing result paragraph: the H2 response-strength cache supports a
candidate response-cloud observable because the output-output scorer is
operationally separate from and higher-AUC than the tested raw and lowpass H2
diagnostics on this frozen packet, without a best-single-feature or universal
feature-family dominance claim. It collapses under label shuffle. The same-family cache rows show robustness only inside the H2 response
family. The SD/CelebA img2img rows are the failed validation gate, so this
version cannot claim a general diffusion attack, admitted black-box row,
cross-model portability, cross-dataset portability, or downstream-admitted evidence.

## Section-Level Draft Skeleton

| Section | Claim to make | Required evidence | Text boundary |
| --- | --- | --- | --- |
| 1. Introduction | Repeated responses can be treated as a response cloud, and one H2 cloud carries membership signal. | H2 main result and controls. | Say "can in this audited family," not "generally does." |
| 2. Response-Cloud Observable | Output-output features are operationally different from direct input/output distance. | Feature definitions and exclusion of direct seed-to-output distance. | Do not claim causal mechanism or universal geometry. |
| 3. H2 Positive Result | The H2 response-strength cache has strong separability. | AUC `0.961529`, TPR tails, raw/lowpass baseline comparison. | Report finite packet denominators; avoid calibrated sub-percent risk language. |
| 4. Controls | The signal survives same-family controls and fails label shuffle. | Label shuffle `0.507595`, shared-position `0.967819`, seed and cache-robustness rows. | Same-family robustness only. |
| 5. Boundary Result | SD/CelebA img2img does not validate portability. | AUC `0.7888`, zero empirical strict-tail recovery over 25 nonmembers, negative delta vs distance. | Make this a main result, not a footnote. |
| 6. Promotion Test | A second response asset is required for full-paper or reportable-admission claims. | Six-gate contract. | No candidate-to-admitted language. |

## Reader Contract: Why This Is Not a General Attack

This version must include a compact boundary paragraph after the H2 result
table. The paragraph should state that the evidence comes from one H2
response-contract family, uses an engineered logistic scorer, has no second
independent response asset, is not admitted to the reportable audit bundle, and
has a negative SD/CelebA img2img portability boundary. If a best-single-feature
or feature-family ablation is not already available in the evidence bank, the
paper should avoid claiming that the fused feature family is intrinsically
better than every simpler H2 feature; the supported claim is separation from
the tested raw and lowpass H2 distance baselines.

## Figure and Table Plan

| Asset | Purpose |
| --- | --- |
| Response-cloud schematic | [`direction-b-response-cloud-schematic.svg`](direction-b-response-cloud-schematic.svg) shows repeated responses as the analyzable object, the output-output feature path, and the failed img2img portability/admission boundary. |
| Feature-family table | Makes the frozen scorer understandable and limits hidden feature-sweep suspicion. |
| H2/control table | Compares output-cloud, raw H2, lowpass H2, label shuffle, seed policy, seed `177`, and same-family cache robustness. |
| Portability boundary panel | Contrasts H2 success with SD/CelebA img2img weakness. |
| Claim-boundary table | Prevents "H2-family observable" from reading as "new admitted black-box row." |

## Allowed Wording

| Allowed | Evidence | Prohibited |
| --- | --- | --- |
| "strong Research-side H2-family observable" | H2 main, controls, and same-family cache-robustness rows | "general diffusion membership attack" |
| "same-family cache robustness" | seed `176 -> 177` and `177 -> 176` cache-robustness checks | "cross-model portability" or "cross-dataset portability" |
| "portability boundary" | SD/CelebA img2img weakness and zero empirical strict-tail recovery over 25 nonmembers | "downstream-admitted attack" or "admitted black-box row" |
| "negative img2img portability result" | AUC `0.7888`, zero empirical strict-tail recovery over 25 nonmembers, weaker than simple distance | "portability admission" |

## Team Work Order

| Team member | Next useful action | Explicit non-action |
| --- | --- | --- |
| Observable lead | Write introduction and thesis around "observable plus boundary" rather than "new attack." | Do not sell H2 as general diffusion evidence. |
| Scorer engineer | Freeze feature-family description and ensure every number maps to an existing metric artifact. | Do not run more H2 sweeps for symmetry. |
| Visual lead | Maintain the response-cloud schematic plus one combined H2/control/boundary panel from existing metrics. | Do not create diagrams that hide the single-family boundary. |
| Skeptical reviewer | Check every sentence for cross-model, cross-dataset, or reportable-admission leakage. | Do not request new experiments unless they change standalone viability. |

## Review Risks and Fixes

| Risk | Fix |
| --- | --- |
| Reviewers read it as overfit feature engineering. | Freeze feature families, report controls, and do not add same-cache sweeps. |
| Same-family cache robustness is mistaken for cross-model portability. | Call it H2 response-family robustness only. |
| "Mechanism" sounds causal. | Use "observable" or "mechanism candidate" unless a second asset proves portability. |
| img2img result is read as a failed attack. | Make it the boundary result that defines honest scope. |
| Short paper looks too narrow. | Claim the narrowness explicitly: a positive controlled result plus a negative portability gate. |

## Go / No-Go

| Decision | Condition |
| --- | --- |
| Keep as short-paper draft | Current evidence supports a bounded H2 response-cloud observable case study with a negative portability result. |
| Fork LaTeX as standalone short paper | Later decision only; allowed after an explicit go/no-go if scoped as H2 response-family observable plus img2img boundary, with no candidate-to-admitted language. |
| Promote to full paper | Requires second independent response asset passing fixed target identity, exact split, row-level response/score coverage, metric provenance, hashable provenance/replay, and real surface delta. |
| Promote to reportable/runtime evidence | No-go; H2 output-cloud remains Research-side candidate-only. |
| Refuse more work | Do not fork for more H2 feature sweeps, 512/512 symmetry reruns, repeat-count tuning, KDE/shadow variants, or input-distance fusion. |
