# Paper 1 Statistical Audit

**Purpose**: Pre-submission statistical review of all key numbers.  
**Target**: target venue (rigorous review, reproduction certification expected).

## 1. Recon (N=100 admitted black-box)

### Raw numbers
- AUC = 0.837
- TPR@1%FPR = 22/100 = 0.22
- TPR@0.1%FPR = 11/100 = 0.11

### Wilson 95% CI
```
TPR@1%FPR: 22/100 → Wilson CI [0.150, 0.311]
TPR@0.1%FPR: 11/100 → Wilson CI [0.063, 0.186]
```

### Critical limitation
**0.1% FPR claim is not statistically supported.** With only 100 clean negatives, the empirical FPR resolution is 1% (1/100). A 0.1% FPR threshold cannot be meaningfully calibrated — it requires ≥1,000 clean negatives.

### Recommended framing
- Report TPR@1%FPR with Wilson CI as the primary black-box metric
- Mention TPR@0.1%FPR only with explicit caveat: "insufficient clean samples for reliable calibration"
- State: "Recon is an admitted but underpowered black-box signal"
- For robust 0.1% FPR claims: need N≥1,000 clean negatives

---

## 2. CLiD Collapse (spurious signal)

### Raw numbers
- Paper-prompt AUC = 1.000
- Neutral-prompt AUC = 0.586
- ΔAUC = 0.414
- N = 100 member + 100 nonmember (same images, different prompts)

### Recommended test
**Paired bootstrap of ΔAUC**:
- Resample 100 pairs with replacement, 10,000 iterations
- Compute AUC_original - AUC_neutral for each bootstrap sample
- Report 95% CI for ΔAUC
- Expected CI: approximately [0.35, 0.48] (well above zero)

**Permutation test**:
- Shuffle condition labels (original/neutral) within each image pair
- Recompute ΔAUC for each permutation
- p-value = fraction of permutations with |ΔAUC| ≥ observed |0.414|
- Expected p < 0.001

### Note on AUC=1.000
When AUC=1.000, normality assumptions break down. Do NOT use DeLong's test (assumes asymptotic normality). Use bootstrap or permutation instead.

---

## 3. scnet DCU (weak signal)

### Raw numbers
- TC64 (0.78M): AUC = 0.521
- TC128 (11.76M): AUC = 0.530
- TC192 (42.97M): AUC = 0.538

### Key claim
"All bootstrap 95% CIs cross 0.5"

### Required supporting evidence
1. **DeLong test** for each model: H0: AUC = 0.5 vs H1: AUC ≠ 0.5
2. **Bootstrap CI**: 10,000 iterations, stratified by member/nonmember
3. **Permutation test**: shuffle labels, recompute AUC, report p-value
4. **Multiple testing correction**: 3 models × N attacks → Holm-Bonferroni

### Expected outcome
All three models fail to reject H0 at α=0.05 after correction. This establishes the "weak signal" classification.

### Scale-null claim
"54× capacity increase (0.78M → 42.97M) yields +0.017 AUC gain"

Supporting evidence needed:
- Regression of AUC ~ log(params) with CI
- Or simply: ΔAUC = 0.017, bootstrap CI for ΔAUC

---

## 4. Low-FPR Calibration Requirements

| Claimed FPR | Minimum clean negatives needed | Recommended |
|:-----------:|:-----------------------------:|:-----------:|
| 1% | 300 | 1,000 |
| 0.1% | 3,000 | 10,000 |
| 0.01% | 30,000 | 100,000 |

**Rule of thumb**: If 0 false positives observed among n clean images, the approximate 95% upper bound is 3/n.

### Which claims in our paper are affected?

| Claim | N (clean) | Can support FPR=1%? | Can support FPR=0.1%? |
|-------|:---------:|:-------------------:|:---------------------:|
| Recon TPR@1%=22% | 100 | Marginal (barely 1% resolution) | **No** (need ≥1000) |
| CLiD TPR@1%=100% | 100 | Marginal | **No** (need ≥1000) |
| GSA TPR@1%=98.7% | 1000 | Yes | Marginal (need ≥3000) |

### Paper 1 policy
- Report TPR@1%FPR as primary low-FPR metric
- Mention TPR@0.1%FPR only for lines with N≥1,000
- Add a "Statistical Limitations" paragraph documenting the sample-size/FPR trade-off

---

## 5. Multiple Testing Correction

With 16+ experiment lines and multiple metrics per line, some "significant" results may arise by chance.

### Recommendation
- Primary table: report raw (uncorrected) metrics with CIs
- Appendix: apply Holm-Bonferroni correction across all lines
- Note which lines survive correction and which don't
- The WSN taxonomy is robust to this: "weak" lines wouldn't survive anyway; "spurious" lines are killed by controls, not p-values

---

## 6. Checklist Before Submission

- [ ] Recon: Wilson CIs computed and reported
- [ ] CLiD: paired bootstrap ΔAUC CI and permutation p-value
- [ ] scnet: DeLong + bootstrap + permutation for all three models
- [ ] Low-FPR caveats documented for all N<1000 lines
- [ ] Multiple testing appendix
- [ ] All CIs computed with ≥10,000 bootstrap iterations
- [ ] Seed and hyperparameters for all statistical tests documented
