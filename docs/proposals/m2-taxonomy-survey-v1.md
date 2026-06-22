# M2 Taxonomy/Survey — 论文提案 v1

日期：2026-06-22
状态：SCOPING（目标 ACM CSUR 或 NeurIPS Position Paper）

## 1. 核心研究问题

**RQ**: DiffAudit 中提出的 5 级证据状态分类（Admitted → Conditionally Admitted → Watch → Excluded → Negative）能否泛化到扩散模型以外的生成式 AI 领域（LLM、GAN、水印），作为跨领域 MIA 声明质量的统一评估框架？

## 2. 贡献矩阵

| # | 贡献 | 类型 | 匹配度 |
|---|------|------|--------|
| C1 | 跨领域 MIA 声明分类法（5 证据状态 × 4 领域） | 系统化框架 | CSUR 核心需求 |
| C2 | LLM 训练数据检测的 evidence gate 案例研究 | 实证迁移 | NeurIPS 偏好 |
| C3 | GAN 成员推断的 replicability audit | 再现性分析 | 两个 venue 均需要 |
| C4 | 水印检测声明的过声称风险评估 | 领域审计 | — |
| C5 | 开放 MIA Claim Register（社区可贡献） | 基础设施 | CSUR 长期价值 |

## 3. 5 证据状态原型（已有）

| 状态 | 定义 | 扩散 MIA 示例 | LLM 示例 | GAN 示例 |
|------|------|-------------|---------|---------|
| **Admitted** | AUC>0.7, 多控制通过, 独立复现 | H1 activation subspace (AUC 0.839) | — | — |
| **Conditionally Admitted** | AUC>0.6, 多数控制通过, 有限样本 | H2 output-cloud (AUC 0.962, N=64 caveat) | — | — |
| **Watch** | 边界 AUC, 控制未完成, 需要更多数据 | DDIM 750k temporal grid | — | — |
| **Excluded** | 控制失败, 混杂变量, 无法排除替代解释 | CLiD prompt-conditioned collapse | — | — |
| **Negative** | AUC≈0.5, 零效果 | scnet capacity null (ΔAUC=0.003) | — | — |

*注：LLM/GAN/水印列需要从文献中填充*

## 4. 论文结构草案

1. **Introduction**: MIA claims are proliferating across generative AI domains, but quality assessment remains ad-hoc. We propose a unified 5-state evidence classification.
2. **Background**: MIA in diffusion, LLM, GAN, watermark settings. Commonalities and differences in threat models.
3. **The 5-State Evidence Taxonomy**: Formal definitions, gate criteria, per-state required evidence
4. **Case Study: Diffusion MIA** (from DiffAudit Paper 1): 15+ claims mapped to 5 states
5. **Case Study: LLM Training Data Detection**: Map existing LLM MIA claims to taxonomy
6. **Case Study: GAN Membership Inference**: Reproduce and classify key GAN MIA results
7. **Case Study: Watermark Detection Claims**: Audit overclaiming in watermark detection literature
8. **Discussion**: Cross-domain patterns, taxonomy limitations, community adoption path
9. **Conclusion**

## 5. 关键优势（vs M1 Defense Transfer）

| 维度 | M1 | M2 |
|------|----|----|
| GPU 需求 | ~100 GPU-h | 0（纯文献 + 分析） |
| 时间 | 8-10 周 | 5-7 周 |
| 竞争 | 中（防御论文较少） | 低（无统一 MIA 质量框架） |
| 风险 | 中（需要实验成功） | 低（文献整理 + 分类） |
| 与 Paper 1 关系 | 防御侧延伸 | 方法论泛化 |

## 6. 时间线

| 周 | 里程碑 | 资源 |
|----|--------|------|
| W1-2 | 系统检索 LLM/GAN/水印 MIA 文献 | CPU-only |
| W3 | 5 状态定义精化 + 跨领域 gate criteria | CPU-only |
| W4 | LLM 案例研究：映射现有声明到分类 | CPU-only |
| W5 | GAN 案例研究 + 水印审计 | CPU-only |
| W6 | 初稿写作 | CPU-only |
| W7 | 修改 + 投稿 | — |

**总计**: 5-7 周，零 GPU

## 7. 与 Paper 1 的关系

- Paper 1 是 M2 的核心案例之一（"Case Study: Diffusion MIA"）
- M2 将 Paper 1 的 evidence gate 方法论提升为跨领域通用框架
- M2 不修改 Paper 1 的结论，而是将其作为 5 状态分类的 exemplar
- 两篇可以同时投稿（不重叠 venue：Paper 1 → TMLR，M2 → CSUR/NeurIPS）

## 8. 下一步

- [ ] 检索 LLM MIA 系统综述（作为基线文献）
- [ ] 收集 5 个已有 exemplar 的详细状态映射
- [ ] 联系合作者确认跨领域范围

---

*本文档是 M2 的 living proposal。*
