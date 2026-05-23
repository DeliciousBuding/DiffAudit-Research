# 灰盒工作台

## 当前状态

- 方向：部分观测成员推断（PIA、SecMI、TMIA-DM）及防御评估。
- 主要方法：`PIA` 是已准入的最强本地 DDPM/CIFAR10 灰盒审计线路。
- 支撑参考：`SecMI` 经全划分审查后达到证据就绪状态，但仍在 Platform/Runtime 准入证据之外。其准入合约现已固化为仅 Research 支撑证据。
- 防御参考：随机 dropout 是临时防御比较器，并非已验证的隐私保护。
- 活跃候选：灰盒 CDI/TMIA-DM/PIA 三评分真实性加固是 CPU 优先且仅内部。ReDiffuse 750k 精确重放因 AUC 一般且严格尾部证据较弱而为仅候选；800k 仍被阻止。已归档的论文候选（SIMA、Noise-as-Probe、MoFit、Structural Memorization）已审查重新入场并保持在暂缓状态。
- Fashion-MNIST DDPM 状态：score-norm 和 score-Jacobian 敏感度侦察均较弱（`AUC = 0.515137` 和 `0.511719`，零低 FPR 恢复）；不要扩展时间步、`p`-范数、扰动尺度、种子、调度器、范数或包大小变体。
- 官方 SimA 状态：代码公开观察加。上游发布定义了一个基于去噪器输出评分范数的独特攻击，但公开的划分清单、检查点、评分数组、ROC/度量工件和就绪验证器缺失；无 GPU 作业发布。
- TMIA-DM 公共表层复查：仅 CRAD 论文/PDF。2026-05-15 关卡未发现官方代码、目标检查点、不可变划分清单、逐样本评分、ROC 数组、度量 JSON 或验证器输出；不要重新打开内部 TMIA-DM/三评分工作或从头实现时间噪声轨迹。
- MoFit 状态：机制相关的无标题灰盒路径，但公开代码说明仍为 `TBW` 且目标/划分工件缺失。不要从头实现替代/嵌入优化或发布 GPU。
- DSiRe / LoRA-WiSE 状态：未来有前景的仅权重隐私审计线路候选，但其声明是聚合 LoRA 微调数据集大小恢复，而非逐样本成员推断。除非打开独立的仅权重消费方合约，否则不要下载 LoRA-WiSE 或运行 `dsire.py`。
- DEB 医疗扩散状态：仅论文源的灰盒机制观察。离散码书扰动加中间轨迹聚合是一个独特可观测项，但没有公开代码、目标/划分清单、中间状态包、评分行、ROC/度量工件或验证器发布。不要从论文实现 DEB 或下载 MedMNIST/CIFAR/TinyImageNet/Stable Diffusion 资产。
- GPU：无发布。

## 文件

| 文件 | 用途 |
| --- | --- |
| [plan.md](plan.md) | 当前状态及后续步骤。 |

当前三评分整合：
[../../docs/evidence/gray-box-triscore-consolidation-review.md](../../docs/evidence/gray-box-triscore-consolidation-review.md)。

当前 SecMI 准入边界：
[../../docs/evidence/secmi-admission-contract-hardening-20260511.md](../../docs/evidence/secmi-admission-contract-hardening-20260511.md)。

当前已归档论文候选重新入场审查：
[../../docs/evidence/gray-box-paper-candidate-reentry-review-20260512.md](../../docs/evidence/gray-box-paper-candidate-reentry-review-20260512.md)。

当前官方 SimA 工件关卡：
[../../docs/evidence/sima-scorebased-artifact-gate-20260515.md](../../docs/evidence/sima-scorebased-artifact-gate-20260515.md)。

当前 TMIA-DM 公共表层复查：
[../../docs/evidence/tmia-dm-temporal-artifact-gate-20260515.md](../../docs/evidence/tmia-dm-temporal-artifact-gate-20260515.md)。

当前 MoFit 工件裁决：
[../../docs/evidence/mofit-artifact-verdict-20260513.md](../../docs/evidence/mofit-artifact-verdict-20260513.md)。

当前 DSiRe / LoRA-WiSE 边界关卡：
[../../docs/evidence/dsire-lora-wise-dataset-size-boundary-20260515.md](../../docs/evidence/dsire-lora-wise-dataset-size-boundary-20260515.md)。

当前 DEB 医疗扩散工件关卡：
[../../docs/evidence/deb-medical-diffusion-artifact-gate-20260515.md](../../docs/evidence/deb-medical-diffusion-artifact-gate-20260515.md)。

当前 Fashion-MNIST SimA score-norm 闭合：
[../../docs/evidence/fashion-mnist-ddpm-sima-score-norm-20260514.md](../../docs/evidence/fashion-mnist-ddpm-sima-score-norm-20260514.md)。

当前 Fashion-MNIST score-Jacobian 敏感度闭合：
[../../docs/evidence/fashion-mnist-ddpm-score-jacobian-sensitivity-20260514.md](../../docs/evidence/fashion-mnist-ddpm-score-jacobian-sensitivity-20260514.md)。

## 归档

已关闭的笔记位于
[../../legacy/workspaces/gray-box/2026-04/](../../legacy/workspaces/gray-box/2026-04/)。
