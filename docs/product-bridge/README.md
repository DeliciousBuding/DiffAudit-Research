# Product Bridge

This directory explains how Research feeds DiffAudit Platform and Runtime.

DiffAudit Platform should consume only evidence with explicit status and
boundaries. Research can provide product input in three forms:

| Input | Meaning |
| --- | --- |
| Admitted result | A reviewed result that can be shown as audit evidence with its limits. |
| Candidate/challenger result | A bounded result useful for internal comparison but not headline copy. |
| Boundary note | A constraint that prevents overclaiming or guides UI wording. |

Useful documents:

| Document | Purpose |
| --- | --- |
| [runtime.md](runtime.md) | Research-facing Runtime notes. |
| [asset-registry-local-api.md](asset-registry-local-api.md) | Registry alignment contract for Runtime consumers. |
| [local-api.md](local-api.md) | Historical local API compatibility notes. |
| [recon-artifact-replay-guidance.md](recon-artifact-replay-guidance.md) | How to interpret recon replay/debug traces. |

Rules for downstream use:

- Product copy must preserve evidence status.
- Platform should not present smoke-only, blocked, or negative results as
  validated audit methods.
- Runtime handoff requires stable input/output contracts, not just a workspace
  note.
- Research should create an explicit handoff note before changing sibling
  repository schemas or report semantics.
