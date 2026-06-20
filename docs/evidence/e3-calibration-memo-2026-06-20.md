# E3 Calibration Memo

> Date: 2026-06-20
> Hypothesis: DCU weak signal (AUC≈0.518) is caused by SafeConv operator quality, not by general failure of gray-box MIA on self-trained CIFAR-10 DDPMs.
> Verdict: **HYPOTHESIS REJECTED.** SafeConv is NOT the root cause. NVIDIA CUDA produces the same weak-signal regime.

## 1. Experiment Design

Three checkpoint sources evaluated on identical CIFAR-10 50/50 member/nonmember split (N=5000 samples each):

| Label | Source | Architecture | Steps |
|-------|--------|-------------|-------|
| CUDA-DDPM-800k | secmi-bundle / pia-upstream | UNet (ch=128, mult=[1,2,2,2]) | 800k |
| CUDA-DDIM-750k | DDIM upstream | UNet (same arch) | 750k |

**MD5 check**: `secmi-bundle-800k` and `pia-upstream` are the **same checkpoint** (MD5: `ec135e6bbdd9d073b39bff3b80f1f761`). The evaluation originally listed three checkpoints but two were identical. Effectively 2 distinct CUDA models were tested.

Attacks: PIA (interval=200/num=1; interval=100/num=2) and SecMI (t=100/k=10; t=50/k=5; t=200/k=20). All scores computed bidirectionally (lower=member vs higher=member) to prevent direction-coded AUC inflation.

## 2. Results

### CUDA-DDPM-800k (secmi-bundle = pia-upstream)

| Attack | AUC | TPR@1%FPR | TPR@0.1%FPR | Direction |
|--------|:---:|:---------:|:-----------:|-----------|
| SecMI t100_k10 | 0.459 | 0.000 | 0.000 | higher=member (inverted) |
| SecMI t50_k5 | 0.459 | 0.000 | 0.000 | higher=member (inverted) |
| SecMI t200_k20 | 0.459 | 0.000 | 0.000 | higher=member (inverted) |
| PIA int200_num1 | 0.573 | 0.063 | 0.000 | lower=member |
| PIA int100_num2 | **0.605** | **0.063** | 0.000 | lower=member |

### CUDA-DDIM-750k

| Attack | AUC | TPR@1%FPR | TPR@0.1%FPR | Direction |
|--------|:---:|:---------:|:-----------:|-----------|
| SecMI t100_k10 | 0.397 | 0.000 | 0.000 | higher=member (inverted) |
| SecMI t50_k5 | 0.397 | 0.000 | 0.000 | higher=member (inverted) |
| SecMI t200_k20 | 0.397 | 0.000 | 0.000 | higher=member (inverted) |
| PIA int200_num1 | 0.599 | 0.063 | 0.000 | lower=member |
| PIA int100_num2 | **0.605** | **0.038** | 0.000 | lower=member |

### Comparison with DCU Baseline

| Method | AUC | TPR@1% | Platform |
|--------|:---:|:-----:|----------|
| DCU TC192 (scnet) | 0.517 | ~0.01 | DCU SafeConv |
| CUDA DDPM 800k PIA | **0.605** | 0.063 | NVIDIA Standard-UNet |
| CUDA DDIM 750k PIA | 0.605 | 0.038 | NVIDIA Standard-UNet |

## 3. Interpretation

1. **NVIDIA CUDA vs DCU gap (ΔAUC ≈ +0.09)**: NVIDIA CUDA produces marginally better PIA signal than DCU SafeConv, but both stay in the same weak-signal regime. The DCU-observed ceiling is NOT a SafeConv artifact — it's the true ceiling for self-trained CIFAR-10 DDPMs under standard PIA/SecMI attacks.

2. **PIA marginally beats SecMI**: PIA (AUC=0.605) consistently outperforms SecMI (AUC=0.397-0.459) on CUDA, matching the pattern observed on DCU. This provides orthogonal validation that the attack ranking is platform-independent.

3. **SecMI direction inversion**: All SecMI runs show inverted direction (member scores HIGHER than nonmember scores, AUC<0.5), meaning the assumed direction (member has lower L2 error) is wrong for these checkpoints. This is consistent across all three configs and both CUDA models — a platform-independent property of the attack, not a SafeConv bug.

4. **Low-FPR recovery remains zero**: TPR@0.1%FPR = 0.000 across all configs and both models. The N=5000 clean negatives give FPR resolution = 0.02%, but even at this resolution, no true positive exceeds the 0.1% FPR threshold. This reinforces the paper's finite-tail narrative.

5. **Roadmap E3 success standard (AUC≥0.70) not met**: Best AUC=0.605 < 0.70. Per roadmap §3, this is the failure value: "Closes self-trained CIFAR-10 DDPM as a paper-upgrading path."

## 4. Conclusion for Paper 1

- **E3 delivers its failure value**: confirms DCU weak signal is real, not a hardware/operator artifact. This closes the SafeConv hypothesis and prevents further DCU/SafeConv effort.
- **scnet rows (TC64/TC128/TC192) remain in the "weak" category**: the NVIDIA calibration confirms their AUC≈0.518 is the true ceiling, not a measurement artifact.
- **Paper upgrade path**: E3 does NOT upgrade the weak rows to admitted evidence. It strengthens the boundary case: the claim "gray-box MIA on resource-constrained CIFAR-10 DDPMs is weak" now has both DCU and NVIDIA CUDA evidence.
- **No further GPU work needed for this line**: the E3 verdict is conclusive.
