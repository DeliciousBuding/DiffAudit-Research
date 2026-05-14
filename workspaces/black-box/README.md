# Black-Box Workspace

## Current Status

- Direction: black-box membership inference attacks.
- Main method: `recon` is the admitted black-box product row and the selected
  lane for finite-tail confidence hardening.
- Supporting methods: `CLiD`, `variation`, `H2 response-strength`, and
  semantic-auxiliary classifiers.
- Candidate method: simple image-to-image distance is bounded single-asset
  evidence, not a product row or portability result.
- Active candidate: mid-frequency same-noise residual is a distinct observable
  gap. The scorer, collector functions, synthetic tiny cache writer,
  real-asset `4/4` cache preflight, and frozen `64/64` sign-check are
  implemented. The seed-only repeat retained signal, but the comparator audit
  shows mid-band is not uniquely strongest; keep the line as same-noise
  residual candidate evidence, not a mid-frequency-specific claim.
- Variation status: blocked until a real member/nonmember query-image set and
  endpoint contract exist.
- CLiD status: official public `inter_output/*` replay is strong on CPU
  (`AUC = 0.961277`, `TPR@1%FPR = 0.675470`, `ASR = 0.891957`) but remains
  prompt-conditioned candidate-only. The identity-manifest gate found no public
  row manifest, COCO image-id binding, or accessible HF ZIP metadata, so
  admitted black-box claims stay blocked.
- Semantic-auxiliary status: negative-but-useful after low-FPR review; no GPU
  packet selected.
- GPU: no active black-box GPU task running now.
- CommonCanvas status: true second response contract is ready but weak across
  pixel distance, CLIP image-similarity, prompt-response consistency,
  multi-seed response stability, and conditional denoising-loss. Do not reopen
  it through adjacent metric or denoising-loss matrices.
- MIDST TabDDPM status: exact local single-table labels are available, and
  official CITADEL/UQAM Blending++ score exports are the strongest MIDST signal
  so far (`dev+final AUC = 0.598079`, `TPR@1%FPR = 0.095750`), but still below
  the `0.60` reopen floor. Earlier nearest-synthetic-row, shadow-distributional,
  and MIA-EPT-style mechanisms are weaker. Do not expand Blending++ retraining,
  Gower feature matrices, EPT configs, TabSyn, multi-table, or white-box MIDST.
- Beans member-LoRA status: exact known-split target construction fixes the
  old Beans/SD1.5 pseudo-membership issue, but internal conditional
  denoising-loss is weak (`AUC = 0.414400`, reverse `0.585600`) and
  parameter-delta sensitivity is also weak (`AUC = 0.512000`,
  `TPR@1%FPR = 0.040000`); do not expand train-step, rank, resolution, prompt,
  scheduler, loss-weight, timestep, layer, or block matrices.
- MIA_SD status: related face-LDM code/result reference only. Public artifacts
  do not release images, target checkpoint, exact member/nonmember split
  manifest, or reusable query/response package; do not scrape staff images or
  train SD1.5 from this repo.
- FMIA status: OpenReview supplement has frequency-filter attack code and exact
  split manifests, but no target checkpoints, score arrays, generated samples,
  ROC CSVs, or metric artifacts; no GPU release and no admitted row.
- SimA status: official score-based code exists, including SD1.4/SD1.5 scripts,
  but the public release has empty split/checkpoint links, no release assets,
  no split manifests, no target checkpoints, no score arrays, and no ready
  verifier packet; no download, GPU release, or admitted row.
- GenAI Confessions status: public raw image/caption inputs exist for STROLL,
  Carlini, and Midjourney settings, but the fine-tuned STROLL checkpoint,
  generated image-to-image responses, DreamSim distance vectors, ROC/metric
  artifacts, Midjourney query logs, and ready verifier are missing; no dataset
  download, GPU release, or admitted row.

## Files

| File | Purpose |
| --- | --- |
| [plan.md](plan.md) | Current status and next steps. |
| [experiment-entrypoints.md](experiment-entrypoints.md) | Stable CLI commands for running experiments. |
| [paper-matrix-2024-2026.md](paper-matrix-2024-2026.md) | Paper and method overview. |

Current H2 candidate boundary:
[../../docs/evidence/black-box-response-strength-preflight.md](../../docs/evidence/black-box-response-strength-preflight.md).

Current mid-frequency same-noise residual preflight:
[../../docs/evidence/midfreq-same-noise-residual-preflight-20260512.md](../../docs/evidence/midfreq-same-noise-residual-preflight-20260512.md).

Current mid-frequency residual scorer contract:
[../../docs/evidence/midfreq-residual-scorer-contract-20260512.md](../../docs/evidence/midfreq-residual-scorer-contract-20260512.md).

Current mid-frequency residual collector contract:
[../../docs/evidence/midfreq-residual-collector-contract-20260512.md](../../docs/evidence/midfreq-residual-collector-contract-20260512.md).

Current mid-frequency residual tiny runner contract:
[../../docs/evidence/midfreq-residual-tiny-runner-contract-20260512.md](../../docs/evidence/midfreq-residual-tiny-runner-contract-20260512.md).

Current mid-frequency residual real-asset preflight:
[../../docs/evidence/midfreq-residual-real-asset-preflight-20260512.md](../../docs/evidence/midfreq-residual-real-asset-preflight-20260512.md).

Current mid-frequency residual sign-check:
[../../docs/evidence/midfreq-residual-signcheck-20260512.md](../../docs/evidence/midfreq-residual-signcheck-20260512.md).

Current mid-frequency residual stability decision:
[../../docs/evidence/midfreq-residual-stability-decision-20260512.md](../../docs/evidence/midfreq-residual-stability-decision-20260512.md).

Current mid-frequency residual stability result:
[../../docs/evidence/midfreq-residual-stability-result-20260512.md](../../docs/evidence/midfreq-residual-stability-result-20260512.md).

Current mid-frequency residual comparator audit:
[../../docs/evidence/midfreq-residual-comparator-audit-20260512.md](../../docs/evidence/midfreq-residual-comparator-audit-20260512.md).

Current CommonCanvas conditional denoising-loss closure:
[../../docs/evidence/commoncanvas-denoising-loss-20260513.md](../../docs/evidence/commoncanvas-denoising-loss-20260513.md).

Current non-CLiD reselection:
[../../docs/evidence/non-clid-blackbox-reselection.md](../../docs/evidence/non-clid-blackbox-reselection.md).

Current recon validation contract:
[../../docs/evidence/recon-product-validation-contract.md](../../docs/evidence/recon-product-validation-contract.md).

Current recon validation result:
[../../docs/evidence/recon-product-validation-result.md](../../docs/evidence/recon-product-validation-result.md).

Current recon tail confidence review:
[../../docs/evidence/recon-tail-confidence-review.md](../../docs/evidence/recon-tail-confidence-review.md).

Current H2 simple-distance boundary:
[../../docs/evidence/h2-simple-distance-portability-preflight.md](../../docs/evidence/h2-simple-distance-portability-preflight.md).

Current variation query contract audit:
[../../docs/evidence/variation-query-contract-audit.md](../../docs/evidence/variation-query-contract-audit.md).

Current CLiD image-identity boundary:
[../../docs/evidence/clid-image-identity-boundary-contract-20260511.md](../../docs/evidence/clid-image-identity-boundary-contract-20260511.md).

Current CLiD official inter-output replay:
[../../docs/evidence/clid-official-inter-output-replay-20260515.md](../../docs/evidence/clid-official-inter-output-replay-20260515.md).

Current CLiD identity-manifest gate:
[../../docs/evidence/clid-identity-manifest-gate-20260515.md](../../docs/evidence/clid-identity-manifest-gate-20260515.md).

Current FMIA OpenReview frequency artifact gate:
[../../docs/evidence/fmia-openreview-frequency-artifact-gate-20260515.md](../../docs/evidence/fmia-openreview-frequency-artifact-gate-20260515.md).

Current SimA score-based artifact gate:
[../../docs/evidence/sima-scorebased-artifact-gate-20260515.md](../../docs/evidence/sima-scorebased-artifact-gate-20260515.md).

Current GenAI Confessions black-box artifact gate:
[../../docs/evidence/genai-confessions-blackbox-artifact-gate-20260515.md](../../docs/evidence/genai-confessions-blackbox-artifact-gate-20260515.md).

Current response-contract package preflight:
[../../docs/evidence/blackbox-response-contract-package-preflight.md](../../docs/evidence/blackbox-response-contract-package-preflight.md).

Current response-contract discovery:
[../../docs/evidence/blackbox-response-contract-discovery.md](../../docs/evidence/blackbox-response-contract-discovery.md).

Current Beans/SD1.5 response-contract scout:
[../../docs/evidence/beans-sd15-response-contract-scout-20260512.md](../../docs/evidence/beans-sd15-response-contract-scout-20260512.md).

Current Beans/SD1.5 response-contract ready package:
[../../docs/evidence/beans-sd15-response-contract-ready-20260512.md](../../docs/evidence/beans-sd15-response-contract-ready-20260512.md).

Current Beans/SD1.5 simple-distance scout:
[../../docs/evidence/beans-sd15-simple-distance-scout-20260512.md](../../docs/evidence/beans-sd15-simple-distance-scout-20260512.md).

Current Beans/SD1.5 CLIP-distance scout:
[../../docs/evidence/beans-sd15-clip-distance-scout-20260512.md](../../docs/evidence/beans-sd15-clip-distance-scout-20260512.md).

Current Beans/SD1.5 membership semantics correction:
[../../docs/evidence/beans-sd15-membership-semantics-correction-20260512.md](../../docs/evidence/beans-sd15-membership-semantics-correction-20260512.md).

Current Beans member-LoRA denoising-loss closure:
[../../docs/evidence/beans-lora-member-denoising-loss-scout-20260513.md](../../docs/evidence/beans-lora-member-denoising-loss-scout-20260513.md).

Current MIA_SD asset verdict:
[../../docs/evidence/miasd-face-ldm-asset-verdict-20260513.md](../../docs/evidence/miasd-face-ldm-asset-verdict-20260513.md).

Current Beans member-LoRA delta-sensitivity closure:
[../../docs/evidence/beans-lora-delta-sensitivity-20260513.md](../../docs/evidence/beans-lora-delta-sensitivity-20260513.md).

Current semantic-auxiliary low-FPR review:
[../../docs/evidence/semantic-aux-low-fpr-review.md](../../docs/evidence/semantic-aux-low-fpr-review.md).

## Archive

Closed notes are in
[../../legacy/workspaces/black-box/2026-04/](../../legacy/workspaces/black-box/2026-04/).
