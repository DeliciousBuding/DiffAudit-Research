# 黑盒工作台

## 当前状态

- 方向：黑盒成员推断攻击。
- 主要方法：`recon` 是已准入的黑盒产品行，也是选定用于有限尾部置信度加固的审计线路。
- 支撑方法：`CLiD`、`variation`、`H2 response-strength` 以及语义辅助分类器。
- H2 output-cloud geometry 状态：复用既有 H2 `512 / 512` response cache 的
  CPU-only review 发现强候选信号，logistic `AUC = 0.961529`、
  `TPR@1%FPR = 0.333984`、`TPR@0.1%FPR = 0.117188`；seed `177` 仍稳定，
  label-shuffle sanity 回到随机级。后续 `256 / 256` shared-position
  order-control scout 仍为 `AUC = 0.967819`、`TPR@1%FPR = 0.410156`、
  `TPR@0.1%FPR = 0.132812`，label-shuffle `AUC = 0.464066`，因此
  class-ordered seed offset 不是充分解释。同边界 seed `177` shared-position
  scout 仍为 `AUC = 0.956192`、`TPR@1%FPR = 0.285156`、
  `TPR@0.1%FPR = 0.109375`，label-shuffle `AUC = 0.484070`，说明该候选
  在 order-control 后不是单 seed 现象。但它仍只是 Research-side H2 response-cache
  geometry 候选，不是第二公开资产或产品合约。
  不要把它扩成 KDE、shadow density、repeat-count 或同 cache feature sweep；
  不要补跑完整 `512 / 512` 只为表格好看；不要新增 Platform/Runtime schema、
  runner 或 admitted bundle row。
- 已导入候选工件：协作者移交的 Stable Diffusion ReDiffuse 结果包现通过
  `diffaudit probe-rediffuse-sd-artifacts` 进行审计。导入的 `5000` 行
  `2500 / 2500` 包重放结果为 `AUC = 0.710319` 和 `ASR = 0.6846`，因此值得保留作为候选证据。同一导入子集现在也支持
  `diffaudit probe-rediffuse-sd-assets` 和
  `diffaudit score-rediffuse-sd-image`，用于围绕协作者检测器的捆绑包就绪检查和仅候选单张图像评分。该包尚未准入：该包是协作者本地移交，成员侧是类 LAION 可重复子集而非精确的论文 LAION-5B 划分，且其边界为本地模型查询黑盒而非严格的外部纯 API 黑盒。当前本地运行时仍缺少 `fire`、`pytorch_lightning`、
  `skimage`、`omegaconf` 以及本地 `CompVis/stable-diffusion-v1-4` 缓存，因此直接评分已接线但在默认解释器上尚无法端到端运行。不要请求 `coco_data`、不要下载 Stable Diffusion 权重、不要在当前周期内重跑完整的 `2500 / 2500` 路径。
- 最新公共资产关卡：`CopyMark + laion_mi` 作为干净的 Lane A 资产被阻止。有界公共子集和 `diffaudit probe-copymark-laion-mi-assets`
  显示当前公共成员 parquet 仅暴露 `url/caption`，官方成员工具仍期望隐藏的第三列 parquet，官方数值成员文件名跨度为 `9617..33905220` 而当前公共
  parquet 仅 `13396` 行，且实时抽查发现仅有 `4/10` 的前几条公共成员 URL 仍返回 `200`。将其仅保留为 Research 侧 CopyMark 支撑证据；不要将此分支升级为大规模下载、URL 恢复工作或 GPU 执行。
- 最新元数据复查：CLiD 仍因 HF 数据集授权问题受阻，而非本地登录问题。2026-05-23 已确认本地 token 存在和数据集元数据可访问，但 `mia_COCO.zip` 的认证范围访问返回 `403 restricted / not in the authorized list`。CopyMark
  `laion_ridar` 仅为支撑证据：公共 `10000 / 10000` 图像日志和聚合 `AUROC = 0.872134768572823` ROC/阈值 JSON 是有用证据，但仍没有逐行评分字段或紧凑的文件名/角色/检查点评分清单。未选择任何下载、GPU 任务或准入行。
- 候选方法：简单的图像到图像距离是有界单资产证据，而非产品行或可移植性结果。
- 活跃候选：中频同噪声残差是一个可辨别的可观测差距。评分器、采集器函数、合成微缓存写入器、真实资产 `4/4` 缓存预检以及冻结的 `64/64` 符号检查均已实现。仅种子重复保留了信号，但比较器审计显示中频带并非唯一最强的；将该线路保留为同噪声残差候选证据，而非中频特定声明。
- Variation 状态：在存在真实的成员/非成员查询图像集和端点合约之前被阻止。
- CLiD 状态：官方的公共 `inter_output/*` 重放在 CPU 上表现强劲（`AUC = 0.961277`、`TPR@1%FPR = 0.675470`、`ASR = 0.891957`），但仍仅为提示条件候选。身份清单关卡未发现公共行清单或 COCO 图像 ID 绑定。2026-05-23 复查确认该 HF ZIP 对该 token 仍不可访问，因此准入的黑盒声明仍被阻止。
- 语义辅助状态：在低 FPR 审查后为负面但有用；未选择 GPU 包。
- GPU：当前没有活跃的黑盒 GPU 任务运行。
- CommonCanvas 状态：真正的二次响应合约已就绪，但跨像素距离、CLIP 图像相似度、提示-响应一致性、多种子响应稳定性以及条件去噪损失方面表现较弱。不要通过相邻度量或去噪损失矩阵重新打开此项。
- MIDST TabDDPM 状态：精确的本地单表标签可用，官方 CITADEL/UQAM Blending++ 评分导出是迄今为止最强的 MIDST 信号（`dev+final AUC = 0.598079`、`TPR@1%FPR = 0.095750`），但仍低于 `0.60` 的重新打开阈值。更早的最近合成行、影子分布和类 MIA-EPT 机制更弱。不要扩展 Blending++ 重训练、Gower 特征矩阵、EPT 配置、TabSyn、多表或白盒 MIDST。
- Beans member-LoRA 状态：精确的已知划分目标构造修复了旧的 Beans/SD1.5 伪成员关系问题，但内部条件去噪损失较弱（`AUC = 0.414400`，反向 `0.585600`），参数增量敏感度也较弱（`AUC = 0.512000`、`TPR@1%FPR = 0.040000`）；不要扩展训练步数、秩、分辨率、提示、调度器、损失权重、时间步、层或块矩阵。
- MIA_SD 状态：仅为相关 face-LDM 代码/结果参考。公共工件不发布图像、目标检查点、精确的成员/非成员划分清单或可复用的查询/响应包；不要从此仓库抓取人员图像或训练 SD1.5。
- FMIA 状态：OpenReview 补充材料有频率滤波攻击代码和精确的划分清单，但没有目标检查点、评分数组、生成样本、ROC CSV 或度量工件；无 GPU 发布且无准入行。
- SimA 状态：官方基于评分的代码存在，包括 SD1.4/SD1.5 脚本，但公开发布有空划分/检查点链接、无发布资产、无划分清单、无目标检查点、无评分数组、无就绪验证器包；无下载、GPU 发布或准入行。
- GenAI Confessions 状态：STROLL、Carlini 和 Midjourney 设置有公共原始图像/标题输入，但缺少微调 STROLL 检查点、生成的图像到图像响应、DreamSim 距离向量、ROC/度量工件、Midjourney 查询日志和就绪验证器；无数据集下载、GPU 发布或准入行。

## 文件

| 文件 | 用途 |
| --- | --- |
| [plan.md](plan.md) | 当前状态及后续步骤。 |
| [experiment-entrypoints.md](experiment-entrypoints.md) | 运行实验的稳定 CLI 命令。 |
| [paper-matrix-2024-2026.md](paper-matrix-2024-2026.md) | 论文和方法概览。 |

当前 H2 候选边界：
[../../docs/evidence/black-box-response-strength-preflight.md](../../docs/evidence/black-box-response-strength-preflight.md)。

当前 H2 output-cloud geometry 候选：
[../../docs/evidence/h2-output-cloud-geometry-20260525.md](../../docs/evidence/h2-output-cloud-geometry-20260525.md)。

当前中频同噪声残差预检：
[../../docs/evidence/midfreq-same-noise-residual-preflight-20260512.md](../../docs/evidence/midfreq-same-noise-residual-preflight-20260512.md)。

当前中频残差评分器合约：
[../../docs/evidence/midfreq-residual-scorer-contract-20260512.md](../../docs/evidence/midfreq-residual-scorer-contract-20260512.md)。

当前中频残差采集器合约：
[../../docs/evidence/midfreq-residual-collector-contract-20260512.md](../../docs/evidence/midfreq-residual-collector-contract-20260512.md)。

当前中频残差微运行器合约：
[../../docs/evidence/midfreq-residual-tiny-runner-contract-20260512.md](../../docs/evidence/midfreq-residual-tiny-runner-contract-20260512.md)。

当前中频残差真实资产预检：
[../../docs/evidence/midfreq-residual-real-asset-preflight-20260512.md](../../docs/evidence/midfreq-residual-real-asset-preflight-20260512.md)。

当前中频残差符号检查：
[../../docs/evidence/midfreq-residual-signcheck-20260512.md](../../docs/evidence/midfreq-residual-signcheck-20260512.md)。

当前中频残差稳定性决策：
[../../docs/evidence/midfreq-residual-stability-decision-20260512.md](../../docs/evidence/midfreq-residual-stability-decision-20260512.md)。

当前中频残差稳定性结果：
[../../docs/evidence/midfreq-residual-stability-result-20260512.md](../../docs/evidence/midfreq-residual-stability-result-20260512.md)。

当前中频残差比较器审计：
[../../docs/evidence/midfreq-residual-comparator-audit-20260512.md](../../docs/evidence/midfreq-residual-comparator-audit-20260512.md)。

当前 CommonCanvas 条件去噪损失闭合：
[../../docs/evidence/commoncanvas-denoising-loss-20260513.md](../../docs/evidence/commoncanvas-denoising-loss-20260513.md)。

当前非 CLiD 重新选择：
[../../docs/evidence/non-clid-black-box-reselection.md](../../docs/evidence/non-clid-black-box-reselection.md)。

当前 recon 验证合约：
[../../docs/evidence/recon-product-validation-contract.md](../../docs/evidence/recon-product-validation-contract.md)。

当前 recon 验证结果：
[../../docs/evidence/recon-product-validation-result.md](../../docs/evidence/recon-product-validation-result.md)。

当前 recon 尾部置信度审查：
[../../docs/evidence/recon-tail-confidence-review.md](../../docs/evidence/recon-tail-confidence-review.md)。

当前 H2 简单距离边界：
[../../docs/evidence/h2-simple-distance-portability-preflight.md](../../docs/evidence/h2-simple-distance-portability-preflight.md)。

当前 variation 查询合约审计：
[../../docs/evidence/variation-query-contract-audit.md](../../docs/evidence/variation-query-contract-audit.md)。

当前 CLiD 图像身份边界：
[../../docs/evidence/clid-image-identity-boundary-contract-20260511.md](../../docs/evidence/clid-image-identity-boundary-contract-20260511.md)。

当前 CLiD 官方中间输出重放：
[../../docs/evidence/clid-official-inter-output-replay-20260515.md](../../docs/evidence/clid-official-inter-output-replay-20260515.md)。

当前 CopyMark laion_mi 公共绑定关卡：
[../../docs/evidence/copymark-laion-mi-public-binding-gate-20260517.md](../../docs/evidence/copymark-laion-mi-public-binding-gate-20260517.md)。

当前 Stable Diffusion ReDiffuse 协作者工件审计：
[../../docs/evidence/stable-diffusion-rediffuse-collaborator-artifact-20260517.md](../../docs/evidence/stable-diffusion-rediffuse-collaborator-artifact-20260517.md)。

当前 CLiD 身份清单关卡：
[../../docs/evidence/clid-identity-manifest-gate-20260515.md](../../docs/evidence/clid-identity-manifest-gate-20260515.md)。

当前 FMIA OpenReview 频率工件关卡：
[../../docs/evidence/fmia-openreview-frequency-artifact-gate-20260515.md](../../docs/evidence/fmia-openreview-frequency-artifact-gate-20260515.md)。

当前 SimA 基于评分的工件关卡：
[../../docs/evidence/sima-scorebased-artifact-gate-20260515.md](../../docs/evidence/sima-scorebased-artifact-gate-20260515.md)。

当前 GenAI Confessions 黑盒工件关卡：
[../../docs/evidence/genai-confessions-black-box-artifact-gate-20260515.md](../../docs/evidence/genai-confessions-black-box-artifact-gate-20260515.md)。

当前响应合约包预检：
[../../docs/evidence/black-box-response-contract-package-preflight.md](../../docs/evidence/black-box-response-contract-package-preflight.md)。

当前响应合约发现：
[../../docs/evidence/black-box-response-contract-discovery.md](../../docs/evidence/black-box-response-contract-discovery.md)。

当前 Beans/SD1.5 响应合约侦察：
[../../docs/evidence/beans-sd15-response-contract-scout-20260512.md](../../docs/evidence/beans-sd15-response-contract-scout-20260512.md)。

当前 Beans/SD1.5 响应合约就绪包：
[../../docs/evidence/beans-sd15-response-contract-ready-20260512.md](../../docs/evidence/beans-sd15-response-contract-ready-20260512.md)。

当前 Beans/SD1.5 简单距离侦察：
[../../docs/evidence/beans-sd15-simple-distance-scout-20260512.md](../../docs/evidence/beans-sd15-simple-distance-scout-20260512.md)。

当前 Beans/SD1.5 CLIP 距离侦察：
[../../docs/evidence/beans-sd15-clip-distance-scout-20260512.md](../../docs/evidence/beans-sd15-clip-distance-scout-20260512.md)。

当前 Beans/SD1.5 成员语义修正：
[../../docs/evidence/beans-sd15-membership-semantics-correction-20260512.md](../../docs/evidence/beans-sd15-membership-semantics-correction-20260512.md)。

当前 Beans member-LoRA 去噪损失闭合：
[../../docs/evidence/beans-lora-member-denoising-loss-scout-20260513.md](../../docs/evidence/beans-lora-member-denoising-loss-scout-20260513.md)。

当前 MIA_SD 资产裁决：
[../../docs/evidence/miasd-face-ldm-asset-verdict-20260513.md](../../docs/evidence/miasd-face-ldm-asset-verdict-20260513.md)。

当前 Beans member-LoRA 增量敏感度闭合：
[../../docs/evidence/beans-lora-delta-sensitivity-20260513.md](../../docs/evidence/beans-lora-delta-sensitivity-20260513.md)。

当前语义辅助低 FPR 审查：
[../../docs/evidence/semantic-aux-low-fpr-review.md](../../docs/evidence/semantic-aux-low-fpr-review.md)。

## 归档

已关闭的笔记位于
[../../legacy/workspaces/black-box/2026-04/](../../legacy/workspaces/black-box/2026-04/)。
