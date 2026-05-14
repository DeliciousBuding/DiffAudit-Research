# Memorization Anisotropy Artifact Gate

> Date: 2026-05-15
> Status: prompt-memorization watch-plus / code-and-prompt-splits-public / no ready score packet / no model download / no GPU release

## Question

Does `Detecting and Mitigating Memorization in Diffusion Models through
Anisotropy of the Log-Probability` provide a ready DiffAudit membership
artifact, or should it only update the current watch boundary?

This is an artifact gate only. It inspects the official GitHub tree, OpenReview
supplement, and paper text. It does not download Stable Diffusion weights,
Realistic Vision weights, generated images, or benchmark datasets, and it does
not run CUDA.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `Detecting and Mitigating Memorization in Diffusion Models through Anisotropy of the Log-Probability` |
| OpenReview | `https://openreview.net/forum?id=HTPGy5ydAY` |
| arXiv | `https://arxiv.org/abs/2601.20642` |
| Official code | `https://github.com/rohanasthana/memorization-anisotropy` |
| Project page | `https://rohanasthana.github.io/memorization_anisotropy/` |
| Reported venue state | ICLR 2026 paper with official code release |
| Mechanism | Denoising-free memorization detection from score-difference norm plus low-noise anisotropic alignment |
| Domain | Prompt-level text-to-image memorization detection for Stable Diffusion style models, not a ready per-image DiffAudit MIA score packet |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| GitHub repository metadata | Default branch `main`, latest observed push `2026-01-29T11:47:08Z`, license `MIT`, `25` blob files, total blob size `6,993,565` bytes, and `0` GitHub releases. |
| GitHub tree | Contains `detect_mem.py`, `detect_eval.py`, `run_detection.sh`, `environment.yml`, `local_model/pipe.py`, prompt files, and an inference-time mitigation notebook. No committed `.pt`, `.npy`, `.npz`, score CSV, ROC JSON, metric JSON, generated image packet, or model checkpoint was found. |
| OpenReview supplement | The supplementary ZIP is `1,651,129` bytes with SHA256 `3c68d1e66c619d7f4a88194ac9fa4d390758903bccb3f113ada307e65027a696` and `28` entries. It mirrors the code/prompt release and has only an empty `det_outputs/` directory. |
| Prompt files in supplement | `sd1_mem.txt` has `500` nonempty lines, `sd1_nmem.txt` has `500`, `sd2_mem.txt` has `219`, `sd2_nmem.txt` has `500`, `RV_mem.txt` has `90`, `RV_nmem.txt` has `90`, and `RV_mem_full.txt` has `500`. These are prompt-level memorized/nonmemorized lists, not immutable image-identity manifests. |
| `run_detection.sh` | Runs SD v1.4 and SD v2 with seed `51`, `gen_num = 1`, guidance scale `7.5`, and mode `x,c|x`; it calls `detect_mem.py` for member and nonmember prompt files. |
| `detect_mem.py` | Downloads/loads `CompVis/stable-diffusion-v1-4`, `stabilityai/stable-diffusion-2`, or `SG161222/Realistic_Vision_V5.1_noVAE`, then writes norm and cosine tensors to local `./det_outputs/*.pt`. Those tensors are not released. |
| `detect_eval.py` | Computes AUC plus `TPR@1%FPR` and `TPR@3%FPR` from generated `.pt` tensors. The default paths point under `./det_outputs/ablation3/...`, which is not present in the repository or supplement. |

Representative paper metrics from Table 1:

| Setting | Paper metric |
| --- | --- |
| SD v1.4, `n = 1`, `M(xT, c)` | `AUC = 0.994 ± 0.001`, `TPR@1%FPR = 0.935 ± 0.002`, time `1.10` seconds per 10 prompts |
| SD v1.4, `n = 4`, `M(xT, c)` | `AUC = 0.999 ± 0.001`, `TPR@1%FPR = 0.984 ± 0.002`, time `3.40` seconds per 10 prompts |
| SD v2.0, `n = 1`, `M(xT, c)` | `AUC = 0.953 ± 0.016`, `TPR@1%FPR = 0.791 ± 0.015`, time `2.20` seconds per 10 prompts |
| SD v2.0, `n = 4`, `M(xT, c)` | `AUC = 0.981 ± 0.003`, `TPR@1%FPR = 0.890 ± 0.009`, time `7.30` seconds per 10 prompts |

The reported metrics are scientifically strong for prompt-level memorization
detection, but they are paper metrics rather than reusable DiffAudit score
artifacts.

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Partial. The code names SD v1.4, SD v2, and Realistic Vision model IDs, but no exact model snapshot hashes, local weight bundle, or target checkpoint artifact is released. Running the release would download large model weights. |
| Exact member split | Partial. Prompt-level memorized lists are public, but they do not bind each row to an immutable training image identity or a DiffAudit member image/query object. |
| Exact nonmember split | Partial. Prompt-level nonmemorized lists are public, but they are prompt controls, not exact held-out image manifests with provenance hashes. |
| Query/response or score coverage | Fail. The repository and supplement do not ship generated images, per-prompt tensors, score arrays, ROC arrays, metric JSON, or a ready result packet. |
| Metric contract | Paper-only plus executable code. `detect_eval.py` defines the metric calculation, but it requires locally generated `.pt` files that are not included. |
| Mechanism delta | Pass as a watch item. Combining isotropic norm and anisotropic alignment is distinct from the existing prompt-conditioned CLiD packet, SimA score-norm gate, and the older diffusion-memorization prompt reference. |
| Current DiffAudit fit | Research-only prompt-memorization watch-plus. It can inform future memorization detection scope, but it does not satisfy the current per-sample image/latent-image MIA consumer contract. |
| GPU release | Fail. A faithful run would require model downloads and CUDA forward passes to create the missing score tensors. |

## Decision

`prompt-memorization watch-plus / code-and-prompt-splits-public / no ready
score packet / no model download / no GPU release`.

This is stronger than a paper-only item because the official release includes
code and prompt splits. It is still not a DiffAudit execution lane because the
public surface lacks reusable score tensors, ROC/metric files, generated image
responses, model snapshot hashes, and image-identity manifests.

Stop condition:

- Do not download SD v1.4, SD v2, Realistic Vision, generated image payloads,
  or MemBench-style assets for this paper inside the current roadmap cycle.
- Do not run `run_detection.sh`, CUDA forward passes, seed matrices,
  generation-count sweeps, mode sweeps, or gamma/normalization ablations until
  a ready score packet or an explicit prompt-memorization lane exists.
- Do not promote this into Platform/Runtime admitted rows. It is prompt-level
  memorization detection, not a per-sample MIA packet with immutable image
  identities and public score coverage.

## Reflection

This check prevents two route errors. First, it avoids treating a high ICLR
paper table as a ready DiffAudit packet when the reusable score artifacts are
missing. Second, it keeps prompt-level memorization detection separate from the
current image/latent-image membership consumer contract. Current slots remain
`active_gpu_question = none`, `next_gpu_candidate = none`, and `CPU sidecar =
none selected after Memorization Anisotropy artifact gate`.

## Platform and Runtime Impact

None. Platform and Runtime should continue consuming only the admitted `recon /
PIA baseline / PIA defended / GSA / DPDM W-1` set. Memorization Anisotropy does
not add a product row, schema field, recommendation rule, or Runtime job.
