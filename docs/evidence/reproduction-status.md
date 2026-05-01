# Experiment Status

This page tracks the status of each research direction. Detailed notes are in
[workspace-evidence-index.md](workspace-evidence-index.md) and `legacy/`.

## Status Stages

| Stage | Meaning |
| --- | --- |
| `research-ready` | Paper, upstream code, and data requirements reviewed. |
| `code-ready` | Commands, configs, and tests exist in this repository. |
| `asset-ready` | Required datasets or model weights are available locally. |
| `evidence-ready` | A reviewed experiment summary exists. |
| `benchmark-ready` | Paper-level benchmarks can be reproduced. |

Smoke tests and dry runs are engineering validation, not benchmark claims.

## Current Status

| Track | Status | Notes |
| --- | --- | --- |
| Black-box `recon` | `evidence-ready` | Strongest black-box method and the selected non-CLiD lane for product-consumable strengthening. Public data limits strict paper-aligned claims. See [non-clid-blackbox-reselection.md](non-clid-blackbox-reselection.md). |
| Black-box `CLiD` | `hold-candidate` | Selected as a bounded black-box lane after H2 SD/CelebA text-to-image transfer was protocol-blocked. The 100/100 packet is strong and repeat-stable under prompt-conditioned evaluation, but prompt-neutral perturbation collapses the signal, swapped-prompt control is degraded, within-split prompt shuffle is weak and seed-sensitive, prompt-text-only review is moderate AUC but weak strict-tail, and control attribution shows auxiliary-feature instability under prompt controls. Current evidence supports a prompt-conditioned diagnostic claim only, not admitted general black-box evidence. No next CLiD GPU task is selected. See [black-box-next-lane-selection.md](black-box-next-lane-selection.md), [clid-bridge-contract.md](clid-bridge-contract.md), [clid-score-schema-gate.md](clid-score-schema-gate.md), [clid-tiny-score-bridge.md](clid-tiny-score-bridge.md), [clid-100-score-packet.md](clid-100-score-packet.md), [clid-candidate-integrity-review.md](clid-candidate-integrity-review.md), [clid-repeat-stability.md](clid-repeat-stability.md), [clid-prompt-perturbation.md](clid-prompt-perturbation.md), [clid-prompt-conditioning-boundary.md](clid-prompt-conditioning-boundary.md), [clid-swapped-prompt-control.md](clid-swapped-prompt-control.md), [clid-within-split-shuffle-control.md](clid-within-split-shuffle-control.md), [clid-prompt-text-only-review.md](clid-prompt-text-only-review.md), and [clid-control-attribution.md](clid-control-attribution.md). |
| Black-box `variation` | `code-ready` | API-only support method; needs real query data for stronger claims. |
| Black-box `H2 response-strength` | candidate-only | Positive-but-bounded DDPM/CIFAR10 candidate: frozen cutoff-0.50 lowpass follow-up passed, and raw H2 recovered strict-tail signal on the fresh packet. SD/CelebA text-to-image transfer is blocked by protocol mismatch. Not admitted evidence or a `recon` replacement. See [black-box-response-strength-preflight.md](black-box-response-strength-preflight.md), [h2-lowpass-followup-contract.md](h2-lowpass-followup-contract.md), and [h2-cross-asset-contract-preflight.md](h2-cross-asset-contract-preflight.md). |
| Gray-box `PIA` | `evidence-ready` | Strongest attack + defense story. Primary gray-box method. |
| Gray-box `SecMI` | `code-ready` | Independent reference method. |
| Gray-box `TMIA-DM` | `code-ready` | Strong alternative, secondary to PIA. |
| White-box `GSA` | `evidence-ready` | Strongest white-box method. Upper-bound reference. |
| White-box `DPDM` | `code-ready` | Defended comparator with protocol limitations. |
| Cross-box integration | candidate-only | Cross-track score sharing is useful for internal comparison, but current packets do not show stable low-FPR gains. See [cross-box-boundary-status.md](cross-box-boundary-status.md). |

## More Details

- Workspace state: [workspace-evidence-index.md](workspace-evidence-index.md)
- Verified results: [admitted-results-summary.md](admitted-results-summary.md)
- Cross-box boundary: [cross-box-boundary-status.md](cross-box-boundary-status.md)
- H2 response-strength preflight: [black-box-response-strength-preflight.md](black-box-response-strength-preflight.md)
- Innovation map: [innovation-evidence-map.md](innovation-evidence-map.md)
- Platform integration: [../product-bridge/README.md](../product-bridge/README.md)
- Data setup: [../assets-and-storage/data-and-assets-handoff.md](../assets-and-storage/data-and-assets-handoff.md)

## Promotion Rules

A result can be promoted to a higher status when it has:

- Defined data or experiment identity
- Reproducible commands or configs
- Reported metrics (AUC, ASR, TPR@1%FPR, TPR@0.1%FPR where applicable)
- A status label from the stages above
- Clear documentation of what it does and does not prove
