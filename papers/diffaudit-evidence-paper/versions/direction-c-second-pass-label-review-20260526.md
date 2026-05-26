# Direction C Second-Pass Label Review 2026-05-26

> Status: bounded agent second-pass review.
> Scope: label-promotion risk audit for the selected Direction C corpus.
> No downloads: no browsing, cloning, model/data fetching, e-print downloads, or experiments.

This review addresses the largest remaining reviewer risk for Direction C:
the corpus labels were produced by the same project team and could be read as a
single-review artifact. It is still not independent human inter-rater
reliability. It is a bounded second-pass agent review whose value is narrower:
identify label-promotion risks before the selected corpus is used in the
Direction A paper or a future Direction C manuscript.

The machine-readable adjudication table is
[`../data/artifact_second_pass_label_review_20260526.csv`](../data/artifact_second_pass_label_review_20260526.csv).

## Review Inputs

| Input | Rows | Role |
| --- | ---: | --- |
| `../data/artifact_corpus_v1.csv` | 21 | Existing evidence-note corpus over admitted, candidate, support, negative, and metadata-only surfaces. |
| `../data/artifact_corpus_fixed_search_20260526.csv` | 17 | Frozen GitHub/arXiv metadata-search batch. |
| Local evidence notes referenced by rows | as needed | Used only to verify disputed labels; no external refresh. |

## Review Protocol

Two reviewers were asked to separately check gate labels under the same
claim-relative rubric used in the paper:

- `Pass`: enough evidence for the stated paper role, not universal success.
- `Partial`: relevant surface exists, but a stronger claim would need missing
  target, split, row evidence, metric, boundary, or delta information.
- `Fail`: the row lacks the surface needed for that gate under the stated
  claim role.

The first reviewer completed all 38 rows. The second reviewer was interrupted
after the full task ran too long and was redirected to the label-promotion-risk
subset: rows with positive/support evidence or fixed-search metadata labels
that could be too generous. This was deliberate; low-risk all-Fail rows do not
change the paper route.

## Disagreements and Adjudication

| Corpus | Row | Gate | Proposed change | Adjudication |
| --- | --- | --- | --- | --- |
| v1 | `v0-01` admitted bundle | evidence | `Pass -> Partial` | Not adopted. The row is a mixed-replay positive control for the admitted bundle, not a claim that every admitted row has row-score arrays. The mixed boundary is now explicit in `main.tex` and `source_map.md`. |
| v1 | `v0-01` admitted bundle | metric | `Pass -> Partial` | Not adopted for the same reason; uncertainty remains limited to rows with direct score arrays. |
| v1 | `v1-10` Discrete DLM withdrawn paper | delta | `Partial -> Fail` | Adopted. A withdrawn, no-PDF/no-code/no-packet record has no usable artifact delta. |
| fixed-search | `fs20260526-arxiv-03` Noise Aggregation | target | `Partial -> Fail` | Adopted. The local gate says paper-source-only: no public target checkpoint, hash, or released target packet. |

## Result

The review found no new admitted-like fixed-search row and no evidence/metric
promotion in the metadata-only batch. Two label tightenings were applied to the
CSV sources:

- `v1-10.delta_gate = Fail`
- `fs20260526-arxiv-03.target_gate = Fail`

The admitted-bundle disagreement is retained as a documented caveat rather
than applied as a label change. This protects the paper from a stronger but
misleading statement: the admitted bundle is audit-ready under its mixed
contract, while row-score bootstrap uncertainty exists only for a subset of its
rows.

## Claim Boundary

This review can support a narrow statement: a bounded second-pass label audit
found only two adopted gate tightenings and no new label-promotion row in the
selected corpus. It must not be reported as independent human annotation,
inter-rater reliability, field-wide artifact prevalence, or proof that public
diffusion MIA artifacts generally fail.
