# Reproduction And Evidence Status

This page is the public status ledger. It is intentionally short: detailed
dated verdict notes live in [workspace-evidence-index.md](workspace-evidence-index.md)
and `legacy/workspaces/`.

## Status Ladder

| State | Meaning |
| --- | --- |
| `research-ready` | Paper, upstream code, and asset requirements have been reviewed. |
| `code-ready` | Commands, configs, and tests exist in this repository. |
| `asset-ready` | Required local datasets, weights, or supplementary files have been probed. |
| `evidence-ready` | A reviewed summary or verdict exists. |
| `benchmark-ready` | The lane can reasonably claim paper-level benchmark execution. |

Dry-runs and smoke tests are useful engineering checks, but they are not
benchmark claims.

## Current Track Summary

| Track | Current state | Public claim boundary |
| --- | --- | --- |
| Black-box `recon` | `evidence-ready` | Strongest black-box line, but public-asset semantics limit strict paper-aligned claims. |
| Black-box `CLiD` | `code-ready` / bounded corroboration | Useful support line; not a headline replacement. |
| Black-box `variation` | `code-ready` / smoke-supported | API-only support line; real query assets are required for stronger claims. |
| Gray-box `PIA` | `evidence-ready` | Strongest attack + defense story and primary gray-box evidence line. |
| Gray-box `SecMI` | corroboration | Useful independent reference, not the main headline. |
| Gray-box `TMIA-DM` | challenger reference | Strong challenger, not promoted above PIA. |
| White-box `GSA` | `evidence-ready` | Strongest white-box line and upper-bound evidence. |
| White-box `DPDM/W-1` | defended comparator | Comparator with protocol-boundary limits, not a final benchmark. |
| Cross-box / `I-A` | CPU-first next lane | Boundary-maintenance and product-consumable evidence hardening. |

## Where To Inspect Details

- Active workspace state: [workspace-evidence-index.md](workspace-evidence-index.md)
- Admitted summary: [admitted-results-summary.md](admitted-results-summary.md)
- Innovation map: [innovation-evidence-map.md](innovation-evidence-map.md)
- Product boundary: [../product-bridge/README.md](../product-bridge/README.md)
- Asset setup: [../assets-and-storage/data-and-assets-handoff.md](../assets-and-storage/data-and-assets-handoff.md)

## Promotion Rule

A result can move toward product-facing evidence only when it has:

- a frozen asset or packet identity
- a reproducible command or contract
- reported metrics where applicable
- a status label from the ladder above
- a known boundary for what must not be claimed
