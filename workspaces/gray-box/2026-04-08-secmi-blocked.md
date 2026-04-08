# 2026-04-08 Gray-Box Follow-Up: SecMI Blocked Baseline

## Status Panel

- `owner`: `research_leader`
- `updated_at`: `2026-04-08 23:17:22 +08:00`
- `selected_baseline`: `SecMI`
- `current_state`: `blocked baseline`
- `evidence_level`: `runtime-probe`

## Command Run

```powershell
conda run -n diffaudit-research python -m diffaudit runtime-probe-secmi `
  --config tmp/configs/rendered-checks/secmi.local.yaml `
  --repo-root external/SecMI
```

## Probe Result

```json
{
  "status": "blocked",
  "error": "Missing SecMI flagfile: REPLACE_WITH_SECMI_MODEL_DIR\\flagfile.txt",
  "repo_root": "external/SecMI"
}
```

## Interpretation

- The current `SecMI` local config is still placeholder-based and does not point to a real paper-aligned model root.
- The missing `flagfile.txt` is a hard blocker for the existing runtime adapter.
- `SecMI` should remain in the roadmap as a gray-box baseline candidate, but it should not continue to compete for GPU time in the current sprint.

## Decision

`SecMI` is now recorded as `blocked baseline` until a real checkpoint root and matching `flagfile.txt` are supplied.
