# Multi-Direction Paper Drafts

> Date: 2026-05-26
> Purpose: generate several distinct paper versions from the same evidence
> without creating a LaTeX maintenance mess.

## Decision

Keep Direction A as the active LaTeX manuscript. Preserve Directions B, C, and
D as manuscript-level Markdown drafts until their go/no-go gates justify a TeX
fork. This gives the project several paper options while protecting the shared
claim boundary.

The versions are intentionally different papers, not four wordings of the same
paper:

| Version | Primary reader question | Scientific object | Why it is distinct |
| --- | --- | --- | --- |
| A | When is a diffusion MIA score reusable audit evidence? | Evidence contract and admitted/candidate taxonomy | Turns the whole workspace into a measurement-methodology paper. |
| B | Is repeated-response geometry a real membership observable? | H2 response-cloud mechanism candidate | Treats one strong technical signal as a bounded mechanism short paper. |
| C | What do selected diffusion MIA artifact surfaces actually support? | Selected-corpus claim-support audit | Makes claim support the empirical object without field-wide prevalence claims. |
| D | How should downstream reports consume privacy evidence safely? | Artifact contract and report-correctness threat model | Turns the evidence boundary into an artifact/demo paper before any systems claim. |

## Version Set

| Direction | Research team | Paper identity | Current decision |
| --- | --- | --- | --- |
| A | Evidence Contract Team | Full security/privacy measurement paper | Primary 8-page LaTeX draft; continue reviewer-facing tightening without forking other TeX manuscripts. |
| B | Response Geometry Team | H2-limited mechanism short/workshop paper | Strong technical case study; no full-paper portability claim until a second response asset appears. |
| C | Artifact Claim-Support Team | Selected-corpus claim-support measurement paper | v1 metadata corpus, fixed GitHub/arXiv batch, gate-summary assets, and selected-corpus consistency pass now exist; standalone aggregate claims need a larger corpus or second label review. |
| D | Artifact Contract Team | Artifact/demo contract paper | Hold full systems claims until fault-injection, report-drift, external-use, or deployment evidence exists. |

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
| Artifact Claim-Support Team | What claims do selected diffusion MIA artifact surfaces actually support? | Use v1, the 2026-05-26 GitHub/arXiv fixed-search batch, generated gate-summary counts, and the completed selected-corpus consistency pass for claim-control drafting. | Stop if aggregate claims exceed the selected corpus. |
| Artifact Contract Team | How can report consumers avoid unsupported claim promotion? | Keep as artifact/demo brief and collect fault-injection, report-drift, or external-use evidence. | Stop if the paper only describes schema without measurable report-correctness benefit. |

## Team Deliverable Contract

Each team is allowed to produce only three deliverables before a TeX fork:

| Deliverable | Required content | Anti-sprawl rule |
| --- | --- | --- |
| One-page pitch | title, thesis, venue posture, three contributions, one fatal risk | Must cite existing evidence files; no new source of truth. |
| Manuscript skeleton | abstract, section plan, figure/table plan, claim boundaries | Markdown only until go/no-go passes. |
| Go/no-go memo | what new evidence would change the decision | No new CLI, validator, crawler, or GPU run unless it changes promotion. |

This keeps the "multiple paper versions" work as scientific strategy rather
than documentation inflation.

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
2. Use Direction C v1 plus the GitHub/arXiv fixed-search metadata batch,
   gate-summary assets, and selected-corpus consistency pass for claim-control
   drafting; add a broader source batch or second label review only for
   standalone aggregate claims.
3. Keep Direction B as a short-paper-ready H2 mechanism draft until a second
   response asset exists.
4. Keep Direction D as an artifact/demo contract brief until fault-injection,
   report-drift, external-use, or deployment evidence exists.
