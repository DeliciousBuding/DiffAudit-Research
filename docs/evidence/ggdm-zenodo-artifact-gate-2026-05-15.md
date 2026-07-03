# GGDM Zenodo Artifact Gate

> Date: 2026-05-15
> Status: graph-diffusion cross-modal watch / code-only artifact / no score packet / no GPU release

## Question

Does `Inference Attacks Against Graph Generative Diffusion Models` provide a
clean next Lane A asset for DiffAudit, or at least a bounded CPU packet that can
change the current `active_gpu_question = none` state?

This is an asset gate only. It inspects public metadata and the small Zenodo
software archive. No graph datasets, generated graph samples, graph diffusion
checkpoints, or score packets were downloaded or executed.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `Inference Attacks Against Graph Generative Diffusion Models` |
| Publication venue | USENIX Security 2026 according to the public arXiv abstract |
| ArXiv | `https://arxiv.org/abs/2601.03701` |
| Zenodo record | `https://zenodo.org/records/17946102` |
| DOI | `10.5281/zenodo.17946102` |
| Record publication date | `2025-12-16` |
| License | `cc-by-4.0` |
| File inspected | `Inference-attacks-against-GGDM-main.zip` |
| File size | `56,162` bytes |
| Zenodo checksum | `md5:96ba7e93e7b5de231ae3a5ea510d7141` |
| Local SHA256 | `cb189c79ecd495c11db214fcbb159c42c8cecb4b1eb77f5c933dff090e35bc0e` |

The archive was staged under `<DOWNLOAD_ROOT>/shared/ggdm-inference-attacks/`
for inspection because it is a small code artifact, not a model or dataset
payload.

## Artifact Contents

The ZIP has `36` entries. The relevant top-level surfaces are:

| Path | Finding |
| --- | --- |
| `README.md` | Says this is the implementation for the USENIX 2026 graph generative diffusion inference paper and points to EDP-GNN, GDSS, and DiGress upstream model repos. |
| `MIA/README.md` | Only instructs running `generate_graphAWE_mutag-mia-black.py`; it states that the Anonymous Walk Embeddings module is not publicly released and must be requested from authors. |
| `MIA/generate_graphAWE_mutag-mia-black.py` | Loads local `*-train_feats_label_edge_list` pickle files, hard-coded generated-graph directories, and `sample_data` pickle files; writes AWE CSVs and similarity pickles. |
| `PIA/graph_noniid_mutag_pia.py` | Loads local training-feature pickles and generated graph sample pickles; computes graph distribution distances, but ships no ready target/split/score artifact. |
| `GRA/regal_diffusion_align.py` / `GRA/regal_diffusion_sim.py` | Require local generated-graph sample directories and match/prediction pickle files. |
| `defense/` | Contains defense scripts with placeholder `XXX` generated-graph paths and local dataset-loading assumptions. |

No target checkpoint, graph training split manifest, generated graph cache,
member/nonmember score CSV, ROC artifact, or metrics JSON is present in the
archive.

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for execution. The README names EDP-GNN, GDSS, and DiGress as upstream model families, but the inspected artifact does not bind a fixed trained target checkpoint or exact training recipe. |
| Exact member split | Fail. Scripts reference local `*-train_feats_label_edge_list` pickle files, but no hashable per-graph member manifest is released. |
| Exact nonmember split | Fail. The archive does not expose a held-out graph manifest or query set. |
| Query/response or score coverage | Fail. Generated graph sample directories and similarity outputs are local dependencies, not shipped artifacts. |
| Metric contract | Partial method reference only. Code sketches GRA/MIA/PIA computations, but there is no bounded ready score packet. |
| Mechanism delta | Pass as a watch item: graph generative diffusion is not CommonCanvas, MIDST, Beans, Fashion-MNIST, CLiD, ReDiffuse, SecMI, or the existing image/latent-image routes. |
| Current DiffAudit fit | Cross-modal watch. It is closer to GGDM-specific graph privacy than the current product-facing image/latent-image admitted bundle. |
| GPU release | Fail. Running this would require acquiring graph datasets, target generated samples, missing AWE code, and likely retraining or recreating graph diffusion targets. |

## Decision

`graph-diffusion cross-modal watch / code-only artifact / no score packet / no GPU release`.

This is a legitimate related-method artifact and the Zenodo payload is small
enough to inspect, but it does not satisfy the membership-semantics or
query/response gates for DiffAudit execution. It should stay as a Research-only
watch item unless authors publish a public-safe graph target checkpoint or
deterministic target recreation, exact member/nonmember graph manifests,
generated graph sample caches, and reusable score/ROC artifacts.

Stop condition:

- Do not request the withheld AWE module, download graph datasets, train
  EDP-GNN/GDSS/DiGress targets, or regenerate graph sample caches inside the
  current image/latent-image roadmap cycle.
- Do not add graph-diffusion claims, Platform rows, Runtime schemas, or
  admitted bundle entries from this artifact.
- Reopen only if a manifest-backed graph target/split/score packet appears, or
  if DiffAudit explicitly opens a graph generative diffusion membership lane.

## Reflection

This cycle tested a genuinely non-duplicate public artifact instead of
relabeling a closed weak image route. The result does not discover a runnable
new signal; it adds a precise cross-modal boundary and preserves
`active_gpu_question = none`, `next_gpu_candidate = none`, and
`CPU sidecar = none selected`.

## Platform and Runtime Impact

None. This is Research-only intake evidence. Platform and Runtime should
continue consuming only the admitted `recon / PIA baseline / PIA defended / GSA
/ DPDM W-1` set.
