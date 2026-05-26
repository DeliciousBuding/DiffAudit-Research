# Direction C Draft: Selected-Corpus Artifact Claim Support

## Assigned Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Measurement lead | Claim-support lead | Defines inclusion protocol, claim-support levels, six-gate method, and non-hostile framing. |
| Artifact engineer | Provenance audit lead | Separates metadata-only rows from scoreable, replayed, feature-packet, and admitted rows. |
| Table lead | Corpus visualization lead | Builds stratified gate heatmap, artifact funnel, and claim-support figures. |
| Cherry-pick auditor | Selection-bias critic | Ensures corpus selection is frozen before outcome claims and denominators are written. |

## Working Paper

| Field | Draft choice |
| --- | --- |
| Title | From Artifact Surfaces to Audit Claims: A Selected-Corpus Measurement of Diffusion MIA Claim Support |
| Target type | Selected-corpus artifact claim-support measurement paper |
| Venue posture | Measurement, ML systems, or security/privacy methods venue; reproducibility venue only if metadata-only, scoreable/replay, feature-packet, source-confounded, and admitted-control rows are separated |
| Current artifact | Draft plus v0/v1 corpus files and fixed-search batch: [`../direction-c-corpus-protocol.md`](../direction-c-corpus-protocol.md), [`../direction-c-corpus-v1.md`](../direction-c-corpus-v1.md), [`../direction-c-fixed-search-batch-20260526.md`](../direction-c-fixed-search-batch-20260526.md), [`../../data/artifact_corpus_v1.csv`](../../data/artifact_corpus_v1.csv), and [`../../data/artifact_corpus_fixed_search_20260526.csv`](../../data/artifact_corpus_fixed_search_20260526.csv) |

## Abstract

In a frozen selected corpus of DiffAudit evidence notes and a small fixed
GitHub/arXiv metadata search, we measure what claims each diffusion MIA artifact
surface can support. Artifact availability is not the same as auditability, and
metadata-only evidence is not the same as reproduction. We code each row through
six gates: target identity, split semantics, score or response coverage, metric
provenance, consumer boundary, and surface delta. The selected corpus contains
several distinct strata: metadata-only public surfaces, artifact-inspectable
surfaces, positive but non-admitted feature packets, scoreable but weak bounded
scouts, source-confounded collaborator/local packets, and internal admitted
controls. These are not failures of the original papers; they are
claim-boundary measurements. The paper's central result is a selected-corpus
taxonomy of artifact claim support: what can be inspected, what can be replayed
or scored, what can be audited, and what can be safely consumed. Counts are
reported only within strata and are not field-wide prevalence estimates.

## Controlling Thesis

The publishable claim is not "public artifacts fail." The claim is that
reusable diffusion MIA evidence has stricter claim-support levels than artifact
availability or scoreability. The unit of analysis is an artifact surface under
a frozen inclusion rule, not a paper-quality judgment. A public artifact can
support metadata inspection, artifact inspection, a bounded research-side
replay, or a consumer-safe audit claim, and those are different scientific
objects.

## Standalone Version Definition

This version is a claim-support measurement paper. It should read as:

> We measured what kinds of claims selected diffusion MIA artifacts can support
> under a reusable audit contract.

It should not read as:

> We surveyed the whole field and found that diffusion MIA artifacts fail.

The current corpus supports selected-corpus reasoning only. A standalone paper
can be written now as a scoped measurement note if it reports strata separately:
metadata-only rows, artifact-inspectable rows, scoreable/replayed rows,
source-confounded packets, feature packets, and admitted controls. Any
CCF-B-style aggregate claim needs either a broader frozen source pass or a
second independent label review, and even then it must not pool metadata-only
rows into a reproduction denominator.

## Standalone Claim-Support Gate

| Gate | Required stance before standalone submission |
| --- | --- |
| Unit of analysis | Artifact surface under a frozen inclusion rule, not paper success/failure. |
| Denominators | Report metadata-only, artifact-inspectable, scoreable/replayed, feature-packet, source-confounded, and admitted-control rows separately. |
| Weak scouts | Use as bounded exclusions for tested contracts only; never as disproof of original papers. |
| Positive packets | Treat positive scores as claim support only at the available surface level; do not promote feature packets to raw-image audit evidence. |
| Aggregate language | Selected-corpus taxonomy is allowed; field-wide prevalence, venue-wide quality, and inter-rater reliability require new evidence. |
| Consumer language | Consumer-safe audit claims require target identity, split semantics, row-bound score/response coverage, metric provenance, boundary fit, and surface delta. |

## Selected-Corpus Protocol Required Before Full Claims

| Protocol item | Required decision |
| --- | --- |
| Current search date | Frozen at 2026-05-26 for the fixed GitHub/arXiv metadata batch. |
| Current covered sources | GitHub search and arXiv metadata search only, plus existing DiffAudit evidence notes. |
| Explicitly excluded from the current fixed batch | OpenReview, Hugging Face, Papers with Code, Zenodo, major-venue manual chasing, full artifact downloads, and full upstream replays. |
| Broader standalone sources | arXiv, OpenReview, major venue proceedings, GitHub, Zenodo, Hugging Face, Papers with Code. |
| Keywords | diffusion membership inference; generative model membership inference; diffusion memorization; copyright/data identification diffusion; synthetic data MIA. |
| Metadata-only rows | Record URLs, modality, target type, artifact type, public surface, six-gate labels, and no large downloads; these rows support surface-inspection claims only. |
| Scoreable/replayed rows | Require an existing score packet, response cache, feature tensor, metric JSON, bounded local packet, or replayed metric with row-level meaning. |
| Target size | Add 10-20 papers or artifact surfaces before making aggregate claims. |
| Strata | Separate metadata-only surfaces, artifact-inspectable surfaces, scoreable/replayed packets, positive-but-non-admitted feature packets, bounded negatives, source-confounded cases, and admitted controls. |

## Current Evidence Snapshot

| Evidence item | What it supports | What it does not support |
| --- | --- | --- |
| 21-row v1 corpus | Controlled selected-corpus gate taxonomy and stratum separation. | Field-wide prevalence or venue-wide artifact quality. |
| 17-row fixed-search batch from 2026-05-26 | Independent metadata-only search layer over a frozen query set. | Full reproducibility, replayability, or auditability judgment without downloads or replays. |
| Generated gate-summary CSV/PDF | Counts of pass/partial/fail gate labels inside the selected corpus and within declared strata. | Statistical estimates of public artifact availability or pooled reproducibility rates. |
| Selected-corpus consistency pass | Internal label coherence; no invalid labels, contradictions, or promotions after four empty-result `delta_gate` demotions. | Independent inter-rater reliability. |

## Claim-Support Levels

| Level | Row type | Supported claim | Not supported |
| --- | --- | --- | --- |
| L0 | Metadata-only | A public surface was found, absent, or partial under frozen search rules. | Reproduction, replayability, scoreability, or auditability. |
| L1 | Artifact-inspectable | Code, manifests, release structure, hashes, or documented splits can be inspected. | Metric claims unless score/response/feature rows exist. |
| L2 | Scoreable/replayed | Existing score, response, feature, or bounded local packets support finite research-side measurement. | Consumer-safe admission without boundary and surface-delta gates. |
| L3 | Audit-ready/admitted | Row-bound evidence, metric provenance, and consumer boundary support an admitted audit claim. | Generalization beyond the admitted contract or calibrated continuous low-FPR risk. |

## Contribution Claims

| Claim | Evidence anchor | Boundary |
| --- | --- | --- |
| C-C1: Artifact availability, scoreability, replayability, auditability, and consumer-safe reporting are distinct. | Six-gate protocol, v1 corpus, fixed-search batch, and gate-summary assets | Supports selected-corpus taxonomy only; no field-wide prevalence claims. |
| C-C2: Metadata-only rows must not be pooled with scoreable or replayed rows. | 2026-05-26 fixed-search batch versus v1 evidence-note rows | Metadata rows support surface-inspection claims, not reproduction or replay rates. |
| C-C3: Positive packets can be scientifically useful but non-admitted. | Tracing Roots AUC `0.815826` | Feature-packet evidence only, not raw image audit evidence. |
| C-C4: Bounded weak scouts are useful exclusions. | ReDiffuse `0.4996/0.5053`, CommonCanvas `0.5148`, MIDST `0.598079` | Excludes tested routes only; does not disprove original methods. |
| C-C5: Source confounding must be audited. | SD ReDiffuse AUC `0.710319`, source-only AUC `1.0` | Cross-source stress test, not same-distribution MIA. |
| C-C6: Consumer-boundary gates can be proposed as reusable audit-consumer requirements. | Gate definitions in source/claim maps | Proposal derived from DiffAudit evidence; external validation is needed before a general adoption claim. |

## Manuscript Spine

| Section | Draft content |
| --- | --- |
| Introduction | Distinguish artifact availability, scoreability, replayability, auditability, and consumer-safe reporting. |
| Selected-Corpus Protocol | Present fixed search window, covered sources, excluded sources, keywords, metadata fields, and exclusion rules before any results. |
| Claim-Support Levels and Six-Gate Method | Define L0-L3 claim-support levels and pass/partial/fail gates for target identity, member/nonmember split, score/response coverage, metric provenance, consumer boundary, and surface delta. |
| Artifact Strata | Separate metadata-only surfaces, artifact-inspectable surfaces, public score/feature packets, bounded local scouts, source-confounded collaborator/local packets, internal candidate controls, and internal admitted controls. |
| Results | Report gate matrix and claim-support taxonomy as coded rows in this corpus; avoid ranking papers by "failure" or reporting pooled reproducibility rates. |
| Case Studies | Split by stratum: public metadata surfaces, public score/feature packets, bounded local scouts, collaborator/local packets, and internal controls. |
| Lessons for Authors | State what future artifacts should publish: manifests, hashes, score rows, ROC arrays, metric JSON, finite-tail denominators, boundary language. |
| Threats to Validity | Selected-corpus bias, same-team labels, local-only evidence, metadata-only inspection limits, DiffAudit-specific consumer boundary, finite tails. |

## Section-Level Draft Skeleton

| Section | Claim to make | Required evidence | Text boundary |
| --- | --- | --- | --- |
| 1. Introduction | Auditability is a stricter object than artifact availability or scoreability. | Six-gate contract and examples of distinct strata. | Avoid hostile "artifact failure" framing. |
| 2. Corpus Construction | The corpus is frozen and selected by explicit rules. | v1 corpus, fixed-search batch, protocol docs. | State selected-corpus only. |
| 3. Claim-Support Ladder | L0-L3 levels define what a row can support before gates are interpreted. | metadata-only, artifact-inspectable, scoreable/replayed, and admitted rows. | Do not pool metadata-only rows with replay rows. |
| 4. Six-Gate Method | Gates define what claim an artifact can support within its stratum. | target identity, split semantics, score/response coverage, metric provenance, consumer boundary, surface delta. | Gates are audit-consumer requirements, not moral judgments. |
| 5. Stratified Gate Results | Selected artifacts occupy multiple support states. | gate-summary CSV/PDF and strata table. | Counts are not prevalence estimates or reproducibility rates. |
| 6. Case Studies | Positive, weak, and confounded packets reveal different claim boundaries. | Tracing Roots, ReDiffuse, CommonCanvas, MIDST, SD ReDiffuse, H2. | Weak scouts do not disprove original papers. |
| 7. Author Checklist | Future artifacts can make claims reusable by publishing row-bound evidence. | release checklist from Direction A. | Checklist is prescriptive, not a pass/fail ranking of papers. |

## Figure and Table Plan

| Asset | Purpose |
| --- | --- |
| Corpus flow diagram | Shows fixed search, screening, metadata-only extraction, replay/score packet identification, and gate assignment. |
| Claim-support ladder | Shows L0-L3 support levels before presenting gate results. |
| Six-gate heatmap | Main selected-corpus empirical figure; caption must state that counts are not prevalence estimates or pooled reproducibility rates. |
| Artifact stratum table | Prevents metadata-only rows, public replay/feature packets, source-confounded packets, and internal controls from being mixed. |
| Signal-vs-completeness scatter | Shows that high or positive scores are not sufficient for auditability. |
| Gap-taxonomy chart | Counts target-identity, split, score, provenance, and boundary gaps without ranking papers as failures. |

## Team Work Order

| Team member | Next useful action | Explicit non-action |
| --- | --- | --- |
| Measurement lead | Write the method as a claim-support audit, with inclusion rules and support levels before results. | Do not state field-wide artifact prevalence. |
| Artifact engineer | Keep gate labels tied to existing CSV rows and generated summaries. | Do not download large models or rerun upstream training for narrative symmetry. |
| Table lead | Produce a heatmap and stratum table from existing selected-corpus data. | Do not merge metadata-only, replay, feature-packet, source-confounded, and admitted rows. |
| Cherry-pick auditor | Decide whether a broader source pass or second label review is needed before standalone aggregate claims. | Do not approve standalone aggregate or inter-rater claims from the selected corpus alone. |

## Review Risks and Fixes

| Risk | Fix |
| --- | --- |
| Looks anecdotal or DiffAudit-history-biased. | v1 adds 10 metadata-only surfaces from existing notes; the 2026-05-26 fixed-search batch adds an independent selection layer; the selected-corpus consistency pass found no invalid labels or promotions and demoted four empty-result `delta_gate` labels. |
| Sounds hostile to other papers. | Use claim-support language; do not say papers "fail." |
| Mixes metadata-only rows with replay rows. | Use stratified denominators and never report a pooled reproducibility rate. |
| Mixes public artifacts with internal controls. | Explicit artifact strata in table and prose. |
| Gate labels look subjective. | State that labels are protocol labels from a same-team consistency pass; do not claim independent inter-rater reliability unless a second review is added. |
| Consumer boundary looks project-specific. | Generalize as audit-consumer requirements and keep DiffAudit as one implementation. |

## Go / No-Go

| Decision | Condition |
| --- | --- |
| Keep as Direction A companion draft | Current selected-corpus matrix is enough for a scoped support section. |
| Promote to scoped standalone measurement note | Allowed if title, abstract, results, and figures all say selected corpus and use stratified denominators. |
| Promote to CCF-B-style standalone paper | Requires one broader frozen source pass or a second independent label review, plus unchanged metadata/replay/admitted separation. |
| Fork LaTeX | Allowed only after the selected-corpus gate matrix and taxonomy stay scoped, or after broader/second-review evidence is added. |
| Stop | Stop if the draft needs field-wide prevalence, paper-failure ranking, weak-scout disproof, or pooled metadata/replay denominators to sound important. |
