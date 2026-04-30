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
| Black-box `recon` | `evidence-ready` | Strongest black-box method. Public data limits strict paper-aligned claims. |
| Black-box `CLiD` | `code-ready` | Supporting method, not a headline replacement. |
| Black-box `variation` | `code-ready` | API-only support method; needs real query data for stronger claims. |
| Black-box `H2 response-strength` | candidate-only | Raw-primary 512 / 512 validation is negative-but-useful: strong AUC, failed strict low-FPR gate. A fixed cutoff-0.50 lowpass follow-up contract exists but is not admitted evidence. See [black-box-response-strength-preflight.md](black-box-response-strength-preflight.md) and [h2-lowpass-followup-contract.md](h2-lowpass-followup-contract.md). |
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
