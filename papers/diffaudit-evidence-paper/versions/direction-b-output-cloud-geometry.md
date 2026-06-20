# Version B: H2-Only Response-Cloud Geometry and Failed Portability Boundary

## Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Observable lead | Response geometry lead | Define the response-cloud observable and keep the H2 boundary explicit. |
| Scorer engineer | Control implementation lead | Freeze the bounded scorer description and map every metric to existing evidence only. |
| Visual explanation lead | Observable visualization lead | Build one geometry/control/portability-boundary figure plan from existing metrics. |
| Skeptical reviewer | Portability critic | Block cross-model wording, reportable admission, field-wide claims, and same-cache feature-sweep inflation. |

## Short-Paper Package

| Field | Choice |
| --- | --- |
| Working title | H2-Only Response-Cloud Geometry and the Failed Img2img Portability Gate |
| One-line hook | A controlled H2 response cloud carries a membership-separating output-output geometry signal; the same observable fails this fixed img2img portability gate. |
| Paper type | Response-cloud observable short/workshop paper |
| Venue posture | Markdown short-paper package now; standalone TeX fork only after an explicit go/no-go decision, and full CCF-B response-observable paper only with a second independent response asset |
| Current status | Candidate paper, not active main manuscript |

## Difference From Direction A

Direction A is an evidence-contract paper: its main question is when a score
can become reusable audit evidence. Direction B is not another contract paper.
Its main question is narrower and more mechanistic: what kind of information is
present in repeated responses, and where does that information stop carrying
across response contracts?

| Axis | Direction A main paper | Direction B short paper |
| --- | --- | --- |
| Central object | Admission contract for reusable audit rows | Response-cloud geometry as a bounded H2-family observable |
| Main evidence move | Report five role-separated rows with replay/source tier attached and explain why candidates stay out | Show one strong H2-family observable and one negative portability gate |
| Role of H2 | Candidate negative control inside a broader framework | Main subject of the paper |
| Role of SD/CelebA img2img | Boundary evidence for non-admission | Central negative result that defines scope |
| Success condition | Reviewer accepts evidence-contract methodology | Reviewer accepts a narrow response-cloud observable study with honest portability limits |
| Forbidden drift | Governance-only paper | General diffusion attack, product row, or field-wide portability claim |

## Abstract Draft

Repeated diffusion queries produce a cloud of responses, not just a single
image-to-image distance. This short paper asks whether geometry inside that
response cloud can act as a membership observable, and whether the observable
survives beyond the response contract where it is discovered. On the H2
response-strength cache, output-output features such as within-step repeat
distance, timestep centroid movement, and response-cloud Gram spectra reach
AUC `0.961529`, a higher point-estimate AUC on this frozen H2 cache than the
tested raw and lowpass H2 distance diagnostics. Label-shuffle controls return random-level behavior,
shared-position seed-offset controls preserve the signal, seed `177` remains
strong, and fold-disjoint same-family cache-robustness checks reach mean AUC
`0.959755`. These controls make the H2 signal hard to dismiss as a trivial
label leak, class-ordered seed artifact, or single-seed accident inside this
response family. The portability test is the central counter-result: on the
SD/CelebA img2img portability packet, the same output-output geometry reaches
only AUC `0.7888`, has zero strict-tail recovery (`n0=25`), and is weaker than the
simple input-output distance comparator. This img2img result is a failed
validation gate for this packet, not proof that response-cloud geometry can
never be portable. We therefore present response-cloud
geometry as a controlled H2-family observable whose negative portability
boundary is part of the result, not as a broadly portable or downstream-admitted
diffusion membership attack. This is a candidate H2 response-family observable;
it is not an admitted black-box row, operational attack, or cross-model portability
claim.

## Controlling Question

Can repeated responses expose membership through geometry among outputs, and
does that geometry survive when moved from the H2 response-strength contract to
an SD/CelebA img2img contract?

The answer is intentionally two-sided:

| Part | Answer | Consequence |
| --- | --- | --- |
| H2 response family | Yes, strongly under bounded controls. | Worth writing as a response-cloud observable short paper. |
| SD/CelebA img2img portability | No, not under the current packet; strict-tail recovery is zero (`n0=25`) and simple distance is stronger. | Blocks full-paper portability, admitted black-box, and product claims. |

## Response Contract Box

| Contract field | Frozen value for this draft |
| --- | --- |
| Discovery surface | H2 response-strength cache with repeated responses. |
| Observable | Output-output geometry: repeat distances, timestep centroid movement, and response-cloud Gram/PCA spectra. |
| Explicit exclusions | No direct seed-to-output distance and no input-to-output fusion in the claimed H2 observable. |
| Scorer | Logistic readout over frozen feature families; report as a packet-level diagnostic, not a causal mechanism. |
| Controls | Label shuffle, shared-position seed-offset control, seed `177` stability, and fold-disjoint same-family cache-robustness checks. |
| Failed validation gate | Fixed SD/CelebA img2img portability packet: output-cloud AUC `0.7888`, zero strict-tail recovery (`n0=25`), below simple-distance AUC `0.8768`. |
| Promotion condition | A second independent response asset must pass target, split, row-level response/score, metric provenance, hashable provenance/replay, consumer boundary, and surface-delta gates. |

## Core Thesis

Membership signal can be recoverable from relationships among repeated
responses inside one audited H2 response family, not only from the tested direct
query-to-output or seed-to-output distance baselines. The scientific unit is
the contrast: a strong controlled H2 response-cloud signal plus a negative
img2img portability boundary. The claim stops there. Current evidence does not
support cross-model portability, cross-dataset portability, reportable admission,
admitted black-box wording, or a new general diffusion membership attack.

## Contribution Claims

| Claim | Evidence | Boundary |
| --- | --- | --- |
| B1: A response-cloud observable exists operationally. | Feature design excludes direct seed-to-output and input-to-output distance and uses output-output geometry: repeat distances, centroid motion, and cloud spectra. | Operational separation only; no causal mechanism or universal geometry claim. |
| B2: The H2 positive result is controlled. | Main AUC `0.961529`, label-shuffle `0.507595`, shared-position AUC `0.967819`, seed `177` stability, shared-position label-shuffle `0.464066`. | One H2 response-contract family; finite empirical tails. |
| B3: Same-family cache robustness is not portability. | Seed `176` -> `177` AUC `0.948990`, seed `177` -> `176` AUC `0.970520`, mean `0.959755`. | Same H2 response family only; not cross-model or cross-dataset portability. |
| B4: Negative portability is a main result. | SD/CelebA img2img portability packet AUC `0.7888`, TPR@1%FPR `0.0`, TPR@0.1%FPR `0.0`, simple distance AUC `0.8768`. | Blocks reportable-admission and full-paper portability claims. |
| B5: The right conclusion is H2-family observable, not attack admission. | H2 controls are strong but the second response surface does not validate the observable. | No Runtime runner, Platform schema, bundle row, or public product copy. |

## Evidence Ledger

| Evidence unit | Metric readout | Interpretation |
| --- | --- | --- |
| H2 response-cloud main cache | AUC `0.961529`, TPR@1%FPR `0.333984`, TPR@0.1%FPR `0.117188` | Strong within-family response-cloud signal. |
| H2 raw / lowpass comparators | Raw AUC `0.905693`, lowpass AUC `0.895679` | Output-cloud logistic has a higher point-estimate AUC on this cache than the tested H2 distance diagnostics. |
| Label shuffle | AUC `0.507595` | No obvious label-through pipeline leak. |
| Shared-position order control | AUC `0.967819`, TPR@0.1%FPR `0.132812` | Class-ordered seed offset is not a sufficient explanation. |
| Shared-position seed `177` | AUC `0.956192`, TPR@0.1%FPR `0.109375` | Controlled signal is not single-seed. |
| Same-family cache robustness | Mean AUC `0.959755`, min TPR@1%FPR `0.375000` | Strong same-family robustness, not portability. |
| SD/CelebA img2img output-cloud portability packet | AUC `0.7888`, TPR@1%FPR `0.0`, TPR@0.1%FPR `0.0` | Negative portability gate. |
| SD/CelebA img2img simple-distance comparator | AUC `0.8768`, empirical 0-FP TPR `0.44` | Simpler input-output distance remains the honest img2img mainline. |

All tail metrics in this direction are finite empirical packet readouts. H2
intervals are recorded aggregate candidate-side intervals and do not change the
admission state.

## Section Spine

| Section | Job |
| --- | --- |
| Introduction | State the observable question and preview the two-sided answer: strong H2, negative img2img portability. |
| Response-Cloud Observable | Define output-output geometry and explicitly separate it from direct input/output distance. |
| Bounded Scorer | Freeze the feature families and logistic reporting without adding new sweeps. |
| H2 Positive Result | Report AUC/tail metrics and distance-baseline comparison inside H2 only. |
| Controls and Same-Family Robustness | Present label shuffle, shared-position seed policy, seed `177`, and same-family cache-robustness checks. |
| Negative Portability Boundary | Put the SD/CelebA img2img weakness in the main argument as a result, not a caveat. |
| Claim Boundary and Promotion Test | Define the second-asset gate required before any full-paper or admitted claim. |

## Figure/Table Spine

| Asset | Purpose |
| --- | --- |
| Response-cloud schematic | Shows repeated responses as the object of measurement, not decorative model art. |
| Feature-family table | Makes the bounded scorer inspectable and limits hidden feature-sweep suspicion. |
| H2/control table | Combines main AUC/tails, label shuffle, seed policy, seed `177`, and same-family cache robustness. |
| Portability-boundary panel | Places SD/CelebA img2img weakness beside H2 success to define scope. |
| Claim-boundary box | States that same-family cache robustness is not cross-model or cross-dataset portability. |

## Go / No-Go

| Decision | Condition |
| --- | --- |
| Go as short/workshop paper | Current H2 positive result, controls, same-family cache robustness, and negative portability boundary are enough if written as a bounded response-cloud observable study. |
| Do not fork as full response-observable paper | No second independent response asset has validated the observable. |
| Promote to full paper | Requires a second response asset with fixed target identity, exact member/nonmember split, row-level response or score coverage, metric provenance, hashable provenance/replay, and a real surface delta over simple distance. |
| Downstream/admitted claim | Not allowed; H2 output-cloud remains Research-side candidate-only. |
| Refuse more H2 polishing experiments | Same-cache feature sweeps, 512/512 symmetry reruns, repeat-count tuning, KDE/shadow variants, and input-distance fusion do not resolve portability. |
| Refuse overclaim language | Do not say downstream-admitted, admitted black-box, field-wide, cross-model, cross-dataset, or broadly portable. |

## Decision

Keep Direction B as the sharpest technical short-paper candidate, separate from
Direction A. Its publishable unit is the honest contrast: strong controlled H2
response-cloud signal plus negative img2img portability. The negative boundary
is not a weakness to hide; it is what prevents the paper from becoming an
unsupported general attack claim. Do not make it the main/full paper, admit it
as black-box evidence, or turn it into product copy until a second independent
response asset validates the observable.
