# Gray-Box Workspace

## Current Status

- Direction: partial-observation membership inference (PIA, SecMI, TMIA-DM) and defense evaluation.
- Main method: `PIA` is the strongest admitted local DDPM/CIFAR10 gray-box line.
- Supporting reference: `SecMI` is evidence-ready after full-split review, but
  remains outside Platform/Runtime admitted evidence. Its admission contract is
  now hardened as Research-only supporting evidence.
- Defense reference: stochastic dropout is a provisional defended comparator,
  not validated privacy protection.
- Active candidate: gray-box CDI/TMIA-DM/PIA tri-score truth-hardening is
  CPU-first and internal-only. ReDiffuse 750k exact replay is candidate-only
  after modest AUC and weak strict-tail evidence; 800k remains blocked.
- GPU: none released.

## Files

| File | Purpose |
| --- | --- |
| [plan.md](plan.md) | Current status and next steps. |

Current tri-score consolidation:
[../../docs/evidence/graybox-triscore-consolidation-review.md](../../docs/evidence/graybox-triscore-consolidation-review.md).

Current SecMI admission boundary:
[../../docs/evidence/secmi-admission-contract-hardening-20260511.md](../../docs/evidence/secmi-admission-contract-hardening-20260511.md).

## Archive

Closed notes are in
[../../legacy/workspaces/gray-box/2026-04/](../../legacy/workspaces/gray-box/2026-04/).
