# DiffAudit Paper Versions

> Date: 2026-05-26
> Role: compare several publishable paper directions without creating parallel
> LaTeX sprawl.

This folder contains paper-version briefs and manuscript-level Markdown drafts.
The briefs define direction boundaries; [`drafts/`](drafts/) contains fuller
paper versions that can be promoted to LaTeX only after their go/no-go gates
are met. The shared evidence boundary remains:

- Use `../source_map.md` for admissible sources.
- Use `../claim_register.md` before promoting any statement.
- Use `../evidence_bank.md` for numbers.
- Treat `../main.tex` as the active Direction A LaTeX draft.

## Version Map

| Version | Team | Paper Type | Current Decision |
| --- | --- | --- | --- |
| A | Evidence Contract Team | Security/privacy measurement | Main manuscript now. |
| B | Response Geometry Team | Response-cloud mechanism short/workshop paper | Keep as second-track; negative img2img portability is central, and full-paper claims need a second response asset. |
| C | Artifact Claim-Support Team | Selected-corpus L0-L3 claim-support measurement paper | v1 corpus, GitHub/arXiv fixed-search batch, gate summary, and selected-corpus consistency pass exist; standalone aggregate claims need stratified denominators plus a broader corpus or second label review. |
| D | Artifact Contract Team | Independent artifact-contract/report-correctness package | Hold full systems claims until fault-injection, report-drift, external-use, or deployment evidence exists. |

## Research Team Operating Board

Each direction is assigned to a paper team with a distinct scientific object.
The team names are organizational handles for writing, evidence review, and
critique; they do not authorize new validators, crawlers, downloads, or GPU runs
unless the direction's promotion gate says the evidence would change.

| Direction | Team mandate | Lead roles | Next deliverable | Promotion gate | Stop rule |
| --- | --- | --- | --- | --- | --- |
| A | Turn the whole workspace into an evidence-contracted measurement paper. | Framework PI, metric-audit lead, figure editor, validity critic. | Tighten `../main.tex` around measurement motivation, selected-set framing, and reviewer-facing contribution language. | Final claim audit passes, PDF compiles at page budget, and every headline statement maps to `../claim_register.md`. | Stop any CCF-B pitch that reads as internal governance rather than measurement science. |
| B | Make H2 output-cloud geometry a bounded mechanism short paper. | Response-geometry lead, scorer engineer, mechanism visual lead, portability critic. | Keep the Markdown draft short-paper-ready with H2 controls and img2img portability failure as a main result. | A second independent response asset passes the six gates, or the team explicitly targets a short/workshop H2-only paper. | Stop same-cache feature sweeps, repeat tuning, or portability language without new evidence. |
| C | Measure claim-support levels over a frozen selected corpus. | Claim-support lead, provenance-audit lead, corpus table lead, selection-bias critic. | Use v1 corpus, fixed-search batch, gate summaries, and consistency pass to draft stratified L0-L3 results. | Broader frozen corpus or second independent label review exists before any standalone aggregate claim. | Stop any pooled reproducibility rate, field-wide prevalence claim, or hostile "paper failure" framing. |
| D | Package the evidence boundary as an artifact/report-correctness contract. | Contract architecture lead, bundle-validation lead, report-correctness lead, public-boundary critic. | Draft a public-safe artifact/demo version with admitted-only risk-card language and a fault-injection table plan. | Observed fault-injection, report-drift, external-use, or deployment evidence exists before systems-paper promotion. | Stop if the result is only a schema description without measurable report-correctness benefit. |

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
| [`direction-c-corpus-v1.md`](direction-c-corpus-v1.md) | Structured v1 metadata-only expansion from existing evidence notes. |
| [`../data/artifact_corpus_v1.csv`](../data/artifact_corpus_v1.csv) | Machine-readable 21-row corpus table for gate-matrix and claim-support drafting. |
| [`direction-c-fixed-search-batch-20260526.md`](direction-c-fixed-search-batch-20260526.md) | Independent fixed-search metadata batch over GitHub and arXiv. |
| [`../data/artifact_corpus_fixed_search_20260526.csv`](../data/artifact_corpus_fixed_search_20260526.csv) | Machine-readable fixed-search batch table with inclusion, exclusion, and gate labels. |
| [`../data/artifact_gate_summary.csv`](../data/artifact_gate_summary.csv) | Generated selected-corpus gate counts for Direction C claim-control framing; not prevalence evidence. |
| [`../data/artifact_strata_summary.csv`](../data/artifact_strata_summary.csv) | Generated selected-corpus stratum and inclusion-decision counts. |
| [`../figures/artifact_gate_summary.pdf`](../figures/artifact_gate_summary.pdf) | Generated gate-count figure for the active manuscript; selected-corpus only. |

## Selection Matrix

| Criterion | A: Evidence Contract | B: Output Cloud | C: Claim Support | D: Artifact Contract |
| --- | --- | --- | --- | --- |
| Uses current evidence honestly | Strong | Medium | Medium | Medium |
| Needs new model/data execution | Low | Medium-high | Low | Low |
| CCF-B+ plausibility now | Medium | Low unless scoped as short paper | Medium if claims stay selected-corpus only; higher needs broader corpus or second label review | Low-medium |
| Biggest missing piece | Stronger venue framing and method detail | Second response asset | Broader fixed-source pass or second independent label review if aiming standalone | Fault-injection, report-drift, external-use, or deployment evidence |
| Overclaiming risk | Medium | High | Medium | Medium |
| Current action | Tighten `../main.tex` and add venue-grade selected-set framing | Keep as H2-limited short-paper draft | Use v1, GitHub/arXiv fixed-search, gate-summary outputs, and selected-corpus consistency pass for L0-L3 claim-support drafting | Hold for artifact/demo/report-correctness package |

## Team Assignment Rule

Every direction has a named research team, but the team is a responsibility
split, not permission to add tooling. The lead owns the thesis and claim
boundary; the evidence engineer checks numbers and scripts; the figures editor
turns existing data into readable figures; the critic blocks overclaiming.
