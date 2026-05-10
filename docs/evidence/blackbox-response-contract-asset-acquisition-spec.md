# Black-Box Response-Contract Asset Acquisition Spec

> Date: 2026-05-10
> Status: needs-assets; no GPU release

## Purpose

This spec defines the minimum asset package required to reopen black-box
response-strength, simple-distance, or variation-style execution on a second
asset family.

The preceding local audit found one CPU-eligible image-to-image path
(`SD1.5/CelebA`) and no second compatible response contract. Re-running the
same family would not test portability.

## Required Package

A valid package must live under `<DIFFAUDIT_ROOT>/Download/black-box/` and use
a stable asset id, for example `response-contract-<dataset>-<model>-YYYYMMDD`.

```text
Download/black-box/
  datasets/<asset-id>/
    query/member/
    query/nonmember/
    splits/member_ids.json
    splits/nonmember_ids.json
    manifest.json
  supplementary/<asset-id>/
    responses/member/
    responses/nonmember/
    endpoint_contract.json
    response_manifest.json
```

`manifest.json` must include:

- dataset name, source, license boundary, and acquisition date,
- model or endpoint identity,
- split construction rule and random seed if applicable,
- member and nonmember query counts,
- query budget, repeat count, and stochastic controls,
- response observability type: image, latent, logits, score, or equivalent
  tensor,
- hash list or equivalent integrity check for query and response files.

## Minimum Acceptance Gate

The smallest useful scout package is:

- at least `25` member query identities and `25` nonmember query identities,
- response files or endpoint replay contract for every query identity,
- fixed repeat count or fixed stochastic seed policy,
- one same-cache comparator surface that both member and nonmember queries use,
- a documented path to `100/100` before any admission-level claim,
- strict-tail reporting fields for `AUC`, `ASR`, `TPR@1%FPR`, and
  `TPR@0.1%FPR`,
- an adaptive boundary describing what a repeated-query attacker can vary and
  what remains fixed.

No GPU packet is released until a CPU preflight proves this gate is satisfied.

## Preferred Acquisition Targets

| Priority | Target | Why | Required proof |
| --- | --- | --- | --- |
| 1 | New image-to-image family | Closest comparator to the existing SD1.5/CelebA simple-distance signal while testing portability. | Different dataset or model family, query images, response images, fixed repeats. |
| 2 | Repeated-response API package | Can support response-strength without local model weights. | Endpoint identity, replayable responses, query budget, repeat policy. |
| 3 | Variation query set | Reopens the variation lane without assuming a local generator. | Member/nonmember query folders plus endpoint contract. |

Text-to-image prompt-only assets are insufficient unless they also provide
query-image identity, observable responses, and controlled repeats.

## CPU Preflight Contract

After a candidate package lands, run from the `Research/` repository root:

```powershell
python -X utf8 scripts/audit_variation_query_contract.py `
  --query-root ../Download/black-box/datasets/<asset-id>/query `
  --min-split-count 25
```

If the package is image-to-image compatible, also run:

```powershell
python -X utf8 scripts/probe_h2_cross_asset_contract.py `
  --download-root ../Download `
  --endpoint-mode image_to_image `
  --controlled-repeats `
  --response-images-observable
```

The current H2 probe validates the built-in SD1.5/CelebA contract shape. A new
second asset must add or configure an equivalent CPU probe before the first
GPU-eligible verdict. Both the dataset/query split and the response or endpoint
contract must pass CPU validation.

To avoid hand-built partial packages, first dry-run the scaffold:

```powershell
python -X utf8 scripts/scaffold_response_contract_package.py `
  --asset-id response-contract-<dataset>-<model>-YYYYMMDD `
  --download-root ../Download `
  --dataset-name <dataset> `
  --model-identity <model-or-endpoint> `
  --endpoint-mode image_to_image `
  --repeat-count <fixed-repeat-count>
```

Only add `--create` after the package identity and repeat policy are final.
The scaffold writes empty templates only; it does not satisfy the query,
response, provenance, or integrity requirements by itself.

To scan all current candidates:

```powershell
python -X utf8 scripts/discover_response_contract_packages.py `
  --download-root ../Download `
  --include-asset-id response-contract-<dataset>-<model>-YYYYMMDD
```

## Verdict

`needs-assets`.

This spec completes the CPU-only acquisition definition, but does not reopen a
model run. The next actionable item is external acquisition or construction of
one package matching the gate above.

## Platform and Runtime Impact

No Platform or Runtime schema change is needed. A future packet may require a
product-bridge note only if it becomes admitted or changes exported evidence
fields.
