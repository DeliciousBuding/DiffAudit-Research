# CopyMark CommonCanvas Query Asset

> Date: 2026-05-12
> Status: query split ready / needs responses / no GPU release

## Question

Can the CopyMark/CommonCanvas direction move from provenance intake to an actual
local second-benchmark asset without downloading the full dataset or starting a
model run?

## Taste Check

This is real asset acquisition, not another validator. The action creates a
small fixed query split that can support the next decision: whether it is worth
generating responses and running one simple CPU scorer.

It deliberately stops before responses and GPU. A query-only package is not
ready evidence.

## Local Asset

Asset id:

```text
response-contract-copymark-commoncanvas-20260512
```

Local non-Git package roots:

```text
<DIFFAUDIT_ROOT>/Download/black-box/datasets/response-contract-copymark-commoncanvas-20260512/
<DIFFAUDIT_ROOT>/Download/black-box/supplementary/response-contract-copymark-commoncanvas-20260512/
```

The tiny split was extracted from the Hugging Face `chumengl/copymark`
`datasets.zip` by HTTP range reads. The full archive was not downloaded.

Selection:

- member queries: first `25` lexicographic images from
  `commoncatalog-2-5k-eval` and first `25` from `commoncatalog-2-5k-test`.
- nonmember queries: first `25` lexicographic images from
  `coco2017-val-2-5k-eval` and first `25` from `coco2017-val-2-5k-test`.
- total query count: `50` member and `50` nonmember.

Manifest status:

- `manifest.json` exists and records source zip size, etag, source paths,
  captions, dimensions, byte sizes, and SHA-256 hashes.
- `splits/member_ids.json` and `splits/nonmember_ids.json` exist.
- `endpoint_contract.json` and `response_manifest.json` exist as protocol
  placeholders.
- no responses have been generated or attached.

## Probe

Command:

```powershell
python -X utf8 scripts/probe_response_contract_package.py `
  --asset-id response-contract-copymark-commoncanvas-20260512 `
  --download-root ../Download `
  --min-split-count 25 `
  --output workspaces/black-box/artifacts/copymark-commoncanvas-response-contract-probe-20260512.json
```

Result:

- status: `needs_responses`
- member query count: `50`
- nonmember query count: `50`
- missing checks: `response_member_count`, `response_nonmember_count`

Artifact:

[workspaces/black-box/artifacts/copymark-commoncanvas-response-contract-probe-20260512.json](../../workspaces/black-box/artifacts/copymark-commoncanvas-response-contract-probe-20260512.json)

## Verdict

`query split ready / needs responses / no GPU release`.

This advances the second-asset mainline: there is now a concrete local
CommonCanvas/CommonCatalog query split with real files and hash provenance.
It still does not answer transferability because no target responses exist.

Next smallest useful action:

1. Generate or attach deterministic CommonCanvas responses for the `100` fixed
   queries under the endpoint contract.
2. Re-run the package probe and require `status = ready`.
3. Only then run one simple CPU scorer. Do not start with fusion or broad
   ablations.

Stop condition:

- If deterministic CommonCanvas response generation is infeasible locally or
  response semantics cannot be made reproducible, mark this package
  `query-only / blocked` and do not build a scorer around it.

## Platform and Runtime Impact

None. This is Research-side asset preparation only. It does not change admitted
Platform or Runtime rows.
