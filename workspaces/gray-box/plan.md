# Gray-Box Plan

## Status

- `PIA`: strongest admitted local DDPM/CIFAR10 gray-box attack plus
  provisional defended comparator.
- `SecMI`: supporting reference and corroboration line, not the primary
  headline.
- `TMIA-DM`: strong gray-box alternative, secondary to PIA.
- `ReDiffuse`: candidate baseline-alignment line opened by the collaborator
  `DDIMrediffuse` bundle and 750k checkpoint.
- `PIA vs TMIA-DM confidence-gated switching`: closed as negative but useful.

## Active Question

Is there any active gray-box candidate that should consume the next GPU slot?

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

## Next Action

No gray-box GPU task is running. Keep `PIA` as the admitted gray-box line with
bounded adaptive and finite low-FPR caveats. ReDiffuse is closed as
candidate-only for now; do not run 800k or larger packets without a new scorer
hypothesis and CPU preflight.

## GPU Policy

No ReDiffuse GPU task is released.

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
