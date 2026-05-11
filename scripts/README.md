# 脚本目录

存放可重复使用的工具脚本。

## 原则

- 一个脚本做一件事
- 主要服务环境验证、数据检查、实验管理
- 不放一次性本地命令

## 环境变量

| 变量 | 用途 |
| --- | --- |
| `DIFFAUDIT_WORKSPACE_ROOT` | 工作区根目录覆盖 |
| `DIFFAUDIT_RESEARCH_PYTHON` | Python 解释器路径覆盖 |

脚本默认从当前 `Research/scripts` 位置推导路径，可以通过环境变量覆盖。

## 脚本速查

| 脚本 | 用途 |
| --- | --- |
| `run_local_checks.py` | 运行本地质量检查，支持 `--python` 和 `--fast` |
| `audit_local_storage.py` | 审计本地大文件和数据边界，默认 dry-run |
| `validate_attack_defense_table.py` | 校验攻击-防御汇总表 |
| `export_admitted_evidence_bundle.py` | 导出并校验完整 admitted evidence bundle |
| `validate_intake_index.py` | 校验 intake index 的数据和清单 |
| `validate_local_api_registry_alignment.py` | 校验与 Runtime-Server 的注册表一致性 |
| `monitor_gsa_sequence.py` | 监控 GSA 训练进度 |
| `prepare_clid_local_bridge.py` | 准备 CLiD 本地运行配置 |
| `launch_dpdm_training.ps1` | 启动单个 DPDM 训练 |
| `launch_dpdm_target_and_shadows.ps1` | 启动 target + shadow 训练序列 |
| `launch_dpdm_shadow_sequence.ps1` | 按顺序启动 shadow 训练 |
| `run_x90_larger_surface_triscore.py` | X-90 larger-surface 复算辅助 |
| `run_x90_tmiadm512_assets.py` | X-90 TMIA-DM 512-surface 数据辅助 |
