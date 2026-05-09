# DiffAudit Research Roadmap

> Last updated: 2026-05-10

This is the short steering document for Research. Execution history and old
run narratives live in `legacy/`; current workspace state lives in
`workspaces/`; reviewed evidence lives in `docs/evidence/`.

## Current Focus

| Field | Current value |
| --- | --- |
| Active work | `ReDiffuse scoring-contract parity review` |
| Current GPU candidate | `ReDiffuse 750k ResNet 64/64 parity packet` |
| CPU sidecar | `ReDiffuse 800k probe evidence sync` plus CLiD/variation boundary maintenance |
| Active GPU question | none running |
| Platform/Runtime impact | none; candidate-only Research work |

Current objective: decide whether the collaborator `DDIMrediffuse` bundle can
produce a paper-faithful gray-box baseline that is comparable with PIA/SecMI, or
whether Research should keep the current `first_step_distance_mean` scorer as a
separate candidate baseline.

## Mainline Claims

| Lane | Status | Current claim | Boundary |
| --- | --- | --- | --- |
| Black-box `recon` | admitted | Current black-box product row and minimal-permission risk proof. | Public-100 strict-tail fields are finite-count evidence, not calibrated continuous sub-percent FPR. |
| Gray-box `PIA` | admitted | Strongest gray-box attack + stochastic-dropout defense story. | Workspace-verified and adaptive-reviewed, but paper-aligned release provenance remains bounded. |
| White-box `GSA + DPDM W-1` | admitted comparator | Strongest white-box risk upper bound plus defended comparator. | Not a final paper-level benchmark. |
| ReDiffuse | candidate | Collaborator bundle and 750k checkpoint are runnable; 800k checkpoint is runtime-probe compatible. | Not admitted; scoring-contract parity is unresolved. |
| CLiD / H2 / simple-distance / variation / semantic-aux | hold or candidate-only | Useful diagnostics and bounded candidates. | No GPU task unless a new protocol/data contract clears a CPU preflight. |

## Current Gate

The only released next GPU candidate is:

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

Success criteria:

- `status = ready`
- same CIFAR10 ratio0.5 split hash:
  `aca922ecee25ef00dc6b6377ebaf7875dfcc77c2cdfe27c873b26a65134aa0c0`
- `checkpoint_step = 750000`
- `scoring_mode = resnet`
- four metrics present: `AUC`, `ASR`, `TPR@1%FPR`, `TPR@0.1%FPR`
- ResNet train/test counts recorded
- verdict states whether ResNet parity is viable, candidate-only, or negative

Stop conditions:

- CUDA unavailable or memory pressure appears
- ResNet scorer is reversed or near-random at 64/64
- output lacks low-FPR fields, split identity, checkpoint step, or scorer
  contract fields
- result would require Platform/Runtime schema changes before a product-bridge
  handoff exists

## Next Decision Contract

After the 750k ResNet 64/64 parity packet:

1. If ResNet parity is positive and not reversed, run a 800k ReDiffuse
   direct-distance sanity packet before any PIA/SecMI comparison.
2. If ResNet parity is weak or reversed, freeze ReDiffuse as
   `candidate-only / scoring-contract unresolved` and keep direct-distance as a
   separate Research surface.
3. Do not update `docs/evidence/admitted-results-summary.md` unless a later
   reviewed packet is explicitly promoted.
4. Do not change Platform or Runtime schemas in this cycle.

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
| ReDiffuse 800k runtime-probe note | CPU-only | 800k can load under the ReDiffuse bundle, but metrics are not run yet. |
| CLiD prompt-conditioned boundary | CPU-only | Preserve diagnostic claim boundary; no GPU unless a new image-identity protocol exists. |
| Variation query-contract watch | CPU-only / blocked | Reopen only when real member/nonmember query images and endpoint contract exist. |
| Simple-distance second-asset portability | needs assets | Reopen only with a second valid image-to-image or repeated-response contract. |

## Recent Verdicts

| Item | Verdict | Evidence |
| --- | --- | --- |
| ReDiffuse collaborator bundle intake | positive intake, candidate-only | [docs/evidence/rediffuse-collaborator-bundle-intake.md](docs/evidence/rediffuse-collaborator-bundle-intake.md) |
| ReDiffuse 750k direct-distance 64/64 | positive compatibility packet, not admitted | [docs/evidence/rediffuse-cifar10-small-packet.md](docs/evidence/rediffuse-cifar10-small-packet.md) |
| ReDiffuse 800k runtime probe | runtime-compatible, metrics not run | [docs/evidence/rediffuse-800k-runtime-probe.md](docs/evidence/rediffuse-800k-runtime-probe.md) |
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
