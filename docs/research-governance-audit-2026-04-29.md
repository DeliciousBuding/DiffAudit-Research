# Research Governance Audit - 2026-04-29

This is the read-only audit captured before the cleanup edits on
`research-governance-cleanup-20260429`. It records the repo state that motivated
the governance pass.

## Branch And Worktree

- starting branch: `main`
- cleanup branch: `research-governance-cleanup-20260429`
- active GPU question at freeze: `none`
- next GPU candidate at freeze: `none`
- history rewrite performed: no

## Hot-Path Size

| File | Observation |
| --- | --- |
| `ROADMAP.md` | About `442 KB`; acting as roadmap plus long execution log. |
| `workspaces/implementation/challenger-queue.md` | Acting as queue plus X-141 to X-180 decision timeline. |
| `docs/comprehensive-progress.md` | Still useful as detailed handoff, but not the public front door. |

Decision: preserve the long roadmap as
`legacy/execution-log/2026-04-29/continuous-autonomous-mainline-archive.md` and
replace `ROADMAP.md` with a short steering file.

## Workspace Disk Footprint

| Workspace | Approx size |
| --- | ---: |
| `workspaces/white-box` | `59.20 GB` |
| `workspaces/black-box` | `4.84 GB` |
| `workspaces/gray-box` | `4.46 GB` |
| `workspaces/defense` | `2.97 GB` |
| `workspaces/implementation` | `0.85 GB` |
| `workspaces/cross-box` | `<0.01 GB` |
| `workspaces/intake` | `<0.01 GB` |
| `workspaces/runtime` | `<0.01 GB` |

Largest local workspace artifacts observed:

| Approx size | Path |
| ---: | --- |
| `3278.89 MB` | `workspaces/black-box/runs/clid-recon-asset-bridge-probe-20260415-r1/bridged-model/unet/diffusion_pytorch_model.safetensors` |
| `1322.81 MB` | `workspaces/gray-box/assets/pia/sources/OneDrive_1_2026-4-7.zip` |
| `1095.34 MB` | `workspaces/gray-box/assets/secmi/sources/OneDrive_1_2026-4-15.zip` |
| `867.62 MB` | multiple `workspaces/white-box/.../optimizer.bin` checkpoint optimizer states |

Decision: do not move these large local artifacts in this PR. They are ignored
or should remain local; the PR strengthens ignore rules and documents that raw
assets belong in `<DIFFAUDIT_ROOT>/Download/`.

## Tracked Large Files

No Git-tracked file at or above `1 MB` was found during the audit.

Tracked files above `100 KB` are mostly curated paper-report figures and one
oversized hot-path doc:

| Size | Path family |
| ---: | --- |
| `729.50 KB` | `docs/paper-reports/assets/white-box/...png` |
| `684.50 KB` | `docs/paper-reports/assets/black-box/...png` |
| `564.20 KB` | `docs/paper-reports/assets/black-box/...jpeg/png` |
| `502.30 KB` | `docs/paper-reports/assets/gray-box/...png` |
| `442.00 KB` | old `ROADMAP.md` before archive |
| `360.30 KB` | `workspaces/intake/2026-04-12-smp-lora-gpu-expansion-program.md` |

Decision: paper-report figures are tolerated as curated report assets for now.
The old `ROADMAP.md` is archived out of the startup path.

## Generated Or Binary Artifacts Removed From Current Branch

| Path | Action | Reason |
| --- | --- | --- |
| `experiments/_tmp_kandinsky_repro/image_01_01.jpg` | removed from current tree | Temporary generated experiment image; reproducible/generated outputs should not be committed. |
| `tools/gsa_next_run/examples/minimal/assets_root/data.bin` | removed from current tree | Tiny binary fixture was not needed for the example contract; text fixture remains. |

## X-Run Script Audit

Top-level `scripts/run_x*.py` before cleanup:

| Class | Scripts |
| --- | --- |
| Keep as replay helpers | `run_x90_larger_surface_triscore.py`, `run_x90_tmiadm512_assets.py` |
| Archive as closed one-off X-run scripts | `run_x145_*`, `run_x148_*`, `run_x150_*`, `run_x154_*`, `run_x157_*`, `run_x158_*`, `run_x159_*`, `run_x161_*`, `run_x162_*`, `run_x163_*`, `run_x165_*`, `run_x168_*`, `run_x170_*`, `run_x171_*`, `run_x172_*`, `run_x175_*` |

Decision: keep the X-90 helpers because they are reusable replay/build helpers
for the G1-A / X-90 internal auxiliary evidence. Move closed one-off scripts to
`legacy/execution-log/2026-04-29/scripts/`.

## Untracked Governance Inputs

The worktree contained untracked X-141 to X-180 decision anchors plus untracked
X-run scripts and two X-specific tests. Decision: preserve them under
`legacy/execution-log/2026-04-29/` instead of deleting them or leaving them in
hot-path directories.

## Immediate Cleanup Verdict

`positive governance cleanup candidate`: the repo does not currently track
large model/data files above `1 MB`, but it did have a large roadmap-as-log,
one-off scripts in `scripts/`, local generated artifacts already in history,
and a large ignored workspace footprint. Stage 1 should fix current-branch
hygiene and produce a separate history rewrite audit. It should not force-push.
