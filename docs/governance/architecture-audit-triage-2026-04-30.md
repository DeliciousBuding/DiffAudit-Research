# Architecture Audit Triage — 2026-04-30

This note records the durable outcomes from the 2026-04-30 architecture review.
The detailed reviewer packet was treated as an input, not as an admitted
governance artifact: multiple counts were stale after the Phase 0 utils merge,
and several tables mixed tracked repository facts with local workspace state.

## Admitted Findings

| Area | Verdict | Follow-up |
| --- | --- | --- |
| `src -> scripts` package boundary | Correct. `h2_adapter.py` depended on `scripts.train_smp_lora.create_ddpm_model`, which is outside the installed package. | Move the canonical DDPM model factory into `src/diffaudit/defenses/lora_ddpm.py`; scripts import from `src`. |
| Missing package initializers | Correct. `attacks/`, `pipelines/`, and `reports/` relied on implicit namespace packages while sibling packages used `__init__.py`. | Add explicit package initializers for consistency. |
| Local checks vs CI drift | Correct. CI ran public-surface and Markdown-link guards, while `run_local_checks.py --fast` did not. | Add both guards to local checks. |
| `dpdm_w1.py` external import boundary | Correct but not fixed in this PR. It still mutates `sys.path` to load ignored `external/DPDM` code. | Future PR: vendor the minimal DPDM subset or wrap it behind an explicit optional asset contract. |
| `gsa.py` / `gsa_observability.py` cycle | Correct but not fixed in this PR. Current lazy import works, but the shared helpers should be split out before larger GSA refactors. | Future PR: extract `gsa_common.py`. |
| `pyproject.toml` dependency surface | Correct but not fixed in this PR. The package metadata is intentionally much thinner than the research conda environment. | Future PR: split package extras into `core`, `research`, `gpu`, and `dev`. |

## Rejected Or Stale Claims

| Claim Type | Reason |
| --- | --- |
| Exact source, script, test, docs, workspace, and disk counts | Stale after PR #29 and sensitive to ignored local artifacts. Future audits must state whether counts come from `git ls-files` or full local filesystem scans. |
| CLI command tables in the detailed packet | The table contained duplicate rows and one non-existent command. Regenerate from `src/diffaudit/cli.py` before using it as evidence. |
| `graybox_triscore.py` and `semantic_aux_fusion.py` still duplicating metric helpers | Stale. PR #29 migrated both to `diffaudit.utils.metrics`. |
| `configs/feishu_sync.local.yaml` tracked in Git | False on current `main`; the path is ignored and not tracked. |
| Raw local disk cleanup totals | Useful for operator cleanup, but not suitable for public governance docs because they depend on ignored local assets. |

## Audit Rule Going Forward

Architecture-review packets are allowed as internal inputs, but public
governance docs should only admit claims that are:

- reproducible from tracked files or explicitly marked as local-only;
- dated with an absolute date;
- free of machine-local paths and agent-process details;
- expressed as actionable follow-up items rather than long inventory dumps.
