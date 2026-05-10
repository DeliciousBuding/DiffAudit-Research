# Black-Box Workspace

## Current Status

- Direction: black-box membership inference attacks.
- Main method: `recon` is the admitted black-box product row and the selected
  lane for finite-tail confidence hardening.
- Supporting methods: `CLiD`, `variation`, `H2 response-strength`, and
  semantic-auxiliary classifiers.
- Candidate method: simple image-to-image distance is bounded single-asset
  evidence, not a product row or portability result.
- Variation status: blocked until a real member/nonmember query-image set and
  endpoint contract exist.
- Semantic-auxiliary status: negative-but-useful after low-FPR review; no GPU
  packet selected.
- GPU: no active black-box GPU task running now.

## Files

| File | Purpose |
| --- | --- |
| [plan.md](plan.md) | Current status and next steps. |
| [experiment-entrypoints.md](experiment-entrypoints.md) | Stable CLI commands for running experiments. |
| [paper-matrix-2024-2026.md](paper-matrix-2024-2026.md) | Paper and method overview. |

Current H2 candidate boundary:
[../../docs/evidence/black-box-response-strength-preflight.md](../../docs/evidence/black-box-response-strength-preflight.md).

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

Current response-contract package preflight:
[../../docs/evidence/blackbox-response-contract-package-preflight.md](../../docs/evidence/blackbox-response-contract-package-preflight.md).

Current response-contract discovery:
[../../docs/evidence/blackbox-response-contract-discovery.md](../../docs/evidence/blackbox-response-contract-discovery.md).

Current semantic-auxiliary low-FPR review:
[../../docs/evidence/semantic-aux-low-fpr-review.md](../../docs/evidence/semantic-aux-low-fpr-review.md).

## Archive

Closed notes are in
[../../legacy/workspaces/black-box/2026-04/](../../legacy/workspaces/black-box/2026-04/).
