# X-173 H2 Post-Validation Boundary Review

Date: 2026-04-29
Status: `positive boundary / GPU hold`

## Question

After `X-172` passed a non-overlap `128 / 128` H2 validation rung, should the Research mainline immediately spend another GPU rung on `256 / 256`, promote H2, or first freeze stricter comparator/adaptive/query-budget gates?

## Inputs

- X168 scout:
  - `workspaces/implementation/2026-04-29-x168-blackbox-h2-strength-response-gpu-scout.md`
- X171 frequency boundary:
  - `workspaces/implementation/2026-04-29-x171-h3-frequency-filter-cache-ablation.md`
- X172 validation:
  - `workspaces/implementation/2026-04-29-x172-h2-strength-response-validation.md`
- X172 run:
  - `workspaces/black-box/runs/x172-h2-strength-response-validation-20260429-r1/summary.json`

## Review

H2 now has real candidate evidence:

- `X-168` `64 / 64` raw H2 logistic:
  - `AUC = 0.928955`
  - `ASR = 0.859375`
  - `TPR@1%FPR = 0.218750`
  - `TPR@0.1%FPR = 0.218750`
- `X-171` frequency ablation:
  - `lowpass_0_5` preserved H2 low-FPR tail
  - high-pass views collapsed, so the signal is not high-frequency-only
- `X-172` non-overlap `128 / 128` raw H2 logistic:
  - `AUC = 0.887756`
  - `ASR = 0.808594`
  - `TPR@1%FPR = 0.093750`
  - `TPR@0.1%FPR = 0.062500`
- `X-172` `lowpass_0_5` secondary:
  - `AUC = 0.879333`
  - `ASR = 0.796875`
  - `TPR@1%FPR = 0.195312`
  - `TPR@0.1%FPR = 0.078125`

This is enough to change H2's internal status:

- before: `positive but bounded scout`
- now: `validated positive-but-bounded candidate surface`

It is not enough to promote H2:

- no same-packet `recon` comparator is frozen
- no `256 / 256` independent rung exists
- no fixed query-budget/adaptive repeated-query stress test exists
- no calibrated decision rule is frozen across scout and validation
- evidence remains `DDPM/CIFAR10` only
- no Runtime runner or Platform consumer contract exists

## Candidate Decisions

| Candidate | Decision | Reason |
| --- | --- | --- |
| Promote H2 to admitted black-box evidence | reject | The validation is positive but still lacks comparator, 256/256, adaptive budget, and deployment contract. |
| Immediately run `256 / 256` GPU validation | hold | Positive evidence exists, but a blind scale-up risks spending GPU before comparator/adaptive gates are frozen. |
| Treat `lowpass_0_5` as the new primary scorer | reject for now | It improves low-FPR on X172 but slightly weakens AUC/ASR and was introduced as a boundary check; primary remains raw H2 until a scorer-selection gate is frozen. |
| Freeze H2 comparator/adaptive validation contract | select | This is the cheapest next step and defines what a future larger GPU rung must prove. |
| Platform/Runtime handoff | reject | No consumer schema should change from candidate evidence. |

## Verdict

`positive boundary / GPU hold`

H2 is now a validated positive-but-bounded black-box candidate surface, not admitted evidence. The next live task should be CPU-first `X-174 H2 comparator/adaptive validation contract freeze`. A larger GPU rung is not released until that contract defines:

- same-packet comparator target
- raw-vs-lowpass scorer selection rule
- query-budget/adaptive repeated-query stress rule
- validation packet identity
- kill gate for `256 / 256`

## Control State

- `active_gpu_question = none`
- `next_gpu_candidate = none until X174 freezes an H2 comparator/adaptive validation contract`
- `current_execution_lane = X174 H2 comparator/adaptive validation contract freeze`
- `cpu_sidecar = I-A / cross-box boundary maintenance`

## Handoff

- `Platform`: no handoff.
- `Runtime-Server`: no handoff.
- `Docs/materials`: note-level only. H2 can be mentioned as a validated candidate surface but not as admitted black-box evidence, not as `recon` replacement, and not as conditional diffusion coverage.
