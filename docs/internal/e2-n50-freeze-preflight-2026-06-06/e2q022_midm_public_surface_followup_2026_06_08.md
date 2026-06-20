# E2Q-022 MIDM Public-Surface Follow-Up

> Date: 2026-06-08
> Mode: GitHub tree/raw probes + arXiv metadata; no dataset, checkpoint, result, or notebook execution
> Decision: code-public watch-plus only; not a second public score/response asset; no compute release

## Scope

This follow-up rechecks the current public surface for:

`Membership Inference of Diffusion Models`
(`arXiv:2301.09956`).

The row is relevant because it is an early image-diffusion MIA method with a
public code repository:

- `https://github.com/HailongHuPri/MIDM`
- `https://arxiv.org/abs/2301.09956`

This pass does not download datasets, FFHQ assets, target checkpoints, result
files, model weights, or notebook outputs. It checks the repository identity,
visible code/notebook surface, and whether compact row-bound result artifacts
are committed.

Sources checked:

- `https://github.com/HailongHuPri/MIDM`
- `https://raw.githubusercontent.com/HailongHuPri/MIDM/main/README.md`
- `https://raw.githubusercontent.com/HailongHuPri/MIDM/main/Example.ipynb`
- raw probes for likely result/manifest paths:
  `ffhq_1000_idx.npy`, `results/ffhq_1000_idx.npy`,
  `results/ddpm_ffhq/loss_ffhq_1000_ddpm.h5py`,
  `results/ddpm_ffhq/likelihood_ffhq_1000_ddpm.h5py`, `metrics.json`,
  `roc.csv`, and `manifest.json`
- `https://export.arxiv.org/api/query?id_list=2301.09956`

## Current Public Surface

The current public repository surface is:

| Field | Current observation |
| --- | --- |
| repository | `HailongHuPri/MIDM` |
| HEAD | `a7e7be0e00da5ea9473a0e9e1d0091fec638c8c0` |
| README SHA-256 | `55c17489e93b8ce375e24e11222fdc8afc189a2c7d791f3c44be9e113341326b` |
| paper | `arXiv:2301.09956v1` |
| arXiv date | published/updated `2023-01-24` |
| categories | `cs.CR`, `cs.LG` |
| visible surface | preprocessing, attack, and metric code plus an example notebook |
| notebook outputs | `Example.ipynb` has `28` cells, `0` outputs, and no execution counts |

The raw probes for compact public result artifacts returned `404` for:

| Probe | Observation |
| --- | --- |
| `ffhq_1000_idx.npy` | not committed |
| `results/ffhq_1000_idx.npy` | not committed |
| `results/ddpm_ffhq/loss_ffhq_1000_ddpm.h5py` | not committed |
| `results/ddpm_ffhq/likelihood_ffhq_1000_ddpm.h5py` | not committed |
| `metrics.json` | not committed |
| `roc.csv` | not committed |
| `manifest.json` | not committed |

The public surface is therefore method-code public, but output-free. It exposes
how an experiment could be run locally; it does not expose a compact public
artifact that binds target identity, member/nonmember rows, scores/features,
metrics, and provenance into a no-training review packet.

## Gate Readout

| Gate | Readout | Decision |
| --- | --- | --- |
| Target identity | The paper/repo describe diffusion-model MIA experiments, but no immutable public target checkpoint hash or model artifact identity is committed. | `Fail` |
| Split semantics | The code references FFHQ-style member/nonmember handling, but no immutable committed row manifest was found. | `Fail` |
| Score/response coverage | No public row-bound score rows, generated responses, feature packet, result HDF5, ROC CSV, metric JSON, or notebook outputs were observed. | `Fail` |
| Metric provenance | Metric code exists, but public metrics are not packaged as replayable row-bound artifacts. | `Partial` |
| Semantic boundary | The method is directly about membership inference for diffusion models. | `Pass` |
| Consumer/delta boundary | There is no downstream audit packet, surface-delta control, or no-training verifier. | `Fail` |

## Decision

`code-public watch-plus /
row_bound_score_response_packet_missing / no_compute_release`.

MIDM remains a useful background and support reference for the history of
diffusion-model membership inference. It does not change the current
CCF-A-facing evidence state: the public surface lacks a committed row manifest,
target checkpoint hash, row-bound score/response/feature packet, ROC/metric
JSON, notebook outputs, and no-training verifier.

Do not count `E2Q-022` as a second public response/score asset, N50 denominator
row, admitted evidence, C14 false-promotion row, reviewer-reliability evidence,
prevalence evidence, or compute-release target.

Reopen only if the authors publish at least one compact artifact surface:

- immutable target checkpoint/model identity;
- committed member/nonmember row manifest;
- public score, feature, generated-response, ROC, or metric packet;
- executed notebook outputs with artifact hashes; or
- a no-training verifier command over the published artifacts.
