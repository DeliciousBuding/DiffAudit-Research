# E2SCT-016 MIAHOLD Public-Surface Check

> Date: 2026-06-07
> Scope: no-download public-surface check for the measurement-route gap board.

## Question

Does `E2SCT-016` expose checkpoint-bound membership scores, ROC arrays,
metric JSON/CSV, generated responses, or a verifier that can make HOLD++ a
current E2 defense or response/score evidence row?

## Checked Public Surface

No repository clone, release asset, dataset, model, checkpoint, audio payload,
image payload, W&B artifact, or generated output was downloaded. GitHub REST
API was rate-limited during this refresh, so the current check used public
raw files, GitHub HTML pages, and the prior Research evidence gate:
[`docs/evidence/miahold-higher-order-langevin-artifact-gate-20260515.md`](../../evidence/miahold-higher-order-langevin-artifact-gate-20260515.md).

| Surface | Observation |
| --- | --- |
| Main repo | `https://github.com/bensterl15/MIAHOLD` |
| CIFAR repo | `https://github.com/bensterl15/MIAHOLDCIFAR` |
| Releases | Both release pages show no visible release assets. |
| Main README | Identifies the repo as the official HOLD++ membership-privacy codebase with toy and audio examples. |
| Audio README | Largely follows the upstream Grad-TTS README and points to Google Drive Grad-TTS / HiFi-GAN checkpoints, training, and inference commands. |
| Audio split surface | GitHub HTML exposes LJSpeech and LibriTTS train / valid / test text-file surfaces. |
| Audio attack code | `audio_application/attack.py` loads a local checkpoint, computes `BinaryAUROC` / `BinaryROC`, prints max AUC / TPR, and logs metrics to W&B. |
| CIFAR README | Primarily documents CLD-SGM training/evaluation and Google Drive checkpoint setup. |
| CIFAR HOLD config | `configs/specific_cifar10.txt` sets `sde = hold` and `model_order = 3`. |
| CIFAR split rule | `util/datasets.py` downloads CIFAR-10 and subsets the first `128` train rows and first `128` validation rows in code. |
| CIFAR PIA code | `pia.py` computes ROC/AUC in memory, prints `AUC = ...`, logs `val/AUROC` to W&B, and has ROC artifact saving commented out. |

## Finding

`E2SCT-016` is a mixed-modality defense false-promotion exemplar. It has real
mechanism code, split hints, metric code, and a CIFAR HOLD configuration, so a
weak code-availability or metric-code rule could over-promote it. DiffAudit
still blocks the row because the public surface does not expose reusable
checkpoint-bound evidence.

The allowed public surface does not expose:

- checkpoint-bound defended/undefended target identities with hashes;
- immutable member/nonmember manifests bound to those targets;
- reusable member/nonmember score rows;
- ROC arrays;
- metric JSON/CSV;
- generated response packets;
- a no-training verifier command.

## Gate Result

| Gate | Result | Reason |
| --- | --- | --- |
| Target / checkpoint identity | `Fail` | Checkpoint acquisition or training is required; no public checkpoint-bound target packet was found. |
| Split identity | `Partial` | Audio filelists and CIFAR code-level first-`128` splits are visible, but they are not bound to released target and score artifacts. |
| Score or response | `Fail` | Scores and ROC arrays are computed at runtime or logged to W&B, not exposed as public packets. |
| Metric provenance | `Fail` | Metric code exists, but no public metric JSON/CSV, ROC arrays, or verifier were found. |
| Provenance | `Partial` | Official code surfaces are public, but the evidence-bearing artifacts are not. |
| Consumer/delta | `Fail` | This is defense and mixed-modality support, not a current image-diffusion E2 response/score denominator row. |

## Decision

`mixed_modality_defense_false_promotion_exemplar /
metric_code_split_visible / score_artifacts_missing / no_compute_release`.

Do not count `E2SCT-016` as admitted evidence, a response/score asset, a
defense effectiveness result, or an external-audit denominator row. Keep it as
a false-promotion exemplar candidate for the measurement route: public code,
split hints, and metric code are not enough without checkpoint-bound scores,
ROC arrays, metrics, and a verifier.

Allowed wording:

`MIAHOLD/HOLD++ exposes defense code, split hints, CIFAR HOLD configuration,
and PIA-style metric code, but the current public surface does not expose
checkpoint-bound member/nonmember score rows, ROC arrays, metric JSON/CSV,
generated responses, or a no-training verifier. It is a mixed-modality defense
false-promotion exemplar, not admitted response/score or defense-effectiveness
evidence.`

## Baseline Tags

- `code_availability_would_promote`
- `metric_code_split_would_promote`
- `paper_claim_artifact_link_would_promote`
- `diffaudit_contract_blocks_or_bounds`

Do not tag `score_only_would_promote` or
`artifact_availability_would_promote` unless public checkpoint-bound score or
response artifacts appear.

## Reopen Condition

Reopen only if the authors publish a compact public packet that binds fixed
HOLD++ target checkpoints, member/nonmember manifests, raw scores or response
packets, ROC arrays, metric JSON/CSV, and a verifier command. For the audio
branch, also require an explicit consumer-boundary decision opening a TTS/audio
defense lane.

Do not download Grad-TTS, HiFi-GAN, CLD-SGM, CIFAR, CelebA, LJSpeech,
LibriTTS, W&B artifacts, checkpoints, generated samples, or release assets for
this gate.
