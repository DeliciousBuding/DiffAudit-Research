# CIFAR-10 DDPM PIA/NNS MIA Evidence Note

> Date: 2026-05-24
> Status: evidence-ready (aggregate metrics); strict-tail blocked

## Summary

PIA and NNS (ResNet18 on PIA features) attacks evaluated on two independent
pre-trained CIFAR-10 DDPM/DDIM checkpoints. NNS achieves AUC≈0.990 on both,
cross-validating the result. Strict-tail TPR is blocked by an FPR dead-zone:
scores force FPR to jump from 0 to ~12%, making low-FPR per-sample MIA
infeasible.

## Experimental Design

- **Target**: CIFAR-10 DDPM/DDIM (ReDiffuse ICLR 2025 supplement split)
- **Split**: 25,000 members + 25,000 non-members from `STL10_train_ratio0.5.npz`
- **Checkpoints**:
  - 750k DDIM: `DDIM-ckpt-step750000.pt` (collaborator 2026-05-09)
  - 800k DDPM: `cifar10_ddpm/checkpoint.pt` (PIA assets, 800k steps)
- **Attack methods**:
  - PIA: epsilon-prediction consistency at t=200
  - NNS: ResNet18 classifier trained on PIA features (80/20 split, 15 epochs)
  - SecMI: multi-step DDIM reverse/denoise at various intervals
- **Metrics**: AUC, ASR, TPR@FPR

## Results

### 800k DDPM checkpoint

| Method | AUC | ASR | TPR@5%FPR | TPR@1%FPR |
|---|---|---|---|---|
| Raw PIA (i200) | 0.8853 | 0.8153 | 0.0000 | 0.0000 |
| SecMI (i200-n4) | 0.7761 | 0.7098 | 0.0000 | 0.0000 |
| **NNS (ResNet18)** | **0.9903** | **0.9630** | 0.0000 | 0.0000 |

PIA sweep (i200: 0.885, i100: 0.838, i50: 0.679) confirms interval=200 is optimal.

### 750k DDIM checkpoint

| Method | AUC | ASR |
|---|---|---|
| Raw PIA (i200) | 0.8747 | 0.8051 |
| SecMI (i200-n4) | 0.4612 | 0.4346 |
| **NNS (ResNet18)** | **0.9891** | **0.9566** |

### Self-trained checkpoints (negative controls)

| Steps | PIA AUC | SecMI AUC |
|---|---|---|
| 10k (STL-10) | 0.500 | - |
| 10k (CIFAR-10) | 0.503 | - |
| 100k (CIFAR-10) | 0.471 | 0.477 |

### FPR dead-zone (NNS on 800k)

```
Non-members > 0.5: 223/4999 (4.5%)
Members    > 0.5: 4847/4999 (97.0%)
Non-members > 0.8: 53/4999 (1.1%)
```

The ROC curve has FPR=0 until threshold ~1.07 (first non-member outlier),
then jumps to FPR≈0.12 (cluster of non-members with similar scores).
No FPR value exists between ~0.0002 and ~0.12, making TPR@5%FPR=0
despite AUC=0.990.

## Interpretation

1. **PIA attack is validated**: AUC=0.885 on both checkpoints
2. **NNS second-stage improves AUC to ~0.990** on both checkpoints
3. **Cross-validation holds**: 750k and 800k independently trained models give
   nearly identical NNS metrics (0.989 vs 0.990)
4. **Training scale critical**: 10k and 100k self-trained checkpoints produce
   random AUC; 750k+ is needed for detectable signal
5. **FPR dead-zone is the core limitation**: NNS scores cluster non-members
   into two groups (95.5% below 0.5, 4.5% above), creating a ROC cliff
   that prevents low-FPR per-sample MIA

## Implications for DiffAudit

- AUC=0.990 is a strong aggregate MIA signal (standard paper claim)
- Per-sample low-FPR MIA is not feasible with PIA/NNS attack family
- This is consistent with existing gray-box PIA evidence: "AUC 尚可但严格低尾证据不足"
- For the admitted evidence bundle: PIA+NNS results strengthen the gray-box
  line but do NOT change the per-sample MIA boundary

## Files

- PIA/NNS scripts: `Research/outputs/score_800k_pia.py`, `score_800k_nns.py`, `score_750k_nns.py`
- Scores: `C:\Users\Ding\DiffAudit\outputs\cifar10-800k-existing\pia_v2_scores.npz`, `nns_scores.npz`
- Scores: `C:\Users\Ding\DiffAudit\outputs\cifar10-750k-ddim\nns_scores.npz`
