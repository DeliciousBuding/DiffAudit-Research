# DDPM-750k Step-Matched Control — Evidence Packet

Date: 2026-06-25
Status: COMPLETE
Role: Step-count confound resolution for Paper 1 Section 6.5

## Artifact Identity

| Field | Value |
|-------|-------|
| Checkpoint directory | `<DOWNLOAD_ROOT>/checkpoints/ddpm-cifar10-750k/` |
| Training script | Research/training/ddpm-cifar10/train_ddpm_cifar10_750k.py |
| Final SHA256 (step 750k) | ab824b6fcb11aa24... (checkpoint-step750000.pt) |
| Canonical checkpoint | checkpoint.pt (573 MB) |
| Training log | `training/outputs/ddpm-cifar10-750k/training.log` |
| Training duration | ~125h (2026-06-22 10:29 → 2026-06-25 02:29) |
| GPU | RTX 4070 8GB laptop |
| Interruption | Jun 22 power outage; recovered from 260k; lost ~7,600 steps |
| Arch checkpoints | 100k, 200k, 300k, 400k, 500k, 600k, 650k, 660k, 670k, 680k, 690k, 700k, 710k, 720k, 730k, 740k, 750k (17 total) |
| Manifest | checkpoint directory `manifest.json` |
| Post-outage hardening | heartbeat.json, SESSION START markers, resilient dataloader, python -u, flush=True, standardized recovery procedure |

## Training Configuration

```
T=1000, CH=128, CH_MULT=[1,2,2,2], ATTN=[1], NUM_RES_BLOCKS=2, DROPOUT=0.1
BETA_1=0.0001, BETA_T=0.02, LR=2e-4, BATCH_SIZE=64, EMA_DECAY=0.9999
TOTAL_STEPS=750000, GRAD_CLIP=1.0, WARMUP_STEPS=5000, SEED=42
```

## H1 v2 Unified Results (same script, 128m/128nm, 3-shadow LR PCA=6)

| Checkpoint | AUC | TPR@1% | TPR@0.1% | Shuffle | Ablation |
|------------|-----|--------|----------|---------|----------|
| DDPM-750k | 0.648 | 0.094 | 0.000 | 0.484 | 0.646-0.656 |
| DDPM-750k seed43 | 0.666687 | 0.015625 | 0.000 | 0.453552 | 0.664673-0.684387 |
| DDPM-800k seed43 | 0.664612 | 0.015625 | 0.000 | 0.487793 | 0.666077-0.671753 |
| DDPM-800k | 0.872 | 0.227 | 0.000 | 0.492 | 0.870-0.873 |
| DDIM-750k | 0.856 | 0.109 | 0.000 | 0.481 | 0.852-0.857 |

Evaluation protocol: h1_activation_scout.py (single script version), 4 sites (late_down, mid_0, mid_1, early_up), 3 timesteps (100, 400, 700), 42 features (36 scalar + 6 PCA).

Previous DDPM-800k values (0.874 N=64, 0.873 N=128) and DDIM-750k value (0.841) were produced by earlier script versions with different shadow-split protocols. The v2 table supersedes all prior H1 numbers.

## Seed43 750k Replication (N=128)

Status: **COMPLETE** (2026-07-02)
Checkpoint: `<DOWNLOAD_ROOT>/checkpoints/ddpm-cifar10-seed43/checkpoint-step750000.pt`
SHA256: `1dad28a63cef2ef4439f77457c10825bcb4ff66ef7c7e3e19dbe285e4503aba2`
Output: `outputs/h1-scout-seed43-750k/h1_results.json` and `summary.json`

H1 scout: AUC=0.666687, TPR@1%=0.015625, TPR@0.1%=0.0, Shuffle=0.453552. The result is close to the seed42 750k AUC regime (+0.019 AUC) but has weaker low-FPR recovery. This supports the interpretation that 750k DDPM checkpoints are moderate H1 candidates, while strong N=512-ready behavior remains run-dependent. The later seed43 800k result kept the run in the moderate band, so seed44/45 are optional replication rather than blockers.

## Seed43 800k Continuation (N=128 + Fine Grid)

Status: **COMPLETE** (2026-07-03)
Checkpoint: `<DOWNLOAD_ROOT>/checkpoints/ddpm-cifar10-seed43/checkpoint-step800000.pt`
SHA256: `19f62a7fbbc4a492e919d31174049bd3bc2e6c2f631d8d38a2a6c79871f47fa8`
H1 output: `outputs/h1-scout-seed43-800k/h1_results.json` and `summary.json`
Fine-grid output: `outputs/h1-fine-grid-seed43-800k/h1_fine_grid_results.json` and `summary.json`

H1 scout: AUC=0.664612, TPR@1%=0.015625, TPR@0.1%=0.0, Shuffle=0.487793. The result is slightly below seed43 750k (delta=-0.002075) and below the seed42 same-trajectory 800k point (delta=-0.052388). Because AUC did not exceed 0.70, the N=512 tail was not run.

Fine temporal grid baseline AUC: 0.674805.

| Site | t=50 | t=100 | t=150 | t=200 | t=300 | t=400 | t=600 | t=800 |
|------|------|-------|-------|-------|-------|-------|-------|-------|
| late_down | -0.0256 | -0.0603 | -0.0049 | -0.0151 | -0.0420 | -0.0591 | -0.0894 | -0.0791 |
| mid_0 | -0.0378 | -0.0144 | -0.0354 | -0.0247 | -0.0466 | -0.0408 | -0.1169 | -0.0491 |

Max |delta|: late_down 0.0894 (t=600), mid_0 0.1169 (t=600).

Result: seed43 800k does not reproduce the seed42 same-trajectory late-stage amplification. The fine-grid sign pattern changes: full-site knockout mostly increases AUC rather than removing separability, so this run does not identify a compact site-time leakage bottleneck.

## Matched Knockout (DDPM-750k, N=64, 4 sites × 3 timesteps)

| Condition | AUC | Δ |
|-----------|-----|---|
| Baseline | 0.726 | — |
| Targeted top-10 KO | 0.693 | +0.033 |
| Random 10 KO (10 seeds, mean) | 0.710 | +0.017 |
| Frozen scorer | 0.562 | +0.164 |

Output: Research/outputs/h1-scout-750k/

## Fine Temporal Grid (DDPM-750k, 8 timesteps, late_down + mid_0, N=64)

Baseline AUC: 0.751

| Site | t=50 | t=100 | t=150 | t=200 | t=300 | t=400 | t=600 | t=800 |
|------|------|-------|-------|-------|-------|-------|-------|-------|
| late_down | +0.097 | +0.055 | +0.069 | +0.044 | -0.015 | -0.036 | +0.030 | +0.081 |
| mid_0 | +0.025 | +0.080 | +0.027 | +0.041 | +0.020 | +0.024 | +0.049 | +0.043 |

Max |Δ|: late_down 0.097 (t=50), mid_0 0.080 (t=100).

Comparison:
- DDPM-800k: distributed (max |Δ| = 0.029 late_down, 0.024 mid_0)
- DDPM-750k: moderately concentrated (max |Δ| = 0.097, 0.080)
- DDIM-750k: strongly concentrated (max |Δ| = 0.221 late_down, 0.194 mid_0)

Output: Research/outputs/h1-fine-grid-ddpm750k/h1_fine_grid_ddpm750k.json

## AUC-vs-Step (DDPM-750k trajectory, 128m/128nm, every 100k)

| Step (k) | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 750 |
|----------|-----|-----|-----|-----|-----|-----|-----|-----|
| AUC | 0.702 | 0.708 | 0.649 | 0.698 | 0.672 | 0.702 | 0.692 | 0.648 |

Stable 0.65-0.71 from 100k onward. Signal emerges early.

Output: Research/outputs/auc_vs_step.json

## N=512 Tail Calibration (DDPM-750k)

| N | AUC | TPR@1% | TPR@0.1% | Shuffle |
|---|-----|--------|----------|---------|
| 128 | 0.648 | 0.094 | 0.000 | 0.484 |
| 512 | 0.560 | 0.014 | 0.008 | 0.483 |

Gate: weak_candidate_review. Signal collapses under scale-up.

Output: Research/outputs/h1-scout-750k-n512/h1_results.json

## Same-Trajectory Continuation: DDPM-750k → 800k

Status: **COMPLETE** (2026-06-25)
Script: train_ddpm_cifar10_750k_to_800k.py (TOTAL_STEPS=800000)
Resumed from: checkpoint-step750000.pt
Completed: 800,000 steps in 6.3h
Final SHA256: a1936284900fa9e6d56e60df4bc72ba1c36ede36c6fc4dfebd2ad0a48e7cbc6b
H1 scout (N=128): AUC=0.717, TPR@1%=0.039, Shuffle=0.507
H1 scout (N=512): AUC=0.605488, TPR@1%=0.025391, TPR@0.1%=0.0, Shuffle=0.488052 (2026-07-01 rerun; raw `outputs/h1-scout-800k-same-trajectory-n512/h1_results.json` and `summary.json` present)

**Result: Modest same-trajectory amplification (+0.069 AUC).** The bulk (~70%) of the independent DDPM-800k signal (0.872) comes from run identity, not from the additional 50k training steps.

Evidence hygiene note (2026-07-01): the same-trajectory N=128 scout, fine-grid JSON artifacts, and same-trajectory N=512 machine-readable rerun artifacts are present. The N=512 rerun used the readable CIFAR-10 dataset root and produced `outputs/h1-scout-800k-same-trajectory-n512/h1_results.json` plus `summary.json`. The rerun AUC is 0.605488, not the previously documented unarchived 0.576 value.

## Key Findings

1. **DDIM advantage confirmed, not due to step count**: DDIM-750k (0.856) substantially exceeds step-matched DDPM-750k (0.648) by ΔAUC=+0.208. The original DDPM-800k vs. DDIM-750k comparison was conservative with respect to DDIM.

2. **Seed43 replicates the moderate regime, not the strong cluster**: seed43 gives AUC=0.666687 at 750k and AUC=0.664612 at 800k, with TPR@1%=0.015625 at both checkpoints. This is above chance and close to seed42 750k by AUC, but it does not show reliable low-FPR recovery or late-stage amplification.

3. **Same-trajectory late-stage amplification is not stable across seeds**: Continuing seed42 DDPM-750k to 800k on the same trajectory produces AUC=0.717, a ΔAUC=+0.069 increase. Continuing seed43 from 750k to 800k produces AUC=0.664612, a small decrease from its 750k point. The independently trained DDPM-800k (0.872) remains dominated by run identity, not pure step count.

4. **Temporal geometry is training-stage AND run-identity dependent**: DDPM-750k is moderately concentrated. Seed42 same-trajectory 800k continuation produces increased concentration (max |delta|=0.152), but seed43 800k changes sign and mostly improves AUC under knockout (max |delta|=0.1169 at `mid_0`, t=600). The independently trained DDPM-800k's temporally distributed pattern remains a run-identity artifact. DDIM-750k is strongly concentrated.

5. **Low-FPR fragility confirmed for the seed42/seed43 moderate points**: DDPM-750k TPR@1% collapses from 0.094 (N=128) to 0.014 (N=512) for seed42, and seed43 has only TPR@1%=0.015625 at both 750k and 800k. Same-trajectory 800k shows similar low-FPR weakness at N=128 (TPR@1%=0.039) and in the archived N=512 rerun (TPR@1%=0.025391, TPR@0.1%=0.0).

## Paper Impact

- Evidence state: H1 remains candidate-positive / low-FPR-fragile
- Claim upgrade: DAAB signal strength and temporal geometry vary with training stage and run identity, not fixed by architecture
- Claim downgrade: "AUC>0.8 universal" replaced by "above-chance signal universal; strength training-stage dependent"
- Confound resolution: Section 6.5 rewritten with unified v2 numbers and honest trajectory caveat
