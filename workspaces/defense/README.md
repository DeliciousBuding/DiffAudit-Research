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
reference:
[../../docs/evidence/ib-defense-reopen-protocol-audit-20260512.md](../../docs/evidence/ib-defense-reopen-protocol-audit-20260512.md).
The current reopen protocol is now frozen as a machine-checkable CPU contract,
but it still releases no GPU and does not train defended shadows:
[../../docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md](../../docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md).
The active review entrypoint now has a CPU guard: explicit
`defended-shadow-reopen` mode rejects old undefended shadow threshold
references, while legacy diagnostic mode stays reproducible:
[../../docs/evidence/ib-reopen-shadow-reference-guard-20260512.md](../../docs/evidence/ib-reopen-shadow-reference-guard-20260512.md).

## Next Steps

The next valid I-B implementation step is not another threshold-transfer review.
It is a tiny defended-shadow training artifact plus adaptive-attacker and
retained-utility measurements under the frozen protocol. Verified defense
claims belong in [../../docs/evidence/](../../docs/evidence/) after review.
