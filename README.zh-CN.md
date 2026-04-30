<div align="center">

<img src="docs/assets/brand/diffaudit-logo.svg#gh-light-mode-only" alt="DiffAudit" width="360">
<img src="docs/assets/brand/diffaudit-logo-white.svg#gh-dark-mode-only" alt="DiffAudit" width="360">

# DiffAudit Research

**扩散模型隐私风险审计工具集。**

[English](README.md) | [中文](README.zh-CN.md)

[![Tests](https://github.com/DeliciousBuding/DiffAudit-Research/actions/workflows/tests.yml/badge.svg)](https://github.com/DeliciousBuding/DiffAudit-Research/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)
![Status](https://img.shields.io/badge/status-research%20prototype-0F766E)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

[DiffAudit Platform](https://github.com/DeliciousBuding/DiffAudit-Platform) ·
[文档](docs/README.md) ·
[快速开始](docs/start-here/getting-started.md) ·
[数据与资产](docs/assets-and-storage/data-and-assets-handoff.md) ·
[实验状态](docs/evidence/reproduction-status.md) ·
[安全](SECURITY.md)

</div>

---

DiffAudit Research 实现了面向扩散模型的成员推理攻击与防御方法。覆盖三种攻击者知识级别——黑盒、灰盒、白盒——并跟踪每种方法从论文阅读到可复现实验的完整过程。

本仓库是 [DiffAudit](https://github.com/DeliciousBuding/DiffAudit-Platform) 系统的研究层，专注于研究代码和实验跟踪。产品界面在 [DiffAudit Platform](https://github.com/DeliciousBuding/DiffAudit-Platform)，任务调度在 Runtime-Server。

每条研究方向都按统一的阶段跟踪：

| 阶段 | 说明 |
| --- | --- |
| 论文基线 | 复现或适配已知的攻击和防御方法，作为对照参考。 |
| 新方法探索 | 带着明确假设测试新想法，给出结论。 |
| 已验证结果 | 只有经过审查、可复现的实验才会提升到这一级。 |

## 系统架构

```mermaid
flowchart LR
  Papers["论文与已发表方法"] --> Research["DiffAudit Research"]
  Ideas["新的研究问题"] --> Research
  Research --> Results["实验结果与状态跟踪"]
  Results --> Runtime["Runtime 任务执行"]
  Results --> Platform["DiffAudit Platform"]
  Platform --> Reports["审计报告与导出"]
```

## 快速开始

```powershell
git clone https://github.com/DeliciousBuding/DiffAudit-Research.git
cd DiffAudit-Research
conda env create -f environment.yml
conda activate diffaudit-research
python scripts/bootstrap_research_env.py --install
python scripts/verify_env.py
python -m diffaudit --help
```

大型数据集和模型权重不存储在 Git 中。配置本地数据路径请参考
[docs/assets-and-storage/data-and-assets-handoff.md](docs/assets-and-storage/data-and-assets-handoff.md)。

## 文档导航

| 需求 | 入口 |
| --- | --- |
| 新贡献者上手 | [docs/start-here/getting-started.md](docs/start-here/getting-started.md) |
| 环境配置 | [docs/start-here/teammate-setup.md](docs/start-here/teammate-setup.md) |
| 数据集与模型权重 | [docs/assets-and-storage/data-and-assets-handoff.md](docs/assets-and-storage/data-and-assets-handoff.md) |
| CLI 命令 | [docs/start-here/command-reference.md](docs/start-here/command-reference.md) |
| 实验状态 | [docs/evidence/reproduction-status.md](docs/evidence/reproduction-status.md) |
| 平台集成 | [docs/product-bridge/README.md](docs/product-bridge/README.md) |
| 仓库结构 | [docs/start-here/repo-map.md](docs/start-here/repo-map.md) |
| 完整文档索引 | [docs/README.md](docs/README.md) |

## 仓库结构

| 路径 | 内容 |
| --- | --- |
| `src/diffaudit/` | Python 包和 CLI——攻击方法、防御方法、评估指标、工具函数。 |
| `configs/` | 实验配置和本地路径模板。 |
| `tests/` | 测试套件。 |
| `scripts/` | 环境搭建、验证和实验脚本。 |
| `docs/` | 贡献指南、实验状态、平台集成文档。 |
| `workspaces/` | 各研究方向的当前状态。 |
| `legacy/` | 归档的实验记录和历史。 |
| `external/` | 上游代码克隆（git-ignored）。 |
| `third_party/` | 上游代码子集（含许可证声明）。 |

## 实验跟踪

每条研究方向有一个状态标签，表示其成熟度：

| 状态 | 含义 |
| --- | --- |
| `research-ready` | 论文、上游代码和数据需求已审查。 |
| `code-ready` | 命令、配置和测试已存在于本仓库。 |
| `asset-ready` | 所需数据集或模型权重已在本地就绪。 |
| `evidence-ready` | 已有经过审查的实验总结。 |
| `benchmark-ready` | 可复现论文级基准测试。 |

冒烟测试和空运行属于工程验证，不是基准测试结果。负面结果会被保留，避免重复失败实验。

## 引用与许可

引用 DiffAudit Research 请使用 [CITATION.cff](CITATION.cff)。上游论文、数据集和第三方代码请按其各自条款引用。

源代码、配置、测试、脚本和原创文档采用 [Apache License 2.0](LICENSE) 许可。
详见 [docs/governance/licensing.md](docs/governance/licensing.md) 和 [NOTICE](NOTICE)。
