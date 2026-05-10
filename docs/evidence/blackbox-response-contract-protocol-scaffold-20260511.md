# Black-Box Response-Contract Protocol Scaffold

> Date: 2026-05-11
> Status: CPU-only scaffold dry-run; needs-assets; no GPU release

## Question

Can the black-box response-contract lane advance without pretending missing
assets are present?

## Method

Run the scaffold helper in dry-run mode for the next concrete candidate package
identity. This does not write raw assets, but it freezes the expected portable
layout and handoff target.

```powershell
python -X utf8 scripts/scaffold_response_contract_package.py `
  --asset-id response-contract-pokemon-kandinsky-20260511 `
  --download-root ..\Download `
  --dataset-name pokemon `
  --model-identity kandinsky `
  --endpoint-mode image_to_image `
  --repeat-count 1 `
  --output workspaces\black-box\artifacts\blackbox-response-contract-scaffold-dryrun-20260511.json
```

Artifact:
`workspaces/black-box/artifacts/blackbox-response-contract-scaffold-dryrun-20260511.json`.

## Result

The scaffold dry-run succeeded and reports the required package roots:

```text
Download/black-box/datasets/response-contract-pokemon-kandinsky-20260511/
Download/black-box/supplementary/response-contract-pokemon-kandinsky-20260511/
```

The required query and response subtrees are:

- `query/member/`
- `query/nonmember/`
- `splits/member_ids.json`
- `splits/nonmember_ids.json`
- `manifest.json`
- `responses/member/`
- `responses/nonmember/`
- `endpoint_contract.json`
- `response_manifest.json`

No files were created under `Download/` because this was a dry-run.

## Verdict

`needs-assets`.

This is useful because it converts the black-box lane from an abstract
"acquire assets" blocker into a precise package contract. It still does not
release a model run. The next useful work is to create or acquire real query
images, split ids, endpoint provenance, responses, and integrity hashes for
this package, then rerun the package probe.

## Next Gate

After real package contents exist, run:

```powershell
python -X utf8 scripts/probe_response_contract_package.py `
  --asset-id response-contract-pokemon-kandinsky-20260511 `
  --download-root ..\Download `
  --output workspaces\black-box\artifacts\blackbox-response-contract-probe-20260511.json
```

Only a `status = ready` probe may reopen a tiny black-box packet. Until then:

- active GPU question: none,
- next GPU candidate: none,
- CPU sidecar: package construction or external acquisition against this
  scaffold.

## Platform and Runtime Impact

No Platform or Runtime schema change is needed. This is a Research asset
handoff and package-readiness artifact only.
