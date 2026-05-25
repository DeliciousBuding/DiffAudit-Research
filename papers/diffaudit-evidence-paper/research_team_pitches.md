# Research Team Pitches

> Date: 2026-05-26
> Scope: read-only subagent reviews converted into persistent paper planning notes.

## Team A: Evidence-Calibrated Measurement

| Field | Pitch |
| --- | --- |
| Title | DiffAudit: Evidence-Calibrated Measurement for Auditing Membership Leakage in Diffusion Models |
| Venue fit | RAID or ACSAC as CCF-B security venues; IMC as measurement-style secondary target if the corpus is expanded. |
| Core thesis | Diffusion-model privacy auditing is bottlenecked less by missing attacks than by unauditable evidence. Public claims often lack fixed target identity, exact member/nonmember splits, row-level scores, finite-tail interpretation, or consumer-safe provenance. |
| Contribution claims | Audit evidence contract; taxonomy of verified/candidate/watch/blocked evidence; admitted black/gray/white-box rows; explicit prevention of high-scoring but unsafe candidates becoming headline claims. |
| Minimum figures/tables | Evidence-gate table; admitted-vs-candidate table; audit pipeline figure; artifact-readiness funnel; case-study comparison with non-admitted labels. |
| Additional work | Lightweight measurement only: freeze candidate corpus, count gate-failure modes, recompute stored metric tables, and ensure every plotted point has row-level evidence. |
| Fatal risks | Looks like internal governance unless artifact-readiness measurement is quantified; admitted rows remain narrow; local-only evidence may be challenged. |
| Overclaiming guard | Claim auditability and evidence calibration, not SOTA attack performance. Always separate admitted/candidate/watch rows and report finite-tail denominators. |

## Team B: Output-Cloud Mechanism

| Field | Pitch |
| --- | --- |
| Title | Output Clouds Remember: Membership Signals in Diffusion Response Geometry |
| Venue fit | Strong privacy/ML security workshop or short paper candidate; full CCF-B paper only if a second independent response asset appears. |
| Scientific question | Do diffusion models leak membership through geometry among repeated outputs, rather than only through query-to-output or seed-to-output distance? |
| Contribution claims | Output-output geometry observable; strong H2 DDPM/CIFAR10 signal; label-shuffle and shared-position controls; seed/cache transfer stability; negative SD/CelebA img2img portability boundary. |
| Figures/tables | Response-cloud method schematic; H2 vs raw/lowpass table; controls table; feature-family/coefficient view; img2img portability table; boundary diagram. |
| Additional bounded experiments | Independent second public response asset; pre-registered interleaved cache-generation protocol; mechanism-focused repeat-count sensitivity; transparent few-feature scorer; extra negative-control split. |
| Fatal risks | Strong evidence remains one H2 response-cache family; img2img portability is weak; logistic fusion may look like feature engineering. |
| Safe claim | Output-output response-cloud geometry is a strong controlled Research-side H2 observable with unresolved and partly negative portability. Cross-cache transfer is same-family robustness, not cross-model or cross-dataset transfer. |

### Team B LaTeX Fork Gate

Fork a standalone TeX draft only if either a second independent response asset
passes the six-gate contract, or the paper is explicitly scoped as a
short/workshop mechanism case study with the SD/CelebA img2img portability
failure as a central result. Do not fork for more H2 feature sweeps, `512/512`
symmetry reruns, repeat-count tuning, KDE variants, or input-distance fusion.

## Team C: Reproducibility and Claim Support

| Field | Pitch |
| --- | --- |
| Title | When Diffusion MIA Scores Are Not Audit Evidence: A Claim-Support Study of Public Artifacts |
| Venue fit | MLSys, NeurIPS Datasets and Benchmarks, SaTML, FAccT methods track; not a new attack paper. |
| Core thesis | Public diffusion MIA artifacts often support some research claim, but not necessarily a portable, row-bound, consumer-safe audit claim. Artifact availability, scoreability, reproducibility, and auditability must be measured separately. |
| Contribution claims | Six-gate second-asset contract; measurement audit across CLiD, Tracing Roots, ReDiffuse, CommonCanvas, MIDST, and Stable Diffusion ReDiffuse; taxonomy of failure modes; negative results as exclusion evidence. |
| Figures/tables | Six-gate candidate matrix; result matrix; artifact funnel from paper claim to reusable evidence; signal-strength vs artifact-completeness map. |
| Lightweight additional work | Freeze search window, sources, keywords, and artifact strata; add 10-20 metadata-only public surfaces; then build gate matrix, checksum/URL table, row-binding audit table, and low-FPR denominator audit. |
| Fatal risks | Looks anecdotal unless candidate inclusion is preregistered; reviewers may ask for new SOTA performance; negative set can appear cherry-picked. |
| Framing rule | Do not say papers fail. Say we measure what survives reusable, row-bound, low-FPR, consumer-safe constraints. |

## Portfolio Decision

The current primary manuscript should remain Team A's evidence-calibrated
measurement paper. It can incorporate Team B as a technical case study and Team
C as its broader reproducibility motivation. Team B becomes the next technical
paper if a second response asset is acquired. Team C becomes a standalone
measurement paper if the artifact corpus is frozen and expanded beyond current
project history.
