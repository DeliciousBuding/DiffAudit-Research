# Defense Workspace

## Current Status

This workspace is for current defense-specific summaries. Historical defense
notes should stay archived unless needed for active work.

Defense results must report low-FPR behavior and adaptive-attacker limitations
before being promoted to public evidence.

MIAHOLD / HOLD++ higher-order Langevin is defense watch-plus only. The public
repos expose higher-order Langevin defense code, audio split filelists, a CIFAR
HOLD config, and PIA-style attack code, but no checkpoint-bound target
artifacts, reusable member/nonmember scores, ROC arrays, metric JSON, generated
responses, or ready verifier outputs. Do not download Grad-TTS/HiFi-GAN/CLD-SGM
checkpoints, CIFAR/CelebA/audio datasets, scrape W&B artifacts, train HOLD++
models, or promote defense rows until checkpoint-bound score artifacts exist.
See
[../../docs/evidence/miahold-higher-order-langevin-artifact-gate-20260515.md](../../docs/evidence/miahold-higher-order-langevin-artifact-gate-20260515.md).

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
A CPU GSA-only preflight now uses the existing per-shadow GSA loss-score
exports to produce true shadow-local risk records for `shadow-01`,
`shadow-02`, and `shadow-03`. It de-duplicates repeated suffix IDs before
writing k32 identity files, but keeps I-B blocked because shadow-local PIA
risk records are still missing from the frozen PIA+GSA contract:
[../../docs/evidence/ib-shadow-local-gsa-risk-preflight-20260515.md](../../docs/evidence/ib-shadow-local-gsa-risk-preflight-20260515.md).

## Next Steps

The next valid I-B implementation step is not another threshold-transfer review
or another target-risk remap. It is either producing shadow-local PIA records
against the same identity contract or explicitly approving weaker GSA-only
semantics, then executing a tiny defended-shadow training artifact and
producing defended-shadow threshold references plus adaptive-attacker and
retained-utility measurements under the frozen protocol.
Verified defense claims belong in [../../docs/evidence/](../../docs/evidence/)
after review.
