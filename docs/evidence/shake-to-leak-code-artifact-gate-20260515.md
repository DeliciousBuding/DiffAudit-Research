# Shake-to-Leak Code Artifact Gate

Date: 2026-05-15

## Verdict

`code-public generative-privacy watch-plus / runtime synthetic-private-set construction / checkpoint-data-score artifacts missing / no download / no GPU release / no admitted row`

Lane A intake checked `VITA-Group/Shake-to-Leak` / `Shake to Leak: Fine-tuning
Diffusion Models Can Amplify the Generative Privacy Risk` because it is a
direct diffusion privacy repository and was not yet represented in the active
watch queue. It is mechanism-relevant: the paper's setup fine-tunes
`CompVis/stable-diffusion-v1-1` on a generated synthetic private set and then
uses SecMI-style MIA plus data extraction to test whether fine-tuning amplifies
generative leakage.

This is not a replay or execution target in the current cycle. The public
repository exposes code, scripts, a vendored SecMI/diffusers tree, and a
domain-name list, but it does not publish frozen target checkpoints, immutable
member/nonmember manifests, generated private-set images, generated attack
responses, reusable score arrays, ROC arrays, metric JSON, or ready verifier
output.

## Public Surface Checked

| Item | Evidence |
| --- | --- |
| Repository | `https://github.com/VITA-Group/Shake-to-Leak` |
| Checked commit | `e4690b8f63769ef2f4e20bb8ec6ca76f508c7628` |
| Commit message/date | `fix priv_domains.json`, `2025-03-15T21:46:45Z` |
| Tree size | `165` blobs, `2,447,056` total blob bytes |
| Large committed blobs | only `teaser_img` at `465,124` bytes |
| Tags/releases | no tags; `gh release list` returned no release rows |
| Domain list | `data/priv_domains.json`, `40` celebrity/person domains |

The public tree has no committed model or result artifacts with extensions such
as `.pt`, `.pth`, `.ckpt`, `.safetensors`, `.npy`, `.npz`, `.jsonl`, `.csv`,
`.zip`, or `.tar`. The only large blob is the README teaser image.

## Execution Contract Found

The README describes a three-step local pipeline:

1. `python sp_gen.py` generates the synthetic private set.
2. Fine-tuning scripts run LoRA, DreamBooth, LoRA+DB, or End2End fine-tuning.
3. Attack scripts run SecMI MIA or data extraction.

The checked scripts make the runtime asset requirements explicit:

- `sp_gen.py` loads `CompVis/stable-diffusion-v1-1`, uses CUDA, and generates
  `num_gen = 2000` images per domain into `./data/sp/<domain>/`.
- `scripts/lora_db.sh` fine-tunes `CompVis/stable-diffusion-v1-1` from
  `data/sp/<domain>` and writes local checkpoints under `./ckpts/<domain>/`
  with `--num_train_epochs=100`.
- `scripts/secmi_sd_laion.sh` changes into `../SecMI` and runs
  `python -m src.mia.secmi` with `--dataset-root ../data/`,
  `--member-folder laion-2b`, `--nonmember-folder celeb_and_web`,
  `--model-name CompVis/stable-diffusion-v1-1`, and
  `--ckpt-path ./ckpts/<domain>`.
- `data_extraction.py` loads a local fine-tuned checkpoint, generates
  `num_cand = 5000` candidate images, and compares them against local
  private-folder images with CLIP and pixel-space alignment.

The vendored `SecMI/src/mia/secmi.py` computes member and nonmember scores from
local datasets and the local checkpoint, sweeps thresholds, and prints AUROC.
It does not commit a reusable score packet or result file.

## Gate Assessment

| Gate | Status |
| --- | --- |
| Target identity | Blocked. The target is a locally fine-tuned SD-v1-1 checkpoint under `./ckpts/<domain>`, not a published checkpoint with size/hash/training binding. |
| Member/nonmember split | Blocked. The scripts expect local `data/laion-2b/<domain>` and `data/celeb_and_web/<domain>` folders, but no immutable sample manifest or image identity table is published. |
| Query/response coverage | Blocked. Synthetic private-set images, fine-tuned model outputs, extraction candidates, and attack responses are generated at runtime and are not committed. |
| Score/metric artifacts | Blocked. No per-sample score arrays, ROC arrays, metric JSON/CSV, or ready verifier output is published. |
| Mechanism novelty | Useful as a watch-plus mechanism: fine-tuning-amplified generative leakage is distinct from plain score/loss replay, but the public surface is only a code recipe. |
| Download/GPU decision | No release. Execution would require SD-v1-1 weights, domain data, synthetic private-set generation, fine-tuning, SecMI scoring, and extraction generation from scratch. |

## Boundary Decision

Keep Shake-to-Leak as Research-only code-public watch-plus evidence. Do not
download Stable Diffusion weights, LAION/person images, celebrity/web image
folders, generated synthetic private sets, checkpoints, or full repo payloads.
Do not run `sp_gen.py`, LoRA/DB/End2End fine-tuning, SecMI scripts, or data
extraction. Do not promote Shake-to-Leak into Platform/Runtime admitted rows
without public checkpoint-bound score artifacts and immutable sample
membership semantics.

Current slots after this gate:

- `active_gpu_question = none`
- `next_gpu_candidate = none`
- `CPU sidecar = none selected after Shake-to-Leak code artifact gate`

Reflection: this cycle found a real new mechanism hook, but not a replayable
artifact. Running it now would create a new training-and-extraction experiment,
not verify a public result, so the correct decision is to stop at watch-plus.
