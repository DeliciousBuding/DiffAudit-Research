# X-178 Same-Packet Recon Comparator Feasibility Review

Date: 2026-04-29
Status: `blocked but useful / comparator-blocked`

## Question

After `X-176` validated H2 on a non-overlap `256 / 256` DDPM/CIFAR10 packet and `X-177` blocked promotion until comparator truth is resolved, can the admitted black-box `recon` line be evaluated on the same packet?

## Inputs Reviewed

- H2 validation packet:
  - `workspaces/black-box/runs/x176-h2-nonoverlap-256-validation-20260429-r1/summary.json`
  - `workspaces/black-box/runs/x176-h2-nonoverlap-256-validation-20260429-r1/scores.json`
  - `workspaces/black-box/runs/x176-h2-nonoverlap-256-validation-20260429-r1/response-cache.npz`
- H2 implementation contract:
  - `legacy/execution-log/2026-04-29/scripts/run_x172_blackbox_h2_strength_response_validation_gpu.py`
  - `legacy/execution-log/2026-04-29/scripts/run_x168_blackbox_h2_strength_response_gpu_scout.py`
- admitted `recon` runtime summary:
  - `experiments/recon-runtime-mainline-ddim-public-100-step30/summary.json`
  - `experiments/recon-runtime-mainline-ddim-public-100-step30/artifact-mainline/summary.json`
- `recon` implementation and gate:
  - `src/diffaudit/attacks/recon.py`
  - `external/Reconstruction-based-Attack/README.md`
  - `workspaces/black-box/2026-04-10-recon-decision-package.md`
  - `workspaces/implementation/2026-04-21-issue10-recon-stage0-paper-gate.md`

## Evidence

### H2 packet identity

`X-176` is a DDPM/CIFAR10 response-surface packet:

- config: `configs/attacks/pia_mainline_canonical.yaml`
- repo root: `external/PIA`
- split root: `external/PIA/DDPM`
- membership source: `CIFAR10_train_ratio0.5.npz` through `mia_train_idxs` and `mia_eval_idxs`
- packet size: `256 / 256`
- split offset: `192`
- output: generated response distances and H2 logistic scores, not reconstruction-distance artifacts

The X176 primary metric remains:

- raw H2: `AUC = 0.913940 / ASR = 0.851562 / TPR@1%FPR = 0.171875 / TPR@0.1%FPR = 0.062500`
- mandatory secondary `lowpass_0_5`: `0.140625 / 0.050781` at the two low-FPR points

### Admitted recon packet identity

The admitted `recon` result is a Stable Diffusion / text-image reconstruction-distance chain:

- backend: `stable_diffusion`
- model: `runwayml/stable-diffusion-v1-5`
- datasets: four `text` + `image` `.pt` payloads
- target/shadow models: `celeba_partial_target/checkpoint-25000` and `celeba_shadow/checkpoint-25000`
- packet: public-100 per split
- metric: `AUC = 0.849 / ASR = 0.51 / TPR@1%FPR = 1.0`
- evidence status: admitted black-box main evidence under `fine-tuned / controlled / public-subset / proxy-shadow-member`

The current implementation contract reinforces this boundary:

- `src/diffaudit/attacks/recon.py` declares `RECON_RUNTIME_DATASET_KEYS = ("text", "image")`
- `src/diffaudit/attacks/recon.py` declares `SUPPORTED_RECON_BACKENDS = {"stable_diffusion", "kandinsky_v22"}`
- the upstream recon README describes a LoRA-finetuned Stable Diffusion pipeline and reconstruction distance over generated images
- the strict Stage 0 paper gate already blocks promotion from local-semantic-chain-ready to paper-aligned while `shadow_member_proxy` remains proxy semantics

### Artifact status note

The admitted `recon` summary references generated `score-artifacts`, and the committed summary/artifact-mainline summaries remain available. In the current worktree, the raw `score-artifacts` directory is not present under `experiments/recon-runtime-mainline-ddim-public-100-step30/`; this is not the decisive blocker for X178, but it prevents a direct local re-score without reacquiring/regenerating those raw artifacts.

## Feasibility Matrix

| Option | Feasible as same-packet comparator? | Reason |
| --- | --- | --- |
| Run admitted `recon` on X176 DDPM/CIFAR10 indices | no | X176 has no text prompts, no Stable Diffusion LoRA target/shadow model pair, and no `text` + `image` recon dataset payloads. |
| Convert X176 CIFAR10 images into a `recon` dataset | no for X178 | This would create a new protocol and still lacks a compatible fine-tuned text-to-image model pair; it would not be the admitted `recon` comparator. |
| Compare admitted `recon` metrics against X176 H2 metrics | no | Cross-protocol summary comparison would mix Stable Diffusion/CelebA/public-subset and DDPM/CIFAR10/PIA splits, so it cannot decide same-packet superiority. |
| Run H2 on admitted `recon` assets | not a same-packet comparator | This may become a future response-surface acquisition idea, but it requires a new Stable Diffusion adapter and does not answer whether H2 beats admitted `recon` on X176. |
| Build a DDPM/CIFAR10 reconstruction-distance baseline | future candidate only | It could create a same-family baseline, but it would not be the admitted `recon` method and would require a new frozen contract, implementation, and GPU budget review. |

## Verdict

`blocked but useful / comparator-blocked`

The same-packet admitted `recon` comparator is not implementable on the X176 PIA/DDPM/CIFAR10 packet with current assets and code. The blocker is semantic and protocol-level, not just missing execution time:

- H2 is DDPM/CIFAR10 response-surface evidence.
- admitted `recon` is Stable Diffusion text-image reconstruction-distance evidence.
- the shared label type `member / nonmember` is insufficient for a valid comparator because model family, data representation, target/shadow contract, and score extraction differ.

## Control Decision

- `comparator_implementable = false`
- `h2_admitted_change = none`
- `h2_candidate_status = strong validated positive-but-bounded candidate`
- `h2_candidate_only_freeze = true until a compatible comparator surface is acquired`
- `next_gpu_candidate = none until X179 comparator-acquisition contract review`
- no same-contract H2 GPU expansion
- no `recon` replacement
- no Runtime-Server / Platform handoff

## Next Lane

`X-179 black-box comparator-acquisition contract review` should be CPU-first and decide whether any compatible acquisition path is worth a bounded GPU release:

1. DDPM/CIFAR10 reconstruction-distance baseline: same asset family, but not admitted `recon`.
2. Stable Diffusion/CelebA H2 response-surface adapter: closer to admitted `recon`, but a new implementation and likely heavy GPU path.
3. Candidate-only freeze plus shift back to `I-A / cross-box` maintenance if neither path has a bounded hypothesis, host-fit budget, and low-FPR kill gate.

## Handoff

- `Platform`: no change.
- `Runtime-Server`: no change.
- `Docs/materials`: if H2 is mentioned, say it is a strong validated DDPM/CIFAR10 internal candidate blocked by incompatible admitted-`recon` comparator assets. Do not present it as admitted evidence, a `recon` replacement, conditional diffusion coverage, or commercial-model evidence.
