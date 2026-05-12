# I-B Defended-Shadow Reopen Protocol

Date: 2026-05-12

## Verdict

`protocol-frozen; no GPU release`

This note turns the I-B defended-shadow/adaptive-attacker reopen requirement
into a machine-checkable CPU contract. It does not execute defended-shadow
training, run an adaptive attacker, or promote I-B defense evidence.

The stable artifact is
[`workspaces/defense/artifacts/ib-defended-shadow-reopen-protocol-20260512.json`](../../workspaces/defense/artifacts/ib-defended-shadow-reopen-protocol-20260512.json).
The validator is `scripts/validate_ib_defended_shadow_reopen_protocol.py`.

## Question

Can the next I-B task be specified tightly enough that a future tiny run would
test a real defended-shadow/adaptive-attacker claim instead of repeating the
old undefended threshold-transfer diagnostic?

## Hypothesis

I-B can only be reopened if defended shadows and an adaptive attacker are
evaluated under the same identity contract as the undefended target.

## Falsifier

If defended-shadow training is unavailable, retained utility regresses, or
strict-tail improvement is absent under a defended-shadow threshold reference,
the line closes without a larger GPU packet.

## Frozen Contract

| Component | Requirement |
| --- | --- |
| Defended-shadow training | Use `run-risk-targeted-unlearning-pilot` as the defended checkpoint entrypoint, starting with a tiny-first budget. |
| Adaptive attacker | Use `review-risk-targeted-unlearning-pilot` only when its threshold reference is defended shadows, not the old undefended shadow summary. |
| Identity | Keep target checkpoint, member split, nonmember split, forget set, and retain set fixed. |
| Metrics | Report `AUC`, `ASR`, `TPR@1%FPR`, `TPR@0.1%FPR`, and retained utility. |
| Finite-tail language | Report denominators and do not claim calibrated continuous sub-percent FPR. |
| Stop rule | Close the line if strict-tail improvement is absent, utility regresses, or defended-shadow training is unavailable. |

## What This Blocks

- Admitted defense evidence.
- Adaptive robustness claims.
- Platform/Runtime defense rows.
- Old undefended threshold-transfer GPU packets.
- Any GPU packet authorized by this protocol alone.

## Next Action

Do not launch GPU from this protocol alone. The first CPU plumbing step is now
complete:
[ib-reopen-shadow-reference-guard-20260512.md](ib-reopen-shadow-reference-guard-20260512.md).
A later CPU preflight produced a coverage-aware training manifest, but it is
blocked because the current target k32 forget IDs are not covered by the shadow
member datasets:
[ib-defended-shadow-training-manifest-20260512.md](ib-defended-shadow-training-manifest-20260512.md).
The remaining reopen requirements are executed defended-shadow training
artifacts, adaptive-attacker measurement, retained utility, and strict-tail
improvement under a defended-shadow threshold reference.
