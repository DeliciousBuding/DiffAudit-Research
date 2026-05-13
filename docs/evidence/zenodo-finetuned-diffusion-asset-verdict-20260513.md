# Zenodo Fine-Tuned Diffusion Asset Verdict

> Date: 2026-05-13
> Status: archive-structured / manifest-incomplete / no download / no GPU release

## Taste Check

This is a Lane A clean-asset search verdict. The candidate is not LAION-mi live
URLs, CommonCanvas, MIDST, Beans, MNIST, Fashion-MNIST, or Kohaku/Danbooru.
The question is whether it can become a cleaner second membership asset without
downloading a large archive first.

## Candidate

| Field | Value |
| --- | --- |
| Record | Zenodo `10.5281/zenodo.13371475` |
| Title | `Black-box Membership Inference Attacks against Fine-tuned Diffusion Models` |
| License | `cc-by-4.0` |
| File | `extra_data-20240825T145405Z-001.zip` |
| Size | `736,366,195` bytes |
| Checksum | `md5:a52e197025c54c197b00674d398f2f6a` |

No full archive, model weights, dataset payloads, or responses were downloaded.
Only the Zenodo API metadata and ZIP central directory were inspected.

## ZIP Directory Evidence

The ZIP central directory has `21` entries. Relevant entries include:

| Path class | Examples |
| --- | --- |
| Target checkpoints | `extra_data/model_checkpoints/celeba_target/checkpoint-25000/pytorch_lora_weights.bin`, `optimizer.bin`, `scheduler.bin` |
| Partial target checkpoints | `extra_data/model_checkpoints/celeba_partial_target/checkpoint-25000/pytorch_lora_weights.bin` |
| Shadow checkpoints | `extra_data/model_checkpoints/celeba_shadow/checkpoint-25000/pytorch_lora_weights.bin` |
| Partial shadow checkpoints | `extra_data/model_checkpoints/celeba_partial_shadow/checkpoint-25000/pytorch_lora_weights.bin` |
| Dataset payloads | `extra_data/dataset/100-target/non_member/dataset.pkl`, `extra_data/dataset/partial-100-target/member/dataset.pkl`, `extra_data/dataset/partial-100-target/non_member/dataset.pkl`, `extra_data/dataset/100-shadow/non_member/dataset.pkl` |
| README | only `extra_data/blip_checkpoint/README.md`, not a top-level experiment manifest |

This structure is more promising than a model card with broad training-source
claims because it contains target/shadow checkpoint names and dataset payload
names. It is still not enough to release GPU or a full download.

## Gate Result

| Gate | Verdict |
| --- | --- |
| Target model identity | Partial pass: archive contains `celeba_target` and `celeba_partial_target` LoRA checkpoints, but the base diffusion model and training recipe are not available from the central directory alone. |
| Exact member/nonmember split | Fail: central directory does not expose a complete readable split manifest, and the expected `100-target/member/dataset.pkl` entry is not visible in the inspected directory. |
| Query/response coverage | Fail: no generated response package or query-response contract is visible from metadata. |
| Mechanism delta | Pass for intake: fine-tuned diffusion target/shadow LoRA setup is not one of the closed asset families. |
| Public-safe documentation | Pass: Zenodo metadata and CC-BY-4.0 license can be cited without local paths or secrets. |

## Decision

`archive-structured / manifest-incomplete / no download / no GPU release`.

This candidate should remain on Lane A watch, but it does not pass the
membership/query-response gates. The archive is large enough that a full
download is not justified until a public README, paper artifact, or small
manifest clarifies the target base model, exact member/nonmember payloads, and
query/response or scoring contract.

Smallest valid reopen condition:

- Find an upstream README, paper appendix, or code reference that explains the
  archive layout and proves exact target member/nonmember semantics; or
- Perform a deterministic partial ZIP member extraction only for a tiny manifest
  file if one is later discovered in the central directory.

Stop condition:

- Do not download the full `736 MB` archive or run LoRA-based scoring from this
  record until target identity and split semantics are manifest-backed.

## Reflection

This cycle tested asset portability rather than adding process around a weak
line. The result changes the queue: Zenodo fine-tuned diffusion is more
structured than broad-provenance assets, but it is not yet a GPU candidate.

## Platform and Runtime Impact

None. This is Research-only intake evidence and does not affect admitted rows,
Runtime schemas, or Platform product copy.
