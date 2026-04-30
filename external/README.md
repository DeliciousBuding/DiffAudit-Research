# External Code Clones

`external/` contains upstream code repositories or local exploratory clones.

Don't store raw datasets, model weights, or supplementary files here long-term.

## Expected Clone Map

- `CLiD/` — local clone of upstream CLiD code when needed
  - raw CLiD supplementary files live under `<DIFFAUDIT_ROOT>/Download/black-box/supplementary/clid-mia-supplementary/`
- `SecMI/` — optional full upstream clone for config/split/structure reference
  - canonical in-repo minimal integration is `<DIFFAUDIT_ROOT>/Research/third_party/secmi/`
- `PIA/`, `Reconstruction-based-Attack/`, `GSA/`, `DiT/`, `DPDM/`, `mia-diffusion/`
  - optional upstream or exploratory code clones

These directories are git-ignored and may be absent on a clean machine. Recreate
them with the shallow clone commands in
`docs/assets-and-storage/data-and-assets-handoff.md`.

## Don't Store Here

- Raw downloaded data
- Processed data for specific tracks
- Experiment results

Use instead:

- `<DIFFAUDIT_ROOT>/Download/` for raw data intake
- `<DIFFAUDIT_ROOT>/Research/workspaces/<direction>/assets/` for processed data
- `<DIFFAUDIT_ROOT>/Research/workspaces/<direction>/runs/` for experiment results
