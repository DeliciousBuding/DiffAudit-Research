# Cross-Box Workspace

## Current Status

This workspace is for cross-track comparison work. The current verdict is that
cross-box score sharing is useful for internal comparison but remains
candidate-only.

Current integration boundaries are documented in
[../../docs/product-bridge/README.md](../../docs/product-bridge/README.md) and
[../../docs/evidence/cross-box-boundary-status.md](../../docs/evidence/cross-box-boundary-status.md) and
[../../docs/evidence/cross-box-successor-scope-20260512.md](../../docs/evidence/cross-box-successor-scope-20260512.md) and
[../../docs/evidence/research-boundary-card.md](../../docs/evidence/research-boundary-card.md).
Post-I-B reselection selected an I-C same-spec evaluator feasibility scout, and
that scout keeps I-C on hold because the current PIA bridge surface is still a
translated-alias canary rather than same-spec reuse:
[../../docs/evidence/post-ib-next-lane-reselection-20260512.md](../../docs/evidence/post-ib-next-lane-reselection-20260512.md) and
[../../docs/evidence/ic-same-spec-evaluator-feasibility-scout-20260512.md](../../docs/evidence/ic-same-spec-evaluator-feasibility-scout-20260512.md).

## Next Steps

There is no active cross-box CPU or GPU task. Do not schedule another
cross-box fusion run without a new low-FPR hypothesis and a distinct observable
or transfer contract. Reopen only under the conditions in
[../../docs/evidence/cross-box-successor-scope-20260512.md](../../docs/evidence/cross-box-successor-scope-20260512.md).
For I-C specifically, reopen only after a same-spec evaluator can emit
`AUC`, `ASR`, `TPR@1%FPR`, and `TPR@0.1%FPR` on more than the single
`965 / 1278` pair with a matched random comparator.
