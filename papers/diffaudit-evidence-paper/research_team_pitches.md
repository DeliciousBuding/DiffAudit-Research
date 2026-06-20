# Research Team Pitches

> Date: 2026-06-09
> Scope: persistent paper-team planning notes for the A-D manuscript directions.

## Portfolio Operating Rule

The four teams may produce different paper versions under one evidence ledger
plus the generated claim-trace/provenance tables. A team may change framing,
section order, figures, venue posture, and reviewer argument. Candidate
promotion, private claim registers, and symmetric model/data execution stay
outside this portfolio pass.
The expected output before a TeX fork is a readable paper version: title,
abstract, controlling thesis, contribution claims, section spine, figure/table
plan, review risks, and a go/no-go gate.

The canonical team/version operating board is `versions/README.md`. This file is
a pitch book; if a mandate or gate differs, `versions/README.md` wins.

## 2026-05-27 Multi-Team Assignment

The portfolio can generate several paper versions. Teams compete on thesis
quality and evidence discipline. Extra scaffolding does not count as progress.
The current assignment is:

| Track | Team | Version to write | Decision authority |
| --- | --- | --- | --- |
| A | Evidence Contract Team | Full security/privacy measurement paper. | Owns the active LaTeX draft and final claim boundary. |
| B | Response Geometry Team | H2-limited short/workshop paper. | May request a TeX fork only for an explicitly scoped short paper or after a second response asset passes gates. |
| C | Artifact Claim-Support Team | Measurement paper over frozen selected artifacts. | Aggregate results require stratified denominators; broader claims need a larger distinct-surface corpus, and reliability/adjudication claims need external label audit. |
| D | Artifact Contract Team | Artifact/demo/report-correctness paper. | Generated risk-card and selected fault-injection blocking support artifact/demo claims; systems effectiveness needs report-drift, external-use, or deployment evidence. |

This cycle uses four teams. The current negative/support candidates fit as
boundary evidence inside A/C or as gates for B/D.

Continuation review outcome: Team A is the full-paper track with CCF-B-style
measurement-paper potential. Current submission strength depends on external
C14 labels, a larger distinct-surface corpus, or a second row-bound
score/response asset. Team B is a valid independent short/workshop track only as H2
response-cloud geometry plus failed img2img portability. Team C is a technical
report or scoped measurement note unless a larger distinct-surface corpus or
external label audit is added. Team D is an artifact/demo report-correctness
note until report-renderer drift, external-use, or public-safe demo/deployment
evidence exists. The `21`, `17`, and `10` Direction C denominators stay
separate; report them as stratified counts.

## Team A: Evidence-Contracted Measurement

| Field | Pitch |
| --- | --- |
| Title | When Do Diffusion Membership-Inference Scores Become Audit Evidence? An Evidence-Contracted Measurement Study |
| Venue fit | RAID or ACSAC as CCF-B security venues; IMC as measurement-style secondary target if the corpus is expanded. |
| Core thesis | Diffusion-model privacy auditing is bottlenecked by unauditable evidence. In the selected artifacts audited here, many attractive claims lack fixed target identity, exact member/nonmember splits, row-level scores, finite-tail interpretation, or consumer-boundary provenance. |
| Contribution claims | Audit evidence contract; taxonomy of verified/candidate/watch/blocked evidence; reportable black/gray/white-box rows with replay/source tiers; explicit separation and claim-register blocking language for high-scoring but unsafe candidates. Report-correctness fault injection belongs to Team D and currently supports artifact/demo packaging. |
| Minimum figures/tables | Evidence-gate table; reportable-vs-candidate table; audit pipeline figure; selected-corpus gate-summary text summary or support figure; boundary-case comparison with non-admitted labels. |
| Additional work | Lightweight measurement only: use the existing selected v1 corpus and the 2026-05-26 fixed-search metadata batch, report stratified gate counts only within those frozen denominators, recompute stored metric tables, and ensure every plotted point has row-level evidence or source-documented point-estimate provenance. |
| Fatal risks | Looks like internal governance unless artifact-readiness measurement is quantified; admitted rows remain narrow; restricted/non-redistributable evidence may be challenged. |
| Overclaiming guard | Claim auditability and evidence calibration. Keep SOTA attack performance out of the contribution frame; separate admitted/candidate/watch rows and report finite-tail denominators. |

## Team B: Response-Cloud Observable

| Field | Pitch |
| --- | --- |
| Title | H2-Only Response-Cloud Geometry and the Failed Img2img Portability Gate |
| Venue fit | Strong privacy/ML security workshop or short paper candidate; full CCF-B response-observable paper only if a second independent response asset appears. |
| Scientific question | Does the audited H2 repeated-response cache expose membership through geometry among repeated outputs beyond query-to-output or seed-to-output distance? |
| Contribution claims | Output-output geometry as an operationally separated H2 observable relative to tested raw/lowpass baselines; strong H2 DDPM/CIFAR10 signal; label-shuffle and shared-position controls; same-family cache robustness; negative SD/CelebA img2img portability boundary. |
| Figures/tables | Response-cloud method schematic; H2 vs raw/lowpass table; controls table; feature-family/coefficient view; img2img portability table; boundary diagram. |
| Additional bounded experiments | H2 polishing is closed by default. A second public response asset and pre-registered interleaved cache-generation protocol are the experiments that can change full-paper viability. |
| Fatal risks | Strong evidence remains one H2 response-cache family; img2img portability is weak; logistic fusion may look like feature engineering. |
| Safe claim | Output-output response-cloud geometry is a strong controlled Research-side H2 observable relative to tested H2 baselines, with unresolved and partly negative portability. Same-family cache robustness stays within the tested model/dataset family. |

### Team B LaTeX Fork Gate

Fork a standalone TeX draft after a second independent response asset passes
the six-gate contract, or after the scope is fixed as a short/workshop
observable study centered on the SD/CelebA img2img portability failure. Closed
items: H2 feature sweeps, `512/512` symmetry reruns, repeat-count tuning, KDE
variants, and input-distance fusion.

## Team C: Selected-Corpus Artifact Claim-Support Measurement

| Field | Pitch |
| --- | --- |
| Title | From Artifact Surfaces to Audit Claims: A Selected-Corpus Measurement of Diffusion MIA Claim Support |
| Venue fit | MLSys, SaTML, FAccT methods track, or measurement workshop; reproducibility venues only if L0 metadata, L1 inspection, L2 scoreable/replayed, feature-packet, source-confounded, and L3 admitted-control rows are separated. |
| Core thesis | In a frozen selected corpus, diffusion MIA artifact surfaces support different L0-L3 claim levels: metadata discovery, artifact inspection, bounded score/replay, consumer-admitted evidence, and consumer-boundary reporting. |
| Contribution claims | L0-L3 claim-support levels; six-gate second-asset contract; selected-corpus claim-support audit across CLiD, Tracing Roots, ReDiffuse, CommonCanvas, MIDST, Stable Diffusion ReDiffuse, fixed GitHub/arXiv search records, and three targeted L1 artifact-link seeds; taxonomy of support states; weak results as tested-route exclusions only. |
| Figures/tables | Claim-support ladder; stratified six-gate matrix; selected-corpus gate-summary figure or compact text summary; artifact funnel from paper claim to reusable evidence; signal-strength vs artifact-completeness map. |
| Lightweight additional work | Use the 21-row v1 corpus, the 2026-05-26 fixed-search batch, the 2026-05-27 HF/Zenodo/OpenReview broader-source API pass, the three targeted L1 artifact-link seeds, generated gate-summary counts, completed selected-corpus consistency pass, and bounded second-pass label-hygiene review/resolution with stratified denominators. Standalone aggregate claims need a larger distinct-surface corpus. Reliability/adjudication claims need external label audit; same-team checks remain label hygiene. |
| Fatal risks | Looks anecdotal unless candidate inclusion is preregistered; metadata-only rows can be mistaken for reproductions; mixed strata can create false equivalence. |
| Framing rule | Use this framing: the paper measures which claim level survives reusable, row-bound, low-FPR, consumer-boundary constraints. Metadata-only and replay rows stay separate; weak scouts are route-local checks. |

## Portfolio Decision

The current primary manuscript remains Team A's evidence-contracted measurement
paper. It can incorporate Team B as a technical negative-control section and
Team C as broader claim-support motivation plus selected-corpus gate summary.
Team B becomes the next technical paper after a second response asset or a fixed
short-paper scope around H2 observables and portability failure. Team C becomes
a standalone measurement paper after distinct artifact-surface growth or
external label audit, with stratified denominators preserved.

## Execution Board Pointer

Use `versions/README.md` for the active multi-team execution board. Keeping one
board avoids drift between pitch language, promotion gates, and stop rules.

## Team D: Independent Artifact Contract and Consumer Boundary

| Field | Pitch |
| --- | --- |
| Title | An Artifact Contract for Safe Consumption of Diffusion Privacy Evidence |
| Venue fit | Artifact/demo track or software-engineering-for-ML venue now; applied systems only after report-drift, external-use, or deployment evidence exists. |
| Core thesis | Report consumers need machine-checkable evidence bundles that encode admission state, provenance, finite-tail semantics, and boundary language. Current evidence supports an independent artifact-contract/report-correctness package. Deployed enforcement, external adoption, and measured report-drift prevention remain future evidence gates. |
| Contribution claims | Bundle schema; admitted/candidate/support/blocked separation; generated public-safe risk-card renderer; public-surface and candidate-promotion language guards; report-correctness threat model; observed bundle-level and risk-card fault-injection checks using existing bundle/check paths; blocked-promotion examples. |
| Minimum figures/tables | Contract architecture diagram; bundle schema table; admission-state state machine; drift/fault-injection table; public-safe risk-card example. |
| Additional work | Collect external or semi-external report usage, or run a report-drift A/B evaluation showing fewer unsupported claims under the generated risk-card path. |
| Fatal risks | Systems-paper framing needs report-drift, external-use, or deployment evidence; the current package reads as artifact documentation. |
| Overclaiming guard | Keep Platform/Runtime private topology, real domains, SSH aliases, secrets, and local machine paths out of public text. |
