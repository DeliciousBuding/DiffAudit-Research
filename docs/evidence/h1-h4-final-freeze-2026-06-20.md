# H1/H4 Final Freeze — 2026-06-20

> ChatGPT final verdict: **FREEZE.** Evidence complete. No more GPU.

## H1: Distributed Activation-Amplitude Bias (DAAB)

### Six-Level Evidence Chain

| Level | Finding | Evidence |
|-------|---------|----------|
| 1. Existence | Real signal | AUC=0.873 (DDPM 800k), AUC=0.841 (DDIM 750k) |
| 2. Replication | Cross-checkpoint | Signal generalizes across training runs |
| 3. Characterization | Activation magnitude | μ_abs = 78% of signal; early_up + late_down dominate |
| 4. Non-localizability (count) | Top-10 not causal | Targeted Δ=+0.008 vs Random Δ=+0.018 (within noise) |
| 5. Non-localizability (percent) | Top-4% less important | Targeted Δ=+0.008 vs Random Δ=+0.049 (2.8σ below) |
| 6. Forensic fragility | Low-FPR collapse | TPR@1%: 0.484→0.055 under N=64→128 scale-up |

### Core Insight

> *"H1 separates correlation, mechanism, causality, and admissibility: activation fingerprints are real and replicated, but the channels most correlated with membership are not causal bottlenecks, and the resulting signal remains fragile at low-FPR operating points."*

### Claim Matrix Entry

| Row | Status | Allowed | Blocked |
|-----|--------|---------|---------|
| H1/DAAB | candidate-positive, tail-fragile | Internal U-Net activations carry replicated aggregate membership signal dominated by activation amplitude | Admitted low-FPR forensic evidence |
| H1 channel KO | mechanistic support, non-localizable | Membership-correlated channels are not causal bottlenecks; signal is distributed and redundant | Significant channels are a compact removable leakage source |

## H4: Closed

**Status**: Closed / not released.

**Reason**: Sparse channel editing is not supported because no compact causal edit target was found. Even after identifying membership-correlated channels, targeted knockout does not suppress H1 more than random deletion. The activation signal is not locally editable by sparse channel removal.

## Paper's Soul

> *"Real signal does not imply causal localization; causal non-localization does not imply forensic admission."*

## GPU: FROZEN

No DiT, no new H2, no full H4, no bottom controls. Move to writing.
