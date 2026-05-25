# DiffAudit Paper Portfolio

> Date: 2026-05-26
> Goal: turn current Research evidence into publishable, academically honest paper tracks.

## Shared Rule

All paper tracks share the same evidence bank. A result may be promoted in text
only if its source artifact proves target identity, split semantics, score or
response coverage, metric provenance, and boundary language. Candidate results
must stay candidate. Weak results are valuable only when they rule out a
plausible route or motivate a sharper research question.

## Direction A: Evidence-Contracted Auditing

| Field | Plan |
| --- | --- |
| Working title | DiffAudit: Evidence-Contracted Membership Leakage Auditing for Diffusion Models |
| Team | Framework team: opus lead for thesis/structure, haiku for metric extraction checks, sonnet for figure readability and paper polish |
| Venue fit | Security/privacy measurement, applied ML security, CCF-B+ systems/security/privacy track |
| Thesis | Diffusion membership auditing needs evidence contracts, not only high AUC. Binding each claim to target identity, split, score/response coverage, metrics, provenance, and consumer boundary separates deployable evidence from attractive but non-consumable signals. |
| Core contributions | Evidence contract and admitted/candidate/watch taxonomy; a five-row admitted cross-permission evidence bundle; H2 output-cloud geometry as a controlled candidate case study; a negative evidence map showing why second-asset claims are hard. |
| Main figures | Evidence-contract pipeline; admitted bundle metric/cost chart; H2 control chart; second-asset gate matrix. |
| Status | Primary track for the first LaTeX draft. |
| Risk | Reviewers may see it as engineering governance unless the paper frames contracts as a measurement methodology and uses H2 plus negative gates as scientific evidence. |

## Direction B: Output-Cloud Geometry Mechanism

| Field | Plan |
| --- | --- |
| Working title | Output-Cloud Geometry in a Controlled H2 Diffusion Response Family |
| Team | Mechanism team: opus for hypothesis and validity threats, haiku for bounded scorer/control scripts, sonnet for visual explanation of response-cloud features |
| Venue fit | ML security workshop or short paper now; full CCF-B only if a second independent response asset appears |
| Thesis | The audited H2 repeated-response cache contains output-output geometric signatures that are not reducible to seed-to-output distance, and these signatures survive same-family seed-offset controls. |
| Core contributions | Output-cloud feature family; label-shuffle sanity; shared-position order-control; seed-stability and cross-cache transfer; img2img portability failure as a boundary result. |
| Main figures | Feature schematic; raw/lowpass/output-cloud comparison; seed/control/label-shuffle bars; portability failure panel. |
| Extra work needed | A second independent image-diffusion asset or a stronger non-H2 response contract. Without that, write it only as a mechanism short paper with portability failure central. |
| Risk | Single-family H2 evidence and weak img2img portability make this hard to defend as a full paper alone. |

## Direction C: Public Artifact Reproducibility and Claim Support

| Field | Plan |
| --- | --- |
| Working title | When Diffusion MIA Scores Are Not Audit Evidence: A Claim-Support Study of Public Artifacts |
| Team | Reproducibility team: opus for gate design, haiku for metadata/replay scripts, sonnet for candidate taxonomy and tables |
| Venue fit | Security/privacy measurement, reproducibility/replicability, ML systems workshop; CCF-B possible if artifact corpus is expanded and preregistered |
| Thesis | Public diffusion MIA artifacts often support some research claim, but not necessarily a portable, row-bound, consumer-safe audit claim. The paper measures artifact availability, scoreability, reproducibility, and auditability as distinct states. |
| Core contributions | Six-gate second-asset contract; audited candidate corpus; bounded replays/scouts for ReDiffuse, CommonCanvas, MIDST, Tracing Roots, CopyMark, and collaborator SD ReDiffuse; stop rules preventing low-information sweeps. |
| Main figures | Candidate gate heatmap; weak-signal scatter; source-confounding example; artifact availability taxonomy. |
| Extra work needed | Run gate-label consistency review over the 21-row v1 corpus plus the 2026-05-26 fixed-search batch; add one broader fixed-source pass only if targeting a standalone reproducibility paper. |
| Risk | Needs careful methodology to avoid appearing as anecdotal project notes or field-wide prevalence claims. |

## Direction D: Consumer-Boundary Systems Paper

| Field | Plan |
| --- | --- |
| Working title | From Membership Scores to Auditable Evidence: A Runtime Contract for Diffusion Privacy Reports |
| Team | Systems team: opus for architecture and threat model, haiku for bundle/export validation, sonnet for report/UI diagrams |
| Venue fit | Applied systems/security demo, artifact track, software engineering for ML; less likely as pure CCF-B research without user study or deployment evaluation |
| Thesis | Privacy audit outputs should be consumed only through machine-checkable bundles with boundary language, finite-tail interpretation, and provenance constraints. |
| Core contributions | Admitted evidence bundle schema; public-surface checks; finite empirical tail semantics; Platform/Runtime bridge; drift/audit validation. |
| Main figures | Bundle schema; pipeline from experiment to runtime report; consumer drift checks; example risk card. |
| Extra work needed | Deployment/user-study evidence, external adopter scenario, or report-drift/fault-injection evidence. |
| Risk | Too product/system oriented for a mainline research venue unless tied tightly to measurement correctness. |

## Immediate Choice

Direction A is the best first manuscript because it can honestly absorb all
current evidence without overclaiming. Direction B is the strongest technical
mechanism but needs a second asset or explicit short-paper scope. Direction C
now has a fixed-search batch, but still needs gate-label consistency before
standalone aggregate claims. Direction D is best as an artifact/demo paper
after Direction A defines the scientific contract and report-drift or
external-use evidence exists.

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
