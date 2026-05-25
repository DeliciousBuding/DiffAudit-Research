# Direction C Corpus Protocol v0

> Date: 2026-05-26
> Status: metadata-only frozen starter corpus; no new downloads, model runs, or
> repository clones.

This protocol turns Direction C from a paper idea into an auditable measurement
plan. It is intentionally narrower than a standalone reproducibility paper. Its
job is to define what can be counted from existing evidence without cherry
picking or inventing missing artifacts.

## Inclusion Rule

A candidate enters v0 if it satisfies all conditions below:

- It appears in an existing DiffAudit evidence note or product-bridge card.
- The note records a concrete public artifact, collaborator artifact, score
  packet, response packet, feature packet, or bounded replay/scout.
- The note records a decision that affects paper claims, candidate status, or
  Platform/Runtime admission.
- The candidate can be classified without downloading additional checkpoints,
  datasets, generated images, model folders, or large repositories.

Excluded from v0:

- Purely speculative papers with no checked public surface.
- Semantic-shift privacy topics that have not affected the current membership
  evidence boundary.
- Items whose only available information is a headline metric copied from a
  paper table with no artifact inspection.

## Six Gates

| Gate | Pass Meaning | Partial Meaning | Fail Meaning |
| --- | --- | --- | --- |
| Target identity | Fixed target/checkpoint or fixed released packet identity. | Target family known but checkpoint/regeneration identity missing. | Only paper-level target prose. |
| Split binding | Exact member/nonmember rows or fixed feature/score split. | Split exists but cannot bind to raw public rows. | No exact member/nonmember contract. |
| Evidence coverage | Row-level scores, response cache, feature tensor, or scoreable local packet. | Aggregate metrics plus partial row logs. | Only aggregate paper metrics. |
| Metric provenance | Metrics replayed or computed from stored rows/packets. | Metrics read from official result files without row score vectors. | Metrics not traceable to artifacts. |
| Consumer boundary | Claim can be consumed under an explicit admitted/support/candidate boundary. | Useful for Research but not current Platform/Runtime. | Boundary mismatch or semantic shift blocks use. |
| Surface delta | Adds a non-duplicate model/data/modality/response/feature surface. | Same family but useful support context. | Same-family repeat with no decision value. |

## Frozen v0 Corpus

| Candidate | Artifact Surface | Gate Summary | Direction C Role |
| --- | --- | --- | --- |
| Admitted bundle | Five machine-readable admitted rows | Passes current consumer boundary | Positive control for audit-ready evidence |
| H2 output-cloud geometry | Existing response caches plus replayed metrics | Strong candidate, consumer boundary partial | Mechanism candidate with controlled non-admission |
| H2 img2img portability | Existing SD/CelebA img2img response caches | Metric pass, portability fail | Boundary-negative result |
| CLiD official inter-output | Official `inter_output/*` score files | Strong metric, image identity blocked | Positive score packet with row-binding gap |
| Tracing the Roots | OpenReview feature tensors and replay code | Feature-level pass, raw provenance partial | Positive feature-packet evidence |
| CopyMark official score artifacts | Official result JSON, image logs, score tensors | Artifact-rich but no compact admitted packet | Artifact availability vs auditability case |
| ReDiffuse STL-10 scout | Exact split plus bounded local score packet | Executable but weak signal | Bounded negative with clean split |
| CommonCanvas response packet | Real `50/50` query/response contract | True second response packet, weak scorers | Second-asset negative |
| MIDST Blending++ | Official score exports plus local labels | Borderline metric below reopen floor | Cross-domain negative/support |
| Stable Diffusion ReDiffuse collaborator | Local `5000`-row packet and ROC files | Replayable, source-confounded | Source-confounding case |
| Quantile/SecMI public packet | Third-party `t_error` score rows and splits | Positive support, same-family SecMI | Support-only public score packet |

## Initial Gate Matrix

| Candidate | Target | Split | Evidence | Metric | Boundary | Delta |
| --- | --- | --- | --- | --- | --- | --- |
| Admitted bundle | Pass | Pass | Pass | Pass | Pass | Partial |
| H2 output-cloud geometry | Pass | Pass | Pass | Pass | Partial | Partial |
| H2 img2img portability | Pass | Pass | Pass | Pass | Fail | Pass |
| CLiD official inter-output | Partial | Partial | Pass | Pass | Partial | Pass |
| Tracing the Roots | Partial | Pass | Pass | Pass | Partial | Pass |
| CopyMark official score artifacts | Partial | Partial | Partial | Partial | Partial | Pass |
| ReDiffuse STL-10 scout | Pass | Pass | Pass | Pass | Fail | Pass |
| CommonCanvas response packet | Partial | Pass | Pass | Pass | Fail | Pass |
| MIDST Blending++ | Partial | Pass | Pass | Pass | Partial | Pass |
| Stable Diffusion ReDiffuse collaborator | Partial | Partial | Pass | Pass | Fail | Pass |
| Quantile/SecMI public packet | Partial | Pass | Pass | Pass | Partial | Partial |

## Failure Taxonomy

| Failure Mode | Meaning | v0 Examples |
| --- | --- | --- |
| Identity gap | Public artifact lacks raw target checkpoint or regeneration identity. | Tracing the Roots, CLiD, CopyMark |
| Row-binding gap | Score rows cannot bind to immutable public sample IDs. | CLiD, CopyMark |
| Consumer-boundary mismatch | Artifact is useful for Research but not Platform/Runtime admission. | H2 output-cloud, Tracing the Roots, Quantile/SecMI |
| Weak transferred signal | Bounded scorer answers the decision question but does not reopen the route. | ReDiffuse STL-10, CommonCanvas, MIDST |
| Source confounding | Membership label is entangled with source dataset/domain labels. | Stable Diffusion ReDiffuse collaborator |

## Expansion Rule

Direction C may expand beyond v0 only by adding candidates that meet the
inclusion rule above. The first expansion should be metadata-only: record URL,
artifact type, latest observed public surface, gate results, and whether a
small replay is already present. Do not download large archives, checkpoints,
datasets, generated image folders, or model repositories just to fill a table.

## Paper-Claim Boundary

Allowed:

- "In this frozen starter corpus, many strong or positive artifact surfaces are
  not automatically audit-ready."
- "Gate failures are heterogeneous: identity, row binding, consumer boundary,
  weak transferred signal, and source confounding are different phenomena."
- "Negative bounded scouts can be evidence when they close a route-selection
  question."

Forbidden:

- "Most diffusion MIA papers are not reproducible."
- "A weak bounded scout disproves the original method."
- "Artifact-rich public repositories are failed releases."
- "Support-only public score packets are admitted DiffAudit rows."
