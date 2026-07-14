# Changelog

All notable changes to DiffAudit Research are documented here.

## [2026-07-11] — Paper 1 Evidence-Contract Reconstruction

### Changed
- Quarantined historical Phase G H1 targets and claims after invalid
  member/nonmember ground truth and resubstitution scoring were identified.
- Replaced the run-dynamics execution route with a predeclared member-only
  corrected-evidence protocol using held-out rows, common noise, row-bound
  scores, a validation attack, and hard STOP/REPLICATE/MATURE gates.
- Marked historical run-identity, continuation, N=512 cluster, temporal,
  knockout, and mechanism interpretations as diagnostic-only.

## [2026-07-05] — Governance & Toolchain Upgrade

### Added
- Ruff lint + format configuration in `pyproject.toml`
- Mypy type checking configuration
- Pytest markers: `slow`, `gpu`, `smoke`, `inference`
- Evidence claim JSON Schema (`claim-evidence-schema.json`)
- `check_stale_docs.py` for automated doc staleness detection
- Pre-commit: ruff lint + ruff-format hooks (bash → Python migration)
- Root `.gitignore` for workspace-level ignore rules

### Fixed
- Pre-commit YAML parsing errors (bash hooks converted to Python)
- 3 new pre-commit utility scripts: `_hook_no_dated_filenames.py`, `_hook_no_root_scripts.py`, `_hook_evidence_md_headers.py`

### Changed
- RESEARCH ROADMAP: `YYYYMMDD` → `YYYY-MM-DD` date format migration (155 evidence docs)
- `envOrDefault("true", ...)` → `strconv.ParseBool` for demo mode
- Dependabot: actions/checkout 6 → 7

## [2026-06-19] — Phase G Evidence Freeze (now quarantined)

- Frozen claim matrix established
- H1/DAAB run-dynamics replication (Phase G)
- N=512 two-cluster pattern analysis complete
- Evidence bank and paper manuscript under revision
