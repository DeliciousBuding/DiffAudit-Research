# CDI Official Artifact Gate

> Date: 2026-05-15
> Status: code-public / dataset-inference semantic shift / large-assets-required / no ready score packet / no download / no GPU release

## Question

Does the official `sprintml/copyrighted_data_identification` release provide a
current DiffAudit execution lane that is genuinely different from the weak
pointwise MIA probes while still satisfying target identity, member/nonmember
split, score coverage, metric contract, and bounded stop-gate requirements?

This is an artifact gate, not a CDI reproduction attempt. No model checkpoint,
ImageNet data, MS-COCO data, submodule payload, feature tensor, score tensor, or
Google Drive artifact was downloaded.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `CDI: Copyrighted Data Identification in Diffusion Models` |
| Official repository | `https://github.com/sprintml/copyrighted_data_identification` |
| Repository head checked | `dcd62258b0b3fde05d52aaecfade3b5f4c09507a` on `main` |
| Claim semantics | Dataset inference / copyrighted-data identification, not pointwise single-image membership inference |
| Model families in configs | DiT, U-ViT, LDM, U-ViT text-to-image, U-ViT unconditional, and CIFAR10/SecMI wrappers |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| Official README | Describes an official CDI implementation and explicitly frames CDI as dataset inference because individual-image MIAs are not strong enough for confident copyrighted-data identification. |
| Official README setup | Requires a `cdi` conda environment, a Google Drive model folder via `gdown`, ImageNet train/validation data, MS-COCO 2014 train/validation data plus annotations, COCO text-embedding extraction, and git submodules. |
| GitHub repository tree | Contains configs, dataloaders, model wrappers, attack feature extraction, score computation, and evaluation scripts; no committed `out/features`, `out/scores`, target score packet, or small ready benchmark artifact was present in the public tree. |
| `conf/config.yaml` | Defaults to `n_samples_eval = 20000`, `train_samples = 2500`, `valid_samples = 2500`, and `run_id = 25k`, which is not a tiny first packet. |
| `conf/model/dit.yaml` and `conf/model/uvit_t2i.yaml` | Target configs point to local `model_checkpoints/...` and local ImageNet/COCO dataset paths rather than a self-contained small artifact bundle. |
| `src/dataloaders/dit_dataloader.py` and `src/dataloaders/uvit_t2i_dataloader.py` | Members are loaded from training splits and nonmembers from validation/test splits. This gives a clean conceptual split, but not a small frozen DiffAudit manifest or score packet. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Partial pass. The repo exposes model configs and wrapper identities, but the runnable checkpoints are external local files from a Google Drive model folder and are not hash-pinned in this gate. |
| Exact member split | Partial pass. ImageNet/COCO training splits are used as members, but there is no small committed member manifest or bounded first-packet ID list. |
| Exact nonmember split | Partial pass. ImageNet validation and COCO validation/test-style splits are used as nonmembers, but there is no small committed nonmember manifest or bounded first-packet ID list. |
| Query/response or score coverage | Fail for immediate execution. The public tree does not ship precomputed features, scores, CDI p-values, or a small score packet. |
| Metric contract | Pass at code level. The evaluation surface supports MIA metrics and CDI p-values, but the intended run requires full feature extraction and score computation first. |
| Mechanism delta | Pass as a semantic shift. CDI is a dataset-inference aggregation framework, not another pointwise denoising-loss, score-norm, CLIP/pixel, gradient, or response-stability variant. |
| Current DiffAudit fit | Hold. Opening CDI would change the claim from per-sample membership to dataset-level evidence and would require large model/data downloads plus a new consumer-boundary decision. |
| GPU release | Fail. No bounded command, staged assets, checkpoint hashes, frozen small split, or stop gate exists in this workspace. |

## Decision

`code-public / dataset-inference semantic shift / large-assets-required / no
ready score packet / no download / no GPU release`.

CDI is a useful scientific pivot candidate if DiffAudit explicitly decides that
weak pointwise MIA results should be reframed as dataset-level evidence. It is
not a current automatic Lane A or Lane B execution target because the first real
run would require large external assets and a claim-semantics change, not just a
small metric packet.

Do not download the CDI Google Drive model folder, ImageNet train/validation
archives, MS-COCO 2014 train/validation archives, annotations, generated COCO
text embeddings, or submodule model payloads by default. Reopen only if the
roadmap explicitly opens a dataset-inference lane and freezes:

- checkpoint source, size, and hash verification;
- exact member/nonmember image ID manifests for a bounded first packet;
- the CDI `P` size and contamination assumptions;
- one statistical decision metric, including p-value and low-FPR reporting;
- and a consumer-boundary note that keeps dataset-level evidence separate from
  per-sample membership rows.

## Platform and Runtime Impact

None. This is Research-only gate evidence. It does not add a Platform product
row, does not change Runtime schemas, and does not promote CDI or internal
tri-score evidence to admitted status.
