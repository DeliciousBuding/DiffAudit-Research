# E2Q-005 Tracing the Roots Package Check

> Date: 2026-06-06
> Scope: no-download package-work check for the current priority E2 row.

`E2Q-005` remains the only priority package-work candidate from freeze-review
v1. This check does not make it countable denominator evidence.

## What Exists Now

- Evidence note:
  `docs/evidence/tracing-roots-feature-packet-mia-20260515.md`
- Replay metric JSON:
  `workspaces/gray-box/artifacts/tracing-roots-feature-packet-mia-20260515.json`
- Local replay metric in JSON: AUC `0.815826`, accuracy `0.7375`,
  TPR@1%FPR `0.134`, TPR@0.1%FPR `0.038`
- Tensor hashes recorded in JSON for:
  `train/member`, `train/external`, `eval/member`, `eval/external`
- OpenReview supplement identity JSON:
  [`e2q005_tracing_roots_openreview_identity_2026_06_06.json`](e2q005_tracing_roots_openreview_identity_2026_06_06.json)

## Public Supplement Recheck

The 2026-06-06 OpenReview supplement recheck succeeded:

- ZIP size: `45,499,156` bytes
- ZIP SHA-256:
  `62e9ae3833bcc0f102612d05898262eea2b6025fe8949a72c3f055a8534c7b41`
- central directory entry count: `12`
- four tensor hashes match the replay JSON
- all four tensors load with torch on CPU
- each raw tensor shape is `1000 x 3000`
- each replay-selected feature shape is `1000 x 1002`
- no loaded tensor reports NaN values

The older extracted paths still do not exist:

- `tmp/tracing-roots-supp-20260515/data/cifar10/train/member.pt`
- `tmp/tracing-roots-supp-20260515/data/cifar10/train/external.pt`
- `tmp/tracing-roots-supp-20260515/data/cifar10/eval/member.pt`
- `tmp/tracing-roots-supp-20260515/data/cifar10/eval/external.pt`

Use the 2026-06-06 ZIP identity JSON as the current package-work evidence
instead of those stale extracted paths.

## Decision

`E2Q-005` can enter single-row package-work preparation, but not N50 external
adjudication.

The single-row blind-review skeleton is:
[`e2q005_single_row_blind_review_skeleton_2026_06_06.md`](e2q005_single_row_blind_review_skeleton_2026_06_06.md).

This still does not make `E2Q-005` a countable denominator row. The feature
packet lacks raw target checkpoint identity and raw sample IDs.

The package wording must stay precise: this is a public feature-packet MIA
surface with fixed tensor roles and replay metrics, not a raw target checkpoint,
raw image identity, or black-box response packet.

Machine-readable checklist:
[`e2q005_tracing_roots_package_check_2026_06_06.csv`](e2q005_tracing_roots_package_check_2026_06_06.csv).
