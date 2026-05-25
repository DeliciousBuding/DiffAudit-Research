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
| B | Response Geometry Team | Mechanism short/workshop paper | Keep as second-track; needs second response asset for full paper. |
| C | Artifact Reproducibility Team | Claim-support measurement paper | v1 corpus, fixed-search batch, gate summary, and selected-corpus consistency pass exist; standalone aggregate claims need a broader corpus or second label review. |
| D | Audit Systems Team | Systems/artifact paper | Downstream brief only; hold until deployment, user-study, external-use, or report-drift evidence exists. |

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
| [`../data/artifact_corpus_v1.csv`](../data/artifact_corpus_v1.csv) | Machine-readable 21-row corpus table for gate-matrix and failure-taxonomy drafting. |
| [`direction-c-fixed-search-batch-20260526.md`](direction-c-fixed-search-batch-20260526.md) | Independent fixed-search metadata batch over GitHub and arXiv. |
| [`../data/artifact_corpus_fixed_search_20260526.csv`](../data/artifact_corpus_fixed_search_20260526.csv) | Machine-readable fixed-search batch table with inclusion, exclusion, and gate labels. |
| [`../data/artifact_gate_summary.csv`](../data/artifact_gate_summary.csv) | Generated selected-corpus gate counts for Direction C claim-control framing; not prevalence evidence. |
| [`../data/artifact_strata_summary.csv`](../data/artifact_strata_summary.csv) | Generated selected-corpus stratum and inclusion-decision counts. |
| [`../figures/artifact_gate_summary.pdf`](../figures/artifact_gate_summary.pdf) | Generated gate-count figure for the active manuscript; selected-corpus only. |

## Selection Matrix

| Criterion | A: Evidence Contract | B: Output Cloud | C: Artifact Repro | D: Audit Systems |
| --- | --- | --- | --- | --- |
| Uses current evidence honestly | Strong | Medium | Medium | Medium |
| Needs new model/data execution | Low | Medium-high | Low | Low |
| CCF-B+ plausibility now | Medium | Low unless scoped as short paper | Medium if claims stay selected-corpus only; higher needs broader corpus or second label review | Low-medium |
| Biggest missing piece | Stronger venue framing and method detail | Second response asset | Broader fixed-source pass or second independent label review if aiming standalone | External/deployment evidence |
| Overclaiming risk | Medium | High | Medium | Medium |
| Current action | Tighten `../main.tex` and add venue-grade corpus framing | Keep as H2-limited short-paper draft | Use v1, fixed-search, gate-summary outputs, and selected-corpus consistency pass for claim-control drafting | Hold for artifact/demo |

## Team Assignment Rule

Every direction has a named research team, but the team is a responsibility
split, not permission to add tooling. The lead owns the thesis and claim
boundary; the evidence engineer checks numbers and scripts; the figures editor
turns existing data into readable figures; the critic blocks overclaiming.
