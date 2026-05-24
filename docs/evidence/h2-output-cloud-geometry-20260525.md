# H2 Output-Cloud Geometry Cache Review

> Date: 2026-05-25
> Status: candidate complementary signal / CPU-only cache review / order-control required before promotion / no GPU release / no admitted row

## Question

在已有 H2 response-strength cache 上，输出之间的几何结构是否携带不同于
seed-to-output distance 的 membership 信号？

本轮只复用现有
`workspaces/black-box/runs/h2-response-strength-512-20260501-r1/response-cache.npz`。
没有生成新响应、没有下载资产、没有运行 GPU，也没有扩展同一路线的 KDE、shadow
density、repeat-count 或特征 sweep。

## Contract

脚本：
`scripts/review_h2_output_cloud_geometry.py`

输入 cache：

| Field | Value |
| --- | ---: |
| Samples | `1024` |
| Members | `512` |
| Nonmembers | `512` |
| Timesteps | `40 / 80 / 120 / 160` |
| Repeats per timestep | `2` |
| Response shape | `[1024, 4, 2, 3, 32, 32]` |

特征只使用 output-output geometry：

| Feature family | Meaning |
| --- | --- |
| within-timestep pair RMSE | 同一 timestep 内不同 repeat 的响应距离 |
| timestep centroid RMSE | 不同 timestep 的响应云 centroid 距离 |
| response-cloud PCA trace/top share | 小响应云 Gram spectrum 的尺度和集中度 |

该脚本刻意不读取 seed-to-output distance 特征，因此不会退化成原 H2 simple
distance 评分器。

## Result

主结果：
`workspaces/black-box/artifacts/h2-output-cloud-geometry-20260525.json`

| Metric | Output-cloud logistic | Raw H2 logistic | Lowpass H2 logistic |
| --- | ---: | ---: | ---: |
| AUC | `0.961529` | `0.905693` | `0.895679` |
| ASR | `0.900391` | `0.841797` | `0.831055` |
| TPR@1%FPR | `0.333984` | `0.134766` | `0.148438` |
| TPR@0.1%FPR | `0.117188` | `0.0` | `0.025391` |

相对 raw H2：`AUC +0.055836`，`TPR@1%FPR +0.199218`，
`TPR@0.1%FPR +0.117188`。

相对 lowpass H2：`AUC +0.065850`，`TPR@1%FPR +0.185546`，
`TPR@0.1%FPR +0.091797`。

简单单特征不能解释该结果：

| Best simple view | Feature | Orientation | AUC | TPR@1%FPR | TPR@0.1%FPR |
| --- | --- | --- | ---: | ---: | ---: |
| Best AUC | `centroid_rmse_40_160` | negative | `0.801182` | `0.03125` | `0.005859` |
| Best low-FPR | `cloud_pca_top_share` | negative | `0.650913` | `0.078125` | `0.017578` |

Seed stability check：
`workspaces/black-box/artifacts/h2-output-cloud-geometry-seed177-20260525.json`

| Metric | Seed 177 |
| --- | ---: |
| AUC | `0.961048` |
| ASR | `0.900391` |
| TPR@1%FPR | `0.353516` |
| TPR@0.1%FPR | `0.130859` |

Label-shuffle sanity：
`workspaces/black-box/artifacts/h2-output-cloud-geometry-label-shuffle-20260525.json`

| Metric | Label shuffle |
| --- | ---: |
| AUC | `0.507595` |
| ASR | `0.521484` |
| TPR@1%FPR | `0.011719` |
| TPR@0.1%FPR | `0.003906` |

这说明 scorer/evaluation 管线没有明显的标签直通泄漏。

## Critical Caveat

该结果仍然不能晋升。源 cache 的响应生成存在 class-ordered seed offset：
`scripts/run_h2_response_strength_validation.py` 中 member 侧使用
`sample_offset = 0`，nonmember 侧使用 `sample_offset = len(member_indices)`。
Output-output geometry 对采样种子和响应云形态敏感，因此当前强信号可能混入
class-ordered sampling effect。

这不是要继续在同一个 cache 上补表格；它只定义一个非常窄的下一步：
如果需要推进，最多释放一个有界 order-control / reseeded / interleaved
response-cache scout，用来判断该强信号是否跨 class-order 控制保留。

## Decision

`candidate complementary signal / order-control required / no admitted row`。

保留为 Research-side 强候选，因为它满足三个有价值条件：

- 它是不同 observable：output-output cloud geometry，而不是 seed-to-output distance。
- 它在同一 H2 cache 上明显强于 raw/lowpass H2 logistic。
- 它通过了 seed-177 稳定性和 label-shuffle sanity。

但当前不做以下事情：

- 不升级到 Platform/Runtime admitted bundle。
- 不新增产品 schema、Runtime runner、UI 类型或 bundle row。
- 不在同一 cache 上展开 KDE、shadow density、repeat-count、特征族或融合 sweep。
- 不释放 GPU 或大下载。

下一次重新评估只允许基于一个 order-control cache 的结果。如果 reseeded /
interleaved cache 仍保持强 AUC 和严格尾部恢复，再讨论是否进入更正式的 H2
output-cloud 机制线；如果不保持，该候选直接关闭为 class-ordered response-cache
artifact。

## Platform and Runtime Impact

None. The admitted Platform/Runtime bundle remains the existing five rows:
`recon`, `PIA baseline`, `PIA defended`, `GSA`, and `DPDM W-1`.
