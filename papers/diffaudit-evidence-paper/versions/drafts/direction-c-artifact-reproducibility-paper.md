# Direction C Draft: Selected-Corpus Artifact Claim Support

## Assigned Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Measurement lead | opus | Defines inclusion protocol, six-gate method, and non-hostile framing. |
| Artifact engineer | haiku | Checks manifests, hashes, row binding, score packets, and metric provenance. |
| Table lead | sonnet | Builds gate heatmap, artifact funnel, and failure taxonomy figures. |
| Cherry-pick auditor | opus | Ensures corpus selection is frozen before outcome claims are written. |

## Working Paper

| Field | Draft choice |
| --- | --- |
| Title | When Diffusion MIA Scores Are Not Audit Evidence: A Selected-Corpus Claim-Support Study |
| Target type | Selected-corpus artifact claim-support measurement paper |
| Venue posture | Measurement, ML systems, or security/privacy methods venue; reproducibility venue only if replay evidence is separated from metadata-only rows |
| Current artifact | Draft plus v0/v1 corpus files and fixed-search batch: [`../direction-c-corpus-protocol.md`](../direction-c-corpus-protocol.md), [`../direction-c-corpus-v1.md`](../direction-c-corpus-v1.md), [`../direction-c-fixed-search-batch-20260526.md`](../direction-c-fixed-search-batch-20260526.md), [`../../data/artifact_corpus_v1.csv`](../../data/artifact_corpus_v1.csv), and [`../../data/artifact_corpus_fixed_search_20260526.csv`](../../data/artifact_corpus_fixed_search_20260526.csv) |

## Abstract

In a frozen selected corpus of DiffAudit evidence notes and a small fixed
GitHub/arXiv metadata search, we study which claims each diffusion MIA artifact
surface can support. Artifact availability is not the same as auditability, and
metadata-only evidence is not the same as reproduction. We code each row through
six gates: target identity, split semantics, score or response coverage, metric
provenance, consumer boundary, and surface delta. The selected corpus contains
several distinct outcomes: positive but non-admitted feature packets, scoreable
but weak bounded scouts, source-confounded collaborator/local packets,
metadata-only public surfaces, and internal admitted controls. These are not
failures of the original papers; they are claim-boundary measurements. The
paper's central result is a selected-corpus taxonomy of artifact claim support:
what can be inspected, what can be replayed, what can be scored, what can be
audited, and what can be safely consumed.

## Controlling Thesis

The publishable claim is not "public artifacts fail." The claim is that
reusable diffusion MIA evidence has stricter requirements than artifact
availability or scoreability. A public artifact can support a paper claim, a
research-side replay, or a consumer-safe audit claim, and those are different
scientific objects.

## Standalone Version Definition

This version is a claim-support measurement paper. It should read as:

> We measured what kinds of claims selected diffusion MIA artifacts can support
> under a reusable audit contract.

It should not read as:

> We surveyed the whole field and found that diffusion MIA artifacts fail.

The current corpus supports selected-corpus reasoning only. A standalone paper
can be written now as a scoped measurement note, but any CCF-B-style aggregate
claim needs either a broader frozen source pass or a second independent label
review.

## Selected-Corpus Protocol Required Before Full Claims

| Protocol item | Required decision |
| --- | --- |
| Current search date | Frozen at 2026-05-26 for the fixed GitHub/arXiv metadata batch. |
| Current covered sources | GitHub search and arXiv metadata search only, plus existing DiffAudit evidence notes. |
| Explicitly excluded from the current fixed batch | OpenReview, Hugging Face, Papers with Code, Zenodo, major-venue manual chasing, full artifact downloads, and full upstream replays. |
| Broader standalone sources | arXiv, OpenReview, major venue proceedings, GitHub, Zenodo, Hugging Face, Papers with Code. |
| Keywords | diffusion membership inference; generative model membership inference; diffusion memorization; copyright/data identification diffusion; synthetic data MIA. |
| Metadata only | Record URLs, modality, target type, artifact type, public surface, six-gate labels, and no large downloads. |
| Target size | Add 10-20 papers or artifact surfaces before making aggregate claims. |
| Strata | Separate audit-ready controls, positive-but-non-admitted packets, bounded negatives, source-confounded cases, no/partial-artifact cases, and internal controls. |

## Current Evidence Snapshot

| Evidence item | What it supports | What it does not support |
| --- | --- | --- |
| 21-row v1 corpus | Controlled selected-corpus gate taxonomy and stratum separation. | Field-wide prevalence or venue-wide artifact quality. |
| 17-row fixed-search batch from 2026-05-26 | Independent metadata-only search layer over a frozen query set. | Full reproducibility judgment without downloads or replays. |
| Generated gate-summary CSV/PDF | Counts of pass/partial/fail gate labels inside the selected corpus. | Statistical estimates of public artifact availability. |
| Selected-corpus consistency pass | Internal label coherence; no CSV label changes required. | Independent inter-rater reliability. |

## Contribution Claims

| Claim | Evidence anchor | Boundary |
| --- | --- | --- |
| C-C1: Artifact availability, scoreability, reproducibility, and auditability are distinct. | Six-gate protocol, v1 corpus, and 2026-05-26 fixed-search batch | Supports selected-corpus claims only; no field-wide prevalence claims. |
| C-C2: Positive packets can be scientifically useful but non-admitted. | Tracing Roots AUC `0.815826` | Feature-packet evidence only, not raw image audit evidence. |
| C-C3: Bounded weak scouts are useful exclusions. | ReDiffuse `0.4996/0.5053`, CommonCanvas `0.5148`, MIDST `0.598079` | Does not disprove original methods. |
| C-C4: Source confounding must be audited. | SD ReDiffuse AUC `0.710319`, source-only AUC `1.0` | Cross-source stress test, not same-distribution MIA. |
| C-C5: Consumer-boundary gates can be generalized beyond DiffAudit. | Gate definitions in source/claim maps | Must be written as audit-consumer requirements, not project policy. |

## Manuscript Spine

| Section | Draft content |
| --- | --- |
| Introduction | Distinguish artifact availability, scoreability, reproducibility, and auditability. |
| Selected-Corpus Protocol | Present fixed search window, covered sources, excluded sources, keywords, metadata fields, and exclusion rules before any results. |
| Six-Gate Method | Define pass/partial/fail for target identity, member split, nonmember split, score/response coverage, metric provenance, and consumer-boundary fit. |
| Artifact Strata | Separate public artifacts, collaborator/local packets, internal admitted controls, and internal candidate controls. |
| Results | Report gate matrix and failure taxonomy as coded rows in this corpus; avoid ranking papers by "failure." |
| Case Studies | Split by stratum: public metadata/code surfaces, public score/feature packets, bounded local scouts, collaborator/local packets, and internal controls. |
| Lessons for Authors | State what future artifacts should publish: manifests, hashes, score rows, ROC arrays, metric JSON, finite-tail denominators, boundary language. |
| Threats to Validity | Cherry-picking, local-only evidence, metadata-only inspection limits, DiffAudit-specific consumer boundary, finite tails. |

## Section-Level Draft Skeleton

| Section | Claim to make | Required evidence | Text boundary |
| --- | --- | --- | --- |
| 1. Introduction | Auditability is a stricter object than artifact availability. | Six-gate contract and examples of distinct strata. | Avoid hostile "artifact failure" framing. |
| 2. Corpus Construction | The corpus is frozen and selected by explicit rules. | v1 corpus, fixed-search batch, protocol docs. | State selected-corpus only. |
| 3. Six-Gate Method | Gates define what claim an artifact can support. | target identity, split semantics, score/response coverage, metric provenance, consumer boundary, surface delta. | Gates are audit-consumer requirements, not moral judgments. |
| 4. Gate Results | Selected artifacts occupy multiple support states. | gate-summary CSV/PDF and strata table. | Counts are not prevalence estimates. |
| 5. Case Studies | Positive, weak, and confounded packets reveal different claim boundaries. | Tracing Roots, ReDiffuse, CommonCanvas, MIDST, SD ReDiffuse, H2. | Weak scouts do not disprove original papers. |
| 6. Author Checklist | Future artifacts can make claims reusable by publishing row-bound evidence. | release checklist from Direction A. | Checklist is prescriptive, not a pass/fail ranking of papers. |

## Figure and Table Plan

| Asset | Purpose |
| --- | --- |
| Corpus flow diagram | Shows fixed search, screening, metadata-only extraction, and gate assignment. |
| Six-gate heatmap | Main empirical figure after expansion. |
| Artifact stratum table | Prevents internal controls and public artifacts from being mixed. |
| Signal-vs-completeness scatter | Shows that high or positive scores are not sufficient for auditability. |
| Failure-taxonomy chart | Counts target-identity, split, score, provenance, and boundary gaps. |

## Team Work Order

| Team member | Next useful action | Explicit non-action |
| --- | --- | --- |
| Measurement lead | Write the method as a claim-support audit, with inclusion rules before results. | Do not state field-wide artifact prevalence. |
| Artifact engineer | Keep gate labels tied to existing CSV rows and generated summaries. | Do not download large models or rerun upstream training for narrative symmetry. |
| Table lead | Produce a heatmap and stratum table from existing selected-corpus data. | Do not merge internal controls with public metadata-only rows. |
| Cherry-pick auditor | Decide whether a broader source pass or second label review is needed before standalone submission. | Do not approve standalone aggregate claims from the selected corpus alone. |

## Review Risks and Fixes

| Risk | Fix |
| --- | --- |
| Looks anecdotal or DiffAudit-history-biased. | v1 adds 10 metadata-only surfaces from existing notes; the 2026-05-26 fixed-search batch adds an independent selection layer; the selected-corpus consistency pass made no CSV label changes. |
| Sounds hostile to other papers. | Use claim-support language; do not say papers "fail." |
| Mixes public artifacts with internal controls. | Explicit artifact strata in table and prose. |
| Consumer boundary looks project-specific. | Generalize as audit-consumer requirements and keep DiffAudit as one implementation. |

## Go / No-Go

| Decision | Condition |
| --- | --- |
| Keep as draft | Current v0 supports a structured plan. |
| Promote to standalone paper | Requires one broader source pass or a second independent label review if making aggregate claims beyond this corpus. |
| Fork LaTeX | Allowed only after the selected-corpus gate matrix and failure taxonomy are kept scoped, or after broader/second-review evidence is added. |
| Stop | If expansion remains only existing DiffAudit history; that would be a section in Direction A, not a standalone paper. |
