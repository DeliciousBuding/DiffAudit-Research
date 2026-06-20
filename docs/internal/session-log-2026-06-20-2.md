# DiffAudit Paper 1 — 2026-06-20 会话进展总结

## 实验完成（5 项 GPU 实验）

1. **精细时间网格 DDPM 8步** — 信号分布式，max Δ=+0.029（16格点中0个超过0.05）
2. **精细时间网格 DDIM 8步** — 信号集中式，max Δ=+0.221（7.6× 差异）
3. **DDIM N=64 机制分析** — 通道级 DAAB 普适：mu/var 极端冗余（各≈99.8%合并）
4. **DDIM 30-seed 匹配通道 knockout** — d=0.10, p=0.60，通道非局部化确认
5. **DDIM N=128 scout** — AUC=0.869, TPR@1%=0.273（DDPM的5×）

## 关键科学发现

- **时间分布是训练依赖的**：DDPM 分布式 vs DDIM 集中式（7.6× 差异）
- **法医脆弱性部分训练依赖**：DDPM TPR@1%=0.055，DDIM TPR@1%=0.273
- **通道级 DAAB 完全普适**：mu/var冗余、相关-因果分离、通道非局部化、站点因果梯度——全部跨checkpoint确认
- **DAAB属性矩阵**：8项属性中6项跨checkpoint一致，2项训练依赖

## 论文修订

- ✅ Abstract 重写（科学先行，含DDIM发现）
- ✅ Conclusion 重写（证据状态收束）
- ✅ Fine Temporal Grid 新章节 + 表格
- ✅ Admission Map → Figure 1
- ✅ C14 降级至1段
- ✅ 修复 same-team labels、Table ??、2.8-sigma 语言
- ✅ PDF 编译（14页）

## 外部审查

- **ChatGPT**：7项必须修改（摘要重写、H1前置、Admission Map、C14降级、修blocker、语言收紧、结论重写）
- **Workflow 7-agent**：12项过度声明风险、叙事建议、实验缺口

## 待办

- [ ] H1/H2 章节重排（Workflow 规划中）
- [ ] CIFAR-100 跨数据集验证（网络阻断，需手动下载）
- [ ] 训练预算消融（无兼容中间checkpoint）
- [ ] DDIM 低步数鲁棒性
- [ ] 最终 PDF 上传 ChatGPT 审核

## Git 状态

Branch: `paper/evidence-contracted-workspace`
今日 commits: 8+ 次，全部已推送

## 关键文件

- 论文 LaTeX: `papers/diffaudit-evidence-paper/main.tex`
- 论文 PDF: `papers/diffaudit-evidence-paper/paper.pdf`（14页）
- Claim matrix: `docs/paper1/frozen_claim_matrix.md`
- 证据文档: `docs/evidence/h1-fine-temporal-grid-2026-06-20.md`, `h1-mechanistic-ddim-2026-06-20.md`
- Workflow 审查: `docs/paper1/workflow-review-2026-06-20.md`
- DDIM N=128 结果: `outputs/h1_scout/h1_ddim_n128_results.json`
- DDIM knockout 结果: `outputs/h1_scout/h1_channel_knockout_ddim.json`
