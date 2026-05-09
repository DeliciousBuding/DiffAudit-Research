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
- 750k `resnet` scorer smoke runs, but only at a tiny held-out 4/4 scale.
- 800k PIA checkpoint is ReDiffuse runtime-probe compatible on CPU; metrics are
  not run yet.

## Next Action

Run one bounded 750k `64/64` parity packet with:

- `--scoring-mode resnet`
- `--max-samples 64`
- `--attack-num 1`
- `--interval 200`
- `--average 10`
- `--k 100`
- `--scorer-train-portion 0.2`
- `--scorer-epochs 15`

After that packet, write a verdict note and decide whether to:

1. keep ReDiffuse as paper-faithful enough for a same-contract 800k sanity
   packet, or
2. freeze it as candidate-only with unresolved scoring-contract parity.

## GPU Policy

One GPU task is released: `ReDiffuse 750k ResNet 64/64 parity packet`.

Do not run 800k metrics, 128/128, 256/256, or 512/512 until the 750k parity
verdict is documented. Keep PIA-related admitted claims aligned with
[../../docs/evidence/admitted-results-summary.md](../../docs/evidence/admitted-results-summary.md).
