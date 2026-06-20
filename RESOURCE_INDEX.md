# DiffAudit Research -- Resource Index

> **SSOT for datasets, checkpoints, scripts, results, and experiment planning.**
> Last updated: 2026-06-20
> Auto-derived from `outputs/catalog_checkpoints.json`, `outputs/dataset_checkpoint_matrix.json`, `scripts/build_compatibility_matrix.py`, `scripts/catalog_checkpoints.py`, and live directory scans.

---

## 1. Dataset x Checkpoint Compatibility Matrix

**Legend:**
| Symbol | Meaning |
|---|---|
| `[OK]` | Compatible AND tested (results available) |
| `[UNTESTED]` | Compatible but UNTESTED (runnable, no results) |
| `[CLOSED]` | Direction closed (weak results, route blocked by governance) |
| `[NO]` | Incompatible (format / dataset / resolution / model-family mismatch) |

### Matrix

| Dataset | DDPM-CIFAR10-800k | DDPM-CIFAR100-800k | DDIM-CIFAR10-750k | GuidedDiff-CIFAR10-500k | DDPM-STL10-final | DDPM-STL10-99k | DDPM-STL10-overfit-* | Beans-LoRA-SD15 | NDSS-2025-derived | SD-v1-4-CompVis |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **CIFAR-10** | `[OK]` | `[NO]` | `[OK]` | `[UNTESTED]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` |
| **CIFAR-100** | `[NO]` | `[OK]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` |
| **STL-10** | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[CLOSED]` | `[UNTESTED]` | `[UNTESTED]` | `[NO]` | `[NO]` | `[NO]` |
| **Fashion-MNIST** | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` |
| **Beans** | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[CLOSED]` | `[UNTESTED]` | `[UNTESTED]` |
| **CelebA** | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[NO]` | `[UNTESTED]` | `[UNTESTED]` |

### Key Observations

1. **CIFAR-10 x DDPM-800k** is the most-tested pair: SecMI, PIA, gray-box tri-score, H2 sidecar, activation scouts.
2. **CIFAR-10 x DDIM-750k** has H1 channel-knockout + checkpoint-portability gate, but no full SecMI 25k/25k.
3. **CIFAR-100 x DDPM-CIFAR100-800k** has H1 activation scouts only; no SecMI/PIA/tri-score yet.
4. **STL-10 x DDPM-STL10-final** is closed: both ReDiffuse and SimA scouts returned random-level AUC.
5. **STL-10 overfit variants** (m500/m1000/m2000) are UNTESTED -- overfit regime may yield stronger signal.
6. **Fashion-MNIST** has 3 weak known-split scouts (PIA-style, SimA, score-Jacobian). No DDPM checkpoint persisted locally.
7. **Beans-LoRA-SD15** is CLOSED: membership provenance not proven for SD1.5 train/val.
8. **GuidedDiff-CIFAR10-500k** loads in ReDiffuse but has a different UNet architecture (OpenAI guided-diffusion format).

---

## 2. Dataset Inventory

Every dataset with location, provenance, and membership ground-truth status.

### Primary Datasets (Active Research)

| Dataset | Resolution | Member Ground Truth | Status | Data Path |
|---|---|---|---|---|
| **CIFAR-10** | 32x32x3 | PROVEN: train=50k, test=10k | `research-ready` | `Download/shared/datasets/cifar-10-python.tar.gz`; `data/datasets/pytorch/cifar10/` (symlink to PIA upstream) |
| **CIFAR-100** | 32x32x3 | PROVEN: train=50k, test=10k | `research-ready` | `Download/shared/datasets/cifar-100-python.tar.gz`; `data/datasets/pytorch/cifar-100-python/` |
| **STL-10** | 96x96x3 | PROVEN: train=5k, test=8k, unlabeled=100k + fold_indices | `research-ready` | `Download/shared/datasets/stl10_binary/`; `data/datasets/pytorch/stl10/` |
| **Fashion-MNIST** | 28x28x1 | PROVEN: train=60k, test=10k | `asset-ready` | Raw folder (no local DDPM checkpoint persisted) |
| **Beans** | variable (512x512 for SD1.5) | NOT PROVEN for SD1.5 membership | `hold-membership-blocked` | HF datasets `beans` |
| **CelebA** | 178x218 | PARTITION exists (train/val/test), no diffusion checkpoint trained on known splits | `hold-membership-blocked` | `Download/shared/datasets/celeba/` |

### Member/Nonmember Split Files

| Dataset | Split File | Location | Size |
|---|---|---|---|
| CIFAR-10 | `CIFAR10_train_ratio0.5.npz` | `Research/data/splits/CIFAR10_train_ratio0.5.npz` | 392 KB (25k member / 25k nonmember) |
| CIFAR-100 | `CIFAR100_train_ratio0.5.npz` | `Research/data/splits/CIFAR100_train_ratio0.5.npz` | 392 KB (25k member / 25k nonmember) |
| STL-10 | `STL10_train_ratio0.5.npz` | `Research/data/splits/STL10_train_ratio0.5.npz` | 782 KB (50k member / 50k nonmember) |
| CIFAR-10 | `cifar10_member_25k.pt` | `Download/shared/datasets/cifar10_member_25k.pt` | -- |
| STL-10 | `stl10_member_50k.pt` | `Download/shared/datasets/stl10_member_50k.pt` | -- |

### Shared Weights (Foundation Models)

| Asset ID | Description | Source | Local Path |
|---|---|---|---|
| `SH-WT-01` | Stable Diffusion v1.5 | HuggingFace `stable-diffusion-v1-5/stable-diffusion-v1-5` | `Download/shared/weights/stable-diffusion-v1-5/` |
| `SH-WT-02` | CLIP ViT-L/14 | HuggingFace `openai/clip-vit-large-patch14` | `Download/shared/weights/clip-vit-large-patch14/` |
| `SH-WT-03` | BLIP large | HuggingFace `Salesforce/blip-image-captioning-large` | `Download/shared/weights/blip-image-captioning-large/` |
| `SH-WT-04` | DDPM CIFAR-10 32 | HuggingFace `google/ddpm-cifar10-32` | `Download/shared/weights/google-ddpm-cifar10-32/` |

### Downstream Supplementary Assets

| Asset ID | Content | Local Path |
|---|---|---|
| `GB-WT-01` | SecMI CIFAR bundle (DDPM-800k checkpoints) | `Download/gray-box/weights/secmi-cifar-bundle/` |
| `GB-SUP-02` | SecMI member split `.npz` files | `Download/gray-box/supplementary/secmi-member-splits/` |
| `BB-SUP-02` | CLiD supplementary mirror | `Download/black-box/supplementary/clid-mia-supplementary/` |
| `BB-RECON` | Recon bundle (NDSS-2025 black-box MIA) | `Download/black-box/supplementary/recon-assets/` |
| `GB-PIA` | PIA upstream dataset assets | `Download/gray-box/supplementary/pia-upstream-assets/` |
| `CelebA 7z` | CelebA image 7z parts | `Download/shared/supplementary/celeba-7z-parts/` |
| `DDIM-STL10` | Collaborator DDIM STL10 bundle | `Download/shared/supplementary/collaborator-ddim-stl10-20260527/` |

---

## 3. Checkpoint Inventory

Every model checkpoint, architecture, format, and compatibility.

### DDPM Checkpoints (Rediffuse-UNet format, 128/256 channels, ~548 MB each)

| Checkpoint | Dataset | Step | Format | ReDiffuse-Loadable | Key Experiments | Location Pattern |
|---|---|---|---|---|---|---|
| **DDPM-CIFAR10-800k** | CIFAR-10 | 800,000 | rediffuse-unet | Yes | SecMI/PIA E3 eval, H2 sidecar, gray-box tri-score, activation scout | `Download/gray-box/weights/secmi-cifar-bundle/` (3 copies) |
| **DDPM-CIFAR100-800k** | CIFAR-100 | 800,000 | rediffuse-unet | Yes | H1 channel knockout, activation fine-grid | `Download/gray-box/weights/secmi-cifar-bundle/` (2 copies) |
| **DDPM-STL10-final** | STL-10 | final | rediffuse-unet | Yes | Smoke test, ReDiffuse bounded scout (AUC=0.4996, closed), SimA (AUC=0.5053, closed) | `Research/tmp/` |
| **DDPM-STL10-99k** | STL-10 | 99,000 | rediffuse-unet | Yes | Collaborator DDPM, UNTESTED | `Download/shared/supplementary/collaborator-ddim-stl10-20260527/` |

### STL-10 Overfit Checkpoints (Rediffuse-UNet, 128/256 channels, ~548 MB each)

| Checkpoint | Members | Seed | Step | Status |
|---|---|---|---|---|
| DDPM-STL10-overfit-m500-9k | 500 | 1 | 9,000 | `[UNTESTED]` |
| DDPM-STL10-overfit-m1000-9k | 1,000 | 0 | 9,000 | `[UNTESTED]` |
| DDPM-STL10-overfit-m1000-5k | 1,000 | -- | 5,000 | `[UNTESTED]` (continued from 15k/20k/25k base) |
| DDPM-STL10-overfit-m2000-8k | 2,000 | 0 | 8,000 | `[UNTESTED]` |

### Non-DDPM Checkpoints

| Checkpoint | Format | Dataset | Size | Note |
|---|---|---|---|---|
| **DDIM-CIFAR10-750k** | rediffuse-unet | CIFAR-10 | 548 MB | Collaborator checkpoint, ReDiffuse-compatible |
| **GuidedDiff-CIFAR10-500k** | guided-diffusion-unet | CIFAR-10 | 201 MB | Different UNet architecture (256/256 channels), loads in ReDiffuse but not tested for MIA |
| **Beans-LoRA-SD15** | peft-lora | Beans | 3 MB | PEFT/LoRA for SD1.5 UNet, not standalone |
| **NDSS-2025-derived** | text+image wrapper | COCO-like (fine-tuned SD) | 4-428 MB | Black-box proxy tensors, not loadable model checkpoints |
| **SD-v1-4-CompVis** | diffusers (HF) | LAION-5B | -- | Used in xuchi-reproduction (COCO-like MIA), not stored locally |

### Checkpoint Catalog Tooling

- **Catalog all checkpoints:** `python scripts/catalog_checkpoints.py` -- Output: `outputs/catalog_checkpoints.json` (~2000 lines, 12 checkpoints catalogued with format/size/compatibility)
- **Build matrix:** `python scripts/build_compatibility_matrix.py` -- Output: `outputs/dataset_checkpoint_matrix.json`

---

## 4. Script Inventory

### Core Tools (`Research/tools/`)

| Tool | Purpose |
|---|---|
| `tools/gsa_next_run/` | GSA training job runner: gate control, hashing, git-info, CLI dispatch |
| `tools/pia_next_run/` | PIA training job runner: gate control, hashing, git-info, CLI dispatch |

### Environment & Setup (`scripts/`)

| Script | Purpose |
|---|---|
| `bootstrap_research_env.py` | Install research environment dependencies |
| `verify_env.py` | Verify environment is correctly set up |
| `render_team_local_configs.py` | Bind local paths from `configs/assets/team.local.yaml` |
| `write_imagefolder_labels.py` | Write ImageFolder-style label files |

### Storage & Integrity (`scripts/`)

| Script | Purpose |
|---|---|
| `audit_local_storage.py` | Audit local large files and data boundary; default dry-run, `--execute` to relocate |
| `check_markdown_links.py` | Check Markdown link integrity |
| `check_public_surface.py` | Check public repo paths for leaks and candidate-result boundary language |
| `run_pr_checks.py` | GitHub PR fast gate (no PyTorch, no runtime tests) |
| `run_local_checks.py` | Local quality checks with `--python` and `--fast` flags |
| `run_docs_checks.py` | Document consistency checks |

### Experiment Execution (`scripts/`)

| Script | Purpose |
|---|---|
| `e3_train_and_eval.py` | E3 pipeline: train + eval on existing checkpoints |
| `e3_eval_existing.py` | E3: evaluate existing checkpoints only |
| `batch_eval_sweep.py` | Batch evaluation sweep |
| `batch_smp_lora_sweep.py` | Batch SMP LoRA sweep |
| `train_smp_lora.py` | Train SMP LoRA defense |
| `evaluate_smp_lora_defense.py` | Evaluate SMP LoRA defense |
| `launch_dpdm_training.ps1` | Launch single DPDM training |
| `launch_dpdm_target_and_shadows.ps1` | Launch target + shadow DPDM training |
| `launch_dpdm_shadow_sequence.ps1` | Launch shadow training sequence |
| `launch_dpdm_shadow_sequence_after_pid.ps1` | Launch shadow sequence after PID |
| `launch_gsa_training.ps1` | Launch GSA training |
| `launch_gsa_training_sequence.ps1` | Launch GSA training sequence |
| `launch_gsa_shadows_after_pid.ps1` | Launch GSA shadows after PID |
| `monitor_gsa_sequence.py` | Monitor GSA training progress |

### H1 Channel Knockout & Activation Scouts (`scripts/`)

| Script | Purpose |
|---|---|
| `h1_activation_scout.py` | H1 DDPM CIFAR-10 activation space scout |
| `h1_channel_knockout.py` | H1 DDIM 750k CIFAR-10 channel knockout |
| `h1_channel_knockout_cifar100.py` | H1 CIFAR-100 channel knockout |
| `h1_channel_knockout_ddim.py` | H1 DDIM 750k channel knockout (DDIM variant) |
| `h1_cifar100_grid.py` | H1 CIFAR-100 activation grid |
| `h1_fine_grid_cifar100.py` | H1 CIFAR-100 fine grid |
| `h1_fine_grid_ddim.py` | H1 DDIM fine grid |
| `h1_matched_knockout.py` | H1 matched-size channel knockout control |
| `h1_mechanistic_ddim.py` | H1 DDIM mechanistic analysis |
| `h1_scout_ddim_n128.py` | H1 DDIM n=128 scout |

### H2 & Response-Cache Scripts (`scripts/`)

| Script | Purpose |
|---|---|
| `h2_score_vector_sidecar.py` | H2 score-vector sidecar analysis |
| `collect_h2_img2img_response_cache.py` | Collect H2 image-to-image response cache |
| `evaluate_h2_response_cache.py` | Evaluate H2 response cache |
| `run_h2_response_strength_validation.py` | H2 response-strength validation |
| `review_h2_img2img_output_cloud_portability.py` | H2 output-cloud img2img portability review |
| `review_h2_img2img_simple_distance.py` | H2 simple-distance comparator |
| `review_h2_lowpass_cutoffs.py` | H2 lowpass cutoff review |
| `review_h2_output_cloud_geometry.py` | H2 output-cloud geometry review |
| `review_h2_output_cloud_transfer.py` | H2 output-cloud transfer review |
| `probe_h2_cross_asset_contract.py` | H2 cross-asset contract probe |

### Attack Methodology Scripts (`scripts/`)

**Black-box:**
| Script | Purpose |
|---|---|
| `run_blackbox_prompt_response_consistency.py` | Black-box prompt-response consistency |
| `run_blackbox_semantic_aux_fusion.py` | Black-box semantic auxiliary fusion |
| `run_blackbox_semantic_aux_probe.py` | Black-box semantic auxiliary probe |
| `run_recon_timestep_probe.py` | Reconstruction timestep probe |
| `review_recon_tail_confidence.py` | Recon tail-confidence review |

**Gray-box:**
| Script | Purpose |
|---|---|
| `run_graybox_triscore_canary.py` | Gray-box tri-score canary |
| `review_graybox_triscore_truth_hardening.py` | Gray-box tri-score truth hardening |
| `run_secmi_pia_disagreement.py` | SecMI vs PIA disagreement analysis |
| `run_pia_tmiadm_confidence_switch.py` | PIA/TMIA-DM confidence switch |
| `build_secmi_pia_adaptive_comparability_board.py` | SecMI/PIA adaptive comparability |
| `validate_secmi_supporting_contract.py` | SecMI supporting contract validation |
| `review_rediffuse_checkpoint_portability_gate.py` | ReDiffuse checkpoint portability gate |
| `review_rediffuse_resnet_contract_scout.py` | ReDiffuse ResNet contract scout |

**CLiD (Black-box, prompt-conditioned):**
| Script | Purpose |
|---|---|
| `audit_clid_threshold_compatibility.py` | CLiD threshold compatibility audit |
| `prepare_clid_local_bridge.py` | Prepare CLiD local bridge |
| `prepare_clid_sanitized_probe.py` | Prepare CLiD sanitized probe |
| `perturb_clid_bridge_prompts.py` | Perturb CLiD bridge prompts |
| `compare_clid_control_packets.py` | Compare CLiD control packets |
| `validate_clid_identity_boundary.py` | Validate CLiD identity boundary |
| `review_clid_bridge_contract.py` | Review CLiD bridge contract |
| `review_clid_candidate_packet.py` | Review CLiD candidate packet |
| `review_clid_prompt_text_only.py` | Review CLiD prompt-text-only |
| `review_clid_score_schema.py` | Review CLiD score schema |
| `summarize_clid_bridge_pair_outputs.py` | Summarize CLiD bridge pair outputs |

**White-box (GSA / Fisher / Influence):**
| Script | Purpose |
|---|---|
| `review_gsa_diagonal_fisher_feasibility.py` | GSA diagonal Fisher feasibility |
| `review_gsa_loss_score_shadow_stability.py` | GSA loss-score shadow stability |
| `rebuild_gsa_cifar_buckets.py` | Rebuild GSA CIFAR buckets |
| `run_fashion_mnist_score_jacobian_sensitivity.py` | Fashion-MNIST score-Jacobian sensitivity |
| `run_fashion_mnist_sima_score_norm.py` | Fashion-MNIST SimA score-norm |
| `validate_whitebox_influence_curvature_contract.py` | White-box influence curvature |

**Other Attacks:**
| Script | Purpose |
|---|---|
| `run_cdi_internal_canary.py` | CDI internal canary |
| `run_mofit_interface_canary.py` | MoFit interface canary |
| `run_noise_as_probe_interface_canary.py` | Noise-as-probe canary |
| `run_structural_memorization_smoke.py` | Structural memorization smoke |
| `run_commoncanvas_denoising_loss.py` | CommonCanvas denoising loss |
| `run_commoncanvas_multiseed_stability.py` | CommonCanvas multiseed stability |
| `run_beans_lora_member_scout.py` | Beans LoRA member scout |
| `run_beans_lora_delta_sensitivity.py` | Beans LoRA delta sensitivity |
| `probe_midst_blending_plus_plus_scout.py` | MIDST blending++ scout |
| `probe_midst_tabddpm_ept_scout.py` | MIDST TabDDPM EPT scout |
| `probe_tracing_roots_feature_packet.py` | Tracing the Roots feature-packet probe |

**Defense:**
| Script | Purpose |
|---|---|
| `validate_ib_adaptive_defense_contract.py` | IB adaptive defense contract |
| `validate_ib_defended_shadow_reopen_protocol.py` | IB defended shadow reopen |
| `validate_ib_defended_shadow_training_manifest.py` | IB defended shadow training manifest |
| `validate_ib_shadow_local_gsa_risk_preflight.py` | IB shadow local GSA risk preflight |
| `validate_ib_shadow_local_identity_scout.py` | IB shadow local identity scout |

**Variation / Response:**
| Script | Purpose |
|---|---|
| `init_variation_query_set.py` | Initialize variation query set |
| `audit_variation_query_contract.py` | Audit variation query contract |
| `discover_response_contract_packages.py` | Discover response contract packages |
| `scaffold_response_contract_package.py` | Scaffold response contract package |
| `probe_response_contract_package.py` | Probe response contract package |

### Paper, Release & Evidence Bundle Scripts (`scripts/`)

| Script | Purpose |
|---|---|
| `check_e2_freeze_preflight.py` | Offline validate E2 freeze-preflight table |
| `check_e2_public_sources.py` | E2 N50 preflight URL reachability (HEAD/Range/1-byte probe) |
| `refresh_e2_public_surface_metadata.py` | E2 no-download metadata refresh |
| `build_e2_false_promotion_expansion_queue.py` | E2 C14+ false-promotion corpus expansion |
| `build_e2_n50_preflight.py` | E2 N50 preflight builder |
| `build_e2_false_promotion_pilot.py` | E2 false-promotion pilot |
| `build_e2_public_freeze_ledger.py` | E2 public-source freeze ledger |
| `build_claim_gate_recode_packet.py` | C1-C15 claim-gate blind recode template |
| `check_paper_release_packet.py` | Validate paper release packet |
| `export_paper_supplement.py` | Export anonymous supplement ZIP + SHA-256 |
| `export_admitted_evidence_bundle.py` | Export admitted evidence bundle |
| `export_false_promotion_review_bundle.py` | Export C14 false-promotion external review bundle |
| `export_recon_product_evidence_card.py` | Export recon product evidence card |
| `aggregate_e2_blind_review.py` | Aggregate E2 blind review |
| `aggregate_e2q005_external_review.py` | Aggregate E2Q-005 single-row external review |
| `aggregate_false_promotion_external_review.py` | Aggregate C14 false-promotion reviewer CSV |
| `inspect_e2q005_tracing_roots_package.py` | E2Q-005 OpenReview supplement identity/tensor-hash check |
| `replay_mofit_public_coco_scores.py` | MoFit public COCO score replay (AUC, ROC, gate-status) |
| `validate_attack_defense_table.py` | Validate attack-defense summary table |
| `validate_intake_index.py` | Validate intake index |
| `validate_local_api_registry_alignment.py` | Validate Runtime-Server registry alignment |
| `evaluate_report_correctness_faults.py` | Report-correctness fault-injection matrix |
| `render_admitted_risk_card.py` | Render admitted evidence risk card |
| `run_x90_larger_surface_triscore.py` | X-90 larger-surface tri-score |
| `run_x90_tmiadm512_assets.py` | X-90 TMIA-DM 512-surface assets |

### Edge-Case Probes (`scripts/`)

| Script | Purpose |
|---|---|
| `probe_edge_cases.py` | Edge case probe (batch 1) |
| `probe_edge_cases2.py` | Edge case probe (batch 2) |
| `verify_h1_loading.py` | Verify H1 activation loading |
| `reorder_sections.py` | Reorder document sections |

### Scripts Dependencies

- **Python 3.10+**, conda environment `diffaudit-research`
- **PyTorch** with CUDA (most attack/eval scripts)
- **HuggingFace** `diffusers`, `transformers` (SD, CLIP, BLIP, Beans)
- **Key local packages:** `src/diffaudit/` (attacks, defenses, utils, pipelines, reports, cli)
- **External clones:** PIA, CLiD, Reconstruction-based-Attack, GSA, DiT, DPDM (under `external/`)
- **Config path binding:** `configs/assets/team.local.yaml` (git-ignored, absolute paths)

---

## 5. Results Inventory

### Key Result Snapshots

#### E3 Evaluation (Existing Checkpoints)

| Checkpoint | Attack | AUC | TPR@1%FPR | Note |
|---|---|---|---|---|
| DDPM-CIFAR10-800k | SecMI (t100/k10) | 0.459 | 0.0 | Weak |
| DDPM-CIFAR10-800k | SecMI (t50/k5) | 0.459 | 0.0 | Weak |
| DDPM-CIFAR10-800k | SecMI (t200/k20) | 0.459 | 0.0 | Weak |
| DDPM-CIFAR10-800k | PIA (int200/num1) | 0.573 | 0.063 | Moderate |
| DDPM-CIFAR10-800k | PIA (int100/num2) | 0.605 | 0.063 | Moderate |
| DDIM-CIFAR10-750k | SecMI (all variants) | ~0.397 | 0.0 | Weaker than 800k |
| DDIM-CIFAR10-750k | PIA (int200/int100) | 0.599-0.605 | -- | Comparable to 800k |

**Location:** `outputs/e3_existing_eval/e3_eval_results.json`

#### H1 Activation Scouts

| Experiment | Best AUC | Notes |
|---|---|---|
| H1 DDIM 750k channel knockout | 0.895 (baseline), 0.668 (targeted mean) | 16-channel knockout |
| H1 CIFAR-100 channel knockout | 0.811 (baseline), 0.748 (late_down_t600 best) | Activation-space fine grid |
| H1 DDIM fine grid | -- | Detailed activation patterns |
| H1 mechanistic analysis | -- | CIFAR-10 + CIFAR-100 |

**Location:** `outputs/h1_scout/` (JSON + PKL activation tensors + PDF/PNG figures)

#### H2 Score-Vector Sidecar

| Experiment | AUC | Notes |
|---|---|---|
| H2 score-vector scout (DDPM-800k) | 0.681 | Label-shuffle control: 0.475 |

**Location:** `outputs/h2_sidecar/h2_results.json`, `h2_features.pkl`

#### Admitted Evidence (Evidence-Ready)

| Track | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
|---|---|---|---|---|
| Black-box `recon` | 0.837 | 0.74 | 0.22 | 0.11 |
| Gray-box `PIA` (25k/25k full) | -- | -- | -- | -- |
| Gray-box SecMI (25k/25k full) | 0.886 | -- | -- | -- |
| Gray-box NNS (SecMI) | 0.946 | -- | -- | -- |
| Gray-box tri-score (CDI/TMIA-DM/PIA) | 0.859 | -- | -- | -- |

#### Candidate-Only (Research-side, not Platform-admitted)

| Track | AUC | TPR@1%FPR | TPR@0.1%FPR |
|---|---|---|---|
| H2 output-cloud geometry (512/512) | 0.962 | 0.334 | 0.117 |
| H2 output-cloud geometry (256/256 controlled) | 0.968 | 0.410 | 0.133 |
| CLiD official inter_output replay | 0.961 | 0.675 | -- |
| H2 response-strength simple-distance (25/25 admission) | 0.877 | -- | -- |
| Mid-frequency same-noise residual (64/64) | 0.733 | -- | -- |
| ReDiffuse SD collaborator (5000-row) | 0.710 | -- | -- |
| Tracing the Roots feature packet | 0.816 | 0.134 | -- |

#### Closed / Weak Directions

| Track | Best AUC | Verdict |
|---|---|---|
| STL-10 ReDiffuse bounded scout | 0.500 | Random-level, direction closed |
| STL-10 SimA score-norm | 0.505 | Random-level, direction closed |
| Beans LoRA denoising loss | 0.414 | Membership provenance blocked |
| Fashion-MNIST PIA-style loss | 0.536 | Weak |
| Fashion-MNIST SimA score-norm | 0.515 | Weak |
| Fashion-MNIST score-Jacobian | 0.512 | Weak |
| CommonCanvas prompt-response | 0.441 | Weak |
| CommonCanvas denoising-loss | 0.515 | Weak |
| MIDST TabDDPM nearest-neighbor | 0.566 | Weak |
| MIDST TabDDPM EPT | 0.530 | Weak |
| Tiny overfit gradient-prototype | 0.501 | Random-level |

### Detailed Evidence Location

All detailed experiment reports, gate reviews, and metric packets are in `docs/evidence/`:

- `docs/evidence/reproduction-status.md` -- Master status board
- `docs/evidence/workspace-evidence-index.md` -- Cross-reference to workspace evidence
- `docs/evidence/non-clid-black-box-reselection.md` -- Recon product evidence
- `docs/evidence/recon-product-validation-*.md` -- Recon product validation
- `docs/evidence/h2-output-cloud-geometry-20260525.md` -- H2 geometry
- `docs/evidence/clid-*.md` -- CLiD series
- `docs/evidence/rediffuse-*.md` -- ReDiffuse series
- `docs/evidence/midfreq-*.md` -- Mid-frequency series
- `docs/evidence/fashion-mnist-*.md` -- Fashion-MNIST series
- `docs/evidence/beans-*.md` -- Beans series
- `docs/evidence/midst-*.md` -- MIDST series

Paper-corpus results and review bundles are in `papers/diffaudit-evidence-paper/`:
- `data/artifact_corpus_v1.csv`
- `data/artifact_corpus_fixed_search_20260526.csv`
- `data/artifact_corpus_broader_source_20260527.csv`
- `data/artifact_second_pass_label_review_20260526.csv`
- `data/artifact_corpus_targeted_artifact_links_20260527.csv`
- `data/negative_support_curated_metrics.csv`

---

## 6. Quick Reference: "I Want to Run X on Y"

### Run Membership Inference (Strong -- Evidence-Ready)

| Goal | Recipe |
|---|---|
| **Gray-box PIA on CIFAR-10** | Use `DDPM-CIFAR10-800k` + `CIFAR10_train_ratio0.5.npz`. Run PIA with config `configs/attacks/pia_plan.yaml`. Member split: `external/PIA/DDPM`. Checkpoint from `Download/gray-box/weights/secmi-cifar-bundle/`. |
| **Gray-box SecMI on CIFAR-10** | Use `DDPM-CIFAR10-800k` + `CIFAR10_train_ratio0.5.npz`. Full 25k/25k. Config: `configs/attacks/secmi_plan.yaml`. |
| **Black-box recon on NDSS-2025** | Use `Download/black-box/supplementary/recon-assets/`. Config: `configs/attacks/recon_plan.yaml`. Bounded public-100 step30 rerun. |
| **H1 activation scout on CIFAR-10** | Use `DDPM-CIFAR10-800k` or `DDIM-CIFAR10-750k` + CIFAR-10 split. Run `h1_activation_scout.py` or `h1_channel_knockout.py`. |

### Run Evaluation on Existing Checkpoints

| Goal | Recipe |
|---|---|
| **E3 quick eval (SecMI + PIA)** | `python scripts/e3_eval_existing.py`. Reads `DDPM-CIFAR10-800k` and `DDIM-CIFAR10-750k`. Output: `outputs/e3_existing_eval/e3_eval_results.json`. |
| **Full train + eval** | `python scripts/e3_train_and_eval.py`. |

### Explore Untested Combinations

| Goal | Recipe | Risk |
|---|---|---|
| **STL-10 overfit MIA** | Use `DDPM-STL10-overfit-m1000-9k` + `STL10_train_ratio0.5.npz`. Overfit regime may yield signal. ReDiffuse-compatible. | HIGH: full-training regime gave random-level AUC. Overfit regime is speculative. |
| **STL-10 99k collaborator eval** | Use `DDPM-STL10-99k` + `STL10_train_ratio0.5.npz`. | MEDIUM: 99k steps may need more training for useful signal. |
| **GuidedDiff CIFAR-10 MIA** | Use `GuidedDiff-CIFAR10-500k` + `CIFAR10_train_ratio0.5.npz`. Different UNet arch (OpenAI guided-diffusion). | HIGH: needs architecture adapter to compare with ReDiffuse results. |
| **CIFAR-100 SecMI / PIA** | Use `DDPM-CIFAR100-800k` + `CIFAR100_train_ratio0.5.npz`. Same arch as CIFAR10-800k, different weights. | MEDIUM: no SecMI/PIA eval run yet; H1 activation scout only. |

### Verify Asset Integrity

| Goal | Recipe |
|---|---|
| **Check all local data/checkpoints** | `python scripts/audit_local_storage.py` (dry-run default; `--execute` to relocate) |
| **Catalog all .pt files** | `python scripts/catalog_checkpoints.py` |
| **Build compatibility matrix** | `python scripts/build_compatibility_matrix.py` |
| **Verify environment** | `python scripts/verify_env.py` |
| **Verify local path binding** | `python scripts/render_team_local_configs.py` |
| **PIA asset probe** | `python -m diffaudit probe-pia-assets --config configs/attacks/pia_plan.yaml --member-split-root external/PIA/DDPM` |
| **GSA asset probe** | `python -m diffaudit probe-gsa-assets --repo-root external/GSA --assets-root workspaces/white-box/assets/gsa` |
| **Recon bundle audit** | `python -m diffaudit audit-recon-public-bundle --bundle-root Download/black-box/supplementary/recon-assets/...` |

### Run Paper / Release Checks

| Goal | Recipe |
|---|---|
| **PR fast gate** | `python scripts/run_pr_checks.py` |
| **Paper release packet check** | `python scripts/check_paper_release_packet.py` |
| **E2 freeze preflight** | `python scripts/check_e2_freeze_preflight.py` |
| **Public surface leak check** | `python scripts/check_public_surface.py` |
| **Export supplement ZIP** | `python scripts/export_paper_supplement.py --check` |
| **Export evidence bundle** | `python scripts/export_admitted_evidence_bundle.py` |
| **E2 public-source URL check** | `python scripts/check_e2_public_sources.py` |

### Run Defense Evaluation

| Goal | Recipe |
|---|---|
| **SMP LoRA defense** | `python scripts/train_smp_lora.py` then `python scripts/evaluate_smp_lora_defense.py` |
| **DPDM training** | `.\scripts\launch_dpdm_training.ps1` or `.\scripts\launch_dpdm_target_and_shadows.ps1` |
| **IB defense contract** | `python scripts/validate_ib_adaptive_defense_contract.py` |

---

## Appendix A: Directory Map

| Path | Role |
|---|---|
| `Research/` | Git repo root (this document) |
| `Research/src/diffaudit/` | Python package: attacks, defenses, utils, pipelines, cli |
| `Research/configs/` | Experiment configs (attacks, benchmarks, datasets, models, assets) |
| `Research/scripts/` | All runnable scripts (see Section 4) |
| `Research/tools/` | GSA/PIA training job runner tools |
| `Research/tests/` | Test suite |
| `Research/docs/` | Documentation: evidence, assets, start-here, product-bridge, internal |
| `Research/papers/` | Paper corpus: data CSVs, builds, version drafts |
| `Research/workspaces/` | Current research state per direction (black-box, gray-box, white-box, etc.) |
| `Research/legacy/` | Archived experiment notes and history |
| `Research/external/` | Shallow clones of upstream repos (PIA, CLiD, GSA, DiT, DPDM, etc.) |
| `Research/third_party/` | Vendored upstream code subsets (SecMI) |
| `Research/references/` | Paper PDFs, supplementary materials, Rediffuse/DDPM reference code |
| `Research/notebooks/` | Jupyter notebooks (currently empty) |
| `Research/build/` | Build artifacts |
| `Research/tmp/` | Temporary files (git-ignored) |
| `Research/data/datasets/pytorch/` | Local PyTorch dataset cache (CIFAR, STL-10 symlinks) |
| `Research/outputs/` | Local scratch outputs (git-ignored, not for delivery) |
| `Download/` | Sibling directory: raw datasets, weights, supplementary archives (not in git) |

## Appendix B: Key Config Files

| File | Purpose |
|---|---|
| `configs/assets/team.local.template.yaml` | Template for local path binding (copy to `team.local.yaml`) |
| `configs/assets/team.local.yaml` | ACTIVE local path config (git-ignored, absolute paths) |
| `configs/attacks/pia_plan.yaml` | PIA attack plan |
| `configs/attacks/pia_mainline_canonical.yaml` | PIA mainline canonical config |
| `configs/attacks/secmi_plan.yaml` | SecMI attack plan |
| `configs/attacks/recon_plan.yaml` | Recon attack plan |
| `configs/attacks/variation_plan.yaml` | Variation attack plan |
| `configs/attacks/clid_plan.yaml` | CLiD attack plan |
| `configs/benchmarks/secmi_smoke.yaml` | SecMI smoke test |
| `configs/assets/black-box.requirements.yaml` | Black-box asset requirements |
| `configs/assets/gray-box.requirements.yaml` | Gray-box asset requirements |
| `environment.yml` | Conda environment (CPU) |
| `environment.gpu-cu128.yml` | Conda environment (GPU, CUDA 12.8) |
| `pyproject.toml` | Python project metadata |

## Appendix C: External Code Clones

| Repo | Clone Command | Purpose |
|---|---|---|
| PIA | `git clone --depth 1 https://github.com/kong13661/PIA.git external/PIA` | Gray-box PIA attack |
| CLiD | `git clone --depth 1 https://github.com/zhaisf/CLiD external/CLiD` | Black-box CLiD attack |
| Recon | `git clone --depth 1 https://github.com/py85252876/Reconstruction-based-Attack external/Reconstruction-based-Attack` | Recon attack |
| GSA | `git clone --depth 1 https://github.com/py85252876/GSA.git external/GSA` | White-box GSA attack |
| DiT | `git clone --depth 1 https://github.com/facebookresearch/DiT.git external/DiT` | DiT model reference |
| DPDM | `git clone --depth 1 https://github.com/nv-tlabs/DPDM.git external/DPDM` | DPDM defense |

All `external/` directories are git-ignored. Use shallow clones (`--depth 1`) by default.
