# 入门指南

> **Note:** For current Phase G work, see [docs/start-here/phase-g-runbook-2026-06-30.md](phase-g-runbook-2026-06-30.md)

*Last updated: 2026-07-03*

这份文档面向第一次进入 DiffAudit Research 仓库的新成员或外部贡献者。

## 先做什么

建议按这个顺序入手：

1. 阅读根目录 [README.md](../../README.md)
2. 阅读 [docs/start-here/teammate-setup.md](teammate-setup.md)
3. 按 [docs/assets-and-storage/data-and-assets-handoff.md](../assets-and-storage/data-and-assets-handoff.md) 补齐 `Download\` 资产并绑定本地路径
4. 按 [docs/start-here/command-reference.md](command-reference.md) 跑一次环境验证、资产探针和 `dry-run`
5. 阅读 [docs/start-here/environment.md](environment.md)
6. 阅读 [docs/governance/github-collaboration.md](../governance/github-collaboration.md)
7. 进入自己负责的工作区

## 需要先知道的几件事

- 这是研究仓库，不是产品仓库
- 当前默认主线是 Paper 1 Phase G：H1/DAAB run-dynamics 和 claim qualification
- 黑盒、灰盒、白盒工作区是历史/候选方向入口；除非 `ROADMAP.md` 明确重开，不作为当前主线
- 代码、资产、实验三者必须分开表述
- 没有真实运行证据，不要说“复现成功”

## 第一次本地验证

```powershell
conda activate diffaudit
python scripts/util/bootstrap_research_env.py --install
python scripts/util/verify_env.py
python -m diffaudit --help
python -m pytest tests/test_cli_module_entrypoint.py tests/test_render_team_local_configs.py -q
python -m diffaudit plan-variation --config configs/attacks/variation-plan.yaml
python -m diffaudit plan-pia --config configs/attacks/pia-plan.yaml
```

第一次使用前，先复制 `configs/assets/team.local.template.yaml` 为本地 `configs/assets/team.local.yaml`，再填写自己的真实路径。大数据集、权重和 supplementary 包默认放在仓库外的 `<DIFFAUDIT_ROOT>/Download/`，不要放进 `Research/external/`。

如果当前 shell 还没激活 conda，也可以直接写成：

```powershell
conda run -n diffaudit python scripts/util/verify_env.py
conda run -n diffaudit python -m diffaudit --help
conda run -n diffaudit python -m pytest tests/test_cli_module_entrypoint.py tests/test_render_team_local_configs.py -q
conda run -n diffaudit python -m diffaudit probe-secmi-assets --config configs/attacks/secmi-plan.yaml
```

## 工作区选择

- 负责黑盒：`workspaces/black-box/`
- 负责白盒：`workspaces/white-box/`
- 负责灰盒：`workspaces/gray-box/`
- 负责共享工程：`workspaces/implementation/`

## 做事方式

1. 先写计划
2. 再写配置
3. 再写 adapter / probe
4. 先跑对应方向的 `probe-*` 命令
5. 最后才跑真实实验
