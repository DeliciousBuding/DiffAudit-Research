# CommonCanvas Conditional Denoising-Loss Scout

Date: 2026-05-13

## Question

After the CopyMark/CommonCanvas response-contract packet was weak under output
similarity, prompt-response consistency, and multi-seed response stability,
does a model-internal PIA-style loss expose membership? Specifically, do
CommonCatalog member query images have lower caption-conditioned
noise-prediction MSE than COCO holdout query images under
`common-canvas/CommonCanvas-XL-C`?

## Contract

- Asset: `response-contract-copymark-commoncanvas-20260512`.
- Target model: `common-canvas/CommonCanvas-XL-C`.
- Member split: `50` CommonCatalog query images from the existing CopyMark
  package.
- Nonmember split: `50` COCO holdout query images from the same package.
- Score: negative mean conditional denoising MSE over timesteps
  `[200, 500, 800]`; higher means more member-like.
- Resolution: `256` for bounded GPU feasibility on the local RTX 4070.
- Runner: `scripts/run_commoncanvas_denoising_loss.py`.
- Artifact:
  `workspaces/black-box/artifacts/commoncanvas-denoising-loss-20260513.json`.

This is not a black-box response-similarity metric. It uses the existing
membership-valid CopyMark/CommonCanvas split and tests a PIA-style internal
training-objective observable.

## Result

| Metric | Value |
| --- | ---: |
| AUC | `0.5148` |
| Reverse AUC | `0.4852` |
| ASR | `0.5700` |
| TPR@1%FPR | `0.0200` |
| TPR@0.1%FPR | `0.0200` |
| Member loss mean | `0.174177` |
| Nonmember loss mean | `0.175785` |

## Decision

Close CommonCanvas conditional denoising-loss by default.

The mechanism is genuinely different from pixel/CLIP/prompt/stability
response scorers, but it still fails the stop gate: AUC is below `0.60` and
strict-tail recovery is only `1 / 50` member at zero false positives. Do not
expand this into timestep, resolution, scheduler, seed, loss-weight, or
subset matrices. CommonCanvas remains useful as a true second response
contract, but the current observed mechanisms are weak and not admitted.

## Platform and Runtime Impact

None. No admitted result, schema change, or downstream consumer change.
