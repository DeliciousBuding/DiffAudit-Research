# Gray-Box Paper-Candidate Reentry Review

Date: 2026-05-12

## Verdict

`hold`; no GPU task is released.

The post-I-B successor slot asked whether any archived paper-backed gray-box
candidate should reenter the active lane after ReDiffuse, tri-score, SecMI,
diagonal-Fisher, cross-box successor scoping, and I-B defense-aware reopen
scouting all closed as candidate-only, supporting-only, negative, or hold.

The answer is no under the current evidence. SIMA, Noise-as-Probe, MoFit, and
Structural Memorization are useful archived candidates, but none currently
passes a low-FPR / adaptive / reproducible-contract gate that would justify
GPU or admitted-evidence work.

Machine-readable review:
`workspaces/gray-box/artifacts/graybox-paper-candidate-reentry-20260512.json`.

## Hypothesis And Falsifier

Hypothesis: at least one archived gray-box paper candidate has enough existing
artifact evidence, distinctness, and protocol clarity to become the next
CPU-active or GPU-candidate lane without repeating a closed same-family route.

Falsifier: if every candidate is canary-only, negative, low-FPR unstable,
asset/protocol blocked, or already covered by a closed fusion/support route,
then keep the lane on hold and do not spend GPU.

The falsifier is triggered.

## Candidate Review

| Candidate | Evidence read | Current read | Decision |
| --- | --- | --- | --- |
| SIMA | `sima-cifar10-runtime-rescan-20260416-cpu-32-r2`, `sima-packet-score-export-pia-full-overlap-20260421-r1`, `crossbox-pairboard-pia-sima-full-overlap-20260421-r1` | Standalone CPU scan is weak (`AUC = 0.584961`, `TPR@0.1%FPR = 0.03125`). PIA+SIMA pairboard improves AUC in repeated holdout, but strict-tail wins are unstable. | Hold. Do not run a larger SIMA or SIMA+PIA packet without a new low-FPR-primary scorer contract. |
| Noise-as-Probe | `noise-as-probe-cfg-microprobe-*`, `noise-as-probe-hidden-guidance-jitter-*` | Fixed guidance microprobes have promising tiny-threshold reads (`accuracy = 0.875` at 8/8), but hidden guidance jitter collapses to `accuracy = 0.5` and no low-FPR denominator exists. | Hold. Do not GPU-scale until a protocol controls guidance leakage and defines strict-tail metrics. |
| MoFit | `mofit-sd15-celeba-reviewrung-20260416-cpu-r2`, `mofit-sd15-celeba-microrung-20260416-cpu-r2` | Interface canary only (`2` members / `2` nonmembers); no AUC, ASR, low-FPR, or adaptive contract. | Hold / needs protocol. |
| Structural Memorization | `structural-memorization-smoke-20260415-r1` | Negative-but-useful local approximation (`AUC = 0.375`, `ASR = 0.53125`, `TPR@1%FPR = 0.0625`). | Closed for now; do not rerun without a new structural observable. |

## Release Gate

No candidate satisfies all required conditions:

- clear member/nonmember identity and target asset identity,
- reproducible command or code path,
- metrics including AUC, ASR, TPR@1%FPR, and TPR@0.1%FPR where applicable,
- low-FPR as a primary gate rather than an afterthought,
- adaptive or leakage-control boundary,
- a distinct observable not already covered by ReDiffuse, tri-score,
  cross-box score sharing, or diagonal-Fisher.

## Next Action

The next active CPU sidecar should be `paper-backed new-observable intake
scout`: look for a genuinely different observable or a ready response-contract
asset package before scheduling any model run.

Do not reopen SIMA, Noise-as-Probe, MoFit, or Structural Memorization from
their current artifacts alone.

## GPU State

`active_gpu_question = none`; `next_gpu_candidate = none`.
