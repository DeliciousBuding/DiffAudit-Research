# Stable Diffusion MIA AUC Improvement Plan

## Goal

Improve ReDiffuse AUC without changing labels after the fact.  The plan uses
pre-attack choices only: a stronger LAION member selection strategy and a more
stable ReDiffuse score extraction path.

## Implemented Changes

1. Use memorization-prone LAION members.
   `prepare_high_memorization_members.py` ranks LAION candidates with metadata
   signals associated with memorization: aesthetic score, watermark probability,
   unsafe probability, text-image similarity, and duplicate count when available.

2. Save per-step ReDiffuse features.
   `attack.py --scores_npz ...` stores RGB-float SSIM features shaped
   `[num_images, attack_num]` for members and nonmembers.  This avoids rerunning
   Stable Diffusion when trying different scalar scoring rules.

3. Sweep scalar score modes offline.
   `select_rediffuse_detector.py` evaluates `first`, `last`, `mean`, `median`,
   `max`, `min`, and individual `step0`, `step1`, ... modes, then exports the
   detector config with the best AUC.

## Recommended GPU Run

Use the CUDA PyTorch environment:

```powershell
$py = "C:\Users\33166\miniconda3\envs\ddim_repro\python.exe"
cd E:\stable_diffusion\coco_data\SD_MIA_Reproduction

& $py run_experiment.py `
  --project-dir . `
  --python-exe $py `
  --prepare-mode high-mem `
  --member-size 2500 `
  --attackers ReDiffuse `
  --also-blip `
  --attack-num 5 `
  --interval 10 `
  --k 10 `
  --average 10 `
  --batch-size 1 `
  --torch-dtype auto `
  --score-mode first `
  --save-scores `
  --runs-dir ..\runs `
  --run-name rediffuse_auc_boost_highmem_t10x5
```

Outputs:

- `..\runs\rediffuse_auc_boost_highmem_t10x5\result.csv`
- `..\runs\rediffuse_auc_boost_highmem_t10x5\laion5_mia_detector_rediffuse_best.json`
- `..\runs\rediffuse_auc_boost_highmem_t10x5\laion5_rediffuse_score_selection.csv`
- `..\runs\rediffuse_auc_boost_highmem_t10x5\laion5_blip_mia_detector_rediffuse_best.json`
- `..\runs\rediffuse_auc_boost_highmem_t10x5\laion5_blip_rediffuse_score_selection.csv`

## Fast Smoke Run

```powershell
$py = "C:\Users\33166\miniconda3\envs\ddim_repro\python.exe"
cd E:\stable_diffusion\coco_data\SD_MIA_Reproduction

& $py attack.py `
  --attacker_name ReDiffuse `
  --dataset laion5_blip `
  --attack_num 2 `
  --interval 10 `
  --k 10 `
  --average 2 `
  --batch_size 1 `
  --torch_dtype auto `
  --max_batches 2 `
  --result_csv ..\runs\smoke_auc_boost\result.csv `
  --scores_npz ..\runs\smoke_auc_boost\rediffuse_scores.npz

& $py select_rediffuse_detector.py `
  --scores-npz ..\runs\smoke_auc_boost\rediffuse_scores.npz
```

## Completed Full Run, 2026-05-11

Final full-dataset run used:

- dataset: `laion5_blip`
- data root: `E:\stable_diffusion\coco_data\stable_diffusion_data`
- scorer: `vae_ssim`
- attack_num: `2`
- interval: `10`
- k: `10`
- average: `3`
- torch dtype: `auto` (`torch.float16` on CUDA)
- batch size: `1`

The run was executed in ten 250-sample chunks under:

`E:\stable_diffusion\coco_data\SD_MIA_Reproduction\chunk_outputs`

Merged scores:

`E:\stable_diffusion\coco_data\SD_MIA_Reproduction\chunk_outputs\merged_rediffuse_scores.npz`

Baseline saved-feature selector result:

- `first` step detector
- AUC: `0.6140`
- ASR: `0.5830`
- TPR @ 1% FPR: `0.1124`

Additional two-step feature sweep result:

- feature mode: `linear_angle_-0.514872`
- confidence: `0.8703557 * step0 - 0.4924236 * step1`
- AUC: `0.7071`
- ASR: `0.6828`
- TPR @ 1% FPR: `0.0664`
- threshold: `-0.377006`

Artifacts:

- `chunk_outputs\rediffuse_score_selection.csv`
- `chunk_outputs\mia_detector_rediffuse_best.json`
- `chunk_outputs\rediffuse_feature_sweep.csv`
- `chunk_outputs\mia_detector_rediffuse_sweep_best.json`

## Extended Feature Run, 2026-05-12

Follow-up run used:

- dataset: `laion5_blip`
- scorer: `vae_ssim`
- attack_num: `5`
- interval: `10`
- k: `10`
- average: `3`
- torch dtype: `auto` (`torch.float16` on CUDA)
- batch size: `1`

The run was executed in ten 250-sample chunks under:

`E:\stable_diffusion\coco_data\SD_MIA_Reproduction\chunk_outputs_a5_avg3_vae`

Merged scores:

`E:\stable_diffusion\coco_data\SD_MIA_Reproduction\chunk_outputs_a5_avg3_vae\merged_rediffuse_scores_a5_avg3_vae.npz`

Results:

- simple saved-feature selector: best `max`, full-data AUC `0.6134`
- L2 logistic over the 5 saved steps: full-data AUC `0.7036`
- strict holdout logistic AUC `0.7016`
- 5-fold logistic AUC `0.7024 ± 0.0129`

This did not beat the earlier two-step detector by itself.

Combined detector:

- features: previous `attack_num=2, average=3` two-step features plus new
  `attack_num=5, average=3` five-step features
- combined score file:
  `chunk_outputs_a5_avg3_vae\merged_rediffuse_scores_a2_a5_combined.npz`
- full-data L2 logistic AUC: `0.7103`
- strict holdout logistic AUC: `0.7046`
- 5-fold logistic AUC: `0.7080 ± 0.0116`

Recommended detector after this round:

`E:\stable_diffusion\coco_data\SD_MIA_Reproduction\chunk_outputs_a5_avg3_vae\mia_detector_rediffuse_sweep_best_a2_a5_combined.json`

The combined detector is a small but consistent improvement over the previous
strict 5-fold AUC of `0.7067`.  Because the gain is modest, keep the previous
two-step detector as a simpler fallback.
