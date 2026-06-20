# E2Q-005 External-Style Review Rubric

> Date: 2026-06-06
> Scope: decision rubric for `E2Q-005` single-row feature-packet acceptability.

This rubric decides only whether `E2Q-005` is useful in an E2
false-promotion corpus as a provenance-limited feature-packet row. It does not
turn the row into N50 denominator evidence, Platform/Runtime evidence, or a
black-box response benchmark.

## Review Question

Can a public supplementary CIFAR10 diffusion-trajectory feature packet, with
fixed member/external train/eval tensor roles and replayed metrics, serve as a
valid false-promotion review row even though raw checkpoint and raw sample
provenance are absent?

## Inputs

- Skeleton:
  [`e2q005_single_row_blind_review_skeleton_2026_06_06.md`](e2q005_single_row_blind_review_skeleton_2026_06_06.md)
- Identity JSON:
  [`e2q005_tracing_roots_openreview_identity_2026_06_06.json`](e2q005_tracing_roots_openreview_identity_2026_06_06.json)
- Package check:
  [`e2q005_tracing_roots_package_check_2026_06_06.md`](e2q005_tracing_roots_package_check_2026_06_06.md)

## Required Judgments

| Judgment | Accept if | Reject if |
| --- | --- | --- |
| Public identity | OpenReview supplement URL, ZIP size, SHA-256, and central directory are enough to identify the reviewed packet. | The reviewer cannot independently identify the same public supplement. |
| Row binding | Tensor names and roles are sufficient to bind member/external train/eval rows at feature-packet level. | The reviewer requires raw image IDs, raw samples, or checkpoint regeneration for the specific E2 claim. |
| Metric provenance | Replay JSON and tensor hashes are enough to recompute or trust the reported AUC/accuracy/low-FPR metrics. | Metrics depend on unobserved scripts, mutable state, or non-public score rows. |
| Claim wording | Allowed wording stays limited to positive Research-side feature-packet evidence. | Any wording promotes raw target provenance, black-box response evidence, N50 denominator status, or Platform/Runtime admission. |
| False-promotion value | The row can teach reviewers that high metrics plus public features still leave target/provenance gates partial. | The row only duplicates an already-covered support case and would not change baseline-vs-contract decisions. |

## Decision Labels

- `accept_feature_packet_review_row`: use as one provenance-limited review row
  in a future E2 false-promotion corpus, outside the N50 denominator until the
  corpus freezes.
- `hold_support_only`: keep as bounded support; do not include in corpus
  review because feature-packet-only evidence would confuse the target claim.
- `reject_current_e2`: exclude from current E2 corpus because the row cannot be
  reviewed without raw target/sample provenance.

## Stop Rules

- Do not download new datasets, images, model weights, or generated payloads.
- Do not launch GPU/DCU jobs.
- Do not broaden this into a Tracing-the-Roots reproduction project.
- Do not use this review to reopen all E2 rows unless a new public artifact
  changes a gate.
