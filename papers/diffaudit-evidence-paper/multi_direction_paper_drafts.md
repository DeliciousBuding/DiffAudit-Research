# Multi-Direction Paper Drafts

> Date: 2026-05-26
> Purpose: generate several distinct paper versions from the same evidence
> without creating a LaTeX maintenance mess.

## Decision

Keep Direction A as the active LaTeX manuscript. Preserve Directions B, C, and
D as manuscript-level Markdown drafts until their go/no-go gates justify a TeX
fork. This gives the project several paper options while protecting the shared
claim boundary.

## Version Set

| Direction | Research team | Paper identity | Current decision |
| --- | --- | --- | --- |
| A | Evidence Contract Team | Full security/privacy measurement paper | Primary. Expand the existing LaTeX draft to 6-8 pages. |
| B | Response Geometry Team | H2-limited mechanism short/workshop paper | Strong technical case study; no full-paper portability claim until a second response asset appears. |
| C | Artifact Reproducibility Team | Claim-support reproducibility/measurement paper | v1 metadata corpus, fixed-search batch, gate-summary assets, and selected-corpus consistency pass now exist; standalone aggregate claims need a larger corpus or second label review. |
| D | Audit Systems Team | Downstream systems/artifact/demo paper | Hold until deployment, user study, external adopter, or report-drift evidence exists. |

## Draft Files

| Direction | Draft |
| --- | --- |
| A | [`versions/drafts/direction-a-evidence-contract-paper.md`](versions/drafts/direction-a-evidence-contract-paper.md) |
| B | [`versions/drafts/direction-b-output-cloud-short-paper.md`](versions/drafts/direction-b-output-cloud-short-paper.md) |
| C | [`versions/drafts/direction-c-artifact-reproducibility-paper.md`](versions/drafts/direction-c-artifact-reproducibility-paper.md) |
| D | [`versions/drafts/direction-d-audit-systems-paper.md`](versions/drafts/direction-d-audit-systems-paper.md) |

## Cross-Team Allocation

| Team | Lead question | Immediate task | Stop rule |
| --- | --- | --- | --- |
| Evidence Contract Team | When does a diffusion MIA score become reusable audit evidence? | Strengthen [`main.tex`](main.tex) with corpus framing, method detail, and reviewer-facing claims. | Stop any claim that bypasses [`claim_register.md`](claim_register.md). |
| Response Geometry Team | Does repeated-response geometry expose membership beyond direct distance? | Keep H2 as a bounded case study and prepare short-paper draft language with same-family wording. | Stop unless a second response asset or explicit short-paper scope exists. |
| Artifact Reproducibility Team | What claims do public diffusion MIA artifacts actually support? | Use v1, the 2026-05-26 fixed-search batch, generated gate-summary counts, and the completed selected-corpus consistency pass for claim-control drafting. | Stop if aggregate claims exceed the selected corpus. |
| Audit Systems Team | How can runtime/report consumers avoid unsupported claim promotion? | Keep as downstream brief and collect report-drift or external-use evidence. | Stop if the paper only describes schema without measurable report-correctness benefit. |

## Shared Evidence Boundary

All versions must use the same evidence files:

- [`source_map.md`](source_map.md)
- [`claim_register.md`](claim_register.md)
- [`evidence_bank.md`](evidence_bank.md)

No version may independently upgrade H2 output-cloud geometry, Tracing Roots,
ReDiffuse, CommonCanvas, MIDST, CopyMark, CLiD, or collaborator SD ReDiffuse
from candidate/support evidence into admitted evidence.

## Next Work Order

1. Expand Direction A's LaTeX draft first.
2. Use Direction C v1 plus the fixed-search metadata batch, gate-summary
   assets, and selected-corpus consistency pass for claim-control drafting; add
   a broader source batch or second label review only for standalone submission.
3. Keep Direction B as a short-paper-ready H2 mechanism draft until a second
   response asset exists.
4. Keep Direction D as an artifact/demo brief until external-use or report-drift
   evidence exists.
