# H1 Fine Temporal Grid — Training Stage, Procedure, and Run Identity Shape Membership Signal Geometry

> Date: 2026-06-20 (DDPM 800k + DDIM 750k), updated 2026-06-25 (DDPM 750k)
> Status: **Complete for seed42/independent checkpoints** — DDPM 800k independent, DDIM 750k, DDPM 750k, and DDPM 750k->800k same-trajectory fine grids are done
> Key finding (revised): **Temporal signal geometry varies with training procedure, training stage, and run identity. The independent DDPM-800k distributed pattern is not reproduced by same-trajectory continuation.**

## Motivation

The spatiotemporal causal grid (4 sites × 3 timesteps) showed sharp causal localization: mid_0@t=100 and late_down@t=100 carry nearly all membership signal, while t=400 and t=700 are causally negligible. This raised the question: **Is the strong causal gradient a measurement artifact of coarse (3-point) temporal sampling?**

We designed an 8-timestep fine grid on DDPM 800k to test this. The result: YES, 3-timestep grids amplify apparent causal concentration 4-7×. Individual knockout effects nearly vanish at 8-timestep resolution.

Then we ran the same experiment on DDIM 750k. The result was the OPPOSITE.

## Design

- **Targets**: DDPM 800k + DDIM 750k
- **Sites**: late_down, mid_0
- **Temporal grid**: 8 timesteps — t=50, 100, 150, 200, 300, 400, 600, 800
- **Knockout**: Full-site zeroing at each (site, timestep) individually
- **Classifier**: LogisticRegression, PCA=6, same as main H1 scout
- **N**: 64/64 (member/nonmember) for each checkpoint

## Results

### DDPM 800k — Signal DISTRIBUTED

**Baseline AUC: 0.833** (8 timesteps)

| Site | t=50 | t=100 | t=150 | t=200 | t=300 | t=400 | t=600 | t=800 |
|------|:----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| **late_down** Δ | **+0.029** | +0.010 | −0.019 | +0.022 | +0.008 | +0.004 | +0.006 | −0.007 |
| **mid_0** Δ | −0.021 | +0.009 | +0.002 | +0.003 | 0.000 | −0.024 | +0.021 | +0.004 |

**Max individual knockout effect: +0.029 (late_down@t=50).** Most knockouts have negligible effect. Signal is redundantly distributed across timesteps.

### DDIM 750k — Signal CONCENTRATED

**Baseline AUC: 0.854** (8 timesteps)

| Site | t=50 | t=100 | t=150 | t=200 | t=300 | t=400 | t=600 | t=800 |
|------|:----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| **late_down** Δ | +0.166 | **+0.221** | +0.130 | +0.134 | +0.120 | +0.131 | +0.094 | +0.152 |
| **mid_0** Δ | +0.118 | +0.156 | +0.138 | +0.147 | **+0.194** | +0.120 | +0.127 | +0.114 |

**Max individual knockout effect: +0.221 (late_down@t=100).** Nearly ALL knockouts produce large effects (all Δ > 0.09). Signal is causally concentrated.

### DDPM 750k (2026-06-25) — Signal MODERATELY CONCENTRATED

**Baseline AUC: 0.751** (8 timesteps)

| Site | t=50 | t=100 | t=150 | t=200 | t=300 | t=400 | t=600 | t=800 |
|------|:----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| **late_down** Δ | **+0.097** | +0.055 | +0.069 | +0.044 | −0.015 | −0.036 | +0.030 | +0.081 |
| **mid_0** Δ | +0.025 | **+0.080** | +0.027 | +0.041 | +0.020 | +0.024 | +0.049 | +0.043 |

**Max individual knockout effect: +0.097 (late_down@t=50).** This is a critical finding: DDPM at 750k steps shows *moderately concentrated* signal, much more like DDIM-750k than the independent DDPM-800k packet. The DDPM-800k distributed pattern is not a generic DDPM property.

Output: `Research/outputs/h1-fine-grid-ddpm750k/h1_fine_grid_ddpm750k.json`

### Same-Trajectory DDPM 800k (2026-06-25) — Signal INCREASED CONCENTRATION

**Baseline AUC: 0.805** (8 timesteps)

| Site | t=50 | t=100 | t=150 | t=200 | t=300 | t=400 | t=600 | t=800 |
|------|:----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
| **late_down** Δ | +0.031 | +0.108 | +0.095 | +0.108 | +0.107 | +0.140 | +0.076 | **+0.152** |
| **mid_0** Δ | +0.119 | +0.137 | +0.137 | **+0.148** | +0.114 | +0.142 | +0.101 | +0.061 |

**Max individual knockout effect: +0.152 (late_down@t=800), +0.148 (mid_0@t=200).** Continuing the 750k checkpoint to 800k on the same trajectory does not reproduce the independent 800k distributed geometry. It makes the temporal geometry more concentrated.

Output: `Research/outputs/h1-fine-grid-800k-same-trajectory/h1_fine_grid_ddpm800k_st.json`

### Four-Way Comparison

| Metric | DDPM 750k | DDPM 800k independent | DDPM 800k same-trajectory | DDIM 750k |
|--------|:---:|:---:|:---:|:---:|
| Baseline AUC (8t) | 0.751 | 0.833 | 0.805 | 0.854 |
| late_down max Δ | +0.097 | +0.029 | **+0.152** | **+0.221** |
| mid_0 max Δ | +0.080 | +0.024 | **+0.148** | **+0.194** |
| Mean \|Δ\| across grid | 0.049 | 0.012 | 0.107 | 0.146 |
| Knockouts with Δ>0.05 | 8/16 | 0/16 | 15/16 | 16/16 |
| Pattern | Moderate concentration | Distributed | Increased concentration | Strong concentration |

### Comparison: 3-timestep vs 8-timestep Knockout

| Checkpoint | 3-timestep max Δ | 8-timestep max Δ | Ratio |
|------------|:---:|:---:|:---:|
| DDPM 800k late_down | +0.138 | +0.029 | 4.8× |
| DDPM 800k mid_0 | +0.149 | +0.024 | 6.2× |
| DDIM 750k late_down | — | **+0.221** | — |
| DDIM 750k mid_0 | — | **+0.194** | — |

## Interpretation

### 1. The Core Finding (Revised): Training Stage, Procedure, and Run Identity Control Signal Geometry

The DDPM-750k step-matched control and same-trajectory continuation change the interpretation. **DDPM at 750k steps produces moderately concentrated signal, and the same trajectory becomes more concentrated at 800k. The independent DDPM-800k distributed pattern is therefore a run-identity artifact, not a generic late-training or DDPM property.**

This is stronger than the original finding. Temporal geometry is not simply a DDPM-vs-DDIM property. It varies with training stage and run identity: the seed42 same trajectory moves from moderate concentration to increased concentration, while the older independent DDPM-800k packet is distributed and DDIM-750k is strongly concentrated.

### 2. Why This Matters (Revised)

- **For attackers**: DDIM-750k, DDPM-750k, and same-trajectory DDPM-800k all show moderate-to-strong per-timestep knockout effects. The independent DDPM-800k packet alone resists targeted single-cell intervention through temporal redundancy.
- **For defenders**: Temporal redundancy cannot be assumed from algorithm family or training length; it may be trajectory-specific.
- **For methodology**: "Resolution-dependence" varies with training procedure, training duration, and run identity.
- **For the paper**: The original "DDPM distributed, DDIM concentrated" claim was a special case of a more general phenomenon: run-sensitive temporal geometry.

### 3. Mechanistic Hypothesis

- **DDPM**: Training with full stochastic forward process (1000 noise levels) → UNet learns to predict noise at ALL noise levels with equal fidelity → membership signal redundantly encoded across the temporal axis
- **DDIM**: Training with deterministic inference objective (fewer effective steps, non-Markovian forward process) → UNet concentrates its representational capacity at critical denoising stages → membership signal concentrates at those same stages

This hypothesis predicts:
1. The DDIM concentration should be visible in the 3-timestep spatiotemporal grid as well (stronger causal peaks)
2. DDIM late_down and mid_0 should show PER-SITE knockout effects comparable to DDPM 3-timestep effects
3. Other training procedures (e.g., score-based, consistency models) should produce different signal geometries

### 4. Updated Scientific Narrative

**Before DDPM-750k control:**
> "DDPM training yields temporally distributed signal; DDIM training yields concentrated signal."

**After DDPM-750k control and same-trajectory continuation:**
> "Temporal signal geometry varies with training procedure, training stage, and run identity. The seed42 DDPM trajectory is moderately concentrated at 750k and more concentrated at 800k; the independent DDPM-800k distributed geometry is not reproduced on the same trajectory. DDIM at 750k is strongly concentrated. Channel-level distribution (no single channel is causal) remains separate from temporal concentration."

## Cross-Checkpoint Replication Summary (Updated 2026-06-25)

| DAAB Property | DDPM 750k | DDPM 800k independent | DDPM 800k same-trajectory | DDIM 750k | Universal? |
|---------------|:---:|:---:|:---:|:---:|:---:|
| Above-chance signal | yes, 0.648 | yes, 0.872 | yes, 0.717 | yes, 0.856 | yes |
| AUC>0.8 | no | yes | no | yes | no, run-dependent |
| Channel non-localizability | ✅ | ✅ | ✅ | ✅ |
| Full-site knockout gradient | ✅ | ✅ | ✅ | ✅ |
| Spatiotemporal locus (t=100 peak) | partial | yes | shifted/broader | yes | no |
| **Temporal distribution (fine grid)** | Moderate concentration | Distributed | Increased concentration | Strong concentration | no, run-sensitive |
| N=512 raw artifact | present | present | pending archival | present | incomplete |

## Next Steps

1. Archive or re-run same-trajectory DDPM-800k N=512 raw JSON.
2. Complete seed43 to 750k and 800k, then run H1 scout/fine-grid/N=512 gate.
3. Decide seed44 only after seed43 800k results.
4. Keep H4 site-time attenuation behind seed43 fine-grid; do not claim defense effectiveness from knockout deltas alone.

## Sources

- DDPM 8-timestep: inline script (see session transcript)
- DDIM 8-timestep: `scripts/h1/h1_fine_grid_ddim.py`
- DDPM 3-timestep: `outputs/h1-scout/h1_fullsite_knockout.json`
- Main H1 scout: `scripts/h1/h1_activation_scout.py`
- DDIM N=128 scout: `outputs/h1-scout/h1_ddim750k_results.json`
