# Assets And Storage

This directory explains where non-code research assets live.

| Document | Purpose |
| --- | --- |
| [data-and-assets-handoff.md](data-and-assets-handoff.md) | How to obtain datasets, weights, supplementary files, and upstream code. |
| [storage-boundary.md](storage-boundary.md) | What belongs in Git, `Download/`, `external/`, `third_party/`, and workspace assets. |
| [download-naming-policy.md](download-naming-policy.md) | Naming rules for `<DIFFAUDIT_ROOT>/Download/`. |
| [research-download-master-list.md](research-download-master-list.md) | Rebuild list for first-wave assets. |
| [research-download-current-status.md](research-download-current-status.md) | Current local asset status snapshot. |
| [recon-public-asset-mapping.md](recon-public-asset-mapping.md) | Boundary notes for the public recon asset bundle. |

Large files stay outside the Git repository. Commit manifests, summaries, and
provenance notes instead of raw datasets, checkpoints, tensors, or archives.

For local workspace hygiene, use:

```powershell
python -X utf8 scripts/audit_local_storage.py
```

The script defaults to dry-run. It reports Git-tracked large files, misplaced
raw assets, generated run payloads, cache/tmp directories, and large external
clones without moving anything unless `--execute` is passed.
