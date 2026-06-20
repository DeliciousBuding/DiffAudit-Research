# E2SCT-035 OpenLVLM-MIA VLM Public Surface Check

> Date: 2026-06-09
> Mode: no-download primary-source check over GitHub raw files and Hugging Face
> repository metadata; no parquet shards, model weights, generated responses,
> GPU runs, or attack executions.
> Decision: future VLM controlled-benchmark scout only; not current Direction A
> image-diffusion evidence; not C14/N50; not a second public score/response
> asset; no_compute_release

## Scope

OpenLVLM-MIA surfaced during the broad multimodal/LLM sidecar search as the
strongest public controlled-benchmark candidate outside the current
image-diffusion lane.

This check asks a narrow question: does the public surface expose a current
Direction A row-bound score/response or metric packet, or only a future VLM
stratum candidate?

Sources checked:

- `https://github.com/yamanalab/openlvlm-mia`
- `https://raw.githubusercontent.com/yamanalab/openlvlm-mia/main/README.md`
- `https://raw.githubusercontent.com/yamanalab/openlvlm-mia/main/main.py`
- `https://raw.githubusercontent.com/yamanalab/openlvlm-mia/main/configs/config_vision_encoder_pretrain.yaml`
- `https://raw.githubusercontent.com/yamanalab/openlvlm-mia/main/configs/config_projector_pretrain.yaml`
- `https://raw.githubusercontent.com/yamanalab/openlvlm-mia/main/configs/config_instruction_tuning.yaml`
- `https://huggingface.co/datasets/paper-2229/openlvlm-mia`
- `https://huggingface.co/paper-2229/openclip-llava`

GitHub REST contents API was not used for the decision because the public IP
was rate-limited; raw GitHub files and `git ls-remote` were sufficient for the
no-download gate.

## Public Surface

`git ls-remote` on 2026-06-09 returned:

- GitHub code main: `879265f7a17cdf616bad90b9d1ba29b213eccd4d`
- HF dataset main: `a4656ebdf1e0ba8c04fae43acd8022e6cc699bbb`
- HF model main: `8c57a060bd4f2fe6cfe403cbf673f693ff00da26`

The README describes OpenLVLM-MIA as a controlled 6,000-image benchmark for
large vision-language model MIA with ground-truth membership at three training
stages. It links the HF dataset `paper-2229/openlvlm-mia` and HF model
`paper-2229/openclip-llava`.

The HF dataset metadata exposes:

- features: `image`, `label`, `parent_dataset`
- splits: `vision_encoder_pretrain`, `projector_pretrain`,
  `instruction_tuning`
- examples: `2,000` per split, `6,000` total
- data files: seven large parquet shards under `data/`

The HF model metadata exposes config/tokenizer files and seven large safetensor
shards. The model README lists base models
`laion/CLIP-ViT-H-14-laion2B-s32B-b79K` and `lmsys/vicuna-7b-v1.5`.

The public code is not just a paper stub. `main.py` loads the HF dataset and
model, evaluates examples, writes `evaluation_results_<timestamp>.pkl`, builds
a score table, computes AUC and TPR@5%FPR, then writes a local CSV. The three
checked config files point to the three HF splits and the HF model.

## Gate Readout

| Gate | Readout | Decision |
| --- | --- | --- |
| Target identity | Public HF model identity is fixed for this check. | `Partial` |
| Split semantics | Public HF dataset exposes labels and three training-stage splits. | `Pass` for a future VLM stratum; not current image-diffusion lane |
| Score/response coverage | No committed row-bound attack scores, generated responses, PKL outputs, CSV score table, ROC rows, or metric JSON were found in the no-download public tree checks. | `Fail` |
| Metric provenance | `main.py` computes AUC/TPR@5%FPR only after local runtime evaluation. | `Fail` for no-training replay |
| Provenance | Code, dataset, and model HEAD identities are fixed; large parquet/model payloads were not downloaded. | `Partial` |
| Consumer boundary | The surface is VLM membership inference, not diffusion image-generation MIA. | `Fail` for Direction A |
| Surface delta | The candidate would be a new modality/consumer stratum, not a second image-diffusion score/response asset. | `Fail` for current second-asset gate |

## Decision

`future VLM controlled-benchmark scout only / public labels-model-code /
runtime_score_outputs_only / no_compute_release`.

OpenLVLM-MIA should not enter current Direction A. It is not a C14 row, not an
N50 denominator row, not admitted evidence, and not the second public
score/response asset. Its value is a possible future VLM controlled-benchmark
stratum if the project opens a separate paper direction with its own consumer
question and gate table.

Allowed wording:

`OpenLVLM-MIA is a future VLM controlled-benchmark scout: it has public labels,
model, and code, but current public sources do not expose a ready row-bound
attack-score/response metric packet, and the modality is outside the current
image-diffusion Direction A lane.`

Forbidden wording:

- admitted DiffAudit evidence;
- current C14 row;
- N50 external denominator row;
- image-diffusion denominator evidence;
- second public score/response asset;
- compute-release target;
- evidence that Direction A now has a second independent row-bound asset;
- evidence that VLM findings transfer to image-diffusion membership auditing.

## Next Action

Do not release compute from this gate.

Reopen only if a separate VLM stratum is approved and the public package or a
bounded local verifier exposes:

- immutable target and split identities;
- row-bound attack scores, responses, or prediction packets;
- metric JSON/CSV or a no-training replay command over public inputs;
- hashes for the exact row packet and score packet; and
- a consumer boundary that is explicitly VLM-specific rather than
  image-diffusion Direction A wording.
