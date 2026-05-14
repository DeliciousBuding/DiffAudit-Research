# Gray-Box Plan

## Status

- `PIA`: strongest admitted local DDPM/CIFAR10 gray-box attack plus
  provisional defended comparator.
- `SecMI`: evidence-ready supporting reference and corroboration line, not the
  admitted primary headline.
- `TMIA-DM`: strong gray-box alternative, secondary to PIA.
- `ReDiffuse`: candidate baseline-alignment line opened by the collaborator
  `DDIMrediffuse` bundle and 750k checkpoint.
- `SIMA / Noise-as-Probe / MoFit / Structural Memorization`: archived
  paper-backed candidates; reentry review keeps them on hold.
- `Official SimA`: code-public watch-plus after the 2026-05-15 artifact gate;
  still not executable because public split manifests, checkpoints, score
  arrays, ROC/metric artifacts, and a ready verifier are missing.
- `Fashion-MNIST SimA score-norm`: weak fresh mechanism scout on a real
  train/test split (`AUC = 0.515137`, `TPR@1%FPR = 0.0`); no timestep, `p`-norm,
  seed, scheduler, or packet-size expansion.
- `Fashion-MNIST score-Jacobian sensitivity`: weak fresh local score-field
  sensitivity scout on the same split (`AUC = 0.511719`, `TPR@1%FPR = 0.0`);
  no timestep, perturbation-scale, seed, scheduler, norm, or packet-size
  expansion.
- `PIA vs TMIA-DM confidence-gated switching`: closed as negative but useful.
- `CDI/TMIA-DM/PIA tri-score`: positive-but-bounded internal evidence
  aggregation; not admitted and not product-facing.

## Current Question

What is the correct gray-box boundary after ReDiffuse and CDI/TMIA-DM/PIA
tri-score both closed as candidate-only or internal-only evidence?

Current evidence:

- 750k ReDiffuse asset intake is positive and candidate-only.
- 750k `first_step_distance_mean` 64/64 packet is positive as compatibility,
  but not comparable with PIA/SecMI admitted metrics.
- 750k `resnet` 64/64 parity packet is negative: `AUC = 0.411982`,
  `ASR = 0.538462`, and both low-FPR metrics are `0.0`.
- 800k PIA checkpoint is ReDiffuse runtime-probe compatible on CPU; metrics are
  not run.
- Direct-distance boundary review blocks automatic 800k metrics because it
  would only test a Research-specific proxy surface.
- Checkpoint-portability gate confirms 750k/800k metadata and split hash
  compatibility, but blocks release because the scorer contract remains
  unresolved.
- ResNet contract scout blocks treating the current Research `resnet` mode as
  exact collaborator replay because checkpoint-selection and score-orientation
  semantics differ.
- `resnet_collaborator_replay` now preserves the collaborator
  checkpoint-selection counter contract and passes a 4-sample real-asset CPU
  smoke. This is a preflight, not admitted evidence.
- 750k `resnet_collaborator_replay` GPU packet completed with `AUC = 0.702293`,
  `ASR = 0.682692`, `TPR@1%FPR = 0.019231`, and `TPR@0.1%FPR = 0.019231`.
  This is candidate-only; strict-tail evidence is weak.
- X-88, X-141, and X-142 tri-score packets are positive internal evidence.
  The best repeat reports `AUC = 0.859043`, `ASR = 0.786133`,
  `TPR@1%FPR = 0.118164`, and `TPR@0.1%FPR = 0.023438`, but the contract
  explicitly says `headline_use_allowed = false` and
  `external_evidence_allowed = false`.
- Tri-score truth-hardening closed as positive-but-bounded: all three frozen
  packets beat admitted PIA on AUC and both low-FPR fields, while ASR is not
  stable enough for the support claim. The result remains internal-only.
- SecMI full-split admission-boundary review upgrades SecMI from `code-ready`
  to `evidence-ready` supporting reference: full `25k / 25k` execution reports
  stat `AUC = 0.885833` and NNS `AUC = 0.946286`, but it remains outside the
  admitted bundle until its consumer boundary, structured cost, and
  adaptive-review contract are hardened.
- SecMI admission-contract hardening keeps both stat and NNS as
  `research-support-only` rows. NNS still needs an explicit product-facing
  auxiliary-head contract before any admission discussion.
- Archived gray-box paper candidates were re-reviewed after I-B hold. SIMA has
  weak standalone metrics and unstable strict-tail pairboard gains. The
  2026-05-14 Fashion-MNIST DDPM score-norm scout and local score-Jacobian
  sensitivity scout also failed, with `AUC = 0.515137` and `0.511719` plus zero
  low-FPR recovery. The 2026-05-15 official SimA release gate found useful
  score-based code but no public split/checkpoint/score packet.
  Noise-as-Probe is sensitive to guidance leakage; MoFit remains canary-only;
  Structural Memorization is negative on the local smoke. None releases GPU.

## Next Action

No gray-box GPU task is running. Keep `PIA` as the admitted gray-box line with
bounded adaptive and finite low-FPR caveats. Keep SecMI as a strong hardened
supporting reference, not a Platform/Runtime row. ReDiffuse is closed as
candidate-only for now; do not run 800k or larger packets without a new scorer
hypothesis and CPU preflight. CDI/TMIA-DM/PIA tri-score is closed as
positive-but-bounded internal evidence; do not run a larger same-contract
tri-score packet.
Do not reopen SIMA, Noise-as-Probe, MoFit, or Structural Memorization without
a genuinely new low-FPR-primary observable or protocol. Do not expand the
Fashion-MNIST SimA or score-Jacobian checks into timestep, `p`-norm,
perturbation-scale, seed, scheduler, norm, or packet-size matrices.
Do not run official SimA GPU jobs, request checkpoints by email, or rebuild its
DDPM/SD targets from scratch unless public split/checkpoint/score artifacts
appear.

Canonical consolidation:
[../../docs/evidence/graybox-triscore-consolidation-review.md](../../docs/evidence/graybox-triscore-consolidation-review.md).

Canonical truth-hardening:
[../../docs/evidence/graybox-triscore-truth-hardening-review.md](../../docs/evidence/graybox-triscore-truth-hardening-review.md).

## GPU Policy

No ReDiffuse GPU task is released.

No tri-score GPU task is released. The next gray-box task must introduce a new
scorer, surface, or falsifier before it can become CPU-active again.

Fashion-MNIST SimA score-norm closure is tracked by
[../../docs/evidence/fashion-mnist-ddpm-sima-score-norm-20260514.md](../../docs/evidence/fashion-mnist-ddpm-sima-score-norm-20260514.md).

Official SimA artifact gate is tracked by
[../../docs/evidence/sima-scorebased-artifact-gate-20260515.md](../../docs/evidence/sima-scorebased-artifact-gate-20260515.md).

Fashion-MNIST score-Jacobian sensitivity closure is tracked by
[../../docs/evidence/fashion-mnist-ddpm-score-jacobian-sensitivity-20260514.md](../../docs/evidence/fashion-mnist-ddpm-score-jacobian-sensitivity-20260514.md).

Do not run 800k metrics, 128/128, 256/256, or 512/512 without a new CPU
contract. The 800k checkpoint is runtime-compatible, but metrics remain blocked
by [../../docs/evidence/rediffuse-checkpoint-portability-gate.md](../../docs/evidence/rediffuse-checkpoint-portability-gate.md).
The original Research `resnet` implementation is also blocked as non-exact
replay by
[../../docs/evidence/rediffuse-resnet-contract-scout.md](../../docs/evidence/rediffuse-resnet-contract-scout.md).
The explicit collaborator replay mode is tracked by
[../../docs/evidence/rediffuse-exact-replay-preflight.md](../../docs/evidence/rediffuse-exact-replay-preflight.md).
The 750k exact-replay packet verdict is tracked by
[../../docs/evidence/rediffuse-exact-replay-packet.md](../../docs/evidence/rediffuse-exact-replay-packet.md).
Keep PIA-related admitted claims aligned with
[../../docs/evidence/admitted-results-summary.md](../../docs/evidence/admitted-results-summary.md).
Keep the SecMI admission boundary aligned with
[../../docs/evidence/secmi-full-split-admission-boundary-review.md](../../docs/evidence/secmi-full-split-admission-boundary-review.md).
The hardened SecMI admission-contract artifact is tracked by
[../../docs/evidence/secmi-admission-contract-hardening-20260511.md](../../docs/evidence/secmi-admission-contract-hardening-20260511.md).
Archived paper-candidate reentry is tracked by
[../../docs/evidence/graybox-paper-candidate-reentry-review-20260512.md](../../docs/evidence/graybox-paper-candidate-reentry-review-20260512.md).
