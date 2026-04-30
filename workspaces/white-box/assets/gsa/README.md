# GSA Assets Root

This directory is the early local data root for the white-box `GSA` method.

It exists to keep three concerns separate:

- `external/GSA` — upstream code clone
- `workspaces/white-box/assets/gsa` — local data, manifests, and source bundles
- `workspaces/white-box/runs` — execution outputs and summaries

## Expected Layout

- `datasets/` — extracted datasets and split-ready image buckets
- `checkpoints/` — `GSA`-compatible training outputs (`checkpoint-*` directories)
- `manifests/` — provenance notes, split manifests, ownership notes
- `sources/` — raw archives or import bundles

These data files are local-only and git-ignored, except for this documentation.

## When to Use

Use this root when the material is:

- required by the white-box `GSA` method
- too large or too local to commit
- not an execution output

Don't use for:

- upstream code → `workspaces/white-box/external/GSA`
- smoke test outputs → `workspaces/white-box/runs`
- gray-box `PIA` data → `workspaces/gray-box/assets/pia`

## Current Status

This root is now legacy for production use.

Current active `GSA` data has moved to:

- `workspaces/white-box/assets/gsa-cifar10-1k-3shadow`

This older root is still useful as a record of the early CPU closed-loop path
and a local compatibility/debugging stash, but should no longer be treated as
the active data root for `catalog` or `contracts/best`.

For next steps, see [HANDOFF.md](HANDOFF.md).
