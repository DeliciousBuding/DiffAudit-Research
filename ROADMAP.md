# DiffAudit Research Roadmap

> Last updated: 2026-05-10

This is the short steering document for Research. Execution history and old
run narratives live in `legacy/`; current workspace state lives in
`workspaces/`; reviewed evidence lives in `docs/evidence/`.

## Current Focus

| Field | Current value |
| --- | --- |
| Active work | `ReDiffuse exact replay packet verdict` |
| Current GPU candidate | none selected |
| CPU sidecar | next-lane reselection after ReDiffuse candidate-only closure |
| Active GPU question | none running |
| Platform/Runtime impact | none; candidate-only Research work |

Current objective: close the ReDiffuse exact-replay gate and reselect the next
lane. The 750k exact-replay GPU packet completed with `AUC = 0.702293`, but
strict-tail evidence remains weak (`TPR@1%FPR = 0.019231`,
`TPR@0.1%FPR = 0.019231`) and the held-out ResNet accuracy is `0.5`. ReDiffuse
stays candidate-only; no 800k shortcut is released. See
[docs/evidence/rediffuse-exact-replay-packet.md](docs/evidence/rediffuse-exact-replay-packet.md).
The black-box response-contract package preflight remains `needs-assets`; see
[docs/evidence/blackbox-response-contract-acquisition-audit.md](docs/evidence/blackbox-response-contract-acquisition-audit.md)
and
[docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](docs/evidence/blackbox-response-contract-asset-acquisition-spec.md).
The package-level preflight is
[docs/evidence/blackbox-response-contract-package-preflight.md](docs/evidence/blackbox-response-contract-package-preflight.md).
The resting-state audit is
[docs/evidence/research-resting-state-audit-20260510.md](docs/evidence/research-resting-state-audit-20260510.md).
The first post-resting CPU discovery review closed the GSA loss-score LR rescue
path as negative-but-useful; see
[docs/evidence/gsa-loss-score-shadow-stability-review.md](docs/evidence/gsa-loss-score-shadow-stability-review.md).

## Mainline Claims

| Lane | Status | Current claim | Boundary |
| --- | --- | --- | --- |
| Black-box `recon` | admitted | Current black-box product row and minimal-permission risk proof. | Public-100 strict-tail fields are finite-count evidence, not calibrated continuous sub-percent FPR. |
| Gray-box `PIA` | admitted | Strongest admitted local DDPM/CIFAR10 gray-box line; stochastic dropout is a provisional defended comparator. | Bounded repeated-query adaptive review only; low-FPR values are finite empirical tails, not calibrated sub-percent FPR. |
| White-box `GSA + DPDM W-1` | admitted comparator | Strongest white-box risk upper bound plus defended comparator. | Not a final paper-level benchmark. |
| ReDiffuse | candidate-only | Collaborator bundle and 750k checkpoint are runnable; exact replay shows modest AUC but weak strict-tail evidence. | Do not promote; do not run 800k automatically; reopen only with a new scorer hypothesis or stricter paper-faithful contract. |
| CLiD / H2 / simple-distance / variation / semantic-aux | hold or candidate-only | Useful diagnostics and bounded candidates. | No GPU task unless a new protocol/data contract clears a CPU preflight. |

## Current Gate Verdict

The ReDiffuse gate is closed as candidate-only. The released 750k ResNet parity
packet completed:

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit run-rediffuse-runtime-packet `
  --workspace workspaces/gray-box/runs/rediffuse-cifar10-750k-resnet-parity-20260510-gpu-64 `
  --device cuda `
  --max-samples 64 `
  --batch-size 8 `
  --attack-num 1 `
  --interval 200 `
  --average 10 `
  --k 100 `
  --scoring-mode resnet `
  --scorer-train-portion 0.2 `
  --scorer-epochs 15 `
  --scorer-batch-size 128
```

Result: `AUC = 0.411982`, `ASR = 0.538462`, `TPR@1%FPR = 0.0`,
`TPR@0.1%FPR = 0.0`, and best held-out ResNet accuracy `0.5`. Runtime checks
passed, but the scorer is not a viable parity surface at this gate. See
[docs/evidence/rediffuse-resnet-parity-packet.md](docs/evidence/rediffuse-resnet-parity-packet.md).

The follow-up direct-distance boundary review blocks an automatic 800k metrics
packet because it would only test a Research-specific proxy surface. See
[docs/evidence/rediffuse-direct-distance-boundary-review.md](docs/evidence/rediffuse-direct-distance-boundary-review.md).
The checkpoint-portability gate confirms that 750k/800k metadata and the
collaborator split are compatible, but it still blocks GPU because the
paper-faithful scorer contract is unresolved. See
[docs/evidence/rediffuse-checkpoint-portability-gate.md](docs/evidence/rediffuse-checkpoint-portability-gate.md).
The ResNet contract scout resolves the ambiguity against the current adapter:
collaborator `nns_attack` does not update `test_acc_best` and negates logits
before a member-lower ROC, while the Research adapter restores the true best
held-out epoch and uses unnegated logits as higher-is-member scores. See
[docs/evidence/rediffuse-resnet-contract-scout.md](docs/evidence/rediffuse-resnet-contract-scout.md).
The exact replay preflight adds `resnet_collaborator_replay`, preserving the
collaborator checkpoint-selection counter contract while keeping raw logits in
the project metric convention. A 4-sample CPU smoke passed. See
[docs/evidence/rediffuse-exact-replay-preflight.md](docs/evidence/rediffuse-exact-replay-preflight.md).
The bounded 750k exact-replay packet then completed on CUDA. It shows modest
AUC but weak strict-tail evidence and no admitted promotion. See
[docs/evidence/rediffuse-exact-replay-packet.md](docs/evidence/rediffuse-exact-replay-packet.md).

## Next Decision Contract

1. ReDiffuse is closed as candidate-only for now. Do not run 800k or larger
   ReDiffuse packets without a new scorer hypothesis and CPU preflight.
2. I-A truth-hardening completed as positive boundary hardening. See
   [docs/evidence/pia-stochastic-dropout-truth-hardening-review.md](docs/evidence/pia-stochastic-dropout-truth-hardening-review.md).
3. Non-gray-box reselection selected a CPU-only black-box response-contract
   acquisition audit. It closed as `needs-assets`, not GPU-ready. The minimum
   acquisition package is specified in
   [docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](docs/evidence/blackbox-response-contract-asset-acquisition-spec.md);
   see also
   [docs/evidence/blackbox-response-contract-acquisition-audit.md](docs/evidence/blackbox-response-contract-acquisition-audit.md)
   for the audit result and
   [docs/evidence/non-graybox-reselection-20260510.md](docs/evidence/non-graybox-reselection-20260510.md).
4. Do not update `docs/evidence/admitted-results-summary.md` unless a reviewed
   packet is explicitly promoted.
5. Do not change Platform or Runtime schemas in this cycle.

## Long-Running Goal Loop

Every autonomous research cycle must follow this loop:

1. `review`: read this roadmap, reproduction status, admitted results,
   workspace evidence index, challenger queue, and the relevant workspace plan.
2. `select`: choose one bounded question; keep at most one active GPU task.
3. `preflight`: freeze hypothesis, assets, split, metrics, falsifier, GPU cap,
   output path, and stop conditions.
4. `run`: start with CPU/tiny smoke; run at most one bounded GPU packet.
5. `verdict`: classify as `admitted`, `candidate-only`, `hold`, or
   `negative-but-useful`.
6. `sync`: update the evidence note, `ROADMAP.md`,
   `workspaces/implementation/challenger-queue.md`, and the relevant workspace
   plan.
7. `next`: set `next_gpu_candidate = none` unless the next bounded packet is
   explicitly released.

## Current Sidecars

| Sidecar | Mode | Why |
| --- | --- | --- |
| CLiD prompt-conditioned boundary | CPU-only | Preserve diagnostic claim boundary; no GPU unless a new image-identity protocol exists. |
| Variation query-contract watch | CPU-only / blocked | Reopen only when real member/nonmember query images and endpoint contract exist. |
| Simple-distance second-asset portability | needs assets | Reopen only with a second valid image-to-image or repeated-response contract. |

## Recent Verdicts

| Item | Verdict | Evidence |
| --- | --- | --- |
| ReDiffuse collaborator bundle intake | positive intake, candidate-only | [docs/evidence/rediffuse-collaborator-bundle-intake.md](docs/evidence/rediffuse-collaborator-bundle-intake.md) |
| ReDiffuse 750k direct-distance 64/64 | positive compatibility packet, not admitted | [docs/evidence/rediffuse-cifar10-small-packet.md](docs/evidence/rediffuse-cifar10-small-packet.md) |
| ReDiffuse 800k runtime probe | runtime-compatible, metrics not run | [docs/evidence/rediffuse-800k-runtime-probe.md](docs/evidence/rediffuse-800k-runtime-probe.md) |
| ReDiffuse 750k ResNet parity | negative-but-useful; scoring-contract unresolved | [docs/evidence/rediffuse-resnet-parity-packet.md](docs/evidence/rediffuse-resnet-parity-packet.md) |
| ReDiffuse direct-distance boundary | closed as candidate-only; no GPU release | [docs/evidence/rediffuse-direct-distance-boundary-review.md](docs/evidence/rediffuse-direct-distance-boundary-review.md) |
| ReDiffuse checkpoint-portability gate | blocked-by-scoring-contract; 800k metrics shortcut remains closed | [docs/evidence/rediffuse-checkpoint-portability-gate.md](docs/evidence/rediffuse-checkpoint-portability-gate.md) |
| ReDiffuse ResNet contract scout | blocked-by-contract-mismatch; current adapter is not exact collaborator replay | [docs/evidence/rediffuse-resnet-contract-scout.md](docs/evidence/rediffuse-resnet-contract-scout.md) |
| ReDiffuse exact replay preflight | CPU preflight passed; no GPU release | [docs/evidence/rediffuse-exact-replay-preflight.md](docs/evidence/rediffuse-exact-replay-preflight.md) |
| ReDiffuse 750k exact replay | candidate-only; modest AUC but weak strict-tail evidence | [docs/evidence/rediffuse-exact-replay-packet.md](docs/evidence/rediffuse-exact-replay-packet.md) |
| PIA stochastic-dropout truth-hardening | positive boundary hardening; no GPU release | [docs/evidence/pia-stochastic-dropout-truth-hardening-review.md](docs/evidence/pia-stochastic-dropout-truth-hardening-review.md) |
| Non-gray-box reselection | selected black-box response-contract acquisition audit; no GPU release | [docs/evidence/non-graybox-reselection-20260510.md](docs/evidence/non-graybox-reselection-20260510.md) |
| Black-box response-contract acquisition audit | needs-assets; no GPU release | [docs/evidence/blackbox-response-contract-acquisition-audit.md](docs/evidence/blackbox-response-contract-acquisition-audit.md) |
| Black-box response-contract asset spec | needs-assets; minimum second-asset package defined; no GPU release | [docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](docs/evidence/blackbox-response-contract-asset-acquisition-spec.md) |
| Black-box response-contract package preflight | needs-assets; Kandinsky/Pokemon has weights but no query/response package | [docs/evidence/blackbox-response-contract-package-preflight.md](docs/evidence/blackbox-response-contract-package-preflight.md) |
| Research resting-state audit | temporary resting state; no active GPU candidate or reducible CPU sidecar until assets or a new hypothesis arrive | [docs/evidence/research-resting-state-audit-20260510.md](docs/evidence/research-resting-state-audit-20260510.md) |
| GSA loss-score shadow stability | negative-but-useful; LR distinct-scorer rescue path fails leave-one-shadow-out gate | [docs/evidence/gsa-loss-score-shadow-stability-review.md](docs/evidence/gsa-loss-score-shadow-stability-review.md) |
| Recon product row | admitted black-box row | [docs/evidence/recon-product-validation-result.md](docs/evidence/recon-product-validation-result.md) |
| Semantic-aux low-FPR review | negative-but-useful | [docs/evidence/semantic-aux-low-fpr-review.md](docs/evidence/semantic-aux-low-fpr-review.md) |

## Key Source Documents

- Project overview: [README.md](README.md)
- Documentation index: [docs/README.md](docs/README.md)
- Experiment status: [docs/evidence/reproduction-status.md](docs/evidence/reproduction-status.md)
- Verified results: [docs/evidence/admitted-results-summary.md](docs/evidence/admitted-results-summary.md)
- Innovation map: [docs/evidence/innovation-evidence-map.md](docs/evidence/innovation-evidence-map.md)
- Workspace index: [docs/evidence/workspace-evidence-index.md](docs/evidence/workspace-evidence-index.md)
- Active queue: [workspaces/implementation/challenger-queue.md](workspaces/implementation/challenger-queue.md)
- Gray-box plan: [workspaces/gray-box/plan.md](workspaces/gray-box/plan.md)
- Product bridge: [docs/product-bridge/README.md](docs/product-bridge/README.md)
- Research governance: [docs/governance/research-governance.md](docs/governance/research-governance.md)

## Platform and Runtime Boundary

No Platform or Runtime schema changes are needed for the current black-box
response-contract acquisition state. If a future result changes exported
fields, report format, or recommendation logic, create a handoff note under
`docs/product-bridge/` before changing sibling repositories.
