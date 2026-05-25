# DiffAudit Evidence Paper Workspace

This directory turns the current DiffAudit Research evidence into paper-grade
artifacts. It intentionally separates paper tracks from raw experiment
workspaces.

## Layout

| Path | Purpose |
| --- | --- |
| `paper_portfolio.md` | Candidate paper directions, teams, venues, risks, and immediate choice. |
| `multi_direction_paper_drafts.md` | Manuscript-level comparison of four paper versions and their research teams. |
| `versions/` | Direction-specific paper briefs with team assignment, abstract, outline, evidence boundary, and go/no-go criteria. |
| `versions/drafts/` | Full Markdown paper-version drafts for Directions A-D; only Direction A currently has LaTeX. |
| `versions/direction-c-corpus-protocol.md` | Frozen v0 metadata-only corpus protocol for the artifact reproducibility paper direction. |
| `source_map.md` | Authoritative evidence sources and forbidden moves. |
| `claim_register.md` | Allowed, support-only, and prohibited claims. |
| `evidence_bank.md` | Human-readable metric ledger for manuscript drafting. |
| `research_team_pitches.md` | A/B/C paper-team pitches and risks from read-only subagent review. |
| `BUILD.md` | Figure generation and LaTeX compile commands. |
| `scripts/build_paper_assets.py` | Rebuilds paper CSV/PDF figure assets from repository JSON artifacts. |
| `data/` | Generated CSV tables used by figures and LaTeX. |
| `figures/` | Generated PDF figures. |
| `main.tex` | Primary Direction A manuscript draft. |
| `refs.bib` | Initial bibliography for the manuscript draft. |
| `paper.pdf` | Current compiled PDF snapshot when built locally. |

## Current Primary Track

Direction A, "Evidence-Contracted Auditing", is the first manuscript because it
can use current positive, candidate, and negative evidence without pretending
that the project has already solved broad cross-asset generalization.
The competing paper versions are kept under `versions/` so later work can
advance one direction without duplicating the evidence register or claim rules.
The current paper-version drafts are:

- Direction A: evidence-contracted security/privacy measurement paper.
- Direction B: output-cloud geometry short/workshop paper; full-paper promotion
  requires a second independent response asset.
- Direction C: claim-support artifact reproducibility paper; promotion requires
  metadata-only corpus expansion beyond DiffAudit history.
- Direction D: audit systems/artifact paper; promotion requires deployment,
  external-use, user-study, or report-drift evidence.

## Academic Discipline

- Use only recorded metrics and cited sources.
- Keep candidate and admitted claims separate.
- Treat finite-tail low-FPR numbers as empirical packet readouts.
- Do not turn bounded negative scouts into universal negative claims.
