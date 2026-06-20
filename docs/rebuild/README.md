# 重建（已归档）

本目录先前跟踪 DiffAudit Research 的代码库重建工作。重建计划已归档至 `Docs/archive/Research/docs/rebuild/codebase-rebuild-plan.md`。

当前状态（截至 2026-04-30 已合并）：

- 共享工具提取至 `src/diffaudit/utils/`。
- CLI 包拆分至 `src/diffaudit/cli/`。
- 本地检查与公开表层和 Markdown 链接守卫对齐。
- 从 `src/diffaudit/` 移除空的占位包目录。

仍待处理的重建工作：

- 仅在特征测试存在后再拆分最大的适配器模块。
- 用显式的公共辅助 API 替换私有跨模块导入。
- 当测试、CLI 命令或下游消费方需要时，将剩余可复用脚本逻辑移入包模块。
- 在包/运行时边界稳定后重新审视包依赖 extras。

## 规则

- 优先选择不改变行为的小型 PR。
- 不要将代码架构重建与新的 GPU 实验混合。
- 不要将证据文件移入此目录。
- 此处仅记录长期有效决策；短期执行笔记归属 PR 或需要保留时归属 `legacy/`。
