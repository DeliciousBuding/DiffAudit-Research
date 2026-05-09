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

Can collaborator-style ReDiffuse scoring become a comparable gray-box baseline
against the existing PIA/SecMI line?

Current evidence:

- 750k ReDiffuse asset intake is positive and candidate-only.
- 750k `first_step_distance_mean` 64/64 packet is positive as compatibility,
  but not comparable with PIA/SecMI admitted metrics.
- 750k `resnet` 64/64 parity packet is negative: `AUC = 0.411982`,
  `ASR = 0.538462`, and both low-FPR metrics are `0.0`.
- 800k PIA checkpoint is ReDiffuse runtime-probe compatible on CPU; metrics are
  not run yet.

## Next Action

Run a CPU-only direct-distance boundary review before releasing any further
ReDiffuse GPU work. The review must decide whether the positive
`first_step_distance_mean` packet is a useful standalone Research surface or
whether the ReDiffuse lane should close until a stronger collaborator-style
scorer hypothesis appears.

## GPU Policy

No ReDiffuse GPU task is released.

Do not run 800k metrics, 128/128, 256/256, or 512/512 without a new CPU
contract. Keep PIA-related admitted claims aligned with
[../../docs/evidence/admitted-results-summary.md](../../docs/evidence/admitted-results-summary.md).
