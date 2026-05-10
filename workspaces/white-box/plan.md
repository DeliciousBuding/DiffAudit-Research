# White-Box Plan

## Status

- `GSA`: strongest white-box method.
- `DPDM`: defended comparator with protocol limitations.
- `Finding NeMo` and related localization work: exploratory results, not promoted.
- Distinct second white-box family: still open, not selected.
- GSA loss-score LR transfer: closed as negative-but-useful after
  leave-one-shadow-out stability review; do not GPU-scale from the existing
  scorer.

## Next Action

Don't reopen same-family GPU work unless a genuinely new hypothesis survives
CPU review. The current next-candidate discovery slot should prioritize
black-box response-contract package construction over another GSA loss-score
scorer. I-C cross-permission / translated-contract work is also on hold until
a same-spec evaluator and matched comparator contract exist. Keep current
status reflected in
[../../docs/evidence/reproduction-status.md](../../docs/evidence/reproduction-status.md).

## Current Status

Strong upper-bound method, no immediate GPU candidate. The latest CPU-only
loss-score shadow stability review is
[../../docs/evidence/gsa-loss-score-shadow-stability-review.md](../../docs/evidence/gsa-loss-score-shadow-stability-review.md).
The current I-C successor review is
[../../docs/evidence/ic-cross-permission-successor-scope.md](../../docs/evidence/ic-cross-permission-successor-scope.md).
