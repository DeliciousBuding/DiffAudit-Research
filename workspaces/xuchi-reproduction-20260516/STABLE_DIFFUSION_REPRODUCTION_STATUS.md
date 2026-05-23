# Stable Diffusion MIA Reproduction Status

## Scope

This project reproduces the Stable Diffusion portion of the paper:

`Towards Black-Box Membership Inference Attack for Diffusion Models`

The reproduced task is not Stable Diffusion training.  It is the membership
inference attack pipeline: reconstruct input images with Stable Diffusion,
score reconstruction similarity, and evaluate whether the score separates
member and non-member samples.

## Requirement Checklist

| Requirement | Status | Notes |
|---|---|---|
| member data from LAION-style local subset | done | `E:\stable_diffusion\coco_data\stable_diffusion_data\images-random` |
| member list | done | `E:\stable_diffusion\coco_data\stable_diffusion_data\val-list-2500-random.npy` |
| non-member data from COCO2017-val | done | `E:\stable_diffusion\coco_data\coco_data\val2017` |
| 2500 member + 2500 non-member full evaluation | done | exported `result.csv` has 5000 samples |
| model `CompVis/stable-diffusion-v1-4` | done | loaded from local HuggingFace cache |
| no Stable Diffusion retraining | done | no training or fine-tuning performed |
| no LoRA / DreamBooth / Textual Inversion | done | only pretrained SD v1-4 is used |
| BLIP caption route | done | `laion5_blip` route uses saved BLIP captions |
| metric SSIM | done | saved ReDiffuse features are SSIM-based; current best also fuses SSIM features |
| diffusion step / interval `t=10`, `k=10` | done | all final runs use `interval=10`, `k=10` |
| AUC | done | final combined detector full-data AUC `0.7103` |
| ASR | done | final combined detector ASR `0.6846` |
| TPR@FPR=1% | done | final combined detector `0.0716` = `7.16%` |
| image-level result CSV | done | `reproduction_artifacts\result.csv` |
| ROC curve | done | `reproduction_artifacts\roc_curve.png` and `roc_curve.csv` |
| single-image score command | done | `score_single_image.py` |

## Current Final Artifacts

Directory:

`E:\stable_diffusion\coco_data\SD_MIA_Reproduction\reproduction_artifacts`

Files:

- `result.csv`
- `metrics.json`
- `metrics.csv`
- `roc_curve.csv`
- `roc_curve.png`

Final full-data metrics:

| AUC | ASR | TPR@FPR=1% |
|---:|---:|---:|
| `0.7103` | `0.6846` | `0.0716` |

Strict validation of the current recommended detector:

| Validation | AUC |
|---|---:|
| holdout | `0.7046` |
| 5-fold | `0.7080 ± 0.0116` |

## Comparison To Paper Table 3

| Scenario | Paper AUC | Paper ASR | Paper TPR@1%FPR | Local AUC |
|---|---:|---:|---:|---:|
| Laion5 | `0.81` | `0.75` | `20.6%` | not final target in this run |
| Laion5 with BLIP | `0.82` | `0.75` | `21.7%` | `0.7103` |

The local result is clearly above random guessing and above the earlier
reproduction package result (`0.6302`), but it is still below the paper table.
The main likely reason is that the exact paper LAION-5B member split is not
available; the local member set is a repeatable LAION-like subset.

## Black-Box Boundary Note

The implementation uses `CompVis/stable-diffusion-v1-4` locally and does not
train or fine-tune the model.  It reconstructs images through the ReDiffuse
DDIM-style reconstruction procedure and only exports reconstruction similarity
features for evaluation.

One nuance: the current local implementation calls the denoiser through the
Diffusers pipeline wrapper to obtain noise predictions needed by the DDIM
ReDiffuse steps.  It does not inspect training data, weights, gradients, or
intermediate activations beyond the model-query output used for reconstruction.
If a stricter external-service definition is required, the next version should
use only a public `img2img` / image variation endpoint and treat the generated
image as the sole observable output.  That would be a stricter API-black-box
variant and should be reported separately.

## Single Image Scoring

Example:

```powershell
$py = 'C:\Users\33166\miniconda3\envs\ddim_repro\python.exe'
cd E:\stable_diffusion\coco_data\SD_MIA_Reproduction

& $py score_single_image.py `
  --image 'E:\stable_diffusion\coco_data\stable_diffusion_data\images-random\laion_000250717.jpg' `
  --prompt 'a woman with long hair and a crown of flowers' `
  --detector-json 'E:\stable_diffusion\coco_data\SD_MIA_Reproduction\chunk_outputs_a5_avg3_vae\mia_detector_rediffuse_sweep_best_a2_a5_combined.json' `
  --feature-plan a2_a5_combined
```

Output fields include:

- `score`: higher means more likely member
- `threshold`: member if `score >= threshold`
- `prediction`: `1` for member, `0` for non-member
