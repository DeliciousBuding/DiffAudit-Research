# DiffAudit Research Roadmap

> Last updated: 2026-05-01

This is the short steering document for Research. Execution history is in
`legacy/`; current workspace state is in `workspaces/`.

## Current Focus

- **Active work:** CLiD adaptive prompt-perturbation design
- **Next GPU task:** none selected
- **CPU work:** design the next admission test that separates prompt signal from membership signal

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

Resume with CLiD adaptive prompt-perturbation design. H2 is held for cross-asset work
because SD/CelebA text-to-image is protocol-incompatible with H2
response-strength. `recon` remains the admitted black-box baseline, `variation`
lacks a real query set and endpoint, and CLiD is selected as the next bounded
prompt-conditioned black-box lane. The first local bridge preparation succeeded
with 8 member and 8 nonmember exports, the bridge contract review passed, and
the score-summary schema gate is defined. The first 8/8 tiny CLiD score bridge
was reusable but not promotable. The 100/100 packet clears the score-summary
gate with strong low-FPR signal, but remains candidate-only until stability,
row-alignment, and adaptive leakage review pass. The first integrity review
found no obvious row-alignment, duplicate-image, duplicate-prompt, or text-length
leakage explanation, and an independent repeat is stable. Prompt-neutral
perturbation collapses the signal, so CLiD should be treated as a
prompt-conditioned candidate rather than admitted general black-box evidence.
The next CLiD task is CPU-only: specify an admission test that can separate
prompt information from membership signal before any new GPU packet is selected.

## Key Documents

- Project overview: [README.md](README.md)
- Documentation index: [docs/README.md](docs/README.md)
- Experiment status: [docs/evidence/reproduction-status.md](docs/evidence/reproduction-status.md)
- CLiD score gate: [docs/evidence/clid-score-schema-gate.md](docs/evidence/clid-score-schema-gate.md)
- CLiD prompt boundary: [docs/evidence/clid-prompt-conditioning-boundary.md](docs/evidence/clid-prompt-conditioning-boundary.md)
- CLiD prompt-control contract: [docs/evidence/clid-adaptive-prompt-perturbation-contract.md](docs/evidence/clid-adaptive-prompt-perturbation-contract.md)
- Platform integration: [docs/product-bridge/README.md](docs/product-bridge/README.md)
- Research governance: [docs/governance/research-governance.md](docs/governance/research-governance.md)
- Active task queue: [workspaces/implementation/challenger-queue.md](workspaces/implementation/challenger-queue.md)

## Platform and Runtime Boundary

No Platform or Runtime schema changes are needed for the current cleanup. If a
future result changes exported fields, report format, or recommendation logic,
create a handoff note under `docs/product-bridge/` before changing sibling
repositories.
