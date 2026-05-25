# Direction C Draft: Artifact Reproducibility and Claim Support

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
| Title | When Diffusion MIA Scores Are Not Audit Evidence: A Claim-Support Study of Public Artifacts |
| Target type | Reproducibility/measurement paper |
| Venue posture | Reproducibility, measurement, ML systems, or security/privacy methods venue |
| Current artifact | Draft plus v0/v1 corpus files and fixed-search batch: [`../direction-c-corpus-protocol.md`](../direction-c-corpus-protocol.md), [`../direction-c-corpus-v1.md`](../direction-c-corpus-v1.md), [`../direction-c-fixed-search-batch-20260526.md`](../direction-c-fixed-search-batch-20260526.md), [`../../data/artifact_corpus_v1.csv`](../../data/artifact_corpus_v1.csv), and [`../../data/artifact_corpus_fixed_search_20260526.csv`](../../data/artifact_corpus_fixed_search_20260526.csv) |

## Abstract

Public diffusion membership-inference artifacts often expose code,
checkpoints, score packets, or supplementary materials, but artifact
availability is not the same as auditability. This paper studies what claims
public artifacts can safely support. We evaluate artifacts through six gates:
target identity, member split, nonmember split, score or response coverage,
metric provenance, and consumer-boundary fit. The current DiffAudit starter
corpus shows several distinct outcomes. Some packets are positive but
non-admitted because they expose feature-level rather than image-level evidence.
Some bounded scouts are scoreable but weak under the audited observable. Some
local or collaborator packets are replayable but source-confounded. These are
not failures of the original papers; they are claim-boundary measurements. The
paper's central result is a taxonomy of artifact claim support: what can be
replayed, what can be scored, what can be audited, and what can be safely
consumed.

## Controlling Thesis

The publishable claim is not "public artifacts fail." The claim is that
reusable diffusion MIA evidence has stricter requirements than artifact
availability or scoreability. A public artifact can support a paper claim, a
research-side replay, or a consumer-safe audit claim, and those are different
scientific objects.

## Corpus Protocol Required Before Full Claims

| Protocol item | Required decision |
| --- | --- |
| Search date | Freeze at an absolute cutoff, e.g. 2026-05-26 for the first corpus expansion. |
| Sources | arXiv, OpenReview, major venue proceedings, GitHub, Zenodo, Hugging Face, Papers with Code. |
| Keywords | diffusion membership inference; generative model membership inference; diffusion memorization; copyright/data identification diffusion; synthetic data MIA. |
| Metadata only | Record URLs, modality, target type, artifact type, public surface, six-gate labels, and no large downloads. |
| Target size | Add 10-20 papers or artifact surfaces before making aggregate claims. |
| Strata | Separate audit-ready controls, positive-but-non-admitted packets, bounded negatives, source-confounded cases, no/partial-artifact cases, and internal controls. |

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
| Corpus Protocol | Present fixed search window, sources, keywords, metadata fields, and exclusion rules before any results. |
| Six-Gate Method | Define pass/partial/fail for target identity, member split, nonmember split, score/response coverage, metric provenance, and consumer-boundary fit. |
| Artifact Strata | Separate public artifacts, collaborator/local packets, internal admitted controls, and internal candidate controls. |
| Results | Report gate matrix and failure taxonomy; avoid ranking papers by "failure." |
| Case Studies | Tracing Roots feature packet, ReDiffuse STL-10 bounded scouts, CommonCanvas, MIDST, SD ReDiffuse source confounding, H2 as internal candidate control. |
| Lessons for Authors | State what future artifacts should publish: manifests, hashes, score rows, ROC arrays, metric JSON, finite-tail denominators, boundary language. |
| Threats to Validity | Cherry-picking, local-only evidence, metadata-only inspection limits, DiffAudit-specific consumer boundary, finite tails. |

## Figure and Table Plan

| Asset | Purpose |
| --- | --- |
| Corpus flow diagram | Shows fixed search, screening, metadata-only extraction, and gate assignment. |
| Six-gate heatmap | Main empirical figure after expansion. |
| Artifact stratum table | Prevents internal controls and public artifacts from being mixed. |
| Signal-vs-completeness scatter | Shows that high or positive scores are not sufficient for auditability. |
| Failure-taxonomy chart | Counts target-identity, split, score, provenance, and boundary gaps. |

## Review Risks and Fixes

| Risk | Fix |
| --- | --- |
| Looks anecdotal or DiffAudit-history-biased. | v1 adds 10 metadata-only surfaces from existing notes; the 2026-05-26 fixed-search batch adds an independent selection layer; next run gate-label consistency. |
| Sounds hostile to other papers. | Use claim-support language; do not say papers "fail." |
| Mixes public artifacts with internal controls. | Explicit artifact strata in table and prose. |
| Consumer boundary looks project-specific. | Generalize as audit-consumer requirements and keep DiffAudit as one implementation. |

## Go / No-Go

| Decision | Condition |
| --- | --- |
| Keep as draft | Current v0 supports a structured plan. |
| Promote to standalone paper | Requires gate-label consistency review over v1 plus the fixed-search batch, and preferably one broader source pass if making aggregate claims beyond this corpus. |
| Fork LaTeX | Allowed only after consistency review produces a defensible gate matrix and failure-taxonomy table. |
| Stop | If expansion remains only existing DiffAudit history; that would be a section in Direction A, not a standalone paper. |
