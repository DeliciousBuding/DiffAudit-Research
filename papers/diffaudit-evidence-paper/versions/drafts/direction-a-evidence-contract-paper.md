# Direction A Draft: Evidence-Contracted Measurement

## Assigned Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Paper PI | Framework lead | Controls thesis, venue fit, contribution language, and rebuttal posture. |
| Evidence engineer | Metric audit lead | Verifies reportable-row metrics, finite-tail denominators, scripts, and evidence-source provenance. |
| Figures editor | Visualization lead | Owns evidence-contract diagrams, bundle charts, and candidate/reportable visual separation. |
| Internal area chair | Validity critic | Blocks governance-only prose and unsupported generalization. |

## Working Paper

| Field | Draft choice |
| --- | --- |
| Title | When Do Diffusion Membership-Inference Scores Become Audit Evidence? An Evidence-Contracted Measurement Study |
| Target type | Full security/privacy measurement paper |
| Venue posture | Security/privacy measurement or applied ML security venue; CCF-B full-paper posture only after reviewer-facing measurement-method framing is strong |
| Current artifact | Active LaTeX draft: [`../../main.tex`](../../main.tex) |

## Abstract

Membership inference against diffusion models is often reported as a scalar
attack score. For a security or privacy audit, the harder measurement question
is which evidence packets survive replay, finite-tail, and consumer-boundary
checks well enough to support a specific target, split, observable, metric, and
consumer claim. This version studies evidence sufficiency for audit reports as
a measurement endpoint: given a proposed claim and an evidence packet, determine
whether the claim is being escalated beyond its observable support, and identify
the strongest wording plus first missing surface that the packet can support.
The protocol treats the unit of analysis as a row-bound evidence packet. Method
names, repositories, and headline AUCs enter only through packet fields.
Applying the C1-C15 claim trace to proposed audit claims separates
three replay-admitted packets, two bounded source-documented point comparators,
one high-AUC repeated-response candidate that remains candidate-only after
SD/CelebA img2img and consumer-boundary gates fail, boundary-case
metadata/source-query/artifact controls, thirteen prepared C14 pre-label
public-surface stress rows, and C15 release-wording QA. No external C14 reviewer
CSVs are complete yet. The result is claim-bound evidence measurement.

## Controlling Thesis

The scientific contribution is evidence calibration. Diffusion MIA research has
many attractive scores, but the audit question is narrower: which scores can be
reused by another consumer without changing target identity, split semantics,
metric meaning, or artifact boundary? The paper turns this into a concrete
measurement contract and shows that positive, candidate, and negative results
all have decision value when their boundaries are explicit. The active LaTeX
draft now frames the endpoint as evidence-sufficiency measurement: a reviewer can
inspect the trace row, identify the first missing surface, and check whether the
allowed wording changes.

## Contribution Claims

| Claim | Evidence anchor | Boundary |
| --- | --- | --- |
| A-C1: The six-gate admission rule returns a gate vector, first blocker, evidence state, and strongest allowed wording for each claim. | [`../../claim_register.md`](../../claim_register.md), [`../../source_map.md`](../../source_map.md), [`../../data/claim_trace.csv`](../../data/claim_trace.csv) | Methodological claim; public-paper prevalence is outside this claim. |
| A-C2: The active C1-C15 trace separates replay-admitted packets, source-documented point estimates, candidate/support evidence, bounded negatives, C14 prepared pre-label weak-rule stress controls, and C15 release-wording QA. | [`../../data/claim_trace.csv`](../../data/claim_trace.csv), [`../../data/source_provenance.csv`](../../data/source_provenance.csv) | Claim-state output; leaderboard, prevalence, reviewer-reliability, and systems-effectiveness claims are outside scope. |
| A-C3: Five role-separated calibration rows can be discussed together only after replay/source tier is attached. | [`../../evidence_bank.md`](../../evidence_bank.md) reportable rows and calibration bundle table | Three rows are replay-admitted; two are source-documented point estimates; no homogeneous benchmark, interval, dominance, or cross-access ranking. |
| A-C4: H2 is the high-AUC non-admission counterexample. | H2 AUC `0.961529`, same-family cache-robustness mean `0.959755`, img2img AUC `0.7888` | H2 remains candidate-only because non-adjacent-surface and consumer-boundary gates fail. |
| A-C5: Negative/support gates prevent false portability and artifact-availability claims. | ReDiffuse, CommonCanvas, MIDST, Tracing the Roots, separately supplied SD ReDiffuse, and fixed-search notes | Route-local blockers only; original-method refutation and field-wide prevalence estimates are outside scope. |

## Manuscript Spine

| Section | Draft content |
| --- | --- |
| Introduction | Open with the gap between attack scores and audit evidence. Explain why high-AUC diffusion MIA results can be unusable when target identity, split semantics, row coverage, or consumer boundary are missing. |
| Related Work | Position against classical MIA, diffusion MIA, image memorization/copying, and artifact reproducibility. Show why audit consumption needs a contract. |
| Evidence Contract | Define target identity, split semantics, score/response coverage, metric provenance, consumer boundary, and surface delta. Include finite-tail language. |
| Measurement Protocol | Explain admitted/candidate/support/blocked states; map the claim-first procedure to `source_map.md`, `claim_register.md`, and `evidence_bank.md`; show how metrics are generated from existing JSON artifacts and how candidate promotion depends on the gates. |
| Artifact Corpus | Introduce the current corpus as a controlled evidence set, then state its limits. Keep fixed-search and broader-source rows inspectable and non-pooled with replay rows; use Direction C expansion as source-query denominator controls, not as completed broad-literature proof. |
| Reportable Bundle | Present five role-separated reportable rows with metrics, costs if available, access mode, replay tier, and caveat. |
| H2 Case Study | Show output-cloud geometry as a positive candidate and explain the controls: label shuffle, shared-position seed policy, seed stability, and same-family cache robustness. |
| Negative and Support Evidence | Use weak scouts and feature packets to show why second-asset claims require more than scoreability. |
| Discussion | Frame evidence contracts as measurement science and state what future papers should publish to become reusable. |
| Threats to Validity | Cover local artifact bias, corpus size, finite tails, candidate boundary, and lack of broad portability. |

## Figure and Table Plan

| Asset | Purpose | Status |
| --- | --- | --- |
| Evidence-contract pipeline | Shows how rows move from artifact to admitted/candidate/support state. | In active LaTeX. |
| Reportable metric chart | Makes the five-row mixed-strength bundle legible without hiding caveats. | Generated from JSON-derived CSV. |
| H2 controls chart | Shows candidate signal, label-shuffle sanity, shared-position control, and same-family cache robustness. | Generated. |
| Candidate/support gate matrix | Prevents H2, Tracing the Roots, and weak scouts from reading like admitted rows. | In active LaTeX. |
| Artifact-corpus funnel | Helps reviewers see why selected records, fixed-search metadata, and broader-source hygiene are separate denominators. | Covered in the active LaTeX by the corpus-construction table; a standalone funnel figure is deferred to Direction C or appendix material to keep the current 10-page draft focused. |

## Review Risks and Fixes

| Risk | Fix |
| --- | --- |
| Reads like internal governance. | Put measurement problem first: score-only claims lack reusable evidence. |
| Reportable bundle is narrow. | State replay strength explicitly and use candidate/negative evidence to show why stronger admission is hard. |
| H2 looks like the real paper. | Keep H2 as a negative-control section inside the contract paper unless a second response asset appears. |
| Negative evidence looks cherry-picked. | Use Direction C as selected-corpus boundary evidence now; require a larger distinct-surface corpus before standalone aggregate claims, and external label audit before reliability claims. |
| Contract reads as descriptive artifact documentation. | Preserve a claim-first protocol: define the unsafe consumer claim, bind the minimum evidence packet, replay or record metrics, assign gates, choose the strongest allowed state, and make the trace row inspectable enough for a reviewer to falsify the wording. |

## Full-Paper Readiness Memo

Date: 2026-05-27

This memo fills the Evidence Contract Team review packet from
`../README.md`. It audits readiness for the active LaTeX draft. The current
paper still needs an evidence-strength gate before submission posture improves.

| Review item | Current evidence | Decision |
| --- | --- | --- |
| Title | `When Do Diffusion Membership-Inference Scores Become Audit Evidence? An Evidence-Contracted Measurement Study` | Fits the paper object: claim/evidence measurement, with the reviewer-facing measurement question foregrounded before the project name. |
| Abstract/headline claims | Main claims map to `../../data/claim_trace.csv` rows C1-C15 and `../../claim_register.md`; C12 is a sidecar source-query denominator control, C13 is a sidecar targeted L1 artifact-link control, C14 is a prepared pre-label weak-rule stress object, and C15 is release-wording QA. | Allowed with bounded wording. |
| Contribution claims | Contributions state falsifiable claim admission, a generated claim trace, H2 failed-admission stress test, and selected-corpus boundary evidence. | Aligned with the current trace and avoids SOTA/leaderboard framing. |
| Reviewer-entry polish | The Introduction now names RQ1/RQ2/RQ3 for the contract, admission-tier, and stress-test questions, and normalizes paper-facing Tracing the Roots mentions. | Improves first-page legibility without changing any metric, gate, or admission state. |
| Evidence-alignment polish | Side review found three scrutiny risks: C12 looked like an unexposed 12th main claim, H2 img2img portability used unsupported comparator wording, and C5 provenance did not name MIDST or separately supplied SD ReDiffuse. | Fixed in the active draft and generated sidecars: C12 is explicitly source-query denominator control only, H2 portability no longer claims that comparator result, and C5 provenance now resolves route-specific source rows. |
| Reviewer-risk hardening | A later review flagged three remaining full-paper risks: contribution could read like a reproducibility checklist, consumer-boundary could look circular, and selected corpus could look decision-selected. | Fixed in `main.tex`: abstract/introduction now frame claim-support outcome measurement, consumer-boundary is derived from external consumer requirements, and the corpus is explicitly a purposive stress-test corpus with no sensitivity/specificity or field-behavior estimate. |
| Reviewer-surface pass | A read-only venue reviewer flagged project/tool framing, process-like contribution bullets, implementation-first protocol wording, cherry-pick corpus wording, and H2 looking like a hidden second contribution. | Fixed in `main.tex`: the title is question-led, contribution bullets now describe falsifiable claim-state outputs, Measurement Protocol starts with the abstract four-step claim/packet procedure, the corpus is a boundary-case corpus, and H2 is a high-AUC non-admission counterexample. |
| External reviewer-risk pass | Two read-only reviewers flagged remaining risks: the abstract/contributions could still read as ledger work, the consumer-boundary gate could look circular, H2 implementation detail could distract from the non-admission point, and corpus counts could look like coverage results. | Tightened in `main.tex`: the abstract now frames evidence sufficiency for audit reports as the endpoint, the first contribution detects claim escalation and records the first missing surface, consumer-boundary tasks are fixed before gate labels, reportable point rows are explicitly non-interval point evidence, and H2 is labeled as a metric-strength stress test. |
| 2026-05-27 Team A continuation review | Scientific-framing and related-work reviewers flagged residual ledger wording, possible circular consumer-boundary reading, an MIA-limitation-sensitive training-use phrase, and H2 section title risk. | Fixed in `main.tex`: claim-support outcomes replace gate-transition phrasing, consumer tasks are tied to observable reviewer actions, benchmark-label wording avoids individual training-use proof, Related Work now says the paper adjudicates claim admissibility, corpus counts are construct-validity checks, and H2 starts with the candidate-boundary framing. |
| 2026-05-27 post-continuation venue-hardening | Evidence Contract and portfolio reviewers flagged three remaining venue risks: validation scope could still read like a case-study codebook, five reportable rows did not expose enough target/split/replay identity in the paper surface, and the consumer-boundary gate was still too prose-based. | Fixed in `main.tex`: the corpus section now states that it does not estimate contract performance and uses purposive boundary cases only, consumer-boundary rows in the gate table make consumer actions and missing artifacts explicit, and the five calibration cases now name target/split and replay tier without requiring a sidecar jump. |
| 2026-05-27 claim-boundary table pass | A later read-only review warned that the trace table still looked like a ledger and that H2 rejection could look subjective. | Fixed in `main.tex`: the claim-trace table is now a reviewer-facing unsafe-claim table mapping evidence present, first missing surface, and allowed wording for leaderboard/dominance, point-interval, H2 portability, corpus-prevalence, and route-general claims. |
| 2026-05-27 abstract/layout polish | The latest self-review found that the abstract evidence enumeration was too long, the second contribution could be tightened, two small tables used justified `p{}` columns, and a `target/checkpoint` phrase caused an avoidable hbox warning in the final validity-threat page. | Fixed in `main.tex`: the abstract now lists the three replay-admitted packets, two point comparators, H2 candidate, and boundary metadata/source-query/artifact-link controls in one readable claim sentence; the contribution wording is shorter; the small tables use existing `L{}` columns; and the release checklist uses `target and checkpoint identities`. No claim scope or metric changed. |
| 2026-05-27 C13 manuscript consistency pass | A reviewer-risk pass found trace-scope drift after C13: the abstract and contribution bullets still used 12-row language, and consumer-boundary gates could still look subjective. | Fixed in `main.tex`: the paper moved to boundary-case validation, targeted-L1 sidecar rows entered the unsafe-claim and validation-layer surfaces, and consumer-boundary rows became observable reviewer actions. The current C1-C15 trace keeps later C14 prepared pre-label stress controls and C15 release-wording QA separate. |
| 2026-05-27 external-style validation/audit-interface pass | A read-only external reviewer flagged three residual CCF-B risks: validation scope could still look too small or circular, consumer templates needed a stronger predeclared anchor, and sidecar proof files were not auditable enough from the manuscript surface. | Fixed in `main.tex`: the introduction states validation criteria, consumer-boundary templates anchor the protocol, and the measurement protocol exposes the claim-trace/source-provenance interface for headline counts, wording, hashes, and repository identities. |
| 2026-05-27 targeted artifact-link expansion | A targeted chase over the existing `fs20260526-arxiv-04` metadata-only seed found the official MIDM GitHub code/protocol artifact. | Updated C13 and Direction C sidecars from two to three non-pooled targeted L1 rows. The new MIDM row is L1 artifact-inspection evidence only: generated split indices and loss/likelihood attack outputs are documented, but no immutable split manifest, row-score array, ROC, metric JSON, checkpoint hash, or verifier packet was observed. |
| 2026-05-27 measurement-instrument polish | Two read-only reviewers flagged that the paper could still read as an internal ledger, that H2 could look like a hidden candidate-method result, and that aggregate-corpus and label-reliability proof obligations were too easy to conflate. | Fixed in `main.tex` and `source_map.md`: the trace is now described as a measurement instrument with variables and admissible outputs, H2 is explicitly a metric-only negative control, clean immutable release-snapshot expectations are stated, corpus/prevalence obligations are separated from external multi-reviewer label-audit obligations, and the targeted artifact-link source map now says three non-pooled L1 surfaces. |
| 2026-05-27 first-page validation-design polish | The first page still risked reading as trace bookkeeping because the abstract and contributions led with the then-current claim inventory and a trace-row-change criterion. | Fixed in `main.tex`: the abstract now frames the evaluation as a boundary-case validation design, the introduction uses coded variables and coded claim-state changes, and the contribution bullets name replay-admitted packets, point comparators, metric-only negatives, source/artifact stops, and blocked overclaim wording. |
| 2026-05-27 case-study/state-machine wording demotion | PDF-surface review found that repeated `case study` wording and `claim-state transition` phrasing could make the contribution read as a project report or internal state machine. | Fixed in `main.tex`: first-page, pipeline, discussion, and conclusion wording now use validation study, boundary-case result, H2 negative-control, packet-to-wording, and newly supplied evidence-surface language with unchanged metrics, gates, and claim states. |
| 2026-05-27 boundary-validation target pass | A submission-strength review found that the corpus section needed to say why a small purposive set is still a scientific validation object. | Fixed in `main.tex`: the validation target is now discriminative correctness over claim states, with explicit expected behavior for positive controls, high-score metric-only negatives, route-closure negatives, and L0/L1 artifact stops. |
| 2026-05-28 external-review wording pass | Read-only reviewer agents flagged that the first page still sounded defensive, that score-only/code-availability baselines were not contrasted clearly enough, and that several internal-origin terms retained process flavor. | Fixed in `main.tex`: the abstract now leads with a frozen boundary-case validation suite, the introduction states how score-only and code-availability rules would overpromote claims, contributions and corpus text are compressed, H2/corpus terms use observable/construct-validity language, and restricted/non-redistributable artifact wording replaces local workflow terms. |
| 2026-05-28 claim-evidence audit pass | A read-only claim audit found four support risks: H2 wording implied retained prediction arrays, C13 was missing from `evidence_bank.md`, C12 query-row wording overstated empty/noisy/duplicate observations, and recon metadata exceeded the point-only claim boundary. | Fixed in `main.tex`, `build_paper_assets.py`, `claim_register.md`, `evidence_bank.md`, and generated CSVs: H2 now says aggregate held-out prediction summaries, C13 has an evidence-bank row, C12 is metadata-screening/query hygiene, and recon quality/cost says source-documented public-100 threshold readout with no row-score array retained. |
| 2026-05-29 external-origin wording cleanup | Follow-up scan found residual reader-facing origin labels, over-broad source-scope language, case-study framing, and stale recon-readout language outside the main claim boundary. | Fixed in `main.tex`, `claim_register.md`, `evidence_bank.md`, `source_map.md`, Direction C/D reader views, curated corpus rows, and `build_paper_assets.py`: public wording now uses restricted/separately supplied/source-confounded packets, metadata-screening/query hygiene, and boundary examples. Real evidence paths and provenance IDs are preserved as anchors, but generated notes no longer expose stale origin-label or source-scope phrasing. |
| Page state | `paper.pdf` is a 10-page letter-paper draft after the 2026-06-09 rebuild. | Current release gates allow this draft; any target venue with a tighter limit needs a separate compression pass. |
| Continuation build verification | On 2026-06-09, `python -X utf8 scripts\run_pr_checks.py` passed after rebuilding `paper.pdf`, regenerating paper assets, exporting the anonymous supplement, exporting the C14 false-promotion review bundle, and synchronizing the post-label key SHA. `pdfinfo` reports `Pages: 10` and letter paper size; `pdffonts` reports no Type 3 fonts. | The current Direction A surface is mechanically sound enough for further reviewer-facing argument work. Submission strength still depends on external C14 labels, a larger distinct-surface corpus, or a second independent row-bound score/response asset. |
| PDF/font/layout QA | `pdffonts paper.pdf` reports Type 1 fonts only. The current draft contains the evidence-contract pipeline, C14 weak-rule figure, admitted-row chart, H2 controls chart, claim trace/gate tables, corpus-construction table, negative/support table, and references. | The PDF is readable as a 10-page conference-style draft; compression is venue-specific editing separate from claim-evidence changes. |
| Final claim audit | Current sidecars prove the headline counts and metrics used by `main.tex`: `claim_trace.csv` has C1-C15; `admitted_rows.csv` has five rows split into two row-score replay, one target-score replay, and two source-documented point rows; `h2_output_cloud_rows.csv` supports H2 AUC `0.961529`, label-shuffle AUC `0.507595`, cache-robustness AUC range `0.94899--0.97052`, and img2img AUC `0.7888` with zero strict-tail recovery; the main selected-corpus/fixed-search denominators are `21` and `17`; C12 records a separate `10`-row broader-source sidecar; C13 records a separate three-row targeted L1 sidecar for Direction C; C14 is `packet_ready_only` with `n_reviewers=0`; C15 covers 28 release-wording QA cases. | Headline numerical claims are trace-supported in the current draft; C12/C13 are sidecar controls, C14 is pre-label only, and C15 is release QA. |
| Boundary-case validation framing | The active manuscript now frames the corpus section as a validation design: positive replay/source controls, H2 metric-only negative control, route-closure negatives, support/source-confounder controls, and L0/L1 artifact stops. Generated L0-L3 support summaries still report selected-corpus counts `8/3/9/1` and fixed-search counts `13/4/0/0`, while the broader-source pass is metadata-screening/query hygiene and targeted artifact links are non-pooled L1 stops. | Stronger venue-facing framing for Direction A; standalone aggregate claims still need a larger distinct-surface corpus, and reliability/adjudication claims need external multi-reviewer label audit. |
| External-style wording polish | Targeted manuscript/PDF scans no longer find prior workspace, executor-review, evidence-register, route-decision, project-label, note/card jargon, stale origin-label wording, over-broad source-scope wording, or stale recon-readout wording in the paper surface; the abstract now uses boundary-case validation design and the conclusion uses boundary-reporting language. | Internal-project wording risk is reduced for the current draft. |
| Falsifiability/proof obligations | The Discussion now states the evidence that would change bounded outcomes: H2 needs a non-adjacent response asset plus consumer-boundary path; selected-corpus aggregates need a larger distinct-surface frozen corpus; reliability/adjudication claims need external label audit; point-role comparators need row- or target-score arrays before interval/dominance claims. | Strengthens the measurement-science posture without upgrading any candidate row. |
| Claim-trace table readability | The active manuscript replaced the generic trace-schema table with a five-row unsafe-claim table covering leaderboard/dominance, point-interval, H2 portability, corpus-prevalence, and route-general claims. | Improves reviewer falsifiability without promoting sidecar claims. |
| References | 25 citation keys in the current BibTeX output; missing keys `0`; unused keys `0`; BibTeX warning count `0`. | Reference hygiene is acceptable without adding page-expensive URL/DOI fields. |
| Forbidden-claim scan | Latest targeted source and PDF scans find no stale consumer/product/admission shorthand, false pooled-denominator wording, stale validation-scope wording, internal review overclaim wording, stale origin-label wording, over-broad source-scope wording, stale recon-readout wording, or H2 prediction-array wording. PDF-surface wording remains bounded to guarded or negated uses of `leaderboard`, `prevalence`, `field-wide`, `reliability`, `inter-rater`, and `deployment`. | No affirmative overclaiming hit found in the scanned surface. |

Headline claim coverage:

| Paper statement | Trace/register support | Allowed wording |
| --- | --- | --- |
| Five reportable rows exist under one contract. | C1, C2, `admitted-evidence-bundle.json`, reportable table. | Three replay-admitted packets plus two source-documented point comparators; homogeneous benchmarking is outside scope. |
| H2 is strong but non-admitted. | C3, C4, H2 controls table, H2 admission-decision table. | Controlled same-family candidate and failed-admission stress test; no admitted black-box row. |
| Selected artifact records support boundary decisions. | C6-C10, C12, and C13, `artifact_corpus_v1.csv`, fixed-search batch, broader-source API pass, targeted artifact-link pass, second-pass label review. | Selected-corpus / metadata-process / L1 artifact-inspection evidence only; field prevalence and independent reliability require new evidence. |
| Uncertainty is partial. | C11, `metric_uncertainty.csv`. | Intervals only where score arrays or recorded H2 aggregate CIs support them; no dominance or admission upgrade. |
| Negative/support routes are decision evidence. | C5, negative/support table. | Route-local first blockers and `Not allowed` labels; no method refutation. |

Visible paper objects:

| Object | Purpose | Readiness |
| --- | --- | --- |
| Evidence-contract pipeline figure | Shows claim-oriented state transition. | Present in active LaTeX. |
| Claim-trace group table and gate matrix | Make the C1-C15 measurement endpoint auditable without printing the full sidecar table. | Present in active LaTeX; detailed rows stay in `claim_trace.csv`. |
| Corpus-construction table | Declares the `21` selected rows, `17` fixed-search metadata observations, `10` broader-source API observations, and `3` targeted L1 artifact-link rows in the active LaTeX. | Present in active LaTeX plus sidecar. |
| Reportable evidence table and chart | Keeps mixed replay/source tiers visible. | Present/generated. |
| H2 controls chart and admission table | Preserves the positive signal while showing non-admission. | Present/generated. |
| Negative/support table | Prevents route-local weak results from becoming broad claims. | Present in active LaTeX with `Not allowed` labels. |

Current go/no-go:

| Decision | Reason |
| --- | --- |
| Continue Direction A as the only full LaTeX manuscript. | It absorbs reportable rows, H2, selected corpus, and negative/support evidence under one shared ledger. |
| CCF-B/CCF-A posture remains conditional. | The current draft passes artifact-backed claim-support and release gates. CCF-B submission posture remains blocked until one of the evidence-strength gates lands: external C14 labels, a larger distinct-surface corpus, or a second row-bound score/response asset. |
| New GPU experiments remain closed. | The remaining blocker is paper validity and claim framing. |
| B/C/D TeX forks remain closed. | Their promotion gates remain narrower than Direction A. |

## Go / No-Go

| Decision | Condition |
| --- | --- |
| Continue as main LaTeX | Already satisfied: uses all evidence under the shared claim boundary. |
| Continue tightening the 10-page LaTeX draft | Improve motivation, method detail, reviewer-facing contribution wording, and venue-specific compression after evidence scope is stable. |
| Submit as CCF-B-style measurement paper | Needs venue-facing polish and stronger external-facing corpus evidence beyond this internal claim audit; reliability/adjudication claims need external label audit. |
| Stop | If the paper cannot sustain a measurement-science thesis. |
