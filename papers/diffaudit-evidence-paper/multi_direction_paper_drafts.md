# Multi-Direction Paper Drafts

> Date: 2026-06-09
> Purpose: compare several paper versions from the same evidence while keeping
> one active LaTeX manuscript.

## Decision

Keep Direction A as the active LaTeX manuscript. Preserve Directions B, C, and
D as manuscript-level Markdown drafts until their go/no-go gates justify a TeX
fork. This gives the project several paper options while protecting the shared
claim boundary.

`versions/README.md` is the canonical operating board for version/team gates.
This file is a comparison memo; version gates stay there.

The versions ask different paper questions:

| Version | Primary reader question | Scientific object | Why it is distinct |
| --- | --- | --- | --- |
| A | When is a diffusion MIA score reusable audit evidence? | Evidence contract and admitted/candidate taxonomy | Turns the whole workspace into a measurement-methodology paper. |
| B | Is repeated-response geometry a real membership observable? | H2-only response-cloud observable | Treats one strong technical signal plus a negative portability gate as a bounded response-cloud short paper. |
| C | What do selected diffusion MIA artifact surfaces actually support? | Selected-corpus claim-support audit | Makes L0-L3 claim support the empirical object without field-wide prevalence or pooled reproducibility claims. |
| D | How should downstream reports consume privacy evidence safely? | Artifact contract and report-correctness threat model | Turns the evidence boundary into an artifact/demo/report-correctness package before any systems claim. |

## Version Set

| Direction | Research team | Paper identity | Current decision |
| --- | --- | --- | --- |
| A | Evidence Contract Team | Full security/privacy measurement paper | Primary 10-page LaTeX draft. Next gains come from reviewer-facing argument tightening, external C14 labeling from the prepared no-reviewer packet, corpus strengthening, or second row-bound score/response asset search. |
| B | Response Geometry Team | Response-cloud observable short/workshop paper | Strong bounded H2 observable with negative img2img portability failure as a main result; response-cloud schematic now anchors the boundary story; no full-paper portability claim until a second response asset appears. |
| C | Artifact Claim-Support Team | Selected-corpus L0-L3 claim-support measurement paper with stratified denominators | Current support includes the v1 metadata corpus, fixed GitHub/arXiv batch, HF/Zenodo/OpenReview broader-source API pass, three targeted L1 artifact-link seeds, gate-summary assets, generated claim-support summary figure, consistency pass, and bounded second-pass review. Standalone aggregate claims need stratified denominators plus a larger distinct-surface corpus; reliability/adjudication claims need external label audit. |
| D | Artifact Contract Team | Independent artifact-contract/report-correctness package | Treat as artifact/demo appendix with a generated risk card, selected fault-injection rows, and current artifact/demo packet summary; full systems framing still needs report-drift, external-use, or deployment evidence. |

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
| Evidence Contract Team | When does a diffusion MIA score become reusable audit evidence? | Strengthen [`main.tex`](main.tex) with selected-set framing, method detail, and reviewer-facing claims. | Claims must resolve through [`claim_register.md`](claim_register.md). |
| Response Geometry Team | Does repeated-response geometry expose membership beyond direct distance? | Keep H2 as a bounded short-paper observable with same-family wording and portability failure central. | Stop unless a second response asset or explicit short-paper scope exists. |
| Artifact Claim-Support Team | What claims do selected diffusion MIA artifact surfaces actually support? | Use v1, the 2026-05-26 GitHub/arXiv fixed-search batch, the 2026-05-27 HF/Zenodo/OpenReview broader-source API pass, the three targeted L1 artifact-link seeds, generated gate-summary counts, completed consistency pass, and bounded second-pass label-hygiene review/resolution for L0-L3 claim-support drafting. | Stop if aggregate claims exceed the selected corpus or pool metadata-only rows with replay rows. |
| Artifact Contract Team | How can report consumers avoid unsupported claim escalation? | Keep the generated risk card and observed fault-injection rows aligned with existing bundle/check paths while collecting report-drift, external-use, or deployment evidence. | Systems-paper framing needs measurable report-correctness benefit; validator work needs a decision-changing role. |

## Non-Overlap Contract

| Direction | Unique deliverable | Out of scope |
| --- | --- | --- |
| A | Final claim audit and 10-page evidence-contract manuscript. | Full H2 observable paper, field-wide artifact prevalence, deployed report-correctness measurement. |
| B | Short-paper H2 boundary draft with output-cloud controls and img2img portability failure. | Cross-model portability, reportable admission, or general diffusion attack status. |
| C | Stratified L0-L3 corpus table with selected-corpus gate counts. | Pooled reproducibility rate or field-wide artifact-quality prevalence. |
| D | Fault-injection/report artifact or public-safe risk-card package. | Applied systems effectiveness before report-drift, external-use, or deployment evidence. |

## Team Deliverable Contract

Each team is allowed to produce only three deliverables before a TeX fork:

| Deliverable | Required content | Anti-sprawl rule |
| --- | --- | --- |
| One-page pitch | title, thesis, venue posture, three contributions, one fatal risk | Cite existing evidence files; keep the shared ledger authoritative. |
| Manuscript skeleton | abstract, section plan, figure/table plan, claim boundaries | Markdown only until go/no-go passes. |
| Go/no-go memo | what new evidence would change the decision | No new CLI, validator, crawler, or GPU run unless it changes promotion. |

This keeps the "multiple paper versions" work tied to scientific strategy and
prevents documentation inflation.

## Shared Evidence Boundary

All versions must use the same evidence files:

- [`source_map.md`](source_map.md)
- [`claim_register.md`](claim_register.md)
- [`evidence_bank.md`](evidence_bank.md)
- [`data/claim_trace.csv`](data/claim_trace.csv)
- [`data/source_provenance.csv`](data/source_provenance.csv)

Candidate/support evidence keeps the shared state in every draft: H2 output-cloud
geometry, Tracing Roots, ReDiffuse, CommonCanvas, MIDST, CopyMark, CLiD, and
separately supplied SD ReDiffuse remain outside admitted evidence until their
own row-bound packets pass the contract.

## Next Work Order

1. Expand Direction A's LaTeX draft first.
2. Use Direction C v1 plus the GitHub/arXiv fixed-search metadata batch,
   HF/Zenodo/OpenReview broader-source API pass, three targeted L1 artifact-link
   seeds, gate-summary assets, selected-corpus consistency pass, and bounded
   second-pass label-hygiene review/resolution for L0-L3 claim-support drafting.
   Standalone aggregate claims need a larger distinct-surface corpus;
   reliability/adjudication claims need external label audit.
3. Keep Direction B as a short-paper-ready response-cloud draft with negative
   img2img portability central until a second response asset exists.
4. Keep Direction D as an independent artifact-contract/report-correctness package; the
   current generated risk card and selected fault-injection rows support artifact/demo
   packaging, while report-drift, external-use, or deployment evidence is still needed
   for systems-paper claims.
