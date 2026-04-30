# External Code Clones

`external/` 只放上游代码仓或本地 exploratory clone。

不要把原始数据集、原始权重、补充附件长期堆在这里。

## Expected Clone Map

- `CLiD/`
  - local working clone for upstream CLiD code when needed
  - raw CLiD supplementary mirror lives under `<DIFFAUDIT_ROOT>/Download/black-box/supplementary/clid-mia-supplementary/`
- `SecMI/`
  - optional full upstream clone for upstream config / split / structure reference
  - canonical in-repo minimal integration surface is `<DIFFAUDIT_ROOT>/Research/third_party/secmi/`
- `PIA/`, `Reconstruction-based-Attack/`, `GSA/`, `DiT/`, `DPDM/`, `mia-diffusion/`
  - optional upstream or exploratory code clones

These directories are intentionally not committed and may be absent on a clean
machine. Recreate them with the shallow clone commands in
`docs/assets-and-storage/data-and-assets-handoff.md`.

## Not For

- raw downloaded asset bundles
- lane-normalized admitted assets
- run evidence

Use:

- `<DIFFAUDIT_ROOT>/Download/` for raw intake
- `<DIFFAUDIT_ROOT>/Research/workspaces/<lane>/assets/` for lane-normalized gateways
- `<DIFFAUDIT_ROOT>/Research/workspaces/<lane>/runs/` for evidence
