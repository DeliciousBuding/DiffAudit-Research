# DiffAudit Evidence Claim Matrix (Frozen)

> 冻结时间：2026-06-19
> **2026-07-03 更新**: H1/DAAB 行已纳入 Phase G run-dynamics baseline。旧数字（DDPM-800k AUC=0.873, DDIM-750k AUC=0.841）已被统一脚本重新评估的 v2 数字取代；same-trajectory DDPM-800k N=512 已补齐 raw JSON，rerun AUC=0.605488；seed43 750k/800k scout 完成，AUC=0.666687/0.664612。
> 用途：Paper 1 submission 的唯一数据源。所有 Agent 写作必须引用本表，不得使用其他数字。
> 规则：每个方法一行，包含允许的声明（allowed claim）和禁止的声明（blocked claim）。

## Admitted Evidence (5 rows)

| # | Method | Access | Model/Data | AUC | TPR@1%FPR | TPR@0.1%FPR | N (m/nm) | Status |
|---|--------|--------|-----------|:---:|:---------:|:-----------:|:---:|--------|
| 1 | **GSA 3-shadow** | White-box | GPU-scale internal | **0.998** | 0.987 | 0.432 | 1000/1000 | admitted |
| 2 | **DPDM defended** | White-box | Defended model | 0.489 | ~0 | 0.0 | 1000/1000 | admitted |
| 3 | **PIA baseline** | Gray-box | GPU512 internal | 0.841 | 0.059 | 0.012 | 512/512 | admitted |
| 4 | **PIA defended** | Gray-box | Stochastic dropout | 0.828 | 0.053 | 0.010 | 512/512 | admitted |
| 5 | **Recon DDIM** | Black-box | Public-100, step30 | 0.837 | **0.22** | 0.11 | 100/100 | admitted |

### Allowed Claims (Admitted)
- White-box GSA: strong membership signal under favorable access (AUC=0.998, TPR@1%=0.987)
- Gray-box PIA: moderate signal with limited low-FPR recovery (AUC=0.841, TPR@1%=0.059)
- Black-box Recon: admitted but underpowered (N=100); headline uses Wilson 95% CI [0.1500, 0.3107] for TPR@1%FPR
- Recon TPR@0.1%FPR: reported only as uncalibrated empirical tail (100 clean negatives, FPR resolution=1%); NOT a calibrated 0.1% FPR claim

### Blocked Claims (Admitted)
- ❌ "Black-box MIA achieves 0.1% FPR"
- ❌ "Recon demonstrates reliable black-box membership inference at sub-percent FPR"
- ❌ Any statement implying Recon N=100 supports meaningful 0.1% FPR calibration

---

## Spurious Evidence (1 row)

| # | Method | Access | Model/Data | AUC (paper) | AUC (control) | ΔAUC | N | Status |
|---|--------|--------|-----------|:---:|:---:|:---:|:---:|--------|
| 6 | **CLiD** | Black-box | T2I diffusion | **1.000** | **0.586** | 0.414 | 100/100 | spurious |

### Allowed Claims (CLiD)
- Observed collapse: AUC 1.000 under prompt-conditioned → AUC 0.586 under prompt-neutral (same images)
- TPR@1%FPR collapses from 1.00 to 0.02
- Diagnostic interpretation: original signal reflects prompt-image alignment, not membership
- This is a worked example of the "spurious" category in our taxonomy

### Blocked Claims (CLiD)
- ❌ Any bootstrap CI, p-value, or permutation test on ΔAUC (raw score vectors unavailable; simulated scores ≠ evidence)
- ❌ "We statistically prove CLiD signal is spurious with p<0.001"
- ❌ Any numeric claim about the ΔAUC distribution beyond the observed point estimate

---

## Weak Evidence (14 rows)

| # | Method | Access | Model/Data | AUC | CI | N | Status |
|---|--------|--------|-----------|:---:|-----|:---:|--------|
| 7 | **scnet TC64** | Gray-box | CIFAR-10 0.78M | 0.514 | [0.495, 0.531] | K=2000 | weak |
| 8 | **scnet TC128** | Gray-box | CIFAR-10 11.76M | 0.518 | [0.501, 0.536] | K=2000 | weak |
| 9 | **scnet TC192** | Gray-box | CIFAR-10 42.97M | 0.517 | [0.499, 0.535] | K=2000 | weak |
| 10 | **CommonCanvas** | Black-box | CommonCanvas | 0.574 | — | — | weak |
| 11 | **Fashion-MNIST** | Black-box | DDPM | 0.515 | — | — | weak |
| 12 | **MIDST** | Black-box | TabDDPM | 0.530 | — | — | weak |
| 13 | **Beans LoRA delta** | Black-box | LoRA probe | 0.512 | — | 25 | weak |
| 14 | **Beans LoRA loss** | Black-box | LoRA probe | 0.414 | — | 25 | weak |
| 15 | **ReDiffuse DiT** | Black-box | DiT local | ~0.5 | — | — | weak |
| 16 | **Semantic-Aux** | Black-box | Fusion | +0.002 | — | — | weak |
| 17 | **E3 CUDA DDPM 800k PIA** | Gray-box | NVIDIA UNet CIFAR-10 | 0.605 | — | N=5000 | weak (PIA bug: eps_getter=None; SecMI only) |
| 18 | **E3 CUDA DDIM 750k PIA** | Gray-box | NVIDIA UNet CIFAR-10 | 0.605 | — | N=5000 | weak (PIA bug) |
| 19 | **E3 CUDA DDPM SecMI (all ckpts)** | Gray-box | NVIDIA UNet CIFAR-10 | 0.459 | — | N=5000 | weak |
| 23 | **H2 Score-Vector Geometry** | White-box sidecar | CUDA UNet CIFAR-10 | 0.681 | — | N=128/128 | weak/killed |

### Allowed Claims (H2 Score-Vector Sidecar) — new 2026-06-20
- H2 score-vector geometry on the E3-calibrated CUDA DDPM target produced weak, unstable sidecar signal
- AUC decreased from 0.753 (N=64) to 0.681 (N=128), ΔAUC=-0.072
- Low-FPR TPR remained unreliable (0.063 at N=128)
- This line does not support score-vector observables as a robust attack family on CIFAR-10 DDPMs

### Blocked Claims (H2 Score-Vector)
- ❌ "H2 score-vector geometry is a robust second attack family"
- ❌ Any claim that score-vector features provide reliable membership signal

### Allowed Claims (scnet)
- 54× capacity increase (0.78M → 42.97M params) produced no practically or statistically meaningful MIA gain (ΔAUC=0.003, approx 95% CI [-0.0225, 0.0285], approx p=0.82)
- Bootstrap K=2000, 10,000 iterations. All models' CIs cross or barely exceed 0.5
- Interpret as: within our experimental resolution, resource-constrained CIFAR-10 DDPM scaling does not produce transferable gray-box MIA signal

### Blocked Claims (scnet)
- ❌ "We prove that capacity never increases membership leakage"
- ❌ "scnet demonstrates diffusion MIA fundamentally fails"
- ❌ Extrapolation to larger models or different data regimes
- ❌ Any claim that this constitutes evidence about production-scale diffusion models

### Allowed Claims (E3 Calibration)
- E3 confirms DCU weak signal is NOT a SafeConv hardware/operator artifact: NVIDIA CUDA Standard-UNet produces PIA AUC=0.605, SecMI AUC=0.459 (direction-inverted) on the same CIFAR-10 50/50 split — both in the same weak-signal regime as DCU TC192 (AUC=0.517)
- PIA marginally outperforms SecMI on CUDA (ΔAUC≈+0.15), matching the attack ranking observed on DCU — platform-independent validation
- SecMI direction inversion (member scores HIGHER than nonmember, AUC<0.5) is consistent across all three configs and both CUDA models — a platform-independent property, not a SafeConv bug
- TPR@0.1%FPR = 0.000 across all CUDA configs — finite-tail recovery is absent even with N=5000 clean negatives
- Roadmap E3 success standard (AUC≥0.70) was NOT met; E3 delivers its failure value per roadmap §3
- Source: `docs/evidence/e3-calibration-memo-2026-06-20.md`

### Blocked Claims (E3)
- ❌ "NVIDIA CUDA demonstrates meaningful gray-box MIA signal on CIFAR-10 DDPMs" (AUC=0.605 < 0.70, low-FPR recovery is zero)
- ❌ "SafeConv quality degradation explains DCU weak results" (E3 rejects this hypothesis)
- ❌ Any claim that self-trained CIFAR-10 DDPMs are a paper-upgrading path
- ❌ Extrapolation from E3 to production-scale diffusion models

### Allowed Claims (other weak)
- These lines provide supporting evidence that many candidate MIA signals are weak under the tested conditions
- They illustrate the "weak" category in our WSN taxonomy
- They do NOT prove that MIA is impossible in these settings

---

## Non-Portable Evidence (1 row)

| # | Method | Access | Model/Data | AUC | TPR@1%FPR | TPR@0.1%FPR | N | Status |
|---|--------|--------|-----------|:---:|:---------:|:-----------:|:---:|--------|
| 20 | **H2 output-cloud** | Black-box | SD1.5 response cache | **0.962** | 0.334 | 0.117 | 256/256 | candidate |

### Allowed Claims (H2)
- Strong within-family signal: AUC=0.962, TPR@1%=0.334 on low-pass H2 features
- Label-shuffle null: AUC=0.508 (random-level)
- Shared-position order-control: signal survives class-ordered seed-offset check (AUC=0.968)
- Cross-cache transfer: seed176→177 mean AUC=0.960 (not single-seed)
- Fresh SD1.5 img2img packet: best raw AUC=0.646, TPR@1%=0.12 — did NOT pass H2 strong-signal gate (AUC≥0.85, TPR@1%≥20%, TPR@0.1%≠0)
- Classification: non-portable (strong within one response family, fails under img2img portability)

### Blocked Claims (H2)
- ❌ "H2 demonstrates reliable black-box MIA"
- ❌ Any claim that H2 is admitted evidence
- ❌ GPU allocation for same-cache sweeps or cosmetic ablations
- ❌ Using H2 as primary evidence for any positive MIA claim

---

## External High-Performing Support (1 row)

| # | Method | Access | Model/Data | AUC | TPR@1%FPR | TPR@0.1%FPR | N | Status |
|---|--------|--------|-----------|:---:|:---------:|:-----------:|:---:|--------|
| 21 | **MoFIT** | Black-box | Public COCO scores | **0.942** | 0.488 | 0.324 | 500/500 | external-support |

### Allowed Claims (MoFIT)
- Strong external black-box signal exists: AUC=0.942, TPR@1%=0.488 on public COCO score files
- Label-permutation null: AUC=0.501 (random-level) — signal is genuine, not chance
- We acknowledge MoFIT to prevent overclaiming: this paper does NOT assert that all black-box MIA fails
- Status: external high-performing support. NOT admitted internal evidence (checkpoint identity local-path, row IDs not explicit, score-file certification absent, metric computed DiffAudit-side)

### Blocked Claims (MoFIT)
- ❌ "Our audit admits MoFIT as internal evidence"
- ❌ Any claim that MoFIT's blocker status has been resolved
- ❌ GPU allocation (blockers are metadata/row-binding/checkpoint identity, not compute)

---

## Candidate / Pending (4 rows)

| # | Method | Access | Model/Data | AUC | TPR@1%FPR | N | Status |
|---|--------|--------|-----------|:---:|:---------:|:---:|--------|
| 22 | **PIA/TMIA-DM** | Gray-box | GPU512 | — | — | — | candidate / pending admission review |
| 24 | **H1 Activation-Subspace (DAAB) v2** | White-box activation | CUDA UNet CIFAR-10, 6 ckpts | **0.648–0.872** | 0.016–0.227 | 128/128 | candidate-positive / run-sensitive |
| 25 | **H1 DDPM-750k (matched controls)** | White-box activation | Self-trained 750k, seeds 42/43 | **0.648, 0.666687** | 0.094, 0.015625 | 128/128 | step-count / seed replication |
| 26 | **H1 N=512 tail cluster** | White-box activation | DDPM/DDIM CIFAR-10 scaled | **0.560–0.815** | 0.014–0.158 | 512/512 | run-sensitive; same-trajectory raw artifact present |

### Allowed Claims (H1/DAAB v2) — updated 2026-06-25

H1 v2 uses a unified evaluation protocol (same script, N=128/128, 3-shadow LR PCA=6, 4 sites × 3 timesteps, 42 features). All prior numbers (DDPM-800k 0.873, DDIM-750k 0.841) are superseded.

**Phase G unified comparison:**

| Checkpoint | AUC | TPR@1% | Shuffle AUC |
|------------|-----|--------|-------------|
| DDPM-750k | 0.648 | 0.094 | 0.484 |
| DDPM-750k seed43 | 0.666687 | 0.015625 | 0.453552 |
| DDPM-800k same-trajectory | 0.717 | 0.039 | 0.507 |
| DDPM-800k seed43 | 0.664612 | 0.015625 | 0.487793 |
| DDPM-800k independent | 0.872 | 0.227 | 0.492 |
| DDIM-750k | 0.856 | 0.109 | 0.481 |

- Internal UNet activations carry detectable, above-chance membership signal across evaluated checkpoints. Signal strength is training-trajectory dependent (0.648–0.872)
- seed43 at 750k stays near the seed42 750k AUC regime (0.666687 vs 0.648) but has weak low-FPR recovery (TPR@1%=0.015625), so it supports the moderate 750k regime without creating a strong-run cluster
- seed43 at 800k remains moderate (AUC=0.664612, TPR@1%=0.015625) and does not reproduce the seed42 same-trajectory amplification; N=512 was not run because the N=128 AUC did not exceed 0.70
- DDIM-750k substantially exceeds step-matched DDPM-750k (ΔAUC=+0.208), confirming DDIM advantage is not a step-count artifact. The original DDPM-800k vs DDIM-750k comparison was conservative with respect to DDIM
- Same-trajectory DDPM-750k→800k increases AUC only from 0.648 to 0.717 (Δ=+0.069). The independent DDPM-800k gap (0.872−0.648=+0.224) is therefore dominated by run identity rather than pure step count
- Signal passes label-shuffle control (0.453552–0.507) and does not depend on a single UNet site
- H1 provides a mechanistically distinct white-box observable: non-gradient, non-loss, activation-based
- **Fine temporal grid (8 timesteps)**: DDPM-750k is moderately concentrated (max |delta|=0.097), independent DDPM-800k is distributed (0.029), seed42 same-trajectory DDPM-800k is more concentrated (0.152), seed43 DDPM-800k changes sign with max |delta|=0.1169 and knockout mostly increasing AUC, and DDIM-750k is strongly concentrated (0.221). Temporal geometry varies with training procedure, training stage, and run identity
- **AUC-vs-step**: H1 signal stable 0.65–0.71 from 100k–750k within the DDPM-750k trajectory; the independent DDPM-800k high AUC is not reproduced by same-trajectory continuation
- N=512 tail: DDPM-750k collapses to AUC=0.560, independent DDPM-800k retains AUC=0.815, DDIM-750k retains AUC=0.812. Same-trajectory DDPM-800k N=512 now has raw JSON and remains weak-to-moderate at AUC=0.605488, TPR@1%=0.025391, TPR@0.1%=0.0
- H4 closed: no compact post-training edit target exists

### Blocked Claims (H1/DAAB v2)
- ❌ "H1 is admitted membership evidence"
- ❌ "AUC>0.8 is universal for DAAB" — DDPM-750k AUC=0.648 is below 0.8
- ❌ "DDPM always produces temporally distributed signal" — DDPM-750k is moderately concentrated
- ❌ "Late-stage amplification explains independent DDPM-800k" — same-trajectory amplification is modest
- ❌ "same-trajectory late-stage amplification is stable across seeds" — seed43 750k->800k does not amplify
- ❌ "low-FPR fragility proven across all configurations" — strong N=512 runs exist even though seed42/seed43 750k and same-trajectory 800k are low-FPR weak
- ❌ "Activation-subspace attack achieves reliable low-FPR MIA"
- ❌ "Significant channels are a compact removable leakage source"
- ❌ Any TPR@0.1%FPR claim
- ❌ "H1 is as strong as GSA"

---

## Statistical Boundary Rules

| Rule | Value |
|------|-------|
| Primary low-FPR metric | TPR@1%FPR |
| TPR@0.1%FPR | Only reported for lines with N≥1,000 clean negatives |
| Proportions | Wilson 95% CI, not normal approximation |
| AUC comparison | Bootstrap (10,000 iterations); DeLong only if normality holds |
| Multiple testing | Holm-Bonferroni across all reported lines (appendix) |
| CLiD ΔAUC | Observed point estimate only. No simulated/bootstrap inference |
| Recon 0.1% FPR | Not a calibrated claim. FPR resolution = 1/100 = 1% |
| Clean N for 1% FPR (rule-of-3) | ≥300 |
| Clean N for 0.1% FPR (rule-of-3) | ≥3,000 |
| Clean N for 0.01% FPR (rule-of-3) | ≥30,000 |

## Core Narrative Constraints

| ALLOWED | BLOCKED |
|---------|---------|
| "Diffusion MIA signals are heterogeneous and require diagnostic admission" | "Diffusion MIA fails" / "MIA is impossible" |
| "Strong signals exist (GSA, MoFIT); our contribution is diagnosing admissibility" | "All black-box MIA is weak" |
| "We propose WSN taxonomy + 10-point diagnostic protocol" | "We present the first comprehensive MIA evaluation" |
| "Bounded measurement / evidence-contracted audit" | "Definitive benchmark" / "Complete survey" |

## Evidence Sources

| Source | Lines |
|--------|-------|
| `Research/docs/evidence/admitted-results-summary.md` | #1–5 |
| `Research/docs/paper1/evidence-matrix.md` | All |
| `Research/docs/paper1/statistical-audit.md` | Statistical rules |
| `Research/docs/evidence/e3-calibration-memo-2026-06-20.md` | #17–19 |
| `Docs/internal/ccf-a-research-roadmap-2026-06-06.md` | E1/E2/E3 status (internal — not in public repository) |
| `Research/docs/evidence/clid-prompt-perturbation.md` | #6 |
| `Research/docs/evidence/h2-output-cloud-geometry-20260525.md` | #20 |
| `Research/docs/evidence/h1-activation-scout-memo-2026-06-20.md` | #24 |
| `Research/docs/evidence/h1-mechanistic-analysis-2026-06-20.md` | #24 |
| `Research/docs/evidence/h1-fine-temporal-grid-2026-06-20.md` | #24 (DDPM vs DDIM temporal distribution) |
| `Research/docs/evidence/h2-score-vector-sidecar-memo-2026-06-20.md` | #23 |
| `Docs/internal/e2-n50-freeze-preflight-2026-06-06/` | MoFIT preflight (internal — not in public repository) |
