# StablePrivateLoRA Defense Artifact Gate

> Date: 2026-05-15
> Status: split-payload-present / training-only defense code / score-artifacts-missing / no download / no GPU release

## Question

Can `WilliamLUO0/StablePrivateLoRA` become a bounded defense or second-asset
execution target for DiffAudit, rather than another paper-only privacy-defense
reference?

This gate inspected only public GitHub metadata, the README, the file tree, and
the training scripts. No dataset image payload, SD-v1.5 base model, LoRA
checkpoint, generated image, training output, or attack score packet was
downloaded or executed.

## Candidate

| Field | Value |
| --- | --- |
| Repository | `https://github.com/WilliamLUO0/StablePrivateLoRA` |
| Paper | `Privacy-Preserving Low-Rank Adaptation Against Membership Inference Attacks for Latent Diffusion Models` / AAAI 2025 / arXiv `2402.11989` |
| Default branch inspected | `main` |
| Latest repo push observed | `2025-08-23T11:19:03Z` |
| License field | none exposed through GitHub repo metadata |
| Target family | Stable Diffusion v1.5 LoRA adaptation on Pokemon, CelebA, AFHQ, and MS-COCO-style split folders |
| Public split payload | Git tree exposes `dataset/*` image/text folders, including member/nonmember-style CelebA folders and Pokemon prompt-image files |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| `README.md` | Official implementation, names MP-LoRA and SMP-LoRA defense variants, links arXiv `2402.11989`, and reports FID/KID/ASR/AUC/TPR only as embedded table images. |
| Git tree metadata | `dataset/Pokemon` has `1,666` blobs (`372,570,174` bytes); `dataset/CelebA_Small` has `600` blobs (`83,656,629` bytes); large split folders also exist for CelebA, AFHQ, and MS-COCO-style variants. |
| Git tree metadata | No `score`, `auc`, `roc`, `metric`, `csv`, `json`, `h5`, `pt`, or `safetensors` result/checkpoint artifact was found outside the `sd-scripts` submodule path. |
| `MP-LoRA-Pokemon.sh` / `SMP-LoRA-Pokemon.sh` | Scripts expect a hard-coded local SD-v1.5 base model path, train on `./dataset/Pokemon`, run `400` epochs, and save new LoRA checkpoints locally. |
| `MP-LoRA-CelebA.sh` / `SMP-LoRA-CelebA.sh` | Scripts require the caller to set `D_tr`, `D^m_aux`, `D^nm_aux`, `D^m_te`, and `D^nm_te` paths, then train for `400` epochs against a local SD-v1.5 base model. |
| Python training scripts | Build member/nonmember attack loaders and print train/test accuracy while saving `attack_model_best.pth`, but do not ship the trained attack model, LoRA checkpoints, raw per-sample scores, ROC curves, or metric JSON. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for execution. The scripts target SD-v1.5 plus newly trained LoRA variants, but no trained LoRA/checkpoint hash is released. |
| Exact member split | Partial pass. Public split folder names encode member/nonmember-style partitions for CelebA-family experiments, and Pokemon files are committed, but the defense scripts still generate/train local targets. |
| Exact nonmember split | Partial pass. Nonmember folders are visible for CelebA-family experiments, but no immutable score packet binds those identities to a released target checkpoint. |
| Query/response or score coverage | Fail. The repo ships table PNGs and training code, not generated response folders, raw per-sample attack scores, ROC CSVs, metric JSON, or ready checkpoints. |
| Mechanism delta | Pass as a defense reference. MP-LoRA/SMP-LoRA is a privacy-preserving LoRA adaptation mechanism, not another MIDM/MIDST/Beans scorer variant. |
| Download justification | Fail for this cycle. Making it executable would require cloning/downloading large dataset payloads, supplying SD-v1.5, training LoRA variants for 400 epochs, and regenerating attack scores. |
| Current DiffAudit fit | Defense watch-plus. Stronger than paper-only because split payloads and code are public, but still not a bounded defense row or score packet. |
| GPU release | Fail. No frozen target checkpoint plus ready score artifacts exist. |

## Decision

`split-payload-present / training-only defense code / score-artifacts-missing /
no download / no GPU release`.

StablePrivateLoRA is worth retaining as a defense watch-plus candidate because
it publishes more than a paper: split folder structure, image/text payloads, and
training code are all visible. It still does not satisfy a DiffAudit execution
gate because the current public surface requires local SD-v1.5, local LoRA
training, and score regeneration, while the repo does not release immutable
checkpoints, raw attack scores, ROC artifacts, or metric packets.

Smallest valid reopen condition:

- A public MP-LoRA/SMP-LoRA/LoRA checkpoint bundle with size/hash and training
  binding to a fixed split;
- Raw per-sample attack score artifacts or metric JSON/CSV for member and
  nonmember identities; and
- A bounded verifier command that reads those artifacts without training SD-v1.5
  LoRAs or rebuilding the attack model from scratch.

Stop condition:

- Do not clone or download the large dataset image payloads, SD-v1.5 base
  model, LoRA checkpoints, generated images, or logs in the current cycle.
- Do not train MP-LoRA/SMP-LoRA, train the attack model, OCR table PNGs into
  admitted metrics, or promote this into Platform/Runtime defense rows.

## Platform and Runtime Impact

None. This is Research-only defense-watch evidence. Platform and Runtime should
continue consuming only the admitted `recon / PIA baseline / PIA defended / GSA
/ DPDM W-1` set.
