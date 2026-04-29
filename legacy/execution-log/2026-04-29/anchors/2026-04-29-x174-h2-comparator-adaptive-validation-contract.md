# X-174 H2 Comparator / Adaptive Validation Contract Freeze

Date: 2026-04-29
Status: `positive contract freeze / CPU stress next`

## Question

After `X-172` validated H2 on a non-overlap `128 / 128` packet and `X-173` held promotion/GPU expansion, what exact contract must be satisfied before any larger H2 GPU rung is allowed?

## Inputs

- X168 scout:
  - `workspaces/implementation/2026-04-29-x168-blackbox-h2-strength-response-gpu-scout.md`
- X171 frequency boundary:
  - `workspaces/implementation/2026-04-29-x171-h3-frequency-filter-cache-ablation.md`
- X172 validation:
  - `workspaces/implementation/2026-04-29-x172-h2-strength-response-validation.md`
- X173 post-validation review:
  - `workspaces/implementation/2026-04-29-x173-h2-post-validation-boundary-review.md`

## Frozen Status

H2 strength-response is now:

- `validated positive-but-bounded black-box candidate surface`
- not admitted evidence
- not a `recon` replacement
- not a Runtime/Platform consumer contract
- not evidence for conditional diffusion, Stable Diffusion, or DiT

## Frozen Contract For Any Future GPU Rung

### 1. Packet Identity

Future larger validation must use a non-overlap packet:

- default next GPU packet, if later released: `256 / 256`
- split offset: `192`
  - skips the first `64 / 64` used by `X-168`
  - skips the next `128 / 128` used by `X-172`
- same asset family:
  - PIA DDPM/CIFAR10 checkpoint
  - PIA split file under `external/PIA/DDPM`

### 2. Query Budget

The fixed budget remains:

- four timesteps: `40 / 80 / 120 / 160`
- two repeats per timestep
- total model-response calls per sample: `8`
- no extra adaptive retry or post-hoc repeat budget may be added inside the validation packet

Before any `256 / 256` GPU run, a CPU-only cache stress must report whether the current `128 / 128` validation still works under:

- one-repeat budget (`4` calls/sample)
- per-timestep leave-one-strength-out features
- raw H2 versus `lowpass_0_5` H2 scorer stability

### 3. Scorer Selection

Primary scorer stays:

- raw H2 logistic over four minimum original-to-output RMSE features

Mandatory secondary scorer:

- H3 `lowpass_0_5` H2 logistic

Promotion of `lowpass_0_5` to primary is not allowed unless a CPU stress packet freezes a no-leak scorer-selection rule. The current reason is simple: `lowpass_0_5` improves low-FPR on `X-172`, but it was introduced as a boundary check and should not become a post-hoc primary scorer without a fixed selection rule.

### 4. Comparator

Current same-packet comparator is still simple H2 baselines only:

- single timestep
- mean minimum distance
- distance slope

A same-packet `recon` comparator is not frozen yet. That blocks admitted black-box promotion even if the next H2 GPU rung is positive.

The next comparator work should be CPU-first:

- decide whether a same-packet `recon` comparator is implementable on the PIA DDPM/CIFAR10 packet
- if not, explicitly record H2 as `validated candidate without admitted comparator`

### 5. Kill Gate For Larger GPU

Do not release `256 / 256` unless the CPU stress in the current `128 / 128` cache shows:

- raw or predeclared lowpass H2 beats the best simple low-FPR baseline on both `TPR@1%FPR` and `TPR@0.1%FPR`
- one-repeat budget does not collapse both low-FPR metrics to zero
- leave-one-strength-out does not show a single mandatory timestep without which all low-FPR signal disappears
- raw-vs-lowpass scorer choice is predeclared before the next GPU run
- no same-packet comparator wording claims H2 is admitted or `recon`-superior

## Verdict

`positive contract freeze / CPU stress next`

The next live task is `X-175 H2 query-budget and scorer-stability cache stress` on the X172 cache. No new GPU task is released yet.

## Control State

- `active_gpu_question = none`
- `next_gpu_candidate = none until X175 query-budget/scorer-stability stress passes the X174 gate`
- `current_execution_lane = X175 H2 query-budget and scorer-stability cache stress`
- `cpu_sidecar = I-A / cross-box boundary maintenance`

## Handoff

- `Platform`: no handoff.
- `Runtime-Server`: no handoff.
- `Docs/materials`: no public claim change. H2 remains a validated internal candidate, not admitted evidence.
