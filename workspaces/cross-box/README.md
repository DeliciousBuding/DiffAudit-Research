# 跨审计线路工作台

## 当前状态

本工作台用于跨审计线路比较工作。当前裁决是跨审计线路评分的共享对内部比较有用，但仍仅为候选。

当前集成边界文档位于
[../../docs/product-bridge/README.md](../../docs/product-bridge/README.md)、
[../../docs/evidence/cross-box-boundary-status.md](../../docs/evidence/cross-box-boundary-status.md)、
[../../docs/evidence/cross-box-successor-scope-20260512.md](../../docs/evidence/cross-box-successor-scope-20260512.md) 和
[../../docs/evidence/research-boundary-card.md](../../docs/evidence/research-boundary-card.md)。
后 I-B 重新选择选择了 I-C 同规格评估器可行性侦察，该侦察将 I-C 保持在暂缓状态，因为当前 PIA 桥接表面仍是翻译别名金丝雀而非同规格复用：
[../../docs/evidence/post-ib-next-lane-reselection-20260512.md](../../docs/evidence/post-ib-next-lane-reselection-20260512.md) 和
[../../docs/evidence/ic-same-spec-evaluator-feasibility-scout-20260512.md](../../docs/evidence/ic-same-spec-evaluator-feasibility-scout-20260512.md)。

## 后续步骤

没有活跃的跨审计线路 CPU 或 GPU 任务。除非有新的低 FPR 假设和独特的可观测项或迁移合约，否则不要安排另一次跨审计线路融合运行。仅在
[../../docs/evidence/cross-box-successor-scope-20260512.md](../../docs/evidence/cross-box-successor-scope-20260512.md)
中规定的条件下重新打开。
对于 I-C 具体而言，仅在同规格评估器能够在超过单个
`965 / 1278` 对并在匹配随机比较器下产出 `AUC`、`ASR`、`TPR@1%FPR` 和 `TPR@0.1%FPR` 之后再重新打开。
