# Black-Box Response-Contract Discovery

> Date: 2026-05-10
> Status: needs-assets; no GPU release

## Question

Do the current `Download/black-box/datasets/` and
`Download/black-box/supplementary/` roots contain any paired second
response-contract package that passes the CPU package gate?

## Method

This review adds a repository-level discovery check on top of the existing
single-package preflight. It scans the two portable black-box package roots,
unions dataset ids, supplementary ids, and explicitly requested ids, then runs
the same CPU gate for every candidate.

Command:

```powershell
python -X utf8 scripts/discover_response_contract_packages.py `
  --download-root ..\Download `
  --include-asset-id response-contract-pokemon-kandinsky-20260510
```

The command is expected to return nonzero unless at least one package is ready.
That is a readiness signal, not a test failure.

For controlled intake, the package skeleton can be planned without writing
files:

```powershell
python -X utf8 scripts/scaffold_response_contract_package.py `
  --asset-id response-contract-pokemon-kandinsky-20260510 `
  --download-root ..\Download `
  --dataset-name pokemon `
  --model-identity kandinsky `
  --repeat-count 1
```

This dry-run reports the directories and template manifests that would be
created. It does not claim package readiness and does not create data.

## Result

| Field | Value |
| --- | --- |
| Discovery status | `needs_assets` |
| Dataset package ids | `0` |
| Supplementary package ids | `2` |
| Candidate ids inspected | `3` |
| Ready asset ids | none |
| Supplementary-only ids | `clid-mia-supplementary`, `recon-assets` |
| Explicit missing id | `response-contract-pokemon-kandinsky-20260510` |

All inspected candidates returned `needs_assets`.

## Interpretation

The current local black-box asset root has legacy or supporting supplementary
directories, but it does not have a paired package in the response-contract
shape:

- no `Download/black-box/datasets/<asset-id>/query/member/` package exists,
- no paired `query/nonmember/` package exists,
- no split metadata exists for a second response-contract candidate,
- no paired endpoint contract and response manifest exists,
- no response files cover a fixed member/nonmember query budget.

This strengthens the previous `needs-assets` verdict because the check is now
systematic across the package roots instead of only hand-checking one named
candidate.

## Verdict

`needs-assets`.

No GPU task is released. The next useful step is asset construction or external
acquisition, not another model run. A future package should be created under:

```text
Download/black-box/datasets/response-contract-<dataset>-<model>-YYYYMMDD/
Download/black-box/supplementary/response-contract-<dataset>-<model>-YYYYMMDD/
```

It must then pass:

```powershell
python -X utf8 scripts/probe_response_contract_package.py `
  --asset-id response-contract-<dataset>-<model>-YYYYMMDD `
  --download-root ..\Download
```

If using the scaffold helper, only run it with `--create` after the asset id,
dataset identity, model identity, endpoint mode, and repeat policy are chosen.
The created templates still require real query files, real split ids, response
files, provenance, and integrity metadata before the package can pass preflight.

## Platform and Runtime Impact

No Platform or Runtime change is needed. This is Research-side package hygiene
and acquisition gating only.
