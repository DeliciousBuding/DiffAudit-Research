# Implementation Plan

## Status

- Shared CLI and local checks are active.
- `challenger-queue.md` is the active candidate-management surface.
- Long dated implementation notes have moved to `legacy/workspaces/`.

## Next Action

Keep validation and public-surface guards current:

```powershell
python -X utf8 scripts/check_public_surface.py
python -X utf8 scripts/check_markdown_links.py
conda run -n diffaudit-research python scripts/run_local_checks.py --fast
```

## Current Verdict

Implementation is a support lane. It should improve reproducibility and
handoff quality, not create unsupported research claims.
