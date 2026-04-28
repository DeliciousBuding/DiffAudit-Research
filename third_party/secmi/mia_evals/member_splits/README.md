# SecMI Member Splits

The original SecMI split `.npz` files are data artifacts, not vendored source.
They are intentionally not committed to this repository.

Use one of these locations instead:

- Full upstream clone: `external/SecMI/mia_evals/member_splits/`
- Team asset mirror: `<DIFFAUDIT_ROOT>/Download/gray-box/supplementary/secmi-member-splits/`

When running SecMI probes, pass the local split directory explicitly:

```powershell
python -m diffaudit probe-secmi-assets --config configs/attacks/secmi_plan.yaml --member-split-root <path-to-member-splits>
```
