# Black-Box Response-Contract Package Preflight

> Date: 2026-05-10
> Status: needs-assets; no GPU release

## Question

Can the local Kandinsky/Pokemon assets instantiate a second black-box
response-contract package, instead of replaying the existing SD1.5/CelebA
image-to-image family?

## Candidate

`response-contract-pokemon-kandinsky-20260510`

This candidate is worth checking because local Kandinsky/Pokemon LoRA-style
assets exist under the recon supplementary asset area. If it had a member /
nonmember query split and observable response contract, it would be a different
model/data family from SD1.5/CelebA.

## CPU Preflight

Command shape:

```powershell
python -X utf8 scripts/probe_response_contract_package.py `
  --asset-id response-contract-pokemon-kandinsky-20260510 `
  --dataset-root <DIFFAUDIT_ROOT>\Download\black-box\datasets\response-contract-pokemon-kandinsky-20260510 `
  --supplementary-root <DIFFAUDIT_ROOT>\Download\black-box\supplementary\recon-assets\public-kandinsky-pokemon `
  --min-split-count 25
```

The preflight checks only package readiness. It does not call an endpoint and
does not run a model.

## Gate

A package must provide:

- `query/member/` and `query/nonmember/` with at least `25` query images each.
- `splits/member_ids.json` and `splits/nonmember_ids.json`.
- `manifest.json` with dataset/source/split provenance.
- `endpoint_contract.json` with supported endpoint mode and fixed repeat or
  seed policy.
- `response_manifest.json`.
- `responses/member/` and `responses/nonmember/` covering every query under
  the fixed repeat policy.

## Result

| Field | Value |
| --- | --- |
| Status | `needs_assets` |
| Supplementary root | present |
| Dataset/query root | missing |
| Member query images | `0 / 25` |
| Nonmember query images | `0 / 25` |
| Endpoint contract | missing |
| Response manifest | missing |
| Response files | missing |

## Verdict

`needs-assets`.

The Kandinsky/Pokemon assets are not currently a response-contract package.
They are useful as a candidate target family, but not sufficient to schedule a
GPU run. The result rules out treating the local LoRA-weight directory as a
second black-box response-contract by itself.

## Next Action

Build or acquire a real package under:

```text
Download/black-box/datasets/response-contract-pokemon-kandinsky-20260510/
Download/black-box/supplementary/response-contract-pokemon-kandinsky-20260510/
```

Do not release GPU until the CPU preflight returns `status=ready`.

## Platform and Runtime Impact

No Platform or Runtime changes are needed.
