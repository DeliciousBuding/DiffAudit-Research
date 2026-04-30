# Product Bridge

This directory explains how Research feeds DiffAudit Platform and Runtime.

Platform should only consume results that have explicit status and clear
limitations. Research provides three kinds of output:

| Output | What it means |
| --- | --- |
| Verified result | A reviewed experiment result that can be shown as audit evidence. |
| Candidate result | A result useful for internal comparison, not yet ready for external use. |
| Constraint note | A known limitation that prevents overclaiming in Platform UI. |

## Documents

| Document | Purpose |
| --- | --- |
| [runtime.md](runtime.md) | Notes for Runtime integration. |
| [asset-registry-local-api.md](asset-registry-local-api.md) | Data registry contract for Runtime consumers. |
| [local-api.md](local-api.md) | Historical local API notes. |
| [recon-artifact-replay-guidance.md](recon-artifact-replay-guidance.md) | How to interpret recon debug traces. |

## Integration Rules

- Platform copy must reflect the actual experiment status.
- Don't present smoke tests or negative results as validated audit methods.
- Runtime integration requires stable input/output contracts.
- Before changing schemas or report format across repositories, create a
  handoff note here first.
