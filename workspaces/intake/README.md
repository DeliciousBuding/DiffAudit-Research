# Intake Workspace

## Current Status

- Direction: new method evaluation and paper scouting.
- No active intake review.
- Current long-horizon intake posture: external asset acquisition watch only.
  A candidate is actionable only when it fixes target identity, exact
  member/nonmember lists, query/response coverage, and a non-adjacent mechanism
  hypothesis before any GPU release.

Archived reviews are in
[../../legacy/workspaces/intake/2026-04/](../../legacy/workspaces/intake/2026-04/).

## Next Steps

New intake proposals should include:

- target model identity: checkpoint, endpoint, or reproducible training recipe
- exact member evidence: per-sample target training or fine-tuning membership
- exact nonmember evidence: held-out samples that are not target training data
- query/response contract: existing responses or deterministic generation plan
- mechanism delta: why this is not another CommonCanvas, Beans, MIDST, MNIST,
  Fashion-MNIST, final-layer gradient, or midfreq variant
- stop gate: close immediately if the first bounded packet has `AUC < 0.60` or
  near-zero `TPR@1%FPR`

If a proposal cannot satisfy these fields, keep it as watch-only and do not
write a new scope/audit chain.
