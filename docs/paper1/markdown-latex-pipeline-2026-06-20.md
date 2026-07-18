> **QUARANTINED / historical process note (2026-07-18).** Canonical manuscript is **not** stored in this public repo. Do not treat listed private LaTeX paths as clone requirements.

# Markdown → LaTeX → PDF Pipeline

> 用户要求：论文应该先写完整 markdown 版，再转 LaTeX，再编译 PDF。
> 当前状态：直接写 LaTeX 编译。需改为 markdown 先行。

## 工作流

```
1. 科学内容 → docs/paper1/paper.md（markdown，易讨论修改）
2. markdown 审查（ChatGPT、Workflow、人工）
3. md → tex 转换（pandoc 或手动）
4. LaTeX 编译 → paper.pdf
```

## 工具链

```bash
# Markdown → LaTeX
pandoc paper.md -o paper.tex --template=ieee

# 或手动维护 .md 和 .tex 同步
```

## 优势

- markdown 易读易改，方便 ChatGPT 审查
- 科学讨论聚焦内容而非排版
- Git diff 清晰可读
- LaTeX 只负责最终排版

## 当前状态

- `docs/paper1/paper-h1-section-markdown-2026-06-20.md` — H1 section markdown 版 ✅
- `[manuscript lives outside this public repo]` — 完整 LaTeX 源码 ✅
- 需要：将完整论文转为单一 markdown 文件，建立同步机制
