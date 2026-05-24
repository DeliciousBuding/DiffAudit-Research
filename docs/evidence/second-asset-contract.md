# 第二资产合约

> 日期：2026-05-23
> 状态：Research 侧合约定义 / 无 GPU 释放 / 无候选选定
>
> 本文档定义了一个候选必须满足的最低要求，才能被视为真正的"第二资产"——一个新的扩散模型目标家族，将证据扩展到当前单一 (DDPM, CIFAR-10) 面之外。

## 1. 为什么需要第二资产

所有五条已准入 Platform/Runtime 证据行共享同一个资产家族：

| 行 | 线路 | 方法 | 模型 | 数据集 |
| --- | --- | --- | --- | --- |
| recon DDIM public-100 step30 | 黑盒 | recon | Stable Diffusion v1.5 + DDIM | 公开子集 |
| PIA GPU512 baseline | 灰盒 | PIA | CIFAR-10 DDPM | CIFAR-10 |
| PIA GPU512 + dropout defense | 灰盒 | PIA | CIFAR-10 DDPM (defended) | CIFAR-10 |
| GSA 1k-3shadow | 白盒 | GSA | CIFAR-10 DDPM | CIFAR-10 |
| GSA 1k-3shadow + DPDM W-1 | 白盒 | GSA | DPDM / Diffusion-DP | CIFAR-10 |

五行中有四行使用同一个目标模型家族（DDPM on CIFAR-10 32x32
unconditional）。第五行使用 DPDM，它是同一架构的 DP 训练变体。这是同一个面。

为了科学有效性，"扩散模型成员关系可被审计"这一主张必须在至少一个真正不同的
目标家族上得到验证——不同的数据集、不同的架构、不同的条件范式，或不同的模态，
且具有真实的 member/nonmember ground truth。

## 2. 现有已准入资产模式（参考）

每条已准入行均符合以下模式：

### 2.1 Target Identity

- **模型架构**：已指定（DDPM, DPDM）
- **Checkpoint**：Workspace 已验证的 checkpoint 目录，包含固定的 state dict
- **格式**：Accelerate checkpoint 目录（白盒）或原始 `.pt`（灰盒）
- **训练溯源**：CIFAR-10 数据集，已知训练配方
- **可哈希性**：Checkpoint 本地存储且经 workspace 验证，尽管并非每条已准入行都存储了 checkpoint 文件本身的公开 SHA-256

### 2.2 Split 合约

- **成员定义**：源自 CIFAR-10 train split（50,000 张图像）
- **非成员定义**：源自 CIFAR-10 test split（10,000 张图像）
- **索引清单**：精确的 numpy `.npz` 数组，包含 `mia_train_idxs`、
  `mia_eval_idxs` 和 `ratio`（如适用）
- **可验证性**：划分文件随资产包存储；索引可通过从规范 CIFAR-10 归档中重新提取来复现

### 2.3 Score 合约

- **分辨率**：行级别——每个评估样本一个 score
- **包大小**：已知基数（例如 PIA 每 split 512，GSA 2000）
- **Score 类型**：连续标量（损失值、分类器激活值、DreamSim 距离）
- **格式**：包含指标数组的 JSON 摘要；每次运行一个规范的 summary.json

### 2.4 Metric 合约

四项标准头条指标：

- **AUC**: Area under the ROC curve
- **ASR**: Attack success rate at a fixed threshold
- **TPR@1%FPR**: True positive rate at 1% false positive rate
- **TPR@0.1%FPR**: True positive rate at 0.1% false positive rate

### 2.5 低 FPR 解释

所有已准入行使用相同的有限经验尾部解释：

- 非成员分母 (N) 是固定且已知的
- TPR@1%FPR 使用约 N/100 个假阳性
- TPR@0.1%FPR 使用约 N/1000 个假阳性
- 这些是有限包读数，而非连续校准估计
- 最小非零 FPR 为 1/N

### 2.6 溯源

- **资产等级**：`single-machine-real-asset` 或 `real-asset-closed-loop`
- **证据级别**：`runtime-mainline`（DPDM 为 `runtime-smoke`）
- **状态**：`workspace-verified`
- **来源**：规范数据集归档（cifar-10-python.tar.gz），具有已知溯源
- **运行输出**：来自已记录运行的规范 summary.json

## 3. 最低第二资产合约

候选必须通过全部六关。若任何一关失败，该候选不能作为第二资产用于科学可移植性主张。

### 第一关：Target Identity

| 要求 | 含义 |
| --- | --- |
| 架构已指定 | 模型类别、参数数量和架构名称（如 DDPM, DiT, EDM, TabDDPM, LDM）必须有文档记录。 |
| Checkpoint 存在 | 一个冻结的、已训练的模型 checkpoint 必须可公开访问或本地存储，并具有可验证的 SHA-256 哈希。仅有训练代码是不够的。 |
| Checkpoint 可访问 | Checkpoint 链接必须可解析（HTTP 200 或等效）。返回 HTTP 401 或 403 的 Google Drive 链接视为阻断。 |
| 训练溯源已知 | 用于训练目标的数据集以及训练配方（epochs、超参数、数据预处理）必须有文档记录。 |
| 身份固定 | Checkpoint 在评估之间不得变更。"下载并从头训练"的说明不是固定身份。 |

**以下情况判定失败**：checkpoint 缺失、不可访问、不可验证，或仅提供"下载并从头训练"。

### 第二关：Split 合约

| 要求 | 含义 |
| --- | --- |
| Member split 存在 | 精确的成员样本清单（索引、文件名或行 ID）必须可公开获取或本地存储，并具有可验证哈希。 |
| Nonmember split 存在 | 精确的非成员清单，来自同一领域但与训练集不相交，必须以相同标准可用。 |
| 成员语义清晰 | 成员定义必须无歧义，且符合标准成员推断实践（成员 = 曾在该目标模型的训练集中）。 |
| Split 基数已知 | 必须公布精确的 member/nonmember 数量。未知或近似数量不可接受。 |
| Split 可哈希 | 划分文件必须存储为固定产物（`.npz`、`.npy`、`.json`、`.csv`），具有可验证的 SHA-256 哈希。 |
| Split 溯源有文档 | 源数据集和划分推导方法必须有文档记录。无溯源追踪的划分不可验证。 |

**以下情况判定失败**：划分索引缺失、数量为近似值、划分推导无文档，或已发布清单无法重新绑定到公开面（例如行标识符不再可解析）。

### 第三关：Query/Response 或 Score 覆盖

| 要求 | 含义 |
| --- | --- |
| 行级别 score 存在 | 每个评估样本一个 score，存储为长度为 N（member + nonmember 数量）的向量。仅有聚合指标是不够的。 |
| Score 包公开或已存储 | Score 数组必须可公开下载或存储在 DiffAudit workspace 中，具有可验证哈希。 |
| Score 类型已指定 | Score 的含义（损失、似然、距离、分类器置信度、误差比）必须有文档记录。 |
| 标签完整 | 每个 score 都有对应的 member/nonmember 标签。 |
| 生成代价有界 | 若 score 不是预计算的，则生成它们的命令必须具有已知的有界代价（GPU 小时、挂钟时间）。"训练并运行全部"不是有界的。 |

**以下情况判定失败**：仅有聚合指标、score 数组缺失、标签不完整，或生成 score 的路径无界。

### 第四关：Metric 合约

| 要求 | 含义 |
| --- | --- |
| 四项头条指标齐全 | AUC, ASR, TPR@1%FPR, TPR@0.1%FPR 必须可计算或已发布。 |
| 有限尾部解释 | 必须报告非成员分母，以便评估 FPR 粒度。 |
| 最小非零 FPR | 必须声明（1/N，其中 N 为非成员数量）。 |
| 指标来源可验证 | 指标必须可追溯到特定的 score 数组或运行摘要。无 score 溯源的声明指标不可验证。 |

**以下情况判定失败**：仅报告 AUC、非成员分母未知，或指标从论文复制而无产物支撑。

### 第五关：溯源与可验证性

| 要求 | 含义 |
| --- | --- |
| 所有产物可哈希 | Checkpoint、划分文件、score 数组和指标摘要应各自具有可验证哈希，或存储在 DiffAudit workspace 的版本控制下。 |
| 无单点故障溯源 | Checkpoint 不得依赖单个研究者的本地磁盘或临时的 Google Drive 链接。 |
| 重放已定义 | 存在一个有界命令，可从 checkpoint 和划分复现 score。 |
| 论文溯源不够 | 没有公开产物的论文结果不满足此关。 |

**以下情况判定失败**：产物仅存于论文、仅存于 Google Drive，或需要联系作者获取关键缺失部分。

### 第六关：面增量（第二资产之"第二"）

| 要求 | 含义 |
| --- | --- |
| 不同于当前面 | 候选必须在至少一个维度上不同于当前 DDPM/CIFAR-10 面：数据集、模型架构、条件范式或模态。 |
| 增量有文档 | 具体差异必须明确说明（例如"相同 DDPM 架构，但 CIFAR-100 数据集替代 CIFAR-10"）。 |
| 增量提供科学价值 | 表面性变更（不同随机种子、不同训练 epoch）不是真正的第二面。 |

**可接受的增量**：

| 类别 | 示例 | 科学价值 |
| --- | --- | --- |
| 相同架构，不同数据集 | DDPM on CIFAR-100 或 STL-10 | 测试成员推断跨视觉领域的泛化性 |
| 不同架构，相同数据集 | DiT on CIFAR-10, EDM on CIFAR-10 | 测试架构是否影响可审计性 |
| 条件扩散 | Stable Diffusion + exact member LoRA | 测试条件化是否改变攻击面 |
| 不同模态 | TabDDPM on tabular data, graph diffusion, audio diffusion | 测试扩散成员推断是否超越图像领域 |

**不可作为第二面的情况**：

- 相同 DDPM/CIFAR-10 使用不同攻击方法（这是不同的方法，而非不同的资产）
- 相同 DDPM/CIFAR-10 使用不同防御（这是不同的防御，而非不同的资产）
- 相同 DDPM/CIFAR-10 使用不同随机种子或训练 epoch（无真正的面增量）

## 4. 当前路径快速评估

### 4.1 同家族：DDPM on CIFAR-100 / STL-10 / Tiny-IN

| Gate | Status |
| --- | --- |
| Target identity | **Fail**。ReDiffuse OpenReview 补充材料有 DDPM 攻击/训练代码和精确的划分清单，但没有已训练的 checkpoint。FMIA OpenReview 补充材料同理。 |
| Split contract | **Pass with caveat**。存在带哈希的精确 `.npz` 清单：CIFAR100 (25000/25000)、STL10 (50000/50000)、Tiny-IN (50000/50000)。2026-05-25 STL-10 预检确认 `50k / 50k` 索引可绑定到本地 STL-10 unlabeled payload，且低层图像统计 holdout probe 近随机；但 `STL10_train_ratio0.5.npz` 与 `TINY-IN_train_ratio0.5.npz` byte-identical，削弱独立 split provenance 解释。 |
| Score coverage | **Weak local only**。2026-05-25 本地 bounded scout 已生成 `256 / 256` score packet，但这是 `300` step 自训练 tiny target，不是公开第三方 score 包。 |
| Metric contract | **Weak local only**。bounded scout 指标为随机级：`AUC = 0.4996337890625`、`ASR = 0.509765625`、`TPR@1%FPR = 0.01171875`、`TPR@0.1%FPR = 0.0`。 |
| Provenance | **Partial**。划分可哈希，STL-10 管线资源预检和 bounded scout 已通过，但缺少公开第三方 checkpoint / score artifact。 |
| Surface delta | **Pass**。不同数据集是真正的面增量。 |

**当前结论**：已发布的 STL-10 划分索引足以跑通本地 bounded scout，但
`300` step tiny target 的固定 timestep denoising-loss 没有成员信号。因此当前最短
闭合路径不再是继续堆 step/seed/timestep 矩阵，而是等待公开第三方 checkpoint /
score packet，或提出真正不同的成员 observable。CIFAR-100 仍是同路径备选，但在
STL-10 负结果后不应默认释放 GPU。

**风险**：自训练 checkpoint 的证据力弱于公开第三方 checkpoint。训练配方必须有
文档记录且可复现，结果才能被独立验证。bounded scout 结果是弱结果，不得写成
第二资产闭合。

### 4.2 MIDM FFHQ

| Gate | Status |
| --- | --- |
| Target identity | **Fail**。宣传的 Google Drive checkpoint 返回 HTTP 401。 |
| Split contract | **Partial**。脚本在本地生成 `ffhq_1000_idx.npy`，但无固定的公开清单。 |
| Score coverage | **Fail**。未发布 `loss_ffhq_1000_ddpm.h5py` 或指标 JSON。 |
| Metric contract | **Partial**。代码在 1000/1000 标签上定义了 TPR-at-fixed-FPR 指标。 |
| Provenance | **Fail**。Checkpoint 和划分不可独立验证。 |
| Surface delta | **Pass**。FFHQ（面部图像，128x128）是与 CIFAR-10 不同的领域。 |

**判定**：阻断。仅当 checkpoint 变为可访问且 score 包已发布时重新开启。

### 4.3 CopyMark / LAION-mi

| Gate | Status |
| --- | --- |
| Target identity | **Partial**。Stable Diffusion 是公开的，但具体的 LoRA/member 设置依赖于公开 parquet 行绑定。 |
| Split contract | **Fail**。官方 member 数字文件名无法映射到当前公开的 `members.parquet` 行；公开 parquet 仅暴露 `url` 和 `caption` 列。 |
| Score coverage | **Partial**。官方 score 产物存在，但行绑定已断裂。 |
| Metric contract | **Partial**。指标存在于官方产物中。 |
| Provenance | **Fail**。公开面无法将 score 重新绑定到 members。 |
| Surface delta | **Pass**。Stable Diffusion + LAION subset 是不同的条件范式。 |

**判定**：阻塞。仅当作者发布紧凑的行绑定清单或恢复公开标识符列时重新开启。

### 4.4 MIDST TabDDPM（表格数据）

| Gate | Status |
| --- | --- |
| Target identity | **Pass**。MIDST 挑战赛提供 70 个 TabDDPM 模型文件夹（30 train + 20 dev + 20 final），包含合成表格。 |
| Split contract | **Pass**。MIDST 挑战赛行具有已知标签（在挑战赛各阶段内，每个模型 100 members、100 nonmembers）。 |
| Score coverage | **Partial**。本地 scout 已生成行级别 score（最近邻距离、EPT 误差画像、影子分布散度）。 |
| Metric contract | **Pass**（本地 scout）。Score 存在但迁移阶段信号弱（dev+final AUC ~0.53）。 |
| Provenance | **Pass**。本地 scout 存储在 workspace 产物中。 |
| Surface delta | **Pass**。表格数据是真正不同的模态。 |

**判定**：迁移阶段信号弱，阻止晋升。训练阶段 AUC 强（EPT 约 0.85+），但
dev/final 不携带信号（AUC ~0.53）。这作为跨模态支撑证据有价值，但不能作为
已准入的第二资产。仅当新的公开产物或真正新的表格扩散成员可观测量改变了
dev/final 迁移叙事时重新开启。

### 4.5 MT-MIA 关系表格

| Gate | Status |
| --- | --- |
| Target identity | **Partial**。生成器家族（ClavaDDPM, RelDiff）、数据集和种子已固定，但未提供已训练的 checkpoint 身份。改用预生成的合成表格。 |
| Split contract | **Pass**。公开的 `split/mem` 和 `split/non_mem` 关系型 CSV。 |
| Score coverage | **Pass**。18 个官方 JSONL score/指标包，每个含 2000 个 score。 |
| Metric contract | **Pass**。官方包中包含 AUC 和 fixed-FPR TPR 值。 |
| Provenance | **Pass**（score 包公开、可哈希）。Checkpoint 溯源缺失。 |
| Surface delta | **Pass**。关系表格扩散是不同的模态。 |

**判定**：强于 MIDST 和 FERMI，也强于大多数 watch 项。18 个 score 包是公开的、
可哈希的，且同时包含 score 和指标。阻断因素是跨模态范围边界：当前
Platform/Runtime 仅准入图像/潜空间扩散证据。生成器使用预计算的合成表格而非
冻结 checkpoint。一旦对关系表格做出消费边界决策，这是跨模态第二资产扩展的
最强候选。

### 4.6 DurMI（TTS/音频）

| Gate | Status |
| --- | --- |
| Target identity | **Partial**。OpenReview 补充材料有攻击代码；Zenodo 有 checkpoint 元数据但无现成 score 数组。 |
| Split contract | **Partial**。GradTTS LJSpeech 划分（5977/5977）有文档但未作为固定清单文件发布。 |
| Score coverage | **Fail**。无 duration-loss score 数组、ROC 数组或指标 JSON。 |
| Metric contract | **Fail**。无已发布指标。 |
| Provenance | **Fail**。无现成 verifier 输出。 |
| Surface delta | **Pass**。TTS/音频是不同的模态。 |

**判定**：Watch-plus。需要现成的 score 数组和 TTS 消费边界决策。不是最易达的路径。

## 5. 建议

### 当前不释放的路径：ReDiffuse DDPM on CIFAR-100

ReDiffuse OpenReview 补充材料仍提供 CIFAR-100 `25000 / 25000` 精确划分清单、
DDPM 攻击/训练代码和有文档记录的训练配方。因此它保留为同家族不同数据集的
潜在第二面，但不是当前默认 GPU 任务。

阻断点不是 split，而是缺少公开第三方 checkpoint / score packet。2026-05-25
STL-10 bounded scout 已证明同一路径可以执行并产出 `256 / 256` score packet，
但 `300` step tiny target 的固定 timestep denoising-loss 和 denoiser-output
score-norm 都是随机级。因此在没有新 observable 或明确长训预算之前，继续转向
CIFAR-100 从头训练更像换数据集重复同一不确定路线，而不是高信息增益实验。

只有满足以下条件之一时，才重新评估 CIFAR-100：

- 出现公开第三方 CIFAR-100 checkpoint、score packet、ROC/metric artifact 或可哈希 verifier。
- 提出真正不同于 STL-10 denoising-loss / score-norm 的成员 observable，并先有有界预检。
- 明确批准长训预算，同时提前定义 checkpoint SHA-256、score 数组、四项头条指标和发布合约。

在这些条件出现前，不下载 Tiny-ImageNet，不跑 CIFAR-100 / STL-10 step、seed、
timestep、EMA、scheduler、batch-size 或 fusion 矩阵，也不把"可训练"写成第二资产闭合。

### 最强跨模态路径：MT-MIA 关系表格

MT-MIA 仓库提供 18 个现成 score 包，带有精确划分。这是唯一已拥有公开 score
产物的路径。阻断因素纯粹是消费边界范围决策：关系表格成员关系目前不在
Platform/Runtime 已准入范围内。

做出准入关系表格证据的消费边界决策，将以零额外 GPU 工作解锁此路径。

### 不值得重新开启的路径

| 候选 | 原因 |
| --- | --- |
| MIDM FFHQ | Checkpoint 不可访问（Google Drive 401）；无 score 包 |
| CopyMark LAION-mi | 行绑定缺口；公开面无法将 score 重新绑定到 members |
| MIDST TabDDPM | 迁移信号弱；三个 scout 均确认 |
| FMIA CIFAR-100/STL-10 | 与 ReDiffuse 相同缺口（无 checkpoint），但 ReDiffuse 的 workspace 兼容性更好 |
| LSA-Probe | Mock demo 数据；无真实 score 产物 |
| GGDM | Zenodo 仅代码归档；无 checkpoint/split/score |
| FERMI | 纯论文；无代码或产物 |
| Noise Aggregation | 纯论文；无代码或产物 |
| TMIA-DM | 纯论文；无代码或产物 |

## 6. 使用本合约

当新候选出现时（来自论文检索、OpenReview 补充材料、GitHub 发布或合作者移交），
按顺序对照六关进行评估。通过 1-5 关但未通过第 6 关的候选是"同面扩展"（不是
第二资产）。通过 1-3 关但未通过第 4 或第 5 关的候选是"score 不完整 watch"
（供将来参考但尚未就绪）。

只有通过全部六关的候选才能被提议为真正的第二资产，用于科学可移植性主张。

## 7. 修订历史

| 日期 | 变更 |
| --- | --- |
| 2026-05-25 | 将 CIFAR-100 从"最可达路径"收紧为当前不释放路径：等待公开 checkpoint/score、新 observable，或明确长训发布合约。 |
| 2026-05-25 | 记录 ReDiffuse STL-10 bounded scout 已完成且 denoising-loss 指标随机级；关闭默认 GPU 扩参。 |
| 2026-05-25 | 更新 ReDiffuse STL-10 路径：记录 split/statistics/resource preflight 已通过，但 checkpoint/score/metric 仍缺失，只允许 bounded scout。 |
| 2026-05-23 | 初始合约定义。记录最低六关标准并评估当前路径。 |
