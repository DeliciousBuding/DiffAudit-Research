# Research Team Pitches

> Date: 2026-05-26
> Scope: persistent paper-team planning notes for the A-D manuscript directions.

## Portfolio Operating Rule

The four teams are allowed to produce different paper versions, but they must
share one evidence ledger. A team may change framing, section order, figures,
venue posture, and reviewer argument. It may not promote candidate evidence,
create a private claim register, or start new model/data execution for symmetry.
The expected output before a TeX fork is a readable paper version: title,
abstract, controlling thesis, contribution claims, section spine, figure/table
plan, review risks, and a go/no-go gate.

## Team A: Evidence-Contracted Measurement

| Field | Pitch |
| --- | --- |
| Title | DiffAudit: Evidence-Contracted Measurement for Auditing Membership Leakage in Diffusion Models |
| Venue fit | RAID or ACSAC as CCF-B security venues; IMC as measurement-style secondary target if the corpus is expanded. |
| Core thesis | Diffusion-model privacy auditing is bottlenecked less by missing attacks than by unauditable evidence. Public claims often lack fixed target identity, exact member/nonmember splits, row-level scores, finite-tail interpretation, or consumer-safe provenance. |
| Contribution claims | Audit evidence contract; taxonomy of verified/candidate/watch/blocked evidence; admitted black/gray/white-box rows; explicit prevention of high-scoring but unsafe candidates becoming headline claims. |
| Minimum figures/tables | Evidence-gate table; admitted-vs-candidate table; audit pipeline figure; selected-corpus gate-summary figure; case-study comparison with non-admitted labels. |
| Additional work | Lightweight measurement only: freeze candidate corpus, count gate-failure modes, recompute stored metric tables, and ensure every plotted point has row-level evidence. |
| Fatal risks | Looks like internal governance unless artifact-readiness measurement is quantified; admitted rows remain narrow; local-only evidence may be challenged. |
| Overclaiming guard | Claim auditability and evidence calibration, not SOTA attack performance. Always separate admitted/candidate/watch rows and report finite-tail denominators. |

## Team B: Output-Cloud Mechanism

| Field | Pitch |
| --- | --- |
| Title | Response-Cloud Geometry Has an H2 Membership Signal, But Does Not Port to Img2img |
| Venue fit | Strong privacy/ML security workshop or short paper candidate; full CCF-B mechanism paper only if a second independent response asset appears. |
| Scientific question | Does the audited H2 repeated-response cache expose membership through geometry among repeated outputs, rather than only through query-to-output or seed-to-output distance? |
| Contribution claims | Output-output geometry as an operationally separated H2 observable relative to tested raw/lowpass baselines; strong H2 DDPM/CIFAR10 signal; label-shuffle and shared-position controls; same-family cross-cache stability; negative SD/CelebA img2img portability boundary. |
| Figures/tables | Response-cloud method schematic; H2 vs raw/lowpass table; controls table; feature-family/coefficient view; img2img portability table; boundary diagram. |
| Additional bounded experiments | No more H2 polishing by default. A second public response asset and pre-registered interleaved cache-generation protocol are the only experiments that can change full-paper viability. |
| Fatal risks | Strong evidence remains one H2 response-cache family; img2img portability is weak; logistic fusion may look like feature engineering. |
| Safe claim | Output-output response-cloud geometry is a strong controlled Research-side H2 observable relative to tested H2 baselines, with unresolved and partly negative portability. Cross-cache transfer is same-family robustness, not cross-model or cross-dataset transfer. |

### Team B LaTeX Fork Gate

Fork a standalone TeX draft only if either a second independent response asset
passes the six-gate contract, or the paper is explicitly scoped as a
short/workshop mechanism case study with the SD/CelebA img2img portability
failure as a central result. Do not fork for more H2 feature sweeps, `512/512`
symmetry reruns, repeat-count tuning, KDE variants, or input-distance fusion.

## Team C: Selected-Corpus Artifact Claim-Support Measurement

| Field | Pitch |
| --- | --- |
| Title | From Artifact Surfaces to Audit Claims: A Selected-Corpus Measurement of Diffusion MIA Claim Support |
| Venue fit | MLSys, SaTML, FAccT methods track, or measurement workshop; reproducibility venues only if L0 metadata, L1 inspection, L2 scoreable/replayed, feature-packet, source-confounded, and L3 admitted-control rows are separated. |
| Core thesis | In a frozen selected corpus, diffusion MIA artifact surfaces support different L0-L3 claim levels: metadata discovery, artifact inspection, bounded score/replay, audit-ready evidence, and consumer-safe reporting. |
| Contribution claims | L0-L3 claim-support levels; six-gate second-asset contract; selected-corpus claim-support audit across CLiD, Tracing Roots, ReDiffuse, CommonCanvas, MIDST, Stable Diffusion ReDiffuse, and fixed GitHub/arXiv search records; taxonomy of support states; weak results as tested-route exclusions only. |
| Figures/tables | Claim-support ladder; stratified six-gate matrix; selected-corpus gate-summary figure; artifact funnel from paper claim to reusable evidence; signal-strength vs artifact-completeness map. |
| Lightweight additional work | Use the 21-row v1 corpus, the 2026-05-26 fixed-search batch, generated gate-summary counts, and the completed selected-corpus consistency pass with stratified denominators. Add one broader fixed-source pass or a second independent label review only for standalone aggregate claims. |
| Fatal risks | Looks anecdotal unless candidate inclusion is preregistered; metadata-only rows can be mistaken for reproductions; mixed strata can create false equivalence. |
| Framing rule | Do not say papers fail, do not pool metadata-only rows with replay rows, and do not treat weak scouts as disproof. Say we measure what claim level survives reusable, row-bound, low-FPR, consumer-safe constraints. |

## Portfolio Decision

The current primary manuscript should remain Team A's evidence-contracted
measurement paper. It can incorporate Team B as a technical case study and Team
C as its broader claim-support motivation and selected-corpus gate summary.
Team B becomes the next technical paper if a second response asset is acquired
or if the scope is explicitly a short H2 case study with portability failure
central. Team C becomes a standalone measurement paper only if the selected
corpus grows or receives a second independent label review while preserving
stratified denominators and no field-wide overclaiming.

## Multi-Team Execution Board

| Team | Paper version to own | Decision authority | Immediate writing target | Must escalate before |
| --- | --- | --- | --- | --- |
| Team A: Evidence-Contracted Measurement | Full Direction A LaTeX manuscript. | Final wording for admitted/candidate/support taxonomy, venue posture, and rebuttal stance. | Rewrite the active manuscript as a measurement-methodology paper rather than an internal governance report. | Removing H2 from the main paper, changing admitted rows, or claiming cross-asset generality. |
| Team B: Output-Cloud Mechanism | Direction B H2-limited short/workshop draft. | Mechanism vocabulary, response-cloud feature explanation, and portability-boundary wording. | Make the positive H2 controls and negative SD/CelebA img2img gate read as one coherent short-paper result. | Adding new H2 sweeps, calling same-family transfer cross-model transfer, or forking LaTeX as a full paper. |
| Team C: Selected-Corpus Claim Support | Direction C selected-corpus measurement draft. | L0-L3 level definitions, stratum denominators, corpus inclusion and exclusion language. | Turn gate-summary counts into stratified results while preserving selected-corpus-only claims. | Reporting pooled rates, field-wide prevalence, independent inter-rater reliability, or paper-quality judgments. |
| Team D: Artifact Contract | Direction D artifact/demo/report-correctness draft. | Bundle/report threat model, public-safe risk-card language, and systems-promotion evidence rules. | Specify an artifact-contract paper that can stand before deployment claims exist. | Claiming drift reduction, external adoption, deployed enforcement, or product effectiveness without observed evidence. |

## Team D: Independent Artifact Contract and Consumer Boundary

| Field | Pitch |
| --- | --- |
| Title | An Artifact Contract for Safe Consumption of Diffusion Privacy Evidence |
| Venue fit | Artifact/demo track or software-engineering-for-ML venue now; applied systems only after fault-injection, report-drift, external-use, or deployment evidence exists. |
| Core thesis | Report consumers should not use diffusion MIA scores directly. They should consume machine-checkable evidence bundles that encode admission state, provenance, finite-tail semantics, and boundary language. Current evidence supports an independent artifact-contract/report-correctness package, not deployed enforcement, external adoption, or measured report-drift prevention. |
| Contribution claims | Bundle schema; admitted/candidate/support/blocked separation; public-surface guards; report-correctness threat model and planned fault-injection checks; public-safe risk-card language; blocked-promotion examples. |
| Minimum figures/tables | Contract architecture diagram; bundle schema table; admission-state state machine; drift/fault-injection table; public-safe risk-card example. |
| Additional work | Collect external or semi-external report usage, or run a fault-injection/report-drift evaluation showing that guardrails block candidate promotion and finite-tail miswording. |
| Fatal risks | Without fault-injection, external-use, deployment, or report-drift evidence, this reads as product documentation rather than a systems paper. |
| Overclaiming guard | Keep Platform/Runtime private topology, real domains, SSH aliases, secrets, and local machine paths out of public text. |
