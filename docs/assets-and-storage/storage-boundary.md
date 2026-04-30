# Research Storage Boundary

This document answers one question:

Where should external code, datasets, weights, track assets, and run results go inside `Research`?

---

## Quick Reference

- `external/` holds **external code repos / local exploration clones**
- `third_party/` holds **minimal vendored code that the repo actually depends on**
- `<DIFFAUDIT_ROOT>/Download/` holds **raw downloads**
- `workspaces/<track>/assets/` holds **normalized verified asset entry points for each track**
- `workspaces/<track>/runs/` holds **experiment outputs and results**
- `outputs/` holds **local temporary outputs, not used as Git evidence**
- `<DIFFAUDIT_ROOT>/Archive/research-local-artifacts/` holds **locally generated large artifacts, moved out reversibly**
- `experiments/` commits only **sanitized summary / report**, not raw image/tensor outputs

Do not mix these roles.

---

## 1. `Research/external/`

What goes here:

- upstream paper code repo clones
- local exploratory mirrors
- external implementations not meant for direct commit to the main codebase

Examples:

- `external/PIA`
- `external/CLiD`
- `external/Reconstruction-based-Attack`
- `external/DiT`

What does NOT go here:

- your canonical run results
- the repo's own main code
- long-stashed raw dataset archives
- large unstructured checkpoint collections
- `downloads/` or similar raw-intake aggregation directories

Rules:

- `external/` is an "upstream code workspace", not a "data store"
- upstream implementations that can be pointed to via `--repo-root` should go here
- unless an upstream release is tightly coupled to a code directory, do not stash large datasets here long-term
- if you see `Research/external/downloads/`, that is boundary drift; move it back to `<DIFFAUDIT_ROOT>/Download/`

---

## 2. `Research/third_party/`

What goes here:

- minimal vendored subsets that the current repo code actually depends on

Example:

- `third_party/secmi/`

What does NOT go here:

- full upstream repos copied wholesale
- clones used only for temporary experiments
- datasets, weights, training results

Rules:

- only the minimum code subset that must be vendored for maintenance or integration belongs in `third_party/`
- this is long-term in-repo maintained code, not a temporary exploration area

---

## 3. `<DIFFAUDIT_ROOT>/Download/`

What goes here:

- raw downloaded datasets
- raw downloaded model weights
- zip / tar / supplementary releases
- author release mirrors
- checkpoints or paper attachments not yet normalized

Examples:

- `Download/shared/datasets/...`
- `Download/shared/weights/...`
- `Download/gray-box/weights/...`
- `Download/black-box/supplementary/...`
- `Download/white-box/supplementary/...`

Rules:

- `Download/` is the machine-local "raw intake layer"
- it stores things that are large, raw, replaceable, and re-downloadable
- do not use `Download/` as an experiment results layer
- do not write research conclusions in `Download/`

---

## 4. `Research/workspaces/<track>/assets/`

What goes here:

- normalized, repo-consumable verified asset entry points for a given track
- manifest files
- split metadata
- small contract files
- track-local normalized asset trees when needed

Examples:

- `workspaces/gray-box/assets/pia/manifest.json`
- `workspaces/white-box/assets/gsa/...`

Rules:

- this is the "assets the research repo currently claims and consumes"
- it can reference raw items in `Download/`, or hold small normalized results
- but do not copy all raw downloads here again

Simple decision:

- if the item is still a "raw download", put it in `Download/`
- if it has become a "stable contract entry point for the current track", put it in `workspaces/<track>/assets/`

---

## 5. `Research/workspaces/<track>/runs/`

What goes here:

- output from each experiment / evaluation / run
- `summary.json`
- exported scores / board / packet summaries
- machine-readable results for the current task

Rules:

- `runs/` holds results, not upstream code
- do not put raw datasets or large model repos in `runs/`
- each task should point to a canonical result anchor

Raw runtime queues, generated image folders, score tensor folders, and checkpoint
or split binaries are local artifacts. They should stay in ignored directories
or the external asset layer, while the repository keeps the sanitized
`summary.json`, result note, manifest, or report that describes the outcome.

## 6. `Research/outputs/`

What goes here:

- local training defaults
- temporary evaluation dumps
- generated checkpoints, weights, and training logs
- scratch rerun outputs

Rules:

- `outputs/` is ignored at the repository root.
- Do not use it as a canonical result anchor.
- Do not commit files from it just because a metric is useful.
- If a result should survive review, promote the metric into a workspace
  result note, a small `summary.json`, or a verified result table.

---

## 7. `<DIFFAUDIT_ROOT>/Archive/research-local-artifacts/`

What goes here:

- generated checkpoints
- bridged model directories
- large run payloads
- temporary cache directories that should not be part of the Research delivery surface
- preserved source copies when a canonical `Download/` target already exists

Rules:

- This is a reversible local quarantine, not a collaborator setup surface.
- The repository may keep a script that knows how to audit or move these
  artifacts, but it should not commit the artifacts themselves.
- If old local commands still need the historical path, use an ignored junction
  or symlink from `Research/` to the archived or downloaded asset.
- Do not write research results here. Results still belong in workspace
  summaries, evidence notes, or verified result tables.

Use:

```powershell
python -X utf8 scripts/audit_local_storage.py
python -X utf8 scripts/audit_local_storage.py --execute --json-out <DIFFAUDIT_ROOT>\Archive\research-local-artifacts\2026-04-30\manifest.json
```

The first command is dry-run. The second command only moves ignored local
assets that contain no Git-tracked files.

---

## 8. Current Repo Exceptions

### `SecMI`

- `external/SecMI/` = full upstream clone, used for upstream config / split / layout reference
- `third_party/secmi/` = minimal vendored surface actually used by DiffAudit integration

Both can coexist, but their roles must be explicitly distinguished. Do not casually say "SecMI is in external" or "SecMI is in third_party" without specifying which.

### `CLiD`

- `external/CLiD/` = local working clone / `--repo-root`
- `<DIFFAUDIT_ROOT>/Download/black-box/supplementary/clid-mia-supplementary/` = raw supplementary mirror

In practice:

- for local bridging or upstream code reading, go to `external/CLiD`
- for raw supplementary / `inter_output`, go to `Download`

### `recon-assets`

`recon-assets` has been moved out of `external/`. Its current canonical raw bundle location is:

- `<DIFFAUDIT_ROOT>/Download/black-box/supplementary/recon-assets/`

It is no longer part of the code clone layer.

## 9. Most Common Mistakes

### Case A: Putting datasets into `external/`

Convenient short-term, messy long-term.

Correct approach:

- raw downloads go to `<DIFFAUDIT_ROOT>/Download/` first
- the current track's actual consumption entry point is recorded in `workspaces/<track>/assets/` or a manifest pointing to the download

### Case B: Writing run results back into `Download/`

Wrong.

`Download/` stores raw intake only, not research conclusions.

### Case C: Mixing repo-dependent code with exploration clones

Correct separation:

- code the repo actually depends on and must maintain together -> `third_party/`
- full upstream repos, local exploratory clones -> `external/`

### Case D: Committing a small JSON directly from `outputs/`

This mixes the generation layer and the evidence layer again.

Correct approach:

- raw run outputs stay in the ignored `outputs/` directory
- durable metrics go into the corresponding workspace result note or `summary.json`
- `git status` should show curated evidence, not training directory fragments

---

## 10. Recommended Discipline Going Forward

1. New external code repo:
   - put it in `external/` first
2. New raw dataset / weights / attachments:
   - put them in `<DIFFAUDIT_ROOT>/Download/` first
3. A track needs to turn raw material into a stable consumption entry point:
   - create a manifest or normalized entry in `workspaces/<track>/assets/`
4. Actual execution evidence:
   - write only to `workspaces/<track>/runs/`
5. Only when "the current repo code must directly import / patch it long-term":
   - put the minimum necessary code in `third_party/`

---

## 11. Summary

If you ask "where do external code and datasets go":

- external code defaults to `Research/external/`
- raw datasets and raw weights default to `<DIFFAUDIT_ROOT>/Download/`
- the current research mainline's actual track entry points go in `Research/workspaces/<track>/assets/`
- run results go in `Research/workspaces/<track>/runs/`
- temporary training outputs go in the ignored `Research/outputs/`
- locally generated large artifacts can be moved to `<DIFFAUDIT_ROOT>/Archive/research-local-artifacts/`
- only minimal vendored dependencies go in `Research/third_party/`

Directory naming conventions are in [download-naming-policy.md](download-naming-policy.md).
