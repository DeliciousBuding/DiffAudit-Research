# `src/diffaudit`

这里放仓库内所有共享可执行代码。

## 设计目标

当前代码层的目标不是“一次性复现完所有论文”，而是先把各条方法线统一成一套可迭代的工程接口：

- `plan`
- `probe`
- `dry-run`
- `runtime smoke`
- `artifact summary`

这样可以把“代码准备好”“资产准备好”“结果准备好”三件事分开管理。

## 当前模块

| 路径 | 说明 |
| --- | --- |
| `config.py` | 仓库统一配置结构 |
| `cli/` | 所有仓库对外命令入口；`_parser.py` 定义 argparse surface，`_dispatch.py` 负责命令分发 |
| `attacks/` | 各方法线的 planner / probe / dry-run / smoke |
| `pipelines/` | 通用 pipeline 逻辑 |
| `utils/` | 共享指标、I/O、Gaussian 和 diffusion schedule helper |
| `metrics/` | placeholder package；shared metric implementations currently live in `utils/metrics.py` |
| `reports/` | 统一报告输出层 |

## 当前攻击线

| 方法 | 代码文件 | 当前能力 |
| --- | --- | --- |
| `secmi` | `attacks/secmi.py`, `attacks/secmi_adapter.py` | plan / probe / prepare / dry-run / runtime probe / synth smoke |
| `pia` | `attacks/pia.py`, `attacks/pia_adapter.py` | plan / probe / dry-run / runtime probe / runtime smoke / synth smoke |
| `clid` | `attacks/clid.py` | plan / probe / dry-run / dry-run smoke / artifact summary |
| `recon` | `attacks/recon.py` | plan / probe / dry-run / eval smoke |
| `variation` | `attacks/variation.py` | plan / probe / dry-run / synthetic smoke |

## 开发约定

1. 新增方法线时，先补测试，再补 planner / probe / dry-run。
2. 真实 benchmark 不到位前，优先补 smoke 或 artifact summary。
3. 不要把个人实验脚本直接堆进 `src/diffaudit/` 根目录。
4. 新命令接入时，默认同时更新：
   - `src/diffaudit/cli/_parser.py`
   - `src/diffaudit/cli/_dispatch.py`
   - [README.md](../../README.md)
   - [configs/README.md](../../configs/README.md)
   - [experiments/README.md](../../experiments/README.md)
   - 对应工作区 `plan.md`
