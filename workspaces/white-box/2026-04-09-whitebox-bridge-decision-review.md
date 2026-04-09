# 2026-04-09 White-Box Bridge Decision Review

## 目的

这份文档用于把当前 `white-box same-protocol bridge` 收口成一次正式决策，而不是继续停留在“已经有一份 batch32 诊断结果”的中间态。

当前唯一允许的输出不是新增口头判断，而是三选一：

1. `继续扩大`
2. `保持冻结`
3. `失败收口`

在这份文档完成之前：

- `batch32 diagnostic comparator` 只能写成 `runtime-smoke / diagnostic`
- 不得写成 admitted benchmark
- `Phase E` 不正式打开

## 当前固定前提

- 当前唯一 active GPU 问题仍然是 `white-box same-protocol bridge`
- admitted attack baseline 仍是：
  - `workspaces/white-box/runs/gsa-runtime-mainline-20260409-cifar10-1k-3shadow-epoch300-rerun1/summary.json`
- defended main rung 仍是：
  - `workspaces/white-box/runs/dpdm-w1-multi-shadow-comparator-targetmember-strongv3-3shadow-full-rerun8-20260408/summary.json`
- 当前 batch32 诊断结果是：
  - `workspaces/white-box/runs/dpdm-w1-multi-shadow-comparator-targetmember-sameproto3shadow-batch32-diagnostic-20260409/summary.json`
- 当前诊断指标为：
  - `auc = 0.541199`
  - `asr = 0.515625`
  - `tpr@1%fpr = 0.0`
  - `tpr@0.1%fpr = 0.0`
  - `shadow_train_size = 768`
  - `target_eval_size = 256`

## 当前问题

当前已经确认的事实不是“bridge 快做完了”，而是下面这三点：

1. `batch_size = 32` 已经足以恢复 `shadow-02 / shadow-03` 训练链
2. 当前 bridge 至少已经有一份可复述的 diagnostic artifact
3. 这份 artifact 仍然不是与 admitted `GSA rerun1 / W-1 strong-v3 full-scale` 同协议的 benchmark 结果

因此，这份 decision review 的核心问题只有一个：

`batch32 diagnostic comparator` 是否足以支持下一步 same-protocol 放大，还是应保持冻结，或直接以失败模式收口？

## 决策选项

### 选项 A：继续扩大

选择条件：

- 能明确说明当前 batch32 结果虽然仍是 diagnostic，但已经足以指向一个具体的放大方向
- 放大后的目标协议、训练规模、预算上限、退出条件已经固定
- 放大不会引入第二条白盒长任务，也不会重新定义 bridge 问题

必须同时满足的附加条件：

- 启动入口已经 portable
- 不依赖 `LocalOps/paper-resource-scheduler`
- 放大后的成功/失败口径已提前写清

允许写出的结论：

- `bridge 继续扩大`
- `当前 diagnostic 已足以支持下一步 same-protocol benchmark-closure`

不允许写出的结论：

- `benchmark 已完成`
- `defended benchmark 已成立`

### 选项 B：保持冻结

选择条件：

- 当前 batch32 结果足以证明训练链已被修正
- 但不足以支持进一步升级到 admitted 或更强 benchmark 面
- 继续扩大当前只会消耗 GPU，而不会显著提高 scientific clarity

允许写出的结论：

- `batch32 result retained as diagnostic evidence`
- `bridge currently frozen without admitted change`

这是当前默认推荐分支。

原因：

- 当前 artifact 仍停留在 `runtime-smoke`
- 当前协议规模与 admitted 面差距仍然明显
- 当前更高优先级的非 GPU 工作仍包括 `PIA provenance dossier`

### 选项 C：失败收口

选择条件：

- 已能稳定复述为什么当前 `DPDM / W-1` 无法进入与 `GSA rerun1` 同协议的 benchmark 面
- 根因已经从偶发异常收敛为结构性 blocker
- 继续投入主 GPU 资源的收益低于转向下一问题

允许写出的结论：

- `same-protocol bridge cannot currently reach benchmark-closure`
- `current route closed as a reproducible failure mode`

允许接受的失败类型：

- 架构不兼容
- 数据切分或训练目标不兼容
- 评估规模无法在当前 defended route 下收敛到可比协议
- 当前 portable 入口仍无法稳定支撑对外部协作者复现

## 推荐默认分支

当前默认建议为：`保持冻结`

理由如下：

1. 当前 batch32 结果已经证明了训练链修正有效，但还不足以把 bridge 升级成 admitted comparator
2. 现阶段最重要的价值是把 `diagnostic` 和 `benchmark` 的边界钉死，而不是继续在口径未固定时放大
3. `PIA provenance` 仍是当前主讲线最硬的非 GPU blocker；如果继续扩大 bridge，很容易把注意力从主讲线硬门槛上挪走

只有在 `2026-04-23` 前出现新的明确证据，证明 bridge 放大具有高确定性收益，才允许从默认分支切到 `继续扩大`。

## 时间节点

### `2026-04-23` 前

必须完成：

- 一次 bridge decision review
- 三选一中的明确推荐分支
- 对当前 batch32 artifact 的固定定位

### `2026-04-30` 前

必须完成：

- 三选一决策写回：
  - `workspaces/white-box/2026-04-09-whitebox-same-protocol-bridge.md`
  - `docs/comprehensive-progress.md`
  - `docs/reproduction-status.md`
  - 需要时同步根层 `ROADMAP.md` 与 `GLOBAL_TASK_BOARD.md`
- 明确 `Phase E` 是否允许打开

## 验收标准

到 `2026-04-30` 前，这份 decision review 只有在同时满足下面 4 条时才算完成：

1. `batch32 diagnostic comparator` 仍未被错误升级成 admitted benchmark
2. 三选一决策已经明确写下，而不是继续停留在观察态
3. 当前 bridge 的成功/失败边界已可复述
4. 对后续 GPU 队列的影响已经写清

## 对后续 GPU 排队的影响

- 只有当 bridge 完成正式三选一收口后，下一条 GPU 问题才允许进入准入验证
- bridge 若保持冻结或失败收口，并不等于白盒线失败；它只说明当前 same-protocol route 到达了阶段边界
- 下一条 GPU 候选默认顺序仍是：
  1. `PIA paper-aligned confirmation`
  2. `Finding NeMo / local memorization` intake 升级
  3. `DP-LoRA`
