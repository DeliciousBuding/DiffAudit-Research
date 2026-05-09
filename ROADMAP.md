# DiffAudit Research Roadmap

> Last updated: 2026-05-10

This is the short steering document for Research. Execution history and old
run narratives live in `legacy/`; current workspace state lives in
`workspaces/`; reviewed evidence lives in `docs/evidence/`.

## Current Focus

| Field | Current value |
| --- | --- |
| Active work | `ReDiffuse post-parity contract review` |
| Current GPU candidate | none selected |
| CPU sidecar | `ReDiffuse direct-distance boundary review` plus CLiD/variation boundary maintenance |
| Active GPU question | none running |
| Platform/Runtime impact | none; candidate-only Research work |

Current objective: close the ReDiffuse scoring-contract gate. The
collaborator-style ResNet scorer ran on the 750k checkpoint but did not produce
an interpretable membership signal. Research should keep the current
`first_step_distance_mean` surface as candidate-only unless a new CPU contract
justifies a different scorer hypothesis.

## Mainline Claims

| Lane | Status | Current claim | Boundary |
| --- | --- | --- | --- |
| Black-box `recon` | admitted | Current black-box product row and minimal-permission risk proof. | Public-100 strict-tail fields are finite-count evidence, not calibrated continuous sub-percent FPR. |
| Gray-box `PIA` | admitted | Strongest gray-box attack + stochastic-dropout defense story. | Workspace-verified and adaptive-reviewed, but paper-aligned release provenance remains bounded. |
| White-box `GSA + DPDM W-1` | admitted comparator | Strongest white-box risk upper bound plus defended comparator. | Not a final paper-level benchmark. |
| ReDiffuse | candidate-only | Collaborator bundle and 750k checkpoint are runnable; 800k checkpoint is runtime-probe compatible; ResNet parity packet is negative. | Not admitted; current paper-faithful scoring parity is unresolved. |
| CLiD / H2 / simple-distance / variation / semantic-aux | hold or candidate-only | Useful diagnostics and bounded candidates. | No GPU task unless a new protocol/data contract clears a CPU preflight. |

## Current Gate Verdict

The released 750k ResNet parity packet has completed:

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

## Next Decision Contract

1. Freeze ReDiffuse as `candidate-only / scoring-contract unresolved`.
2. Do not run an automatic 800k metrics packet from the failed ResNet parity
   gate.
3. Run a CPU-only direct-distance boundary review before any further ReDiffuse
   GPU work.
4. Do not update `docs/evidence/admitted-results-summary.md` unless a later
   reviewed packet is explicitly promoted.
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
| ReDiffuse direct-distance boundary review | CPU-only | Decide whether the positive 750k direct-distance packet is worth a new hypothesis, or should close as separate candidate-only surface. |
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

No Platform or Runtime schema changes are needed for the current ReDiffuse
parity cycle. If a future result changes exported fields, report format, or
recommendation logic, create a handoff note under `docs/product-bridge/` before
changing sibling repositories.
