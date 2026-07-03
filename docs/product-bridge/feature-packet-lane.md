# 灰盒 Feature-Packet 候选消费者线路

> 状态：deferred candidate design note / 未开通 Platform 或 Runtime 通道（2026-05-25 consumer verdict） | 当前正面候选：Tracing the Roots

## 背景

DiffAudit 当前 Platform/Runtime 仅消费黑盒响应合约证据（查询图像 → 生成响应 → 逐样本评分）。
但扩散模型成员推断的研究面不仅限于黑盒——灰盒和白盒场景下，内部特征（梯度、轨迹、激活）
同样携带成员信号。

灰盒 feature-packet 候选消费者线路用于定义未来可能的 Platform/Runtime 消费边界。
截至 2026-05-25，它不是已准入消费通道，也不会因为 Tracing the Roots 单例立刻开通。
最新 consumer verdict 见
[../evidence/feature-packet-channel-consumer-verdict-2026-05-25.md](../evidence/feature-packet-channel-consumer-verdict-2026-05-25.md)。

## 与黑盒响应合约的区别

| 维度 | 黑盒响应合约 | 灰盒 feature-packet |
|------|-------------|-------------------|
| 证据形式 | 查询图像 + 生成响应 + 逐样本评分 | 预计算 feature tensor + 分类器 + 聚合指标 |
| 评分方式 | Runtime 逐样本执行 | Research 预计算，Runtime 消费固定数据包 |
| 权限假设 | 仅 API 访问 | 需要内部模型访问以提取特征 |
| 产品声明 | "此图像在训练集中" | "扩散轨迹特征携带可检测的成员信号" |
| 身份绑定 | 逐图像可验证 | Feature 级别，非图像身份级别 |

## 候选准入合约

Feature-packet 证据若要从 Research 候选晋升为 Platform/Runtime 准入结果，必须满足：

1. **固定数据包**：Feature tensor 已公开，SHA-256 hash 可验证，不可变
2. **可回放指标**：AUC/ASR/TPR@1%FPR/TPR@0.1%FPR 可从 feature tensor 和分类器重新计算
3. **来源清晰**：论文/补充材料/supplement 来源明确，checksum 可验证
4. **声明边界**：产品 copy 必须显式标注"feature-packet 证据，非逐图像身份证据"
5. **独立 schema**：不混用黑盒响应合约的 Platform/Runtime schema

## Tracing the Roots — 当前正面候选

### 证据摘要

| 指标 | 值 |
|------|-----|
| 训练样本 | 2000（1000 成员 + 1000 外部） |
| 评估样本 | 2000（1000 成员 + 1000 外部） |
| 特征维度 | 1002（loss + image-gradient + parameter-gradient 轨迹） |
| 评估 AUC | 0.815826 |
| 评估 TPR@1%FPR | 0.134 |
| 评估 TPR@0.1%FPR | 0.038 |
| 评估准确率 | 0.7375 |

### Feature Tensor 完整性

| 文件 | SHA-256 |
|------|---------|
| `train/member.pt` | `f02f16a02d80c067865d7902d653eed65676c73f1472fb7f04b090d3afb89ebe` |
| `train/external.pt` | `4f5a54efb8683237691c79f71f72fccc787db4e32fe9352faa6f528f111bc7bd` |
| `eval/member.pt` | `93b9e5eefbab1a820a4945bce79dfa95f5799df2b77ba771d8bfe159e9fcdaa9` |
| `eval/external.pt` | `ee9829eaa32d6a54c73b0851513cd5edeea7da2b810d61fb99b330429909616e` |

### 来源

- OpenReview NeurIPS 2025 supplement：`https://openreview.net/forum?id=mE74JKHTCE`
- Supplement SHA-256：`62e9ae3833bcc0f102612d05898262eea2b6025fe8949a72c3f055a8534c7b41`
- 回放代码：`train.py`、`eval.py`、`utils.py`（supplement 内含）

### 可主张

- 扩散轨迹特征（loss + 梯度轨迹）在 held-out 评估集上携带可检测的成员信号
- AUC=0.816，TPR@1%FPR=0.134，信号非平凡
- Feature tensor 公开可验证，不依赖任何外部 API 或 gated 数据集

### 不可主张

- 任何特定 CIFAR-10 图像的成员身份
- 黑盒条件下可检测的成员信号
- 可推广到其他模型/数据集的结论（无特征再生脚本）
- 已经进入现有 Platform/Runtime `admitted-evidence-bundle.json`

## Platform/Runtime 影响

- **Research**：保留 `tracing-roots` candidate card 和 feature-packet metric artifact；不改现有 admitted bundle
- **Runtime**：当前无需新增 runner；若未来准入，应作为固定 feature-packet 结果类型，而不是逐样本运行时评分
- **Platform**：当前不新增 `feature-packet` 展示类型；若未来准入，必须先有独立 schema 和产品桥接交接
- **产品 copy**：当前不得写成已准入审计证据；只能在 Research / future-work 语境中标注为"灰盒轨迹特征候选证据"

## 2026-05-25 Consumer Verdict

本线路当前 deferred。原因不是 Tracing the Roots 信号弱，而是公开面仍只有一个
feature-packet singleton。2026-05-25 窄范围复查没有找到第二个公开非同源
image/latent-image diffusion membership feature-packet，也没有找到 raw checkpoint、
raw sample manifest 或 feature-regeneration assets。为单例直接新增 schema、bundle、
validator、tests、Platform 展示类型和 Runtime runner 属于低收益工程化。

## 晋升前置条件

Tracing the Roots 或其他 feature-packet 证据若要进入 Platform/Runtime，至少需要先满足
以下触发条件之一：

1. 第二个公开、可校验、非同源的 diffusion feature-packet，带固定 member/nonmember
   feature tensors、metrics 和来源 checksum。
2. raw target checkpoint identity、raw sample manifests 和可再生 feature extraction contract。
3. DiffAudit 明确决定打开灰盒/白盒 feature-level 产品线，并接受它不是逐图像 identity proof。

触发后才进入具体准入工程，至少包括：

1. 独立于黑盒响应合约的 schema 和机器可读 bundle，不复用现有五行 `admitted-evidence-bundle.json`。
2. 对 `feature-packet` 权限假设、非逐图像身份边界、低 FPR 解释和产品 copy 的 reviewed handoff。
3. `scripts/validate_attack_defense_table.py`、bundle export、测试和产品桥接文档同步更新。
4. 明确说明它是灰盒 feature-level 信号，不是 raw checkpoint / image query-response / per-image identity proof。

## 修订历史

| 日期 | 变更 |
|------|------|
| 2026-05-23 | 初始版本，提出灰盒 feature-packet 线路和 Tracing the Roots 候选 |
| 2026-05-25 | 修正消费者边界：该线路为候选合约，Tracing the Roots 尚未进入 Platform/Runtime admitted bundle |
| 2026-05-25 | Consumer verdict：公开面没有第二个可用 feature-packet 或 raw regeneration assets，本线路 deferred，不开通 Platform/Runtime 通道 |
