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
| `versions/direction-c-corpus-v1.md` | Structured Direction C corpus expansion from existing metadata-gate evidence notes. |
| `versions/direction-c-fixed-search-batch-20260526.md` | Independent fixed-search metadata batch for Direction C; no downloads, no clone, no model/data execution. |
| `source_map.md` | Authoritative evidence sources and forbidden moves. |
| `claim_register.md` | Allowed, support-only, and prohibited claims. |
| `evidence_bank.md` | Human-readable metric ledger for manuscript drafting. |
| `research_team_pitches.md` | A/B/C paper-team pitches and risks from read-only subagent review. |
| `BUILD.md` | Figure generation and LaTeX compile commands. |
| `scripts/build_paper_assets.py` | Rebuilds paper CSV/PDF figure assets from repository JSON artifacts. |
| `data/` | Generated CSV tables used by figures and LaTeX. |
| `data/artifact_corpus_v1.csv` | Direction C metadata-only corpus table; not a generated metric table. |
| `data/artifact_corpus_fixed_search_20260526.csv` | Direction C fixed-search corpus batch; curated metadata, not a generated metric table. |
| `data/artifact_gate_summary.csv` | Generated selected-corpus gate counts for Direction C claim-control framing; not prevalence evidence. |
| `data/artifact_strata_summary.csv` | Generated selected-corpus stratum and inclusion-decision counts. |
| `figures/` | Generated PDF figures. |
| `figures/artifact_gate_summary.pdf` | Generated gate-count figure used in `main.tex`; selected-corpus only, not field-wide prevalence. |
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
- Direction C: claim-support artifact reproducibility paper; it now has a
  21-row v1 corpus plus a fixed-search metadata batch, but still needs
  gate-label consistency review before standalone aggregate claims.
- Direction D: audit systems/artifact paper; it remains downstream material
  until deployment, external-use, user-study, or report-drift evidence exists.

## Academic Discipline

- Use only recorded metrics and cited sources.
- Keep candidate and admitted claims separate.
- Treat finite-tail low-FPR numbers as empirical packet readouts.
- Do not turn bounded negative scouts into universal negative claims.
- Treat the v1 artifact corpus as a structured starter corpus, not a complete
  survey of all diffusion or generative privacy papers.
- Treat the fixed-search batch as selection-process evidence, not prevalence
  evidence over the field.
