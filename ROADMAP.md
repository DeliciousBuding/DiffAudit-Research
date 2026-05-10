# DiffAudit Research Roadmap

> Last updated: 2026-05-11

This is the short steering document for Research. Execution history and old
run narratives live in `legacy/`; current workspace state lives in
`workspaces/`; reviewed evidence lives in `docs/evidence/`.

## Current Focus

| Field | Current value |
| --- | --- |
| Active work | `black-box response-contract protocol scaffold` |
| Current GPU candidate | none selected |
| CPU sidecar | CPU-only response-contract package construction; no model run |
| Active GPU question | none running |
| Platform/Runtime impact | none; asset-readiness verdict only |

Current objective: turn the black-box response-contract blocker into a precise
portable package handoff without claiming assets are ready. The
Kandinsky/Pokemon package scaffold dry-run is frozen at
`response-contract-pokemon-kandinsky-20260511`; it still needs real
member/nonmember query images, split ids, endpoint provenance, response files,
manifest metadata, and integrity hashes before any model run can reopen. See
[docs/evidence/blackbox-response-contract-protocol-scaffold-20260511.md](docs/evidence/blackbox-response-contract-protocol-scaffold-20260511.md).
I-B risk-targeted unlearning and I-C cross-permission successor scoping are both
on hold; neither releases GPU work. See
[docs/evidence/ib-risk-targeted-unlearning-successor-scope.md](docs/evidence/ib-risk-targeted-unlearning-successor-scope.md)
and
[docs/evidence/ic-cross-permission-successor-scope.md](docs/evidence/ic-cross-permission-successor-scope.md).
The downstream consumer boundary is synchronized: admitted rows remain `recon`,
`PIA`, and `GSA + DPDM W-1`; ReDiffuse, tri-score, cross-box fusion,
H2/simple-distance, CLiD, GSA LR, and black-box response-contract acquisition
remain candidate, negative, hold, or needs-assets states. See
[docs/evidence/research-boundary-consumability-sync-20260510.md](docs/evidence/research-boundary-consumability-sync-20260510.md).
Gray-box tri-score survives as internal Research candidate evidence, but it is
not admitted, not product-facing, and not a GPU release candidate. See
[docs/evidence/graybox-triscore-consolidation-review.md](docs/evidence/graybox-triscore-consolidation-review.md)
and
[docs/evidence/graybox-triscore-truth-hardening-review.md](docs/evidence/graybox-triscore-truth-hardening-review.md).
The systematic black-box response-contract discovery closed as `needs-assets`,
so acquiring or constructing second response-contract assets remains required
before black-box portability validation can run. The post-tri-score intake
refresh also closes as `needs-assets`; the 2026-05-11 scaffold dry-run now
freezes the next package handoff layout without changing that verdict. See
[docs/evidence/blackbox-response-contract-second-asset-intake-20260511.md](docs/evidence/blackbox-response-contract-second-asset-intake-20260511.md)
and
[docs/evidence/blackbox-response-contract-protocol-scaffold-20260511.md](docs/evidence/blackbox-response-contract-protocol-scaffold-20260511.md).
The 750k
exact-replay GPU packet completed with `AUC = 0.702293`, but strict-tail
evidence remains weak (`TPR@1%FPR = 0.019231`, `TPR@0.1%FPR = 0.019231`) and
the held-out ResNet accuracy is `0.5`; ReDiffuse stays candidate-only and no
800k shortcut is released. See
[docs/evidence/rediffuse-exact-replay-packet.md](docs/evidence/rediffuse-exact-replay-packet.md)
and
[docs/evidence/post-rediffuse-next-lane-reselection.md](docs/evidence/post-rediffuse-next-lane-reselection.md).
The black-box response-contract package preflight remains `needs-assets`; see
[docs/evidence/blackbox-response-contract-acquisition-audit.md](docs/evidence/blackbox-response-contract-acquisition-audit.md)
and
[docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](docs/evidence/blackbox-response-contract-asset-acquisition-spec.md).
The package-level preflight is
[docs/evidence/blackbox-response-contract-package-preflight.md](docs/evidence/blackbox-response-contract-package-preflight.md).
The repository-level discovery pass also found no ready paired package:
[docs/evidence/blackbox-response-contract-discovery.md](docs/evidence/blackbox-response-contract-discovery.md).
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
2. Black-box second response-contract acquisition is the active CPU sidecar,
   but remains `needs-assets`. Do not GPU-scale until a package matching the
   frozen `response-contract-pokemon-kandinsky-20260511` layout exists and
   passes preflight. The scaffold dry-run is a handoff contract, not readiness.
3. Gray-box tri-score truth-hardening used existing X-88/X-141/X-142 artifacts
   only and closed as `positive-but-bounded`. Do not promote to admitted
   evidence and do not run a larger same-contract packet.
4. I-A truth-hardening completed as positive boundary hardening. See
   [docs/evidence/pia-stochastic-dropout-truth-hardening-review.md](docs/evidence/pia-stochastic-dropout-truth-hardening-review.md).
5. Non-gray-box reselection selected a CPU-only black-box response-contract
   acquisition audit. It closed as `needs-assets`, not GPU-ready. The minimum
   acquisition package is specified in
   [docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](docs/evidence/blackbox-response-contract-asset-acquisition-spec.md);
   see also
   [docs/evidence/blackbox-response-contract-acquisition-audit.md](docs/evidence/blackbox-response-contract-acquisition-audit.md)
   for the audit result and
   [docs/evidence/non-graybox-reselection-20260510.md](docs/evidence/non-graybox-reselection-20260510.md).
6. Do not update `docs/evidence/admitted-results-summary.md` unless a reviewed
   packet is explicitly promoted.
7. Boundary-consumability sync completed without changing Platform or Runtime
   schemas. Downstream consumers should continue using only the admitted rows
   listed in `docs/evidence/admitted-results-summary.md`.
8. I-B risk-targeted unlearning is on hold until a defended-shadow or
   adaptive-attacker review contract is frozen. Do not GPU-scale the existing
   threshold-transfer diagnostics.
9. I-C cross-permission / translated-contract work is on hold until a same-spec
   evaluator and matched random comparator contract exist. Do not spend GPU on
   same-pair replay.

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
| Response-contract package construction | CPU-only / needs assets | Use the 2026-05-11 scaffold as the portable handoff target; no GPU until preflight is ready. |

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
| Post-ReDiffuse reselection | selects black-box second response-contract acquisition; no GPU release | [docs/evidence/post-rediffuse-next-lane-reselection.md](docs/evidence/post-rediffuse-next-lane-reselection.md) |
| Gray-box tri-score consolidation | positive-but-bounded internal evidence; no admitted promotion | [docs/evidence/graybox-triscore-consolidation-review.md](docs/evidence/graybox-triscore-consolidation-review.md) |
| Gray-box tri-score truth-hardening | positive-but-bounded internal evidence; no admitted promotion and no GPU release | [docs/evidence/graybox-triscore-truth-hardening-review.md](docs/evidence/graybox-triscore-truth-hardening-review.md) |
| PIA stochastic-dropout truth-hardening | positive boundary hardening; no GPU release | [docs/evidence/pia-stochastic-dropout-truth-hardening-review.md](docs/evidence/pia-stochastic-dropout-truth-hardening-review.md) |
| Non-gray-box reselection | selected black-box response-contract acquisition audit; no GPU release | [docs/evidence/non-graybox-reselection-20260510.md](docs/evidence/non-graybox-reselection-20260510.md) |
| Black-box response-contract acquisition audit | needs-assets; no GPU release | [docs/evidence/blackbox-response-contract-acquisition-audit.md](docs/evidence/blackbox-response-contract-acquisition-audit.md) |
| Black-box response-contract asset spec | needs-assets; minimum second-asset package defined; no GPU release | [docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](docs/evidence/blackbox-response-contract-asset-acquisition-spec.md) |
| Black-box response-contract package preflight | needs-assets; Kandinsky/Pokemon has weights but no query/response package | [docs/evidence/blackbox-response-contract-package-preflight.md](docs/evidence/blackbox-response-contract-package-preflight.md) |
| Black-box response-contract discovery | needs-assets; no paired package found under black-box dataset/supplementary roots | [docs/evidence/blackbox-response-contract-discovery.md](docs/evidence/blackbox-response-contract-discovery.md) |
| Black-box response-contract second-asset intake | needs-assets; no ready package after post-tri-score refresh | [docs/evidence/blackbox-response-contract-second-asset-intake-20260511.md](docs/evidence/blackbox-response-contract-second-asset-intake-20260511.md) |
| Black-box response-contract protocol scaffold | CPU-only scaffold dry-run; needs-assets; no GPU release | [docs/evidence/blackbox-response-contract-protocol-scaffold-20260511.md](docs/evidence/blackbox-response-contract-protocol-scaffold-20260511.md) |
| Research boundary-consumability sync | synchronized admitted-vs-candidate boundary; no schema change | [docs/evidence/research-boundary-consumability-sync-20260510.md](docs/evidence/research-boundary-consumability-sync-20260510.md) |
| I-B risk-targeted unlearning successor scope | hold; no GPU release until defended-shadow/adaptive review contract exists | [docs/evidence/ib-risk-targeted-unlearning-successor-scope.md](docs/evidence/ib-risk-targeted-unlearning-successor-scope.md) |
| I-C cross-permission successor scope | hold; no GPU release until same-spec evaluator and matched comparator exist | [docs/evidence/ic-cross-permission-successor-scope.md](docs/evidence/ic-cross-permission-successor-scope.md) |
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

No Platform or Runtime schema changes are needed. The current consumer rule is
to use only admitted rows (`recon`, `PIA`, `GSA + DPDM W-1`) and keep
ReDiffuse, tri-score, cross-box fusion, H2/simple-distance, CLiD, GSA LR, and
response-contract acquisition out of product-facing admitted evidence. If a
future result changes exported fields, report format, or recommendation logic,
create a handoff note under `docs/product-bridge/` before changing sibling
repositories.
