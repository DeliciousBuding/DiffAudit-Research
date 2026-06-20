# DiffAudit Paper Versions

> Date: 2026-06-09
> Role: track active paper directions and claim gates without parallel TeX forks.

## Canonical Rule

This file is the canonical board for multi-version paper planning. The root
summary files (`../paper_portfolio.md`, `../multi_direction_paper_drafts.md`,
and `../research_team_pitches.md`) are reader views. This board controls the
current mandate, gate, team assignment, and next action. A replacement
paper-direction register must replace this file and retire this board.

This folder contains paper-version briefs and manuscript-level Markdown drafts.
The briefs define direction boundaries; [`drafts/`](drafts/) contains fuller
paper versions that can be promoted to LaTeX only after their go/no-go gates
are met. The shared evidence boundary remains:

- Use `../source_map.md` for admissible sources.
- Use `../claim_register.md` before promoting any statement.
- Use `../evidence_bank.md` for numbers.
- Use `../data/claim_trace.csv` and `../data/source_provenance.csv` for
  per-claim trace rows and local artifact identity.
- Treat `../main.tex` as the active Direction A LaTeX draft.

## 2026-05-27 Portfolio Decision

Multiple paper versions are controlled writing tracks over one shared evidence
ledger. The portfolio decision for the next cycle is:

1. Keep Direction A as the only active full-paper LaTeX manuscript.
2. Maintain Directions B, C, and D as manuscript-level Markdown tracks with
   explicit teams, promotion gates, and stop rules.
3. Direction E stays closed. Current evidence supports four distinct scientific
   objects; a fifth track would repackage weak or candidate-only evidence.
4. If a new independent evidence object appears, first classify whether it
   strengthens A, unlocks B/C/D, or creates a new paper object. Only the last
   case may add a new direction.

Next concrete outputs: Direction A reviewer-facing polish and C14 external-label
collection, a short-paper-ready Direction B brief, a selected-corpus Direction C
results skeleton with stratified denominators, and a Direction D artifact/demo
risk-card plus selected fault-injection evidence. Direction A owns TeX today.

## 2026-05-27 Four-Team Review Outcome

Four read-only research-team reviews support several paper versions when each
version has a different scientific object and promotion gate.

| Direction | Owning research team | Independent-paper posture | Next evidence that would change the decision | Hard no-go |
| --- | --- | --- | --- | --- |
| A | Evidence Contract Team | Current full-paper track with CCF-B-style measurement-paper potential; submission readiness depends on reviewer-facing polish and stronger distinct-surface support. | External-style reviewer polish plus a larger distinct-surface corpus for aggregate corpus claims; external label audit only if making reliability/adjudication claims. | More score tables, GPU runs, leaderboard language, homogeneous five-row benchmark wording, or consumer-boundary H2 wording. |
| B | Response Geometry Team | Independent short/workshop track only: H2 response-cloud observable plus failed img2img portability gate. | A second independent response asset that passes target, split, response/score, metric, provenance, consumer-boundary, and surface-delta gates. | Same-cache feature sweeps, repeat tuning, KDE/shadow variants, cross-model portability, reportable admission, or hiding the img2img failure. |
| C | Artifact Claim-Support Team | Scoped selected-corpus measurement note; not a field-wide reproducibility or prevalence paper. | A larger frozen distinct-surface batch, or external label audit if reliability/adjudication language is needed. | Pooling `21`, `17`, and `10` into `48`, calling same-team label hygiene inter-rater reliability, or hostile paper-failure framing. |
| D | Artifact Contract Team | Artifact/demo/report-correctness package; not a systems-effectiveness paper. | Report-renderer A/B drift reduction, semi-external use, public-safe demo/deployment telemetry, or broader observed report-surface fault injection tied to realistic report drafts. | Deployed enforcement, external adoption, user-impact, or systems-effectiveness claims from schema, phrase guards, or selected fault injection alone. |

The writing sequence is fixed: finish Direction A's reviewer-facing manuscript
surface first, keep B/C/D paper-ready in Markdown, and promote the track whose
missing evidence arrives.

## Current Consolidated State

The current paper set has four generated versions with one shared evidence
ledger. The earlier progress log has been collapsed into the decision-relevant
state below.

| Direction | Current paper surface | Evidence state | Next useful action |
| --- | --- | --- | --- |
| A | Active LaTeX manuscript in `../main.tex` and `../paper.pdf`. | The manuscript presents evidence sufficiency for audit reports as the measurement endpoint, defines claim escalation, reports claim-support outcomes, uses purposive boundary cases to test claim-state behavior, states how score-only or code-availability rules would overpromote claims, makes consumer-boundary checks and role-separated calibration packet identities visible, keeps H2 as a metric-strength stress test, and treats `21/17/10/3` denominators as scoped corpus rows. The 2026-06-09 build is a 10-page letter-paper draft with no Type 3 fonts. C14 is prepared as a thirteen-row author-keyed pre-label stress object with hard-blind review materials; completed reviewer CSVs/declarations are still required before adjudication, reliability, denominator, or prevalence claims. | Reviewer-facing argument polish; C14 reviewer-label collection; stronger distinct-surface corpus if standalone aggregate corpus claims become central. |
| B | Markdown short/workshop version in `drafts/direction-b-output-cloud-short-paper.md`. | H2 output-cloud AUC/control rows are preserved as candidate-only; SD/CelebA img2img is the failed portability/admission gate; the draft now has a short-paper introduction, central-results spine, and response-cloud schematic asset. | Paperization only: tighter prose around existing H2/control/boundary tables. No same-cache sweeps. |
| C | Markdown selected-corpus measurement version in `drafts/direction-c-artifact-reproducibility-paper.md`. | `21` selected rows, `17` fixed GitHub/arXiv metadata rows, and `10` HF/Zenodo/OpenReview source-query observations are non-poolable; the draft now places the denominator box before any standalone abstract/results. A targeted 2026-05-27 artifact-link pass recovered three L1 public artifact surfaces from existing metadata-only rows: one HF dataset, one official SecMI GitHub implementation/split tree, and one official MIDM code/protocol repository. They are not score/metric replay and are not pooled with existing denominators. | Keep denominator-first results text and figures; add a larger distinct-surface corpus only via targeted artifact-link acquisition, and add external label audit only for reliability claims. Stop broad no-download sweeps that only re-find existing or noisy metadata. |
| D | Markdown artifact/demo/report-correctness version in `drafts/direction-d-audit-systems-paper.md`. | The draft now has a current artifact/demo packet summary tying the architecture SVG, generated risk card, renderer/public-surface guards, and selected fault-injection rows to artifact/demo correctness only. | Systems-effectiveness still requires report-drift A/B, external-use, or public-safe deployment/demo evidence. |

Verification state for Direction A: the 2026-06-09 release packet rebuild
regenerated CSV sidecars, figures, `paper.pdf`, the anonymous supplement, and
the C14 review bundles. `python -X utf8 scripts\run_pr_checks.py` passes,
including public-surface, claim-gate recode, report-correctness
fault-injection, C14 aggregation in `prepared_no_reviewer_csvs` scope, public-surface freeze
preflight, and paper release-packet checks. `pdfinfo` reports ten pages and
`pdffonts` reports no Type 3 fonts. The current draft is buildable and
public-surface clean. Submission strength still depends on external C14 labels,
a larger frozen public-source corpus, or a second independent row-bound
score/response asset.

## Version Map

| Version | Team | Paper Type | Current Decision |
| --- | --- | --- | --- |
| A | Evidence Contract Team | Security/privacy measurement | Main manuscript now. |
| B | Response Geometry Team | Response-cloud observable short/workshop paper | Keep as second-track; negative img2img portability is central, and full-paper claims need a second response asset. |
| C | Artifact Claim-Support Team | Selected-corpus L0-L3 claim-support measurement paper | v1 corpus, GitHub/arXiv fixed-search batch, HF/Zenodo/OpenReview broader-source pass, targeted artifact-link pass, gate summary, consistency pass, and bounded second-pass label review exist; standalone aggregate claims still need stratified denominators plus a larger distinct-surface corpus, and reliability/adjudication claims need external label audit. |
| D | Artifact Contract Team | Independent artifact-contract/report-correctness package | Treat as artifact/demo report-correctness package with a generated risk card, selected observed fault-injection rows, and direct candidate-promotion language guards; full systems framing still needs report-drift, external-use, or deployment evidence. |

## Multi-Version Production Line

The project may maintain several paper-facing tracks over one evidence ledger.
The production split for this cycle is:

| Output | Owning team | File target | Exit condition |
| --- | --- | --- | --- |
| Active full manuscript | Evidence Contract Team | `../main.tex` and `drafts/direction-a-evidence-contract-paper.md` | Claim trace and PDF checks, including no Type 3 fonts and balanced final-page rendering, keep the five-row bundle inside the shared claim boundary. |
| Technical short-paper package | Response Geometry Team | `direction-b-output-cloud-geometry.md` and `drafts/direction-b-output-cloud-short-paper.md` | H2 remains candidate-only and the img2img failure stays central. |
| Selected-corpus measurement package | Artifact Claim-Support Team | `direction-c-artifact-reproducibility.md` and `drafts/direction-c-artifact-reproducibility-paper.md` | Counts use separate `21`-row selected-corpus, `17`-row fixed-search, and `10`-row broader-source denominators. |
| Targeted artifact-link pass | Artifact Claim-Support Team | `direction-c-targeted-artifact-link-pass-20260527.md` and `../data/artifact_corpus_targeted_artifact_links_20260527.csv` | Three existing metadata-only seeds now have L1 public artifact surfaces: one Hugging Face dataset, one official SecMI GitHub implementation/split tree, and one official MIDM code/protocol repository; no score/metric replay and no denominator pooling. |
| Artifact/demo package | Artifact Contract Team | `direction-d-audit-systems.md` and `drafts/direction-d-audit-systems-paper.md` | A generated public-safe risk card, initial observed fault-injection rows, and direct candidate-as-admitted/reportable language checks exist; report-drift, external-use, or deployment evidence is required before systems-paper claims. |

No team owns evidence promotion alone. A team can change framing, section
order, and figure emphasis; it cannot change admission state without updating
the claim register, source map, generated trace, and the promotion gate here.

## Research Team Operating Board

Each direction is assigned to a paper team with a distinct scientific object.
The team names are organizational handles for writing, evidence review, and
critique. New validators, crawlers, downloads, and GPU runs require a promotion
gate showing that the evidence would change the paper decision.

Internal staffing follows the active dev-team split without turning it into
paper text: architecture/claim decisions are reviewed by the reasoning lead,
small metric/provenance checks go to the implementation checker, and figure or
manuscript-layout work goes to the document/visual editor. The named research
teams below remain the paper-facing handles.

| Direction | Team mandate | Lead roles | Next deliverable | Promotion gate | Stop rule |
| --- | --- | --- | --- | --- | --- |
| A | Turn the current evidence base into an evidence-contracted measurement paper. | Framework PI, replay/provenance audit lead, figure editor, claim-scope critic. | Maintain the filled full-paper readiness memo; next useful work is reviewer-facing tightening, C14 label collection, and corpus strengthening. | Final claim audit passes, PDF compiles at page budget, and every headline statement maps to `../claim_register.md`. | CCF-B/CCF-A positioning must read as measurement science, with internal-governance phrasing removed. |
| B | Make H2 output-cloud geometry a bounded response-cloud observable short paper. | Response-geometry lead, scorer engineer, observable visual lead, portability critic. | Keep the Markdown draft short-paper-ready with H2 controls and img2img portability failure as a required main table/panel. | A second independent response asset passes the six gates, or the team explicitly targets a short/workshop H2-only paper. | Stop same-cache feature sweeps, repeat tuning, or portability language without new evidence. |
| C | Measure claim-support levels over a frozen selected corpus. | Claim-support lead, provenance-audit lead, corpus table lead, selection-bias critic. | Use v1 corpus, fixed-search batch, broader-source API pass, targeted L1 artifact-link rows, gate summaries, consistency pass, and bounded second-pass review to draft stratified L0-L3 results. | Larger distinct-surface frozen corpus exists before any standalone aggregate claim; reliability/adjudication language requires external label audit. | Stop any pooled reproducibility rate, field-wide prevalence claim, or hostile "paper failure" framing. |
| D | Package the evidence boundary as an artifact/report-correctness contract. | Contract architecture lead, bundle-validation lead, report-correctness lead, public-boundary critic. | Keep the public-safe risk card, observed bundle/risk-card fault-injection table, direct candidate-promotion language guard, two consumer-boundary no-drift audits, and static architecture SVG aligned with existing checks. | Bundle/risk-card fault injection, direct report-language guards, and no-drift audits are observed; renderer A/B drift reduction, external-use, or deployment evidence is still required before systems-effectiveness claims. | Stop if the result is only a schema description, adds a new validator framework for symmetry, or lacks measurable report-correctness benefit. |

## Team Work Packages

| Team | Immediate paper version | Do now | Boundary |
| --- | --- | --- | --- |
| Evidence Contract Team | Full Direction A conference manuscript. | Replace remaining project-governance phrasing with measurement-method language; make contribution bullets reviewer-facing; check every abstract/introduction claim against `../data/claim_trace.csv`. | The five-row bundle is heterogeneous report evidence, not a benchmark or leaderboard. |
| Response Geometry Team | Direction B short/workshop manuscript. | Turn H2 controls and the img2img portability failure into a compact central-results spine. | H2 stays within existing controls; same-cache sweeps, feature tuning, and cross-model portability need a new response asset. |
| Artifact Claim-Support Team | Direction C selected-corpus measurement manuscript. | Draft stratified L0-L3 result language from the 21-row corpus, 17-row fixed-search batch, 10-row broader-source API batch, and three-row targeted L1 artifact-link pass, with separate denominators. | Metadata-only and replay rows remain separate; same-team checks are label hygiene, not inter-rater reliability. |
| Artifact Contract Team | Direction D artifact/demo/report-correctness manuscript. | Keep the generated public-safe risk card, report-language guard, and observed fault-injection table aligned with existing bundle/check paths. | Systems-effectiveness claims require report-drift, external-use, or deployment evidence. |

Each team may generate a distinct paper version when the scientific object
differs from the existing tracks. A new draft must answer a different reviewer
question from the table above; otherwise it is folded back into the owning
team's pitch, skeleton, or go/no-go memo. Each team may maintain only three
pre-TeX sections inside the existing brief/draft files: pitch, manuscript
skeleton, and go/no-go memo. Extra registers or TeX forks require a promotion
gate.

## Promotion-Review Checklist

Each team now owns a concrete paper-version review packet. The checklist below
is the next decision surface: a team can argue for promotion only by filling
the listed packet without weakening the shared evidence ledger.

| Team | Review packet | Evidence to cite | Promotion question | Blocking answer |
| --- | --- | --- | --- | --- |
| Evidence Contract Team | Full-paper readiness memo for `../main.tex`: title, abstract, contribution claims, figure/table list, and forbidden-claim scan. | `../data/claim_trace.csv`, `../data/source_provenance.csv`, `../claim_register.md`, current PDF checks, `drafts/direction-a-evidence-contract-paper.md`. | Does every headline claim map to an allowed trace row and a visible paper object? | Any leaderboard, homogeneous benchmark, interval, dominance, field-prevalence, or consumer-boundary H2 wording without trace support. |
| Response Geometry Team | Short-paper go/no-go memo: H2 result table, controls table, img2img boundary table, and one boundary paragraph. | H2 output-cloud metrics, label-shuffle, shared-position controls, cache-robustness rows, SD/CelebA img2img packet. | Does the H2 observable plus negative portability result support a scoped short paper? | Any need for same-cache feature sweeps, cross-model portability language, candidate-to-admitted wording, or hiding the img2img failure. |
| Artifact Claim-Support Team | Selected-corpus results skeleton: corpus construction, L0-L3 ladder, stratified gate table, query-hygiene caveat, targeted L1 sidecar, and label-hygiene caveat. | `../data/artifact_corpus_v1.csv`, `../data/artifact_corpus_fixed_search_20260526.csv`, `../data/artifact_corpus_broader_source_20260527.csv`, `../data/artifact_corpus_targeted_artifact_links_20260527.csv`, `../data/artifact_gate_summary.csv`, second-pass label review. | Can the paper state selected-corpus claim-support results with separate `21`, `17`, `10`, and three targeted-L1 rows? | Any pooled reproducibility/auditability rate, field-wide prevalence claim, hostile paper-failure framing, or inter-rater reliability claim. |
| Artifact Contract Team | Artifact/demo packet: generated public-safe risk card, observed fault-injection table, direct candidate-promotion language guard, and no-private-surface scan. | `../../../workspaces/implementation/artifacts/admitted-evidence-bundle.json`, `../../../workspaces/implementation/artifacts/admitted-risk-card.md`, `../../../scripts/render_admitted_risk_card.py`, `../../../scripts/check_public_surface.py`, existing bundle checks, public-surface check, claim register. | Does the package show how report language preserves replay tier, finite-tail caveats, and candidate blocking? | Any claim of deployed enforcement, drift reduction, external adoption, or systems effectiveness without report-drift/external-use/deployment evidence. |

Review packets should stay evidence-minimal. Packets that require new
validators, crawlers, downloads, GPU runs, or a second evidence ledger are no-go
for that direction.

## Manuscript Drafts

| Version | Draft |
| --- | --- |
| A | [`drafts/direction-a-evidence-contract-paper.md`](drafts/direction-a-evidence-contract-paper.md) |
| B | [`drafts/direction-b-output-cloud-short-paper.md`](drafts/direction-b-output-cloud-short-paper.md) |
| C | [`drafts/direction-c-artifact-reproducibility-paper.md`](drafts/direction-c-artifact-reproducibility-paper.md) |
| D | [`drafts/direction-d-audit-systems-paper.md`](drafts/direction-d-audit-systems-paper.md) |

## Direction C Corpus

| Artifact | Purpose |
| --- | --- |
| [`direction-c-corpus-protocol.md`](direction-c-corpus-protocol.md) | Frozen v0 inclusion rule and six-gate protocol. |
| [`direction-c-corpus-v1.md`](direction-c-corpus-v1.md) | Structured v1 metadata-only expansion from existing audited records. |
| [`../data/artifact_corpus_v1.csv`](../data/artifact_corpus_v1.csv) | Machine-readable 21-row corpus table for gate-matrix and claim-support drafting. |
| [`direction-c-fixed-search-batch-20260526.md`](direction-c-fixed-search-batch-20260526.md) | Separately frozen GitHub/arXiv metadata pass. |
| [`../data/artifact_corpus_fixed_search_20260526.csv`](../data/artifact_corpus_fixed_search_20260526.csv) | Machine-readable fixed-search batch table with inclusion, exclusion, and gate labels. |
| [`direction-c-broader-source-pass-20260527.md`](direction-c-broader-source-pass-20260527.md) | Separately frozen no-download Hugging Face Hub, Zenodo, and OpenReview API pass. |
| [`../data/artifact_corpus_broader_source_20260527.csv`](../data/artifact_corpus_broader_source_20260527.csv) | Machine-readable broader-source metadata observations; metadata-screening/query hygiene only, not source-completeness or prevalence evidence. |
| [`direction-c-targeted-artifact-link-pass-20260527.md`](direction-c-targeted-artifact-link-pass-20260527.md) | Targeted artifact-link chase over existing metadata-only seeds; three L1 public artifact surfaces, not score/metric replay. |
| [`../data/artifact_corpus_targeted_artifact_links_20260527.csv`](../data/artifact_corpus_targeted_artifact_links_20260527.csv) | Machine-readable targeted artifact-link rows; reported separately from the `21`, `17`, and `10` denominators. |
| [`direction-c-second-pass-label-review-20260526.md`](direction-c-second-pass-label-review-20260526.md) | Bounded second-pass label review/resolution; not independent human reliability. |
| [`../data/artifact_second_pass_label_review_20260526.csv`](../data/artifact_second_pass_label_review_20260526.csv) | Machine-readable second-pass disagreements and final resolutions. |
| [`../data/artifact_gate_summary.csv`](../data/artifact_gate_summary.csv) | Generated selected-corpus gate counts for Direction C boundary framing; not prevalence evidence. |
| [`../data/artifact_strata_summary.csv`](../data/artifact_strata_summary.csv) | Generated selected-corpus stratum and inclusion-decision counts. |
| [`../data/artifact_claim_support_rows.csv`](../data/artifact_claim_support_rows.csv) | Generated row-level L0-L3 claim-support labels for the selected corpus and fixed-search batch. |
| [`../data/artifact_claim_support_summary.csv`](../data/artifact_claim_support_summary.csv) | Generated L0-L3 claim-support counts: selected corpus `8/3/9/1`, fixed-search batch `13/4/0/0`. |
| [`../figures/artifact_gate_summary.pdf`](../figures/artifact_gate_summary.pdf) | Generated gate-count support figure; active Direction A now summarizes the counts in text. Selected-corpus only. |
| [`../figures/artifact_claim_support_summary.pdf`](../figures/artifact_claim_support_summary.pdf) | Generated L0-L3 claim-support figure for Direction C drafting; selected-corpus and fixed-search denominators are shown side by side, not pooled. |

## Selection Matrix

| Criterion | A: Evidence Contract | B: Output Cloud | C: Claim Support | D: Artifact Contract |
| --- | --- | --- | --- | --- |
| Uses current evidence honestly | Strong | Medium | Medium | Medium |
| Needs new model/data execution | Low | Medium-high | Low | Low |
| CCF-B+ plausibility now | Medium | Low unless scoped as short paper | Medium if claims stay selected-corpus only; higher needs larger distinct-surface corpus and, for reliability/adjudication claims, external label audit | Low-medium |
| Biggest missing piece | External-style reviewer polish plus larger corpus evidence for aggregate claims; replay/source-tier clarity is internally claim-audited | Second response asset | Larger distinct-surface frozen corpus; add external human label review only for reliability/adjudication claims | Report-renderer A/B drift reduction, external-use, or deployment evidence beyond bundle/risk-card fault injection and boundary no-drift audits |
| Overclaiming risk | Medium | High | Medium | Medium |
| Current action | Tighten `../main.tex`, collect C14 reviewer labels, and keep selected-set framing venue-grade | Keep as H2-limited short-paper draft | Use v1, GitHub/arXiv fixed-search, HF/Zenodo/OpenReview broader-source pass, targeted L1 artifact-link rows, gate-summary outputs, consistency pass, and second-pass review/resolution for L0-L3 claim-support drafting; new broad metadata sweeps need distinct artifact surfaces under the inclusion rule | Prepare artifact/demo/report-correctness package; next gap is report-drift/external-use/deployment evidence |

## Team Assignment Rule

Every direction has a named research team, but the team is a responsibility
split, not permission to add tooling. The lead owns the thesis and claim
boundary; the evidence engineer checks numbers and scripts; the figures editor
turns existing data into readable figures; the critic blocks overclaiming.

Each team may produce only three pre-TeX deliverables: a one-page pitch, a
manuscript skeleton, and a go/no-go memo. New LaTeX forks, validators, crawlers,
large downloads, or GPU runs are allowed only when the promotion gate says the
new evidence would change the paper decision.
