# CLiD Official Inter-Output Replay

> Date: 2026-05-15
> Status: official-score-packet-replayed / positive-but-prompt-conditioned / candidate-only / no GPU release / no admitted row

## Question

Does the official `zhaisf/CLiD` repository add a reusable score packet that
changes DiffAudit's prior CLiD boundary?

This replay inspected the public GitHub repository, official `inter_output/*`
text files, evaluator scripts, and Hugging Face dataset metadata. It downloaded
only small README/script/intermediate text outputs through GitHub raw/API. It did
not download the MS-COCO split zip, Stable Diffusion weights, fine-tuned target
or shadow models, generated images, or any GPU artifact.

## Public Surface

| Field | Value |
| --- | --- |
| Repository | `https://github.com/zhaisf/CLiD` |
| Repo description | `[NeurIPS 2024] "Membership Inference on Text-to-image Diffusion Models via Conditional Likelihood Discrepancy"` |
| License | Apache-2.0 |
| Default branch inspected | `main` |
| Latest repo push observed | `2025-09-15T12:24:56Z` |
| Paper | arXiv `2405.14800` / NeurIPS 2024 |
| Dataset metadata | `zsf/COCO_MIA_ori_split1`, public metadata, `gated=auto`, `usedStorage=4,873,649,351` bytes |

The official README says the repository provides intermediate MS-COCO validation
results under real-world training settings. The Git tree contains public
intermediate outputs for `CLID`, `PIA`, `SecMI`, and `PFAMI`.

## Source Files Replayed

| Method | Shadow train/test | Target train/test |
| --- | --- | --- |
| CLiD | `inter_output/CLID/Atk_Impt_M_coco_real_split1_DATA_val17_split1_TRTE_train_MAXsmp_3_T_0506_145909.txt` / `..._TRTE_test_MAXsmp_3_T_0506_145909.txt` | `inter_output/CLID/Atk_Impt_M_coco_real_ori_DATA_val17_TRTE_train_MAXsmp_3_T_0506_145842.txt` / `..._TRTE_test_MAXsmp_3_T_0506_145842.txt` |
| PIA | `inter_output/PIA/Atk_pia_M_coco_real_split1_DATA_val17_split1__TRTE_train_T_0510_172145.txt` / `..._TRTE_test_T_0510_172145.txt` | `inter_output/PIA/Atk_pia_M_coco_real_ori_DATA_val17_TRTE_train_T_0510_172145.txt` / `..._TRTE_test_T_0510_172145.txt` |
| SecMI | `inter_output/SecMI/Atk_sec_M_coco_real_split1_DATA_val17_split1__TRTE_train_T_0510_172145.txt` / `..._TRTE_test_T_0510_172145.txt` | `inter_output/SecMI/Atk_sec_M_coco_real_ori_DATA_val17_TRTE_train_T_0510_172145.txt` / `..._TRTE_test_T_0510_172145.txt` |
| PFAMI | `inter_output/PFAMI/Atk_fluc_M_coco_real_split1_DATA_val17_split1__TRTE_train_T_0518_160926.txt` / `..._TRTE_test_T_0518_160926.txt` | `inter_output/PFAMI/Atk_fluc_M_coco_real_ori_DATA_val17_TRTE_train_T_0518_160926.txt` / `..._TRTE_test_T_0518_160926.txt` |

The replay follows the official scripts' file-loading convention by skipping
the first line of each intermediate output (`f.readlines()[1:]`). That leaves
`2,499` member rows and `2,499` nonmember rows per target/shadow split.

## Replay Method

- CLiD threshold replay follows `cal_clid_th.py`: use `[loss, -mean(CLID
  condition columns)]`, fit a robust scaler on shadow train/test outputs, scan
  `alpha in {0.0, 0.1, ..., 1.0}`, and select the target result from the alpha
  with the best shadow AUC.
- Baseline replay follows `cal_baselines.py`: use the first score column, with
  the same sign handling as the official script for PFAMI.
- Metrics report target AUC, target TPR at `1%` FPR, and target best-threshold
  ASR. No model execution or image/data download is involved.

## Results

CLiD threshold replay:

| Alpha | Shadow AUC | Target AUC | Target TPR@1%FPR | Target ASR |
| --- | ---: | ---: | ---: | ---: |
| `0.0` | `0.604300` | `0.619517` | `0.026411` | `0.584634` |
| `0.1` | `0.650148` | `0.667138` | `0.042817` | `0.620048` |
| `0.2` | `0.702854` | `0.721211` | `0.079632` | `0.663665` |
| `0.3` | `0.760380` | `0.779305` | `0.134454` | `0.709084` |
| `0.4` | `0.818594` | `0.836070` | `0.184474` | `0.759904` |
| `0.5` | `0.871406` | `0.885418` | `0.262105` | `0.800720` |
| `0.6` | `0.913161` | `0.923050` | `0.394158` | `0.840536` |
| `0.7` | `0.940911` | `0.947283` | `0.527411` | `0.872549` |
| `0.8` | `0.954977` | `0.959154` | `0.629452` | `0.890156` |
| `0.9` | `0.957537` | `0.961277` | `0.675470` | `0.891957` |
| `1.0` | `0.951815` | `0.956559` | `0.599840` | `0.890156` |

Baseline target replay:

| Method | Shadow AUC | Target AUC | Target TPR@1%FPR | Target ASR |
| --- | ---: | ---: | ---: | ---: |
| PIA | `0.540467` | `0.555077` | `0.017207` | `0.542017` |
| SecMI | `0.666452` | `0.654664` | `0.039216` | `0.615446` |
| PFAMI | `0.612160` | `0.603953` | `0.027211` | `0.580632` |

Selected replay result: `alpha = 0.9` by best shadow AUC, target
`AUC = 0.961277`, `TPR@1%FPR = 0.675470`, and `ASR = 0.891957`.

## Decision

`official-score-packet-replayed / positive-but-prompt-conditioned /
candidate-only / no GPU release / no admitted row`.

This materially upgrades CLiD from "local bridge/protocol diagnostic" to
"official intermediate score packet replayed on CPU." The signal is strong and
far above the current `0.60` weak-result floor. It still does not promote CLiD
into Platform/Runtime admitted evidence because the repo's packet is
prompt-conditioned text-to-image CLiD on MS-COCO real-world fine-tuning, while
the existing DiffAudit boundary requires an image-identity-safe protocol before
making product-facing black-box claims.

Smallest valid reopen condition for promotion:

- Public-safe target/shadow identity binding that maps these intermediate
  outputs to immutable split manifests without downloading the gated `4.87 GB`
  dataset zip;
- A prompt-neutral or image-identity protocol that preserves the official
  strict-tail signal; and
- A product-bridge handoff that explains how CLiD differs from the admitted
  `recon` black-box row and what Runtime fields would be consumed.

Stop condition:

- Do not download `COCO_MIA_ori_split1`, SD weights, target/shadow checkpoints,
  or generated image payloads in the current cycle.
- Do not run CLiD GPU jobs, XGBoost sweeps, prompt-shuffle matrices, or
  additional prompt controls unless the next step directly tests the
  image-identity boundary.
- Do not change Platform/Runtime admitted rows, recommendation logic, product
  copy, or report schemas from this replay alone.

## Platform and Runtime Impact

None for now. CLiD remains candidate-only. Platform and Runtime should continue
consuming only the admitted `recon / PIA baseline / PIA defended / GSA / DPDM
W-1` set until the prompt-conditioned boundary is resolved.
