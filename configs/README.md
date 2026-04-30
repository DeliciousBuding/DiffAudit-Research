# 配置说明

这个目录放实验配置文件。

## 目录结构

- `attacks/`：攻击方法配置和超参数
- `benchmarks/`：基准测试和 smoke 配置
- `assets/`：本地路径模板（不提交个人真实路径）

## 使用原则

- 共享配置不要写个人机器的真实路径
- 需要本地路径时，参考 `assets/team.local.template.yaml` 创建自己的 `team.local.yaml`
- `attacks/*.yaml` 定义攻击参数，不包含本地目录结构
- 数据集、模型权重等大文件放在仓库外的 `<DIFFAUDIT_ROOT>/Download/`，通过 `assets/team.local.yaml` 配置路径映射

## 配置文件速查

| 文件 | 用途 |
| --- | --- |
| `attacks/secmi_plan.yaml` | SecMI 探针和 dry-run 配置 |
| `attacks/pia_plan.yaml` | PIA 探针、dry-run 和 smoke 配置 |
| `attacks/clid_plan.yaml` | CLiD 条件场景配置 |
| `attacks/recon_plan.yaml` | 黑盒 reconstruction 攻击配置 |
| `attacks/variation_plan.yaml` | API-only variation 攻击配置 |
| `benchmarks/secmi_smoke.yaml` | 最小 smoke 配置 |
| `assets/example.local.yaml` | 路径占位示例（无真实绑定） |
| `assets/team.local.template.yaml` | 新成员填写的本地路径模板 |

## 不要提交的文件

- `assets/team.local.yaml`
- `assets/*.local.yaml` 中的真实机器路径
- 指向大文件的个人绝对路径

如果脚本需要本地数据路径，先复制 `assets/team.local.template.yaml` 为 `assets/team.local.yaml`，再填入真实路径。
