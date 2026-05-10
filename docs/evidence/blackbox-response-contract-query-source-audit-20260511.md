# Black-Box Response-Contract Query-Source Audit

> Date: 2026-05-11
> Status: needs-assets; no GPU release

## Question

Can the local `Download/` tree fill the
`response-contract-pokemon-kandinsky-20260511` skeleton with real
member/nonmember query images or response files without acquiring new assets?

## Method

Inspect the current local asset roots for reusable image or response sources:

```powershell
Get-ChildItem ../Download/black-box/supplementary/recon-assets -Recurse -File |
  Group-Object Extension
```

```powershell
$roots = @("../Download/black-box", "../Download/shared")
foreach ($root in $roots) {
  Get-ChildItem $root -Recurse -File |
    Where-Object { $_.FullName -match 'pokemon|kandinsky|celeba|member|non_member|nonmember|query|response' }
}
```

The audit is CPU-only and does not modify assets.

## Findings

| Root | Finding | Can fill skeleton? |
| --- | --- | --- |
| `../Download/black-box/supplementary/recon-assets/public-kandinsky-pokemon/` | Contains LoRA/weight files and Hugging Face cache metadata only: `.safetensors`, `.metadata`, `.gitignore`, and `CACHEDIR.TAG`. No query images and no responses. | no |
| `../Download/black-box/supplementary/recon-assets/.../source-datasets/` | Contains recon protocol `dataset.pkl` files under CelebA target/shadow source datasets. | no; different protocol and not a Pokemon/Kandinsky response-contract package |
| `../Download/black-box/supplementary/recon-assets/.../derived-public-*` | Contains derived `.pt` tensors used by the admitted recon path. | no; tensor summaries are not query images or response files |
| `../Download/shared/datasets/celeba/` | Contains CelebA archives and annotations. | no for the current Pokemon/Kandinsky package; using it would require a new asset identity and response-capture contract |
| `../Download/black-box/datasets/response-contract-pokemon-kandinsky-20260511/` | Skeleton manifests and empty split files exist. | not ready |
| `../Download/black-box/supplementary/response-contract-pokemon-kandinsky-20260511/` | Endpoint and response manifest templates exist; response folders are empty. | not ready |

## Verdict

`needs-assets`.

The local tree cannot fill the current Pokemon/Kandinsky response-contract
skeleton. The only Pokemon/Kandinsky-local material is model-side LoRA/weight
state, not member/nonmember query images or endpoint responses. Existing CelebA
and recon artifacts are useful for other lanes, but copying them into this
package would mix asset identities and create misleading evidence.

## Next Action

Acquire or build a real Pokemon query split:

- at least `25` member query images,
- at least `25` nonmember query images,
- split ids and provenance in `manifest.json`,
- one controlled image-to-image response per query under the frozen
  Kandinsky endpoint contract,
- integrity hashes in `manifest.json` and `response_manifest.json`.

After those assets exist, rerun:

```powershell
python -X utf8 scripts/probe_response_contract_package.py `
  --asset-id response-contract-pokemon-kandinsky-20260511 `
  --download-root ../Download `
  --output workspaces/black-box/artifacts/blackbox-response-contract-probe-after-query-source-20260511.json
```

Do not release GPU until that probe returns `status = ready`.

## Platform and Runtime Impact

No Platform or Runtime schema change is needed. This is an asset-readiness
audit only.
