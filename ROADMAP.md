# DiffAudit Research Roadmap

> Last updated: 2026-04-30
> Owner: `Researcher`
> Mode: post-governance research reselection; no active GPU task

This file is the short steering document for Research. Long execution history
belongs under `legacy/`; current workspace state belongs under `workspaces/`.

## Current State

- Active work: `Cross-box evidence boundary hardening`
- Next GPU candidate: `none`
- CPU sidecar: `Public-surface / hot-path sync`
- History rewrite policy: audit only; no force-push without separate approval

The information-architecture reset, shared-utils extraction, architecture-audit
triage, asset-boundary cleanup, and CLI package/dispatch split are merged. The
repository is back at a research lane: harden cross-box claim boundaries before
any new GPU task is selected.

The CPU sidecar should run only when public docs, guards, or repository hot
paths become stale.

## Current Research Truth

- Black-box: `recon` remains the strongest main evidence line; `CLiD` and
  semantic-auxiliary classifier work remain bounded support/challenger lines.
- Gray-box: `PIA` remains the strongest attack + defense story; gray-box should
  not consume the next research slot unless a new fact changes the queue.
- White-box: `GSA` remains the strongest upper-bound line; `DPDM` remains a
  defended comparator; distinct second-family work is still not promoted.
- Cross-box: boundary hardening and product-consumable evidence status are the
  next honest lane.

## Next Decision

Resume:

```text
Cross-box evidence boundary hardening
```

Do not reopen no-hypothesis GPU work. A GPU task needs a bounded hypothesis,
frozen asset identity, expected project-level story value, and machine-health
budget.

## Canonical Entry Points

- Public overview: [README.md](README.md)
- Documentation map: [docs/README.md](docs/README.md)
- Reproduction status: [docs/evidence/reproduction-status.md](docs/evidence/reproduction-status.md)
- Product bridge: [docs/product-bridge/README.md](docs/product-bridge/README.md)
- Workspace evidence index: [docs/evidence/workspace-evidence-index.md](docs/evidence/workspace-evidence-index.md)
- Governance: [docs/governance/research-governance.md](docs/governance/research-governance.md)
- Active queue: [workspaces/implementation/challenger-queue.md](workspaces/implementation/challenger-queue.md)

## Handoff Boundary

No Platform or Runtime schema change is required by the current cleanup. If a
future research result changes exported fields, recommendation semantics,
evidence status, or report wording, create an explicit handoff note under
`docs/product-bridge/` before changing sibling repositories.
