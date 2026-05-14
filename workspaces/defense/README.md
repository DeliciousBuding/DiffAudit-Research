# Defense Workspace

## Current Status

This workspace is for current defense-specific summaries. Historical defense
notes should stay archived unless needed for active work.

Defense results must report low-FPR behavior and adaptive-attacker limitations
before being promoted to public evidence.

StablePrivateLoRA is defense watch-plus only. Its public repo exposes
MP-LoRA/SMP-LoRA code and dataset split payloads, but no released
LoRA/checkpoint hashes, raw attack scores, ROC/metric artifacts, generated
responses, or ready verifier command. Do not clone/download the large dataset
payloads, SD-v1.5, LoRA checkpoints, generated images, or logs; do not train
MP-LoRA/SMP-LoRA or promote defense rows until checkpoint-bound score artifacts
exist. See
[../../docs/evidence/stableprivatelora-defense-artifact-gate-20260515.md](../../docs/evidence/stableprivatelora-defense-artifact-gate-20260515.md).

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
The future defended-shadow training set now has a coverage-aware CPU-only
manifest, but the current target k32 identity contract is blocked because the
three shadow member datasets cover only `2/32`, `2/32`, and `1/32` forget IDs:
[../../docs/evidence/ib-defended-shadow-training-manifest-20260512.md](../../docs/evidence/ib-defended-shadow-training-manifest-20260512.md).
A CPU shadow-local identity scout then checked whether target-level risk
records can be filtered into the shadow splits. `shadow-01` and `shadow-02`
can mechanically form a k32/k32 remap, but this remains blocked as true
shadow-local scoring because the risk records are target-level PIA/GSA
full-overlap records:
[../../docs/evidence/ib-shadow-local-identity-scout-20260512.md](../../docs/evidence/ib-shadow-local-identity-scout-20260512.md).

## Next Steps

The next valid I-B implementation step is not another threshold-transfer review.
It is either recomputing true shadow-local risk records or explicitly approving
the weaker two-shadow remap semantics, then constructing fixed identity files,
executing a tiny defended-shadow training artifact, and producing
defended-shadow threshold references plus adaptive-attacker and
retained-utility measurements under the frozen protocol.
Verified defense claims belong in [../../docs/evidence/](../../docs/evidence/)
after review.
