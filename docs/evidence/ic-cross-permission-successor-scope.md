# I-C Cross-Permission Successor Scope

> Date: 2026-05-11
> Status: hold; no GPU release

## Question

After ReDiffuse, gray-box tri-score, black-box response-contract intake, and
I-B successor scoping closed without a new GPU candidate, does I-C
cross-permission / translated-contract work contain a CPU-first successor that
should become active?

## Evidence Reviewed

- The original cross-permission matched pair froze one member/nonmember pair,
  but did not create a same-spec repeated board for release-level evaluation:
  [matched-pair freeze](../../legacy/workspaces/white-box/2026-04/2026-04-17-cross-permission-matched-pair-freeze.md).
- The in-model intervention review showed localized movement, but not a
  support-facing result strong enough for promotion:
  [in-model intervention review](../../legacy/workspaces/white-box/2026-04/2026-04-17-cross-permission-inmodel-intervention-review.md).
- The translated-contract falsifier was negative at the support boundary:
  targeted alias-local movement did not beat the matched random comparator on
  the gray-box support-facing readout:
  [translated falsifier review](../../legacy/workspaces/white-box/2026-04/2026-04-17-cross-permission-translated-falsifier-review.md).
- Later scoping still marked same-pair I-C replay as blocked until a same-spec
  gray-box evaluator and release board exist:
  [G1-A post-BM0 scoping](../../workspaces/2026-04-17-g1a-post-bm0-next-hypothesis-scoping.json).

## Verdict

`hold`.

I-C has a useful negative falsifier, but not an actionable CPU-first successor
lane today. The missing piece is not another narrative pass; it is a same-spec
evaluation contract with:

- paired member/nonmember cases beyond the first frozen pair,
- a gray-box evaluator reporting `AUC`, `ASR`, `TPR@1%FPR`, and
  `TPR@0.1%FPR`,
- a matched random comparator that the targeted intervention must beat,
- a predeclared adaptive boundary for alias or mask selection.

Until that contract exists, I-C should not consume the next CPU-first or GPU
slot.

## Next Action

Keep I-C in `hold`. Prefer black-box response-contract package construction or
protocol scouting because that lane has an executable scaffold and a clear
asset-readiness gate.

## Platform and Runtime Impact

No Platform or Runtime schema change is needed. I-C remains Research-internal
history and should not be exposed as admitted evidence.
