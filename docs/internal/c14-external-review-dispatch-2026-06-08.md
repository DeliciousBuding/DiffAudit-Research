# C14 external-review dispatch note

> Date: 2026-06-08
> Last verified: 2026-06-09
> Scope: internal dispatch aid for sending the prepared C14 hard-blind review
> packet to independent reviewers.

This dispatch note is an internal aid. Current claim scope is
`packet_ready_only`: it supports sending the hard-blind packet, not external
adjudication, reviewer reliability, N50 denominator evidence, admitted
score/response evidence, prevalence, or compute release.

## Current packet state

- Packet status: `prepared_no_reviewer_csvs`
- Reviewer count: `0`
- Allowed claim scope: `packet_ready_only`
- Current C14 row state: thirteen selected pre-label stress rows only
- Current N50 external denominator: `0`
- Current compute-release switch: `0`

Status source:

```text
papers/diffaudit-evidence-paper/build/false_promotion_external_review_packet_status.csv
```

## Files to send

Send each independent reviewer exactly these two files:

```text
papers/diffaudit-evidence-paper/build/diffaudit-false-promotion-review-bundle.zip
papers/diffaudit-evidence-paper/build/diffaudit-false-promotion-review-bundle.zip.sha256
```

Current review bundle SHA-256:

```text
105a0515cfc4c5fc73e2f3b6e23a5a2413d972a0dcff809b7abfaf93d990f4e4
```

Do not send these files before that reviewer's labels and declaration are final:

```text
papers/diffaudit-evidence-paper/build/diffaudit-false-promotion-post-label-key.zip
papers/diffaudit-evidence-paper/build/diffaudit-false-promotion-post-label-key.zip.sha256
```

Current post-label key SHA-256, for maintainer verification only:

```text
a9e2a8a90eb11a4daeb069756426c558d26f338525ab94b713ff2fb4866616ff
```

## Reviewer targets

Launch target:

- `fpr-r01`
- `fpr-r02`
- `fpr-r03`

Two completed reviewer CSVs support only a bounded external-label result.
Three completed CSVs are the minimum for agreement thresholds or reliability
analysis. Neither case changes N50, admitted evidence, or compute release.

## Reviewer return package

Each reviewer must return exactly two files using the same reviewer id:

```text
false_promotion_external_review_<reviewer-id>.csv
REVIEWER_DECLARATION_<reviewer-id>.md
```

Reviewer ids must use lowercase ASCII letters, digits, and hyphens, start with
a letter, and be 3-32 characters long, for example `fpr-r01`.

Required placement after receipt:

```text
papers/diffaudit-evidence-paper/build/false_promotion_external_review_labels/
```

Place the CSV and declaration together. A declaration file without the matching
reviewer CSV is an incomplete return package and must block aggregation.

Then run:

```powershell
python -X utf8 scripts\aggregate_false_promotion_external_review.py
python -X utf8 scripts\check_paper_release_packet.py
python -X utf8 scripts\run_pr_checks.py
```

Do not update paper wording until the aggregation status switches explicitly
allow stronger claims.

## Reviewer invitation template

Subject:

```text
Independent review request: DiffAudit C14 false-promotion packet
```

Body:

```text
Hi <name>,

Could you independently label a 13-row review packet for a diffusion-model
membership-inference evidence study?

The task is a no-download, no-code-run review of public artifact surfaces. It
asks whether weaker public-surface rules would create false-promotion pressure
and what wording is supported by the visible evidence. Please do not use
LLM/AI assistance, do not discuss labels with other reviewers, do not run
upstream code, and do not download large assets.

Attached:
- diffaudit-false-promotion-review-bundle.zip
- diffaudit-false-promotion-review-bundle.zip.sha256

Expected SHA-256 for the ZIP:
105a0515cfc4c5fc73e2f3b6e23a5a2413d972a0dcff809b7abfaf93d990f4e4

Inside the ZIP, please start with REVIEWER_README.md. Use reviewer id
<reviewer-id> in every row and return:

- false_promotion_external_review_<reviewer-id>.csv
- REVIEWER_DECLARATION_<reviewer-id>.md

Please keep the labels final before reading any author-keyed or post-label
materials. I will not send those materials until after your CSV and declaration
are returned.
```

## Intake stop rules

Do not aggregate a returned review if any of these is true:

- required fields are blank;
- file name reviewer id, CSV `reviewer` column, or declaration `reviewer_id`
  disagree;
- reviewer id contains spaces, uppercase letters, punctuation other than
  hyphen, path-like text, or any value outside the stable 3-32 character
  lowercase id format;
- row IDs, titles, allowed-value columns, or row order changed;
- the reviewer omitted the declaration;
- the reviewer used LLM/AI assistance;
- the reviewer read post-label key materials before submission;
- the reviewer discussed labels with another reviewer before submission;
- the reviewer downloaded large assets, ran upstream code, or generated scores;
- any row claims compute release while target/split/row-bound score or response
  packet is still missing.

Rows that need upstream clarification stay excluded from shortcut-rule counts
until resolved.
