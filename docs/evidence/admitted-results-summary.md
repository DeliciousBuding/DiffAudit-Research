# Verified Results Summary

> This summary covers verified results only. Candidate and exploratory
> results are excluded until explicitly promoted.
> Each row comes from `unified-attack-defense-table.json` and retains
> the evidence level, cost, and limitation language tied to the reported metrics.

| Track | Method | Attack | Defense | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | Evidence Level | Quality / Cost | Evidence Location | Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Black-box | Recon risk proof | `recon DDIM public-100 step30` | `none` | 0.837 | 0.74 | 0.22 | 0.11 | `runtime-mainline` | `100 public samples per split; DDIM step30; runtime mainline plus unified artifact threshold replay; cuda runtime` | `Research/workspaces/implementation/artifacts/unified-attack-defense-table.json` (black-box row), [recon-product-validation-result.md](recon-product-validation-result.md) | Evidence holds only under `fine-tuned / controlled / public-subset / proxy-shadow-member` semantics. Demonstrates membership leakage risk under minimal permissions. Current black-box main evidence uses `upstream_threshold_reimplementation` for coherent four-metric reporting; `TPR@0.1%FPR` is a zero-false-positive empirical tail on 100 target nonmembers. |
| Gray-box | PIA baseline | `PIA GPU512 baseline` | `none` | 0.841339 | 0.786133 | 0.058594 | 0.011719 | `runtime-mainline` | `attack_num=30; interval=10; batch_size=8; 512 samples per split; single GPU serial; adaptive repeats=3; wall-clock=212.993833s` | `Research/workspaces/implementation/artifacts/unified-attack-defense-table.json` (gray-box baseline row) | Workspace-verified local DDPM/CIFAR10 baseline with bounded repeated-query adaptive review (`adaptive repeats=3`). Read as `epsilon-trajectory consistency` baseline exposure. `TPR@0.1%FPR` is a finite empirical strict-tail point over 512 target nonmembers, not calibrated sub-percent FPR. Still blocked by checkpoint/source provenance from paper-aligned release. |
| Gray-box | PIA defended | `PIA GPU512 baseline` | `stochastic-dropout all-steps prototype` | 0.828075 | 0.767578 | 0.052734 | 0.009766 | `runtime-mainline` | `attack_num=30; interval=10; batch_size=8; 512 samples per split; single GPU serial; adaptive repeats=3; wall-clock=223.128438s` | `Research/workspaces/implementation/artifacts/unified-attack-defense-table.json` (gray-box defended row) | Workspace-verified local DDPM/CIFAR10 defended comparator with bounded repeated-query adaptive review (`adaptive repeats=3`). Shows inference-time randomization weakening `epsilon-trajectory consistency`, but remains provisional. `TPR@0.1%FPR` is a finite empirical strict-tail point over 512 target nonmembers, not calibrated sub-percent FPR. Blocked by checkpoint/source provenance. Not validated privacy protection. |
| White-box | GSA attack | `GSA 1k-3shadow` | `none` | 0.998192 | 0.9895 | 0.987 | 0.432 | `runtime-mainline` | `target_eval_size=2000; shadow_train_size=4200; 3 shadows; cuda` | `Research/workspaces/implementation/artifacts/unified-attack-defense-table.json` (white-box attack row) | Admitted white-box attack line. Treat as risk upper bound, not final paper-level benchmark. |
| White-box | DPDM defended | `GSA 1k-3shadow` | `DPDM strong-v3 full-scale` | 0.488783 | 0.4985 | 0.009 | 0.0 | `runtime-mainline` | `target_eval_size=2000; shadow_train_size=6000; classifier=logistic-regression-1d` | `Research/workspaces/implementation/artifacts/unified-attack-defense-table.json` (white-box defended row) | Admitted white-box defense comparator. Bridge frozen; not a finished benchmark. Comparison informs governance decisions. |

Each row records only the admitted primary value and can be cited directly.
Gray-box PIA results must be reported with all four metrics (`AUC / ASR / TPR@1%FPR / TPR@0.1%FPR`).
For the admitted PIA rows, `TPR@0.1%FPR` is a finite empirical strict-tail
point over 512 target nonmembers, not a calibrated continuous sub-percent FPR
claim.
This table also includes `evidence_level` and `quality / cost` so downstream
consumers do not need to infer execution scale from headline metrics alone.
For more detailed fields, see `quality_cost`, `provenance_status`, and
`boundary` in `unified-attack-defense-table.json`. Runtime and Platform
consume only verified data.
