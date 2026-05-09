# Black-Box Response-Contract Acquisition Audit

> Date: 2026-05-10
> Status: needs-assets; no GPU release

## Question

Do local `Download/` assets contain a second compatible black-box
response-strength or simple-distance contract with member/nonmember query
images, observable responses, controlled repeats, and a documented query budget?

## CPU Checks

### Variation Query Contract

```powershell
python -X utf8 scripts/audit_variation_query_contract.py `
  --query-root ..\Download\black-box\datasets\variation-query-set `
  --min-split-count 25
```

Result: `status = blocked`. The query root is missing, member and nonmember
query-image counts are both `0`, and no endpoint contract is configured.

### H2 Default Text-To-Image Contract

```powershell
python -X utf8 scripts/probe_h2_cross_asset_contract.py
```

Result: `status = blocked_protocol_mismatch`. SD1.5 and CelebA assets are
present, but the default text-to-image protocol does not provide query images,
controlled repeats, and observable response images for H2 response-strength.

### H2 Image-To-Image Eligibility Check

```powershell
python -X utf8 scripts/probe_h2_cross_asset_contract.py `
  --endpoint-mode image_to_image `
  --controlled-repeats `
  --response-images-observable
```

Result: `status = eligible_cpu_contract`. SD1.5, CelebA, and recon-derived
public splits are present, and image-to-image protocol fields are satisfiable.
This is still the same SD1.5/CelebA asset family already used by the existing
simple-distance evidence.

## Asset Review

| Candidate asset | Local state | Contract decision |
| --- | --- | --- |
| SD1.5 + CelebA image-to-image | Present and CPU-eligible. | Same asset family; not a second-asset acquisition. |
| Variation query set | Missing under `Download/black-box/datasets/variation-query-set`. | Blocked. |
| Kandinsky/Pokemon recon assets | Weights exist under recon supplementary assets, but no member/nonmember query-image split plus repeated-response endpoint contract is present. | Blocked for response-contract acquisition. |
| CLiD supplementary artifacts | Supplementary outputs exist, but they are not raw query images with controlled response images. | Not a response-contract candidate. |
| CIFAR/DDPM assets | Present for gray/white-box and ReDiffuse work. | Not a black-box second response contract. |

## Verdict

`needs-assets`.

No GPU task is released. The only currently executable image-to-image
response-contract path is the same SD1.5/CelebA family already used for the
bounded simple-distance packet. Running it again would not answer the
second-asset acquisition question.

## Reopen Gate

Reopen this lane only when at least one candidate supplies:

- documented dataset/model/source identity in `Download/`,
- member/nonmember query images or equivalent target identities,
- observable response images or equivalent tensors,
- controlled repeats or fixed stochastic response budget,
- same-cache comparator surface,
- low-FPR strict-tail reporting plan,
- adaptive boundary.

## Next Task

No GPU candidate is selected. The next highest-value CPU task is a targeted
asset-acquisition specification for the missing second response contract, or a
paper/asset scout for a black-box response surface that can satisfy the reopen
gate.

## Platform and Runtime Impact

No Platform or Runtime changes are needed.
