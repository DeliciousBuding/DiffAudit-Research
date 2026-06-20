# A Claim-Admission Protocol for Diffusion Membership-Inference Scores

> TMLR Submission Draft — 2026-06-20
> Markdown version for scientific discussion and review.

---

## Abstract

Diffusion membership-inference (MIA) scores are commonly reported as scalar attack metrics, yet the same score can correspond to different evidence states: a high-AUC signal may be real but forensically fragile, spurious under covariate controls, non-portable across surfaces, or admissible only within a bounded scope. **Membership inference is not a score-ranking problem; it is an evidence-admission problem.**

We formalize this as a claim-admission protocol: a fixed-order gate rule over six surfaces assigns each proposed audit claim to reportable, candidate, support-only, watch, or negative states, applied to 24 boundary cases.

**Centerpiece (H1/DAAB)**: Internal U-Net activations carry replicated membership signal (AUC 0.873 DDPM, 0.841 DDIM). Signal passes shuffle/ablation controls. Channel knockout reveals the most membership-correlated channels are not causal bottlenecks — targeted deletion produces no more degradation than random deletion. Full-site knockout reveals a causal gradient: late_down zeroing collapses AUC to chance, while early_up is dispensable. Per-timestep analysis shows the signal concentrates in early denoising (t=100). We term this **Distributed Activation-Amplitude Bias (DAAB)**: real, replicated, mechanistically characterized, yet non-localizable at the channel level and forensically fragile (TPR@1% collapses 0.484→0.055).

Additional cases: CLiD (spurious, AUC 1.000→0.586), scnet (scale-null, 54× capacity ΔAUC=0.003), H2 output-cloud (non-portable), MoFIT (external support).

**Core insight**: *A diffusion MIA score is not evidence until its claim boundary is admitted.*

## Key Scientific Contributions

1. **Evidence-admission reframing**: MIA is an evidence-state problem, not a score-ranking problem
2. **H1/DAAB**: Six-level mechanistic investigation showing real signal ≠ causal localization ≠ forensic admission
3. **Causal gradient discovery**: Membership signal concentrates in deepest UNet layers (late_down) at earliest denoising (t=100)
4. **Correlation-causation separation**: Most statistically visible channels (early_up) are least causally important
5. **Operational protocol**: Six-gate checklist + allowed/blocked claim language for prospective use

## H1 Evidence Summary

| Level | Finding | Key number |
|-------|---------|------------|
| Existence | Real signal | AUC=0.84-0.88 |
| Replication | Cross-checkpoint | DDPM 800k + DDIM 750k |
| Characterization | Activation magnitude dominant | mu_abs=78%, var=21% |
| Feature redundancy | mu and var are redundant carriers | Either alone → 95-97% of combined AUC |
| Channel non-localizability | Top channels not causal bottlenecks | Targeted Δ=+0.008, Random Δ=+0.004 (30 seeds, p=0.26) |
| Site causal gradient | late_down >> mid_0 > mid_1 > early_up | late_down zero → AUC=0.500 (chance) |
| Temporal causal gradient | t=100 >> t=400 > t=700 | late_down@t=100 Δ=+0.124 |
| Classifier independence | Signal not LR-specific | LR/SVM consistent AUC~0.84-0.85 |
| Forensic fragility | TPR@1% collapses under scale-up | 0.484→0.055 (N=64→128) |
| H4 closure | No compact edit target | — |

## Gold Sentences

> *"Membership inference is not a score-ranking problem; it is an evidence-admission problem."*

> *"A diffusion MIA score is not evidence until its claim boundary is admitted."*

> *"Real signal does not imply causal localization; causal non-localization does not imply forensic admission."*

> *"Membership-correlated channels are not membership-causal channels."*
