# DiffAudit Research Roadmap

> Last updated: 2026-05-24 | [Historical log](docs/internal/roadmap-history-20260524.md)

## 当前状态（2026-05-24）

### Admitted Evidence（Platform/Runtime 可用）

| # | Track | Attack | Defense | AUC | ASR | TPR@1% | Evidence |
|---|---|---|---|---|---|---|---|
| 1 | Black-box | recon DDIM public-100 step30 | none | 0.837 | 0.74 | 0.22 | `docs/evidence/recon-product-validation-result.md` |
| 2 | Gray-box | PIA GPU512 baseline | none | 0.841 | 0.786 | 0.059 | `workspaces/implementation/artifacts/unified-attack-defense-table.json` |
| 3 | Gray-box | PIA GPU512 baseline | stochastic-dropout | 0.828 | 0.768 | 0.053 | `workspaces/implementation/artifacts/unified-attack-defense-table.json` |
| 4 | White-box | GSA 1k-3shadow | none | 0.998 | 0.990 | 0.987 | `workspaces/implementation/artifacts/unified-attack-defense-table.json` |
| 5 | White-box | GSA 1k-3shadow | DPDM strong-v3 | 0.489 | 0.499 | 0.009 | `workspaces/implementation/artifacts/unified-attack-defense-table.json` |
| 6 | Gray-box | Tracing the Roots | none | 0.816 | 0.738 | 0.134 | `docs/product-bridge/tracing-roots-candidate-evidence-card.md` |

### Evidence-Ready（内部验证通过，未收录）

| Line | Best AUC | Best ASR | TPR@5% | Limitation |
|---|---|---|---|---|
| **ReDiffuse PIA** (750k+800k) | 0.885 | 0.815 | 0.000 | 严格低尾为零 |
| **ReDiffuse NNS** (750k+800k) | 0.990 | 0.963 | 0.000 | FPR 死区 0→12%，不可逐样本判定 |
| **ReDiffuse SecMI** (750k+800k) | 0.776 | 0.710 | 0.000 | 始终不如 PIA |
| SecMI stat/NNS | 0.946 | — | 0.114 | structural-support-only |
| H2/simple-distance | 0.877 | 0.84 | — | candidate-only |
| CDI/TMIA-DM/PIA tri-score | — | — | — | internal-only candidate |

### Pipeline & Infrastructure

| 组件 | 文件 | 状态 |
|---|---|---|
| DDPM 训练 (AMP, EMA) | `scripts/train_{stl10,cifar10}_pt.py`, `train_cifar10_100k.py` | 可用 |
| PIA scoring | `scripts/score_{stl10,cifar10}_pia_v2.py`, `score_800k_pia.py` | 已验证 |
| SecMI scoring | `scripts/score_{cifar10,800k}_secmi.py` | 可用（不如 PIA） |
| NNS scoring | `scripts/score_{800k,750k}_nns.py` | 已验证 |
| 数据准备 | `scripts/prep_cifar10.py` | 可用 |
| 路径约定 | 全部 env-var 驱动 (`DIFFAUDIT_DATA`/`DIFFAUDIT_OUTPUT`) | — |

### 资产库存

| Checkpoint | Steps | 模型 | 兼容性 |
|---|---|---|---|
| 800k PIA DDPM | 800,000 | UNet (ch=128) | PIA/SecMI/NNS 全通过 |
| 750k DDIM | 750,000 | UNet (ch=128) | PIA/NNS 交叉验证 |
| 自训练 CIFAR-10 | 100,000 | UNet (ch=128) | AUC≈0.5（无效） |
| 自训练 STL-10 | 10,000 | UNet (ch=128) | AUC≈0.5（无效） |
| ~~OpenAI 500k~~ | 500,000 | OpenAI UNet | 架构不兼容 |
| ~~HF DDPM~~ | — | Diffusers UNet | 架构不兼容 |

## 核心发现与决策

1. **PIA/NNS 方法论已通过交叉验证**（2 checkpoints, AUC 0.88/0.99）
2. **低 FPR 逐样本 MIA 不可行**（FPR 死区 0→12%，PIA/NNS 家族的根局限性）
3. **Consumer GPU 从零训练不通**（≤100k 步全随机，800k 需 3 天 RTX 4070）
4. **公开第二资产不存在**（CIFAR-100/STL-10/Tiny-IN 均无公开 checkpoint）
5. **现有 3 个可用 checkpoint 已完整评估**，不需要继续在此线路上追加实验

## 6 个月远景（2026-05 → 2026-11）

```
Phase A: 巩固当前证据面 ✅ 完成
├── ✅ PIA/NNS cross-validation (AUC=0.990)
├── ✅ FPR dead-zone characterized
├── ✅ Self-training ruled out (10k/100k→AUC≈0.5)
├── ✅ Asset search completed (no public non-CIFAR-10 DDPM)
├── ✅ Tracing the Roots admitted (evidence bundle row 6)
└── ✅ ReDiffuse → evidence-ready

Phase B: 整理与发布（5月-6月）
├── 对外可读的 evidence bundle 文档完善
├── admitted-results-summary.md 更新 (Tracing the Roots)
├── Platform/Runtime 展示面准备（4C 省赛答辩）
└── 论文 outline（若决定投稿）

Phase C: 新资产监控（持续）
├── 等待新论文发布 public checkpoint (CIFAR-100/STL-10/Tiny-IN)
├── SecMI/PIA 作者 SharePoint/OneDrive 定期重试
├── 防御侧 artifact gate 监控（CPSample, DualMD）
└── 黑盒第二资产搜索（6 个月窗口）

Phase D: 方法论扩展（条件触发）
├── 若新 checkpoint 出现 → 立即 PIA+NNS scoring
├── 若新 MIA 论文有 code+checkpoint → 复现评估
└── 若论文投稿决定 → 补充 benchmark 级实验
```

### 当前约束

- **GPU**: RTX 4070 Laptop 8GB, CUDA ready, 插电使用
- **active_gpu_question**: none（PIA+NNS 已完成，无新 GPU 任务）
- **不启动**: 自训练 DDPM >100k 步、新 architecture 适配（HF/OpenAI）、CLiD/CopyMark 扩展
- **历史详细记录**: [docs/internal/roadmap-history-20260524.md](docs/internal/roadmap-history-20260524.md)
