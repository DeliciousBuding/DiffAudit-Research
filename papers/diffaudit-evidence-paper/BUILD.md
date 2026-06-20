# Build Notes

## Generate Paper Assets

Run from the Research repository root:

```powershell
python -X utf8 .\papers\diffaudit-evidence-paper\scripts\build_paper_assets.py
```

This rebuilds:

- `data/admitted_rows.csv`
- `data/h2_output_cloud_rows.csv`
- `data/negative_support_rows.csv`
- `data/metric_uncertainty.csv`
- `data/artifact_gate_summary.csv`
- `data/artifact_strata_summary.csv`
- `data/artifact_claim_support_rows.csv`
- `data/artifact_claim_support_summary.csv`
- `data/false_promotion_exemplars.csv`
- `data/false_promotion_rule_summary.csv`
- `data/false_promotion_external_review_packet.csv`
- `data/false_promotion_blinded_review_packet.csv`
- `data/false_promotion_adjudication_key.csv`
- `data/false_promotion_external_review_template.csv`
- `data/false_promotion_row_trace.csv`
- `data/false_promotion_author_gate_matrix.csv`
- `data/false_promotion_gate_summary.csv`
- `data/claim_trace.csv`
- `data/manuscript_claim_audit.csv`
- `data/source_provenance.csv`
- `data/review_snapshot_manifest.csv`
- `figures/admitted_rows_metrics.pdf`
- `figures/h2_output_cloud_controls.pdf`
- `figures/evidence_contract_pipeline.pdf`
- `figures/artifact_gate_summary.pdf`
- `figures/artifact_claim_support_summary.pdf`
- `figures/false_promotion_exemplars.pdf`
- `figures/false_promotion_gate_matrix.pdf`
- `asset_manifest.json`

The script also validates the paper evidence contract while generating assets:
claim-trace gate columns must use only `Pass`, `Partial`, `Fail`, or `N/A`, and
every `provenance_id` referenced by `data/claim_trace.csv` must resolve to a
hashed row in `data/source_provenance.csv`.
The generated `data/manuscript_claim_audit.csv` also ties high-risk manuscript
phrases to their data sidecars; it is an integrity check, not an external
review result.
When `source_provenance.csv` records a dirty tree, the generated
`data/review_snapshot_manifest.csv` records byte hashes and git-status identity
for the local review packet. It is not clean public release provenance.

## Compile Paper

If `latexmk` is unavailable, use the manual chain:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
bibtex build/main
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
Copy-Item -LiteralPath .\build\main.pdf -Destination .\paper.pdf -Force
```

The current verified compile path produced a 10-page letter-paper `paper.pdf`
on 2026-06-08 after the C14 thirteen-row author-keyed false-promotion stress
controls, semantic-boundary controls, and table/figure layout pass.

## Pre-Submission Sanity Checks

Run these checks before claiming the PDF is submission-ready:

```powershell
pdfinfo .\paper.pdf | Select-String 'Pages|Page size'
pdffonts .\paper.pdf
Select-String -Path .\build\main.log -Pattern 'Undefined|Citation.*undefined|Reference.*undefined|Overfull|LaTeX Warning'
pdftotext .\paper.pdf - | Select-String -Pattern 'D:\\|C:\\|Users\\|Documents\\|secret|token|product[- ]ready|disprove|field-wide prevalence|measurement error|scientifically useful|should not be described|should use the narrower claim|public MoFit score-surface replay|Public COCO score replay|hard-blind reviewer packet|support shortcut wording|H2-family packet is positive' -Context 0,1
```

For rendered layout QA of the current critical pages:

```powershell
pdftoppm -png -r 160 -f 1 -l 1 .\paper.pdf .\build\qa-page
pdftoppm -png -r 160 -f 3 -l 3 .\paper.pdf .\build\qa-page
pdftoppm -png -r 160 -f 5 -l 5 .\paper.pdf .\build\qa-page
pdftoppm -png -r 160 -f 8 -l 8 .\paper.pdf .\build\qa-page
pdftoppm -png -r 160 -f 9 -l 9 .\paper.pdf .\build\qa-page
pdftoppm -png -r 160 -f 10 -l 10 .\paper.pdf .\build\qa-page
```

Page 1 contains the abstract and contribution framing; pages 3 and 5 contain
the densest claim/corpus tables and the C14 false-promotion matrix; pages 8
through 10 contain the final discussion, conclusion, and references. The
2026-06-07 visual QA should re-check these pages after any C14 table/figure
edit.

From the repository root, also run:

```powershell
python -X utf8 scripts\check_paper_release_packet.py
python -X utf8 scripts\export_paper_supplement.py --check
python -X utf8 scripts\export_false_promotion_review_bundle.py --check
python -X utf8 scripts\export_false_promotion_review_bundle.py --check-output
python -X utf8 scripts\run_pr_checks.py
git diff --check
```

## Export Anonymous Supplement

After rebuilding paper assets and compiling `paper.pdf`, export the anonymous
supplement packet from the repository root:

```powershell
python -X utf8 scripts\export_paper_supplement.py
```

This writes:

- `papers/diffaudit-evidence-paper/build/diffaudit-evidence-paper-anonymous-supplement.zip`
- `papers/diffaudit-evidence-paper/build/anonymous_supplement_manifest.csv`
- `papers/diffaudit-evidence-paper/build/diffaudit-evidence-paper-anonymous-supplement.zip.sha256`

The ZIP includes the generated, curated, and paper-source paths listed in
`asset_manifest.json`, except paths listed under
`anonymous_supplement_excluded`, plus `asset_manifest.json`, `paper.pdf`, and a
supplement manifest inside the archive. It does not include raw local
workspaces, permission-bound source artifacts, C14 maintainer-only author-key
files, or evidence beyond the release boundary declared in `asset_manifest.json`.

## Export False-Promotion Review Bundle

To prepare the C14 reviewer packet from the repository root:

```powershell
python -X utf8 scripts\export_false_promotion_review_bundle.py
```

This writes:

- `papers/diffaudit-evidence-paper/build/diffaudit-false-promotion-review-bundle.zip`
- `papers/diffaudit-evidence-paper/build/false_promotion_review_bundle_manifest.csv`
- `papers/diffaudit-evidence-paper/build/diffaudit-false-promotion-review-bundle.zip.sha256`
- `papers/diffaudit-evidence-paper/build/diffaudit-false-promotion-post-label-key.zip`
- `papers/diffaudit-evidence-paper/build/false_promotion_post_label_key_manifest.csv`
- `papers/diffaudit-evidence-paper/build/diffaudit-false-promotion-post-label-key.zip.sha256`

The reviewer bundle contains only prepared pre-label review materials. It is not completed
external adjudication, reviewer reliability evidence, an N50 denominator,
admitted score/response evidence, or compute release. The primary reviewer
entry is `data/false_promotion_blinded_review_packet.csv`; `REVIEWER_README.md`
gives the launch instructions and filename convention; `REVIEWER_PUBLIC_URLS.csv`
gives a key-free URL table with reviewer-facing URL notes; `REVIEWER_DECLARATION.md` provides the
machine-checkable declaration template; and `data/false_promotion_row_trace.csv` records reviewer-safe
public URLs, observation dates, and boundary notes for navigation.
`false_promotion_review_bundle_manifest.csv` and the ZIP's
`REVIEW_BUNDLE_MANIFEST.csv` list both the source-backed reviewer files and
the generated reviewer aids (`REVIEWER_README.md`, `REVIEWER_DECLARATION.md`,
`REVIEWER_PUBLIC_URLS.csv`, and the sanitized reviewer row trace).
URL notes are launch hygiene only: they flag known accessibility issues, such
as a related GitHub URL that was already observed as `404`, without changing
the row label or adding evidence.
The reviewer bundle is hard-blind: it does not contain the author-keyed
materials packaged separately under the post-label key ZIP's
`post-label-author-key/` directory.
The author-keyed packet, adjudication key, gate matrix, gate-summary figure,
source rows, rule summary, full row trace, claim trace, source provenance,
claim register, and cached evidence notes are packaged separately in
`diffaudit-false-promotion-post-label-key.zip` for maintainer-only post-label
comparison and traceability. Do not share the post-label key ZIP with reviewers
until their labels and declarations are final.
The bundle also includes
`versions/direction-a-c14-external-review-launch-protocol.md`, which defines
reviewer independence, return-file naming, maintainer intake, reporting
boundaries, and stop rules. The generated `REVIEWER_README.md` also includes a
short cover note and checklist for real reviewer launch. These are launch
materials only; LLM/AI-assisted, model-generated, synthetic, same-team, or
author-key labels must not be reported as external reviewer evidence.

After exporting the bundle, validate the written ZIP/manifest/sha bytes against
current source files:

```powershell
python -X utf8 scripts\export_false_promotion_review_bundle.py --check-output
```

## Aggregate False-Promotion Reviewer Labels

The C14 bundle is label-ready, but it has no independent labels by default. To
validate that the packet can receive reviewer CSVs without reporting an
adjudication result:

```powershell
python -X utf8 scripts\aggregate_false_promotion_external_review.py --check
```

To write the pre-label status artifact before any reviewer CSVs are returned:

```powershell
python -X utf8 scripts\aggregate_false_promotion_external_review.py
```

With no reviewer CSVs, this writes only
`false_promotion_external_review_packet_status.csv` and
`false_promotion_external_review_aggregation.md` under
`papers/diffaudit-evidence-paper/build/`. It does not write majority labels,
disagreement cells, declarations, agreement summaries, or author-key comparison
files; stale label-dependent CSV outputs from an earlier aggregation are
removed. It does not create external adjudication evidence.

When independent reviewers return completed copies of
`data/false_promotion_external_review_template.csv`, they must also return a
completed `REVIEWER_DECLARATION_<reviewer-id>.md`. Place one thirteen-row CSV per reviewer
and one matching declaration per reviewer
under:

```text
papers/diffaudit-evidence-paper/build/false_promotion_external_review_labels/
```

or pass explicit files:

```powershell
python -X utf8 scripts\aggregate_false_promotion_external_review.py --review-file .\reviewer_A.csv --declaration-file .\REVIEWER_DECLARATION_reviewer_A.md --review-file .\reviewer_B.csv --declaration-file .\REVIEWER_DECLARATION_reviewer_B.md
```

The script writes packet-level status, majority labels, disagreement cells,
agreement summaries, declaration status, and author-key comparison files under
`papers/diffaudit-evidence-paper/build/`.
Those aggregation files are written only after reviewer CSVs are loaded.
Rows labeled `needs_external_adjudication` or `invalid_row` remain excluded
until resolved. The aggregation is not an N50 denominator, field-prevalence
estimate, compute release, or inter-rater reliability claim; a reliability
claim still requires an explicit three-reviewer protocol and paper wording.
`false_promotion_external_review_packet_status.csv` keeps the conservative
claim switches machine-readable: external adjudication, reliability claims, and
compute release remain disabled even when reviewer counts and kappa thresholds
are reported.
`scripts\run_pr_checks.py` refreshes this C14 aggregation output before the
release-packet check. `scripts\check_paper_release_packet.py` then requires the
status CSV and Markdown to exist; in the no-reviewer state it rejects status
field drift, stale label-dependent CSV outputs, missing no-reviewer boundary
text, or any nonzero external-adjudication, reliability, or compute-release
claim switch.

## Release Gate

Before treating the paper packet as externally reproducible:

- Every generated, curated, and paper-source path in `asset_manifest.json` must
  exist; every non-excluded path must be tracked or explicitly packaged with the
  paper artifact, together with `paper.pdf`.
- The `anonymous_supplement_policy` in `asset_manifest.json` is the release
  boundary. Local paths, dirty tree state, and generator commands identify the
  reviewed packet; they are not public-redistribution or stronger-replay claims.
- `data/review_snapshot_manifest.csv` is a local review-snapshot byte manifest
  over non-excluded anonymous packet inputs plus `asset_manifest.json` and
  `paper.pdf`; it does not upgrade availability, admission, public
  redistributability, or replay tier.
- Rebuild `data/source_provenance.csv` from a clean release tree before relying
  on its `repo_commit` and `repo_tree_state` fields as public provenance.
- Do not delete `asset_manifest.json` when testing a rebuild; it is regenerated
  by `build_paper_assets.py`, and the script owns the generated, curated, and
  paper-source path lists.

The PDF text scan is intentionally conservative. Hits are not automatically
failures, but each hit must be either a harmless boundary/caveat phrase or
removed before public release.

`scripts\check_paper_release_packet.py` also checks manuscript bibliography
hygiene: every `\cite{...}` key in `main.tex` must appear in `refs.bib`, every
BibTeX entry must be cited, cited entries need the core fields required by their
entry type, and placeholder reference text is rejected.
It also hard-checks `data/mofit_public_gate_status.csv`: the MoFit public
score-surface rows must remain support-only, with four `Partial`
gates, `consumer_boundary=Fail`, `surface_delta=Fail`, no `Pass` gate, no
admission/N50/second-asset/compute-release wording in `allowed_claim`, and the
required forbidden-claim boundaries still present.
