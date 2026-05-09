# DiffAudit Research Roadmap

> Last updated: 2026-05-09

This is the short steering document for Research. Execution history is in
`legacy/`; current workspace state is in `workspaces/`.

## Current Focus

- **Active work:** ReDiffuse scoring-contract parity review
- **Next GPU task:** none selected after the 64/64 ReDiffuse compatibility packet
- **CPU work:** compare the direct-distance adapter scoring contract with the collaborator script's second-stage ResNet classifier

The information-architecture reset, shared utilities extraction, asset boundary
cleanup, and CLI package split are all merged. Cross-box boundary hardening is
now recorded as candidate-only evidence: score sharing is useful for internal
comparison, but the existing packets do not establish stable low-FPR gains.
On 2026-05-09, a collaborator-provided `DDIMrediffuse` bundle and 750k DDIM
checkpoint were ingested as local `Download/` assets. The bundle includes
`ReDiffuseAttacker`, matches the existing PIA CIFAR10 ratio0.5 split hash, and
can load the 750k checkpoint with the bundled UNet. This reopens a bounded
gray-box baseline-alignment task, not an admitted result. See
[docs/evidence/rediffuse-collaborator-bundle-intake.md](docs/evidence/rediffuse-collaborator-bundle-intake.md).
The Research-side adapter now passes CPU `2/2` and CUDA `8/8` compatibility
smokes, and a CUDA `64/64` small packet on the direct-distance scoring surface.
See [docs/evidence/rediffuse-runtime-smoke-result.md](docs/evidence/rediffuse-runtime-smoke-result.md).
The small packet is recorded in
[docs/evidence/rediffuse-cifar10-small-packet.md](docs/evidence/rediffuse-cifar10-small-packet.md).

## Research Directions

- **Black-box:** `recon` is the strongest main line. `CLiD` and
  semantic-auxiliary classifiers are supplementary methods.
- **Gray-box:** `PIA` is the strongest attack + defense story. Gray-box work
  remains the strongest admitted line. The new ReDiffuse bundle is a
  candidate-only baseline-alignment task.
- **White-box:** `GSA` provides the strongest upper-bound results. `DPDM` is
  the defended comparator.
- **Cross-box:** Score sharing is useful for internal comparison, but remains
  candidate-only. See [docs/evidence/cross-box-boundary-status.md](docs/evidence/cross-box-boundary-status.md).

## Next Steps

Proceed with ReDiffuse compatibility review before scheduling another model
run. The immediate goal is to determine whether the collaborator bundle can
reproduce a small CIFAR10 membership-inference packet and whether its protocol
can be compared against the existing PIA/SecMI line without changing output
schemas. Do not promote the 750k checkpoint or ReDiffuse runner until a real
attack run produces metrics with provenance, split, and low-FPR fields.
The next concrete step is a CPU-first scoring-contract review: run the newly
integrated collaborator-style second-stage ResNet scorer, then decide whether
ReDiffuse should be compared with PIA/SecMI as paper-faithful ReDiffuse or kept
as a separate direct-distance Research baseline.

Recon product-consumable strengthening is complete for the current admitted
row. H2 is held for cross-asset
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
The H2 image-to-image micro-packet has run. The protocol is runnable, but the H2
multi-strength logistic curve does not beat the same-cache simple distance
comparator. The result is recorded in
[docs/evidence/h2-img2img-micro-result.md](docs/evidence/h2-img2img-micro-result.md).
H2 remains candidate-only and should not be scaled as-is. The next CPU decision
has now reviewed the simple img2img distance signal. High-strength simple
distance is stronger than H2 logistic on the frozen cache (`AUC = 0.92`,
`ASR = 0.90`, 4/10 TP at 0 FP), but cross-strength rank stability is incomplete.
The review is recorded in
[docs/evidence/h2-img2img-simple-distance-review.md](docs/evidence/h2-img2img-simple-distance-review.md).
Do not schedule another GPU packet until the stability contract is frozen.
The stability contract is now frozen as a non-overlapping `derived-public-25`
offset-10 packet with one high-strength simple-distance scorer. See
[docs/evidence/h2-img2img-simple-distance-stability-contract.md](docs/evidence/h2-img2img-simple-distance-stability-contract.md).
That packet passed: `AUC = 0.99`, `ASR = 0.95`, and 9/10 member true positives
at 0 false positives on the finite 10/10 split. See
[docs/evidence/h2-img2img-simple-distance-stability-result.md](docs/evidence/h2-img2img-simple-distance-stability-result.md).
The simple image-to-image distance signal passed its `25/25` admission-scale
packet on `derived-public-50` positions `[20, 45)`: `AUC = 0.8768`,
`ASR = 0.84`, and 11/25 member true positives at 0 false positives. See
[docs/evidence/h2-img2img-simple-distance-admission-result.md](docs/evidence/h2-img2img-simple-distance-admission-result.md).
This promotes the signal to bounded single-asset black-box evidence, not a
conditional-diffusion generalization and not H2 response-strength promotion.
The recon-vs-simple-distance product bridge comparison is complete:
simple-distance is not product-row ready and recon remains the admitted
black-box Platform row. See
[docs/product-bridge/h2-simple-distance-product-bridge-comparison.md](docs/product-bridge/h2-simple-distance-product-bridge-comparison.md).
The second-asset simple-distance portability preflight is also complete:
current local assets do not provide a valid second image-to-image or
repeated-response contract. See
[docs/evidence/h2-simple-distance-portability-preflight.md](docs/evidence/h2-simple-distance-portability-preflight.md).
The recon product row now has a system-consumable validation guard that prevents
the unified table from silently dropping metric-source, strict-tail, source, or
boundary fields. See
[docs/evidence/recon-product-row-validation-guard.md](docs/evidence/recon-product-row-validation-guard.md).
The admitted recon row is now also exported as a checked product evidence card
for Platform and Runtime consumers. See
[docs/product-bridge/recon-product-evidence-card.md](docs/product-bridge/recon-product-evidence-card.md).
The first non-recon follow-up adds an executable variation query-contract audit.
It is blocked because the real member/nonmember query-image set and endpoint are
not present. See
[docs/evidence/variation-query-contract-audit.md](docs/evidence/variation-query-contract-audit.md).
The semantic-auxiliary classifier lane has also been reviewed against a
low-FPR promotion gate. It is negative-but-useful: the best auxiliary gain over
`mean_cos` is `0.001953`, below the `0.01` promotion gate, so no semantic-aux
GPU packet is selected. See
[docs/evidence/semantic-aux-low-fpr-review.md](docs/evidence/semantic-aux-low-fpr-review.md).
The admitted recon row now has a finite-sample confidence review. It remains
the black-box product row, but strict-tail wording must stay finite-count:
public-100 zero-FP evidence does not calibrate a continuous `0.1%` FPR operating
point at 95% confidence. See
[docs/evidence/recon-tail-confidence-review.md](docs/evidence/recon-tail-confidence-review.md).
No next GPU task is selected.

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
- Variation query contract audit: [docs/evidence/variation-query-contract-audit.md](docs/evidence/variation-query-contract-audit.md)
- Semantic-aux low-FPR review: [docs/evidence/semantic-aux-low-fpr-review.md](docs/evidence/semantic-aux-low-fpr-review.md)
- H2 image-to-image contract: [docs/evidence/h2-image-to-image-contract.md](docs/evidence/h2-image-to-image-contract.md)
- H2 image-to-image micro result: [docs/evidence/h2-img2img-micro-result.md](docs/evidence/h2-img2img-micro-result.md)
- H2 simple-distance review: [docs/evidence/h2-img2img-simple-distance-review.md](docs/evidence/h2-img2img-simple-distance-review.md)
- H2 simple-distance stability contract: [docs/evidence/h2-img2img-simple-distance-stability-contract.md](docs/evidence/h2-img2img-simple-distance-stability-contract.md)
- H2 simple-distance stability result: [docs/evidence/h2-img2img-simple-distance-stability-result.md](docs/evidence/h2-img2img-simple-distance-stability-result.md)
- H2 simple-distance admission contract: [docs/evidence/h2-img2img-simple-distance-admission-contract.md](docs/evidence/h2-img2img-simple-distance-admission-contract.md)
- H2 simple-distance admission result: [docs/evidence/h2-img2img-simple-distance-admission-result.md](docs/evidence/h2-img2img-simple-distance-admission-result.md)
- H2 simple-distance portability preflight: [docs/evidence/h2-simple-distance-portability-preflight.md](docs/evidence/h2-simple-distance-portability-preflight.md)
- Recon product validation contract: [docs/evidence/recon-product-validation-contract.md](docs/evidence/recon-product-validation-contract.md)
- Recon product validation result: [docs/evidence/recon-product-validation-result.md](docs/evidence/recon-product-validation-result.md)
- Recon tail confidence review: [docs/evidence/recon-tail-confidence-review.md](docs/evidence/recon-tail-confidence-review.md)
- ReDiffuse collaborator bundle intake: [docs/evidence/rediffuse-collaborator-bundle-intake.md](docs/evidence/rediffuse-collaborator-bundle-intake.md)
- ReDiffuse collaborator integration report: [docs/evidence/rediffuse-collaborator-integration-report.md](docs/evidence/rediffuse-collaborator-integration-report.md)
- ReDiffuse runtime smoke result: [docs/evidence/rediffuse-runtime-smoke-result.md](docs/evidence/rediffuse-runtime-smoke-result.md)
- ReDiffuse CIFAR10 small packet: [docs/evidence/rediffuse-cifar10-small-packet.md](docs/evidence/rediffuse-cifar10-small-packet.md)
- Recon product row validation guard: [docs/evidence/recon-product-row-validation-guard.md](docs/evidence/recon-product-row-validation-guard.md)
- Platform integration: [docs/product-bridge/README.md](docs/product-bridge/README.md)
- Recon product evidence card: [docs/product-bridge/recon-product-evidence-card.md](docs/product-bridge/recon-product-evidence-card.md)
- H2 simple-distance product bridge comparison: [docs/product-bridge/h2-simple-distance-product-bridge-comparison.md](docs/product-bridge/h2-simple-distance-product-bridge-comparison.md)
- Research governance: [docs/governance/research-governance.md](docs/governance/research-governance.md)
- Active task queue: [workspaces/implementation/challenger-queue.md](workspaces/implementation/challenger-queue.md)

## Platform and Runtime Boundary

No Platform or Runtime schema changes are needed for the current cleanup. If a
future result changes exported fields, report format, or recommendation logic,
create a handoff note under `docs/product-bridge/` before changing sibling
repositories.
