# Black-Box Response-Contract Skeleton Create

> Date: 2026-05-11
> Status: local skeleton created; needs query split; no GPU release

## Question

After freezing the dry-run scaffold, can Research create the portable
Kandinsky/Pokemon response-contract template under `Download/` and make the
remaining blocker exact?

## Method

Create the package skeleton outside Git, then immediately run the CPU package
probe.

```powershell
python -X utf8 scripts/scaffold_response_contract_package.py `
  --asset-id response-contract-pokemon-kandinsky-20260511 `
  --download-root ../Download `
  --dataset-name pokemon `
  --model-identity kandinsky `
  --endpoint-mode image_to_image `
  --repeat-count 1 `
  --create `
  --output workspaces/black-box/artifacts/blackbox-response-contract-scaffold-create-20260511.json
```

```powershell
python -X utf8 scripts/probe_response_contract_package.py `
  --asset-id response-contract-pokemon-kandinsky-20260511 `
  --download-root ../Download `
  --output workspaces/black-box/artifacts/blackbox-response-contract-probe-after-skeleton-20260511.json
```

Tracked artifacts:

- `workspaces/black-box/artifacts/blackbox-response-contract-scaffold-create-20260511.json`
- `workspaces/black-box/artifacts/blackbox-response-contract-probe-after-skeleton-20260511.json`

Local non-Git package roots:

```text
Download/black-box/datasets/response-contract-pokemon-kandinsky-20260511/
Download/black-box/supplementary/response-contract-pokemon-kandinsky-20260511/
```

## Result

The scaffold helper created:

- `query/member/`
- `query/nonmember/`
- `splits/member_ids.json`
- `splits/nonmember_ids.json`
- `manifest.json`
- `responses/member/`
- `responses/nonmember/`
- `endpoint_contract.json`
- `response_manifest.json`

The follow-up probe returned:

| Field | Value |
| --- | --- |
| status | `needs_query_split` |
| member query count | `0` |
| nonmember query count | `0` |
| member response count | `0` |
| nonmember response count | `0` |
| endpoint mode | `image_to_image` |
| repeat count | `1` |
| dataset manifest JSON | valid |
| endpoint contract JSON | valid |
| response manifest JSON | valid |

Missing checks:

- `query_member_min_count`
- `query_nonmember_min_count`
- `response_member_count`
- `response_nonmember_count`

## Verdict

`needs_query_split`.

This is progress only at the asset-boundary level. It proves the portable
package shell and protocol templates are now present locally, but it does not
provide data or responses. No model run is released.

## Next Action

Fill the package with at least `25` member and `25` nonmember query images,
update split ids and manifest provenance, then capture one controlled
image-to-image response per query under the frozen endpoint contract. Only
after the probe returns `status = ready` can a tiny black-box scout be scoped.

## Platform and Runtime Impact

No Platform or Runtime schema change is needed. This is Research-side asset
preparation only.
