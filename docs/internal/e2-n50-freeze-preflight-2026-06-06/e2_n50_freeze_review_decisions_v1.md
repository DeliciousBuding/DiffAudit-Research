# E2 N50 Freeze Review Decisions v1

> Date: 2026-06-06
> Scope: internal freeze-review decisions for the 5 existing external candidates and 11 scout gate-review rows.

## Verdict

This review does not freeze `E2-20260606-N50`.

The denominator remains:

- directly countable external denominator rows: `0`
- priority package-work candidate: `1` (`E2Q-005` Tracing the Roots)
- reviewed but non-countable support / backup / exclude rows: `15`
- external adjudication package status: `No-Go`

The decision table is
[`e2_n50_freeze_review_decisions_v1.csv`](e2_n50_freeze_review_decisions_v1.csv).
It records queue ids, source seed ids, six-gate status, duplicate / surface
policy, first blocker, next artifact check, and allowed wording.

## Main Decisions

`E2Q-005` Tracing the Roots is the only row worth immediate package-work
follow-up. It has a public OpenReview supplementary feature packet, fixed
member/external train and eval tensors, and a local replay result. It still
does not count toward the denominator because raw target/sample provenance and
consumer-boundary wording remain limited.

`E2Q-004` CLiD, `E2Q-006` CopyMark, and `E2Q-011` Quantile/SecMI remain useful
support surfaces, not countable denominator rows. CLiD is blocked by missing
row-to-image identity binding. CopyMark is blocked by the lack of a compact
row-bound manifest. Quantile/SecMI is a third-party SecMI-style support packet,
not official quantile-regression evidence.

`E2Q-009` MIDST and `E2SCT-001` MT-MIA are cross-modal / tabular support unless
a separate tabular-relational stratum is explicitly opened. They must not be
pooled with image-diffusion denominator rows.

The priority scout rows `E2SCT-004`, `E2SCT-012`, `E2SCT-016`, and
`E2SCT-021` do not expose public row-bound score or response packets in the
current metadata. They stay backup/support only.

The semantic-risk rows `E2SCT-002`, `E2SCT-005`, `E2SCT-013`, and `E2SCT-014`
are attribution, classifier-defense, copying, or dataset-level identification
surfaces. They should remain related-method / false-promotion stress examples,
not membership denominator rows.

`E2SCT-006` and `E2SCT-009` remain artifact-followup backups, but current public
metadata is code/prompt/list oriented rather than pointwise membership evidence.

## Freeze Table Rule

A future freeze table must carry both `queue_id` and `source_seed_id`; the old
preflight files mix `E2Q-*`, `E2S-*`, and `E2SCT-*` identifiers, and external
adjudication would be brittle without explicit ID hygiene.

Minimum columns for a countable freeze-candidate table:

- `freeze_candidate_id`
- `queue_id`
- `source_seed_id`
- `source_kind`
- `title`
- `canonical_source_url`
- `artifact_catalog_url`
- `artifact_access_mode`
- `surface_family`
- `modality`
- `target_model_or_checkpoint`
- `dataset_or_contract_id`
- `member_nonmember_split_id`
- `row_identity_binding`
- `score_or_response_artifact`
- `metric_name`
- `metric_provenance`
- `officialness`
- `consumer_boundary`
- `delta_boundary`
- `duplicate_group_id`
- `duplicate_policy`
- `support_only_reason`
- `six_gate_status`
- `first_blocker`
- `adjudication_readiness`
- `reviewer_notes`

## Next Execution Order

1. For `E2Q-005`, recheck the OpenReview supplementary package identity:
   supplement URL, size, SHA-256, central directory, tensor filenames, tensor
   hashes, train/eval member/external counts, and replay metric JSON.
2. Only if `E2Q-005` package identity is stable, prepare a blind-review
   package skeleton for that single row; do not call it an external adjudication
   package for N50.
3. For `E2Q-004`, look only for a public row-to-COCO identity manifest. If the
   manifest is still gated or absent, keep CLiD as bounded support.
4. For `E2Q-006`, look only for a compact public row manifest joining filename,
   role, target checkpoint, score, and metric source.
5. Keep all scout rows as backup/exclude unless a public artifact changes one
   of the six gates. Do not run GPU/DCU jobs for E2.
