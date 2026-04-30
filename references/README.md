# References

论文和参考资料索引。

Git 仓库不包含第三方论文 PDF 或 DOCX 文件。这些材料按上游许可条款管理。需要本地副本时，用 `materials/manifest.csv` 查找来源 URL、校验值和预期本地路径。

## 目录结构

`materials/` 按研究方向组织：

- `black-box/`
- `gray-box/`
- `white-box/`
- `survey/`
- `context/`

## 索引文件

| 文件 | 用途 |
| --- | --- |
| `materials/manifest.csv` | 机器可读的来源清单（路径、方向、评分、校验值） |
| `materials/README.md` | 目录布局、获取规则、命名规则和评分标准 |
| `materials/paper-index.md` | 按论文汇总的索引（含开源链接） |

## 维护规则

- 文件名用 ASCII 和 kebab-case
- 每篇论文在 `manifest.csv` 中占一行
- 不提交第三方 PDF、DOCX、数据集、模型权重等大文件
- 本地论文副本放在 Git 外（如 `<DIFFAUDIT_ROOT>/Download/shared/papers/`）
- 用 `credibility_score` 和 `reference_value_score` 做显式分类

manifest 行或本地路径的存在不代表该论文已被复现。
