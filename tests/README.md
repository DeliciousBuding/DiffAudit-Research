# 测试说明

这里放自动化测试。

## 当前范围

- `test_attack_registry.py`：CLI、planner、adapter、SecMI probe 与 smoke 相关测试
- `test_smoke_pipeline.py`：配置加载、smoke pipeline 与资产说明测试

## 运行建议

优先在 `diffaudit-research` 环境中运行：

```powershell
conda run -n diffaudit-research python -m unittest tests.test_attack_registry tests.test_smoke_pipeline
```

如果要跑全量：

```powershell
conda run -n diffaudit-research python -m unittest
```
