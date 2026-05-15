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
- TMIA-DM public-surface recheck: CRAD paper/PDF only. The 2026-05-15 gate
  found no official code, target checkpoint, immutable split manifest,
  per-sample scores, ROC arrays, metric JSON, or verifier output; do not reopen
  internal TMIA-DM / tri-score work or implement temporal-noise trajectories
  from scratch.
- MoFit status: mechanism-relevant caption-free gray-box route, but public code
  instructions are still `TBW` and target/split artifacts are missing. Do not
  implement surrogate/embedding optimization from scratch or release GPU.
- DSiRe / LoRA-WiSE status: strong future weight-only privacy lane candidate,
  but the claim is aggregate LoRA fine-tuning dataset-size recovery, not
  per-sample membership inference. Do not download LoRA-WiSE or run `dsire.py`
  unless a separate weight-only consumer contract is opened.
- DEB medical diffusion status: paper-source-only grey-box mechanism watch.
  Discrete-codebook perturbation plus intermediate-trajectory aggregation is a
  distinct observable, but no public code, target/split manifests,
  intermediate-state packet, score rows, ROC/metric artifacts, or verifier are
  released. Do not implement DEB from the paper or download MedMNIST/CIFAR/
  TinyImageNet/Stable Diffusion assets.
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

Current TMIA-DM public-surface recheck:
[../../docs/evidence/tmia-dm-temporal-artifact-gate-20260515.md](../../docs/evidence/tmia-dm-temporal-artifact-gate-20260515.md).

Current MoFit artifact verdict:
[../../docs/evidence/mofit-artifact-verdict-20260513.md](../../docs/evidence/mofit-artifact-verdict-20260513.md).

Current DSiRe / LoRA-WiSE boundary gate:
[../../docs/evidence/dsire-lora-wise-dataset-size-boundary-20260515.md](../../docs/evidence/dsire-lora-wise-dataset-size-boundary-20260515.md).

Current DEB medical diffusion artifact gate:
[../../docs/evidence/deb-medical-diffusion-artifact-gate-20260515.md](../../docs/evidence/deb-medical-diffusion-artifact-gate-20260515.md).

Current Fashion-MNIST SimA score-norm closure:
[../../docs/evidence/fashion-mnist-ddpm-sima-score-norm-20260514.md](../../docs/evidence/fashion-mnist-ddpm-sima-score-norm-20260514.md).

Current Fashion-MNIST score-Jacobian sensitivity closure:
[../../docs/evidence/fashion-mnist-ddpm-score-jacobian-sensitivity-20260514.md](../../docs/evidence/fashion-mnist-ddpm-score-jacobian-sensitivity-20260514.md).

## Archive

Closed notes are in
[../../legacy/workspaces/gray-box/2026-04/](../../legacy/workspaces/gray-box/2026-04/).
