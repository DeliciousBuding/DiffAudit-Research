# 资产与存储

本目录说明非代码研究资产的存放位置。

| 文档 | 用途 |
| --- | --- |
| [data-and-assets-handoff.md](data-and-assets-handoff.md) | 如何获取数据集、权重、补充文件与上游代码。 |
| [storage-boundary.md](storage-boundary.md) | 哪些内容属于 Git、`Download/`、`external/`、`third_party/` 以及工作区资产。 |
| [download-naming-policy.md](download-naming-policy.md) | `<DIFFAUDIT_ROOT>/Download/` 的命名规则。 |
| [research-download-master-list.md](research-download-master-list.md) | 首波资产重建清单。 |
| [research-download-current-status.md](research-download-current-status.md) | 当前本地资产状态快照。 |
| [recon-public-asset-mapping.md](recon-public-asset-mapping.md) | 公开 recon 资产包的边界说明。 |

大文件不进入 Git 仓库。提交清单、摘要与来源说明，而不是原始数据集、checkpoint、tensor 或压缩包。

本地工作区卫生检查请使用：

```powershell
python -X utf8 scripts/audit_local_storage.py
```

脚本默认为 dry-run 模式，会报告 Git 追踪的大文件、放错位置的原始资产、生成的运行产物、cache/tmp 目录以及大型 external 克隆，只有在传入 `--execute` 时才会实际移动文件。
