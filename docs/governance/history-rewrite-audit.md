# History Rewrite Audit

> Status: audit only. No history rewrite has been performed.

This document records whether a future `git filter-repo` pass is worth doing.
It is separate from the current governance cleanup because history rewrites
require coordination, force-pushes, and local clone recovery.

## Current Finding

- Current tracked tree has no Git-tracked file at or above `1 MB`.
- Current cleanup removes or ignores small generated artifacts from the live
  branch, but does not erase them from older commits.
- Workspace-local datasets, weights, checkpoints, and generated runs are large,
  but they are not part of the current tracked tree.
- The main remaining history question is whether older commits still contain
  removed generated images, paper extraction caches, raw binary fixtures, or
  previously committed bulky artifacts.

## Candidate Paths For Future History Slimming

If a later phase explicitly approves history rewriting, inspect these paths
first:

| Path pattern | Reason |
| --- | --- |
| `experiments/_tmp_*/` | Temporary generated experiment images should not remain in public history. |
| `docs/internal/paper-reports/ocr/` | OCR cache output is generated and not source material. |
| `docs/internal/paper-reports/markdown/` | Full-paper extraction caches should not be tracked. |
| `references/materials/**/*.pdf` | Third-party papers should be represented by metadata, not Git blobs. |
| `references/materials/**/*.docx` | Third-party or working document binaries should stay outside Git. |
| `workspaces/**/assets/**` | Raw downloaded assets, checkpoints, archives, and normalized heavy artifacts should stay outside Git unless they are small manifests. |
| `workspaces/**/runs/**/bridged-model/**` | Model exports are large generated artifacts. |
| `workspaces/**/runs/**/checkpoints/**` | Checkpoints and optimizer states are large generated artifacts. |
| `*.pt`, `*.pth`, `*.ckpt`, `*.safetensors`, `*.npy`, `*.npz`, `*.bin` | Raw tensor/model/data blobs should not be committed. |
| `*.zip`, `*.tar`, `*.tar.gz`, `*.tgz`, `*.7z`, `*.rar` | Raw asset bundles and archives should live in `Download/` or an external mirror. |

## Proposed Audit Commands

Run these before deciding on a rewrite:

```powershell
git rev-list --objects --all |
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' |
  Sort-Object { [int64](($_ -split ' ')[2]) } -Descending |
  Select-Object -First 100

git filter-repo --analyze
```

If `git filter-repo --analyze` is used, review `.git/filter-repo/analysis/` and
confirm candidate paths against the table above.

## Force-Push Risk

A history rewrite would:

- invalidate existing commit SHAs
- require every collaborator to rebase, reclone, or hard-reset local work
- require all open branches and PRs to be coordinated
- risk losing unpushed local research artifacts if people reset incorrectly
- require GitHub branch-protection and PR-base coordination

Do not rewrite history from a routine cleanup PR.

## Rollback Plan If A Rewrite Is Approved Later

1. Create a mirror backup:

   ```powershell
   git clone --mirror https://github.com/DeliciousBuding/DiffAudit-Research.git DiffAudit-Research-pre-rewrite.git
   ```

2. Tag the last pre-rewrite state:

   ```powershell
   git tag pre-history-rewrite-YYYYMMDD
   git push origin pre-history-rewrite-YYYYMMDD
   ```

3. Run `git filter-repo` on a separate local clone.
4. Verify `git fsck`, tests, docs links, and large-file audit.
5. Force-push only after collaborator confirmation.
6. Keep the mirror backup until all collaborators confirm recovered clones.

## Conclusion

No rewrite in Stage 1: current-branch cleanup is sufficient for reviewability.
History rewriting should remain a separately approved operation with a concrete
blob report, explicit path filters, backup tag, and collaborator recovery plan.
