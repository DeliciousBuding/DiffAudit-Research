# A Claim-Admission Protocol for Diffusion Membership-Inference Scores

> TMLR Submission Draft — 2026-06-20
> Markdown version for scientific discussion and review.
> Full LaTeX source: `papers/diffaudit-evidence-paper/main.tex`
> Compiled PDF: `papers/diffaudit-evidence-paper/paper.pdf`

---

## Abstract

*(Full scientific abstract — see LaTeX source for exact wording)*

Diffusion MIA scores are commonly reported as scalar attack metrics, yet the same score can correspond to different evidence states: a high-AUC signal may be real but forensically fragile, spurious under covariate controls, non-portable across surfaces, or admissible only within a bounded scope. **Membership inference is not a score-ranking problem; it is an evidence-admission problem.**

We formalize this as a claim-admission protocol: a fixed-order gate rule over six surfaces (target identity, split semantics, score/response coverage, metric provenance, consumer boundary, surface delta) assigns each proposed audit claim to reportable, candidate, support-only, watch, or negative states, applied to 24 boundary cases spanning white-box, gray-box, and black-box access.

**Centerpiece (H1/DAAB)**: Internal U-Net activations on CIFAR-10 DDPMs carry replicated membership signal (AUC 0.873 DDPM 800k, 0.841 DDIM 750k). The signal passes shuffle and ablation controls and is dominated by activation magnitude (mu_abs: 78%, variance: 21%; either alone captures 95-97% of combined AUC). However:
- **Channel knockout**: The most membership-correlated channels (~4% significant at p<0.01, concentrated in early_up) are not causal bottlenecks — targeted deletion produces no more degradation than random deletion (matched-count: Δ=+0.008 vs +0.018, σ=0.015; matched-percent: Δ=+0.008 vs +0.004, 30 seeds, d=0.21, p=0.26, 95% CI [-0.003, +0.011])
- **Full-site knockout**: Zeroing all channels at each site reveals a causal gradient: late_down (Δ=+0.374) >> mid_0 (+0.249) > mid_1 (+0.108) > early_up (+0.077) — identical across both checkpoints
- **Spatiotemporal grid** (4 sites × 3 timesteps × 2 checkpoints): The causal locus is sharply concentrated — mid_0@t=100 and late_down@t=100 carry nearly all membership signal; t=400 and t=700 are causally negligible across all sites
- **Key dissociation**: The most statistically visible channels (early_up, 4.7% significant) are at the LEAST causally important site; the causal core (mid_0 + late_down at t=100) harbors fewer individually significant channels

We term this **Distributed Activation-Amplitude Bias (DAAB)**: a real, replicated, mechanistically characterized signal whose aggregate is distributed across channels and statistic types, whose causal core concentrates in bottleneck + deepest layers at early denoising, and whose forensic tail remains fragile (TPR@1% collapses 0.484→0.055 under scale-up). H1 thus separates statistical visibility from causal necessity — a separation that scalar metrics conceal.

**Additional cases**: CLiD (spurious, AUC 1.000→0.586 under prompt-neutral control; ΔAUC point estimate only), scnet (scale-null, 54× capacity ΔAUC=0.003), H2 output-cloud (non-portable, AUC 0.962 within-family, fails img2img), MoFIT (external support, AUC 0.942, missing row binding).

**Core insight**: *"A diffusion MIA score is not evidence until its claim boundary is admitted."*

**Gold sentences**:
- *"Membership inference is not a score-ranking problem; it is an evidence-admission problem."*
- *"Real signal does not imply causal localization; causal non-localization does not imply forensic admission."*
- *"Membership-correlated channels are not membership-causal channels."*

## Paper Structure

1. **Introduction** — claim-admission protocol motivation, CopyMark differentiation
2. **Related Work** — MIA evidence, security measurement, diffusion memorization
3. **Audit Surfaces** — 6-gate evidence contract
4. **Evidence Contract** — formal gate definitions with consumer templates
5. **Measurement Protocol** — 5-state decision rule, gate-assignment procedure
6. **Worked Examples** — 5 admitted rows (GSA, DPDM, PIA baseline/defended, Recon)
7. **H2 Output-Cloud** — candidate boundary case (AUC 0.962, fails portability)
8. **H1 Activation Fingerprints → DAAB** — complete mechanistic investigation
9. **Negative/Support Evidence** — MoFIT, route closures, promotion error taxonomy
10. **Discussion** — actionable checklist, limitations, external validity
11. **Conclusion** — gold sentence summary

## H1/DAAB Evidence Summary

| Level | Finding | Key number | Cross-ckpt? |
|-------|---------|------------|:---:|
| 1. Existence | Real signal | AUC=0.84-0.88 | ✅ |
| 2. Replication | Cross-checkpoint | DDPM 800k + DDIM 750k | ✅ |
| 3. Characterization | mu_abs dominant, mu/var redundant | mu=78%, var=21%; either→95-97% | — |
| 4. Feature redundancy | mu-only AUC=0.800, var-only=0.818, combined=0.839 | sparsity=0.500 (chance) | — |
| 5. Channel non-localizability | Top channels not causal | matched-count: Δ within noise, matched-percent: Δ≈0, 30 seeds | — |
| 6. Site causal gradient | late_down >> mid_0 > mid_1 > early_up | late_down zero→AUC=0.500 | ✅ |
| 7. Spatiotemporal locus | mid_0+late_down@t=100 carry all signal | t=400,700 negligible | ✅ |
| 8. Correlation-causation dissociation | early_up: 4.7% sig, least causal | mid_0+late_down@t=100: causal core | ✅ |
| 9. Classifier independence | LR/SVM consistent | AUC~0.84-0.85 | — |
| 10. Forensic fragility | TPR@1% collapses | 0.484→0.055 (N=64→128) | — |
| 11. H4 closure | No compact edit target | Channel+site knockout evidence | — |

## Key Tables

1. **Admission map** (Fig 1): signal strength × claim-boundary validity
2. **Full-site knockout gradient** (Table): late_down >> mid_0 > mid_1 > early_up
3. **Spatiotemporal causal grid** (Table): 4 sites × 3 timesteps × 2 checkpoints
4. **Allowed/blocked claims** (Table): 6 key boundary cases
5. **Admission checklist** (Table): 6-gate operational protocol

## Review History

| Round | Type | Key fixes |
|-------|------|-----------|
| 1 | ChatGPT deep scientific review | Abstract rewrite, CopyMark differentiation, DAAB naming |
| 2 | 30-seed statistical correction | 5-seed artifact found and corrected |
| 3 | Workflow adversarial review v1 | Same-team→frozen gate labels, CLiD caveat, limitations |
| 4 | Feature ablation | mu/var redundancy, sparsity=chance |
| 5 | Full-site + per-timestep knockout | Causal gradient discovery, spatiotemporal grid |
| 6 | Workflow v2 (Accept/Solid) | TOST caveat, 95% CI, external validity limitations |

## Repository

- **Git**: `DeliciousBuding/DiffAudit-Research`, branch `paper/evidence-contracted-workspace`
- **Scripts**: `scripts/h1_activation_scout.py`, `scripts/h2_score_vector_sidecar.py`, `scripts/h1_matched_knockout.py`
- **Evidence**: `docs/evidence/h1-*.md`, `docs/evidence/h2-*.md`
- **Paper**: `papers/diffaudit-evidence-paper/main.tex`, `paper.pdf`
- **Claim matrix**: `docs/paper1/frozen_claim_matrix.md` (24 rows)
