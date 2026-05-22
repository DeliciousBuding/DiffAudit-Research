# CopyMark + laion_mi Public Binding Gate

> Date: 2026-05-17
> Status: blocked / public row-binding gap / no download beyond small metadata subset / no GPU release / no admitted row

## Question

Can the current public `CopyMark + laion_mi` surface be rebound to exact public
member identities strongly enough to become the next clean Lane A asset?

This cycle was opened because the collaborator-transferred Stable Diffusion
ReDiffuse bundle is useful candidate evidence but not a public immutable asset.
The next high-value question was whether an official public CopyMark branch
could clear the `public identity / exact split / row binding` gate without
requiring the full CopyMark Hugging Face zip, model folders, or GPU work.

## Why This Candidate

- CopyMark already has official public score artifacts, member/nonmember image
  logs, and explicit diffusion-MIA protocol context.
- `laion_mi` is the cleanest remaining public non-CommonCanvas CopyMark branch
  with both public parquet metadata and official member filename logs.
- A small bounded subset was enough to answer the row-binding question, so this
  lane could be audited without large downloads or rerunning an attack.

## Public Surface Used

The local bounded package is:
`<DIFFAUDIT_ROOT>/Download/black-box/supplementary/copymark-laion-mi-public-20260517/`.

Manifest:
`<DIFFAUDIT_ROOT>/Download/black-box/supplementary/copymark-laion-mi-public-20260517/manifest.json`

Bounded raw files:

| File | Role |
| --- | --- |
| `raw/members.parquet` | current public Hugging Face member metadata |
| `raw/nonmembers.parquet` | current public Hugging Face nonmember metadata |
| `raw/pia_laion_mi_image_log.json` | official committed CopyMark member/nonmember filename log |
| `raw/get_laion_mi_2_5k_member_img_caption.py` | official member-download utility |
| `raw/get_laion_mi_2_5k_nonmember_img_caption.py` | official nonmember-download utility |

The machine-readable probe result is:
`<DIFFAUDIT_ROOT>/Research/workspaces/black-box/artifacts/copymark-laion-mi-public-binding-gate-20260517.json`.

## Probe

New bounded CLI:

```powershell
python -m diffaudit probe-copymark-laion-mi-assets
```

Observed result:

| Check | Result |
| --- | --- |
| package root present | pass |
| public `members.parquet` present | pass |
| official `pia_laion_mi_image_log.json` present | pass |
| official member utility present | pass |
| public member schema has only `url/caption` | pass |
| official member utility uses hidden third parquet column | pass |
| member filenames fit within current public row range | fail |
| public row binding reconstructible from current public surface | fail |

Probe verdict:
`blocked`.

## Direct Proof

Current public member parquet:

| Field | Value |
| --- | --- |
| Columns | `['url', 'caption']` |
| Shape | `(13396, 2)` |
| Direct third-column access | `df.iloc[0, 2] -> IndexError: index 2 is out of bounds for axis 0 with size 2` |

This matters because the official member utility still indexes the current row
with `df.iloc[idx, 2]`, so the public parquet no longer exposes the identifier
that the official filename path expects.

Official member image log:

| Field | Value |
| --- | ---: |
| Logged member filenames | `2500` |
| Numeric member ids | `2500` |
| Minimum numeric id | `9617` |
| Maximum numeric id | `33905220` |
| Current public member row count | `13396` |

The numeric filename range is far larger than the current public parquet row
count, so the filenames cannot be interpreted as simple row indices into the
current public `members.parquet`.

## URL Spot-Check

The first ten public member URLs were checked live from the current
`members.parquet`.

| Outcome | Count |
| --- | ---: |
| HTTP `200` | `4` |
| Non-`200` / timeout | `6` |

Observed failures included `400`, `404`, `503`, and timeout. This is a
secondary blocker, not the main one: even if more URLs were still live, the
current public surface still lacks a public row-binding path from official
member filenames back to exact public parquet rows.

## Decision

`blocked / public row-binding gap / no download beyond small metadata subset /
no GPU release / no admitted row`.

The current public CopyMark `laion_mi` surface is useful support evidence, but
it does not unlock a clean Lane A asset:

- the public member parquet no longer exposes the identifier used by the
  official member utility;
- the official numeric member filenames do not map to current public row
  indices; and
- public URL rehydration is only partial even before any exact split proof.

Keep CopyMark in the mainline as support-only official evidence. Do not treat
this branch as a runnable second asset or a public replay packet.

Current slots remain:
`active_gpu_question = none`, `next_gpu_candidate = none`, and
`CPU sidecar = none selected after CopyMark laion_mi public binding gate`.

## Stop Condition

- Do not download the full CopyMark Hugging Face `datasets.zip`.
- Do not download image payloads, model folders, or Stable Diffusion weights
  from this branch.
- Do not try to rescue this lane with large URL scraping, GPU runs, or
  same-contract plumbing work.
- Reopen only if authors publish a compact row-binding manifest, restore the
  public identifier column, or release another public file that binds the
  current score artifacts back to exact public member rows.

## Platform and Runtime Impact

None. The admitted consumer bundle remains unchanged.
