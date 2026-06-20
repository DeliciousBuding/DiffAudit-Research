# E2 False-Promotion Expansion Queue

> Date: 2026-06-07
> Source refresh: `2026-06-07T19:29:29.792284+00:00`
> Scope: next no-download public-surface checks after the 13-row C14 baseline.

## Decision

最新 metadata refresh、`E2SCT-011`、`E2SCT-020`、`E2SCT-019` 和 `E2SCT-024` 行级 exemplar 复核，以及 `E2SCT-022`、`E2SCT-023`、`E2SCT-025`、`E2SCT-028` 的详细关闭检查后，C14 `13` 行以外还有 `0` 个值得下一轮 no-download 复核的 public-surface rows。`E2SCT-022`、`E2SCT-023`、`E2SCT-025` 和 `E2SCT-028` 已关闭为 support-only / watch-plus / code-public reference，不进入 C14，也不再作为待首轮检查的扩展队列成员；`E2SCT-019` 和 `E2SCT-024` 已成为 C14 false-promotion exemplars。剩余队列只用于扩展 false-promotion corpus 的候选检查，不是 admitted evidence，不是 N50 external denominator，也不释放 GPU/DCU。

Do not update the paper C14 selected-row count from `13` until a detailed row-level public-surface check turns another row into a clean exemplar and the review packet/codebook are regenerated.

## Queue

| Priority | Row | Title | Public surface observed | Weak-rule pressure | First blocker | Status |
| --- | --- | --- | --- | --- | --- | --- |
| - | - | - | - | - | No remaining post-C14 expansion row after the 2026-06-07/2026-06-08 detailed checks. | closed |

## Execution Boundary

- Use only public metadata, README/raw page text, API tree/catalog metadata, and existing no-download scripts.
- Do not download archives, media payloads, model weights, datasets, or generated responses.
- Do not run GPU/DCU jobs from this queue.
- If a row only restates a known semantic mismatch, close it as bounded support instead of expanding taxonomy.
- If a row becomes a clean false-promotion exemplar, add a dedicated public-surface check first, then regenerate the C14 assets and review bundle.
