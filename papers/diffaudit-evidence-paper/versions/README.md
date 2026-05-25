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
| C | Artifact Reproducibility Team | Claim-support measurement paper | v0 corpus protocol frozen; expand metadata-only beyond project history. |
| D | Audit Systems Team | Systems/artifact paper | Hold until deployment, user-study, external-use, or report-drift evidence exists. |

## Manuscript Drafts

| Version | Draft |
| --- | --- |
| A | [`drafts/direction-a-evidence-contract-paper.md`](drafts/direction-a-evidence-contract-paper.md) |
| B | [`drafts/direction-b-output-cloud-short-paper.md`](drafts/direction-b-output-cloud-short-paper.md) |
| C | [`drafts/direction-c-artifact-reproducibility-paper.md`](drafts/direction-c-artifact-reproducibility-paper.md) |
| D | [`drafts/direction-d-audit-systems-paper.md`](drafts/direction-d-audit-systems-paper.md) |

## Selection Matrix

| Criterion | A: Evidence Contract | B: Output Cloud | C: Artifact Repro | D: Audit Systems |
| --- | --- | --- | --- | --- |
| Uses current evidence honestly | Strong | Medium | Medium | Medium |
| Needs new model/data execution | Low | Medium-high | Low | Low |
| CCF-B+ plausibility now | Medium | Low unless scoped as short paper | Medium if corpus is expanded under frozen protocol | Low-medium |
| Biggest missing piece | Stronger venue framing and method detail | Second response asset | Broader frozen corpus beyond v0 | External/deployment evidence |
| Overclaiming risk | Medium | High | Medium | Medium |
| Current action | Tighten `../main.tex` and add venue-grade corpus framing | Keep as case study or short-paper draft | Expand [`direction-c-corpus-protocol.md`](direction-c-corpus-protocol.md) metadata-only | Hold for artifact/demo |

## Team Assignment Rule

Every direction has a named research team, but the team is a responsibility
split, not permission to add tooling. The lead owns the thesis and claim
boundary; the evidence engineer checks numbers and scripts; the figures editor
turns existing data into readable figures; the critic blocks overclaiming.
