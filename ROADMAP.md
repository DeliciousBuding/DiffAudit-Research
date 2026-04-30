# DiffAudit Research Roadmap

> Last updated: 2026-04-30
> Owner: `Researcher`
> Mode: information-architecture reset; no active GPU task

This file is the short steering document for Research. Long execution history
belongs under `legacy/`; current workspace state belongs under `workspaces/`.

## Current State

- `active_gpu_question = none`
- `next_gpu_candidate = none`
- `current_execution_item = Research information architecture reset`
- `next_cpu_sidecar = X-181 I-A / cross-box boundary maintenance`
- `history_rewrite_policy = audit only; no force-push without separate approval`

This cleanup does not create new research results. It makes the repository
readable enough for teammates and reviewers to understand which evidence is
paper-grounded, which evidence is bounded exploration, and which evidence can
feed Platform or Runtime.

## Current Research Truth

- Black-box: `recon` remains the strongest main evidence line; `CLiD` and
  semantic-auxiliary classifier work remain bounded support/challenger lines.
- Gray-box: `PIA` remains the strongest attack + defense story; gray-box should
  not consume the next CPU-first slot unless a new fact changes the queue.
- White-box: `GSA` remains the strongest upper-bound line; `DPDM/W-1` remains a
  defended comparator; distinct second-family work is still not promoted.
- Cross-box / innovation: `I-A` truth-hardening and product-consumable boundary
  maintenance are the next honest CPU-first lane.

## Next Decision

After the information-architecture reset PR is merged, resume:

```text
X-181 I-A / cross-box boundary maintenance after H2 comparator block
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

No Platform or Runtime schema change is required by this cleanup. If a future
research result changes exported fields, recommendation semantics, evidence
status, or report wording, create an explicit handoff note under
`docs/product-bridge/` before changing sibling repositories.
