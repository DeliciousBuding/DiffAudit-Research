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
- CLiD status: hold-candidate; prompt controls block image-identity and admitted
  black-box claims.
- Semantic-auxiliary status: negative-but-useful after low-FPR review; no GPU
  packet selected.
- GPU: no active black-box GPU task running now.
- CommonCanvas status: true second response contract is ready but weak across
  pixel distance, CLIP image-similarity, prompt-response consistency,
  multi-seed response stability, and conditional denoising-loss. Do not reopen
  it through adjacent metric or denoising-loss matrices.
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
