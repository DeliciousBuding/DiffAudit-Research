# DiffAudit Research Roadmap

> Last updated: 2026-05-01

This is the short steering document for Research. Execution history is in
`legacy/`; current workspace state is in `workspaces/`.

## Current Focus

- **Active work:** recon product row synchronized; next research lane selection
- **Next GPU task:** none selected
- **CPU work:** product-bridge sync and next black-box/innovation lane selection

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

Proceed with recon product-consumable strengthening. H2 is held for cross-asset
work because SD/CelebA text-to-image is protocol-incompatible with H2
response-strength. `variation` lacks a real query set and endpoint. CLiD is now
hold-candidate: its 100/100 prompt-conditioned packet is strong and
repeat-stable, but fixed-prompt, swapped-prompt, within-split shuffle,
prompt-text-only, and attribution controls show that the signal depends on an
unstable prompt-conditioned auxiliary path. Do not schedule another CLiD GPU
packet without a new protocol that isolates image identity from
prompt-conditioned behavior. The recon CPU contract is now frozen in
[docs/evidence/recon-product-validation-contract.md](docs/evidence/recon-product-validation-contract.md).
The recon code path now emits complete low-FPR metric fields, including
`TPR@0.1%FPR`. A bounded public-100 step30 rerun plus artifact re-summarization
now yields a coherent upstream-threshold candidate packet: `AUC = 0.837`,
`ASR = 0.74`, `TPR@1%FPR = 0.22`, and `TPR@0.1%FPR = 0.11`. Product-row
promotion is complete and recorded in
[docs/product-bridge/recon-product-validation-handoff.md](docs/product-bridge/recon-product-validation-handoff.md).
The next research step is to select a new non-recon lane or a truth-hardening
check that can improve the model story without weakening the claim boundary.

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
- Non-CLiD black-box reselection: [docs/evidence/non-clid-blackbox-reselection.md](docs/evidence/non-clid-blackbox-reselection.md)
- Recon product validation contract: [docs/evidence/recon-product-validation-contract.md](docs/evidence/recon-product-validation-contract.md)
- Recon product validation result: [docs/evidence/recon-product-validation-result.md](docs/evidence/recon-product-validation-result.md)
- Platform integration: [docs/product-bridge/README.md](docs/product-bridge/README.md)
- Research governance: [docs/governance/research-governance.md](docs/governance/research-governance.md)
- Active task queue: [workspaces/implementation/challenger-queue.md](workspaces/implementation/challenger-queue.md)

## Platform and Runtime Boundary

No Platform or Runtime schema changes are needed for the current cleanup. If a
future result changes exported fields, report format, or recommendation logic,
create a handoff note under `docs/product-bridge/` before changing sibling
repositories.
