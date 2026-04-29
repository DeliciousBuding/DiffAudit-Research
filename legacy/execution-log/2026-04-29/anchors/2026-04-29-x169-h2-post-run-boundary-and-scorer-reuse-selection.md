# X-169 H2 Post-Run Boundary And Scorer-Reuse Selection

Date: 2026-04-29
Status: `positive boundary / CPU scorer-reuse released`

## Question

After `X-168` produced a positive `64 / 64` black-box H2 strength-response scout, should the next step immediately spend more GPU on 128/256 validation, or first exploit the cached response surface for CPU-only H1/H3 scorer reuse and boundary review?

## Inputs

- X168 verdict:
  - `workspaces/implementation/2026-04-29-x168-blackbox-h2-strength-response-gpu-scout.md`
- X168 run:
  - `workspaces/black-box/runs/x168-h2-strength-response-gpu-scout-20260429-r1/summary.json`
- X168 response cache:
  - `workspaces/black-box/runs/x168-h2-strength-response-gpu-scout-20260429-r1/response-cache.npz`
- Round-2 black-box plan:
  - `docs/report-bundles/gpt54/round2-results/01.md`

## Review

The X168 positive signal is strong enough to keep `01-H2` live:

- `H2 logistic AUC = 0.928955`
- `H2 logistic ASR = 0.859375`
- `H2 logistic TPR@1%FPR = 0.218750`
- `H2 logistic TPR@0.1%FPR = 0.218750`
- best simple low-FPR baseline was only `0.062500 / 0.062500`

But it is not enough for immediate admission or public promotion:

- packet size is only `64 / 64`
- validation is repeated holdout on one packet, not an independent 128/256 packet
- recon comparator is not frozen inside the same black-box evaluation contract
- response surface is DDPM/CIFAR10 only
- no adaptive repeated-query or query-budget stress test is attached
- Platform/Runtime do not yet have a stable consumer contract for this surface

The response cache changes the cost calculus. Before another GPU validation rung, there are cheap CPU-only checks that can reveal whether the H2 signal is a single scorer artifact or a reusable black-box surface:

- H1 response-cloud geometry can score output-output concentration without new model calls
- H3 frequency filtering can test whether the H2 distance signal is dominated by confounding high-frequency variation
- both checks can run before deciding whether H2 deserves a 128/256 GPU validation rung

## Candidate Decisions

| Candidate | Decision | Reason |
| --- | --- | --- |
| Immediate H2 128/256 GPU validation | hold | X168 is promising, but cache-reuse CPU checks are cheaper and can reduce the risk of scaling a one-scorer artifact. |
| Promote H2 to admitted black-box evidence | reject | `64 / 64` DDPM/CIFAR10 repeated-holdout evidence is below admitted/mainline threshold. |
| H1 response-cloud cache review | select | Directly reuses X168 outputs and tests a distinct output-output scorer family with zero extra GPU. |
| H3 frequency-filter ablation | queue after H1 | Also cache-reusable, but should be evaluated as a plug-in filter after the H1/H2 scorer read is clearer. |
| Platform/Runtime handoff | reject | No consumer schema should change from one scout. |

## Verdict

`positive boundary / CPU scorer-reuse released`

`X-168` keeps black-box H2 live and changes the queue, but the next immediate task is not another GPU run. The next task is a CPU-first H1 response-cloud scorer review on the X168 cache. H3 frequency filtering remains the next CPU ablation after that.

## Control State

- `active_gpu_question = none`
- `next_gpu_candidate = none until X170/X171 scorer-reuse review decides whether H2 validation is worth a new bounded GPU rung`
- `current_execution_lane = X170 H1 response-cloud scorer review on X168 cache`
- `cpu_sidecar = I-A / cross-box boundary maintenance`

## Handoff

- `Platform`: no handoff.
- `Runtime-Server`: no handoff.
- `Docs/materials`: H2 can be described as a live positive-but-bounded black-box candidate surface, not admitted evidence.
