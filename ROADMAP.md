# DiffAudit Research Roadmap

> Last updated: 2026-04-30

This is the short steering document for Research. Execution history is in
`legacy/`; current workspace state is in `workspaces/`.

## Current Focus

- **Active work:** Cross-box experiment boundary hardening
- **Next GPU task:** none selected
- **CPU work:** Public documentation and repository sync

The information-architecture reset, shared utilities extraction, asset boundary
cleanup, and CLI package split are all merged. The repository is currently
focused on hardening cross-box claim boundaries before selecting new GPU tasks.

## Research Directions

- **Black-box:** `recon` is the strongest main line. `CLiD` and
  semantic-auxiliary classifiers are supplementary methods.
- **Gray-box:** `PIA` is the strongest attack + defense story. Gray-box work
  will not take the next research slot unless new findings change priorities.
- **White-box:** `GSA` provides the strongest upper-bound results. `DPDM` is
  the defended comparator.
- **Cross-box:** Boundary hardening and integration of results across
  attacker knowledge levels is the next direction.

## Next Steps

Resume cross-box boundary hardening. New GPU tasks require a clear hypothesis,
required data assets, and an expected contribution to the project narrative.

## Key Documents

- Project overview: [README.md](README.md)
- Documentation index: [docs/README.md](docs/README.md)
- Experiment status: [docs/evidence/reproduction-status.md](docs/evidence/reproduction-status.md)
- Platform integration: [docs/product-bridge/README.md](docs/product-bridge/README.md)
- Research governance: [docs/governance/research-governance.md](docs/governance/research-governance.md)
- Active task queue: [workspaces/implementation/challenger-queue.md](workspaces/implementation/challenger-queue.md)

## Platform and Runtime Boundary

No Platform or Runtime schema changes are needed for the current cleanup. If a
future result changes exported fields, report format, or recommendation logic,
create a handoff note under `docs/product-bridge/` before changing sibling
repositories.
