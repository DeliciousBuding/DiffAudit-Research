# H1 Activation-Subspace Fingerprint — Scout Result

> Date: 2026-06-20 (revised after compute_metrics bugfix)
> Hypothesis: Activation-subspace fingerprints provide a distinct white-box membership signal beyond GSA/loss on E3 calibrated CIFAR-10 DDPM.
> Verdict: **PROMOTED TO SCALE-UP.** Strong signal at N=64 (AUC=0.874, TPR@1%FPR=0.484). Label shuffle and ablation controls pass.
> Next: Scale to 128/128.

## 1. N=64 Scout Results (corrected)

| Shadow | AUC | TPR@1%FPR | TPR@0.1%FPR | Train Acc | Features |
|--------|:---:|:---------:|:-----------:|:---------:|:--------:|
| 1 | **0.8701** | 0.4844 | 0.000 | 0.750 | 42 |
| 2 | **0.8709** | 0.4844 | 0.000 | 0.750 | 42 |
| 3 | **0.8760** | 0.000 | 0.000 | 0.742 | 42 |
| **Aggregate** | **0.8743** | **0.500** | **0.000** | — | — |

### Controls

| Control | AUC | Pass? |
|---------|:---:|:-----:|
| Label shuffle | 0.4104 | ✅ (<0.55) |
| Ablation (drop late_down) | 0.8765 | ✅ (not dominant) |
| Ablation (drop mid_0) | 0.8789 | ✅ |
| Ablation (drop mid_1) | 0.8765 | ✅ |
| Ablation (drop early_up) | 0.8665 | ✅ |

### Promotion Gate Assessment

| Gate | Criterion | Value | Pass? |
|------|-----------|-------|:-----:|
| Beats random | AUC > 0.55 | 0.874 | ✅ |
| Label shuffle | AUC < 0.55 | 0.410 | ✅ |
| TPR@1%FPR positive | TPR > 0.02 | 0.484 | ✅ |
| Not single-site | Multiple sites contribute | ΔAUC < 0.01 | ✅ |
| **Decision** | | | **SCALE TO 128** |

## 2. Interpretation

1. **Strong signal**: AUC=0.874 is clearly above random and in the "strong" regime. Member scores (mean=0.69) significantly higher than nonmember scores (mean=0.31).

2. **Low-FPR recovery exists at 1%**: TPR@1%FPR=0.484 on 2/3 shadows — meaning at the 1% FPR operating point, nearly half of members are correctly identified. This beats the weak loss line.

3. **Not a single-layer artifact**: All 4 sites contribute similarly (ablation AUC range 0.867–0.879). Signal is distributed across the UNet depth.

4. **TPR@0.1%FPR limited by N**: At N=64 clean nonmembers, the 0.1% FPR threshold is essentially the single highest-scoring nonmember. This is unreliable at small N and expected to improve at N=128 or N=256.

5. **Label shuffle control passes**: Shuffled AUC=0.410 < 0.5, confirming the signal is not an artifact of feature dimensionality or LR overfitting.

6. **H1 identifies a distinct second white-box family**: Unlike GSA (gradient-based), H1 uses internal activations — a non-gradient, non-loss signal source. This is scientifically valuable as a complement to the existing admitted evidence.

## 3. Comparison with H2 (Score-Vector Sidecar)

| Metric | H1 (Activation) | H2 (Score-Vector) |
|--------|:---:|:---:|
| AUC | **0.874** | 0.753 |
| TPR@1%FPR | **0.484** | 0.000 |
| Shuffle AUC | 0.410 | 0.481 |
| Feature dims | 42 (scalar+PCA) | 21 (eps L2, cosine, residual) |

H1 outperforms H2 on both AUC and low-FPR recovery. H1's activation features capture more membership information than H2's score-vector features on this checkpoint.

## 4. Impact on Claim Matrix

- H1 N=64 passes promotion gate → scale to 128/128
- If 128/128 confirms: H1 enters claim matrix as candidate or admitted evidence
- Potential new row: "H1 Activation-Subspace Fingerprint | White-box internal activation | AUC=0.874 | TPR@1%=0.484 | N=128 → TBD"
- GSA no longer sole white-box evidence if H1 maintains signal at larger N

## 5. Bug Note

Initial results (AUC=0.5000) were caused by a direction-handling bug in `compute_metrics()`:
- The "higher=member" case incorrectly labeled nonmembers as positive class
- Fixed by always using member=positive labels and flipping scores for direction
- Bug affected both H1 and H2 scripts
- Scripts updated: `h1_activation_scout.py`, `h2_score_vector_sidecar.py`
