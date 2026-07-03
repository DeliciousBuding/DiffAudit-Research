# LeakyCLIP CLIP-Inversion Boundary Gate

> Date: 2026-05-25
> Status: CLIP inversion privacy watch-plus / official code-public / diffusion used only as refinement / no row-bound membership artifact / no download / no GPU release / no admitted row

## Question

Does arXiv `2508.00756` / `LeakyCLIP: Extracting Training Data from CLIP`
expose a public DiffAudit-ready diffusion membership target, split, score
packet, or verifier that should change the active Research slots?

This was selected as a narrow Lane A metadata gate because the recent arXiv
search surfaced a privacy paper whose abstract mentions diffusion models and
training-data membership leakage, and GitHub search found an official public
repository. The check used arXiv API metadata, GitHub repository metadata, the
recursive tree, releases/tags metadata, and the official README. It did not
clone the repository, download CLIP models, download Stable Diffusion or VAE
weights, download LAION/Flickr/LFW/Furniture datasets, generate images, train
embedding alignment, run inversion, or compute metrics.

## Public Surface

| Field | Value |
| --- | --- |
| Paper line | `LeakyCLIP: Extracting Training Data from CLIP` |
| arXiv | `https://arxiv.org/abs/2508.00756v4` |
| Published / updated | `2025-08-01T16:32:48Z` / `2026-05-21T07:46:00Z` |
| Official code | `https://github.com/dongdongunique/LeakyCLIP` |
| Repository state | default branch `main`, pushed `2026-02-27T08:12:16Z`, updated `2026-05-11T07:59:31Z`, `24` stars, no license in GitHub metadata, `0` releases, `0` tags |
| Repository topics | `clip-inversion`, `clip-memorization`, `clip-privacy-leakage`, `multimodal-model-privacy`, `training-data-extraction-from-clip` |
| Current scope | CLIP inversion / multimodal privacy; Stable Diffusion is an optional refinement component, not the audited target model |

The official repository is a real code surface. The checked tree includes
configuration files, inversion/refinement code, evaluation metrics, scripts,
and documentation images:

```text
README.md
config.py
data.py
ea_train.py
eval/metrics.py
inversion/inverter.py
main.py
refinement/sd_refiner.py
configs/baseline/{flickr,furniture_object,laion}.json
configs/method/{flickr,furniture_object,laion,single}.json
scripts/run_dataset_inversion_baseline.sh
scripts/run_ea_train.sh
scripts/run_inversion.sh
scripts/run_laion_inversion.sh
docs/example_output.png
docs/pipeline.png
```

The README describes a three-stage pipeline: adversarial fine-tuning of CLIP,
embedding alignment from text embeddings to pseudo-image embeddings, and
optional Stable Diffusion refinement for texture/detail recovery. It lists
required public CLIP, robust CLIP, Stable Diffusion XL, VAE, SSCD, and dataset
downloads. It also states that membership can be inferred from reconstruction
metrics.

No committed result packet was visible in the checked public tree: no frozen
CLIP checkpoint hashes, no immutable LAION/Flickr/LFW/Furniture member and
nonmember manifests, no generated reconstruction packet, no per-row membership
score file, no ROC arrays, no metric JSON, no trained embedding-alignment
weights, and no no-training verifier output.

## Claim Boundary

LeakyCLIP is scientifically relevant privacy evidence, but it does not audit a
diffusion model as the target. The target under attack is CLIP. Diffusion
appears as an image-refinement stage after CLIP inversion and as a general
background risk in the paper abstract, not as the membership target whose
training set is being inferred.

That makes it adjacent to DiffAudit's image-generation privacy map but outside
the current diffusion / latent-image per-sample membership consumer contract.
Treating it as a diffusion MIA asset would conflate a CLIP inversion threat
model with a diffusion-model membership row.

## Gate Result

| Gate | Result |
| --- | --- |
| Current image/latent-image fit | Partial. It is multimodal image privacy work, but the audited target family is CLIP rather than a diffusion or latent-diffusion generator. |
| Target identity | Fail for DiffAudit replay. The README lists CLIP/robust CLIP/SDXL/VAE model sources, but no paper-bound hashes or frozen target bundle is committed. |
| Exact member split | Fail. No immutable member row IDs, image filenames, captions, URLs, or split manifests are committed. |
| Exact nonmember split | Fail. No row-bound holdout/nonmember manifest is committed. |
| Query/response or score coverage | Fail. The repository ships code and examples, not reconstruction packets, per-row membership scores, ROC arrays, metric JSON, or verifier output. |
| Mechanism delta | Pass as watch-plus only. CLIP inversion with reconstruction metrics is a different privacy surface, but not a diffusion membership mechanism for the current admitted boundary. |
| Download justification | Fail. Running it would require CLIP/SDXL/VAE/SSCD/model and dataset downloads without a released row-bound replay packet. |
| GPU release | Fail. The blocker is target-family boundary plus missing replay artifacts, not local compute. |

## Decision

`CLIP inversion privacy watch-plus / official code-public / diffusion used only
as refinement / no row-bound membership artifact / no download / no GPU release
/ no admitted row`.

Keep LeakyCLIP as Research-only adjacent privacy evidence. It is useful for
framing multimodal model privacy and CLIP training-data extraction risk, but it
does not reopen the current diffusion asset path and does not justify model,
dataset, or GPU work.

Current slots become `active_gpu_question = none`, `next_gpu_candidate = none`,
and `CPU sidecar = none selected after LeakyCLIP CLIP-inversion boundary gate`.

Smallest valid reopen condition:

- authors publish compact row-bound reconstruction and membership score
  packets with immutable member/nonmember manifests, model hashes, ROC arrays,
  metric JSON, and a no-training verifier; and
- DiffAudit explicitly opens a CLIP / multimodal-model privacy consumer
  boundary separate from diffusion / latent-image admitted rows.

Stop condition:

- Do not download CLIP, robust CLIP, SDXL, VAE, SSCD, LAION, Flickr, LFW,
  Furniture, generated reconstructions, or embedding-alignment weights from
  this gate.
- Do not clone or run LeakyCLIP for execution from this gate.
- Do not run `main.py`, `ea_train.py`, `scripts/run_*`, inversion, refinement,
  metric computation, or GPU work from this gate.
- Do not add Platform/Runtime rows, schemas, product copy, or recommendation
  logic until a reviewed CLIP privacy consumer boundary or row-bound replay
  artifacts exist.

## Platform and Runtime Impact

None. Platform and Runtime continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
