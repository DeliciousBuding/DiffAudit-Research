# H2 Score-Vector Geometry — Sidecar Result

> Date: 2026-06-20
> Verdict: **WEAK SUPPORT.** Moderate signal at N=64 (AUC=0.753) decays at N=128 (AUC=0.681). Limited low-FPR recovery.

## Scoreboard

| N | AUC | TPR@1%FPR | TPR@0.1%FPR | Shuffle AUC |
|---|:---:|:---------:|:-----------:|:-----------:|
| 64 | 0.753 | 0.000 | 0.000 | 0.481 |
| **128** | **0.681** | **0.063** | 0.000 | 0.475 |

## Features (21 dims)

- ||epsilon_hat_t||_2 at t=100,200,400 (L2 norm of predicted noise)
- Cross-timestep cosine: cos(t100,t200), cos(t100,t400), cos(t200,t400)
- Low-pass residual at each timestep
- Top-8 per-channel L2 norms at each timestep

## Comparison

| Feature | H1 (Activation) | H2 (Score-Vector) |
|---------|:---:|:---:|
| AUC @ N=128 | **0.873** | 0.681 |
| TPR@1% @ N=128 | 0.055 | **0.063** |
| Signal stability (ΔAUC N=64→128) | **+0.001** | -0.072 |
| Mechanism | Internal activations | Epsilon predictions |

H1 outperforms H2 on AUC and stability. H2's signal decays with sample size, suggesting the score-vector features may be capturing noise rather than robust membership signal at small N.

## Claim Matrix

**Status: Weak support.** Does not meet candidate threshold (AUC < 0.70 at N=128).

**Allowed**: "Score-vector geometry shows moderate membership signal (AUC=0.681) but decays with sample size"
**Blocked**: Any claim of reliable score-vector MIA, candidate status, admitted evidence

## Sources

- Script: `scripts/h2_score_vector_sidecar.py`
- Results: `outputs/h2-sidecar/h2_results.json`
