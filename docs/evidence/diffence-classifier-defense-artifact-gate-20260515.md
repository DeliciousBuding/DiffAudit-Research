# DIFFENCE Classifier-Defense Artifact Gate

> Date: 2026-05-15
> Status: classifier-defense-code-public / split-index-files-present / diffusion-as-preprocessor-not-target / score-artifacts-missing / no download / no GPU release / no admitted row

## Question

Can the official `SPIN-UMass/Diffence` public surface for `DIFFENCE: Fencing
Membership Privacy With Diffusion Models` become the next bounded DiffAudit
defense row, diffusion-model MIA replay, or GPU execution target?

This was an artifact gate only. It inspected GitHub metadata, a shallow Git
tree, README instructions, split/index files, config files, and MIA evaluation
code. No Google Drive model folder, dataset payload, diffusion checkpoint,
classifier checkpoint, generated reconstruction packet, or score output was
downloaded or executed.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `DIFFENCE: Fencing Membership Privacy With Diffusion Models` / NDSS 2025 |
| Paper-index entry | `references/materials/paper-index.md` records DIFFENCE as an inference-side diffusion reconstruction defense for classifier MIA |
| Repository | `https://github.com/SPIN-UMass/Diffence` |
| Checked commit | `2f7bb87dee863538f902098c84d0fe04ddfdcc3f` |
| Latest push observed | `2024-09-06T03:05:08Z` |
| License | MIT |
| GitHub releases | none observed |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| `README.md` | Identifies the repo as the code for the NDSS 2025 paper and describes DIFFENCE as a plug-and-play defense for undefended and defended models. The workflow asks users to partition datasets, download pretrained diffusion checkpoints from Google Drive, download target classifier models from Google Drive, and then run MIA evaluation scripts. |
| `download_models.py` | Defines Google Drive folders for `cifar10`, `cifar100`, and `svhn` diffusion and target model downloads via `gdown.download_folder`. No model files, hashes, or score packets are committed. |
| Dataset folders | `cifar10/`, `cifar100/`, and `svhn/` provide training, defense, and evaluation code for image classifiers, not a diffusion-model target membership contract. |
| `cifar10/cifar_shuffle.pkl`, `cifar100/cifar_shuffle.pkl`, `svhn/svhn_shuffle.pkl` | Commit deterministic shuffle arrays for dataset partitioning (`50,000` CIFAR entries and `73,257` SVHN entries). These are useful split-index evidence, but they are not bound to committed classifier checkpoints or score artifacts. |
| `*/diff_defense/diff_ckpt/CIFAR10_train_ratio0.5.npz` and `CIFAR100_train_ratio0.5.npz` | Commit `mia_train_idxs` and `mia_eval_idxs` arrays of shape `25,000` each plus a scalar `ratio`. These are split-index artifacts for the defense workflow, not released MIA score rows or a DiffAudit diffusion target packet. |
| `data_partition.py` | Downloads public datasets with torchvision and writes local `partition/*.npy` arrays from the committed shuffle. This is a reproducible partition procedure, but it still requires dataset acquisition and local generation of payloads. |
| `evaluate_MIAs/evaluate_mia.sh` | Generates model outputs with and without DIFFENCE, then redirects `dist_attack.py` output into `evaluate_MIAs/results/<defense>` and `<defense>_w_Diffence`. No such result files are committed. |
| `evaluate_MIAs/dist_attack.py` | Computes ROC/AUC and low-FPR/TNR fields from locally generated logits and prints results. It expects generated `.npz` output files and does not ship reusable committed score arrays, ROC CSVs, or metric JSON. |
| `evaluate_MIAs/dist_data.py` | Loads a target classifier checkpoint from `final-all-models/.../*.pth.tar`, constructs member/nonmember tensors from local dataset partitions, and wraps the classifier with DIFFENCE when `--diff` is used. |
| Recursive tree | The repo contains code, configs, small split index files, and Python bytecode caches. It does not commit target classifier checkpoints, diffusion model checkpoints, generated defended/undefended logits, MIA score rows, ROC arrays, metric JSON, or ready verifier outputs. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for DiffAudit execution. DIFFENCE's protected target is an image classifier, with pretrained classifier checkpoints supplied through Google Drive. Diffusion is a purification/pre-inference defense component, not the audited generative model target. |
| Exact member split | Partial pass. CIFAR/SVHN shuffle and `mia_train_idxs` arrays exist, but they are not bound to committed target classifier checkpoints, generated logits, or score packets. |
| Exact nonmember split | Partial pass. `mia_eval_idxs` and test-set based nonmember construction are visible in code, but score artifacts and checkpoint bindings are missing. |
| Query/response or score coverage | Fail. Results are generated locally into `evaluate_MIAs/results`; no defended/undefended logits, scores, ROC arrays, metric JSON, or paper-table replay packet is committed. |
| Mechanism delta | Pass as a related defense reference. DIFFENCE is a distinct inference-side diffusion reconstruction defense, but its threat model is classifier MIA rather than membership inference against a diffusion generator. |
| Current DiffAudit fit | Defense related-method / watch-plus. It can inform defense discussion, but it is not a Platform/Runtime row, not an admitted diffusion-model defense row, and not a GPU replay target. |
| Download justification | Fail. Downloading Google Drive checkpoints would start a classifier-defense reproduction and still would not recover committed score artifacts or a diffusion-model membership contract. |
| GPU release | Fail. The repo lacks frozen public checkpoints with hashes, committed score artifacts, a bounded verifier, and a DiffAudit consumer-boundary decision for classifier-defense rows. |

## Decision

`classifier-defense-code-public / split-index-files-present /
diffusion-as-preprocessor-not-target / score-artifacts-missing / no download /
no GPU release / no admitted row`.

DIFFENCE should be retained as a classifier-defense related-method watch-plus
item. It is stronger than paper-source-only because the official repo exposes
code, configs, and small split-index files. It does not become a DiffAudit
execution target because the protected model is a classifier, the diffusion
model is an input-side defense component, and the public release does not ship
checkpoint-bound defended/undefended MIA score artifacts.

Smallest valid reopen condition:

- Public classifier and diffusion checkpoint bundles with size/hash/training
  binding;
- Matching member/nonmember manifests for the exact target checkpoint;
- Raw defended and undefended member/nonmember logits or score rows, ROC arrays,
  metric JSON, or a bounded verifier that reads public artifacts without
  retraining or acquiring datasets from scratch; and
- An explicit consumer-boundary decision that classifier-defense evidence is in
  scope for DiffAudit, separate from diffusion-generator membership rows.

Stop condition:

- Do not download DIFFENCE Google Drive diffusion or target model folders.
- Do not download CIFAR/SVHN payloads, train classifiers, train diffusion
  models, generate DIFFENCE reconstructions, or run MIA evaluation scripts in
  the current roadmap cycle.
- Do not promote DIFFENCE into Platform/Runtime defense rows, product copy,
  recommendation logic, or the admitted evidence bundle.

## Reflection

This gate prevents a subtle scope error. The title says "with Diffusion
Models", but the audited target in DIFFENCE is a classifier; diffusion is the
defense transformation before classifier inference. That makes it useful for
defense literature context, not a clean second diffusion-model membership asset
or admitted defense row. Current slots remain `active_gpu_question = none`,
`next_gpu_candidate = none`, and `CPU sidecar = none selected after DIFFENCE
classifier-defense artifact gate`.

## Platform and Runtime Impact

None. DIFFENCE remains Research-only classifier-defense watch-plus evidence.
Platform and Runtime continue consuming only the admitted `recon / PIA baseline
/ PIA defended / GSA / DPDM W-1` set.
