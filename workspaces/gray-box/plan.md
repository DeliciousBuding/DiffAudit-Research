# Gray-Box Plan

## Status

- `PIA`: strongest admitted gray-box attack + defense method.
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
  not run yet.
- Direct-distance boundary review blocks automatic 800k metrics because it
  would only test a Research-specific proxy surface.

## Next Action

No gray-box GPU task is released. Keep `PIA` as the admitted gray-box line and
return the active Research slot to I-A truth-hardening unless a new ReDiffuse
scorer or checkpoint-portability hypothesis is written first.

## GPU Policy

No ReDiffuse GPU task is released.

Do not run 800k metrics, 128/128, 256/256, or 512/512 without a new CPU
contract. Keep PIA-related admitted claims aligned with
[../../docs/evidence/admitted-results-summary.md](../../docs/evidence/admitted-results-summary.md).
