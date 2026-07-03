# Feature-Packet 通道消费者裁决

> Date: 2026-05-25
> Status: consumer verdict / feature-packet channel deferred / no Platform or Runtime schema / no admitted row / no download / no GPU release

## 问题

是否应该因为 Tracing the Roots 的正面 feature-packet replay，立刻为
Platform/Runtime 开通一个灰盒 `feature-packet` 消费通道？

本轮只做消费者边界裁决，不运行模型、不下载数据、不新增 CLI、validator 或 bundle
schema。目标是判断一个产品/Runtime 通道是否现在值得开，而不是重复证明
Tracing the Roots 分数为正。

## 现有正面证据

Tracing the Roots 仍是有效的 Research 侧正面证据：

| 指标 | 值 |
| --- | ---: |
| Eval AUC | `0.815826` |
| Eval accuracy | `0.737500` |
| TPR@1%FPR | `0.134000` |
| TPR@0.1%FPR | `0.038000` |

这个结果说明公开的扩散轨迹 feature tensor 携带非平凡成员信号。它不说明
DiffAudit 已经拥有 raw checkpoint、raw member/nonmember image IDs、可再生特征脚本
或图像 query-response 证据。

## 2026-05-25 窄范围公开面复查

复查只查能改变消费者决策的事实：是否已经出现第二个公开 feature-packet，
或是否出现 raw provenance / regeneration assets。

| Surface | Query | Result |
| --- | --- | --- |
| GitHub repos | `diffusion membership feature tensor` | `[]` |
| GitHub repos | `diffusion trajectory membership` | `[]` |
| GitHub repos | `membership inference diffusion features` | `[]` |
| GitHub code | `member.pt external.pt diffusion` | `[]` |
| Hugging Face datasets API | `diffusion membership feature`; `diffusion trajectory membership`; `membership inference diffusion feature packet` | no dataset entries returned |
| Hugging Face models API | same three queries | no model entries returned |
| arXiv exact query | `all:"diffusion trajectory" AND all:"membership inference"` | only Tracing the Roots / `2411.07449v3` |
| arXiv broader trajectory query | `all:"diffusion" AND all:"membership inference" AND all:"trajectory"` | returns already-covered or non-feature-packet lines such as SimA, trajectory-generation privacy, PIA, withdrawn DLM, Tracing the Roots, and RareGraph-Synth |

The live check found no second public image/latent-image diffusion membership
feature-packet suitable for a Platform/Runtime consumer lane.

## 裁决

不在 2026-05-25 开通 Platform/Runtime `feature-packet` 通道。

原因不是 Tracing the Roots 信号弱，而是消费者证据面太窄：

- 只有一个正面 feature-packet singleton，无法证明 schema 可复用。
- 公共包不包含 raw target checkpoint identity、raw sample IDs 或 feature regeneration contract。
- 权限假设是灰盒/白盒内部特征，不是当前产品五行 bundle 的黑盒/白盒既有消费语义。
- 产品 copy 容易被误写成逐图像成员身份判断，但当前证据只支持 feature-level 信号。
- 为单例新增 schema、bundle、validator、tests 和 UI/Runtime 交接是低收益工程化。

当前状态：

- Tracing the Roots 保留为 `positive-provenance-limited` Research 证据。
- `docs/product-bridge/feature-packet-lane.md` 只保留为 deferred candidate design note。
- `admitted-evidence-bundle.json` 仍只有五行：`recon`、`PIA baseline`、
  `PIA defended`、`GSA`、`DPDM W-1`。
- 不改变 Platform schema、Runtime runner、推荐逻辑、产品文案或导出脚本。
- `active_gpu_question = none`，`next_gpu_candidate = none`，
  `CPU sidecar = none selected after feature-packet channel consumer verdict`。

## Reopen 条件

只有出现以下条件之一，才重新评估 feature-packet 消费通道：

- 第二个公开、可校验、非同源的 diffusion feature-packet，带固定 member/nonmember
  feature tensors、metrics 和来源 checksum；
- Tracing the Roots 作者或其他公开源发布 raw target checkpoint identity、
  raw sample manifests 和可再生 feature extraction contract；
- DiffAudit 明确决定打开灰盒/白盒 feature-level 产品线，并接受它不是逐图像
  identity proof 的产品边界。

## Stop 条件

不要围绕 Tracing the Roots 单例新增 Platform/Runtime schema、validator、bundle export、
测试矩阵、UI 展示类型或 Runtime runner。不要下载 raw CIFAR/CelebA-HQ/FFHQ、
target checkpoints、generated images，或启动 feature-family / timestep /
classifier / optimizer sweep。

