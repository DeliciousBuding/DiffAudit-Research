# Version C: Selected-Corpus Artifact Claim-Support Measurement

## Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Measurement lead | Claim-support lead | Define inclusion rules, claim-support levels, and standalone gate language. |
| Artifact engineer | Provenance audit lead | Separate L0 metadata discovery, L1 artifact inspection, L2 scoreable/replayed packets, and L3 admitted rows. |
| Table/figure lead | Corpus visualization lead | Build stratified gate heatmap, artifact funnel, and signal-vs-completeness plot. |
| Cherry-pick auditor | Selection-bias critic | Ensure corpus selection is frozen before conclusions and counts are not prevalence claims. |

## Target Paper

| Field | Choice |
| --- | --- |
| Working title | From Artifact Surfaces to Audit Claims: A Selected-Corpus Measurement of Diffusion MIA Claim Support |
| Paper type | Selected-corpus artifact claim-support measurement paper |
| Venue posture | SaTML, MLSys, FAccT methods, or reproducibility venue only if L0 metadata, L1 inspection, L2 scoreable/replay, and L3 admitted-control rows are reported as separate strata |
| Current status | v0/v1 corpus, 2026-05-26 fixed-search batch, 2026-05-27 HF/Zenodo/OpenReview broader-source API pass, three-row targeted artifact-link pass, selected-corpus gate-label consistency pass, and bounded second-pass label review exist; plausible second manuscript only under selected-corpus claim-support language, not field-wide prevalence or independent inter-rater language |

## Abstract Draft

In a frozen selected corpus of DiffAudit evidence notes, a 2026-05-26
GitHub/arXiv fixed-search metadata batch, and a 2026-05-27 no-download
HF/Zenodo/OpenReview API pass, we measure the strongest claim each
diffusion MIA artifact surface can support under an audit-consumer contract. The
unit is not paper success or field prevalence; it is a coded artifact surface at
one of four support levels: L0 metadata discovery, L1 artifact inspection, L2
scoreable or replayed packet measurement, and L3 admitted audit evidence.
Metadata-only rows can support discovery and inspection claims; scoreable or
replayed rows can support bounded research-side measurements; admitted controls
can support consumer-boundary audit claims only when target identity, split
semantics, row-bound score or response coverage, metric provenance,
consumer-boundary fit, and surface delta are explicit. We report positive
feature packets, weak bounded scouts, source-confounded separately supplied
packets, metadata-only public surfaces, and internal admitted controls as
separate strata, and we do not pool them into a reproducibility denominator.

## Core Thesis

The scientific object is the maximum defensible claim level for each coded
artifact surface, not whether a paper is "good" or "bad." Direction C asks what
can be discovered, inspected, measured, admitted, or consumed from the released
surface that is actually present. Weak scouts exclude a tested route inside a
specified contract; they do not disprove the original paper or adjacent
unreleased implementations. Positive feature packets can be scientifically
useful while still failing the consumer boundary needed for L3 admission.

## Research Questions

| RQ | Question | Allowed answer form |
| --- | --- | --- |
| RQ1 | What is the highest claim-support level reached by each selected artifact surface? | L0/L1/L2/L3 coding with explicit gates. |
| RQ2 | Which gates most often block promotion from inspection or scoreability to audit admission inside this corpus? | Stratified selected-corpus counts only. |
| RQ3 | How do positive packets, weak scouts, and source-confounded packets differ as evidence? | Case-study boundaries tied to row-level evidence. |
| RQ4 | What should future diffusion MIA artifacts release to make audit claims reusable? | Prescriptive checklist, not a ranking of existing papers. |

## Claim-Support Levels

| Level | Entry condition | Supported claim | Not supported |
| --- | --- | --- | --- |
| L0: Metadata discovery | Search result, paper/repo URL, empty result, duplicate hit, or query-noise row under frozen rules. | A public surface was found, absent, partial, duplicate, or noisy under the declared search process. | Reproduction, replayability, scoreability, auditability, or artifact-quality prevalence. |
| L1: Artifact inspection | Code, manifest, hashes, release tree, documented split, or artifact structure can be inspected without row-bound scores/responses. | The surface exposes clues about target identity, split semantics, coverage, or release completeness. | Metric or replay claims unless score, response, feature, or bounded local rows exist. |
| L2: Scoreable/replayed packet | Existing score rows, response cache, feature tensor, metric JSON, or bounded local packet has row-level meaning. | Finite research-side measurements and route decisions inside the tested contract. | Downstream audit admission without consumer-boundary and surface-delta checks. |
| L3: Consumer-admitted evidence | Row-bound evidence, metrics, provenance, consumer boundary, and surface delta jointly pass admission. | An admitted audit claim under the explicit DiffAudit consumer contract. | Generalization beyond the admitted contract or calibrated continuous low-FPR risk outside the finite packet. |

## Denominator Contract

| Evidence set | May be counted as | Must not be counted as |
| --- | --- | --- |
| 21-row v1 evidence-note corpus | Selected-corpus gate matrix and stratum-separated evidence-note rows. | Field-wide diffusion MIA artifact prevalence. |
| 17-row 2026-05-26 fixed-search batch | Frozen metadata/search observations, including duplicates, empty results, query noise, and metadata-only hits. | Replay, reproduction, scoreability, or auditability denominator. |
| 10-row 2026-05-27 broader-source API pass | Metadata-screening/query hygiene over HF/Zenodo/OpenReview API observations, including zero-result, untitled, and duplicate titled hits. | Artifact inspection, replay, prevalence, or standalone corpus-breadth proof. |
| 3-row 2026-05-27 targeted artifact-link pass | L1 artifact-inspection seeds showing that three metadata-only rows have public artifact surfaces: one HF dataset, one official SecMI GitHub implementation/split tree, and one official MIDM code/protocol repository. | Score/metric replay, admitted evidence, or a new denominator to pool with `21`, `17`, or `10`. |
| Generated L0-L3 claim-support summary | Selected corpus counts `8/3/9/1`; no-download fixed-search counts `13/4/0/0`. | Pooled reproducibility, replayability, auditability, or field-prevalence rate. |
| L2 scoreable/replayed rows | Bounded packet measurements with row-level meaning. | L3 admitted evidence unless consumer-boundary and surface-delta gates pass. |
| L3 admitted controls | Consumer-admitted controls under the current DiffAudit admission boundary. | Evidence that all scoreable packets are consumer-admitted. |
| Selected-corpus consistency and second-pass review | Internal label coherence, contradiction checks, and bounded same-team second-pass review/resolution. | Independent human inter-rater reliability or external validation. |

All figures and tables must keep these denominators separate. The v1 corpus and
fixed-search batch may be shown side by side, but any pooled "reproducibility
rate" across metadata-only and replay rows is invalid.

Numerical shorthand is also controlled. Do not write `1/48 consumer-admitted`, `9/21
reproducible`, `0/17 reproducible`, `10-row broader corpus expansion`, or
`inter-rater reliability`. The safe framing is claim-support levels in selected,
non-poolable sets.

## Main Claims

| Claim | Evidence | Boundary |
| --- | --- | --- |
| C1: Artifact availability, inspectability, scoreability, replayability, auditability, and consumer-boundary reporting are distinct claim levels in the selected corpus. | v1 corpus, fixed-search batch, gate-summary assets, consistency pass, and second-pass review/resolution | Selected-corpus taxonomy only; not a field-wide prevalence claim. |
| C2: Metadata-only fixed-search rows must not be pooled with replay rows. | 17-row 2026-05-26 fixed-search batch with zero evidence+metric-pass rows versus v1 evidence-note rows | Metadata rows support discovery/surface-inspection claims, not reproduction or auditability rates. |
| C2b: Broader-source API rows record no-download metadata-screening/query outcomes without adding audit evidence. | 10-row 2026-05-27 HF/Zenodo/OpenReview metadata-screening pass with zero new distinct artifact surfaces and zero admitted rows | Query-hygiene evidence only; not source-completeness, field-wide prevalence, artifact inspection, replayability, or reliability evidence. |
| C3: Positive feature packets can still be non-admitted. | Tracing Roots AUC `0.815826` | Feature-packet evidence only; no promotion to raw image/checkpoint audit evidence. |
| C4: Weak bounded scouts are useful route exclusions. | ReDiffuse `0.4996/0.5053`, CommonCanvas `0.5148`, MIDST `0.598079` | Excludes tested routes only; does not disprove original methods or unreleased settings. |
| C5: Source confounding must be audited before membership claims. | SD ReDiffuse AUC `0.710319`, source-only AUC `1.0` | Cross-source stress test, not same-distribution MIA. |
| C6: A consistency and bounded second-pass review can support label hygiene but not reliability claims. | The consistency pass found no invalid gate values or route-changing contradictions; the bounded second-pass review found no fixed-search admitted-like row or metadata-batch evidence/metric promotion; two adopted label tightenings | Same-team bounded review only; not independent human inter-rater reliability. |

## Section Spine

| Section | Job |
| --- | --- |
| Introduction | Explain why artifact availability is not the same as scientific reuse or consumer-boundary audit evidence. |
| Selected-Corpus Protocol | Freeze inclusion criteria, covered sources, exclusions, no-download policy, and unit of analysis before reporting outcomes. |
| Claim-Support Levels and Six Gates | Define L0-L3 support levels before interpreting pass/partial/fail gates for target identity, split, score/response coverage, metric provenance, consumer boundary, and surface delta. |
| Stratified Results | Report coded rows by stratum: L0 metadata-only, L1 artifact-inspectable, L2 scoreable/replayed, source-confounded, feature-packet, and L3 admitted-control. |
| Boundary Examples | Use Tracing Roots, ReDiffuse, CommonCanvas, MIDST, CopyMark, H2, and separately supplied SD ReDiffuse to show different claim boundaries. |
| Lessons | State what future diffusion MIA artifacts should release for row-bound, finite-tail, consumer-boundary evidence. |
| Threats | Address selected-corpus bias, same-team labels, local environment bias, metadata-only limits, and partial artifacts. |

## Minimum Next Work

| Work | Why it matters |
| --- | --- |
| Use the completed selected-corpus consistency pass and bounded same-team second-pass review/resolution as label-hygiene evidence. | Prevents gate contradictions, but must not be described as independent reliability. |
| Write all results with stratified denominators and L0-L3 labels. | Prevents metadata-only rows from becoming false reproduction or replay rates. |
| Use the completed broader-source API pass only as metadata-screening/query hygiene; use the targeted artifact-link pass only as non-pooled L1 seeds; add a larger distinct-surface corpus if targeting stronger standalone aggregate claims, and add an external reviewer protocol only for reliability claims. | Prevents selected-corpus claims from becoming source-completeness, field-wide prevalence, or inter-rater claims. |
| Add checksums/URLs only where already recorded or easily verified. | Keeps the paper reproducible without downloading large assets. |
| Add a result-reporting paragraph before any table. | Forces readers to see that the empirical claim is claim-support measurement, not a survey of all diffusion MIA papers. |

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
| Go as scoped standalone measurement note | Allowed if the title, abstract, methods, results, and figures explicitly say selected corpus, use L0-L3 labels, and never report a pooled reproducibility rate. |
| Go as CCF-B-style standalone paper | Requires a larger distinct-surface frozen corpus with new artifact surfaces; add an external label audit protocol if making reliability claims. Metadata/replay/admitted separation must stay unchanged, and reliability language requires a multi-reviewer design. |
| No-go | Any version that ranks papers by failure, claims field-wide prevalence, treats weak scouts as disproof, treats consistency/second-pass review as inter-rater reliability, or pools metadata-only rows with replay rows. |

## Decision

The v1 corpus, fixed-search rows, and broader-source API observations now have a
selected-corpus consistency review plus bounded same-team second-pass review/resolution around
the search batches that affect claim promotion. The consistency pass found no
invalid gate values or route-changing contradictions; the bounded second-pass
review found no fixed-search admitted-like row or metadata-batch evidence/metric
promotion. The second pass adopted two extra label tightenings and recorded a non-adopted
mixed-replay admitted-bundle caveat. Direction C is viable as a selected-corpus
claim-support measurement package. Its boundary is precise: it can claim that
selected artifact surfaces occupy different L0-L3 support states under a frozen
protocol. It cannot claim field-wide artifact prevalence, general
reproducibility rates, independent inter-rater reliability, or disproof of
original papers from weak bounded scouts.
