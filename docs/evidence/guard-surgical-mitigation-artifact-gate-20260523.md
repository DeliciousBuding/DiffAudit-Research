# GUARD Surgical Mitigation Artifact Gate

> Date: 2026-05-23
> Status: official code-public mitigation watch / no score artifacts / no
> download / no GPU release

## Question

Can `kairanzhao/GUARD`, the official code for arXiv `2603.00133` /
`You Don't Need All That Attention: Surgical Memorization Mitigation in
Text-to-Image Diffusion Models`, become a bounded DiffAudit execution target,
or should it remain Research-only memorization-mitigation context?

This was a metadata gate only. I checked public arXiv metadata/HTML, arXiv
source `HEAD`, GitHub repository/code searches, the official GitHub repository
metadata, recursive tree metadata, README, and selected raw script text. No
arXiv source tarball, GitHub archive, Google Drive payload, Stable Diffusion
weight, memorized image packet, generated image packet, checkpoint, score file,
ROC artifact, metric JSON, or verifier output was downloaded.

## Candidate

| Field | Value |
| --- | --- |
| Paper | `You Don't Need All That Attention: Surgical Memorization Mitigation in Text-to-Image Diffusion Models` |
| arXiv | `2603.00133v1` |
| Published / updated | `2026-02-23T17:20:40Z` |
| Official repository | `https://github.com/kairanzhao/GUARD` |
| Repository description | `[ICML'26] You Don’t Need All That Attention: Surgical Memorization Mitigation in Text-to-Image Diffusion Models` |
| Default branch / checked commit | `main` / `3a49dafe6de652c1a6d9b6dd13758d2e67118094` |
| Commit date / message | `2026-05-11T20:46:54Z` / `updates` |
| Repo pushed / updated | `2026-05-11T20:46:57Z` / `2026-05-11T20:47:03Z` |
| Repo size / license | `1,457` KB / MIT |
| Releases / tags | none observed |
| arXiv source `HEAD` | `application/gzip`, `Content-Length = 1,429,877`, SHA-256 ETag `7d33099de25263768026fd4d5d45cbb825acbe01bac60ee648843bae565ba625` |

## Public Surface Checked

| Source | Finding |
| --- | --- |
| arXiv HTML | The paper frames GUARD as inference-time memorization mitigation for text-to-image diffusion. It guides generation away from an original training image while preserving prompt alignment through attractive-repulsive dynamics and cross-attention attenuation. |
| GitHub repository search | Exact-title and GUARD/memorization-mitigation searches find the official `kairanzhao/GUARD` repository. RAPTA/ADMCD searches for arXiv `2603.13070` did not expose an official repository. |
| `README.md` | Identifies the repo as official ICML 2026 code. It says the `sdv1_500_mem` Stable Diffusion memorization benchmark follows Webster / Wen et al. and instructs users to download prompts and ground-truth images from Google Drive. |
| `README.md` commands | Run `inference_mem.py` for CA attenuation and CA-in-GUARD over `sdv1_500_mem_groundtruth`, with SD v1.4 / SD v2.0 options, `ViT-g-14` reference model, `gen_seed = 0`, and `end = 500`. |
| Recursive tree | `90` entries, not truncated. It contains `detect_mem.py`, `generate_mask.py`, `inference_mem.py`, `io_utils.py`, `local_sd_pipeline.py`, `optim_utils.py`, `metrics/*`, and vendored `open_clip/*`. |
| Artifact-pattern tree scan | Only code/config-like files appear for score/metric-pattern names, mainly `metrics/*`, `open_clip/model_configs/*.json`, and `optim_utils.py`. No committed checkpoints, score rows, ROC arrays, metric JSON outputs, generated image packets, data archives, or verifier outputs were visible. |
| `detect_mem.py` | Loads `CompVis/stable-diffusion-v1-4` by default, generates samples, collects `uncond_noise_norm` and `text_noise_norm`, and writes runtime JSONL to `det_outputs/`. The file is a generator/scorer script, not a committed result packet. |
| `inference_mem.py` | Loads SD / optional UNet, LPIPS, OpenCLIP, BLIP2/Pegasus-related dependencies, runs mitigation/inference, and logs optionally to W&B. No ready result artifact is committed. |
| `generate_mask.py` | Loads SD components and a dataset, accumulates gradients, and writes local masks. It requires model/data execution, not a precomputed public artifact. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for execution. Scripts default to `CompVis/stable-diffusion-v1-4` and optional SD/UNet paths, but no checkpoint-bound defended/undefended target package or generated response packet is committed. |
| Exact member/nonmember split | Fail for DiffAudit admission. The README points to `sdv1_500_mem` prompts and ground-truth images via Google Drive/Wen et al., but the repo itself does not commit an immutable member/nonmember evaluation manifest. |
| Query/response or score coverage | Fail. The repo commits scripts that generate runtime outputs, not reusable per-row scores, ROC arrays, metric JSON, retained-utility tables, generated images, or verifier outputs. |
| Mechanism delta | Pass as mitigation context. GUARD is a distinct inference-time attention/attractive-repulsive mitigation mechanism, not another LoRA-weight BAF, denoising-loss, CLIP/pixel, CommonCanvas, MIDST, or SecMI repeat. |
| Consumer fit | Fail for current admission. The claim is memorized-generation mitigation, not current per-sample membership audit rows. Product use would need a reviewed memorization-mitigation consumer boundary with pre/post metrics. |
| Download justification | Fail. The public tree is enough to decide this cycle; execution would require Google Drive memorized-image data, Stable Diffusion weights, reference model downloads, and local generation. |
| GPU release | Fail. No public row-bound score packet or verifier exists. |

## Decision

`official code-public mitigation watch / no score artifacts / no download / no
GPU release / no admitted row`.

GUARD is stronger than paper-source-only mitigation work because official code
is public, MIT-licensed, and small enough to inspect through metadata. It still
does not satisfy a DiffAudit execution gate. The public release requires users
to download `sdv1_500_mem` assets from Google Drive, load Stable Diffusion /
reference models, generate outputs, and compute metrics locally. It does not
ship checkpoint-bound target identities, immutable row manifests, generated
response packets, pre/post mitigation scores, ROC arrays, metric JSON,
retained-utility artifacts, or a no-training verifier.

Smallest valid reopen condition:

- Public immutable `sdv1_500_mem` row manifest or equivalent member/nonmember
  / memorized/non-memorized identities;
- Defended and undefended model/scheduler/checkpoint identity with sizes and
  hashes;
- Generated image or internal-score packets bound to those identities;
- Pre/post GUARD score rows, ROC arrays, metric JSON, and retained-utility
  metrics; and
- A bounded verifier command that reads those artifacts without downloading
  Stable Diffusion weights, Google Drive images, or rerunning generation.

Stop condition:

- Do not download the arXiv source, GitHub archive, Google Drive
  `sdv1_500_mem` assets, Stable Diffusion weights, reference model weights,
  generated images, masks, or checkpoints in this cycle.
- Do not run `detect_mem.py`, `inference_mem.py`, `generate_mask.py`, W&B
  logging, local generation, or mitigation sweeps.
- Do not promote GUARD into Platform/Runtime rows until public row-bound
  pre/post mitigation artifacts and a reviewed memorization-mitigation
  consumer boundary exist.

## Platform and Runtime Impact

None. GUARD remains Research-only memorization-mitigation watch evidence.
Platform and Runtime should continue consuming only the admitted
`recon / PIA baseline / PIA defended / GSA / DPDM W-1` set.
