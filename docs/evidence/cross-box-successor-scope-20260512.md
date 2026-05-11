# Cross-Box Successor Scope

Date: 2026-05-12

## Verdict

`hold`; no CPU packet, GPU packet, or schema change is released.

The question was whether Research has a genuinely new cross-box successor
hypothesis beyond existing aligned score sharing, weighted/logistic fusion,
support/disconfirm views, or tail-gated cascades. The answer is no for the
current asset state. Existing cross-box work remains useful for internal
comparison, but the available executable candidates are same-family variants
that do not create a new low-FPR or transfer claim.

## Evidence Reviewed

- [cross-box-boundary-status.md](cross-box-boundary-status.md): current
  cross-box packets are candidate-only because they improve ranking quality in
  some settings but do not establish stable low-FPR gains.
- Existing `workspaces/cross-box/runs/*/summary.json` packets, including
  GSA/PIA, GSA/PIA tail-gated, PIA/SimA, and three-surface consensus boards.
- [graybox-triscore-consolidation-review.md](graybox-triscore-consolidation-review.md)
  and
  [graybox-triscore-truth-hardening-review.md](graybox-triscore-truth-hardening-review.md):
  tri-score is positive-but-bounded internal evidence, not an admitted or
  product-facing cross-box successor.
- [h2-cross-asset-contract-preflight.md](h2-cross-asset-contract-preflight.md),
  [h2-img2img-simple-distance-admission-result.md](h2-img2img-simple-distance-admission-result.md),
  and
  [../product-bridge/h2-simple-distance-product-bridge-comparison.md](../product-bridge/h2-simple-distance-product-bridge-comparison.md):
  simple-distance is bounded single-asset black-box evidence, not a portable
  cross-box replacement.
- [blackbox-response-contract-skeleton-create-20260511.md](blackbox-response-contract-skeleton-create-20260511.md)
  and
  [blackbox-response-contract-query-source-audit-20260511.md](blackbox-response-contract-query-source-audit-20260511.md):
  the next black-box transfer package is still `needs_query_split`; local
  Kandinsky/Pokemon material is weights-only and cannot fill query images or
  responses.

## Falsifier Triggered

The release falsifier is triggered:

```text
If every currently executable cross-box candidate is an existing scalar
score-sharing, fusion, support/disconfirm, or tail-gated variant, and no new
observable or second response-contract package is ready, close the lane as
hold instead of running another same-family board.
```

This condition holds. The known tail-gated cascades can improve strict-tail
fields in some summaries, but they also regress broad AUC/ASR enough that they
are not a clean successor. The known logistic/weighted boards can improve AUC,
but the low-FPR interpretation remains unstable. The only potentially
story-changing transfer direction is a second response-contract black-box
package, and that is asset-blocked.

## Reopen Conditions

Reopen cross-box only when at least one condition is met:

- A second response-contract package probes ready with real member/nonmember
  query images and response coverage, with at least a `25/25` bounded packet
  contract.
- A genuinely new observable appears that is not scalar score sharing,
  weighted/logistic fusion, support/disconfirm voting, tail-gated cascade, or
  a same-contract tri-score rerun.
- A transfer contract defines matched split identity, target asset identity,
  query budget, adaptive-attacker boundary, and low-FPR primary gate before
  any GPU release.

## GPU State

`active_gpu_question = none`; `next_gpu_candidate = none`.

