# 防御工作台

## 当前状态

本工作台用于当前防御专项摘要。历史防御笔记应保持归档，除非活跃工作需要。

防御结果在晋升为公开证据之前必须报告低 FPR 行为和自适应攻击者局限性。

CPSample 仅为防御观察加。OpenReview ICLR 2025 补充材料提供了扩散/分类器代码和小型 `inference_attacks/*.txt` 损失片段，但没有不可变的去噪器/分类器检查点哈希、精确的子集索引清单、逐行绑定的受保护/未受保护评分包、ROC 数组、度量 JSON、保留效用度量或就绪验证器。不要下载 CIFAR-10、CelebA、LSUN、Stable Diffusion 权重、模型检查点、生成图像或缺失的 Google Drive 占位符；不要运行 `python main.py`、训练分类器、微调去噪器、运行 `--inference_attack`、启动 GPU 工作或在检查点绑定的评分工件和自适应防御消费方合约存在之前晋升防御行。参见
[../../docs/evidence/cpsample-defense-artifact-gate-2026-05-15.md](../../docs/evidence/cpsample-defense-artifact-gate-2026-05-15.md)。

DualMD / DistillMD 仅为防御观察加。OpenReview DDMD 补充材料暴露了 DDPM/LDM 训练、分离教师、蒸馏、PIA/SecMIA、黑盒攻击、DDPM 划分索引文件和 FID 统计，但不提供冻结检查点、防御/非防御评分行、ROC 数组、度量 JSON、生成响应或就绪验证器输出。其嵌入的 GitHub 源 `btr13010/DDMD` 不公开。不要下载 SharePoint Pokemon 载荷、Stable Diffusion 权重、CIFAR/STL/Tiny-ImageNet 数据集、运行训练或攻击脚本、启动 GPU 工作，或在检查点绑定的评分工件和消费方边界决策存在之前晋升分离划分防御行。参见
[../../docs/evidence/dualmd-distillmd-defense-artifact-gate-2026-05-15.md](../../docs/evidence/dualmd-distillmd-defense-artifact-gate-2026-05-15.md)。

DIFFENCE 仅为分类器防御观察加。官方仓库提供代码、配置和划分索引文件，但受保护目标是图像分类器，扩散仅为推理前防御组件。它需要 Google Drive 中的分类器/扩散检查点且需本地生成结果，并且未提交防御/非防御 logits、评分行、ROC 数组、度量 JSON 或就绪验证器输出。不要下载 DIFFENCE 模型文件夹或 CIFAR/SVHN 载荷、训练分类器或扩散模型、运行 MIA 脚本，或在检查点绑定的评分工件和明确的消费方边界决策存在之前晋升分类器防御行。参见
[../../docs/evidence/diffence-classifier-defense-artifact-gate-2026-05-15.md](../../docs/evidence/diffence-classifier-defense-artifact-gate-2026-05-15.md)。

MIAHOLD / HOLD++ 高阶 Langevin 仅为防御观察加。公开仓库提供高阶 Langevin 防御代码、音频划分文件列表、CIFAR HOLD 配置和 PIA 式攻击代码，但没有检查点绑定的目标工件、可复用的成员/非成员评分、ROC 数组、度量 JSON、生成响应或就绪验证器输出。不要下载 Grad-TTS/HiFi-GAN/CLD-SGM 检查点、CIFAR/CelebA/音频数据集、抓取 W&B 工件、训练 HOLD++ 模型，或在检查点绑定的评分工件存在之前晋升防御行。参见
[../../docs/evidence/miahold-higher-order-langevin-artifact-gate-2026-05-15.md](../../docs/evidence/miahold-higher-order-langevin-artifact-gate-2026-05-15.md)。

StablePrivateLoRA 仅为防御观察加。其公开仓库提供 MP-LoRA/SMP-LoRA 代码和数据集划分载荷，但没有发布的 LoRA/检查点哈希、原始攻击评分、ROC/度量工件、生成响应或就绪验证器命令。不要克隆/下载大型数据集载荷、SD-v1.5、LoRA 检查点、生成图像或日志；不要训练 MP-LoRA/SMP-LoRA 或在检查点绑定的评分工件存在之前晋升防御行。参见
[../../docs/evidence/stableprivatelora-defense-artifact-gate-2026-05-15.md](../../docs/evidence/stableprivatelora-defense-artifact-gate-2026-05-15.md)。

当前 I-B 风险定向遗忘继承范围处于暂缓状态。现有全划分攻击侧审查显示了小幅度量降低，但由于未重训练防御影子，这些审查并不具备防御感知。参见
[../../docs/evidence/ib-risk-targeted-unlearning-successor-scope.md](../../docs/evidence/ib-risk-targeted-unlearning-successor-scope.md)
和
[../../docs/evidence/ib-adaptive-defense-contract-2026-05-11.md](../../docs/evidence/ib-adaptive-defense-contract-2026-05-11.md)。
最新的防御感知重新打开侦察保持 I-B 暂缓，因为当前最佳 k32 全划分锚点仍仅为攻击侧阈值迁移：
[../../docs/evidence/ib-defense-aware-reopen-scout-2026-05-12.md](../../docs/evidence/ib-defense-aware-reopen-scout-2026-05-12.md)。
后续协议审计检查了活跃 CLI/代码路径并确认 `review-risk-targeted-unlearning-pilot` 仍借用未防御的影子参考：
[../../docs/evidence/ib-defense-reopen-protocol-audit-2026-05-12.md](../../docs/evidence/ib-defense-reopen-protocol-audit-2026-05-12.md)。
当前重新打开协议现已冻结为机器可检查的 CPU 合约，但仍不发布 GPU 且不训练防御影子：
[../../docs/evidence/ib-defended-shadow-reopen-protocol-2026-05-12.md](../../docs/evidence/ib-defended-shadow-reopen-protocol-2026-05-12.md)。
活跃审查入口点现在有 CPU 守卫：显式 `defended-shadow-reopen` 模式拒绝旧的未防御影子阈值参考，而遗留诊断模式保持可复现：
[../../docs/evidence/ib-reopen-shadow-reference-guard-2026-05-12.md](../../docs/evidence/ib-reopen-shadow-reference-guard-2026-05-12.md)。
未来的防御影子训练集现已有一个覆盖感知的仅 CPU 清单，但当前目标 k32 身份合约被阻止，因为三个影子成员数据集分别仅覆盖 `2/32`、`2/32` 和 `1/32` 的遗忘 ID：
[../../docs/evidence/ib-defended-shadow-training-manifest-2026-05-12.md](../../docs/evidence/ib-defended-shadow-training-manifest-2026-05-12.md)。
随后一次 CPU 影子本地身份侦察检查了目标级别风险记录是否可以被过滤到影子划分中。`shadow-01` 和 `shadow-02` 可以机械地形成 k32/k32 重映射，但这仍被阻止为真正的影子本地评分，因为风险记录是目标级别的 PIA/GSA 全重叠记录：
[../../docs/evidence/ib-shadow-local-identity-scout-2026-05-12.md](../../docs/evidence/ib-shadow-local-identity-scout-2026-05-12.md)。
一次 CPU 纯 GSA 预检现使用现有的逐影子 GSA 损失评分导出为 `shadow-01`、`shadow-02` 和 `shadow-03` 生成真正的影子本地风险记录。它在写入 k32 身份文件之前对重复后缀 ID 进行去重，但仍将 I-B 保持阻止状态，因为影子本地 PIA 风险记录在冻结的 PIA+GSA 合约中仍然缺失：
[../../docs/evidence/ib-shadow-local-gsa-risk-preflight-2026-05-15.md](../../docs/evidence/ib-shadow-local-gsa-risk-preflight-2026-05-15.md)。

## 后续步骤

下一个有效的 I-B 实现步骤不是另一次阈值迁移审查或另一次目标风险重映射。它要么是针对同一身份合约生成影子本地 PIA 记录，要么是显式批准较弱的纯 GSA 语义，然后在冻结协议下执行一个微型防御影子训练工件并生成防御影子阈值参考以及自适应攻击者和保留效用度量。
已验证的防御声明在审查后归属 [../../docs/evidence/](../../docs/evidence/)。
