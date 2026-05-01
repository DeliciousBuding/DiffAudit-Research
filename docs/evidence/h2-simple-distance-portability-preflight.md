# H2 Simple-Distance Portability Preflight

This note records the CPU-only preflight after the simple image-to-image
response-distance signal passed its 25/25 single-asset packet.

## Verdict

```text
blocked for second-asset portability; no GPU task selected
```

The current local assets do not provide a clean second image-to-image or
repeated-response contract for the simple-distance signal. The SD1.5/CelebA
contract remains executable, but it is the same asset family that produced the
current evidence. Running it again would not answer portability.

## Preflight Findings

| Candidate | Local state | Decision |
| --- | --- | --- |
| SD1.5/CelebA image-to-image | Assets and protocol are ready; CPU probe returns `eligible_cpu_contract` with controlled repeats and observable response images. | Same asset family; not a second-asset portability test. |
| Kandinsky/Pokemon | Local `public-kandinsky-pokemon` LoRA weights exist, and prior recon smoke evidence exists. No member/nonmember query-image split with a stable returned-image repeated-response contract is present. | Blocked for simple-distance portability. |
| CLiD supplementary COCO/Flickr/Pokemon score files | Supplementary score outputs exist, but they are not raw query images plus a controlled response-image endpoint. | Useful for CLiD/recon context, not this simple-distance contract. |
| Variation API line | Still lacks a real query-image set and endpoint contract. | Needs data/endpoint before use. |

## Probe Evidence

The existing CPU probe confirms that the current SD1.5/CelebA image-to-image
surface is protocol-compatible:

```powershell
python -X utf8 scripts/probe_h2_cross_asset_contract.py `
  --endpoint-mode image_to_image `
  --controlled-repeats `
  --response-images-observable `
  --output workspaces/black-box/runs/h2-portability-preflight-20260501-r1/sd15-celeba-img2img-probe.json
```

Result summary:

| Field | Value |
| --- | --- |
| Status | `eligible_cpu_contract` |
| Asset ready | `true` |
| Protocol ready | `true` |
| Endpoint mode | `image_to_image` |
| Limitation | same SD1.5/CelebA asset family as the admitted simple-distance packets |

The generated JSON is an ignored local run artifact. This note is the canonical
Git evidence anchor.

## Decision

- Do not schedule another same-asset simple-distance GPU packet.
- Do not claim portability from the SD1.5/CelebA packet.
- Keep simple-distance as bounded single-asset black-box evidence.
- Return the next active slot to `recon` product-consumable strengthening unless
  a real second asset appears.

## Reopen Gate

A second-asset simple-distance contract can reopen only when all fields are
available:

| Required field | Meaning |
| --- | --- |
| Member/nonmember query images | A documented split with at least 25/25 images for scout scale and a path to 100/100. |
| Response endpoint | Image-to-image or equivalent repeated-response surface, not prompt-only text-to-image. |
| Controlled repeats | Fixed seeds or repeated stochastic samples under a documented query budget. |
| Observable responses | Generated images or equivalent response tensors available for distance scoring. |
| Asset family boundary | Clearly not the same SD1.5/CelebA/recon-derived packet family. |
| Low-FPR gate | Predeclared zero-FP empirical tail reporting with no sub-percent calibration overclaim. |

Until those fields exist, the honest next research move is recon product-row
hardening or another non-H2 black-box lane, not another same-asset H2 run.
