# DiffAudit Research Roadmap

> Last updated: 2026-05-01

This is the short steering document for Research. Execution history is in
`legacy/`; current workspace state is in `workspaces/`.

## Current Focus

- **Active work:** non-CLiD black-box lane reselection
- **Next GPU task:** none selected
- **CPU work:** pick the next model-mainline question after closing CLiD as hold-candidate

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

Resume with non-CLiD black-box lane reselection. H2 is held for cross-asset work
because SD/CelebA text-to-image is protocol-incompatible with H2
response-strength. `recon` remains the admitted black-box baseline, `variation`
lacks a real query set and endpoint, and CLiD is now hold-candidate. CLiD's
100/100 prompt-conditioned packet is strong and repeat-stable, but fixed-prompt,
swapped-prompt, within-split shuffle, prompt-text-only, and attribution controls
show that the signal depends on an unstable prompt-conditioned auxiliary path.
Do not schedule another CLiD GPU packet without a new protocol that isolates
image identity from prompt-conditioned behavior. The immediate CPU task is to
choose the next black-box question that can improve product-consumable evidence.

## Key Documents

- Project overview: [README.md](README.md)
- Documentation index: [docs/README.md](docs/README.md)
- Experiment status: [docs/evidence/reproduction-status.md](docs/evidence/reproduction-status.md)
- CLiD score gate: [docs/evidence/clid-score-schema-gate.md](docs/evidence/clid-score-schema-gate.md)
- CLiD prompt boundary: [docs/evidence/clid-prompt-conditioning-boundary.md](docs/evidence/clid-prompt-conditioning-boundary.md)
- CLiD prompt-control contract: [docs/evidence/clid-adaptive-prompt-perturbation-contract.md](docs/evidence/clid-adaptive-prompt-perturbation-contract.md)
- CLiD swapped-prompt control: [docs/evidence/clid-swapped-prompt-control.md](docs/evidence/clid-swapped-prompt-control.md)
- CLiD within-split shuffle control: [docs/evidence/clid-within-split-shuffle-control.md](docs/evidence/clid-within-split-shuffle-control.md)
- CLiD prompt-text-only review: [docs/evidence/clid-prompt-text-only-review.md](docs/evidence/clid-prompt-text-only-review.md)
- CLiD control attribution: [docs/evidence/clid-control-attribution.md](docs/evidence/clid-control-attribution.md)
- Platform integration: [docs/product-bridge/README.md](docs/product-bridge/README.md)
- Research governance: [docs/governance/research-governance.md](docs/governance/research-governance.md)
- Active task queue: [workspaces/implementation/challenger-queue.md](workspaces/implementation/challenger-queue.md)

## Platform and Runtime Boundary

No Platform or Runtime schema changes are needed for the current cleanup. If a
future result changes exported fields, report format, or recommendation logic,
create a handoff note under `docs/product-bridge/` before changing sibling
repositories.
