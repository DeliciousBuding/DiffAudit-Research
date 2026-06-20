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
| `run_pr_checks.py` | 运行 GitHub PR 快速门禁，不安装 PyTorch，不跑 runtime 测试 |
| `run_local_checks.py` | 运行本地质量检查，支持 `--python` 和 `--fast` |
| `audit_local_storage.py` | 审计本地大文件和数据边界，默认 dry-run |
| `check_public_surface.py` | 检查公开仓库路径/文本泄漏，并扫描主稿和生成 risk card 的候选结果越界语言 |
| `check_e2_freeze_preflight.py` | 离线校验 E2 freeze-preflight 表，防止把 scout/candidate rows 误写成 external denominator |
| `check_paper_release_packet.py` | 校验论文 release packet：manifest 路径、claim trace/provenance、dirty-tree review snapshot、MoFit gate-status 候选边界、C14 当前 no-reviewer/packet-ready-only 边界、PDF 页数/字体/禁词、LaTeX 日志、`main.tex` claim-boundary 句和 `refs.bib` 引用一致性 |
| `export_paper_supplement.py` | 从 `asset_manifest.json` 导出匿名 supplement ZIP、文件清单和 SHA-256，遵守 `anonymous_supplement_excluded`；`--check` 只校验可打包性 |
| `export_false_promotion_review_bundle.py` | 导出 C14 false-promotion 外部标注材料包；`--check` 只校验 packet/template/codebook 边界 |
| `aggregate_false_promotion_external_review.py` | 聚合 C14 false-promotion reviewer CSV；输出 packet/status/kappa 边界；无标签时 `--check` 只验证 packet label-readiness，不产生 adjudication 结论 |
| `check_e2_public_sources.py` | E2 N50 preflight URL 可达性检查；只做 HEAD/Range/1-byte 级 probe，不下载 artifact payload |
| `refresh_e2_public_surface_metadata.py` | E2 scout candidates 的 no-download metadata refresh；只读公开 API/page/tree/catalog 元数据，生成 gate-review queue |
| `build_e2_false_promotion_expansion_queue.py` | 从最新 no-download metadata refresh 生成 C14 之后的 false-promotion corpus 扩展候选队列；`--check` 校验队列未漂移 |
| `inspect_e2q005_tracing_roots_package.py` | E2Q-005 Tracing the Roots 的 OpenReview supplement 身份、tensor hash 与 replay JSON 对齐检查 |
| `replay_mofit_public_coco_scores.py` | 只抓取 MoFit 官方仓库 4 个公开 COCO 小文本分数文件和 2 个小 caption JSONL，校验 SHA/行数并重算 AUC/TPR；可输出 metrics JSON、alpha sweep、best-alpha ROC、implicit position manifest、gate-status CSV、candidate caption-order manifest、bootstrap/permutation controls；network 小文件 replay，不是 admission、N50 或 compute release |
| `aggregate_e2q005_external_review.py` | 聚合 `E2Q-005` 单行 external-style feature-packet review，保持 no-N50 边界 |
| `build_claim_gate_recode_packet.py` | 生成/校验 C1-C15 claim-gate blind recode template 与 manifest；只准备复标材料，不产生 reliability 结果 |
| `validate_attack_defense_table.py` | 校验攻击-防御汇总表 |
| `export_admitted_evidence_bundle.py` | 导出并校验完整 admitted evidence bundle |
| `render_admitted_risk_card.py` | 从 admitted evidence bundle 渲染并校验公开安全 risk card |
| `evaluate_report_correctness_faults.py` | 复用 risk-card renderer 和 public-surface guard，生成/校验 report-correctness fault-injection 矩阵 |
| `validate_intake_index.py` | 校验 intake index 的数据和清单 |
| `validate_local_api_registry_alignment.py` | 校验与 Runtime-Server 的注册表一致性 |
| `monitor_gsa_sequence.py` | 监控 GSA 训练进度 |
| `prepare_clid_local_bridge.py` | 准备 CLiD 本地运行配置 |
| `launch_dpdm_training.ps1` | 启动单个 DPDM 训练 |
| `launch_dpdm_target_and_shadows.ps1` | 启动 target + shadow 训练序列 |
| `launch_dpdm_shadow_sequence.ps1` | 按顺序启动 shadow 训练 |
| `run_x90_larger_surface_triscore.py` | X-90 larger-surface 复算辅助 |
| `run_x90_tmiadm512_assets.py` | X-90 TMIA-DM 512-surface 数据辅助 |
| `run_beans_lora_member_scout.py` | Beans known-split LoRA target 训练与 conditional denoising-loss scout |
