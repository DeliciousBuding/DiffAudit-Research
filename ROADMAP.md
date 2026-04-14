# DiffAudit Research ROADMAP — 4.19 Competition Sprint

> Last updated: 2026-04-15
> Deadline: 2026-04-19 (Computer Design Competition)
> Hardware: RTX 4070 Laptop 8GB (single GPU) + CPU sidecars

---

## Executive Summary

This roadmap covers **all research directions** for DiffAudit's competition entry. It is designed to be given to an autonomous research agent (Codex GPT-5.4) who will execute GPU runs, explore new methods, and drive the evidence base forward. The agent should use this as a **living document** — updating it as new results come in, new directions emerge, and old directions are resolved.

### Core Philosophy

1. **Evidence first, governance second** — Admitted results matter, but we need *more* admitted results, not more paperwork about existing ones.
2. **GPU time is precious but not sacred** — Every GPU run should answer a real question, but don't let gate-keeping prevent experiments.
3. **Innovation beats replication** — Original ideas and novel combinations beat mechanical reproduction of papers.
4. **Three lines + defenses = complete story** — Black-box, Gray-box, White-box attacks, plus defense comparisons, form the competition narrative.

---

## Part 0: Current Admitted Baselines (DO NOT CHANGE THESE)

These are the fixed reference points. All new work should compare against or complement these:

| Line | Method | Dataset | Best AUC | Status | Notes |
|------|--------|---------|----------|--------|-------|
| Black-box | Recon (DDIM public-100, step30) | CelebA (fine-tuned) | **0.849** | Admitted | Controlled protocol; CopyMark = boundary layer |
| Black-box | Recon (DDIM public-50, step10) | CelebA (fine-tuned) | Best single-metric ref | Admitted | |
| Gray-box | PIA (CIFAR-10, N=8, CPU) | CIFAR-10 | **0.906** | Workspace-verified | N too small; checkpoint/source provenance blocked |
| White-box | GSA (CIFAR-10, 1k-3shadow, epoch300) | CIFAR-10 | **0.489** (rerun1) | Admitted | Toy-ish; needs real checkpoints |
| Exploratory | SMP-LoRA | Various | ~0.63 max | Exploratory | O03/O04/no-TF32 all failed; T06 optimizer/lr pending |
| Defense | PIA stochastic dropout | CIFAR-10 | No improvement | Prototype | Only shifts threshold, no ranking improvement |

### Key External Assets Available

- `external/recon-assets/` — NDSS 2025 black-box checkpoints (CelebA shadow/target, partial variants)
- `external/PIA/` — PIA implementation (DDPM, GradTTS, Stable Diffusion variants)
- `external/SecMI/` — SecMI implementation (CIFAR-10 splits included)
- `external/CLiD/` — CLiD implementation (CLIP-based, SD training code)
- `external/Reconstruction-based-Attack/` — BLIP + LoRA reconstruction attack
- `external/DiT/` — DiT diffusion implementation
- `external/DPDM/` — DPDM defense implementation
- `workspaces/white-box/external/GSA/` — GSA upstream code (DDPM + Imagen)

---

## Part 1: Black-box Lines (Expand & Strengthen)

### B1: Recon (Current Mainline) — OPTIMIZATION

**Status**: AUC 0.849 is solid but could be higher. The DDIM protocol has room for hyperparameter tuning.

**Open Questions**:
- What timestep range [5, 50] gives best AUC? Current uses step30 for main, step10 for best-metric.
- Does increasing shadow model count from 3 improve attack signal?
- Can we combine multiple timesteps into an ensemble score?
- What about varying the DDIM eta parameter (between DDIM and DDPM)?
- Can we use different reconstruction loss functions (LPIPS vs L2 vs L1)?

**GPU Tasks**:
- `B1-G1`: Timestep sweep [5, 10, 15, 20, 25, 30, 40, 50] on existing recon assets. Budget: 2-4 GPUh.
- `B1-G2`: Shadow count comparison [3, 5, 7] at optimal timestep. Budget: 3-6 GPUh.
- `B1-G3`: DDIM eta sweep [0.0, 0.25, 0.5, 0.75, 1.0] to understand DDIM↔DDPM transition effect. Budget: 2-4 GPUh.
- `B1-G4`: LPIPS perceptual loss vs L2 reconstruction. May improve semantic alignment. Budget: 2 GPUh.

**CPU Tasks**:
- Error slice analysis: which samples are misclassified? Is there a pattern (e.g., image complexity, frequency content)?
- Integrate frequency-domain paper insights: do high-frequency samples have lower attack scores?
- Cost analysis: query complexity vs AUC tradeoff curve.

### B2: CLiD (NeurIPS 2024) — NEW BLACK-BOX LINE

**Status**: Code exists in `external/CLiD/` and `src/diffaudit/attacks/clid.py`. Uses CLIP features for membership inference on text-to-image diffusion models. **Has not been executed yet.**

**Why CLiD matters**:
- Independent black-box method from Recon — if both show signals, the evidence is much stronger.
- Uses a completely different mechanism (CLIP feature space vs reconstruction error).
- Can run on the same CelebA assets as Recon for direct comparison.
- NeurIPS 2024 publication adds credibility.

**GPU Tasks**:
- `B2-G1`: CLiD smoke test on existing recon assets (CelebA fine-tuned). Adapt CLiD's pipeline to use our model checkpoints. Budget: 2-4 GPUh.
- `B2-G2`: Full CLiD run with proper member/non-member split. Compare AUC directly with Recon. Budget: 4-8 GPUh.
- `B2-G3`: CLiD + Recon ensemble: does combining CLIP features + reconstruction error improve AUC beyond either alone? Budget: 2 GPUh.

**CPU Tasks**:
- Asset compatibility analysis: can CLiD's code consume our CelebA checkpoints directly?
- Threat model comparison: how does CLiD's assumptions differ from Recon?
- If CLiD fails: diagnose why (CLIP model compatibility? feature extraction pipeline?)

### B3: Variation / Towards (API-only) — UNBLOCK

**Status**: Code exists but blocked by real API asset availability. Has run synthetic smoke on CPU.

**Open Questions**:
- Can we simulate API responses using our local models? (i.e., treat local model outputs as "API responses")
- What minimal API surface is needed? (just image generation? or also loss scores?)
- Can we adapt the variation attack to work in a "local API" mode against our own models?

**Tasks**:
- `B3-C1`: Implement "local API wrapper" that exposes our Recon DDIM model as a generation-only API.
- `B3-G1`: Run variation attack against local API wrapper. Budget: 2 GPUh.

### B4: Novel Black-box Ideas — INNOVATION

**Don't be limited by existing papers. Think about what's unique about diffusion models and how to exploit it:**

**Brainstorming Directions**:
1. **Noise trajectory analysis**: Can we distinguish member vs non-member by analyzing how the denoising trajectory differs? Members might have "smoother" or "more confident" denoising paths.
2. **Output variance across timesteps**: Do member samples show more consistent outputs when noise is re-sampled at different timesteps?
3. **Prompt sensitivity**: For text-conditioned models, do member images respond differently to prompt perturbations?
4. **Classifier-free guidance scale**: Does varying the CFG scale reveal different membership signals?
5. **Cross-model agreement**: If we have multiple fine-tuned models, do members get consistently "better" reconstructions across all of them?
6. **Latent space analysis**: Can we detect membership in the latent space of autoencoder-based diffusion models (e.g., Stable Diffusion's VAE)?
7. **Temporal consistency**: For iterative generation, does the intermediate output sequence differ between members and non-members?

**GPU/CPU Tasks**:
- `B4-X1`: Pick 2-3 most promising ideas above and prototype them. Start with CPU-friendly probes.
- `B4-X2`: For any idea that shows signal on small samples, design a proper GPU experiment.
- `B4-X3**: Write up negative results too — knowing what *doesn't* work is valuable for the competition defense.

---

## Part 2: Gray-box Lines (Expand & Validate)

### G1: PIA (Current Mainline) — SCALE UP

**Status**: AUC 0.906 on N=8 is promising but sample size is too small for competition. Needs N≥50 validation.

**Critical Open Questions**:
- Does AUC hold at N=50? N=100? Or does it drop with more samples?
- What's the optimal attack_num and interval for CIFAR-10 DDPM?
- Can we get meaningful results on 8GB with smart batching?
- How does the proximal initialization parameter (the key PIA innovation) affect results?

**GPU Tasks**:
- `G1-G1`: **Priority #1** — PIA on CIFAR-10 with N=50. Use existing DDPM checkpoint. Budget: 4-8 GPUh.
- `G1-G2**: PIA with N=100 if G1-G1 succeeds. Budget: 8-12 GPUh.
- `G1-G3**: Proximal initialization ablation: vary the proximal weight [0.1, 0.3, 0.5, 0.7, 0.9] to find optimal setting. Budget: 3-5 GPUh.
- `G1-G4**: PIA on Stable Diffusion variant (if assets available). Does PIA transfer to latent diffusion? Budget: 8-16 GPUh.

**Defense Tasks** (run alongside attack tasks):
- `G1-D1**: DP-SGD training on CIFAR-10 DDPM, then run PIA attack. Does DP help? Budget: 4-8 GPUh for training + 2-4h for attack.
- `G1-D2**: Stochastic dropout defense (already prototyped) — re-run with N=50 for proper evaluation. Budget: 2 GPUh.
- `G1-D3**: Noise injection defense — add calibrated noise during inference and measure attack degradation. Budget: 1-2 GPUh.

**CPU Tasks**:
- Checkpoint provenance: track down the exact DDPM checkpoint source, training config, and member split generation process.
- If the checkpoint is self-trained: document the full training recipe so competitors can reproduce.
- If the checkpoint is from upstream: verify the member split matches the paper's protocol.

### G2: SecMI (ICML 2023) — UNBLOCK & RUN

**Status**: Code in `external/SecMI/` and `src/diffaudit/attacks/secmi.py`. Has CIFAR-10 member splits. **Has never been executed.** Based on FID/MMD distribution distance — potentially CPU-runnable.

**Why SecMI matters**:
- Completely different mechanism from PIA (distribution distance vs proximal optimization).
- If both SecMI and PIA show signals on CIFAR-10, gray-box has two independent confirmation lines.
- May not need GPU — uses ResNet feature extractor + statistical tests.
- ICML 2023 publication.

**GPU Tasks**:
- `G2-G1`: SecMI on CIFAR-10 with existing splits. Start with CPU probe first. If ResNet feature extraction needs GPU, budget: 2-4 GPUh.

**CPU Tasks**:
- `G2-C1`: SecMI smoke test on CPU. Check if the ResNet feature extractor runs on CPU with acceptable speed.
- `G2-C2`: Asset validation: verify CIFAR-10 splits in `external/SecMI/mia_evals/member_splits/` are compatible with our setup.
- `G2-C3`: If SecMI runs on CPU, run full pipeline and compare with PIA results.

### G3: SIMA (Score-based) — NEW GRAY-BOX LINE

**Status**: Paper exists (`2025-arxiv-sima-score-based-membership-inference-diffusion-models`). Uses score-based methods for membership inference. **No code implementation yet.**

**Why SIMA matters**:
- Score-based approach is fundamentally different from both PIA and SecMI.
- Could be the third independent gray-box line.
- May work well on the same CIFAR-10 assets.

**Tasks**:
- `G3-C1`: Read and summarize the SIMA paper. Extract the core algorithm, asset requirements, and expected outputs.
- `G3-C2`: Implement a minimal SIMA prototype based on the paper. Can we reuse components from PIA's diffusion code?
- `G3-G1`: If prototype shows promise, run on CIFAR-10. Budget: TBD after implementation.

### G4: MoFit (2026, Caption-free) — EVALUATE

**Status**: Paper exists (`2026-openreview-mofit-caption-free-membership-inference`). Caption-free approach — doesn't need text descriptions.

**Tasks**:
- `G4-C1`: Paper reading and feasibility assessment. Does MoFit work on image-only diffusion models?
- `G4-C2**: If feasible, outline implementation plan.

### G5: Noise-as-a- Probe (2026) — EVALUATE

**Status**: Paper exists (`2026-arxiv-noise-as-a-probe-membership-inference-diffusion-models`). Uses noise injection as a probing mechanism.

**Tasks**:
- `G5-C1`: Paper reading and feasibility assessment.
- `G5-C2**: Could this be combined with PIA? (Use noise injection to enhance PIA's proximal signal.)

### G6: Novel Gray-box Ideas — INNOVATION

**Gray-box = partial model access. What can we do with gradients, intermediate activations, or limited parameter access?**

**Brainstorming Directions**:
1. **Gradient norm analysis**: Do member samples produce different gradient norms during fine-tuning? Simple but potentially effective.
2. **Activation pattern clustering**: Do member samples cluster differently in activation space compared to non-members?
3. **Layer-wise sensitivity**: Which layers of the diffusion model are most informative for membership inference? Can we do layer-by-layer analysis?
4. **Training checkpoint comparison**: Compare model weights before and after fine-tuning on specific samples. Do members leave larger "traces"?
5. **Score function analysis**: The denoising score function might behave differently on members vs non-members. Can we measure this directly?
6. **Fine-tuning trajectory**: Track how the model changes during fine-tuning. Do member samples get "learned" faster?
7. **Cross-sample interaction**: Does the presence of one member affect the attack signal on another member? (Interference effects)

**Tasks**:
- `G6-X1`: Pick 2-3 most promising ideas. Prototype on CPU with existing CIFAR-10 assets.
- `G6-X2`: For any idea showing signal, design proper GPU experiment.

---

## Part 3: White-box Lines (Close the Gap)

### W1: GSA (Current Mainline) — REAL ASSETS RUN

**Status**: End-to-end pipeline works but only on toy synthetic data (N=6 per split). AUC on toy data is meaningless. **The biggest gap in our research.**

**What's Needed**:
1. **Real checkpoints**: Train target and shadow DDPM models on CIFAR-10 with proper member/non-member splits.
2. **Proper scale**: N≥100 per split (member and non-member, target and shadow).
3. **Paper-aligned protocol**: Match the GSA paper's training setup as closely as possible.

**GPU Tasks**:
- `W1-G1`: **Priority #2** — Train DDPM on CIFAR-10 for target model. Budget: 8-16 GPUh (depending on convergence).
- `W1-G2`: Train 3 shadow models on CIFAR-10 (different random splits). Budget: 24-48 GPUh total.
- `W1-G3**: Run GSA gradient extraction on real checkpoints. Budget: 4-8 GPUh.
- `W1-G4**: Train XGBoost attack model and evaluate. Budget: 1-2 GPUh (or CPU).

**Alternative Approach** (if full training is too expensive):
- Use pre-trained DDPM checkpoints from HuggingFace or other sources.
- Fine-tune on small CIFAR-10 subsets to create "target" vs "shadow" distinction.
- This is faster than training from scratch but still gives real gradient signals.

**CPU Tasks**:
- `W1-C1`: Survey available pre-trained DDPM checkpoints. Can we find compatible ones?
- `W1-C2`: If using pre-trained: design the fine-tuning protocol to create proper member/non-member splits.
- `W1-C3`: XGBoost attack model training can run on CPU once gradients are extracted.

### W2: GSA Improvements — INNOVATION

**Beyond the baseline GSA paper, what can we improve?**

**Ideas**:
1. **Better gradient features**: Instead of raw L2 gradients, can we use normalized gradients, gradient directions, or gradient statistics?
2. **Multi-timestep gradients**: GSA uses gradients at a single timestep. What if we aggregate gradients across multiple timesteps?
3. **Layer-specific analysis**: Which UNet layers carry the most membership signal? Can we focus on those layers?
4. **Non-XGBoost classifiers**: Try neural network classifiers on gradient features. Might capture non-linear patterns better.
5. **Gradient ensembling**: Combine gradients from multiple noise levels or multiple generation steps.

**Tasks**:
- `W2-X1`: For any idea above that seems promising, prototype on the existing toy data first (fast iteration).
- `W2-X2**: If toy data shows signal, include in the real-asset GSA run.

### W3: Finding NeMo (NeurIPS 2024) — EVALUATE & INTEGRATE

**Status**: Adapter is implemented but on zero-GPU hold. Paper about localizing memorization neurons in diffusion models.

**Why NeMo matters**:
- Complements GSA: GSA is gradient-based, NeMo is neuron-based. Two different white-box approaches.
- Could provide a completely different type of white-box evidence.
- The "memorization neuron" concept is intuitive for competition presentation.

**Tasks**:
- `W3-C1`: Review the existing adapter implementation. What's blocking execution?
- `W3-C2**: If the blocker is asset-related, design a minimal execution path with available assets.
- `W3-G1**: Minimal smoke test on CIFAR-10 with existing DDPM checkpoint. Budget: 2-4 GPUh.

### W4: Local Mirror (2025 PoPETS) — EVALUATE

**Status**: Paper exists (`2025-local-mirror-white-box-membership-inference-diffusion-models`). **No code yet.**

**Tasks**:
- `W4-C1`: Paper reading and feasibility assessment.
- `W4-C2**: Compare with GSA: does Local Mirror offer something GSA doesn't?
- `W4-C3**: If promising, sketch implementation plan.

### W5: Novel White-box Ideas — INNOVATION

**White-box = full model access. What creative attacks become possible?**

**Brainstorming Directions**:
1. **Hessian-based analysis**: Do member samples have different loss landscape curvature? The Hessian (second derivatives) might reveal memorization.
2. **Influence functions**: Classic ML technique — compute how much each training point affects the model's predictions on test points.
3. **Training data extraction**: Instead of just detecting membership, can we partially reconstruct training data from model weights? (More dramatic for competition.)
4. **Neuron activation patterns**: Do specific neurons fire differently for member vs non-member samples?
5. **Weight differential analysis**: Compare a fine-tuned model with its pre-trained version. Which weights changed most? Do those weights correlate with member data?
6. **Attention map analysis**: For transformer-based diffusion models (DiT), do attention patterns differ for members?
7. **Gradient flow visualization**: Visualize how gradients propagate through the network for member vs non-member samples.

**Tasks**:
- `W5-X1`: Pick 2-3 most visually compelling ideas (competition judges like visualizations!).
- `W5-X2`: Prototype on existing toy data for fast iteration.
- `W5-X3**: For ideas that work, integrate with real-asset GSA pipeline.

---

## Part 4: Defense Lines (Critical for Competition)

**The competition judges WILL ask: "How do you defend against these attacks?"** We need systematic defense comparisons.

### D1: DP-SGD Training

**What**: Train diffusion models with Differential Privacy (DP-SGD).
**Expected**: Higher privacy budget (epsilon) = weaker attack, lower utility.

**GPU Tasks**:
- `D1-G1`: Train CIFAR-10 DDPM with DP-SGD at epsilon = [1, 5, 10, 50, 100]. Budget: 8-16 GPUh total.
- `D1-G2**: Run all three attack lines (Recon, PIA, GSA) on each DP model. Budget: 8-16 GPUh.
- `D1-G3**: Plot Privacy-Utility Tradeoff (PUT) curve: attack AUC vs model quality (FID).

### D2: Gradient Obfuscation

**What**: Modify gradients during white-box access (gradient clipping, noise addition, quantization).
**Expected**: Obfuscation reduces GSA attack strength.

**GPU/CPU Tasks**:
- `D2-G1`: Implement gradient noise injection as a defense wrapper around GSA gradient extraction. Budget: 1-2 GPUh.
- `D2-C1**: Implement gradient clipping defense. Run on CPU with existing gradient artifacts.
- `D2-C2**: Compare multiple obfuscation methods side by side.

### D3: Detection-based Defense

**What**: Detect and block attack queries (e.g., unusual query patterns, repeated sampling).
**Expected**: Attack success rate drops if attack queries are detected.

**Tasks**:
- `D3-C1`: Analyze attack query patterns from Recon/PIA/GSA. What makes them detectable?
- `D3-C2**: Implement simple detection rules (query count, input distribution).
- `D3-G1**: Test detection effectiveness against our own attacks.

### D4: Model Modification Defense

**What**: Modify the model post-training to reduce memorization (e.g., unlearning, fine-tuning on non-member data).
**Expected**: Attack signal weakens without significant utility loss.

**GPU Tasks**:
- `D4-G1**: Fine-tune CIFAR-10 DDPM on a held-out non-member set ("defensive fine-tuning"). Budget: 4-8 GPUh.
- `D4-G2**: Run PIA before and after defensive fine-tuning. Budget: 4 GPUh.

### D5: Defense Comparison Table

**Goal**: Produce a comprehensive defense comparison table for the competition.

| Defense | Recon AUC | PIA AUC | GSA AUC | FID | Training Cost |
|---------|-----------|---------|---------|-----|---------------|
| None (baseline) | 0.849 | 0.906 | TBD | TBD | - |
| DP-SGD (eps=10) | ? | ? | ? | ? | ? |
| DP-SGD (eps=50) | ? | ? | ? | ? | ? |
| Gradient Noise | - | - | ? | - | - |
| Defensive FT | ? | ? | ? | ? | ? |
| Dropout | 0.906* | 0.906* | - | ? | - |

---

## Part 5: Cross-cutting Research

### X1: Unified Evidence Table

**Goal**: All results from all lines should feed into a single comparison table.

**Schema** (expand existing `result-schema.md`):
```json
{
  "run_id": "unique identifier",
  "track": "black-box | gray-box | white-box",
  "method": "recon | pia | gsa | clid | secmi | ...",
  "dataset": "CIFAR-10 | CelebA | ...",
  "model": "DDPM | DDIM | SD1.5 | ...",
  "member_n": 100,
  "non_member_n": 100,
  "shadow_n": 3,
  "metrics": {
    "auc": 0.85,
    "asr": 0.82,
    "tpr_at_1pct_fpr": 0.75,
    "tpr_at_0_1pct_fpr": 0.65
  },
  "cost": {
    "gpu_hours": 4.5,
    "api_queries": 1000,
    "memory_gb": 6.2
  },
  "defense": "none | dp-sgd-eps10 | ...",
  "device": "RTX4070-8GB",
  "timestamp": "2026-04-15T...",
  "status": "admitted | candidate | blocked",
  "notes": "..."
}
```

### X2: Attack-Defense Matrix

**Goal**: For each attack line, show how different defenses affect the result. This is the most important table for the competition.

### X3: Threat Model Comparison

**Goal**: Clearly document what access each attack line requires, so judges can understand the practical implications.

| Attack | Model Access | Data Access | Compute | AUC |
|--------|-------------|-------------|---------|-----|
| Recon | API only (generation) | Query budget | Medium | 0.849 |
| CLiD | API only (generation) + CLIP | Query budget | Medium | ? |
| PIA | Weights + gradients | Training split info | High | 0.906 |
| SecMI | Weights | Feature extractor | Low-Medium | ? |
| GSA | Full weights + gradients | Shadow datasets | Very High | ? |

### X4: Novel Research Ideas — Think Beyond Papers

**The competition rewards originality. Don't just reproduce papers — create new insights.**

**Directions to explore**:
1. **Attack transferability**: Does an attack that works on DDPM also work on DiT? On Stable Diffusion? On Kandinsky?
2. **Dataset dependence**: Are some datasets more vulnerable? (CIFAR-10 vs CelebA vs LSUN)
3. **Model size scaling**: Do larger models leak more or less membership information?
4. **Fine-tuning depth**: How many fine-tuning steps until membership signal appears? Is there a "danger zone"?
5. **Combined attack scoring**: Can we combine scores from multiple attacks into a super-attack? (e.g., Recon score + PIA score + GSA score → ensemble)
6. **Temporal attack evolution**: How does the attack signal evolve during fine-tuning? (snapshot the model every N steps and run the attack)
7. **Adversarial defense**: Can an adversary specifically craft non-member samples that look like members to confuse the attack?

---

## Part 6: Execution Priority

### Immediate Priorities (4.15 - 4.17)

1. **W1-G1/G2**: Train real DDPM checkpoints for GSA. This is the biggest gap. If full training takes too long, use pre-trained + fine-tune approach.
2. **G1-G1**: PIA on N=50 CIFAR-10. Scale up from N=8 to get competition-grade results.
3. **B2-G1**: CLiD smoke test. Quick win — if it works, we get a second black-box line immediately.
4. **G2-C1/G2-G1**: SecMI on CIFAR-10. May run on CPU, making it a free data point.

### Secondary Priorities (4.17 - 4.18)

5. **D1-G1**: DP-SGD training + attack comparison. Defense results are critical for competition.
6. **B1-G1**: Recon timestep sweep. Optimize the existing mainline.
7. **W1-G3/G4**: GSA on real checkpoints. Complete the white-box line.
8. **G1-D1/D2**: PIA defense comparison.

### Final Push (4.18 - 4.19)

9. **X1/X2/X3**: Compile all results into unified tables.
10. Any remaining GPU tasks that showed promise in earlier stages.
11. Write competition materials: evidence summary, methodology, defense analysis.

---

## Part 7: GPU Budget Summary

| Task | Priority | Est. GPUh | Status |
|------|----------|-----------|--------|
| W1-G1: DDPM target training | P0 | 8-16 | Not started |
| W1-G2: 3x shadow training | P0 | 24-48 | Not started |
| G1-G1: PIA N=50 | P0 | 4-8 | Not started |
| B2-G1: CLiD smoke | P1 | 2-4 | Not started |
| G2-G1: SecMI | P1 | 0-4 (maybe CPU) | Not started |
| D1-G1: DP-SGD training | P1 | 8-16 | Not started |
| B1-G1: Recon timestep sweep | P2 | 2-4 | Not started |
| W1-G3: GSA gradient extraction | P2 | 4-8 | Not started |
| G1-G2: PIA N=100 | P2 | 8-12 | Depends on G1-G1 |
| B2-G2: CLiD full run | P2 | 4-8 | Depends on B2-G1 |
| G1-D1: PIA DP defense | P2 | 4-8 | Not started |
| D1-G2: Attack all DP models | P2 | 8-16 | Depends on D1-G1 |
| **Total** | | **76-156 GPUh** | |

**Reality check**: RTX 4070 8GB, ~156 GPUh total. At 24h/day (plugged in), that's ~6.5 days. Competition is 4.19, so we have 4 days = 96 GPUh. **We must be selective.**

**Recommended cut**: Focus on P0 + select P1. Skip P2 unless P0 tasks finish early.
- P0 only: ~38-76 GPUh (2-3 days, feasible)
- P0 + P1: ~54-96 GPUh (3-4 days, tight but possible)
- Everything: 76-156 GPUh (not feasible before 4.19)

---

## Part 8: Autonomous Agent Instructions

**This section is for the Codex research agent. Read carefully.**

### Your Role

You are a research scientist working on DiffAudit, a diffusion model membership inference audit platform. Your job is to:

1. **Execute experiments** from this roadmap (GPU runs on RTX 4070 8GB)
2. **Explore new ideas** not listed here — use your judgment to find high-value directions
3. **Update this document** as you make progress — cross out completed tasks, add new findings
4. **Write results** to `workspaces/<track>/runs/` with proper `summary.json` format
5. **Be creative** — don't just follow the roadmap blindly. If you see a better direction, take it.

### Your Constraints

- **Hardware**: Single RTX 4070 8GB laptop GPU. Be memory-efficient. Use `--batch-size`, gradient checkpointing, mixed precision.
- **Time**: Competition deadline 2026-04-19. Prioritize high-impact experiments.
- **Assets**: Use existing checkpoints and datasets in `external/` and `workspaces/` directories.
- **Reproducibility**: Every run should have a config, seed, and clear provenance.

### Your Freedom

- **You can deviate from this roadmap.** If you find a better approach, document it and pursue it.
- **You can combine methods.** If PIA + SecMI ensemble seems promising, try it.
- **You can implement new attacks.** If you read a paper and think "this would work great here," implement it.
- **You can skip tasks.** If a task seems low-value after investigation, mark it as skipped with reasoning.
- **You should invent.** The best competition entries have something novel. Find it.

### Reporting Format

For each experiment, write:

```markdown
## Experiment: <name>
- Date: YYYY-MM-DD
- Track: black-box | gray-box | white-box | defense
- GPU hours used: X.X
- Dataset: ...
- Model: ...
- Method: ...
- Results: { auc: X, asr: Y, ... }
- Status: admitted | candidate | failed | no-go
- Notes: ...
```

Then update `summary.json` in the appropriate `workspaces/<track>/runs/<run-name>/` directory.

---

## Part 9: Competition Readiness Checklist

By 2026-04-19, we need:

- [ ] Black-box: At least 1 strong result (Recon AUC ≥ 0.85) + preferably 2nd line (CLiD)
- [ ] Gray-box: PIA N≥50 result with stable AUC + preferably SecMI confirmation
- [ ] White-box: GSA on real checkpoints with meaningful AUC (not toy data)
- [ ] Defense: At least 2 defense methods compared against main attacks
- [ ] Unified evidence table with all results
- [ ] Attack-defense comparison matrix
- [ ] Threat model comparison table
- [ ] Competition presentation materials

---

## Appendix: Paper Library

### Black-box Papers
- 2025-NDSS: Black-box membership inference fine-tuned diffusion models (Recon) — **ADMITTED**
- 2024-NeurIPS: CLiD membership inference text-to-image diffusion — **CODE READY**
- 2024-ArXiv: Towards black-box membership inference diffusion models (Variation) — **BLOCKED**
- 2025-VISAPP: Membership inference face fine-tuned latent diffusion — **READ ONLY**

### Gray-box Papers
- 2024-ICLR: PIA proximal initialization — **ADMITTED, NEEDS SCALE-UP**
- 2023-ICML: SecMI membership inference diffusion models — **CODE READY, NOT RUN**
- 2025-ArXiv: SIMA score-based membership inference — **PAPER READ**
- 2026-OpenReview: MoFit caption-free membership inference — **PAPER READ**
- 2026-ArXiv: Noise-as-a-probe membership inference — **PAPER READ**
- 2024-ArXiv: SIDe extracting training data unconditional diffusion — **PAPER READ**
- 2024-ArXiv: Structural memorization membership inference — **PAPER READ**

### White-box Papers
- 2025-PoPETS: White-box membership inference diffusion models (GSA) — **ADMITTED, TOY DATA**
- 2024-NeurIPS: Finding NeMo localizing memorization neurons — **ADAPTER READY**
- 2025-Local Mirror: White-box membership inference diffusion models — **PAPER READ**

### Defense Papers
- 2025-NDSS: Diffence fencing membership privacy diffusion models — **PAPER READ**
- 2025-AAAI: Privacy-preserving LoRA membership inference LDM — **PAPER READ**
- 2024-ArXiv: Dual model defense diffusion membership inference — **PAPER READ**
- 2025-ArXiv: Defending diffusion models membership inference higher-order Langevin — **PAPER READ**
- DPDM — **CODE READY**

### Survey Papers
- 2025-NeurIPS: Tracing the roots origin attribution diffusion trajectories — **REPORT DONE**
- Survey index: diffusion privacy literature — **DONE**

---

## Changelog

| Date | Change |
|------|--------|
| 2026-04-15 | Complete rewrite: competition sprint roadmap, expanded all lines, added innovation directions |
| 2026-04-09 | Previous governance-focused version (archived) |
