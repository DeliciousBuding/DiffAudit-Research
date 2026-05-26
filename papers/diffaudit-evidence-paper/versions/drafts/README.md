# Direction Drafts

> Date: 2026-05-26
> Purpose: preserve several paper versions without forking four LaTeX trees.

These files are manuscript-level drafts, not only direction notes. They are
designed to let the team compare four publishable storylines while keeping one
shared evidence ledger:

- [`../../source_map.md`](../../source_map.md)
- [`../../claim_register.md`](../../claim_register.md)
- [`../../evidence_bank.md`](../../evidence_bank.md)

The active LaTeX manuscript remains [`../../main.tex`](../../main.tex), which
implements Direction A. A new LaTeX fork is allowed only when a direction passes
the go/no-go gate in its draft.

## Draft Map

| Draft | Research team | Intended paper | Current use |
| --- | --- | --- | --- |
| [`direction-a-evidence-contract-paper.md`](direction-a-evidence-contract-paper.md) | Evidence Contract Team | Security/privacy measurement paper | Primary full-paper track. |
| [`direction-b-output-cloud-short-paper.md`](direction-b-output-cloud-short-paper.md) | Response Geometry Team | H2-limited mechanism short/workshop paper | Strong case-study track, no full-paper portability claim yet. |
| [`direction-c-artifact-reproducibility-paper.md`](direction-c-artifact-reproducibility-paper.md) | Artifact Claim-Support Team | Selected-corpus claim-support measurement paper | v1 plus GitHub/arXiv fixed-search batch, selected-corpus consistency pass, and bounded second-pass adjudication exist; standalone aggregate claims need stratified denominators plus broader corpus or external review. |
| [`direction-d-audit-systems-paper.md`](direction-d-audit-systems-paper.md) | Artifact Contract Team | Downstream artifact/demo/report-correctness package | Hold full systems claims until fault-injection, report-drift, external-use, or deployment evidence exists. |

## Global Guardrails

1. Do not split the evidence bank per draft.
2. Do not promote H2 output-cloud geometry to admitted evidence.
3. Do not present bounded weak scouts as failed reproductions of original papers.
4. Do not report finite low-FPR tails as calibrated continuous sub-percent rates.
5. Do not start heavyweight downloads or GPU runs for paper symmetry.
