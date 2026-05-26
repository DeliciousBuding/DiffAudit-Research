# DiffAudit Paper Portfolio

> Date: 2026-05-26
> Goal: turn current Research evidence into publishable, academically honest paper tracks.

## Shared Rule

All paper tracks share the same evidence bank. A result may be promoted in text
only if its source artifact proves target identity, split semantics, score or
response coverage, metric provenance, consumer boundary, and surface delta.
Candidate results must stay candidate. Weak results are valuable only when they
rule out a plausible route or motivate a sharper research question.

## Direction A: Evidence-Contracted Auditing

| Field | Plan |
| --- | --- |
| Working title | DiffAudit: Evidence-Contracted Membership Leakage Auditing for Diffusion Models |
| Team | Evidence Contract Team: methodology lead for thesis and venue framing, metric audit lead for admitted-row checks, visual editor for figure readability and claim separation |
| Venue fit | Security/privacy measurement, applied ML security, CCF-B+ systems/security/privacy track |
| Thesis | Diffusion membership auditing needs evidence contracts, not only high AUC. Binding each claim to target identity, split, score/response coverage, metrics, provenance, and consumer boundary separates deployable evidence from attractive but non-consumable signals. |
| Core contributions | Evidence contract and admitted/candidate/watch taxonomy; a five-row admitted cross-permission evidence bundle; H2 output-cloud geometry as a controlled candidate case study; a negative evidence map showing why second-asset claims are hard. |
| Main figures | Evidence-contract pipeline; admitted bundle metric/cost chart; H2 control chart; second-asset gate matrix. |
| Status | Primary track for the first LaTeX draft. |
| Risk | Reviewers may see it as engineering governance unless the paper frames contracts as a measurement methodology and uses H2 plus negative gates as scientific evidence. |

## Direction B: Response-Cloud Geometry and Portability Boundary

| Field | Plan |
| --- | --- |
| Working title | Response-Cloud Geometry Has an H2 Membership Signal, But Does Not Port to Img2img |
| Team | Response Geometry Team: mechanism lead for hypothesis and validity threats, scorer lead for bounded controls, visual editor for response-cloud explanation |
| Venue fit | ML security workshop or short paper now; full CCF-B only if a second independent response asset appears |
| Thesis | The audited H2 repeated-response cache contains an operationally distinct output-output geometry signal relative to the tested raw/lowpass H2 distance baselines, and the negative SD/CelebA img2img portability result is the central boundary result rather than a caveat. |
| Core contributions | H2-only output-cloud observable; label-shuffle sanity; shared-position order-control; seed-stability and same-family cross-cache transfer; img2img portability failure as a central boundary result. |
| Main figures | Feature schematic; raw/lowpass/output-cloud comparison; seed/control/label-shuffle bars; portability failure panel. |
| Extra work needed | A second independent image-diffusion asset or a stronger non-H2 response contract. Without that, write it only as a mechanism short paper with portability failure central. |
| Risk | Single-family H2 evidence and weak img2img portability make this hard to defend as a full paper alone. |

## Direction C: Selected-Corpus Artifact Claim-Support Measurement

| Field | Plan |
| --- | --- |
| Working title | From Artifact Surfaces to Audit Claims: A Selected-Corpus Measurement of Diffusion MIA Claim Support |
| Team | Artifact Claim-Support Team: measurement lead for gate design, artifact audit lead for metadata and replay checks, table lead for taxonomy and figures |
| Venue fit | Security/privacy measurement, ML systems workshop, or reproducibility venue only if L0 metadata, L1 inspection, L2 scoreable/replay, feature-packet, source-confounded, and L3 admitted-control rows are separated; CCF-B possible only with broader frozen source pass or second independent label review |
| Thesis | In a frozen selected corpus, diffusion MIA artifact surfaces support different L0-L3 claim levels: metadata discovery, artifact inspection, bounded score/replay, audit-ready evidence, and consumer-safe reporting. |
| Core contributions | L0-L3 claim-support levels; six-gate second-asset contract; audited candidate corpus; bounded replays, weak scouts, feature packets, score-artifact gates, and collaborator/local stress tests across ReDiffuse, CommonCanvas, MIDST, Tracing Roots, CopyMark, and collaborator SD ReDiffuse; stop rules preventing low-information sweeps and pooled false denominators. |
| Main figures | Selected-corpus gate heatmap; claim-support ladder; stratified artifact table; weak-signal scatter; source-confounding example. |
| Extra work needed | Selected-corpus gate-label consistency now passes with no invalid gate values, contradictions, or label promotions; four empty-result `delta_gate` labels were demoted from `Partial` to `Fail`. Add one broader fixed-source pass or a second independent label review only if targeting standalone aggregate claims; never pool metadata-only rows with replay rows. |
| Risk | Needs careful methodology to avoid appearing as anecdotal project notes or field-wide prevalence claims. |

## Direction D: Independent Artifact Contract and Consumer Boundary

| Field | Plan |
| --- | --- |
| Working title | An Artifact Contract for Safe Consumption of Diffusion Privacy Evidence |
| Team | Artifact Contract Team: systems lead for architecture and threat model, contract lead for bundle validation, report lead for consumer-facing diagrams |
| Venue fit | Independent artifact-contract/demo/report-correctness package now; applied systems only after fault-injection, report-drift, external-use, or deployment evidence |
| Thesis | Privacy audit outputs should be consumed through machine-checkable bundles that encode admission state, boundary language, finite-tail interpretation, and provenance constraints; current evidence supports an independent artifact-contract package, not deployed enforcement, external adoption, or measured report-drift prevention. |
| Core contributions | Admitted evidence bundle schema; public-surface checks; finite empirical tail semantics; report-correctness threat model and validation hooks; blocked-promotion examples. |
| Main figures | Artifact-contract architecture; bundle schema; admission-state machine; fault-injection table; public-safe risk card. |
| Extra work needed | Fault-injection/report-drift evidence, external adopter scenario, public-safe deployment evidence, or user-study evidence before systems-paper promotion. |
| Risk | Too product/system oriented for a mainline research venue unless tied tightly to measurable report correctness. |

## Immediate Choice

Direction A is the best first manuscript because it can honestly absorb all
current evidence without overclaiming. Direction B is the sharpest technical
short-paper candidate: an H2-only response-cloud observable plus a negative
img2img portability gate. Direction C now has a v1 corpus, a fixed GitHub/arXiv
metadata batch, selected-corpus gate-summary outputs, and a selected-corpus
consistency pass with only four empty-result `delta_gate` demotions, but
standalone aggregate claims still need a broader frozen corpus or second label
review and stratified denominators. Direction D is best as an artifact/demo or
report-correctness package after Direction A defines the scientific contract,
and it needs fault-injection, report-drift, external-use, or deployment evidence
before becoming a full systems paper.

## Version Briefs

The direction-specific writing briefs are now the active comparison layer:

| Version | Brief |
| --- | --- |
| A | [`versions/direction-a-evidence-contract.md`](versions/direction-a-evidence-contract.md) |
| B | [`versions/direction-b-output-cloud-geometry.md`](versions/direction-b-output-cloud-geometry.md) |
| C | [`versions/direction-c-artifact-reproducibility.md`](versions/direction-c-artifact-reproducibility.md) |
| C corpus | [`versions/direction-c-corpus-protocol.md`](versions/direction-c-corpus-protocol.md) |
| C fixed search | [`versions/direction-c-fixed-search-batch-20260526.md`](versions/direction-c-fixed-search-batch-20260526.md) |
| D | [`versions/direction-d-audit-systems.md`](versions/direction-d-audit-systems.md) |

The fuller manuscript-level drafts are indexed at
[`multi_direction_paper_drafts.md`](multi_direction_paper_drafts.md) and live
under [`versions/drafts/`](versions/drafts/). They intentionally stay in
Markdown until a direction passes its go/no-go gate; only Direction A currently
owns the LaTeX manuscript.

Do not fork four independent evidence registers. All versions must keep using
`source_map.md`, `claim_register.md`, and `evidence_bank.md`.
