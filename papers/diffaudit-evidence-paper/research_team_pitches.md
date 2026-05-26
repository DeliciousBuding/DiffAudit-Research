# Research Team Pitches

> Date: 2026-05-26
> Scope: persistent paper-team planning notes for the A-D manuscript directions.

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
| Title | Output-Cloud Geometry in a Controlled H2 Diffusion Response Family |
| Venue fit | Strong privacy/ML security workshop or short paper candidate; full CCF-B paper only if a second independent response asset appears. |
| Scientific question | Does the audited H2 repeated-response cache expose membership through geometry among repeated outputs, rather than only through query-to-output or seed-to-output distance? |
| Contribution claims | Output-output geometry as an operationally separated H2 observable relative to tested raw/lowpass baselines; strong H2 DDPM/CIFAR10 signal; label-shuffle and shared-position controls; same-family cross-cache stability; negative SD/CelebA img2img portability boundary. |
| Figures/tables | Response-cloud method schematic; H2 vs raw/lowpass table; controls table; feature-family/coefficient view; img2img portability table; boundary diagram. |
| Additional bounded experiments | Independent second public response asset; pre-registered interleaved cache-generation protocol; mechanism-focused repeat-count sensitivity; transparent few-feature scorer; extra negative-control split. |
| Fatal risks | Strong evidence remains one H2 response-cache family; img2img portability is weak; logistic fusion may look like feature engineering. |
| Safe claim | Output-output response-cloud geometry is a strong controlled Research-side H2 observable relative to tested H2 baselines, with unresolved and partly negative portability. Cross-cache transfer is same-family robustness, not cross-model or cross-dataset transfer. |

### Team B LaTeX Fork Gate

Fork a standalone TeX draft only if either a second independent response asset
passes the six-gate contract, or the paper is explicitly scoped as a
short/workshop mechanism case study with the SD/CelebA img2img portability
failure as a central result. Do not fork for more H2 feature sweeps, `512/512`
symmetry reruns, repeat-count tuning, KDE variants, or input-distance fusion.

## Team C: Selected-Corpus Artifact Claim Support

| Field | Pitch |
| --- | --- |
| Title | When Diffusion MIA Scores Are Not Audit Evidence: A Selected-Corpus Claim-Support Study |
| Venue fit | MLSys, SaTML, FAccT methods track, or measurement workshop; reproducibility venues only if replay rows are separated from metadata-only rows. |
| Core thesis | In a frozen selected corpus, diffusion MIA artifact surfaces support different claim levels: metadata inspection, scoreability, replay, auditability, and consumer-safe reporting. |
| Contribution claims | Six-gate second-asset contract; selected-corpus claim-support audit across CLiD, Tracing Roots, ReDiffuse, CommonCanvas, MIDST, Stable Diffusion ReDiffuse, and fixed GitHub/arXiv search records; taxonomy of support states; negative results as exclusion evidence. |
| Figures/tables | Six-gate candidate matrix; result matrix; selected-corpus gate-summary figure; artifact funnel from paper claim to reusable evidence; signal-strength vs artifact-completeness map. |
| Lightweight additional work | Use the 21-row v1 corpus, the 2026-05-26 fixed-search batch, generated gate-summary counts, and the completed selected-corpus consistency pass. Add one broader fixed-source pass or a second independent label review only for a standalone submission. |
| Fatal risks | Looks anecdotal unless candidate inclusion is preregistered; metadata-only rows can be mistaken for reproductions; mixed strata can create false equivalence. |
| Framing rule | Do not say papers fail. Say we measure what survives reusable, row-bound, low-FPR, consumer-safe constraints. |

## Portfolio Decision

The current primary manuscript should remain Team A's evidence-contracted
measurement paper. It can incorporate Team B as a technical case study and Team
C as its broader claim-support motivation and selected-corpus gate summary.
Team B becomes the next technical paper if a second response asset is acquired
or if the scope is explicitly a short H2 case study. Team C becomes a standalone
measurement paper only if the selected corpus grows or receives a second
independent label review without field-wide overclaiming.

## Team D: Artifact Contract and Consumer Boundary

| Field | Pitch |
| --- | --- |
| Title | An Artifact Contract for Safe Consumption of Diffusion Privacy Evidence |
| Venue fit | Artifact/demo track or software-engineering-for-ML venue now; applied systems only after fault-injection, report-drift, external-use, or deployment evidence exists. |
| Core thesis | Report consumers should not use diffusion MIA scores directly. They should consume machine-checkable evidence bundles that encode admission state, provenance, finite-tail semantics, and boundary language. Current evidence supports encoding and validation, not deployed enforcement. |
| Contribution claims | Bundle schema; admitted/candidate/support/blocked separation; public-surface guards; report-correctness threat model and planned fault-injection checks; public-safe risk-card language; blocked-promotion examples. |
| Minimum figures/tables | Contract architecture diagram; bundle schema table; admission-state state machine; drift/fault-injection table; public-safe risk-card example. |
| Additional work | Collect external or semi-external report usage, or run a fault-injection/report-drift evaluation showing that guardrails block candidate promotion and finite-tail miswording. |
| Fatal risks | Without fault-injection, external-use, deployment, or report-drift evidence, this reads as product documentation rather than a systems paper. |
| Overclaiming guard | Keep Platform/Runtime private topology, real domains, SSH aliases, secrets, and local machine paths out of public text. |
