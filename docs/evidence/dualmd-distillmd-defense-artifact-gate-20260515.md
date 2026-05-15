# DualMD / DistillMD Defense Artifact Gate

> Date: 2026-05-15
> Status: supplement-code-public / split-index-files-present / checkpoint-and-score-artifacts-missing / no download / no GPU release / no admitted row

## Question

Can the public surface for `Dual-Model Defense: Safeguarding Diffusion Models
from Membership Inference Attacks through Disjoint Data Splitting` become the
next bounded DiffAudit defense row, replay target, or GPU execution target?

This was an artifact gate only. It inspected arXiv/OpenReview metadata, the
arXiv source package, the OpenReview supplementary code archive, small split
index files, README files, and training/evaluation scripts. No SharePoint
Pokemon payload, Stable Diffusion weight, CIFAR/STL/Tiny-ImageNet dataset,
checkpoint, generated image packet, attack score, ROC output, or metric output
was downloaded or executed.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `Dual-Model Defense: Safeguarding Diffusion Models from Membership Inference Attacks through Disjoint Data Splitting` / arXiv `2410.16657` |
| Paper-index entry | `references/materials/paper-index.md` records `DualMD` / `DistillMD` as a disjoint-data-splitting and distillation defense line |
| arXiv source | `https://arxiv.org/e-print/2410.16657` |
| arXiv source size / SHA256 | `642,017` bytes / `4064aedf4eda40e101f67a48a2bc4c9f5019c7a045bf5cb8f132faf6798523aa` |
| arXiv source content | TeX, bibliography/style files, and figures only |
| OpenReview forum | `https://openreview.net/forum?id=PjIe6IesEm` |
| OpenReview supplementary archive | `68,370,168` bytes / SHA256 `90b2b104aff72976bf7cd239cee797bca34fdfe1179796711723eb1a67d9f4ab` |
| Supplement tree | `DDMD/` with `139` ZIP entries and `102` files |
| Git origin embedded in supplement | `https://github.com/btr13010/DDMD.git` |
| Public GitHub status | `btr13010/DDMD` returned GitHub `404`; `gh search repos "DualMD DistillMD"` returned no public repositories |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| arXiv source package | Contains `main.tex`, section TeX files, bibliography/style files, and figures such as `self-distill.png`, `Inference.png`, and `Training.png`. It does not contain code, checkpoints, split manifests, score arrays, ROC arrays, or metric JSON. |
| OpenReview supplementary `DDMD/README.md` | Identifies the archive as code for the Dual-Model Defense paper and gives commands for DDPM training, disjoint dual-model training, distillation, white-box attacks, black-box attacks, and memorization detection. |
| `DDMD/DDPM/scripts/train.sh`, `train_dual.sh`, `distill.sh` | Train a normal DDPM, two disjoint DDPM teachers, and a private student from local datasets for `780001` steps. They expect `../datasets` and write checkpoints under `./experiments`. |
| `DDMD/DDPM/scripts/secmia.sh`, `pia.sh` | Run SecMIA/PIA against locally trained checkpoints such as `./experiments/CIFAR10-distill/ckpt-step780000.pt`. No such checkpoints or resulting scores are shipped. |
| `DDMD/DDPM/SecMIA/member_splits/*.npz` | Commits DDPM split-index files: CIFAR10/CIFAR100 `25,000 / 25,000` `mia_train_idxs` / `mia_eval_idxs`, STL10-Unlabeled and Tiny-ImageNet `50,000 / 50,000`, plus scalar `ratio`. These are split evidence, not score artifacts. |
| `DDMD/DDPM/stats/cifar10.train.npz` | Contains FID cache statistics `mu [2048]` and `sigma [2048, 2048]`. It is not a MIA score, ROC, or metric packet. |
| `DDMD/LDM/scripts/train-ldm.sh`, `train-dual.sh`, `distill-ldm.sh` | Use `runwayml/stable-diffusion-v1-5`, `../datasets/pokemon`, generated BLIP captions, disjoint partitions, and local checkpoints. They require dataset/model acquisition and training/fine-tuning. |
| `DDMD/LDM/scripts/pia.sh` | Uses `CKPT=path_to_ckpt` and runs PIA against a local LDM checkpoint. It is a template, not a replay command over public artifacts. |
| `DDMD/black-box-attack/*` | Provides black-box attack and DualMD defense code paths, but no generated response images, embeddings, DreamSim/feature vectors, ROC arrays, or metric JSON are committed. |
| `DDMD/memorization/examples/sdv1_500_memorized.jsonl` | Reuses the Diffusion Memorization prompt manifest as a related memorization example. It is not a member/nonmember MIA score packet for DualMD/DistillMD. |
| Recursive supplement tree | Contains Python and shell code, small split-index `.npz` files, one FID-stat `.npz`, notebooks, and a `.git` directory. It contains no `.pt`, `.pth`, `.ckpt`, `.safetensors`, `.h5`, `.hdf5`, score CSV, ROC CSV, result JSON, metric JSON, or committed output directory. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for execution. The supplement provides training scripts, but no frozen DDPM/LDM target checkpoint with verifiable size/hash/training binding. LDM scripts require `runwayml/stable-diffusion-v1-5` plus local Pokemon fine-tuning. |
| Exact member split | Partial pass. DDPM SecMIA split-index files are public for CIFAR10/CIFAR100/STL10/Tiny-ImageNet. LDM/Pokemon membership still depends on local dataset layout, generated captions, and training scripts. |
| Exact nonmember split | Partial pass for DDPM split indices; fail for an executable defense replay because no target checkpoint and no score artifacts are bound to the indices. |
| Query/response or score coverage | Fail. The release ships no defended/undefended score rows, generated response packet, ROC arrays, attack metric JSON, or ready verifier output. |
| Mechanism delta | Pass as a defense reference. DualMD/DistillMD is a distinct training-time disjoint split / distillation defense, not another denoising-loss, CommonCanvas, MIDST, Beans, or Fashion-MNIST variant. |
| Current DiffAudit fit | Defense watch-plus. The supplement is stronger than paper-source-only because it includes code and split indices, but it still requires dataset/model acquisition and training from scratch. |
| Download justification | Fail. Downloading Pokemon/Stable Diffusion/CIFAR/STL/Tiny-ImageNet assets would start a reproduction project and still would not recover committed score artifacts. |
| GPU release | Fail. There is no frozen checkpoint, reusable result packet, metric contract, or stop condition that justifies GPU execution in the current roadmap cycle. |

## Decision

`supplement-code-public / split-index-files-present /
checkpoint-and-score-artifacts-missing / no download / no GPU release / no
admitted row`.

DualMD/DistillMD should be retained as a diffusion-model defense watch-plus
item. It materially improves the paper-index state from "no public repository
found" to "OpenReview supplementary code and DDPM split indices are public",
but it does not become a DiffAudit execution target because it does not ship
checkpoint-bound defended/undefended MIA scores, ROC arrays, metric JSON,
generated response packets, or a ready verifier.

Smallest valid reopen condition:

- Public DualMD/DistillMD DDPM or LDM checkpoint bundles with size/hash and
  training/split binding;
- Matching member and nonmember manifests for the exact checkpoint;
- Raw defended and undefended member/nonmember scores, ROC arrays, metric JSON,
  generated response packets, or a bounded verifier command that reads public
  artifacts without retraining or acquiring datasets from scratch; and
- A consumer-boundary decision that defines whether disjoint-training defense
  rows are admitted defense evidence or remain survey/limitation material.

Stop condition:

- Do not download the SharePoint Pokemon payload, Stable Diffusion weights,
  CIFAR/CIFAR100/STL10/Tiny-ImageNet datasets, or any DualMD/DistillMD
  checkpoints from this gate.
- Do not run `train.sh`, `train_dual.sh`, `distill.sh`,
  `train-ldm.sh`, `train-dual.sh`, `distill-ldm.sh`, SecMIA/PIA scripts,
  black-box attack scripts, or memorization notebooks in the current roadmap
  cycle.
- Do not promote DualMD/DistillMD into Platform/Runtime defense rows, product
  copy, recommendation logic, or the admitted evidence bundle.

## Reflection

This gate found a real public supplement that the older paper index had not
captured, so it changed artifact knowledge rather than adding process around a
known dead end. The scientific decision still stays conservative: code and
split indices are not enough to justify a reproduction project when checkpoints
and score artifacts are absent. Current slots remain `active_gpu_question =
none`, `next_gpu_candidate = none`, and `CPU sidecar = none selected after
DualMD / DistillMD defense artifact gate`.

## Platform and Runtime Impact

None. DualMD/DistillMD remains Research-only defense watch-plus evidence.
Platform and Runtime continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
