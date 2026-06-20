# DiffAudit Evidence Paper Workspace

This directory turns the current DiffAudit evidence into paper-grade
artifacts. It intentionally separates paper tracks from raw experiment
workspaces.

## Layout

| Path | Purpose |
| --- | --- |
| `versions/README.md` | Canonical A-D paper-version and research-team operating board. |
| `versions/` | Direction-specific paper briefs with team assignment, abstract, outline, evidence boundary, and go/no-go criteria. |
| `versions/drafts/` | Full Markdown paper-version drafts for Directions A-D; only Direction A currently has LaTeX. |
| `paper_portfolio.md` | Reader-facing portfolio summary; secondary to `versions/README.md`. |
| `multi_direction_paper_drafts.md` | Manuscript-level comparison memo; secondary to `versions/README.md`. |
| `versions/direction-c-corpus-protocol.md` | Frozen v0 metadata-only corpus protocol for the artifact claim-support paper direction. |
| `versions/direction-c-corpus-v1.md` | Structured Direction C corpus expansion from existing metadata-gate evidence notes. |
| `versions/direction-c-fixed-search-batch-20260526.md` | Separately frozen GitHub/arXiv metadata pass for Direction C; no downloads, no clone, no model/data execution. |
| `versions/direction-c-broader-source-pass-20260527.md` | No-download Hugging Face Hub, Zenodo, and OpenReview metadata-screening/query pass for Direction C. |
| `versions/direction-c-targeted-artifact-link-pass-20260527.md` | Targeted artifact-link pass for Direction C; three non-pooled L1 public artifact surfaces. |
| `versions/direction-c-second-pass-label-review-20260526.md` | Bounded Direction C second-pass label review; label hygiene only, not independent human reliability. |
| `versions/direction-a-false-promotion-audit-codebook.md` | Direction A external-style false-promotion review codebook; protocol only, not completed external adjudication. |
| `versions/direction-a-c14-external-review-launch-protocol.md` | C14 launch protocol for reviewer independence, stop rules, aggregation, and reporting boundaries. |
| `versions/direction-a-claim-gate-recode-protocol.md` | C1-C15 claim-gate recode protocol; prepared recode material only, not a reliability result. |
| `versions/direction-a-mofit-public-score-surface.md` | Direction A MoFit public COCO score-surface replay boundary note; support-only public score replay, not admitted evidence. |
| `source_map.md` | Authoritative evidence sources and forbidden moves. |
| `claim_register.md` | Allowed, support-only, and prohibited claims. |
| `evidence_bank.md` | Human-readable metric ledger for manuscript drafting. |
| `research_team_pitches.md` | A-D paper-team pitch book; secondary to `versions/README.md`. |
| `BUILD.md` | Figure generation and LaTeX compile commands. |
| `scripts/build_paper_assets.py` | Rebuilds generated CSV sidecars, claim-trace/provenance tables, PDF figures, and `asset_manifest.json` from existing repository artifacts and frozen evidence notes. |
| `asset_manifest.json` | Generated, curated, and paper-source inventory plus the source and validation policies used by `build_paper_assets.py`. |
| `data/` | Generated CSV tables used by figures and LaTeX. |
| `data/admitted_rows.csv` | Generated reportable-row metric table with access, report-role, and replay-tier fields for the role-separated figure. |
| `data/metric_uncertainty.csv` | Generated AUC uncertainty sidecar for rows with direct score arrays or recorded H2 aggregate CIs; not all rows have intervals. |
| `data/claim_trace.csv` | Generated per-claim trace records tying claim IDs to sources, replay tiers, six explicit gate columns, blockers, states, and allowed wording. |
| `data/manuscript_claim_audit.csv` | Generated manuscript claim-anchor audit tying high-risk paper phrases to current data sidecars; an integrity check, not external review evidence. |
| `data/citation_context_audit.csv` | Generated citation-context inventory tying every `main.tex` citation command to its intended claim role and expected source support; metadata-verified context audit only, not full-text L3 adjudication. |
| `data/claim_gate_recode_template.csv` | Generated shuffled blank C1-C15 recode template for future independent gate-label consistency checks; no labels are filled. |
| `data/claim_gate_recode_packet_manifest.csv` | Generated hash manifest for the blank recode template and author-coded claim trace source; not reviewer evidence by itself. |
| `data/source_provenance.csv` | Generated local artifact identity table with SHA-256 hashes, repository commit IDs, tree state, generator command, and availability tiers. |
| `data/review_snapshot_manifest.csv` | Generated local review-snapshot byte manifest over anonymous-release packet inputs; not clean public release provenance. |
| `data/artifact_corpus_v1.csv` | Direction C metadata-only corpus table; not a generated metric table. |
| `data/artifact_corpus_fixed_search_20260526.csv` | Direction C fixed-search corpus batch; curated metadata, not a generated metric table. |
| `data/artifact_corpus_broader_source_20260527.csv` | Direction C broader-source API metadata observations; metadata-screening/query hygiene only, not source-completeness or prevalence evidence. |
| `data/artifact_corpus_targeted_artifact_links_20260527.csv` | Direction C targeted artifact-link rows; three L1 artifact surfaces, not score replay or a pooled denominator. |
| `data/artifact_second_pass_label_review_20260526.csv` | Direction C second-pass disagreements and same-team resolutions; not a generated metric table. |
| `data/artifact_gate_summary.csv` | Generated selected-corpus gate counts for Direction C claim-control framing; not prevalence evidence. |
| `data/artifact_strata_summary.csv` | Generated selected-corpus stratum and inclusion-decision counts. |
| `data/artifact_claim_support_rows.csv` | Generated row-level L0-L3 claim-support labels for Direction C selected-corpus drafting. |
| `data/artifact_claim_support_summary.csv` | Generated L0-L3 claim-support counts for selected-corpus and fixed-search denominators; not a pooled reproducibility rate. |
| `data/false_promotion_exemplars.csv` | Generated E2 author-keyed weak-rule stress rows derived from thirteen no-download gap-board/post-C14 checks; not denominator or admitted evidence. |
| `data/false_promotion_rule_summary.csv` | Generated pre-label stress-control counts for code, artifact, paper-link, metric/split, and score-only shortcut pressure. |
| `data/false_promotion_blinded_review_packet.csv` | Generated blocker-blinded row packet for independent false-promotion review; primary reviewer input, not completed adjudication. |
| `data/false_promotion_row_trace.csv` | Generated C14 row-level trace with public URLs, no-download evidence-note paths, observation dates, and hashes. |
| `data/false_promotion_external_review_template.csv` | Generated blank reviewer decision template for the thirteen false-promotion rows. |
| `data/false_promotion_adjudication_key.csv` | Generated same-team blocker and allowed-wording key for post-label comparison; not external labels. |
| `data/false_promotion_external_review_packet.csv` | Generated author-keyed row packet retained for audit traceability; not the first file for independent review. |
| `data/false_promotion_author_gate_matrix.csv` | Generated author-keyed C14 gate labels for post-label comparison; not external adjudication or reliability evidence. |
| `data/false_promotion_gate_summary.csv` | Generated author-keyed gate counts over the selected stress rows; not prevalence, denominator, or reliability evidence. |
| `data/mofit_public_gate_status.csv` | Generated six-gate status for the MoFit public score-surface replay; machine-readable support-only boundary only, not admission. |
| `data/mofit_public_caption_position_manifest.csv` | Generated support-only caption-order anchors for MoFit score positions; not certified row binding or admitted evidence. |
| `figures/` | Generated PDF figures. |
| `figures/artifact_gate_summary.pdf` | Generated gate-count support figure; the active `main.tex` summarizes these counts in text to preserve page budget and visual clarity. Selected-corpus only, not field-wide prevalence. |
| `figures/artifact_claim_support_summary.pdf` | Generated Direction C L0-L3 claim-support figure; selected-corpus and fixed-search denominators are plotted side by side and never pooled. |
| `figures/false_promotion_exemplars.pdf` | Generated weak-rule false-promotion matrix for thirteen E2 controls; not a performance figure. |
| `figures/false_promotion_gate_matrix.pdf` | Generated author-keyed C14 gate matrix for internal post-label comparison; kept out of the main paper and anonymous supplement to avoid presenting author labels as external adjudication. |
| `main.tex` | Primary Direction A manuscript draft. |
| `refs.bib` | Manuscript bibliography; the release checker enforces cited-key/ref-key alignment and required BibTeX fields. |
| `paper.pdf` | Current compiled PDF snapshot when built locally. |

`build_paper_assets.py` also validates the claim-trace/provenance contract:
gate columns must use only `Pass`, `Partial`, `Fail`, or `N/A`, and every
`provenance_id` must resolve to a hashed source-provenance row.
Use `asset_manifest.json` as the complete generated/curated/source inventory;
the table above lists the paper-facing entry points. `asset_manifest.json`
covers every CSV, figure, and source file.

## Reviewer Audit Entry

To audit a headline claim without reading raw experiment workspaces:

1. Open `data/claim_trace.csv` and find the `claim_id` referenced by the paper
   or claim register.
2. Check the six gate columns, `first_blocker`, `evidence_state`, and
   `allowed_wording`; the prose must not exceed that row.
3. Follow `provenance_ids` into `data/source_provenance.csv` and verify the
   listed hash, repository identity, generator command, and availability tier.
4. Open `data/citation_context_audit.csv` for the cited sentence. It maps each
   `main.tex` citation command to the intended claim role, expected source
   support, and boundary note. The file is a citation-context inventory; it does
   not claim full-text L3 adjudication.
5. If `source_provenance.csv` reports a dirty tree, verify
   `data/review_snapshot_manifest.csv` as the byte identity of this local review
   packet. It does not upgrade public redistributability, admission, or replay
   tier.
6. Use `asset_manifest.json` to confirm the generated, curated, and paper-source
   files that must be packaged with an anonymous supplement, excluding paths
   listed under `anonymous_supplement_excluded`.
   After export, use `build/anonymous_supplement_manifest.csv` for the packaged
   byte hashes of generated figures, `paper.pdf`, and other archive entries.
7. Run `python -X utf8 scripts\check_paper_release_packet.py` from the
   repository root before treating `paper.pdf` as current; this also checks that
   `main.tex` and `refs.bib` have no missing, unused, or placeholder references.
   For C14 before reviewer labels are returned, the generated
   `build/false_promotion_external_review_packet_status.csv` must still read
   `packet_label_readiness=prepared_no_reviewer_csvs`,
   `reviewer_count_status=none`, `n_reviewers=0`, and
   `allowed_claim_scope=packet_ready_only`, with external-adjudication,
   reliability, and compute-release switches set to `0`.

## Anonymous Supplement Boundary

The anonymous manuscript supplement should package generated, curated, and
paper-source paths listed in `asset_manifest.json`, plus `paper.pdf`, except
paths listed under `anonymous_supplement_excluded`. The excluded C14
author-key/post-label files remain maintainer-only until labels and
declarations are final, while `reviewer_packet_allowed_prelabel` identifies
the pre-label reviewer navigation/preparation files allowed in the anonymous
supplement. The manifest's `anonymous_supplement_policy` is the release
boundary: local `source_provenance.csv` paths, dirty tree state, and
generator commands identify the packet used for reviewer audit, but they are
not public-redistribution, clean-release-provenance, or stronger-replay claims
and do not upgrade any candidate, support-only, or permission-bound row.

Use `versions/README.md` as the paper-direction index. Keep secondary
portfolio/pitch views in sync only when they help a reader compare options.

## Current Primary Track

Direction A, "Evidence-Contracted Measurement", is the first manuscript because it
uses the current positive, candidate, and negative evidence as claim-bound
measurement material. Reportable rows keep their replay or source tier.
Candidate and support rows enter as boundary cases with explicit first blockers.

The E2 no-download checks add a thirteen-row author-keyed C14 stress object.
Those rows cover weak public-surface triggers across code, artifacts,
paper links, metric/split hints, gated starters, adjacent-task claims, mock
demo scores, code snapshots, and repository stubs. C14 is a pre-label
packet-readiness object; denominator, admission, prevalence, and compute-release
statements require separate evidence.
The accompanying hard-blind reviewer ZIP contains only the blocker-blinded
packet, reviewer-safe row trace, blank template, generated reviewer public-URL
table, reviewer declaration, codebook, and launch protocol. These are review
preparation artifacts. External adjudication, reviewer reliability, denominator
evidence, and prevalence require completed independent labels and declarations.
Author-key/post-label C14 files listed in `maintainer_only_author_key` and
`anonymous_supplement_excluded` are packaged separately in the maintainer-only
post-label key ZIP under `post-label-author-key/` and must not be shared until
labels and declarations are final.
The 2026-06-08 and 2026-06-09 public-surface refreshes are recorded as support
and route closures only. MoFit remains a support-only public score-file replay
blocked by row-binding and target-identity gates. NDSS-324, SD-MIA, MIA_SD,
SAMA, MIA-EPT, Diffusion MIA, ReMIA, OpenLVLM-MIA, and the high-value public
asset delta refresh leave current C14, N50, admitted-evidence, second-asset, and
compute-release status unchanged. OpenLVLM-MIA is a future VLM
controlled-benchmark scout outside the current Direction A image-diffusion
evidence lane.
The competing paper versions are kept under `versions/` so later work can
advance one direction without duplicating the evidence register or claim rules.
The current paper-version drafts are:

- Direction A: evidence-contracted security/privacy measurement paper.
- Direction B: output-cloud geometry short/workshop paper; full-paper promotion
  requires a second independent response asset.
- Direction C: selected-corpus claim-support measurement paper; it now has a
  21-row v1 corpus, a 17-row GitHub/arXiv fixed-search metadata batch, a
  10-row HF/Zenodo/OpenReview broader-source API pass, gate-summary outputs,
  one targeted artifact-link pass that recovered three public artifact surfaces
  from existing metadata-only rows,
  and label-hygiene review. The consistency pass found no invalid labels or
  route-changing contradictions; the bounded second-pass label review found no
  admitted-like fixed-search row or metadata-batch evidence/metric promotion and
  adopted two gate tightenings. Standalone aggregate claims still require a
  larger distinct-surface corpus; the targeted HF, SecMI GitHub, and MIDM GitHub
  artifacts are L1 seeds, not an aggregate result. Reliability claims require an external label audit
  protocol. Current same-team checks are label hygiene, not reliability evidence.
- Direction D: artifact/demo/report-correctness paper; it now has generated
  risk-card, selected fault-injection, and candidate-promotion language-guard
  evidence, but remains downstream material until report-drift, external-use,
  or deployment evidence exists.

## Academic Discipline

- Use only recorded metrics and cited sources.
- Keep candidate and admitted claims separate.
- Treat finite-tail low-FPR numbers as empirical packet readouts.
- Keep bounded negative scouts tied to their audited route.
- Treat the v1 artifact corpus as a structured starter corpus, not a complete
  survey of all diffusion or generative privacy papers.
- Treat the fixed-search batch as selection-process evidence, not prevalence
  evidence over the field.
- Treat the broader-source batch as metadata-screening/query hygiene; most rows are
  empty/noisy/duplicate API observations, not artifact inspections or replay
  attempts.
- Treat the targeted artifact-link rows as non-pooled L1 inspection sidecars;
  they do not support score replay, metric reproduction, admission, or corpus
  prevalence claims.
