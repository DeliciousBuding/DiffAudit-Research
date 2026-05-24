# 灰盒 Feature-Packet 消费者线路

> 状态：已开放（2026-05-24） | 首个 admitted entry：Tracing the Roots

## 背景

DiffAudit 当前 Platform/Runtime 仅消费黑盒响应合约证据（查询图像 → 生成响应 → 逐样本评分）。
但扩散模型成员推断的研究面不仅限于黑盒——灰盒和白盒场景下，内部特征（梯度、轨迹、激活）
同样携带成员信号。

灰盒 feature-packet 消费者线路为这类证据提供 Platform/Runtime 消费通道。

## 与黑盒响应合约的区别

| 维度 | 黑盒响应合约 | 灰盒 feature-packet |
|------|-------------|-------------------|
| 证据形式 | 查询图像 + 生成响应 + 逐样本评分 | 预计算 feature tensor + 分类器 + 聚合指标 |
| 评分方式 | Runtime 逐样本执行 | Research 预计算，Runtime 消费固定数据包 |
| 权限假设 | 仅 API 访问 | 需要内部模型访问以提取特征 |
| 产品声明 | "此图像在训练集中" | "扩散轨迹特征携带可检测的成员信号" |
| 身份绑定 | 逐图像可验证 | Feature 级别，非图像身份级别 |

## 准入合约

Feature-packet 证据必须满足：

1. **固定数据包**：Feature tensor 已公开，SHA-256 hash 可验证，不可变
2. **可回放指标**：AUC/ASR/TPR@1%FPR/TPR@0.1%FPR 可从 feature tensor 和分类器重新计算
3. **来源清晰**：论文/补充材料/supplement 来源明确，checksum 可验证
4. **声明边界**：产品 copy 必须显式标注"feature-packet 证据，非逐图像身份证据"
5. **独立 schema**：不混用黑盒响应合约的 Platform/Runtime schema

## Tracing the Roots — 首个 Admitted Entry

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

## Platform/Runtime 影响

- **Research**：`admitted-evidence-bundle.json` 新增 `tracing-roots` entry
- **Runtime**：无需新增 runner——feature-packet 不需要逐样本运行时评分
- **Platform**：新增 `feature-packet` 结果类型，展示 feature-packet 语义而非逐图像结果
- **产品 copy**：标注"灰盒轨迹特征证据——展示扩散模型内部特征携带成员信号"

## 修订历史

| 日期 | 变更 |
|------|------|
| 2026-05-23 | 初始版本，开放灰盒 feature-packet 线路，Tracing the Roots 首个 admitted |
