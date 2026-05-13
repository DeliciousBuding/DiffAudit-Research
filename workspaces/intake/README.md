# Intake Workspace

## Current Status

- Direction: new method evaluation and paper scouting.
- No active intake review.
- Current long-horizon intake posture: LAION-mi is the active Lane A watch
  candidate. It has a named `Stable Diffusion-v1.4` target and public
  member/nonmember metadata splits, but remains response-not-ready until a
  fixed `25/25` URL availability probe recovers a balanced tiny query set.
  No GPU is released for LAION-mi yet.

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

Current LAION-mi follow-up:

- Run a CPU-only fixed `25/25` URL availability probe.
- Record only availability counts and failure classes.
- Do not download a large image set or generate responses until the tiny query
  set is recoverable from both splits.
