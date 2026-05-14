# DMin Data Attribution Gate

> Date: 2026-05-15
> Status: diffusion data-attribution watch-plus / public LoRA-dataset-cache artifacts / not membership inference / no large download / no GPU release

## Question

Does `DMin: Scalable Training Data Influence Estimation for Diffusion Models`
provide a ready DiffAudit mainline after the latest MIA artifact search found
no new public score/ROC packet?

This is an artifact gate only. It inspects public GitHub and Hugging Face
metadata. It does not clone the Hugging Face dataset, download SD3 weights,
download the mixed image dataset, download cached gradients, or run retrieval.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `DMin: Scalable Training Data Influence Estimation for Diffusion Models` |
| arXiv | `https://arxiv.org/abs/2412.08637` |
| Official code | `https://github.com/huawei-lin/DMin` |
| Public LoRA | `https://huggingface.co/huaweilin/DMin_sd3_medium_lora_r4` |
| Public train/test dataset | `https://huggingface.co/datasets/huaweilin/DMin_mixed_datasets_8846` |
| Public cache | `https://huggingface.co/datasets/huaweilin/DMin_sd3_medium_lora_r4_caching_8846` |
| Claim semantics | Training-data influence estimation / data attribution, not per-sample membership inference |
| Model example | Stable Diffusion 3 Medium LoRA trained on a mixed dataset of `8,846` samples |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| GitHub metadata | `huawei-lin/DMin`, default branch `main`, latest observed push `2025-05-17T16:34:23Z`, `19` blobs, total GitHub blob size `4,303,815` bytes, and `0` GitHub releases. |
| README | Describes DMin as scalable training-data influence estimation for diffusion models. It provides a Stable Diffusion LoRA example and says the caching stage can be skipped if the Hugging Face cache is cloned successfully. |
| GitHub tree | Contains retrieval/caching code under `DMIN/`, SD and DDPM pipeline wrappers, `main.py`, SD3 LoRA example notebooks, and a config file. It does not contain MIA labels, ROC arrays, membership score CSVs, or metric JSON. |
| HF LoRA repo | Public, non-gated, last modified `2024-12-17T19:54:18Z`, `6` files, total expanded metadata size `14,361,230` bytes. Key file: `pytorch_lora_weights.safetensors` (`4,742,848` bytes). |
| HF mixed dataset | Public, non-gated, last modified `2024-12-17T19:54:37Z`, `24` files, expanded metadata total `10,185,712,307` bytes. It has `17` train parquet shards and `5` test parquet shards. |
| HF cache repo | Public, non-gated, last modified `2024-12-17T19:53:57Z`, `8,853` siblings. Metadata lists `8,847` `K65536/loss_grad_*.pt` files plus `DimReducer_D1179648.obj`, `index_K65536.bin`, `noise.pkl`, `README.md`, `upload.py`, and `.gitattributes`. |

Representative cache metadata:

| File surface | Observed metadata |
| --- | --- |
| `K65536/loss_grad_*.pt` | `8,847` public compressed-gradient files. First expanded-tree entries are `2,622,675` bytes each. |
| `DimReducer_D1179648.obj` | Public metadata reports `18,875,917` bytes. |
| `index_K65536.bin` | Public HNSW/KNN-style index file listed in cache siblings. |
| `noise.pkl` | Public noise artifact listed in cache siblings. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Pass for data attribution. The example names a public SD3 Medium LoRA repo and a public mixed training dataset. |
| Exact training-data artifacts | Pass at artifact-surface level. The mixed dataset and cached gradients are public and non-gated, though too large to download by default in this MIA roadmap cycle. |
| Query/retrieval coverage | Partial pass. The cache and index make retrieval/influence inspection plausible, but no bounded DiffAudit query packet or paper-level retrieval output packet is committed in this repository. |
| Membership labels | Fail for MIA. DMin does not provide member/nonmember labels or a membership test contract; every training row is part of the influence-retrieval universe. |
| MIA score/ROC coverage | Fail. No membership scores, ROC arrays, AUC/ASR/TPR-at-FPR JSON, or verifier for per-sample MIA is public in the checked surface. |
| Mechanism delta | Pass as a data-audit watch item. Training-data influence retrieval is genuinely different from denoising loss, score norm, prompt-conditioned CLiD, tabular MIDST, and prompt-memorization gates. |
| Current DiffAudit fit | Research-only data-attribution watch-plus. It could inform a future data-attribution lane, but it does not satisfy the current membership-inference consumer contract. |
| GPU release | Fail. Running DMin would require large HF assets and a different claim contract; no current MIA decision depends on it. |

## Decision

`diffusion data-attribution watch-plus / public LoRA-dataset-cache artifacts /
not membership inference / no large download / no GPU release`.

DMin is the strongest public non-MIA artifact found in this search cycle: it
has a public model adapter, public training/test data, public compressed
gradients, and a public retrieval index. It should not be promoted as a
membership-inference result because it lacks member/nonmember labels, MIA
scores, ROC/metric artifacts, and a product-facing MIA contract.

Stop condition:

- Do not download the `10GB` mixed dataset, SD3 base assets, LoRA payloads,
  cached gradients, or retrieval index by default.
- Do not reframe data-attribution retrieval as membership inference or use it
  to add Platform/Runtime admitted rows.
- Reopen only if DiffAudit explicitly opens a training-data attribution lane
  with a separate consumer boundary, or if DMin releases a bounded
  member/nonmember MIA score/metric packet.

## Reflection

This gate captures the one strong ready artifact surfaced by the external
search while preserving scientific semantics. The actionable conclusion is not
"run DMin now"; it is "DMin is a future data-attribution lane, not a hidden
MIA packet." Current slots remain `active_gpu_question = none`,
`next_gpu_candidate = none`, and `CPU sidecar = none selected after DMin data
attribution gate`.

## Platform and Runtime Impact

None. Platform and Runtime should continue consuming only the admitted `recon /
PIA baseline / PIA defended / GSA / DPDM W-1` set. DMin does not add a
membership product row, Runtime job, or admitted bundle entry.
