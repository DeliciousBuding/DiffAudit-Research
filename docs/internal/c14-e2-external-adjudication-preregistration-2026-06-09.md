# C14/E2 External-Adjudication Preregistration

> Date: 2026-06-09
> Scope: locked pre-label protocol supplement for Direction A external review.

This supplement freezes the C14 false-promotion review process before reviewer
labels arrive. It records the row set, weak-rule baselines, reviewer packet,
post-label key, aggregation command, and stopping rules. It is not an external
label result.

## Locked Status

- Review state: `pre_label_preregistered`
- Packet label readiness: `prepared_no_reviewer_csvs`
- Reviewer count: `0` (`n_reviewers=0`)
- Allowed claim scope: `packet_ready_only`
- Selected row count: `13`
- External denominator rows: `0`
- Compute release: `0`

The preregistered row set is the current C14 blocker-blinded packet:

```text
papers/diffaudit-evidence-paper/data/false_promotion_blinded_review_packet.csv
```

The reviewer template is:

```text
papers/diffaudit-evidence-paper/data/false_promotion_external_review_template.csv
```

The codebook is:

```text
papers/diffaudit-evidence-paper/versions/direction-a-false-promotion-audit-codebook.md
```

The launch protocol is:

```text
papers/diffaudit-evidence-paper/versions/direction-a-c14-external-review-launch-protocol.md
```

## Frozen Reviewer Packet

Reviewer-facing files are packaged in:

```text
papers/diffaudit-evidence-paper/build/diffaudit-false-promotion-review-bundle.zip
papers/diffaudit-evidence-paper/build/diffaudit-false-promotion-review-bundle.zip.sha256
```

Current reviewer ZIP SHA-256:

```text
105a0515cfc4c5fc73e2f3b6e23a5a2413d972a0dcff809b7abfaf93d990f4e4
```

The reviewer ZIP is hard-blind. It contains the blocker-blinded packet, blank
template, reviewer-safe row trace, reviewer public URL table, declaration
template, codebook, launch protocol, and bundle manifest. It must not contain
the author adjudication key, author gate matrix, claim trace, source
provenance, source rows, cached evidence notes, or `post-label-author-key/`.

## Frozen Post-Label Key

Maintainer-only post-label files are packaged in:

```text
papers/diffaudit-evidence-paper/build/diffaudit-false-promotion-post-label-key.zip
papers/diffaudit-evidence-paper/build/diffaudit-false-promotion-post-label-key.zip.sha256
```

The post-label key SHA-256 sidecar is authoritative after export. This
preregistration file is hashed into source provenance, and source provenance is
packaged inside the post-label key ZIP, so this file does not embed that ZIP's
self-referential final hash.

```text
papers/diffaudit-evidence-paper/build/diffaudit-false-promotion-post-label-key.zip.sha256
```

This ZIP is released only after a reviewer's CSV and declaration are final. A
reviewer who reads post-label files before submission cannot provide an
independent label for the preregistered analysis.

## Weak-Rule Baselines

The C14 packet tests whether weaker admission rules would promote selected
public surfaces that the DiffAudit contract blocks or bounds. The registered
weak rules are:

- `code_availability_would_promote`
- `artifact_availability_would_promote`
- `paper_claim_artifact_link_would_promote`
- `metric_code_split_would_promote`
- `score_only_would_promote`

The DiffAudit comparator uses the target, split, score/response, metric,
semantic-boundary, provenance, and consumer-boundary gates recorded in the
codebook and template. Reviewers must choose the first blocker and the narrowest
allowed wording for each row.

## Reviewer Intake

Each reviewer must return exactly two files:

```text
false_promotion_external_review_<reviewer-id>.csv
REVIEWER_DECLARATION_<reviewer-id>.md
```

Returned files go under:

```text
papers/diffaudit-evidence-paper/build/false_promotion_external_review_labels/
```

A declaration file without the matching reviewer CSV is an incomplete return
package. The aggregation script must reject it instead of treating the packet as
a clean no-label state.

Before and after intake, run:

```powershell
python -X utf8 scripts\aggregate_false_promotion_external_review.py
python -X utf8 scripts\check_paper_release_packet.py
python -X utf8 scripts\run_pr_checks.py
```

The aggregation result may support only selected-row external-label statements
when the machine-readable status permits them. It does not create field
prevalence, N50 denominator evidence, admitted score/response evidence, reviewer
reliability evidence, or compute release.

## Stop Rules

Stop intake and revise the launch packet if any returned review has changed row
IDs, titles, allowed-value columns, or row order; blank required fields; missing
or mismatched declaration; LLM/AI-assisted labels; post-label exposure before
submission; reviewer discussion before submission; large-asset downloads; code
execution; generated scores; or compute-release claims without fixed target,
split, row-bound score/response packet, metric provenance, and consumer
boundary.

Rows marked `needs_external_adjudication` or `invalid_row` remain excluded from
shortcut-rule counts until resolved.

## Current Boundary

The current paper may state that the C14 packet is label-ready and
preregistered. It may not report completed external adjudication, reviewer
reliability, field prevalence, N50 denominator evidence, admitted evidence, a
second public score/response asset, or compute release.
