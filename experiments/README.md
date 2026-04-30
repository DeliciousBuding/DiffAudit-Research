# 实验输出

存放可提交的最小实验输出和 smoke 结果。

## 当前内容

| 目录 | 说明 |
| --- | --- |
| `secmi-smoke/` | 最小 smoke pipeline 输出 |
| `secmi-synth-smoke/` | CPU synthetic smoke 输出 |
| `secmi-synth-smoke-gpu/` | GPU synthetic smoke 输出 |
| `pia-runtime-smoke-cpu/` | CPU PIA runtime smoke 输出 |
| `pia-runtime-smoke-gpu/` | GPU PIA runtime smoke 输出 |
| `pia-synth-smoke-cpu/` | CPU PIA synthetic smoke 输出 |
| `pia-synth-smoke-gpu/` | GPU PIA synthetic smoke 输出 |
| `clid-dry-run-smoke/` | CLiD dry-run smoke 输出 |
| `clid-artifact-summary/` | CLiD 上游 artifact 复算输出 |
| `recon-eval-smoke/` | 黑盒 reconstruction 评估 smoke 输出 |
| `recon-mainline-smoke/` | 黑盒 reconstruction 主线 smoke 输出 |
| `recon-artifact-summary/` | reconstruction score artifact 复算输出 |
| `recon-upstream-eval-smoke/` | reconstruction 上游评估 smoke 输出 |
| `variation-synth-smoke/` | API-only variation synthetic smoke 输出 |
| `blackbox-status/` | 黑盒结果统一汇总 |
| `templates/` | 结果结构模板 |

## 规则

- 不提交私有数据集或大体积中间产物
- 可以提交 `summary.json` 作为运行记录
- benchmark 结果要写清楚数据前提和攻击假设
- 不提交生成图片、权重文件（`.pt`/`.npz`）等可再生产物
- 需要复核原始输出时，从团队数据镜像或本地 `Download/` 恢复

## 新增实验目录

1. 优先只提交 `summary.json`
2. smoke 生成的临时文件在命令结束后清理
3. 目录命名格式：`方法-模式-设备/场景`（如 `pia-runtime-smoke-gpu`）
