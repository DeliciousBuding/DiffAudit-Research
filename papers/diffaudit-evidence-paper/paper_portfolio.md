# DiffAudit Paper Portfolio

> Date: 2026-06-09
> Goal: turn current DiffAudit evidence into publishable, academically honest paper tracks.

## Shared Rule

All paper tracks share the same evidence bank. A result may be promoted in text
only if its source artifact proves target identity, split semantics, score or
response coverage, metric provenance, consumer boundary, and surface delta.
Candidate results must stay candidate. Weak results are valuable only when they
rule out a plausible route or motivate a sharper research question.

`versions/README.md` is the canonical version/team operating board. This file
is a portfolio summary; promotion gates and team mandates stay in the board.

## Direction A: Evidence-Contracted Measurement

| Field | Plan |
| --- | --- |
| Working title | When Do Diffusion Membership-Inference Scores Become Audit Evidence? An Evidence-Contracted Measurement Study |
| Team | Evidence Contract Team: methodology lead for thesis and venue framing, metric audit lead for reportable-row replay-tier and provenance checks, visual editor for figure readability and claim separation |
| Venue fit | Security/privacy measurement or applied ML security venue. CCF-B full-paper posture needs stronger reviewer-facing measurement-method framing. |
| Thesis | Diffusion membership auditing needs evidence contracts. Binding each claim to target identity, split, score/response coverage, metrics, provenance, and consumer boundary separates reusable audit evidence from attractive high-AUC signals that lack audit use. |
| Core contributions | Evidence contract and reportable/candidate/watch taxonomy; a five-row role-separated reportable bundle with replay/source tiers; H2 output-cloud geometry as a failed-admission stress test; a negative evidence map showing why second-asset claims are hard. |
| Main figures | Evidence-contract pipeline; reportable bundle metric/cost chart with replay-tier and point-estimate markers; H2 control chart; second-asset gate matrix. |
| Status | Primary 10-page LaTeX draft. Current release gates pass; submission strength still depends on external C14 labels, a larger distinct-surface corpus, or a second row-bound score/response asset. |
| Risk | Reviewer-facing text must foreground measurement methodology, with H2 and negative gates used as scientific stress tests. |

## Direction B: Response-Cloud Geometry and Portability Boundary

| Field | Plan |
| --- | --- |
| Working title | H2-Only Response-Cloud Geometry and the Failed Img2img Portability Gate |
| Team | Response Geometry Team: observable lead for hypothesis and validity threats, scorer lead for bounded controls, visual editor for response-cloud explanation |
| Venue fit | ML security workshop or short paper now; full CCF-B only if a second independent response asset appears |
| Thesis | The audited H2 repeated-response cache contains an operationally distinct output-output geometry signal relative to the tested raw/lowpass H2 distance baselines. The negative SD/CelebA img2img portability result defines the paper boundary. |
| Core contributions | H2-only output-cloud observable; label-shuffle sanity; shared-position order-control; seed-stability and same-family cache robustness; img2img portability failure as a central boundary result. |
| Main figures | Response-cloud schematic; raw/lowpass/output-cloud comparison; seed/control/label-shuffle bars; portability failure panel. |
| Extra work needed | A second independent image-diffusion asset or a stronger non-H2 response contract. The current evidence supports an observable short paper centered on portability failure. |
| Risk | Single-family H2 evidence and weak img2img portability make this hard to defend as a full paper alone. |

## Direction C: Selected-Corpus Artifact Claim-Support Measurement

| Field | Plan |
| --- | --- |
| Working title | From Artifact Surfaces to Audit Claims: A Selected-Corpus Measurement of Diffusion MIA Claim Support |
| Team | Artifact Claim-Support Team: measurement lead for gate design, artifact audit lead for metadata and replay checks, table lead for taxonomy and figures |
| Venue fit | Security/privacy measurement, ML systems workshop, or reproducibility venue with separated L0 metadata, L1 inspection, L2 scoreable/replay, feature-packet, source-confounded, and L3 admitted-control rows. CCF-B posture needs a larger distinct-surface corpus; reliability/adjudication claims require external label audit. |
| Thesis | In a frozen selected corpus, diffusion MIA artifact surfaces support different L0-L3 claim levels: metadata discovery, artifact inspection, bounded score/replay, admitted-control evidence, and consumer-boundary reporting. |
| Core contributions | L0-L3 claim-support levels; six-gate second-asset contract; selected-corpus claim-support audit across three non-poolable strata: the 21-row v1 evidence-note corpus, the 2026-05-26 GitHub/arXiv fixed-search metadata batch, and the 2026-05-27 HF/Zenodo/OpenReview broader-source API pass. Three targeted L1 artifact-link seeds add one HF dataset, one official SecMI GitHub implementation/split tree, and one official MIDM code/protocol repository. Bounded replays, weak scouts, feature packets, score-artifact gates, and restricted/non-redistributable or source-confounded stress tests define the stop rules. |
| Main figures | Selected-corpus gate heatmap; claim-support ladder; stratified artifact table; weak-signal scatter; source-confounding example; generated claim-support summary figure. |
| Extra work needed | Current same-team checks support label hygiene: the consistency pass found no invalid gate values or route-changing contradictions, and the bounded second-pass review found no admitted-like fixed-search row or metadata-batch evidence/metric promotion. The 2026-05-27 broader-source API pass is metadata-screening/query hygiene with zero admitted rows; the targeted artifact-link pass adds three L1 artifact seeds with no score/metric replay. Standalone aggregate claims need a larger distinct-surface corpus. Reliability claims need external label audit. Metadata-only rows and replay rows remain separate. |
| Risk | Needs careful methodology to avoid appearing as anecdotal implementation notes or field-wide prevalence claims. |

## Direction D: Independent Artifact Contract and Consumer Boundary

| Field | Plan |
| --- | --- |
| Working title | An Artifact Contract for Safe Consumption of Diffusion Privacy Evidence |
| Team | Artifact Contract Team: systems lead for architecture and threat model, contract lead for bundle validation, report lead for consumer-facing diagrams |
| Venue fit | Independent artifact-contract/demo/report-correctness package now; applied systems only after report-drift, external-use, or deployment evidence |
| Thesis | Privacy audit outputs should be consumed through machine-checkable bundles that encode admission state, boundary language, finite-tail interpretation, and provenance constraints. Current evidence supports an independent artifact-contract package. Deployed enforcement, external adoption, and measured report-drift prevention remain future evidence gates. |
| Core contributions | Admission-state-aware reportable evidence bundle schema; generated public-safe risk-card renderer; public-surface and direct candidate-promotion language checks; finite empirical tail semantics; report-correctness threat model; existing bundle/export/public-surface hooks plus an observed selected-fault table; blocked-promotion examples. |
| Main figures | Artifact-contract architecture; bundle schema; admission-state machine; fault-injection table; public-safe risk card. |
| Extra work needed | Bundle-level fault-injection evidence now exists for candidate insertion, row removal, missing denominator, and source drift; risk-card renderer rejection now exists for candidate replacement and missing nonmember denominator; direct H2/Tracing Roots promotion language checks now cover the active manuscript and generated risk card; 2026-05-12 and 2026-05-15 consumer-boundary no-drift audits also exist. Systems-paper promotion still needs report-renderer A/B drift-reduction evidence, an external adopter scenario, public-safe deployment evidence, or user-study evidence. |
| Risk | Too product/system oriented for a mainline research venue unless tied tightly to measurable report correctness. |

## Immediate Choice

Direction A is the best first manuscript because it absorbs current evidence
inside one claim boundary. Direction B is the sharpest technical short-paper
candidate: an H2-only response-cloud observable plus a negative img2img
portability gate. Direction C has a v1 corpus, a fixed GitHub/arXiv metadata
batch, a HF/Zenodo/OpenReview broader-source API pass, selected-corpus
gate-summary outputs, and same-team label-hygiene checks. Standalone aggregate
claims need a larger distinct-surface corpus or external label audit with
stratified denominators. Direction D is best as an artifact/demo or
report-correctness package after Direction A defines the scientific contract;
full systems framing needs report-renderer A/B drift, external-use, or
deployment evidence.

## Version Briefs

The direction-specific writing briefs are now the active comparison layer:

| Version | Brief |
| --- | --- |
| A | [`versions/direction-a-evidence-contract.md`](versions/direction-a-evidence-contract.md) |
| B | [`versions/direction-b-output-cloud-geometry.md`](versions/direction-b-output-cloud-geometry.md) |
| C | [`versions/direction-c-artifact-reproducibility.md`](versions/direction-c-artifact-reproducibility.md) |
| C corpus | [`versions/direction-c-corpus-protocol.md`](versions/direction-c-corpus-protocol.md) |
| C fixed search | [`versions/direction-c-fixed-search-batch-20260526.md`](versions/direction-c-fixed-search-batch-20260526.md) |
| C broader source | [`versions/direction-c-broader-source-pass-20260527.md`](versions/direction-c-broader-source-pass-20260527.md) |
| C targeted artifact link | [`versions/direction-c-targeted-artifact-link-pass-20260527.md`](versions/direction-c-targeted-artifact-link-pass-20260527.md) |
| D | [`versions/direction-d-audit-systems.md`](versions/direction-d-audit-systems.md) |

The fuller manuscript-level drafts are indexed at
[`multi_direction_paper_drafts.md`](multi_direction_paper_drafts.md) and live
under [`versions/drafts/`](versions/drafts/). They intentionally stay in
Markdown until a direction passes its go/no-go gate; only Direction A currently
owns the LaTeX manuscript.

All versions keep using `source_map.md`, `claim_register.md`,
`evidence_bank.md`, `data/claim_trace.csv`, and `data/source_provenance.csv`;
paper-track forks use the shared evidence register.
