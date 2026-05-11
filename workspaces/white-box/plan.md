# White-Box Plan

## Status

- `GSA`: strongest white-box method.
- `DPDM`: defended comparator with protocol limitations.
- `Finding NeMo` and related localization work: exploratory results, not promoted.
- Distinct second white-box family: selected for CPU-first influence/curvature
  feasibility scouting; no GPU release.
- GSA loss-score LR transfer: closed as negative-but-useful after
  leave-one-shadow-out stability review; do not GPU-scale from the existing
  scorer.

## Next Action

Don't reopen same-family GPU work unless a genuinely new hypothesis survives
CPU review. After SecMI hardening and repeated black-box response-contract
asset blockers, the current discovery slot is a CPU-only white-box
influence/curvature feasibility scout. The scout must reject itself if the
available signal is only scalar loss, gradient norm, GSA loss-score LR, or a
prior activation-subspace variant under a new name. Keep current status
reflected in
[../../docs/evidence/reproduction-status.md](../../docs/evidence/reproduction-status.md).

## Current Status

Strong upper-bound method, no immediate GPU candidate. The latest CPU-only
loss-score shadow stability review is
[../../docs/evidence/gsa-loss-score-shadow-stability-review.md](../../docs/evidence/gsa-loss-score-shadow-stability-review.md).
The current I-C successor review is
[../../docs/evidence/ic-cross-permission-successor-scope.md](../../docs/evidence/ic-cross-permission-successor-scope.md).
The current lane reselection is
[../../docs/evidence/post-secmi-next-lane-reselection-20260511.md](../../docs/evidence/post-secmi-next-lane-reselection-20260511.md).
