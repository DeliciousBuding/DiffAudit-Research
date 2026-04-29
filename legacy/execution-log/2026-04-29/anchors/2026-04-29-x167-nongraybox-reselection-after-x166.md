# X-167 Nongraybox Reselection After X166 Boundary Hardening

Date: 2026-04-29
Status: `positive reselection / one bounded GPU scout released`

## Question

After `X-166` froze H3 as candidate-only selectivity evidence and froze `PIA + GSA + SimA` tri-surface fusion as AUC-positive but low-FPR-unstable, what is the next highest-value Research lane that can use GPU without reopening a frozen surface mechanically?

## Inputs

- H3 fixed-budget closure:
  - `workspaces/implementation/2026-04-29-x163-h3-post-fixed-budget-review.md`
- Tri-surface cross-box review:
  - `workspaces/implementation/2026-04-29-x165-crossbox-trisurface-consensus-review.md`
- Boundary hardening:
  - `workspaces/implementation/2026-04-29-x166-ia-crossbox-boundary-hardening.md`
- Black-box round-2 implementation recommendation:
  - `docs/report-bundles/gpt54/round2-results/01.md`
- Current queue:
  - `workspaces/implementation/challenger-queue.md`

## Candidate Review

| Candidate | Decision | Reason |
| --- | --- | --- |
| Larger H3 selective-gating packet | reject | `X-163` already blocks promotion on gate-leak and oracle-route escape. Larger same-rule packets would only scale a known candidate-only surface. |
| Existing-surface `PIA + GSA + SimA` fusion rerun | reject | `X-165` showed stable AUC lift but unstable low-FPR behavior. No new evidence identity or surface-acquisition hypothesis exists. |
| Activation-subspace / trajectory salvage | reject | `X-145 / X-146 / X-148 / X-150 / X-154` already exhausted top-delta, validation-stable, cross-layer, and trajectory observables below release. |
| Third same-contract `G1-A / X-90` seed | reject | `X-141 / X-142` already make it two-seed internal auxiliary positive. A third same-contract seed is stability polish, not a new hypothesis. |
| Plain gray-box `SimA` or switching rerun | reject | Plain `SimA` is execution-feasible but weak; confidence-gated switching already closed negative-but-useful. |
| Heavy white-box LiRA / Strong LiRA | hold | Distinct-family value is real, but current host-fit and contract cost are above the intended bounded scout budget. |
| `I-B / I-C / I-D` successor reopening | hold | Each innovation surface remains valuable, but no genuinely new bounded successor hypothesis is currently frozen above the existing falsifier/support-only boundaries. |
| `01-black-box H2 strength-response curve` | select | This is the cleanest new surface-acquisition candidate: it acquires fresh model-response outputs rather than recombining existing PIA/GSA/SimA scores, can run as a `64 / 64` scout, and its cached outputs can later support `H1` response-cloud and `H3` frequency-filter CPU/scorer reuse. |

## Selected Contract

`X-168 black-box H2 strength-response 64/64 GPU scout`

Scope:

- asset family: canonical PIA DDPM/CIFAR10 checkpoint and split
- packet: `64` members + `64` nonmembers from frozen PIA split order
- response surface: forward-noise each image at four moderate timesteps, run bounded deterministic DDIM-style partial denoise, and cache the output images / distance vectors
- repeats: `2` noise seeds per timestep
- primary score: logistic regression over a 4-D vector of per-timestep minimum seed-to-output distances
- baseline comparators:
  - best single strength distance
  - mean distance across strengths
  - slope across strengths
- metrics:
  - `AUC`
  - `ASR`
  - `TPR@1%FPR`
  - `TPR@0.1%FPR`
- release gate:
  - positive only if the H2 logistic surface improves low-FPR over the simple distance baselines, or if it produces a clearly reusable response surface that changes the next black-box scorer path
  - AUC-only lift is negative-but-useful and cannot become a promoted black-box line

This is intentionally not a claim that `DDPM/CIFAR10` black-box strength-response has solved conditional diffusion or commercial text-to-image auditing.

## Verdict

`positive reselection / one bounded GPU scout released`

The next GPU slot is released to `X-168` only. No other GPU task is authorized in parallel. The GPU question remains bounded to a small response-surface acquisition scout, not a full black-box benchmark.

## Control State

- `active_gpu_question = X168 black-box H2 strength-response 64/64 GPU scout`
- `next_gpu_candidate = X168 bounded H2 strength-response response-surface scout`
- `current_execution_lane = X168 black-box H2 strength-response GPU scout`
- `cpu_sidecar = I-A / cross-box boundary maintenance plus H1/H3 scorer-reuse design`

## Handoff

- `Platform`: no schema or UI handoff unless `X-168` produces a promoted low-FPR improvement, which is not expected at scout scale.
- `Runtime-Server`: no runner handoff before `X-168` verdict; this remains a research script and cached evidence surface.
- `Docs/materials`: if mentioned, frame as a black-box candidate-surface scout, not admitted evidence.
