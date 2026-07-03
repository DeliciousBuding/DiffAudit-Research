# H2 Output-Cloud Geometry Cache Review

> Date: 2026-05-25
> Status: candidate complementary signal / order-control scout passed / shared-position seed-stable / cross-cache transfer strong / no admitted row / no 512/512 rerun selected

## Question

在已有 H2 response-strength cache 上，输出之间的几何结构是否携带不同于
seed-to-output distance 的 membership 信号？

第一轮只复用现有
`workspaces/black-box/runs/h2-response-strength-512-20260501-r1/response-cache.npz`。
随后只释放一个有界 `256 / 256` shared-position order-control scout，用来回答
class-ordered seed-offset caveat；再释放一个同边界的 seed `177` 稳定性 scout，
用来判断 order-control 后的强信号是否只是单 seed 现象。最后只做一次
CPU-only existing-cache transfer review，用来检查 seed `176` 和 seed `177`
两份 shared-position response cache 之间的 output-cloud logistic 是否能迁移。
没有下载资产，也没有扩展同一路线的 KDE、shadow density、repeat-count 或特征
sweep。

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

## Shared-Position Order-Control Scout

源 `512 / 512` cache 的响应生成存在 class-ordered seed offset：
`scripts/run_h2_response_strength_validation.py` 的历史默认行为是 member 侧
`sample_offset = 0`，nonmember 侧 `sample_offset = len(member_indices)`。
Output-output geometry 对采样种子和响应云形态敏感，因此必须检查强信号是否只是
class-ordered sampling effect。

本轮只加入一个窄的 seed policy 控制：
`scripts/run_h2_response_strength_validation.py --seed-offset-policy shared-position`。
该模式让 member / nonmember 使用相同 per-position seed offset，并在
`summary.json` 中标记 `order_control_scout = true`。运行边界为
`256 / 256`，timesteps `40 / 80 / 120 / 160`，repeats `2`，seed `176`，
holdout repeats `7`，bootstrap iters `100`。GPU scout 用时 `208.866516s`。

Runner summary 的 H2 distance scorer 在 shared-position 下仍为正但尾部弱：

| Metric | Raw H2 logistic | Lowpass H2 logistic |
| --- | ---: | ---: |
| AUC | `0.906967` | `0.898102` |
| ASR | `0.837891` | `0.828125` |
| TPR@1%FPR | `0.058594` | `0.066406` |
| TPR@0.1%FPR | `0.003906` | `0.003906` |

Output-cloud geometry review on the same shared-position cache:
`workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-256-20260525.json`

| Metric | Shared-position `256 / 256` |
| --- | ---: |
| AUC | `0.967819` |
| ASR | `0.923828` |
| TPR@1%FPR | `0.410156` |
| TPR@0.1%FPR | `0.132812` |

Label-shuffle sanity for the shared-position cache:
`workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-256-label-shuffle-20260525.json`

| Metric | Shared-position label shuffle |
| --- | ---: |
| AUC | `0.464066` |
| ASR | `0.505859` |
| TPR@1%FPR | `0.003906` |
| TPR@0.1%FPR | `0.0` |

Same-size historical class-ordered subset from the old cache:
`workspaces/black-box/artifacts/h2-output-cloud-geometry-class-ordered-subset-256-20260525.json`

| Metric | Class-ordered subset `256 / 256` |
| --- | ---: |
| AUC | `0.967438` |
| ASR | `0.916016` |
| TPR@1%FPR | `0.179688` |
| TPR@0.1%FPR | `0.105469` |

Class-ordered subset label shuffle:
`workspaces/black-box/artifacts/h2-output-cloud-geometry-class-ordered-subset-256-label-shuffle-20260525.json`

| Metric | Class-ordered subset label shuffle |
| --- | ---: |
| AUC | `0.427902` |
| ASR | `0.5` |
| TPR@1%FPR | `0.0` |
| TPR@0.1%FPR | `0.0` |

Interpretation: shared-position order-control did not collapse the output-cloud
geometry signal, and its label-shuffle check returns random-level. This removes
the previous class-ordered seed-offset caveat as a sufficient explanation for
the signal. The result still does not imply product admission: it is one
controlled scout on H2 DDPM/CIFAR10 response-cache geometry, not a second
public asset or Platform/Runtime contract.

## Shared-Position Seed-177 Stability Scout

为避免把 order-control 结论建立在单个 random seed 上，下一步只跑同边界
`256 / 256` shared-position seed `177`。运行边界不扩大：timesteps
`40 / 80 / 120 / 160`，repeats `2`，holdout repeats `7`，bootstrap iters
`100`。GPU scout 用时 `185.470864s`。

Runner summary 的 H2 distance scorer：

| Metric | Raw H2 logistic | Lowpass H2 logistic |
| --- | ---: | ---: |
| AUC | `0.911255` | `0.896698` |
| ASR | `0.851562` | `0.828125` |
| TPR@1%FPR | `0.113281` | `0.093750` |
| TPR@0.1%FPR | `0.0` | `0.062500` |

Output-cloud geometry review:
`workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-seed177-256-20260525.json`

| Metric | Shared-position seed `177` |
| --- | ---: |
| AUC | `0.956192` |
| ASR | `0.896484` |
| TPR@1%FPR | `0.285156` |
| TPR@0.1%FPR | `0.109375` |

Label-shuffle sanity:
`workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-seed177-256-label-shuffle-20260525.json`

| Metric | Seed `177` label shuffle |
| --- | ---: |
| AUC | `0.484070` |
| ASR | `0.513672` |
| TPR@1%FPR | `0.023438` |
| TPR@0.1%FPR | `0.011719` |

Interpretation: the shared-position output-cloud signal remains strong under
seed `177`, and label shuffle stays random-level. Together with seed `176`, this
supports the narrower conclusion that output-cloud geometry is a stable H2
mechanism candidate after seed-offset control. It still does not create a
second public asset, a product contract, or an admitted row.

## Cross-Cache Transfer Review

脚本：
`scripts/review_h2_output_cloud_transfer.py`

主结果：
`workspaces/black-box/artifacts/h2-output-cloud-transfer-shared-position-256-20260525.json`

该 review 只读取现有两份 `256 / 256` shared-position response cache：

| Cache | Path |
| --- | --- |
| Seed `176` | `workspaces/black-box/runs/h2-response-strength-256-shared-position-20260525-r1/response-cache.npz` |
| Seed `177` | `workspaces/black-box/runs/h2-response-strength-256-shared-position-seed177-20260525-r1/response-cache.npz` |

Primary transfer 使用 repeated stratified folds：在 source cache 的 train fold
训练 logistic scorer，然后只在 target cache 中对应 held-out sample identities 上
打分。这样避免把两份 cache 中相同 sample identities 的 all-train/all-test
diagnostic 误当成主结论。same-sample 全量迁移只写入 JSON 的 diagnostic 区块。

| Direction | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| seed `176` -> seed `177` | `0.948990` | `0.884766` | `0.375000` | `0.058594` |
| seed `177` -> seed `176` | `0.970520` | `0.935547` | `0.390625` | `0.074219` |

Decision gate：`mean_auc = 0.959755`，`min_tpr_at_1pct_fpr = 0.375000`，
`min_tpr_at_0_1pct_fpr = 0.058594`，verdict =
`cross_cache_transfer_strong_candidate`。

Interpretation: 这不是新资产，也不是产品消费合约，但它比单 cache review 更强：
output-cloud geometry 在两个独立生成的 shared-position response cache 之间保持可迁移，
并且主结果不依赖 same-sample 全量训练/测试诊断。该结论只支持 Research-side
机制候选更稳，不释放新的 GPU、大下载、Platform/Runtime schema 或 bundle row。

## Decision

`candidate complementary signal / order-control scout passed / seed-stable / cross-cache transfer strong / no admitted row`。

保留为 Research-side 强候选，因为它满足三个有价值条件：

- 它是不同 observable：output-output cloud geometry，而不是 seed-to-output distance。
- 它在同一 H2 cache 上明显强于 raw/lowpass H2 logistic。
- 它通过了 seed-177 稳定性和 label-shuffle sanity。
- 它在 `256 / 256` shared-position order-control scout 中没有因 seed-offset 控制而坍塌。
- 它在 shared-position seed `177` scout 中仍保持强 AUC 和非零严格尾部恢复。
- 它在 seed `176` / seed `177` 两份 shared-position response cache 之间通过了
  fold-disjoint transfer review，主结果 `mean_auc = 0.959755`，严格尾部非零。

但当前不做以下事情：

- 不升级到 Platform/Runtime admitted bundle。
- 不新增产品 schema、Runtime runner、UI 类型或 bundle row。
- 不在同一 cache 上展开 KDE、shadow density、repeat-count、特征族或融合 sweep。
- 不把 same-sample all-train/all-test transfer diagnostic 当成 headline 结果。
- 不释放完整 `512 / 512` shared-position GPU rerun 或大下载；当前 `256 / 256`
  order-control 与 cross-cache transfer 已经回答了会改变路线的 caveat。

下一次重新评估不应是同 cache feature sweep 或为了表格好看的 `512 / 512` 补跑。
只有在需要正式晋升机制线、发现第二公开资产、或要建立独立消费合约时，才重新定义
更高成本的验证任务。

## Platform and Runtime Impact

None. The admitted Platform/Runtime bundle remains the existing five rows:
`recon`, `PIA baseline`, `PIA defended`, `GSA`, and `DPDM W-1`.
