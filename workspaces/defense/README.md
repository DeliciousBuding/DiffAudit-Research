# Defense Workspace

## Current Status

This workspace is for current defense-specific summaries. Historical defense
notes should stay archived unless needed for active work.

Defense results must report low-FPR behavior and adaptive-attacker limitations
before being promoted to public evidence.

The current I-B risk-targeted unlearning successor scope is on hold. Existing
full-split attack-side reviews show small metric reductions, but they are not
defense-aware because defended shadows were not retrained. See
[../../docs/evidence/ib-risk-targeted-unlearning-successor-scope.md](../../docs/evidence/ib-risk-targeted-unlearning-successor-scope.md)
and
[../../docs/evidence/ib-adaptive-defense-contract-20260511.md](../../docs/evidence/ib-adaptive-defense-contract-20260511.md).
The latest defense-aware reopen scout keeps I-B on hold because the current
best k32 full-split anchor is still attack-side threshold-transfer only:
[../../docs/evidence/ib-defense-aware-reopen-scout-20260512.md](../../docs/evidence/ib-defense-aware-reopen-scout-20260512.md).
The follow-up protocol audit checks the active CLI/code path and confirms that
`review-risk-targeted-unlearning-pilot` still borrows an undefended shadow
reference, so the lane has no executable defended-shadow or adaptive-attacker
protocol yet:
[../../docs/evidence/ib-defense-reopen-protocol-audit-20260512.md](../../docs/evidence/ib-defense-reopen-protocol-audit-20260512.md).

## Next Steps

Use this workspace only for active defense coordination. Verified defense claims
belong in [../../docs/evidence/](../../docs/evidence/) after review.
