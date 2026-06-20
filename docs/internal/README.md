# 内部研究资料

此目录存放维护者需要的资料，不属于公开入门路径。

可能包含：

- 长期进度台账
- Agent 提示词和操作记录
- 比赛时期材料
- 论文阅读报告
- 外部模型审查包
- 规划草稿和退役研究包笔记

不要将这些文件作为产品文案引用。如果某个发现需要对外展示，
请改写后放入 [../evidence/](../evidence/) 或
[../product-bridge/](../product-bridge/)，并注明明确的证据状态。

当前长期运行目标提示词：
[research-autonomous-execution-prompt.md](research-autonomous-execution-prompt.md)。

当前 CCF-A 论文推进路线：
[ccf-a-research-roadmap-2026-06-06.md](ccf-a-research-roadmap-2026-06-06.md)。

当前 E2 false-promotion 协议草案：
[e2-false-promotion-protocol-2026-06-06.md](e2-false-promotion-protocol-2026-06-06.md)。

当前 C14/E2 pre-label external-adjudication preregistration：
[c14-e2-external-adjudication-preregistration-2026-06-09.md](c14-e2-external-adjudication-preregistration-2026-06-09.md)。
它只冻结 reviewer packet、post-label key、weak-rule baselines、聚合命令和
`n_reviewers=0` 状态；不是 external label result。

当前 E2 v2 internal pilot 输出：
[e2-pilot-2026-06-06-v2/](e2-pilot-2026-06-06-v2/)。

当前 E2 N50 freeze preflight seeds：
[e2-n50-freeze-preflight-2026-06-06/](e2-n50-freeze-preflight-2026-06-06/)。
当前严格结论：此目录还不是 external denominator；先看其中的
`e2_n50_freeze_triage_2026_06_06.csv`、
`e2_n50_public_surface_scout_2026_06_06.csv`、对应 URL check 输出，以及
v1 row review 表
`e2_n50_freeze_review_decisions_v1.csv`。v1 结论仍是 `0` 行可计入 external
denominator。`E2Q-005` Tracing the Roots 已完成 feature-packet-only
single-row package-work 检查，仍不进入 N50 denominator。后续 challenger scout
确认目前没有候选超过 `E2Q-005`；`E2Q-006` CopyMark 只在 compact manifest
出现后才值得重查，`E2SCT-001` MT-MIA 只能作为另开 tabular/relational stratum
的线索。
`E2Q-005` 复核材料使用同目录的
`e2q005_external_style_review_rubric_2026_06_06.md` 和
`e2q005_external_style_review_template_2026_06_06.csv`，只审查
feature-packet-only row acceptability，不进入 N50 denominator。

当前 C14 / high-value public-surface 接手入口：

- `e2_false_promotion_exemplar_summary_2026_06_07.md` 和同名 CSV：十三行
  false-promotion stress object；不是 admitted evidence、N50 denominator、
  prevalence 或 external adjudication。
- `e2_false_promotion_expansion_queue_2026_06_07.md`：post-C14 expansion
  queue 当前为 `0`，不能据此扩大 C14。
- `e2_high_value_public_asset_delta_refresh_2026_06_09.md` 和同名 CSV：
  九个高价值 public asset 的 no-download identity refresh；`9 / 9`
  identity matched，compact reopen hints 为 `0`，不改变 C14、N50、
  admitted evidence、second public score/response asset 或 compute release。
- `e2_high_value_public_asset_delta_refresh_late_2026_06_09.md` 和同名
  CSV：同一 watchlist 的晚间字段级复核；`9 / 9` identity matched，关键
  gate 字段相对早前 refresh 无变化，admission-grade compact reopen surface
  为 `0`。
- `e2_high_value_public_asset_delta_gate_queue_2026_06_09.csv`：后续只读
  gate-review 队列；有 row-bound packet、metric JSON/verifier、target identity
  和 surface-delta control 前，不释放 GPU/DCU。
- `e2sct035_openlvlm_mia_vlm_public_surface_check_2026_06_09.md`：OpenLVLM-MIA
  只作为 future VLM controlled-benchmark scout；不进入当前 image-diffusion
  Direction A、C14、N50 或 second-asset 口径。

当前 E2 codebook refinement 记录：
[e2-codebook-refinement-2026-06-06.md](e2-codebook-refinement-2026-06-06.md)。

当前 E1 manifest-first scout：
[e1-manifest-first-scout-2026-06-06.md](e1-manifest-first-scout-2026-06-06.md)。
