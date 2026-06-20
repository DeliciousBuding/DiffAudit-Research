# Direction A C14 External Review Launch Protocol

Date: 2026-06-08

This protocol turns the C14 false-promotion packet into an executable external
review task. It is launch material only: not external adjudication, not reviewer
reliability evidence, not an N50 external denominator, not field-prevalence
evidence, not admitted score/response evidence, and not compute release.

## Purpose

C14 tests whether weak public-surface rules create author-modeled shortcut
pressure for thirteen selected rows that DiffAudit's evidence contract should
block. The current paper packet is
packet-ready, but it has zero independent labels. This protocol defines how to
collect those labels without leaking the same-team answer key into the review.

## Reviewer Independence

Use reviewers who can inspect public ML/security artifacts and understand
diffusion membership-inference language, but who did not create the C14 row
labels, codebook, row checks, paper claims, or author answer key.

Minimum launch target:

- two independent reviewers for a bounded external-label result;
- three independent reviewers before discussing agreement thresholds or any
  reliability-oriented analysis;
- one thirteen-row CSV per reviewer, with all rows completed before aggregation.

Do not use LLM/AI-assisted labels, model-generated labels, same-team labels,
synthetic labels, or author answer-key labels as external reviewer evidence.
Such labels may be used only for software tests and must stay out of evidence
claims.

Each reviewer must return the bundled reviewer declaration as
`REVIEWER_DECLARATION_<reviewer-id>.md`. The declaration must use a stable
reviewer id such as `fpr-r01`, `fpr-r02`, or `fpr-r03`. Reviewer ids must use
lowercase ASCII letters, digits, and hyphens, start with a letter, and be
3--32 characters long.
The declaration must state that the reviewer:

- did not read author-keyed materials before labeling;
- did not use LLM/AI assistance for gate, verdict, first-blocker, allowed-wording,
  or notes decisions;
- did not communicate with other reviewers about row labels;
- is not a same-team author of the C14 labels, row checks, paper claims,
  codebook, or answer key;
- did not download large assets, run upstream code, or generate new scores.

## Reviewer Packet

Send each reviewer only the current hard-blind false-promotion review bundle:

- `build/diffaudit-false-promotion-review-bundle.zip`
- `build/diffaudit-false-promotion-review-bundle.zip.sha256`

Do not send the maintainer-only post-label key ZIP until that reviewer's labels
and declaration are final:

- `build/diffaudit-false-promotion-post-label-key.zip`
- `build/diffaudit-false-promotion-post-label-key.zip.sha256`

Inside the ZIP, the reviewer should start with:

1. `REVIEWER_README.md`
2. `versions/direction-a-false-promotion-audit-codebook.md`
3. `data/false_promotion_blinded_review_packet.csv`
4. `data/false_promotion_row_trace.csv`
5. `REVIEWER_PUBLIC_URLS.csv`
6. `REVIEWER_DECLARATION.md`
7. `data/false_promotion_external_review_template.csv`

`REVIEWER_PUBLIC_URLS.csv` may include `public_url_note` values for known
accessibility issues observed before launch. These notes are reviewer
navigation aids only; they do not replace the gate decision, add evidence, or
change the row label.

The reviewer ZIP intentionally contains no `post-label-author-key/` directory.
The separate post-label key ZIP contains same-team comparison and provenance
material that reviewers must not receive or read until after labels are final.
This includes:

- `post-label-author-key/false_promotion_adjudication_key.csv`
- `post-label-author-key/false_promotion_external_review_packet.csv`
- `post-label-author-key/false_promotion_author_gate_matrix.csv`
- `post-label-author-key/false_promotion_gate_summary.csv`
- `post-label-author-key/false_promotion_gate_matrix.pdf`
- `post-label-author-key/false_promotion_exemplars.csv`
- `post-label-author-key/false_promotion_rule_summary.csv`
- `post-label-author-key/false_promotion_exemplars.pdf`
- `post-label-author-key/claim_trace.csv`
- `post-label-author-key/source_provenance.csv`
- `post-label-author-key/claim_register.md`
- `post-label-author-key/evidence-notes/*`

Those files are same-team post-label comparison or provenance material, not
pre-label reviewer inputs and not external labels.

## Reviewer Instructions

Each reviewer should:

1. Copy `data/false_promotion_external_review_template.csv`.
2. Fill the same `reviewer` identifier in all thirteen rows.
3. Preserve `review_id`, `source_row_id`, `title`, allowed-value columns, and
   row order.
4. Fill every gate with `Pass`, `Partial`, `Fail`, or `N/A`.
5. Select one `false_promotion_verdict` from the allowed values.
6. Write the first blocker that prevents stronger wording.
7. Write the narrowest allowed wording.
8. Leave `compute_release` as `no` unless the row has fixed target identity,
   fixed split, public row-bound score/response evidence, metric provenance,
   sufficient provenance, and compatible consumer boundary.
9. Add notes only when they explain a decision or unresolved ambiguity.
10. Return one file named
    `false_promotion_external_review_<reviewer-id>.csv`.
11. Return a completed `REVIEWER_DECLARATION_<reviewer-id>.md` with the same reviewer id.
    The reviewer id must use the stable lowercase 3--32 character format
    described above.

Reviewers must not download large assets, run upstream code, train or fine-tune
models, query closed APIs, register for benchmark platforms, or generate new
scores while labeling C14. The task is to judge the current public surface.
If a public URL returns 403, 404, 429, redirects to an unrelated artifact, or is
otherwise inaccessible, the reviewer should record that in `notes` and use
`needs_external_adjudication` if the row cannot be judged from the remaining
pre-label packet and accessible public surfaces. Cached evidence notes are
author-keyed provenance material under `post-label-author-key/` and must not be
used before labels are final.

After returning labels, a reviewer who reads author-keyed files cannot revise
the submitted labels for reliability analysis. A second pass after exposure to
the author key must be treated as discussion material, not an independent label.

## Maintainer Intake

Store returned reviewer CSVs under:

```text
papers/diffaudit-evidence-paper/build/false_promotion_external_review_labels/
```

Before labels are returned, the maintainer may run the aggregator once to write
status-only pre-label outputs:

```powershell
python -X utf8 scripts\aggregate_false_promotion_external_review.py
```

With no reviewer CSVs this writes only
`false_promotion_external_review_packet_status.csv` and
`false_promotion_external_review_aggregation.md`, with
`packet_label_readiness=prepared_no_reviewer_csvs` and all external
adjudication, reliability, and compute-release claim switches disabled.
It removes stale label-dependent CSV outputs from any earlier aggregation so a
pre-label launch directory cannot accidentally expose old majority labels.
The fast PR gate refreshes these status-only outputs before the paper release
check, and the release checker now fails if no-reviewer status fields drift, if
old label-dependent CSVs remain, or if the external-adjudication, reliability,
or compute-release switches become nonzero.

Then run:

```powershell
python -X utf8 scripts\aggregate_false_promotion_external_review.py
```

The maintainer must record:

- reviewer count and reviewer identifiers;
- declaration presence and machine-checked independence-attestation status for each reviewer;
- schema validation status;
- unresolved rows labeled `needs_external_adjudication` or `invalid_row`;
- majority labels and disagreement cells;
- whether threshold checks passed, failed, or were not applicable;
- the machine-readable claim switches in
  `false_promotion_external_review_packet_status.csv`.

## Reporting Boundary

Even after reviewer CSVs exist, report stronger claims only when the aggregation
status supports them and the paper wording has been explicitly updated. Without
the protocol, threshold, and wording conditions listed above, C14 provides no
N50 external denominator, field-prevalence evidence, admitted score/response
evidence, compute release, or reviewer reliability evidence.
Until those conditions hold, the packet remains not external adjudication, not reviewer reliability evidence, and not an N50 external denominator; it does not release compute.

The safe current wording before labels are returned is:

> The C14 packet is label-ready but has zero independent reviewer labels. It is
> a selected stress object for weak-rule false-promotion.

## Stop Rules

Stop and revise the launch packet instead of aggregating if:

- any reviewer changes row IDs, titles, allowed-value columns, or row order;
- a reviewer leaves a required label blank;
- a reviewer reports that a row cannot be labeled from the packet alone;
- a reviewer used the author answer key before finalizing labels;
- a reviewer used LLM/AI assistance for labels or wording;
- a reviewer omitted the declaration or reused another reviewer's id;
- reviewers discussed labels with each other before submission;
- a reviewer downloaded large assets, ran upstream code, or generated new
  scores;
- returned labels imply compute release for a row whose target/split/row-bound
  score or response packet is still missing.

Rows that need upstream clarification stay excluded from shortcut-rule counts
until resolved.
