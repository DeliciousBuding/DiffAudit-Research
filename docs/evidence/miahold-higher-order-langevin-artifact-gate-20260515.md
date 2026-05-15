# MIAHOLD Higher-Order Langevin Artifact Gate

> Date: 2026-05-15
> Status: defense-code-public / split-and-attack-code-present / score-artifacts-missing / no download / no GPU release / no admitted row

## Question

Can the official `bensterl15/MIAHOLD` / `bensterl15/MIAHOLDCIFAR` public
surface for `Defending Diffusion Models Against Membership Inference Attacks
via Higher-Order Langevin Dynamics` become the next bounded DiffAudit defense
or MIA replay target?

This was an artifact gate only. It inspected public GitHub metadata, shallow
Git trees, README files, split files, training logs, configs, and attack code.
No Google Drive checkpoint, audio dataset, CIFAR/CelebA asset, W&B artifact,
generated sample packet, or score output was downloaded or executed.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `Defending Diffusion Models Against Membership Inference Attacks via Higher-Order Langevin Dynamics` / arXiv `2509.14225` |
| Paper-index entry | `references/materials/paper-index.md` already records `HOLD++` as a higher-order Langevin defense line |
| Main repository | `https://github.com/bensterl15/MIAHOLD` |
| Main repo checked commit | `8d3d418a07a33856a28741f10210e9f4b3bc44c7` |
| Main repo latest push observed | `2025-09-01T04:59:18Z` |
| Main repo license field | none |
| CIFAR repository | `https://github.com/bensterl15/MIAHOLDCIFAR` |
| CIFAR repo checked commit | `ce4fcb6ab845f387ac9c8ca50def351d9c5d7a81` |
| CIFAR repo latest push observed | `2026-02-06T17:42:37Z` |
| CIFAR repo license field | `Other` |
| GitHub releases | none observed for either repository |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| `MIAHOLD/README.md` | Identifies the repo as the official HOLD++ privacy-preserving codebase and says it includes toy and audio examples, but still contains placeholder citation, license, and contact fields. |
| `MIAHOLD/audio_application/README.md` | Is largely the upstream Grad-TTS README. It points users to Google Drive for Grad-TTS/HiFi-GAN checkpoints and describes training/inference, not a released HOLD++ score packet. |
| `MIAHOLD/audio_application/split/*` | Commits LJSpeech and LibriTTS filelists, including `ljspeech/train.txt`, `ljspeech/valid.txt`, `libritts/train_100.txt`, and `libritts/test_100.txt`. These are useful split evidence for an audio/TTS defense lane, but not image/latent-image DiffAudit replay assets. |
| `MIAHOLD/audio_application/attack.py` | Loads a local checkpoint, computes member and nonmember reconstruction-style scores from `train_loader` and `test_loader`, computes `BinaryAUROC` / `BinaryROC`, and logs `validation/AUROC_max` plus `validation/tpr_fpr_max` to W&B. It does not write committed score arrays, ROC CSVs, or metric JSON. |
| `MIAHOLD/toy/` | Commits a toy `model.pth` and large training logs. The toy code computes ROC/AUC and logs W&B artifacts, but the public repo does not ship replayable member/nonmember score packets or metric JSON for the paper defense claim. |
| `MIAHOLDCIFAR/README.md` | Is primarily the CLD-SGM README and points to Google Drive checkpoint folders for CIFAR-10/CelebA-HQ. It documents training/evaluation commands, not a released HOLD++ membership score packet. |
| `MIAHOLDCIFAR/configs/specific_cifar10.txt` | Sets `sde = hold` and `model_order = 3`, so the CIFAR branch contains a real higher-order Langevin configuration path. |
| `MIAHOLDCIFAR/util/datasets.py` | Uses torchvision CIFAR-10 train/test data and currently subsets the first `128` train rows and first `128` validation rows in code. This is a code-level split rule, not a committed immutable manifest or released score packet. |
| `MIAHOLDCIFAR/pia.py` | Implements a HOLD-style proximal inference attack: it collects train/validation images, assigns member/nonmember labels, computes ROC arrays in memory, prints `AUC = ...`, and logs `val/AUROC` to W&B. The code comments out saving ROC arrays as artifacts. |
| `MIAHOLDCIFAR/log2.err` / `log2.out` / `nohup.out` | Show a local CUDA training attempt and argument errors. They do not contain a final replayable AUROC board, strict-tail metrics, score arrays, checkpoints, or artifact hashes. |
| Recursive trees | Outside toy/model/logs and split text files, no committed `.npz`, `.npy`, `.h5`, `.hdf5`, score CSV, metric JSON, ROC artifact, or model-checkpoint-bound MIA packet was found. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for execution. The repos contain training code and Google Drive checkpoint instructions, but no public checkpoint-bound HOLD++ target with verifiable size/hash/training binding was committed or released. |
| Exact member split | Partial pass. Audio filelists are committed, and CIFAR code selects fixed first-`128` train rows, but this is not enough for a DiffAudit image/latent-image replay because the corresponding target and score packet are missing. |
| Exact nonmember split | Partial pass. Audio validation/test filelists and CIFAR first-`128` test rows exist at the code/filelist level, but no immutable member/nonmember manifest is bound to a released target and score packet. |
| Query/response or score coverage | Fail. AUROC/ROC values are computed only at runtime and logged to W&B or printed. No reusable member/nonmember scores, ROC arrays, metric JSON, generated responses, or report artifacts are shipped. |
| Mechanism delta | Pass as a defense reference. Higher-order Langevin dynamics / `HOLD++` is a real mechanism shift and not another CommonCanvas, MIDST, Beans, Fashion-MNIST, SecMI, or denoising-loss repeat. |
| Current DiffAudit fit | Defense watch-plus. The code is more useful than paper-source-only defense references, but it is not an executable score packet or admitted defense row. The audio branch is cross-modal; the CIFAR branch still requires checkpoint/data acquisition and execution. |
| Download justification | Fail. Downloading Google Drive checkpoints or datasets would not recover committed score artifacts; it would start a new reproduction/training job without a bounded replay packet. |
| GPU release | Fail. There is no frozen checkpoint, score artifact, metric contract, or stop condition that would justify a GPU run. |

## Decision

`defense-code-public / split-and-attack-code-present /
score-artifacts-missing / no download / no GPU release / no admitted row`.

MIAHOLD should be retained as a higher-order Langevin defense watch-plus item.
It has real defense mechanism code, attack code, filelists, and a CIFAR HOLD
configuration, but it does not expose the artifact set DiffAudit needs for the
next execution cycle: checkpoint-bound target identity, immutable
member/nonmember manifests, reusable score rows, ROC arrays, strict-tail
metrics, or a ready verifier command.

Smallest valid reopen condition:

- A public HOLD++ checkpoint bundle with size/hash and training binding for a
  fixed dataset/split;
- Matching member and nonmember manifests for the checkpoint;
- Raw member/nonmember attack scores, ROC arrays, metric JSON, or a bounded
  verifier command that reads public artifacts without retraining or acquiring
  datasets from scratch; and
- For audio/TTS, an explicit consumer-boundary decision opening a TTS/audio
  defense lane before any dataset/checkpoint download.

Stop condition:

- Do not download Grad-TTS, HiFi-GAN, CLD-SGM, CIFAR, CelebA, LJSpeech, or
  LibriTTS assets from this gate.
- Do not scrape W&B run artifacts, train HOLD++ CIFAR/Grad-TTS models, or
  regenerate PIA scores from scratch in the current roadmap cycle.
- Do not promote HOLD++ into Platform/Runtime defense rows, product copy,
  recommendation logic, or the admitted evidence bundle.

## Reflection

This was the right kind of Lane A/B check: a non-adjacent defense mechanism
with public code was inspected once, then closed at the artifact gate instead
of being turned into a long reproduction project. Current slots remain
`active_gpu_question = none`, `next_gpu_candidate = none`, and `CPU sidecar =
none selected after MIAHOLD higher-order Langevin artifact gate`.

## Platform and Runtime Impact

None. MIAHOLD remains Research-only defense watch-plus evidence. Platform and
Runtime continue consuming only the admitted `recon / PIA baseline / PIA
defended / GSA / DPDM W-1` set.
