# Reconstruction-Based Attack Artifact Gate

Date: 2026-05-15

## Verdict

`checkpoint-and-dataset-public / incomplete score-input split / response-score artifacts missing / no full download / no GPU release / no admitted row`

Lane A intake checked `py85252876/Reconstruction-based-Attack` /
`Black-box Membership Inference Attacks against Fine-tuned Diffusion Models`
because it is a non-duplicate black-box fine-tuned diffusion membership
candidate with an open Zenodo package for checkpoints and datasets.

This is stronger than a paper-only watch item: the public release includes
Stable Diffusion v1-5 LoRA checkpoint folders and several CelebA dataset pickle
files. It is still not a current DiffAudit execution target because the public
surface does not ship generated responses, reconstruction-distance feature
packets, score rows, ROC arrays, metric JSON, or a ready verifier output. The
Zenodo ZIP central directory also does not expose the complete four-way
`target_member / target_non_member / shadow_member / shadow_non_member` score
input set required by the repository's `test_accuracy.py` entrypoint.

## Public Surface Checked

| Item | Evidence |
| --- | --- |
| Repository | `https://github.com/py85252876/Reconstruction-based-Attack` |
| Checked commit | `93ee8dd4d12697354cd182461a9aa268b8de63e6` |
| Git tree | `10` blobs, `71,607` total blob bytes |
| Tags | `git ls-remote` found no tag refs |
| Paper | arXiv `2312.08207` |
| Zenodo record | `https://zenodo.org/records/13371475` |
| Zenodo DOI | `10.5281/zenodo.13371475` |
| Zenodo file | `extra_data-20240825T145405Z-001.zip`, `736,366,195` bytes, `md5:a52e197025c54c197b00674d398f2f6a` |
| Zenodo metadata | open dataset; description says it provides some fine-tuned model checkpoints and datasets |

The Zenodo file was not fully downloaded. The gate used `HEAD` plus byte-range
inspection of the ZIP end-of-central-directory and central directory.

## Repository Contract Found

The README defines a reconstruction-distance pipeline:

1. fine-tune Stable Diffusion v1-5 with LoRA on a prepared dataset;
2. generate images from the fine-tuned model for attack scenarios;
3. calculate reconstruction distance between generated images and query images;
4. train threshold, distribution, or classifier attacks from reconstruction
   distance features.

The code confirms that the public package is not a ready score replay:

- `inference.py` loads `runwayml/stable-diffusion-v1-5`, loads LoRA attention
  processors from a checkpoint directory, generates CUDA responses from
  `dataset["text"]`, and saves images locally.
- `cal_embedding.py` is required after generation to calculate reconstruction
  distance features from generated samples and query images.
- `test_accuracy.py` does not consume raw images or LoRA checkpoints. It
  expects four precomputed torch feature files:
  `--target_member_dir`, `--target_non_member_dir`, `--shadow_member_dir`, and
  `--shadow_non_member_dir`.

## Zenodo ZIP Central Directory

The central directory contains `21` entries with compressed size
`736,355,749` bytes and uncompressed size `1,823,506,683` bytes.

| Surface | Entries |
| --- | --- |
| Extensions | `.bin`: `12`, `.pkl`: `8`, `.md`: `1` |
| Checkpoint folders | `celeba_target`, `celeba_shadow`, `celeba_partial_target`, `celeba_partial_shadow` under `model_checkpoints/*/checkpoint-25000/` |
| LoRA files | each checked checkpoint folder includes `pytorch_lora_weights.bin`, `optimizer.bin`, `scheduler.bin`, and `random_states_0.pkl` |
| Dataset pickle paths | `dataset/partial-100-target/member/dataset.pkl`, `dataset/partial-100-target/non_member/dataset.pkl`, `dataset/100-target/non_member/dataset.pkl`, `dataset/100-shadow/non_member/dataset.pkl` |

Notably, the central directory does not contain generated image responses,
DreamSim/LPIPS/CLIP/reconstruction-distance feature files, score arrays, ROC
arrays, metric JSON, or result logs. It also does not contain a complete
four-way `test_accuracy.py` score-input set; there is no visible
`100-target/member/dataset.pkl` or `100-shadow/member/dataset.pkl` counterpart
in the ZIP central directory.

## Gate Assessment

| Gate | Status |
| --- | --- |
| Target identity | Partial pass. Public LoRA checkpoint folders exist for CelebA target/shadow and partial variants, but the base `runwayml/stable-diffusion-v1-5` weights are not part of the Zenodo package. |
| Member/nonmember split | Partial and incomplete. The ZIP exposes several member/nonmember dataset pickle paths, but the checked central directory does not expose a complete target/shadow member/nonmember score-input set. |
| Query/response coverage | Fail. Generated images are created by `inference.py` at runtime and are not released. |
| Score/metric artifacts | Fail. Reconstruction-distance features, score rows, ROC arrays, metric JSON, and ready verifier outputs are not released. |
| Current DiffAudit fit | Watch-plus only. The candidate is directly relevant to black-box fine-tuned diffusion MIA, but the released package is a checkpoint/data starter rather than a replayable score packet. |
| Download justification | Fail for this cycle. Downloading `736,366,195` bytes would not provide the missing generated responses, reconstruction-distance features, complete score-input split, or metrics. |
| GPU release | Fail. Execution would require the SD v1-5 base model, generated response creation, feature extraction, and attack replay before any metric verdict. |

## Decision

Keep Reconstruction-Based Attack as Research-only black-box watch-plus
evidence. Do not download the Zenodo ZIP, Stable Diffusion v1-5 base weights,
or CelebA payloads in the current cycle. Do not run LoRA inference,
reconstruction-distance extraction, classifier training, or a tiny GPU packet
unless a complete public score-input split or generated response/feature packet
appears, or a separate reviewed decision explicitly accepts rebuilding the
response contract from the checkpoint/data starter package.

Smallest valid reopen condition:

- complete public `target_member`, `target_non_member`, `shadow_member`, and
  `shadow_non_member` feature files compatible with `test_accuracy.py`; or
- generated response images plus reconstruction-distance feature packets and a
  metric/ROC artifact; or
- a bounded consumer-boundary decision that treats this checkpoint/data starter
  package as sufficient for a new response-generation lane, with frozen base
  model hash, ZIP checksum, member/nonmember identity files, command, metric
  contract, and stop condition.

Current slots after this gate:

- `active_gpu_question = none`
- `next_gpu_candidate = none`
- `CPU sidecar = none selected after Reconstruction-Based Attack artifact gate`

Reflection: this cycle found a more concrete public surface than paper-only
assets, but it still does not change the execution decision. Running it now
would be a new response-generation and feature-extraction experiment rather
than a replay of a public score artifact, so the correct action is to stop at
watch-plus.

## Platform and Runtime Impact

None. Platform and Runtime should continue consuming only the admitted
`recon / PIA baseline / PIA defended / GSA / DPDM W-1` set.
