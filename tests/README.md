# Test Guide

This directory contains the automated test suite for DiffAudit Research.

The suite is intentionally CPU-first. Tests should not require downloaded
datasets, model weights, ignored `external/` clones, or GPU access unless the
test name and skip condition make that explicit.

## Layout

| Group | Purpose |
| --- | --- |
| `test_attack_registry.py` | CLI, planner, adapter, SecMI probe, and SecMI smoke coverage. |
| `test_pia_*.py`, `test_sima_adapter.py`, `test_tmiadm_adapter.py` | Gray-box adapter characterization and defense-surface checks. |
| `test_gsa_*.py` | White-box GSA adapter, observability, and packet checks. |
| `test_recon_attack.py`, `test_clid_smoke.py`, `test_variation_attack.py` | Black-box method tests. |
| `test_*report*.py`, `test_validate_*.py` | Report and evidence-table validation. |
| `test_*local*.py`, `test_render_team_local_configs.py` | Local config, storage, and repository hygiene checks. |
| `helpers.py` | Shared test fixtures such as fake CIFAR10, fake SecMI workspaces, and CLI JSON capture. |

Archived tests live under `legacy/` and are not part of the active suite.

## Running Tests

Fast local gate:

```powershell
conda run -n diffaudit-research python -X utf8 scripts/run_local_checks.py --fast
```

Targeted adapter characterization gate:

```powershell
conda run -n diffaudit-research python -m unittest tests.test_attack_registry tests.test_pia_adapter tests.test_pia_epsilon_output_noise tests.test_pia_input_blur_defense tests.test_sima_adapter tests.test_temporal_surrogate tests.test_tmiadm_adapter tests.test_gsa_adapter
```

Full unittest suite:

```powershell
conda run -n diffaudit-research python -m unittest
```

## Fixture Rules

- Prefer `tests.helpers.make_fake_cifar10()` over per-file fake CIFAR10 classes.
- Prefer `tests.helpers.create_fake_secmi_repo()` over real `external/SecMI`
  dependencies.
- Tests that load upstream-style scripts should create temporary fake upstream
  files instead of reading ignored `external/` clones.
- Prefer temporary directories for generated configs, score packets, and
  workspaces.
- Do not add tests that require raw datasets, checkpoints, generated images, or
  local absolute paths.
