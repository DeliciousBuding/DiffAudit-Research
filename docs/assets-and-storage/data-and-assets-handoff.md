# Data And Assets Setup Guide

This document answers the most common questions when onboarding:

- Where datasets, weights, and supplementary files come from
- Where to put them after download
- How to match local paths to repository commands
- How to verify your local layout matches the current project

## 1. Canonical Layout

Default directory layout:

```text
<DIFFAUDIT_ROOT>\
  Research\        # this git repo
  Download\        # local raw datasets / weights / supplementary files
```

`Download\` is not part of the `Research` git repo. It holds large files, license-restricted files, and re-downloadable weights and archives.

`<DIFFAUDIT_ROOT>` is your local project root. It can be anywhere; the important thing is that `Research/` and `Download/` keep their relative roles.

If your machine has a different path, that is fine as long as the relative roles stay the same:

- `Research\external\` holds external code clones only
- `Research\third_party\` holds minimal vendored code only
- `Download\` holds raw downloads
- `Research\workspaces\<track>\assets\` holds normalized track entry points
- `Research\workspaces\<track>\runs\` holds experiment results
- `Research\outputs\` holds local temporary outputs, not used for delivery

Detailed rules are in [storage-boundary.md](storage-boundary.md).

If you want to know why some `Download/` directory names look like asset names and others look like source names, see [download-naming-policy.md](download-naming-policy.md).

## 2. Fastest Way To Match Our Assets

If the team maintains a shared asset mirror, the fastest approach is to copy the whole directory:

```powershell
Copy-Item -Recurse \\YOUR_ASSET_MIRROR\DiffAudit\Download $env:DIFFAUDIT_ROOT\Download
```

If you have not set the environment variable, replace `$env:DIFFAUDIT_ROOT` with your actual absolute path.

After copying, confirm at least these entries exist:

```text
Download\black-box\supplementary\recon-assets\
Download\black-box\supplementary\clid-mia-supplementary\
Download\gray-box\weights\secmi-cifar-bundle\
Download\shared\datasets\cifar-10-python.tar.gz
Download\shared\datasets\celeba\
Download\shared\weights\stable-diffusion-v1-5\
Download\shared\weights\clip-vit-large-patch14\
Download\shared\weights\blip-image-captioning-large\
Download\shared\weights\google-ddpm-cifar10-32\
```

If you cannot copy, download in `first-wave` order from [research-download-master-list.md](research-download-master-list.md). Some assets require login, license acceptance, or author approval. The repository records sources and target directories but cannot commit all large files into git.

Paper PDFs and DOCX context files follow the same rule: the repository records
metadata in `references/materials/manifest.csv`, while local copies belong in a
team asset mirror or an external path such as
`Download\shared\papers\<track>\`. Do not expect GitHub to contain the paper
binaries.

Generated experiment artifacts follow the same rule. GitHub keeps sanitized
summaries and reports; generated images, tensor score packets, runtime job queue
dumps, checkpoints, and split `.npz` files belong in a team mirror, ignored
workspace path, or the local archive. Raw downloaded datasets,
weights, and supplementary files belong in `Download/`; generated run payloads
do not. The repository-root `Research/outputs/` directory is also local scratch
space; promote durable metrics into workspace result notes or `summary.json`
files before committing.

For a local machine cleanup audit, run:

```powershell
python -X utf8 scripts/audit_local_storage.py
```

The script is dry-run by default. It can also relocate ignored local-only
payloads to `Download/` or
`<DIFFAUDIT_ROOT>\Archive\research-local-artifacts\` when run with
`--execute`.

## 3. First-Wave Asset List

New machines should prepare these assets first. They cover most current verification paths:

| Asset ID | What | Source | Destination |
|---|---|---|---|
| `SH-DS-01` | CIFAR-10 archive | https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz | `Download\shared\datasets\cifar-10-python.tar.gz` |
| `SH-DS-02/03` | CelebA images + annotations | https://mmlab.ie.cuhk.edu.hk/projects/CelebA.html | `Download\shared\datasets\celeba\` |
| `SH-WT-01` | Stable Diffusion v1.5 | https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5 | `Download\shared\weights\stable-diffusion-v1-5\` |
| `SH-WT-02` | CLIP ViT-L/14 | https://huggingface.co/openai/clip-vit-large-patch14 | `Download\shared\weights\clip-vit-large-patch14\` |
| `SH-WT-03` | BLIP large | https://huggingface.co/Salesforce/blip-image-captioning-large | `Download\shared\weights\blip-image-captioning-large\` |
| `SH-WT-04` | DDPM CIFAR-10 32 | https://huggingface.co/google/ddpm-cifar10-32 | `Download\shared\weights\google-ddpm-cifar10-32\` |
| `GB-WT-01` | SecMI CIFAR bundle | see [research-download-master-list.md](../assets-and-storage/research-download-master-list.md) | `Download\gray-box\weights\secmi-cifar-bundle\` |
| `GB-SUP-02` | SecMI member split `.npz` files | full SecMI clone or team asset mirror | `Download\gray-box\supplementary\secmi-member-splits\` |
| `BB-SUP-02` | CLiD supplementary mirror | paper supplementary / manual bundle | `Download\black-box\supplementary\clid-mia-supplementary\` |

The current recon bundle is expected under:

```text
Download\black-box\supplementary\recon-assets\
```

If you do not have that directory, ask for the project asset mirror or rebuild it from the release/source noted in [recon-public-asset-mapping.md](recon-public-asset-mapping.md).

## 4. External Code Clones

These are code clones, not data directories. They belong under `Research\external\`:

```powershell
git clone --depth 1 https://github.com/kong13661/PIA.git external/PIA
git clone --depth 1 https://github.com/zhaisf/CLiD external/CLiD
git clone --depth 1 https://github.com/py85252876/Reconstruction-based-Attack external/Reconstruction-based-Attack
git clone --depth 1 https://github.com/py85252876/GSA.git external/GSA
git clone --depth 1 https://github.com/facebookresearch/DiT.git external/DiT
git clone --depth 1 https://github.com/nv-tlabs/DPDM.git external/DPDM
```

`external/` is ignored by git. Do not put datasets or model weights there. Use
shallow clones by default on new machines; fetch full upstream history only
when a specific audit needs it.

## 5. Bind Local Paths

After assets are present, create your local path config:

```powershell
Copy-Item configs/assets/team.local.template.yaml configs/assets/team.local.yaml
```

Fill these fields first:

```yaml
repo:
  research_root: /absolute/path/to/DiffAudit/Research
  download_root: /absolute/path/to/DiffAudit/Download

shared:
  cifar10_archive: /absolute/path/to/DiffAudit/Download/shared/datasets/cifar-10-python.tar.gz
  celeba_root: /absolute/path/to/DiffAudit/Download/shared/datasets/celeba
  sd15_model_dir: /absolute/path/to/DiffAudit/Download/shared/weights/stable-diffusion-v1-5
  clip_model_dir: /absolute/path/to/DiffAudit/Download/shared/weights/clip-vit-large-patch14
  blip_model_dir: /absolute/path/to/DiffAudit/Download/shared/weights/blip-image-captioning-large
  ddpm_cifar10_model_dir: /absolute/path/to/DiffAudit/Download/shared/weights/google-ddpm-cifar10-32
```

Windows, Linux, and macOS each use their own absolute path format. The key point is using absolute paths, not a specific drive letter or user directory.

Then render local configs:

```powershell
python scripts/render_team_local_configs.py
```

`configs/assets/team.local.yaml` is ignored by git. Do not commit personal absolute paths.

## 6. Verification Commands

Run these after environment setup and local path binding:

```powershell
python scripts/verify_env.py
python -m diffaudit --help
python scripts/render_team_local_configs.py
```

Basic asset checks:

```powershell
conda run -n diffaudit-research python -m diffaudit probe-pia-assets --config configs/attacks/pia_plan.yaml --member-split-root external/PIA/DDPM
conda run -n diffaudit-research python -m diffaudit probe-gsa-assets --repo-root external/GSA --assets-root workspaces/white-box/assets/gsa
conda run -n diffaudit-research python -m diffaudit audit-recon-public-bundle --bundle-root "$env:DIFFAUDIT_ROOT\Download\black-box\supplementary\recon-assets\ndss-2025-blackbox-membership-inference-fine-tuned-diffusion-models"
```

Expected result:

- environment commands exit successfully
- `python -m diffaudit --help` lists all CLI commands
- asset probes either report `ready` or name the exact missing local path

## 7. If You Are Taking Over The Research Work

After the machine can run commands, read in this order:

1. [README.md](../../README.md)
2. [teammate-setup.md](../start-here/teammate-setup.md)
3. [comprehensive-progress.md](../internal/comprehensive-progress.md)
4. [reproduction-status.md](../evidence/reproduction-status.md)
5. [mainline-narrative.md](../internal/mainline-narrative.md)
6. [storage-boundary.md](storage-boundary.md)
7. [research-download-master-list.md](../assets-and-storage/research-download-master-list.md)

Current rule of thumb:

- use `Download\` to get the same raw data and weights
- use `team.local.yaml` to bind your machine paths
- use `workspaces/*/assets` manifests as the project-recognized asset contracts
- use `workspaces/*/runs` and implementation notes as experiment results, not as raw dataset storage
- do not rely on `Research/outputs/` for delivery; it is ignored local scratch
