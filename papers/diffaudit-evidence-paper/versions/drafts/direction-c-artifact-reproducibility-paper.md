# Direction C Draft: Selected-Corpus Artifact Claim Support

## Assigned Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Measurement lead | Claim-support lead | Defines inclusion protocol, claim-support levels, six-gate method, and non-hostile framing. |
| Artifact engineer | Provenance audit lead | Separates L0 metadata discovery, L1 artifact inspection, L2 scoreable/replayed packets, feature-packet cases, and L3 consumer-admitted controls. |
| Table lead | Corpus visualization lead | Builds stratified gate heatmap, artifact funnel, and claim-support figures. |
| Cherry-pick auditor | Selection-bias critic | Ensures corpus selection is frozen before outcome claims and denominators are written. |

## Working Paper

| Field | Draft choice |
| --- | --- |
| Title | From Artifact Surfaces to Audit Claims: A Selected-Corpus Measurement of Diffusion MIA Claim Support |
| Target type | Selected-corpus artifact claim-support measurement paper |
| Venue posture | Measurement, ML systems, or security/privacy methods venue; reproducibility venue only if L0 metadata, L1 inspection, L2 scoreable/replay, feature-packet, source-confounded, and L3 admitted-control rows are separated |
| Current artifact | Draft plus v0/v1 corpus files, fixed-search batch, broader-source API pass, targeted artifact-link pass, and second-pass label review: [`../direction-c-corpus-protocol.md`](../direction-c-corpus-protocol.md), [`../direction-c-corpus-v1.md`](../direction-c-corpus-v1.md), [`../direction-c-fixed-search-batch-20260526.md`](../direction-c-fixed-search-batch-20260526.md), [`../direction-c-broader-source-pass-20260527.md`](../direction-c-broader-source-pass-20260527.md), [`../direction-c-targeted-artifact-link-pass-20260527.md`](../direction-c-targeted-artifact-link-pass-20260527.md), [`../direction-c-second-pass-label-review-20260526.md`](../direction-c-second-pass-label-review-20260526.md), [`../../data/artifact_corpus_v1.csv`](../../data/artifact_corpus_v1.csv), [`../../data/artifact_corpus_fixed_search_20260526.csv`](../../data/artifact_corpus_fixed_search_20260526.csv), [`../../data/artifact_corpus_broader_source_20260527.csv`](../../data/artifact_corpus_broader_source_20260527.csv), [`../../data/artifact_corpus_targeted_artifact_links_20260527.csv`](../../data/artifact_corpus_targeted_artifact_links_20260527.csv), and [`../../data/artifact_second_pass_label_review_20260526.csv`](../../data/artifact_second_pass_label_review_20260526.csv) |

The current filename retains the older "reproducibility" shorthand, but the
paper thesis is claim support. The draft should use "claim support",
"artifact surfaces", and "audit-consumer denominators" in titles and abstracts;
"reproducibility rate" is a prohibited framing.

## Pre-Abstract Denominator Box

This box must appear before any standalone abstract or results table. Direction
C has declared, non-poolable evidence sets:

| Evidence set | How it may be used | Explicit no-go |
| --- | --- | --- |
| `21` selected evidence-note rows | L0-L3 selected-corpus claim-support taxonomy. | Do not report a reproduction, replayability, auditability, or field-prevalence rate. |
| `17` GitHub/arXiv fixed-search metadata observations | No-download search provenance and metadata-discovery trace. | Do not treat metadata rows as replay attempts or failed reproductions. |
| `10` HF/Zenodo/OpenReview source-query observations | Metadata-screening/query hygiene only, including zero new distinct artifact surfaces and zero admitted rows. | Do not add these rows to L0-L3 aggregates or call the union `N=48`. |
| `3` targeted artifact-link seeds | L1 artifact-inspection evidence that three existing metadata-only rows have public artifact surfaces: one HF member/nonmember dataset, one official SecMI GitHub implementation/split tree, and one official MIDM code/protocol repository. | Do not treat them as score replay, admitted evidence, or a denominator to pool with `21`, `17`, or `10`. |

The same-team consistency pass and bounded second-pass review are label-hygiene
checks only. They are not independent inter-rater reliability, agreement, or
external validity evidence.

## Abstract

We code L0-L3 claim support for a frozen 21-row selected evidence-note corpus
of diffusion-MIA and adjacent generative/privacy artifact surfaces. Separately,
a 2026-05-26 GitHub/arXiv fixed-search metadata batch, a 2026-05-27
no-download HF/Zenodo/OpenReview API pass, and three targeted L1 artifact-link
seeds record provenance and source-hygiene observations; they are not pooled into
the corpus result. Artifact availability is not auditability, and metadata discovery is
not reproduction. We code each row through four claim-support levels and six
gates: L0 metadata discovery, L1 artifact inspection, L2 scoreable or replayed
packet measurement, and L3 admitted audit evidence; target identity, split
semantics, score or response coverage, metric provenance, consumer boundary,
and surface delta determine whether a row can move upward. The selected corpus
contains metadata-only public surfaces, artifact-inspectable surfaces, positive
but non-admitted feature packets, scoreable but weak bounded scouts,
source-confounded separately supplied packets, and internal admitted controls.
These are not failures of the original papers; they are claim-boundary
measurements over the released surfaces available to a consumer. The paper's
central result is a selected-corpus taxonomy of what can be discovered,
inspected, measured, admitted under a consumer boundary, or blocked from
downstream reporting. Counts are reported only within strata and are not
field-wide prevalence or reproducibility estimates.

## Controlling Thesis

The publishable claim is not "public artifacts fail." The claim is that
reusable diffusion MIA evidence has stricter claim-support levels than artifact
availability or scoreability. The unit of analysis is an artifact surface under
a frozen inclusion rule, not a paper-quality judgment. A public artifact can
support metadata inspection, artifact inspection, a bounded research-side
replay, or a consumer-boundary admitted claim, and those are different scientific
objects.

## Paper Contributions and Research Questions

| Item | Direction C contribution | Boundary |
| --- | --- | --- |
| RQ1 | Measure the maximum L0-L3 claim-support level for selected diffusion-MIA and adjacent generative/privacy artifact surfaces. | Selected corpus only; not a field-wide survey. |
| RQ2 | Separate discovery, inspection, scoreability/replay, and admission into different denominators. | No pooled reproducibility or auditability rate across metadata-only and replay rows. |
| RQ3 | Explain why positive packets, weak bounded scouts, and source-confounded packets have different claim boundaries. | Weak scouts exclude only tested routes; positive packets are not automatically admitted. |
| RQ4 | Derive release requirements for future audit-consumable artifacts. | Prescriptive checklist, not a ranking or failure label for existing papers. |

## Standalone Version Definition

This version is a claim-support measurement paper. It should read as:

> We measured what kinds of claims selected diffusion-MIA and adjacent
> generative/privacy artifacts can support
> under a reusable audit contract.

It should not read as:

> We surveyed the whole field and found that diffusion MIA artifacts fail.

The current corpus supports selected-corpus reasoning only. A standalone paper
can be written now as a scoped measurement note if it reports strata separately:
L0 metadata rows, L1 artifact-inspectable rows, L2 scoreable/replayed rows,
source-confounded packets, feature packets, and L3 admitted controls. Its
independent-paper value comes from the measurement object and denominator
discipline, not from broad coverage. Any CCF-B-style aggregate claim needs
either a larger distinct-surface frozen corpus, with external label audit only
if making reliability claims. Even then it must not pool metadata-only rows into
a reproduction denominator or call same-team checks reliability evidence.

## Standalone Claim-Support Gate

| Gate | Required stance before standalone submission |
| --- | --- |
| Unit of analysis | Artifact surface under a frozen inclusion rule, not paper success/failure. |
| Claim ladder | Define L0 metadata discovery, L1 artifact inspection, L2 scoreable/replayed packet, and L3 admitted evidence before presenting gate counts. |
| Denominators | Report metadata-only, artifact-inspectable, scoreable/replayed, feature-packet, source-confounded, and admitted-control rows separately. |
| Weak scouts | Use as bounded exclusions for tested contracts only; never as disproof of original papers. |
| Positive packets | Treat positive scores as claim support only at the available surface level; do not promote feature packets to raw-image audit evidence. |
| Consistency language | The 2026-05-26 consistency pass plus bounded second-pass label review supports internal label hygiene only; independent inter-rater reliability requires an external reviewer protocol. |
| Aggregate language | Selected-corpus taxonomy is allowed; field-wide prevalence and venue-wide quality require new evidence. |
| Consumer language | Consumer-boundary audit claims require target identity, split semantics, row-bound score/response coverage, metric provenance, boundary fit, and surface delta. |

## Selected-Corpus Protocol Required Before Full Claims

| Protocol item | Required decision |
| --- | --- |
| Current search date | Frozen at 2026-05-26 for the fixed GitHub/arXiv metadata batch. |
| Current covered sources | GitHub search, arXiv metadata search, HF model API, Zenodo records API, OpenReview notes search API, plus existing DiffAudit evidence notes. |
| Explicitly excluded from the current fixed batches | Papers with Code, major-venue manual chasing, full artifact downloads, PDFs, repository clones, model/dataset downloads, and full upstream replays. |
| Broader standalone sources | arXiv, OpenReview, major venue proceedings, GitHub, Zenodo, Hugging Face, Papers with Code. |
| Keywords | diffusion membership inference; generative model membership inference; diffusion memorization; copyright/data identification diffusion; synthetic data MIA. |
| Metadata-only rows | Record URLs, modality, target type, artifact type, public surface, six-gate labels, and no large downloads; these rows support surface-inspection claims only. |
| Scoreable/replayed rows | Require an existing score packet, response cache, feature tensor, metric JSON, bounded local packet, or replayed metric with row-level meaning. |
| Future aggregate-claim threshold | Future aggregate claims require a separately approved larger distinct-surface frozen corpus; current Direction C remains scoped to the existing `21`/`17`/`10` non-poolable sets. |
| Strata | Separate metadata-only surfaces, artifact-inspectable surfaces, scoreable/replayed packets, positive-but-non-admitted feature packets, bounded negatives, source-confounded cases, and admitted controls. |

## Current Evidence Snapshot

| Evidence item | What it supports | What it does not support |
| --- | --- | --- |
| 21-row v1 corpus | Controlled selected-corpus gate taxonomy and stratum separation; composed of `11` v0 evidence surfaces plus `10` v1 metadata-only expansions. | Field-wide prevalence or venue-wide artifact quality. |
| 17 metadata/search observations from the 2026-05-26 fixed-search batch | Separately frozen GitHub/arXiv metadata layer over a declared query set; zero rows pass both evidence and metric gates under this no-download protocol. | Full reproducibility, replayability, auditability judgment, or field prevalence without downloads or replays. |
| 10 metadata/source observations from the 2026-05-27 broader-source API pass | No-download HF/Zenodo/OpenReview metadata-screening/query hygiene: zero HF model hits, zero Zenodo title-exact records, OpenReview duplicate titled metadata for one already-recorded WACV/CoRR paper, and no new admitted row. | Proof of source-completeness, field coverage, artifact prevalence, replayability, or a larger distinct-surface corpus. |
| Generated gate-summary CSV/PDF | Counts of pass/partial/fail gate labels inside the selected corpus and within declared strata. | Statistical estimates of public artifact availability or pooled reproducibility rates. |
| Generated claim-support summary | L0-L3 support-level counts before aggregation: selected corpus `8` L0, `3` L1, `9` L2, `1` L3, where L3 is one role-level mixed-strength positive control; fixed-search batch `13` L0, `4` L1, `0` L2, `0` L3. | A pooled reproducibility, replayability, auditability, or field-prevalence rate. |
| Selected-corpus consistency pass plus bounded second-pass review | Internal label hygiene; the consistency pass found no invalid labels or route-changing contradictions, and the bounded second-pass review found no admitted-like fixed-search row or metadata-batch evidence/metric promotion; two additional gate labels tightened after same-team resolution. | Independent inter-rater reliability. |

## Corpus Flow To Make Inspectable

The standalone version needs a figure or table that makes denominator flow
visible before any result sentence. The safe flow is:

Safe denominator wording:

> We analyze three declared, non-poolable evidence sets: a 21-row selected
> evidence-note corpus for L0-L3 claim-support coding, a separately frozen
> 17-row GitHub/arXiv no-download metadata/search batch for discovery
> provenance, and a 10-row HF/Zenodo/OpenReview no-download API pass for
> metadata-screening/query hygiene. These denominators are never summed, and none is
> reported as a field-wide reproducibility, replayability, auditability, or
> artifact-prevalence rate.

The `21` selected rows themselves are a frozen selected set, not a literature
sample: `11` rows come from v0 evidence surfaces and `10` rows are v1
metadata-only expansions. That composition is useful for claim-boundary coding,
but it cannot be converted into a corpus-growth or field-coverage claim.

## Table 1: Denominator Ledger

This ledger must appear before any standalone results table and should be
promoted as Table 1 if Direction C becomes a standalone note. It prevents the
three evidence sets from being summed into a false `N=48` corpus.

| Evidence set | Result allowed | Result forbidden |
| --- | --- | --- |
| `21` selected evidence-note rows | L0-L3 taxonomy `8/3/9/1` for selected claim-support states. | `9/21 reproducible`, field prevalence, or representative artifact-quality rate. |
| `17` fixed GitHub/arXiv metadata/search rows | L0-L3 metadata/search taxonomy `13/4/0/0` under a no-download protocol. | `0/17 reproducible`, replayability, or auditability denominator. |
| `10` HF/Zenodo/OpenReview broader-source observations | Metadata-screening/query hygiene; no L0-L3 summary, zero new distinct artifact surfaces, and zero admitted rows. | `10-row broader corpus expansion`, field coverage proof, or pooled claim-support denominator. |
| Reportable bundle positive control | One role-level L3 surface representing five mixed-strength reportable rows. | Five homogeneous row-score replay rows or `1/48 consumer-admitted`. |
| Label hygiene check | Same-team trace over `4` promotion-risk disagreements with `2` adopted tightenings. | Independent inter-rater reliability, agreement score, or external label audit. |

| Stage | Rows | Action allowed | Result type |
| --- | ---: | --- | --- |
| Selected evidence-note corpus | `21` | Reuse already audited records and bridge artifacts; no new downloads or model runs. | L0-L3 claim-support taxonomy inside the selected corpus. |
| Fixed GitHub/arXiv metadata batch | `17` | No-download metadata search with empty, duplicate, noisy, and included rows kept visible. | Source-discovery trace; no replay or prevalence estimate. |
| HF/Zenodo/OpenReview broader-source pass | `10` | No-download API observations over three sources and declared queries. | Metadata-screening/query hygiene; zero new distinct artifact surfaces and zero admitted rows. |
| Second-pass label review | `4` promotion-risk disagreements | Same-team bounded review/resolution over high-risk labels. | Label hygiene only; no inter-rater reliability. |

The Methods section should define this flow first, the Results section should
report `8/3/9/1` and `13/4/0/0` only after naming the relevant denominator, and
Threats should state that the second-pass reviewer saw a promotion-risk subset
rather than a full independent annotation task.

## Mandatory Results Preamble

Every results paragraph must first name its denominator: `21` selected
evidence-note rows, `17` fixed-search metadata observations, `10`
broader-source API observations, the `2` targeted artifact-link seeds, or the
subset of rows with row-level scores, responses, feature tensors, or admitted controls.
L0 metadata, L1 inspection, L2 score/replay, source-confounded packets, and L3
admitted controls are not pooled into one reproducibility, replayability, or
auditability rate. The reportable-bundle positive control is role-level mixed:
it contains replay-admitted rows and source-documented point estimates, so it
must not be described as a homogeneous L3 row-score packet.

## Results Skeleton

This skeleton is the safe standalone-results spine for Direction C. It is
intentionally denominator-first so the paper can be promoted to a scoped note
without drifting into field-wide prevalence or pooled reproducibility claims.

| Results paragraph | Denominator to state first | Allowed result sentence | Forbidden drift |
| --- | --- | --- | --- |
| Corpus construction | `21` selected evidence-note rows plus separately frozen `17`-row GitHub/arXiv and `10`-row HF/Zenodo/OpenReview no-download metadata batches, plus three targeted L1 seeds. | "We analyze declared, non-poolable sets: a selected evidence-note corpus used for claim-boundary coding, a metadata-only fixed-search trace used to record public-surface discovery under frozen queries, a broader-source API pass used only for metadata-screening/query hygiene, and targeted artifact-link seeds used only as L1 inspection evidence." | Do not call the union a representative literature survey or convert query-hygiene observations or the targeted seeds into L0-L3 aggregate evidence. |
| Claim-support ladder | `21` selected rows plus `17` fixed-search observations, each assigned an L0-L3 maximum support level before aggregation. | "The selected corpus contains `8/3/9/1` L0-L3 rows, while the no-download fixed-search batch contains `13/4/0/0`; availability, scoreability, replay, and admission are reported as different objects." | Do not report a single reproducibility, replayability, or auditability rate. |
| Fixed-search metadata | `17` metadata/search observations, including empty, duplicate, noisy, and excluded rows. | "The fixed-search batch found no new admitted-like row under the no-download metadata protocol." | Do not describe metadata rows as failed reproductions or proof that the field lacks consumer-admitted artifacts. |
| Targeted artifact-link seeds | The `ta20260527-hf-01`, `ta20260527-github-02`, and `ta20260527-github-03` rows, reported separately from `21`, `17`, and `10`. | "Three existing metadata-only seeds have public artifact surfaces, but no score, response, ROC, metric JSON, or verifier packet." | Do not count them as replay, admitted evidence, or corpus-size proof. |
| L2 research-side packets | Only rows with row-level score, response, feature, metric JSON, or bounded local packets. | "Positive feature packets, weak bounded scouts, and source-confounded packets support route-local claim decisions." | Do not pool them with L0 metadata or L3 admitted controls. |
| L3 positive controls | The reportable bundle, explicitly split into replay-admitted rows and source-documented point estimates. | "The positive control demonstrates the contract states we require, not a homogeneous benchmark row set." | Do not call all five rows row-score replay or use point estimates for interval/dominance claims. |
| Label hygiene | The 2026-05-26 consistency pass plus four-row bounded second-pass review. | "The review tightened two labels and found no admitted-like metadata-batch promotion." | Do not call this independent inter-rater reliability. |

Minimal standalone results text should follow this order: construct the
declared, non-poolable evidence sets, define L0-L3 support levels, report gate
labels within strata, then use boundary examples only to explain why a row's
strongest supported claim stops at its current level.

## Claim-Support Levels

| Level | Row type | Entry condition | Supported claim | Not supported |
| --- | --- | --- | --- | --- |
| L0 | Metadata discovery | Frozen search result, paper/repo URL, empty result, duplicate hit, or query-noise row. | A public surface was found, absent, partial, duplicate, or noisy under declared rules. | Reproduction, replayability, scoreability, auditability, or artifact-quality prevalence. |
| L1 | Artifact-inspectable | Code, manifests, release structure, hashes, documented splits, or artifact tree can be inspected. | The released surface exposes target, split, coverage, or provenance clues. | Metric claims unless score/response/feature rows exist. |
| L2 | Scoreable/replayed | Existing score rows, response cache, feature tensor, metric JSON, bounded local packet, or replayed metric has row-level meaning. | Finite research-side measurement and route decisions inside a tested contract. | Downstream admission without consumer-boundary and surface-delta gates. |
| L3 | Consumer-admitted | Row-bound evidence, metric provenance, and consumer boundary jointly pass admission. | An admitted audit claim under the explicit consumer contract. | Generalization beyond the admitted contract or calibrated continuous low-FPR risk. |

## Contribution Claims

| Claim | Evidence anchor | Boundary |
| --- | --- | --- |
| C-C1: Artifact availability, inspectability, scoreability, replayability, admitted evidence, and consumer-boundary reporting are distinct. | Six-gate protocol, v1 corpus, fixed-search batch, and gate-summary assets | Supports selected-corpus taxonomy only; no field-wide prevalence claims. |
| C-C2: Metadata-only fixed-search rows must not be pooled with scoreable or replayed rows. | 2026-05-26 fixed-search batch with zero evidence+metric-pass rows versus v1 evidence-note rows | Metadata rows support discovery/surface-inspection claims, not reproduction or replay rates. |
| C-C3: Positive packets can be scientifically useful but non-admitted. | Tracing Roots AUC `0.815826` | Feature-packet evidence only, not raw image/checkpoint audit evidence. |
| C-C4: Bounded weak scouts are useful route exclusions. | ReDiffuse `0.4996/0.5053`, CommonCanvas `0.5148`, MIDST `0.598079` | Excludes tested routes only; does not disprove original methods or unreleased settings. |
| C-C5: Source confounding must be audited. | SD ReDiffuse AUC `0.710319`, source-only AUC `1.0` | Cross-source stress test, not same-distribution MIA. |
| C-C6: Consumer-boundary gates can be proposed as reusable audit-consumer requirements. | Gate definitions in source/claim maps | Proposal derived from DiffAudit evidence; external validation is needed before a general adoption claim. |
| C-C7: Same-team consistency and bounded second-pass review are useful but not reliability evidence. | 2026-05-26 consistency pass found no invalid labels or route-changing contradictions; bounded second-pass review found no admitted-like fixed-search row or metadata-batch evidence/metric promotion; adopted tightenings: `v1-10.delta_gate=Fail` and `fs20260526-arxiv-03.target_gate=Fail` | Do not call it independent inter-rater reliability. |

## Result Reporting Contract

| Result object | Required denominator | Forbidden denominator |
| --- | --- | --- |
| Fixed-search discovery results | The 17 frozen search observations, including empty/noise/duplicate rows. | Scoreable artifacts, replay attempts, or reproduction attempts. |
| Broader-source API observations | The 10 frozen HF/Zenodo/OpenReview observations, including zero-result, untitled, and duplicate titled rows. | New artifact surfaces, field coverage, scoreable artifacts, replay attempts, or reproduction attempts. |
| Targeted artifact-link seeds | The three L1 rows `ta20260527-hf-01`, `ta20260527-github-02`, and `ta20260527-github-03`. | Scoreable packet, admitted evidence, field coverage, or pooled corpus denominator. |
| v1 gate matrix | The 21 selected evidence-note rows, reported by stratum. | All diffusion MIA papers or all public artifacts. |
| L2 measurement results | Rows with row-level score, response, feature, metric JSON, or bounded local packets. | L0 metadata-only rows or L1 inspection-only rows. |
| L3 admitted evidence | Rows accepted by the consumer-boundary contract. | Positive feature packets or candidate metrics without admission. |
| Consistency status | Same-team label-hygiene pass plus bounded second-pass label review. | Independent inter-rater reliability, external validity, or field prevalence. |

Every results paragraph should name the denominator before the count or rate.
If a figure mixes strata visually, its caption must state that the groups are
not pooled into a reproduction, replayability, or auditability rate.

## Manuscript Spine

| Section | Draft content |
| --- | --- |
| Introduction | Distinguish artifact availability, scoreability, replayability, admitted evidence, and consumer-boundary reporting. |
| Selected-Corpus Protocol | Present fixed search window, covered sources, excluded sources, keywords, metadata fields, and exclusion rules before any results. |
| Claim-Support Levels and Six-Gate Method | Define L0-L3 claim-support levels before interpreting pass/partial/fail gates for target identity, member/nonmember split, score/response coverage, metric provenance, consumer boundary, and surface delta. |
| Artifact Strata | Separate metadata-only surfaces, artifact-inspectable surfaces, public score/feature packets, bounded local scouts, source-confounded separately supplied packets, internal candidate controls, and internal admitted controls. |
| Results | Report gate matrix and claim-support taxonomy as coded rows in this corpus; avoid ranking papers by "failure" or reporting pooled reproducibility rates. |
| Boundary Examples | Split by stratum: public metadata surfaces, public score/feature packets, bounded local scouts, separately supplied packets, and internal controls. |
| Lessons for Authors | State what future artifacts should publish: manifests, hashes, score rows, ROC arrays, metric JSON, finite-tail denominators, boundary language. |
| Threats to Validity | Selected-corpus bias, same-team labels, restricted/non-redistributable evidence, metadata-only inspection limits, DiffAudit-specific consumer boundary, finite tails. |

## Section-Level Draft Skeleton

| Section | Claim to make | Required evidence | Text boundary |
| --- | --- | --- | --- |
| 1. Introduction | Auditability is a stricter object than artifact availability or scoreability. | Six-gate contract and examples of distinct strata. | Avoid hostile "artifact failure" framing. |
| 2. Corpus Construction | The corpus is frozen and selected by explicit rules. | v1 corpus, fixed-search batch, protocol docs. | State selected-corpus only. |
| 3. Claim-Support Ladder | L0-L3 levels define what a row can support before gates are interpreted. | metadata-only, artifact-inspectable, scoreable/replayed, and consumer-admitted control rows. | Do not pool metadata-only rows with replay rows. |
| 4. Six-Gate Method | Gates define what claim an artifact can support within its stratum. | target identity, split semantics, score/response coverage, metric provenance, consumer boundary, surface delta. | Gates are audit-consumer requirements, not moral judgments. |
| 5. Stratified Gate Results | Selected artifacts occupy multiple support states. | gate-summary CSV/PDF and strata table. | Counts are not prevalence estimates or reproducibility rates. |
| 6. Boundary Examples | Positive, weak, and confounded packets reveal different claim boundaries. | Tracing Roots, ReDiffuse, CommonCanvas, MIDST, SD ReDiffuse, H2. | Weak scouts do not disprove original papers. |
| 7. Author Checklist | Future artifacts can make claims reusable by publishing row-bound evidence. | release checklist from Direction A. | Checklist is prescriptive, not a pass/fail ranking of papers. |

## Case-Study Claim Boundaries

| Case | Claim-support level in this paper | What it demonstrates | Boundary sentence |
| --- | --- | --- | --- |
| Fixed-search metadata rows | L0 | Search provenance and public-surface discovery can be frozen without downloads. | These rows are not replay attempts and never enter the reproduction denominator. |
| CopyMark public artifacts | L1 / artifact-rich partial | Rich public surfaces can still lack compact row-binding for admission. | Artifact richness is not audit readiness. |
| Tracing Roots feature packet | L2 positive non-admitted | A positive replayed feature packet can support a bounded measurement. | Feature evidence does not become raw image/checkpoint consumer evidence. |
| ReDiffuse, CommonCanvas, MIDST scouts | L2 bounded negative or borderline support | Weak scouts can close tested routes and prevent low-value sweeps. | The exclusion is route-local and does not disprove the original papers. |
| Separately supplied SD ReDiffuse packet | L2 source-confounded | Replayable metrics can be dominated by source identity. | This is a source-confounding stress case, not same-distribution MIA proof. |
| DiffAudit consumer-admitted controls | L3 | Row-bound evidence plus consumer boundary can support audit claims. | Admission is contract-specific and does not generalize beyond the admitted/reportable rows' stated replay tiers. |

## Figure and Table Plan

| Asset | Purpose |
| --- | --- |
| Corpus flow diagram | Shows fixed search, screening, metadata-only extraction, replay/score packet identification, and gate assignment. |
| Claim-support ladder | Generated as [`../../figures/artifact_claim_support_summary.pdf`](../../figures/artifact_claim_support_summary.pdf); shows L0-L3 support counts for the `21` selected rows and `17` fixed-search observations side by side before any gate result. |
| Six-gate heatmap | Main selected-corpus empirical figure; caption must state that counts are not prevalence estimates, pooled reproducibility rates, or inter-rater reliability. |
| Artifact stratum table | Prevents metadata-only rows, public replay/feature packets, source-confounded packets, and internal controls from being mixed. |
| Signal-vs-completeness scatter | Shows that high or positive scores are not sufficient for admission. |
| Gap-taxonomy chart | Counts target-identity, split, score, provenance, and boundary gaps without ranking papers as failures. |

## Team Work Order

| Team member | Next useful action | Explicit non-action |
| --- | --- | --- |
| Measurement lead | Write the method as a claim-support audit, with inclusion rules and support levels before results. | Do not state field-wide artifact prevalence. |
| Artifact engineer | Keep gate labels tied to existing CSV rows and generated summaries. | Do not download large models or rerun upstream training for narrative symmetry. |
| Table lead | Maintain the generated L0-L3 claim-support figure, gate heatmap, and stratum table from existing selected-corpus data. | Do not merge metadata-only, replay, feature-packet, source-confounded, and consumer-admitted controls. |
| Cherry-pick auditor | Treat the completed broader-source API pass as hygiene only; decide whether a larger distinct-surface corpus is needed before standalone aggregate claims or external label audit is needed before reliability claims. | Do not approve standalone aggregate or inter-rater claims from the selected corpus alone. |

## Review Risks and Fixes

| Risk | Fix |
| --- | --- |
| Looks anecdotal or DiffAudit-history-biased. | v1 adds 10 metadata-only surfaces from existing notes; the 2026-05-26 fixed-search batch adds a separately frozen GitHub/arXiv metadata layer; the 2026-05-27 broader-source pass adds no-download HF/Zenodo/OpenReview API observations; the selected-corpus consistency pass found no invalid labels or route-changing contradictions, and the bounded second-pass review found no admitted-like fixed-search row or metadata-batch evidence/metric promotion while adopting only two further gate tightenings. |
| Sounds hostile to other papers. | Use claim-support language; do not say papers "fail." |
| Mixes metadata-only rows with replay rows. | Use stratified denominators and never report a pooled reproducibility rate. |
| Mixes public artifacts with internal controls. | Explicit artifact strata in table and prose. |
| Gate labels look subjective. | State that labels are protocol labels from same-team consistency plus bounded second-pass label review; do not claim independent inter-rater reliability unless an external reviewer protocol is added. |
| L0 fixed-search rows look like negative reproductions. | Describe them as metadata/search observations with no downloads, no replays, and no evidence+metric-pass rows. |
| Broader-source rows look like corpus expansion proof. | Describe them as metadata-screening/query hygiene with zero new distinct artifact surfaces and zero admitted rows, not source-completeness evidence. |
| Weak scouts are overread. | Put the tested route and contract in the case-study boundary sentence. |
| Consumer boundary looks project-specific. | Generalize as audit-consumer requirements and keep DiffAudit as one implementation. |

## Go / No-Go

| Decision | Condition |
| --- | --- |
| Keep as Direction A companion draft | Current selected-corpus matrix is enough for a scoped support section. |
| Promote to scoped standalone measurement note | Allowed if title, abstract, results, and figures all say selected corpus and use stratified denominators. |
| Promote to CCF-B-style standalone paper | Requires a larger distinct-surface frozen corpus with new artifact surfaces; add an external label audit protocol if making reliability claims. Metadata/replay/admitted separation must stay unchanged, and reliability language requires a multi-reviewer design. |
| Fork LaTeX | Not in this worker; later allowed only after the selected-corpus gate matrix and taxonomy stay scoped, or after larger corpus or external-review evidence is added. |
| Stop | Stop if the draft needs field-wide prevalence, paper-failure ranking, weak-scout disproof, inter-rater claims from the consistency pass, or pooled metadata/replay denominators to sound important. |
