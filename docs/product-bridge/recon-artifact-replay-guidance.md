# Recon Artifact Replay Clarification

## 这些 replay artifacts 是什么
- 路径 `Research/experiments/recon-artifact-mainline-YYYYMMDD-HHMMSS/` 对应近期从 Runtime `recon_artifact_mainline` job 触发的 replay 资产。每个目录仅包含 `summary.json`，记录 contract `black-box/recon/sd15-ddim`、method（当前为 `threshold`）以及 `artifact_dir` 的本地 score-artifacts 位置。它们只复现特定 `recon-runtime-mainline` 结果的 artifact-generation 阶段，用于调试、验证阈值、核对 replay 流程以及备份 Runtime 的 replay trace。
- 这些 replay 不是新的模型 checkpoint，也没有通过 `Research/docs/evidence/admitted-results-summary.md` 里列出的 admitted 复现流程，它们只是 Runtime 输出的 replay trace 的自说明记录。

## 为什么它们不能替代 admitted main evidence

## Leader / Developer 应如何引用
- Developer 在准备系统展示、Runtime 现象级问题复盘或写 `workspaces/runtime/` intake 时，才可以引用这些目录以便描述可再现的 replay 流程。但在任何 `Platform` / `Runtime-Server` 级别的 material（包括 `Docs/internal/competition-innovation-summary.md` (internal — not in public repository) 或 demo screencast）里，应使用 `admitted-results` 的主线 artifact；若同时演示 replay 的机制，请把它们呈现为 debugging/demo artifact，配合醒目标注”未经过 adjudication”。
- 所有 replay artifacts 继续存放在 `Research/experiments/` 中，并通过本 doc 附带的说明进行组织；如需要在 `docs/README.md` 或章节索引中引用，请链接到本条以保持 Research 里 admitted vs demo 资产的清晰边界。
