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
  Archived paper candidates (SIMA, Noise-as-Probe, MoFit, Structural
  Memorization) were reviewed for reentry and remain on hold.
- Fashion-MNIST DDPM status: score-norm and score-Jacobian sensitivity scouts
  are both weak (`AUC = 0.515137` and `0.511719`, zero low-FPR recovery); do
  not expand timestep, `p`-norm, perturbation-scale, seed, scheduler, norm, or
  packet-size variants.
- Official SimA status: code-public watch-plus. The upstream release defines a
  distinct denoiser-output score-norm attack, but public split manifests,
  checkpoints, score arrays, ROC/metric artifacts, and a ready verifier are
  missing; no GPU job is released.
- MoFit status: mechanism-relevant caption-free gray-box route, but public code
  instructions are still `TBW` and target/split artifacts are missing. Do not
  implement surrogate/embedding optimization from scratch or release GPU.
- GPU: none released.

## Files

| File | Purpose |
| --- | --- |
| [plan.md](plan.md) | Current status and next steps. |

Current tri-score consolidation:
[../../docs/evidence/graybox-triscore-consolidation-review.md](../../docs/evidence/graybox-triscore-consolidation-review.md).

Current SecMI admission boundary:
[../../docs/evidence/secmi-admission-contract-hardening-20260511.md](../../docs/evidence/secmi-admission-contract-hardening-20260511.md).

Current archived paper-candidate reentry review:
[../../docs/evidence/graybox-paper-candidate-reentry-review-20260512.md](../../docs/evidence/graybox-paper-candidate-reentry-review-20260512.md).

Current official SimA artifact gate:
[../../docs/evidence/sima-scorebased-artifact-gate-20260515.md](../../docs/evidence/sima-scorebased-artifact-gate-20260515.md).

Current MoFit artifact verdict:
[../../docs/evidence/mofit-artifact-verdict-20260513.md](../../docs/evidence/mofit-artifact-verdict-20260513.md).

Current Fashion-MNIST SimA score-norm closure:
[../../docs/evidence/fashion-mnist-ddpm-sima-score-norm-20260514.md](../../docs/evidence/fashion-mnist-ddpm-sima-score-norm-20260514.md).

Current Fashion-MNIST score-Jacobian sensitivity closure:
[../../docs/evidence/fashion-mnist-ddpm-score-jacobian-sensitivity-20260514.md](../../docs/evidence/fashion-mnist-ddpm-score-jacobian-sensitivity-20260514.md).

## Archive

Closed notes are in
[../../legacy/workspaces/gray-box/2026-04/](../../legacy/workspaces/gray-box/2026-04/).
