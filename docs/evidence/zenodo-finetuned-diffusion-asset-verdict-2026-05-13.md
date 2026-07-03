# Zenodo Fine-Tuned Diffusion Asset Verdict

> Date: 2026-05-13
> Updated: 2026-06-08
> Status: archive-verified / manifest-incomplete / no GPU release

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

The 2026-05-13 check inspected only Zenodo API metadata and the ZIP central
directory. The 2026-06-08 bounded follow-up downloaded the full archive under
`Download/shared/supplementary/ndss-2025-324-blackbox-mia-20260608/`, verified
the Zenodo MD5 `a52e197025c54c197b00674d398f2f6a`, recorded local SHA-256
`ADB63E025238347BF219A001DAD32BBCC92312CA5BE86CCA0A70F1AF0D2D7098`, and passed
`zipfile.testzip()`.

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
names. It is still not enough to release scoring, admission, or GPU work.

## Gate Result

| Gate | Verdict |
| --- | --- |
| Target model identity | Partial pass: archive contains `celeba_target` and `celeba_partial_target` LoRA checkpoints, but the base diffusion model and training recipe are not available from the central directory alone. |
| Exact member/nonmember split | Fail: central directory does not expose a complete readable split manifest, and the expected `100-target/member/dataset.pkl` entry is not visible in the inspected directory. |
| Query/response coverage | Fail: no generated response package or query-response contract is visible from metadata. |
| Mechanism delta | Pass for intake: fine-tuned diffusion target/shadow LoRA setup is not one of the closed asset families. |
| Public-safe documentation | Pass: Zenodo metadata and CC-BY-4.0 license can be cited without local paths or secrets. |

## 2026-06-08 Full-ZIP Follow-Up

The full-ZIP probe changed the storage fact but not the evidence decision.
Static inspection of the nested torch `dataset.pkl` payloads found only
dataset-level `image` and `text` fields plus PIL image construction globals. It
did not find `id`, `file_name`, or `image_id` fields. The source repository
loads these payloads with `torch.load(...)` and generates reconstruction
distance scores as separate outputs, but those score outputs are not included in
the Zenodo archive.

The public split surface also remains paper-semantics incomplete. The visible
payloads include `partial-100-target/member`, `partial-100-target/non_member`,
`100-target/non_member`, and `100-shadow/non_member`; there is no compact
manifest proving a clean target/shadow member/nonmember four-way split. Local
derived recon assets may use `100-target/non_member` as a `shadow_member_proxy`,
but that is not a paper-faithful split declaration.

## Decision

`archive-verified / manifest-incomplete / no GPU release`.

This candidate should remain on Lane A watch, but it does not pass the
membership/query-response gates. The full download did not supply the missing
row-bound manifest, complete split semantics, score-vector packet, ROC/metric
artifact, or no-training verifier.

Smallest valid reopen condition:

- Find an upstream README, paper appendix, issue, repository file, or small
  manifest that proves exact row identities and paper-faithful target/shadow
  member/nonmember semantics; or
- Find the missing score-vector/metric packet described by the paper appendix.

Stop condition:

- Do not run LoRA-based scoring or GPU work from this record until target
  identity, split semantics, row IDs, score/response packet, metric recompute,
  and label-shuffle control are manifest-backed.

## Reflection

The 2026-06-08 follow-up tested whether the complete public ZIP changes the
gate. It does not: Zenodo fine-tuned diffusion is more structured than
broad-provenance assets, but it is still not a GPU candidate.

## Platform and Runtime Impact

None. This is Research-only intake evidence and does not affect admitted rows,
Runtime schemas, or Platform product copy.
