# Stable Diffusion MIA 复现材料

## 一、复现目标

本文件夹复现论文 `Towards Black-Box Membership Inference Attack for Diffusion Models`
中 Stable Diffusion 部分的黑盒成员推理攻击流程。

复现内容不是训练 Stable Diffusion，而是：

1. 使用预训练模型 `CompVis/stable-diffusion-v1-4`。
2. 准备 2500 张 LAION member 图片和 2500 张 COCO2017-val non-member 图片。
3. 使用 ReDiffuse / Stable Diffusion 重构流程得到图像相似度特征。
4. 用 SSIM 相关特征计算 membership score。
5. 输出 AUC、ASR、TPR@FPR=1%、逐图片 result.csv 和 ROC 曲线。

## 二、最终结果

当前最终 detector 使用 `attack_num=2` 与 `attack_num=5` 两组 ReDiffuse SSIM 特征融合。

| 指标 | 数值 |
|---|---:|
| AUC | `0.7103` |
| ASR | `0.6846` |
| TPR@FPR=1% | `0.0716` |

严格验证：

| 验证方式 | AUC |
|---|---:|
| holdout | `0.7046` |
| 5-fold | `0.7080 ± 0.0116` |

## 三、目录结构

```text
coco_data_20260516/
  artifacts/                    最终验收结果
  coco_data/                    COCO2017-val 非成员样本和 annotations
  runs/                         精简后的最终运行结果副本
  SD_MIA_Reproduction/          核心源码
  stable_diffusion_data/        LAION member 样本、member 列表、BLIP captions
  论文复现攻击材料_20260516/    detector、合并特征、验证表
  论文复现最终材料_20260516/    汇报/验收材料、论文 PDF、最终结果
  README.md
  目录说明.txt
  coco-2500-random.yaml
```

## 四、关键验收文件

```text
artifacts/result.csv
artifacts/metrics.json
artifacts/metrics.csv
artifacts/roc_curve.csv
artifacts/roc_curve.png
论文复现攻击材料_20260516/mia_detector_rediffuse_sweep_best_a2_a5_combined.json
论文复现攻击材料_20260516/merged_rediffuse_scores_a2_a5_combined.npz
STABLE_DIFFUSION_REPRODUCTION_STATUS.md
AUC_IMPROVEMENT_PLAN.md
```

`artifacts/result.csv` 包含：

- `image_path`
- `label`，member=1，non-member=0
- `score`
- `prediction`
- `correct`

## 五、环境说明

推荐使用已有 conda 环境：

```powershell
C:\Users\33166\miniconda3\envs\ddim_repro\python.exe
```

依赖见：

```text
SD_MIA_Reproduction/requirements.txt
```

注意：Stable Diffusion 权重 `CompVis/stable-diffusion-v1-4` 没有打包在本目录中。
复跑时需要本机 HuggingFace cache 已有该模型，或联网下载。

## 六、查看最终指标

```powershell
Get-Content .\artifacts\metrics.json
```

## 七、单张图片打分示例

请在本文件夹根目录运行：

```powershell
$py = 'C:\Users\33166\miniconda3\envs\ddim_repro\python.exe'

& $py .\SD_MIA_Reproduction\score_single_image.py `
  --image '.\stable_diffusion_data\images-random\laion_000250717.jpg' `
  --prompt 'a woman with long hair and a crown of flowers' `
  --detector-json '.\论文复现攻击材料_20260516\mia_detector_rediffuse_sweep_best_a2_a5_combined.json' `
  --feature-plan a2_a5_combined
```

输出中：

```text
score 越高，越倾向 member
prediction = 1 表示 member
prediction = 0 表示 non-member
```

## 八、黑盒边界说明

本项目没有训练或微调 Stable Diffusion，不使用训练 loss、梯度或训练过程信息。

实现方式是在本地加载 `CompVis/stable-diffusion-v1-4`，通过 Diffusers pipeline
执行 ReDiffuse / DDIM 风格重构，并根据重构相似度进行成员推理。
如果要求最严格的外部 API-only 黑盒，即只能看到 image-to-image / variation API
返回的最终图片，则需要另做 API-only 版本并单独报告。
