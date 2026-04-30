# DiffAudit Research Roadmap

> Last updated: 2026-05-01

This is the short steering document for Research. Execution history is in
`legacy/`; current workspace state is in `workspaces/`.

## Current Focus

- **Active work:** CLiD candidate stability and adaptive review
- **Next GPU task:** none selected
- **CPU work:** audit CLiD 100/100 score packet for row alignment, leakage, and repeatability

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

Resume with CLiD candidate stability and adaptive review. H2 is held for cross-asset work
because SD/CelebA text-to-image is protocol-incompatible with H2
response-strength. `recon` remains the admitted black-box baseline, `variation`
lacks a real query set and endpoint, and CLiD is selected as the next bounded
prompt-conditioned black-box lane. The first local bridge preparation succeeded
with 8 member and 8 nonmember exports, the bridge contract review passed, and
the score-summary schema gate is defined. The first 8/8 tiny CLiD score bridge
was reusable but not promotable. The 100/100 packet clears the score-summary
gate with strong low-FPR signal, but remains candidate-only until stability,
row-alignment, and adaptive leakage review pass.

## Key Documents

- Project overview: [README.md](README.md)
- Documentation index: [docs/README.md](docs/README.md)
- Experiment status: [docs/evidence/reproduction-status.md](docs/evidence/reproduction-status.md)
- CLiD score gate: [docs/evidence/clid-score-schema-gate.md](docs/evidence/clid-score-schema-gate.md)
- Platform integration: [docs/product-bridge/README.md](docs/product-bridge/README.md)
- Research governance: [docs/governance/research-governance.md](docs/governance/research-governance.md)
- Active task queue: [workspaces/implementation/challenger-queue.md](workspaces/implementation/challenger-queue.md)

## Platform and Runtime Boundary

No Platform or Runtime schema changes are needed for the current cleanup. If a
future result changes exported fields, report format, or recommendation logic,
create a handoff note under `docs/product-bridge/` before changing sibling
repositories.
