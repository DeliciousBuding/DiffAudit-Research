# DiffAudit Paper 1 — 完整审查包（2026-06-20）

> 发送给 ChatGPT（DiffAudit 项目线程）进行综合审查。请上传 PDF + 粘贴以下 prompt。

---

## Prompt（直接粘贴）

```
以下是 DiffAudit Paper 1 的最新完整版本（PDF 附上）。请进行 TMLR 级别的综合审查。

## 今日新增实验（上次审查后完成）

### 三向精细时间网格对比（8步，全站点 knockout）

| 配置 | late_down max|Δ| | mid_0 max|Δ| | 模式 |
|------|:---:|:---:|------|
| CIFAR-10 DDPM 800k | 0.029 | 0.024 | 分布式 |
| CIFAR-10 DDIM 750k | 0.221 | 0.194 | 集中式 |
| CIFAR-100 DDPM | 0.167 | 0.157 | 集中式 |

发现：时间分布同时依赖训练方式（DDPM vs DDIM）和数据集（CIFAR-10 vs CIFAR-100）。CIFAR-100 DDPM 效应是 CIFAR-10 DDPM 的 5.7×。已软化措辞——用"dataset-dependent"替代"dataset complexity controls"，注明 N=2 不足以建立因果归因。

### CIFAR-100 跨数据集完整结果

**3步时空网格（4站点×3步数）：**
- Baseline AUC=0.835，信号跨数据集存在
- 站点梯度平缓化（所有站点重要，vs CIFAR-10 尖锐 late_down 主导）
- 时间分布拓宽（t=400 峰值，非 t=100）
- 所有站点×步数格点均显示实质 knockout 效应

**8步精细时间网格：**
- Baseline AUC=0.811
- late_down max|Δ|=0.167，mid_0 max|Δ|=0.157
- CIFAR-100 DDPM 天然产生集中式信号（与 DDIM 可比）

**机制分析（N=64）：**
- mu_only=0.844, var_only=0.835, sparsity=0.808
- early_up@t100: 6.6% 显著通道（CIFAR-10 DDPM=4.7%, DDIM=14.1%）
- late_down/mid_0: ~0% 显著通道——几乎无个体显著通道
- 悖论：更少显著通道但更强因果集中。强化 DAAB 核心论：相关≠因果。

**通道 knockout（匹配4%，30 seeds）：**
- Targeted μ=0.659, Random μ=0.657, Diff μ=+0.0018
- d=0.04, p=0.822, 95% CI [-0.0135, +0.0171]
- 效应比 CIFAR-10 DDPM (d=0.21) 更小——通道非局部化跨三配置普适确认

## DAAB 完整属性矩阵（8属性 × 3配置）

| 属性 | CIFAR-10 DDPM | CIFAR-10 DDIM | CIFAR-100 DDPM | 普适？ |
|------|:---:|:---:|:---:|:---:|
| AUC>0.8 | 0.873 | 0.869 | 0.835 | ✅ |
| mu/var 冗余 | ✅ | ✅ 99.8% | ✅ | ✅ |
| 相关-因果分离 | 4.7%→least causal | 14.1%→least causal | 6.6%→least causal | ✅ |
| 通道非局部化 | d=0.21 p=0.26 | d=0.10 p=0.60 | d=0.04 p=0.822 | ✅ |
| 全站点因果梯度 | 尖锐 late_down>> | 尖锐 | **平缓** | ⚠️ 数据集依赖 |
| 时空定位 | t=100 峰值 | t=100 峰值 | **t=400 峰值** | ⚠️ 数据集依赖 |
| 时间分布 | 分布式 | 集中式 | **集中式** | ❌ 训练+数据依赖 |
| 法医脆弱性 | TPR@1%=0.055 | TPR@1%=0.273 | — | ⚠️ 部分训练依赖 |

**结论：** 5/8 属性普适（通道级 DAAB），3/8 属性由训练方式+数据集共同决定（时空几何），1/8 属性部分训练依赖（法医脆弱性）。"Distributed"在通道层面成立且普适，在时间层面为 DDPM 特有。

## 资源发现结果

Workflow 扫描了 127GB / 20,855 文件。兼容 checkpoint 仅 3 个（CIFAR-10 DDPM 800k、DDIM 750k、CIFAR-100 DDPM）。STL-10 数据+split 齐但 checkpoint 格式不兼容。Google DDPM 格式不兼容。无其他可用资源。

## 论文修订状态（相对于上次审查）

已完成：摘要重写、结论重写、Admission Map→Figure 1、C14 降级至 1 段、三向对比表、跨数据集段落、措辞软化（dataset complexity→dataset-dependent）
待完成：H1/H2 章节重排、补充材料（C14 完整表）、Statistical Methods 小节

## 问题

1. 当前 DAAB 属性矩阵是否足够支撑 TMLR 提交？8 属性 × 3 配置的证据范围是否充分？
2. 三向对比的声明边界——N=2 数据集，"dataset-dependent"措辞是否足够谨慎？是否需要更进一步强调 confound（class count vs samples-per-class vs training duration）？
3. 论文当前最薄弱的环节是什么？是结构（H1/H2 顺序）、方法学（缺少 Statistical Methods 小节）、还是证据范围（仅 2 个数据集）？
4. "Distributed Activation-Amplitude Bias" 命名——考虑到 CIFAR-100 DDPM 的时间集中式信号，是否应该重新考虑命名？还是"Distributed"限定于通道层面即可？
5. 是否需要第四个数据集（如 STL-10，需 checkpoint 转换）来强化声明？还是当前证据已足够？

请给出最终的 TMLR 提交意见（Accept/Minor Revision/Major Revision/Reject）及修订路线图。
```

---

## 文件

- **PDF**: `D:\Code\DiffAudit\Research\papers\paper.pdf`（14 页，435KB）
- **LaTeX 源码**: `D:\Code\DiffAudit\Research\papers\diffaudit-evidence-paper\main.tex`
- **Claim Matrix**: `D:\Code\DiffAudit\Research\docs\paper1\frozen_claim_matrix.md`
- **最新会话日志**: `D:\Code\DiffAudit\Research\docs\internal\session-log-2026-06-20-2.md`

## 实验数据文件

所有实验输出在 `D:\Code\DiffAudit\Research\outputs\h1_scout\`：
- `h1_ddim_n128_results.json` — DDIM N=128 scout
- `h1_channel_knockout_ddim.json` — DDIM 通道 knockout
- `h1_channel_knockout_cifar100.json` — CIFAR-100 通道 knockout
- `h1_cifar100_grid.json` — CIFAR-100 时空网格
- `h1_cifar100_fine_grid.json` — CIFAR-100 精细时间网格
- `h1_mechanistic_cifar100.json` — CIFAR-100 机制分析
- `h1_mechanistic_ddim.json` — DDIM 机制分析
- `h1_fine_grid_ddim.json` — DDIM 精细时间网格

---

## 发送方式

1. 打开 https://chatgpt.com/g/g-p-6a22b0f791cc8191924d4dce50d95350-diffaudit/c/6a32cd9f-d040-83e8-af8a-19f2d10737f4
2. 上传 PDF 文件 `D:\Code\DiffAudit\Research\papers\paper.pdf`
3. 粘贴上面的 Prompt
4. 发送
