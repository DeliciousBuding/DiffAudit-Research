# H1 Three-Seed Replication — Quarantined Historical Packet

> **QUARANTINED 2026-07-10**: the local targets trained on rows labeled as
> nonmembers, and the old scorer used resubstitution AUC. This document is not
> primary evidence and none of its run-identity, continuation, cluster, or
> mechanism interpretations may be used in a paper. See the 2026-07-11
> corrected-evidence runbook.

Date: 2026-07-09
Status: QUARANTINED
Role: Historical diagnostic record only

## Scientific Question

Is H1 activation-level MIA signal strength controlled mainly by training trajectory (random seed), or does it converge to a stable value under identical architecture, data, and hyperparameters?

## Experiment Design

| Variable | Value |
|----------|-------|
| Architecture | DDPM UNet (CH=128, CH_MULT=[1,2,2,2], ATTN=[1], NUM_RES_BLOCKS=2, DROPOUT=0.1) |
| Dataset | CIFAR-10 (50,000 train) |
| Training steps | 750,000 (all seeds) + 800,000 (all seeds) |
| Batch size | 64 |
| LR | 2e-4, warmup 5,000 steps |
| β₁, β_T | 1e-4, 0.02 |
| EMA decay | 0.9999 |
| GPU | RTX 4070 8GB laptop |
| **Only variable** | **`--seed` (42 / 43 / 45)** |
| H1 protocol | v3 unified: N=128/128, 3-shadow LR PCA=6, 4 sites × 3 timesteps, 42 features |
| Evaluation script | `scripts/h1/h1_activation_scout.py` (identical across all checkpoints) |

Control: every training run used the same `train_ddpm_cifar10.py`, same `diffaudit` conda env, same readable CIFAR-10 root. No hyperparameter tuning, no per-seed adaptation.

## Results: DDPM-750k (Three-Seed Baseline)

| Seed | Checkpoint SHA256 (750k) | AUC | TPR@1%FPR | Shuffle AUC |
|------|--------------------------|-----|-----------|-------------|
| 42 | `ab824b6fcb11aa24...` | 0.648438 | 0.093750 | 0.483643 |
| 43 | `1dad28a63cef2ef4...` | 0.666687 | 0.015625 | 0.453552 |
| 45 | `5231dc08bff67df8...` | 0.693909 | 0.031250 | 0.508179 |

**Range**: 0.045471 | **Mean**: 0.669678

All three seeds produce AUC in a tight moderate band (0.648–0.694). No seed reaches the strong-cluster regime (AUC>0.80). DDPM-750k H1 signal is reliably moderate.

## Results: DDPM-800k (Continuation)

| Seed | Checkpoint SHA256 (800k) | AUC | TPR@1%FPR | Shuffle AUC | Δ from 750k |
|------|--------------------------|-----|-----------|-------------|-------------|
| 42 | `19f62a7fbbc4a492...` | 0.716858 | 0.039063 | 0.507202 | **+0.068420** |
| 43 | `19f62a7fbbc4a492...` | 0.664612 | 0.015625 | 0.487793 | -0.002075 |
| 45 | `37f0e58377e5b34e...` | 0.645996 | 0.062500 | 0.449402 | **-0.047913** |

**Three seeds, three different 750k→800k behaviors: amplify, flat, drop.**

The independent DDPM-800k (different seed, origin unknown) achieves AUC=0.871948 — far outside the three-seed range — confirming that 800k behavior is entirely trajectory-dependent.

## Raw Outputs

| Seed/Step | H1 Results | Summary | Activations |
|-----------|-----------|---------|-------------|
| seed42-750k | `outputs/h1-scout-750k/h1_results.json` | `outputs/h1-scout-750k/summary.json` | `*_n128.pkl` |
| seed42-800k | `outputs/h1-scout-800k-v2/h1_results.json` | `outputs/h1-scout-800k-v2/summary.json` | `*_n128.pkl` |
| seed43-750k | `outputs/h1-scout-seed43-750k/h1_results.json` | `outputs/h1-scout-seed43-750k/summary.json` | `*_n128.pkl` |
| seed43-800k | `outputs/h1-scout-seed43-800k/h1_results.json` | `outputs/h1-scout-seed43-800k/summary.json` | `*_n128.pkl` |
| seed45-750k | `outputs/h1-scout-seed45-750k/h1_results.json` | `outputs/h1-scout-seed45-750k/summary.json` | `*_5231dc08bff6_n128.pkl` |
| seed45-800k | `outputs/h1-scout-seed45-800k/h1_results.json` | `outputs/h1-scout-seed45-800k/summary.json` | `*_37f0e58377e5_n128.pkl` |
| independent-800k | `outputs/h1-scout-800k-independent-n512/h1_results.json` | N=512 only | `*_n512.pkl` |
| DDIM-750k | `outputs/h1-scout-ddim-750k-n512/h1_results.json` | `outputs/h1-scout-ddim-750k/summary.json` | `*_n512.pkl` |

## N=512 Tail Behavior

| Checkpoint | AUC (N=512) | TPR@1% | vs N=128 |
|------------|-------------|--------|----------|
| DDPM-750k (seed42) | 0.560 | ~0.01 | Collapses |
| DDPM-800k same-trajectory | 0.605 | 0.025 | Collapses |
| DDPM-800k independent | **0.815** | 0.158 | **Retains** |
| DDIM-750k | **0.812** | — | **Retains** |

Strong runs retain signal at N=512; weak/moderate runs collapse. This further supports run-identity as the dominant variable: scale-up behavior is coupled to which trajectory the model took.

## Scientific Claims

### Allowed

1. **DDPM-750k moderate regime is robust.** Three independent seeds converge to AUC 0.648–0.694 (range=0.046). No seed reaches the strong cluster. This eliminates the hypothesis that high-AUC 750k runs occur regularly under standard training.

2. **750k→800k is not a universal amplifier.** Under identical conditions, seed42 amplifies (+0.069), seed43 stays flat (-0.002), and seed45 drops (-0.048). The direction of change depends on run identity.

3. **Run identity dominates the independent DDPM-800k gap.** The independent DDPM-800k AUC (0.872) exceeds the three-seed 800k mean (0.676) by 0.196, far beyond seed-to-seed variance. Whatever produces the strong run at 800k is trajectory-specific, not step-count-driven.

4. **N=512 two-cluster pattern is trajectory-coupled.** Only the strong-run trajectories retain signal at N=512; moderate trajectories collapse.

### Blocked

- ❌ "H1 signal universally amplifies with more training steps"
- ❌ "DDPM-750k regularly produces AUC > 0.80"
- ❌ "750k→800k amplification is a reliable phenomenon"
- ❌ "H1 is admitted membership evidence"

## Theoretical Context

Bonnaire et al. (NeurIPS 2025, arXiv:2505.17638) provide a plausible mechanism: diffusion training follows two timescales — τ_gen (generalization) and τ_mem (memorization). Different random seeds produce different SGD trajectories through the loss landscape, reaching different points on the generalization-memorization spectrum. This explains why seed42's trajectory moves toward stronger memorization in the 750k→800k window while seed45's moves toward further generalization.

## Related Documents

- `docs/paper1/frozen-claim-matrix.md` — canonical claim registry
- `docs/evidence/ddpm-750k-step-matched-control-2026-06-25.md` — seed42 750k training details
- `docs/evidence/experiment-master-log.md` — full experiment chronology
- `docs/start-here/phase-g-runbook-2026-06-30.md` — operational commands
