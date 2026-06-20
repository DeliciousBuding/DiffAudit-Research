# E2SCT-031 SAMA DLM Public-Surface Check

> Date: 2026-06-09
> Mode: GitHub commit/tree check plus small code/config reads; no datasets, models,
> checkpoints, result artifacts, or attack execution
> Decision: support-only DLM public-code artifact; not image-diffusion
> denominator evidence; not admitted; not a second public score/response asset;
> no_compute_release

## Scope

SAMA surfaced during the search for a second row-bound public score/response
asset:

`Membership Inference Attacks on Finetuned Diffusion Language Models`
(`arXiv:2601.20125`, OpenReview `oWKJursYpW`, GitHub `Stry233/SAMA`).

This check asks whether the public repository exposes a ready evidence packet:
target identity, immutable member/nonmember rows, row-bound scores or responses,
metric artifacts, provenance hashes, consumer boundary, and surface-delta
controls. It does not ask whether the method is scientifically interesting, and
it does not evaluate the paper's reported results.

Sources checked:

- `https://github.com/Stry233/SAMA`
- `https://github.com/Stry233/SAMA/tree/5ac7aa4a2e3765958e1b39a7774d72bbe4ee6dcd`
- `https://arxiv.org/abs/2601.20125`
- `https://openreview.net/forum?id=oWKJursYpW`

## Public Surface

`git ls-remote` on 2026-06-09 returned the same commit for `HEAD` and
`refs/heads/main`:

`5ac7aa4a2e3765958e1b39a7774d72bbe4ee6dcd`

A bounded tree/code check found implementation and configuration files, but no
committed result packet. The visible public surface includes:

| Surface | Observation | Boundary |
| --- | --- | --- |
| README | The repository describes SAMA and baseline methods for diffusion language models. Usage requires prepared datasets, trained target DLM models, `SAMA_METADATA_DIR`, and `HF_TOKEN` for gated/private models. | Public method code and instructions, not a row-bound evidence packet. |
| Attack config | `attack/configs/config_all.yaml` sets `target_model: "./"`, `tokenizer: "./"`, local `train_subset.json` / `test_subset.json`, CUDA execution, and `save_metadata: true`. | Target identity and split rows are local placeholders, not immutable public artifacts. |
| Tree contents | The checked tree exposes `attack/`, `dataset/`, `trainer/`, model configs, metric code, and `res/pipe.jpg`. | Code/config surface only. |
| Runtime metadata path | `attack/run.py` computes AUC/TPR from local run outputs and writes metadata after execution. `attack/attacks/sama.py` can write `config.json` and `full_metadata.json` under `SAMA_METADATA_DIR`. | Metadata files are runtime products, not committed public packets. |
| Result artifacts | No public `results/`, score CSV/JSON, ROC arrays, metric JSON, committed `metadata.pkl`, `full_metadata.json`, row manifest, verifier, checkpoint hash packet, or release artifact was observed. | Blocks score/response, metric, provenance, and verifier gates. |

## Gate Readout

| Gate | Readout | Decision |
| --- | --- | --- |
| Target identity | No committed fine-tuned target DLM checkpoint, LoRA, or target hash is public. The attack config points to local `./`. | `Fail` |
| Split semantics | Member/nonmember semantics are present in dataset/attack preparation code, but no immutable public row manifest is committed. | `Fail` |
| Score/response coverage | No ready row-bound score, response, prediction, ROC, or completed metadata packet is public. | `Fail` |
| Metric provenance | Metric code exists, but metrics are produced after local dataset/model execution. | `Fail` |
| Provenance | The code commit is fixed; target, split, score, response, and metric artifact hashes are absent. | `Fail` |
| Consumer boundary | The asset is diffusion-language-model/text evidence, outside the current image-diffusion denominator lane. | `Fail` |
| Surface delta | No public control/delta packet or no-training verifier is committed. | `Fail` |

## Decision

`support-only DLM public-code artifact /
row_bound_score_response_packet_missing / no_compute_release`.

SAMA is a current public DLM MIA codebase with useful runtime-metadata schema
pressure. It does not expose a committed fine-tuned target identity, immutable
member/nonmember row manifest, ready score/response packet, ROC/metric artifact,
provenance hashes, surface-delta control, or no-training verifier.

Allowed wording:

`SAMA is a support-only diffusion-language-model public-code surface. It is
useful for tracking metadata expectations in DLM MIA work, but the public repo
is code/config-only for DiffAudit's evidence contract.`

Forbidden wording:

- admitted DiffAudit evidence;
- current C14 row;
- N50 external denominator row;
- image-diffusion denominator evidence;
- second public score/response asset;
- compute-release target;
- evidence that any image-diffusion MIA route is portable;
- proof that the SAMA method or paper result is wrong.

## Next Action

Do not release GPU/DCU compute from this gate. Reopen only if the authors publish
a compact no-training package with:

- immutable target model identity or checkpoint hash;
- public member/nonmember row manifest;
- row-bound scores, responses, predictions, ROC/metric JSON, or completed
  metadata packet;
- artifact hashes and a verifier command; and
- a consumer-boundary statement that separates DLM/text claims from
  image-diffusion audit claims.
