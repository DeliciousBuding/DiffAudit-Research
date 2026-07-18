# Paper 1 — Markdown Draft (H1 Section Update)

> **QUARANTINED historical narrative (2026-07-10+). Not paper-admissible.**
> Invalid Phase G membership GT / resubstitution scoring. Corrected matrix closed **Route C** (2026-07-18): audit-failure / non-reproduction only.
> Historical AUC 0.84–0.88 / “real, replicated membership signal” language is **not** paper-admissible. Do not treat as submission draft.
> SSOT: `docs/paper1/frozen-claim-matrix.md` + `ROADMAP.md`.

---

## Activation Fingerprints Reveal Distributed Activation-Amplitude Bias

### 1. Motivation

The admitted white-box rows are gradient-based (GSA, DPDM bridge). GSA reaches AUC 0.998 and TPR@1%FPR 0.987, close to saturation for the CIFAR-10 target. A natural measurement question is whether internal UNet activations — neither gradient nor loss nor response-contract — carry a membership signal that could serve as a second independent white-body family.

### 2. Method

We register forward hooks at four UNet sites on the E3-calibrated CUDA DDPM 800k target (UNet ch=128, ch_mult=[1,2,2,2], num_res_blocks=2): late_down, mid_0, mid_1, and early_up. At each site and timestep $t \in \{100, 400, 700\}$, we extract per-channel statistics: mean absolute activation μ_abs, channel variance σ², and activation sparsity. Per-site scalar aggregates are combined with PCA-6 projection of stacked per-channel vectors. Three shadow calibrations train a balanced logistic regression.

### 3. Replicated Aggregate Signal

| Checkpoint | N | AUC | TPR@1%FPR | Shuffle AUC |
|------------|---|:---:|:---------:|:-----------:|
| DDPM 800k | 64 | 0.874 | 0.484 | 0.410 |
| DDPM 800k | 128 | 0.873 | 0.055 | 0.486 |
| DDIM 750k | 128 | 0.841 | 0.078 | 0.504 |

AUC is stable (ΔAUC = +0.001 from N=64 to N=128) and replicates across checkpoints (ΔAUC = -0.032 from DDPM to DDIM). Label-shuffle controls return chance-level AUC. Per-site ablation removes each hook site in turn; all ablated AUCs remain within [0.867, 0.879], ruling out single-site artifacts. H1 was historically described as carrying an aggregate membership signal; that packet is **quarantined** (invalid GT / resubstitution) and is not paper-admissible after Route C.

### 4. Feature Decomposition

We decompose the trained logistic regression coefficients by feature type, UNet site, and timestep:

| Dimension | Dominant contributor | Share |
|-----------|-------------------|:-----:|
| Statistic type | μ_abs (mean absolute activation) | 77.9% |
| | σ² (channel variance) | 21.3% |
| | Sparsity | 0.9% |
| UNet site | early_up (first upsampling ResBlock) | 33.7% |
| | late_down (deepest ResBlock) | 32.1% |
| | mid_0, mid_1 (bottleneck) | 34.2% combined |
| Timestep | t=400 (mid-denoising) | 36.2% |
| | t=100, t=700 | 32.2%, 31.6% |

The signal is dominated by activation magnitude, distributed across pathway extremes rather than concentrated in the bottleneck, and balanced across the denoising trajectory with a mild peak at t=400.

### 5. Correlational Localization

Only ~4% of individual channels show statistically significant member/nonmember differences (p<0.01, t-test). All significant channels exhibit member > nonmember activation (Δ > 0). The most individually significant channels are concentrated at early_up_t100 (24/512 channels, 4.7%) and mid_1_t100 (16/512, 3.1%).

This pattern might suggest a sparse leakage interpretation: a few channels carry the signal. However, statistical correlation does not imply causal importance. We test this directly.

### 6. Channel Intervention Falsifies Sparse-Causal Explanation

We perform targeted channel knockout experiments: zeroing specific channels during the forward pass and re-evaluating H1 with both retrained and frozen scorers.

**Matched-count comparison (both delete exactly 10 channels):**

| Condition | AUC | Δ vs Baseline |
|-----------|:---:|:---:|
| Baseline (no KO) | 0.884 | — |
| Targeted top-10 (t-test significant) | 0.876 | +0.008 |
| Random 10 (mean of 10 seeds, σ=0.015) | 0.866 | +0.018 |

The targeted deletion effect falls within one standard deviation of the random deletion distribution. The top-10 most membership-correlated channels are not causal bottlenecks.

**Matched-percent comparison (both delete ~40 channels, 4% of total):**

| Condition | AUC | Δ vs Baseline |
|-----------|:---:|:---:|
| Baseline (no KO) | 0.906 | — |
| Targeted top-4% (40 channels) | 0.899 | +0.008 |
| Random 4% (5 seeds, σ=0.015) | 0.857 | +0.049 |

Targeted deletion of the top-4% most significant channels causes **significantly less degradation** than random deletion of the same number of channels (targeted Δ = +0.008 vs random mean Δ = +0.049, approximately 2.8σ apart). The most membership-correlated channels are systematically **less** causally important than average channels.

**Frozen-scorer analysis:**

Applying the baseline LR weights to knockout features reveals that the original scorer depends on specific channel patterns: random 4% knockout drops frozen-scorer AUC by 0.138. However, retraining the scorer recovers most of this loss, indicating that the H1 signal family is redundant — alternative channel subsets can support similar aggregate separability.

### 7. Interpretation: Distributed Activation-Amplitude Bias

These results rule out a sparse-channel causal interpretation of H1. The signal is:

- **Real**: AUC=0.84-0.88 across two checkpoints, shuffle controls pass.
- **Replicated**: Signal generalizes from DDPM 800k to DDIM 750k.
- **Characterized**: Dominated by activation magnitude, distributed across sites and timesteps.
- **Non-localizable**: Membership-correlated channels are not causal bottlenecks; targeted deletion is no more effective — and at 4% scale, systematically less effective — than random deletion.
- **Redundant**: Retrained scorers adapt to channel deletion; the signal family survives sparse knockout.
- **Forensically fragile**: TPR@1%FPR collapses from 0.484 (N=64) to 0.055 (N=128). Low-FPR tail does not survive scale-up.

We term this pattern **Distributed Activation-Amplitude Bias (DAAB)**: a replicated activation-level membership trace dominated by activation magnitudes, distributed across UNet channel patterns rather than localized to individually significant channels, and therefore not removable by sparse targeted knockout.

### 8. Admission Consequence

H1 separates four levels that most MIA papers conflate:

| Level | Question | H1 Answer |
|-------|----------|-----------|
| Signal existence | Is there a membership signal? | Yes (AUC=0.84-0.88) |
| Mechanistic characterization | What carries the signal? | Activation magnitude, distributed |
| Causal localization | Can the signal be edited? | No — significant channels are not causal bottlenecks |
| Forensic admission | Is the signal low-FPR reliable? | No — TPR@1% collapses under scale-up |

H1 is therefore **candidate-positive / low-FPR-fragile**, not admitted forensic evidence. It enters the claim register as a diagnostic boundary case demonstrating that real, replicated, mechanistically characterized signals can still fail causal localization and forensic admission.

### 9. H4 Closure

We do not release H4 (post-training subspace editing defense). The channel intervention experiments show that no compact causal edit target exists: even after identifying membership-correlated channels, targeted knockout does not suppress H1 more than random deletion. The activation signal is not locally editable by sparse channel removal. Blind channel pruning would risk utility degradation without a localized editing target.

**H4 status**: Closed. Not released. Sparse channel editing is not supported.

### 10. Core Scientific Insight

> *"H1 separates correlation, mechanism, causality, and admissibility: activation fingerprints are real and replicated, but the channels most correlated with membership are not causal bottlenecks, and the resulting signal remains fragile at low-FPR operating points."*

Or more compactly:

> *"Real signal does not imply causal localization; causal non-localization does not imply forensic admission."*

This is the paper's central scientific contribution, instantiated through H1 as the most nuanced evidence-state transition in the claim matrix.
