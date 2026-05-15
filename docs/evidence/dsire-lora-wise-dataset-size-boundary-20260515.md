# DSiRe / LoRA-WiSE Dataset-Size Boundary Gate

> Date: 2026-05-15
> Status: public LoRA weight benchmark / dataset-size recovery semantic shift /
> no dataset download / no GPU release / no admitted row

## Question

Can `MoSalama98/DSiRe` and the `MoSalama98/LoRA-WiSE` Hugging Face dataset
become a new DiffAudit per-sample membership asset, or should they be kept as a
future weight-only aggregate privacy lane?

This was a Lane A / consumer-boundary metadata gate only. It inspected the
official GitHub repository, repository tree, README, license, DSiRe runner, and
Hugging Face dataset metadata/card. No LoRA-WiSE parquet shard, image payload,
Stable Diffusion weight, LoRA tensor payload, or GPU job was downloaded or
executed.

## Public Surface

| Field | Value |
| --- | --- |
| Code repository | `https://github.com/MoSalama98/DSiRe` |
| Description | Official implementation of `Dataset Size Recovery from LoRA Weights`. |
| Default branch / checked commit | `main` / `7047f5d9a19c1c3a813c2cff603b1004a4250968` |
| Commit date / message | `2024-06-30T19:29:53Z` / `Update citations.` |
| Repo updated / size field | `2025-09-18T06:33:46Z` / `2,723` KB |
| License | Software Research License; research use only, commercial use requires a separate Yissum license. |
| Releases / tags | `0` releases / `0` tags |
| Recursive tree | `LICENCE`, `README.md`, `dsire.py`, `requirements.txt`, and `imgs/diagrama.gif`; no committed model checkpoints, result tables, or local score packets. |
| Hugging Face dataset | `https://huggingface.co/datasets/MoSalama98/LoRA-WiSE` |
| HF dataset SHA / last modified | `50551b9e9cc48d04e996ad036a13ab6d1d55cdd4` / `2024-07-05T09:33:48Z` |
| HF access / storage | public, non-gated / `102,848,183,091` bytes reported `usedStorage` |
| HF configs | `high_32`, `low_16`, `low_32`, `low_8`, `medium_16`, `medium_32`, `medium_32_2` |
| HF rows / files | `2,050` dataset rows across configs, `101` parquet shards, and `7,993` image files in the metadata listing |

## What Is Present

| Source | Finding |
| --- | --- |
| Paper / README claim | DSiRe introduces dataset-size recovery from LoRA weights and reports a best classifier mean absolute error of `0.36` images. The README frames the method as using LoRA matrix norms/spectra to infer the number of fine-tuning images. |
| `dsire.py` | Loads `MoSalama98/LoRA-WISE` with Hugging Face `datasets`, extracts SVD features from LoRA A/B matrices, uses FAISS nearest-neighbor voting across layers, and reports validation accuracy, MAPE, and MAE. |
| LoRA-WiSE dataset card | Describes `2,050` Stable Diffusion LoRA fine-tuned model rows: SD 1.5 and SD 2, ImageNet and Concepts101 sources, low `[1..6]`, medium `[1,10,20,30,40,50]`, and high `[1,10,100,500,1000]` dataset-size labels. Each row represents one fine-tuned model and contains `label`, `name`, and LoRA layer weight arrays. |
| Asset strength | The public dataset is a real benchmark with non-gated metadata and structured parquet shards, unlike README-only or paper-source-only watch items. |

## Gate Result

| Gate | Result |
| --- | --- |
| Per-sample member/nonmember identity | Fail for current DiffAudit admission. The primary label is training dataset size, not per-sample membership. The dataset does not define member/nonmember query rows, generated responses, or low-FPR per-sample MIA metrics. |
| Target model identity | Partial for a future weight-only lane. Each row is a LoRA fine-tuned model weight record, but the current DiffAudit admitted contract is about per-sample image/latent-image membership rows, not aggregate model-level cardinality recovery. |
| Score/metric packet | Partial but semantically shifted. The official script can compute accuracy, MAPE, and MAE for dataset-size prediction, but it does not produce AUC, ASR, TPR@1%FPR, TPR@0.1%FPR, ROC arrays, or member/nonmember score rows. |
| Consumer boundary | Fail for Platform/Runtime admitted rows. Dataset-size recovery is an aggregate privacy-audit task, closer to dataset inference / model-weight forensics than per-sample MIA. It needs a separate consumer vocabulary and Runtime schema before product use. |
| Download justification | Hold. The HF dataset is large (`102.8` GB reported storage) and not needed to decide the current boundary. A download would only be justified after DiffAudit explicitly opens a weight-only LoRA privacy lane with MAE/accuracy as primary metrics. |
| GPU release | Fail. The current decision is semantic and artifact-boundary only; no bounded GPU or CPU sidecar is selected. |

## Decision

`public LoRA weight benchmark / dataset-size recovery semantic shift / no
dataset download / no GPU release / no admitted row`.

DSiRe is not another weak per-sample MIA candidate. It is a stronger and more
distinct public asset than many watch items because it ships official code plus
a large non-gated LoRA weight benchmark. However, it changes the problem type:
the target is aggregate fine-tuning dataset-size recovery from model weights,
not whether a specific image was a training member.

Keep it as a Research-only future weight-only privacy lane candidate. Do not
mix it into admitted `recon / PIA baseline / PIA defended / GSA / DPDM W-1`
rows, and do not cite MAE as a membership AUC substitute.

Smallest valid reopen condition:

- DiffAudit explicitly opens a `weight-only LoRA dataset-size recovery` lane;
- a consumer-boundary note defines how dataset-size recovery differs from
  per-sample membership inference and dataset-level CDI-style claims;
- the lane freezes MAE, MAPE, and accuracy as primary metrics, not AUC/TPR; and
- a bounded metadata-first run selects one small LoRA-WiSE config without
  downloading unrelated image payloads or SD weights.

Stop condition:

- Do not download the full LoRA-WiSE dataset, image folders, Stable Diffusion
  base weights, or LoRA tensor shards inside the current image/latent-image MIA
  roadmap cycle.
- Do not run `python dsire.py *` or FAISS/SVD sweeps before a weight-only lane
  is explicitly opened.
- Do not promote DSiRe into Platform/Runtime admitted rows, product copy,
  recommendation logic, or the admitted evidence bundle.

## Reflection

This gate adds a real future direction without pretending it is the current
answer. The useful signal is that LoRA weights can leak aggregate training-set
cardinality; the immediate discipline is to keep that separate from per-sample
membership claims until DiffAudit has a weight-only consumer contract.

Current slots remain `active_gpu_question = none`, `next_gpu_candidate = none`,
and `CPU sidecar = none selected after DSiRe / LoRA-WiSE dataset-size boundary
gate`.

## Platform and Runtime Impact

None. DSiRe / LoRA-WiSE is not admitted evidence and does not change the
current Platform/Runtime consumer set or schema. A future product integration
would require a new aggregate dataset-size recovery row type and explicit
consumer copy separating model-weight cardinality leakage from per-sample MIA.
