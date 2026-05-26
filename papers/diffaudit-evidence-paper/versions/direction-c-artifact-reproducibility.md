# Version C: Selected-Corpus Artifact Claim Support

## Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Measurement lead | Claim-support lead | Define inclusion rules, claim-support levels, and standalone gate language. |
| Artifact engineer | Provenance audit lead | Separate metadata-only rows from scoreable, replayed, and admitted rows. |
| Table/figure lead | Corpus visualization lead | Build stratified gate heatmap, artifact funnel, and signal-vs-completeness plot. |
| Cherry-pick auditor | Selection-bias critic | Ensure corpus selection is frozen before conclusions and counts are not prevalence claims. |

## Target Paper

| Field | Choice |
| --- | --- |
| Working title | From Artifact Surfaces to Audit Claims: A Selected-Corpus Measurement of Diffusion MIA Claim Support |
| Paper type | Selected-corpus artifact claim-support measurement paper |
| Venue posture | SaTML, MLSys, FAccT methods, or reproducibility venue only if metadata-only, scoreable/replay, and admitted-control rows are reported as separate strata |
| Current status | v0/v1 corpus, 2026-05-26 fixed-search batch, and selected-corpus gate-label consistency pass exist; plausible second manuscript only under selected-corpus claim-support language |

## Abstract Draft

In a frozen selected corpus of DiffAudit evidence notes and a small fixed
GitHub/arXiv metadata search, we measure what claims each diffusion MIA artifact
surface can support. The unit is not paper success or failure; it is the
artifact-surface claim level. Metadata-only rows can support inspection claims,
scoreable or replayed rows can support bounded research-side measurements, and
admitted controls can support consumer-safe audit claims only when target
identity, split semantics, score or response coverage, metric provenance,
consumer-boundary fit, and surface delta are all explicit. The corpus contains
positive feature packets, weak bounded scouts, source-confounded
collaborator/local packets, metadata-only public surfaces, and internal admitted
controls. We report these strata separately and do not treat selected-corpus
counts as field-wide prevalence or reproducibility rates.

## Core Thesis

The scientific object is not whether public artifacts are "good" or "bad." The
object is the strongest defensible claim level for each coded artifact surface:
metadata inspection, artifact inspection, bounded score/replay, audit-ready
evidence, or consumer-safe reporting. Weak scouts exclude a route inside the
tested contract; they do not disprove the original paper.

## Claim-Support Levels

| Level | Supported claim | Not supported |
| --- | --- | --- |
| L0: Metadata-only | A public surface was found or not found under the frozen search/query rules. | Reproduction, scoreability, auditability, or field-wide artifact quality. |
| L1: Artifact-inspectable | Code, manifests, hashes, or release structure can be inspected for target/split/coverage clues. | Row-bound metric claims unless score or response rows are present. |
| L2: Scoreable or replayed | Existing score, response, feature, or bounded local packets support finite research-side measurements. | Consumer-safe audit admission without boundary and surface-delta checks. |
| L3: Audit-ready/admitted | Row-bound evidence, metrics, provenance, and consumer boundary jointly support an admitted audit claim. | Generalization beyond the admitted contract or calibrated continuous low-FPR risk. |

## Main Claims

| Claim | Evidence | Boundary |
| --- | --- | --- |
| C1: Artifact availability, scoreability, replayability, auditability, and consumer-safe reporting are distinct claim levels in the selected corpus. | v1 corpus, fixed-search batch, gate-summary assets, and consistency pass | Selected-corpus taxonomy only; not a field-wide prevalence claim. |
| C2: Metadata-only rows must not be pooled with replay rows. | 17-row 2026-05-26 fixed-search batch versus v1 evidence-note rows | Metadata rows support surface-inspection claims, not reproduction or auditability rates. |
| C3: Positive feature packets can still be non-admitted. | Tracing Roots AUC `0.815826` | Feature packet lacks raw image/checkpoint consumer surface. |
| C4: Weak bounded scouts are useful exclusions. | ReDiffuse `0.4996/0.5053`, CommonCanvas `0.5148`, MIDST `0.598079` | Excludes tested routes only; does not disprove original methods. |
| C5: Source confounding must be audited before membership claims. | SD ReDiffuse AUC `0.710319`, source-only AUC `1.0` | Cross-source stress test, not same-distribution MIA. |

## Section Spine

| Section | Job |
| --- | --- |
| Introduction | Explain why artifact availability is not the same as scientific reuse or consumer-safe audit evidence. |
| Selected-Corpus Protocol | Freeze inclusion criteria, covered sources, exclusions, and unit of analysis before reporting outcomes. |
| Claim-Support Levels and Six Gates | Define L0-L3 support levels and pass/partial/fail gates for target identity, split, score/response coverage, metric provenance, consumer boundary, and surface delta. |
| Stratified Results | Report coded rows by stratum: metadata-only, artifact-inspectable, scoreable/replayed, source-confounded, feature-packet, and admitted-control. |
| Case Studies | Use Tracing Roots, ReDiffuse, CommonCanvas, MIDST, CopyMark, H2, and collaborator SD ReDiffuse to show different claim boundaries. |
| Lessons | State what future diffusion MIA artifacts should release for row-bound, finite-tail, consumer-safe evidence. |
| Threats | Address selected-corpus bias, same-team labels, local environment bias, metadata-only limits, and partial artifacts. |

## Minimum Next Work

| Work | Why it matters |
| --- | --- |
| Use the completed selected-corpus consistency pass as the current gate matrix. | Prevents one-reviewer labels from being silently treated as unreviewed aggregate evidence. |
| Write all results with stratified denominators. | Prevents metadata-only rows from becoming false reproduction or replay rates. |
| Add one broader fixed-source pass or a second reviewer only if targeting standalone aggregate claims. | Prevents selected-corpus claims from becoming field-wide prevalence claims or inter-rater claims. |
| Add checksums/URLs only where already recorded or easily verified. | Keeps the paper reproducible without downloading large assets. |

## Refused Work

| Refused | Reason |
| --- | --- |
| Ranking papers by "failure" | Scientifically hostile and inaccurate. |
| Full dataset/model downloads | The paper is about artifact surface, not recreating every experiment. |
| Broad claims about all diffusion MIA papers | Current corpus is not yet broad enough. |
| Pooling metadata-only and replay rows | It would turn claim-support measurement into a false reproducibility denominator. |

## Go / No-Go

| Decision | Gate |
| --- | --- |
| Go as Direction A companion section | Current selected-corpus gate matrix and fixed-search metadata batch are enough if all counts stay stratified. |
| Go as scoped standalone measurement note | Allowed if the title, abstract, and results explicitly say selected corpus and never report a pooled reproducibility rate. |
| Go as CCF-B-style standalone paper | Requires either a broader frozen source pass or a second independent label review, plus unchanged metadata/replay/admitted separation. |
| No-go | Any version that ranks papers by failure, claims field-wide prevalence, treats weak scouts as disproof, or pools metadata-only rows with replay rows. |

## Decision

The v1 corpus and fixed-search rows now pass a selected-corpus consistency
review with no invalid gate values, evidence/metric contradictions, or label
promotions; four empty-result `delta_gate` labels were demoted from `Partial` to
`Fail`. Direction C is viable as a selected-corpus claim-support measurement
package. It is not yet a field-wide artifact-reproducibility survey, and it
should not fork a LaTeX manuscript unless the scoped measurement posture remains
intact or broader/second-review evidence is added.
