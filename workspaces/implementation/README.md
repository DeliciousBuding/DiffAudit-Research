# 实现工作台

## 当前状态

- 方向：共享 CLI、模式、验证器和仓库工具。
- 优先级：维护实验合约和公开文档质量。
- GPU：无。

## 文件

| 文件 | 用途 |
| --- | --- |
| [plan.md](plan.md) | 当前状态。 |
| [challenger-queue.md](challenger-queue.md) | 按优先级分层排列的活跃任务队列。 |
| [result-schema.md](result-schema.md) | 共享结果模式笔记。 |
| [artifacts/unified-attack-defense-table.json](artifacts/unified-attack-defense-table.json) | 当前唯一活跃的 admitted attack-defense 机器可读总表。 |
| [artifacts/admitted-evidence-bundle.json](artifacts/admitted-evidence-bundle.json) | Platform/Runtime 只读的五行 admitted evidence bundle。 |

`workspaces/implementation/unified-attack-defense-table.json` 不是活跃入口；
不要在 implementation 根目录恢复旧表副本。

## 归档

已关闭的笔记位于
[../../legacy/workspaces/implementation/2026-04/](../../legacy/workspaces/implementation/2026-04/)。
