# E2Q-005 Single-Row Blind-Review Skeleton

> Date: 2026-06-06
> Scope: single-row feature-packet review preparation only.

This is not an `E2-20260606-N50` external adjudication package. It is a
single-row skeleton for judging whether `E2Q-005` can later become a valid row
in an E2 false-promotion corpus.

## Evidence Identity

- Candidate: `E2Q-005` Tracing the Roots
- Source seed: `E2S-005`
- OpenReview forum: `https://openreview.net/forum?id=mE74JKHTCE`
- Supplement URL:
  `https://openreview.net/attachment?id=mE74JKHTCE&name=supplementary_material`
- Supplement ZIP size: `45,499,156` bytes
- Supplement ZIP SHA-256:
  `62e9ae3833bcc0f102612d05898262eea2b6025fe8949a72c3f055a8534c7b41`
- Supplement entry count: `12`
- Identity JSON:
  [`e2q005_tracing_roots_openreview_identity_2026_06_06.json`](e2q005_tracing_roots_openreview_identity_2026_06_06.json)

## Feature Packet

The supplement exposes four CIFAR10 diffusion-trajectory feature tensors:

- `data/cifar10/train/member.pt`
- `data/cifar10/train/external.pt`
- `data/cifar10/eval/member.pt`
- `data/cifar10/eval/external.pt`

The 2026-06-06 identity check confirms:

- every tensor hash matches the existing replay JSON;
- every tensor loads with torch on CPU;
- every raw tensor shape is `1000 x 3000`;
- replay-selected feature shape is `1000 x 1002`;
- no loaded tensor reports NaN values.

Existing replay JSON:
`workspaces/gray-box/artifacts/tracing-roots-feature-packet-mia-20260515.json`.

## Replay Metrics

- Train samples: `2000`
- Eval samples: `2000`
- Positive class: `member`
- Held-out eval AUC: `0.815826`
- Held-out eval accuracy: `0.7375`
- TPR@1%FPR: `0.134`
- TPR@0.1%FPR: `0.038`

## Six-Gate Status

| Gate | Status | Reason |
| --- | --- | --- |
| Target | `Partial` | Public feature packet exists, but raw target checkpoint identity is absent. |
| Split | `Pass` | Public train/eval member/external tensor roles are fixed and hash-checked. |
| Score/response | `Pass_feature_packet_only` | Feature tensors and replay metrics are public; this is not black-box response evidence. |
| Metric | `Pass` | Local replay metric JSON is hash-aligned to the public tensor packet. |
| Provenance | `Partial` | Raw sample ids and raw target regeneration path are absent. |
| Consumer/delta | `Pass_research_side_only` | Useful for Research-side false-promotion review, not Platform/Runtime admission. |

## Allowed Wording

`E2Q-005` is a public supplementary CIFAR10 diffusion-trajectory feature-packet
MIA surface with fixed member/external train and eval tensor roles and local
replay metrics. It is positive but provenance-limited Research-side evidence.

## Forbidden Wording

Do not call this:

- `N50 evidence`
- `external adjudication row`
- `black-box response benchmark`
- `raw checkpoint/sample provenance`
- `Platform/Runtime admitted row`
- `fully reproducible from raw target/data assets`

## Decision

`single-row skeleton prepared / N50 external adjudication remains No-Go`.

The next useful action is external-style review of this one row's
feature-packet-only acceptability. The broader E2 corpus still needs enough
distinct countable rows before an actual external adjudication package exists.
