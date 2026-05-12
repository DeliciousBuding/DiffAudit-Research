# Pull Request

## Summary

- 

## Why

- 

## Validation

- [ ] I ran the relevant checks.
- [ ] I documented anything not verified.
- [ ] I scanned for private local paths, credentials, and data leaks when touching docs/configs.

Docs-only / evidence-only PRs:

```powershell
python -X utf8 scripts/check_public_surface.py
python -X utf8 scripts/check_markdown_links.py
```

Code, script, test, config, or workflow PRs:

```powershell
python -X utf8 scripts/run_local_checks.py --fast
```

## Scope

- [ ] black-box
- [ ] white-box
- [ ] gray-box
- [ ] implementation
- [ ] docs
- [ ] GitHub/repo governance
- [ ] assets / data setup
- [ ] third-party / licensing

## Limitations

- [ ] This PR does not present smoke/dry-run results as benchmark claims.
- [ ] This PR does not relicense or redistribute third-party datasets, weights, papers, or gated assets.

## Blockers / Follow-ups

- 
