# Test Guide

DiffAudit Research 的自动化测试套件。

测试设计为 CPU-first：不依赖下载的数据集、模型权重、`external/` 克隆或 GPU，除非测试名称明确标注。

## 测试分组

| 分组 | 覆盖范围 |
| --- | --- |
| `test_attack_registry.py` | CLI、planner、adapter、SecMI probe 和 smoke |
| `test_pia_*.py`, `test_sima_adapter.py`, `test_tmiadm_adapter.py` | 灰盒 adapter 和防御测试 |
| `test_gsa_*.py` | 白盒 GSA adapter 和可观测性测试 |
| `test_recon_attack.py`, `test_clid_smoke.py`, `test_variation_attack.py` | 黑盒方法测试 |
| `test_*report*.py`, `test_validate_*.py` | 报告和验证表测试 |
| `test_*local*.py`, `test_render_team_local_configs.py` | 本地配置和仓库工具测试 |
| `helpers.py` | 共享测试 fixtures（fake CIFAR10、fake SecMI 工作区等） |

归档测试在 `legacy/`，不在活跃套件中。

## 运行测试

快速本地检查：

```powershell
conda run -n diffaudit-research python -X utf8 scripts/run_local_checks.py --fast
```

Adapter 测试：

```powershell
conda run -n diffaudit-research python -m unittest tests.test_attack_registry tests.test_pia_adapter tests.test_pia_epsilon_output_noise tests.test_pia_input_blur_defense tests.test_sima_adapter tests.test_temporal_surrogate tests.test_tmiadm_adapter tests.test_gsa_adapter
```

完整测试：

```powershell
conda run -n diffaudit-research python -m unittest
```

## Fixture 规则

- 用 `tests.helpers.make_fake_cifar10()` 代替各文件自己的 fake CIFAR10
- 用 `tests.helpers.create_fake_secmi_repo()` 代替真实 `external/SecMI`
- 上游脚本测试用临时 fake 文件，不读 `external/` 克隆
- 生成的配置、score 文件和工作区用临时目录
- 不添加依赖原始数据集、checkpoint 或本地绝对路径的测试
