# DiffAudit Research Roadmap

> Last updated: 2026-05-01

This is the short steering document for Research. Execution history is in
`legacy/`; current workspace state is in `workspaces/`.

## Current Focus

- **Active work:** CLiD artifact-schema validation
- **Next GPU task:** none selected
- **CPU work:** freeze CLiD bridge output contract

The information-architecture reset, shared utilities extraction, asset boundary
cleanup, and CLI package split are all merged. Cross-box boundary hardening is
now recorded as candidate-only evidence: score sharing is useful for internal
comparison, but the existing packets do not establish stable low-FPR gains.

## Research Directions

- **Black-box:** `recon` is the strongest main line. `CLiD` and
  semantic-auxiliary classifiers are supplementary methods.
- **Gray-box:** `PIA` is the strongest attack + defense story. Gray-box work
  will not take the next research slot unless new findings change priorities.
- **White-box:** `GSA` provides the strongest upper-bound results. `DPDM` is
  the defended comparator.
- **Cross-box:** Score sharing is useful for internal comparison, but remains
  candidate-only. See [docs/evidence/cross-box-boundary-status.md](docs/evidence/cross-box-boundary-status.md).

## Next Steps

Resume with CLiD artifact-schema validation. H2 is held for cross-asset work
because SD/CelebA text-to-image is protocol-incompatible with H2
response-strength. `recon` remains the admitted black-box baseline, `variation`
lacks a real query set and endpoint, and CLiD is selected as the next bounded
prompt-conditioned black-box lane. The first local bridge preparation succeeded
with 8 member and 8 nonmember exports; no GPU packet is selected until the CLiD
summary schema and low-FPR gate are frozen.

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
