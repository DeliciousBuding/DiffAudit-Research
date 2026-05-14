# SecMI-LDM Asset Verdict

> Date: 2026-05-14
> Status: SecMI support-family / public download links present / no independent second asset / no download / no GPU release

## Question

Does `jinhaoduan/SecMI-LDM` provide a clean non-duplicate Lane A asset for
DiffAudit: target model identity, exact member/nonmember split, query/response
coverage, provenance, and a bounded scoring contract?

This is an asset gate, not a reproduction attempt. No checkpoint, dataset, or
large artifact was downloaded. A correction pass was added after confirming
the default-branch README on `secmi-ldm`.

## Candidate

| Field | Value |
| --- | --- |
| Public repo | `https://github.com/jinhaoduan/SecMI-LDM` |
| Default branch | `secmi-ldm` |
| Checked commit | `83eff37e06aadf078a79755164a5cf531bd34b04` |
| GitHub license metadata | `Apache-2.0` |
| Description | `SecMI on Latent Diffusion Model (LDM)` |
| Prior DiffAudit relation | Same SecMI author family as the already tracked SecMI supporting-reference line |
| README blob | `1e6b52e64ea0b1b64e08af2e28162d55fd1d99c2`, `2335` bytes |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| GitHub repo metadata | The repository is a fork-style codebase with default branch `secmi-ldm`, last pushed at `2024-03-04T18:55:55Z`. |
| Root `README.md` on `secmi-ldm` | The README is project-specific: it says this code implements SecMI on conditioned generation, including fine-tuned Stable Diffusion and vanilla Stable Diffusion, on top of `diffusers-0.11.1`. |
| README dataset link | The README provides a SharePoint `datasets.zip` link for Pokémon, LAION 2.5k, and COCO2017 validation 2.5k. A HEAD probe returned `302` to a OneDrive path named `datasets.zip`; the zip was not downloaded. |
| README checkpoint link | The README provides a SharePoint `sd-pokemon-checkpoint.zip` link. A HEAD probe returned `302` to a OneDrive path named `sd-pokemon-checkpoint.zip`; the zip was not downloaded. |
| Root tree | Most files are a Diffusers source tree. The only project-specific public entries found at the top-level scan were `scripts/secmi_ldm_pokemon.sh`, `scripts/secmi_sd_laion.sh`, and `src/mia/secmi.py`. |
| `scripts/secmi_ldm_pokemon.sh` | Invokes `python -m src.mia.secmi --dataset pokemon --dataset-root ./datasets --ckpt-path ./checkpoints/sd-pokemon-checkpoint`; it assumes local dataset and checkpoint directories. |
| `scripts/secmi_sd_laion.sh` | Invokes the same runner with `--dataset laion`, local `./datasets`, and `runwayml/stable-diffusion-v1-5`; it does not provide a member/nonmember response packet. |
| `src/mia/secmi.py` | Loads Pokémon with `load_from_disk(dataset_root/pokemon)`, COCO with `coco_split.yaml`, and LAION from local `laion-2.5k/images` plus `captions.npy`; these artifacts are referenced as local files, not published manifests. |
| `src/mia/secmi.py` checkpoint handling | The script hardcodes `/home/jd3734@drexel.edu/workspace/SecMI-LDM/checkpoints/sd-pokemon-checkpoint` before running, overriding the CLI checkpoint path. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Partial pass. The README exposes a Pokémon fine-tuned SD checkpoint download link, but this remains the authors' SecMI LDM target rather than an independent second-asset family for DiffAudit. |
| Exact member split | Partial pass. The README exposes a dataset bundle link and the LAION-vs-COCO script defines member/nonmember roles, but this is still a SecMI reproduction/support packet, not a fresh non-duplicate Lane A asset. |
| Exact nonmember split | Partial pass. COCO validation and LAION/Pokémon split assets appear to be in the downloadable dataset bundle, but no download was needed for the current support-family gate. |
| Query/response coverage | Fail for DiffAudit second-asset use. The repository computes reverse-denoise scores from images/checkpoints and does not publish generated responses or a reusable black-box query/response packet. |
| Scoring contract | Pass as SecMI support. `src/mia/secmi.py` defines a SecMI-style reverse-denoise score and README scripts describe Pokémon fine-tuned SD and vanilla SD over LAION/COCO. |
| Mechanism delta | Fail for Lane A. This is a SecMI LDM variant in the same author/support family as the existing SecMI reference, not a clean second asset independent from the already tracked gray-box SecMI line. |
| GPU release | Fail. The gate being evaluated is clean Lane A acquisition, and this candidate is same-family SecMI support; a full download or GPU rerun would replay admitted/support-family provenance instead of changing the current Research decision. |

## Decision

`SecMI support-family / public download links present / no independent second
asset / no download / no GPU release`.

`jinhaoduan/SecMI-LDM` is useful as a related code reference for SecMI-style
latent-diffusion scoring, but it is not a clean Lane A second asset. The public
surface is a Diffusers fork plus SecMI LDM scripts, and the default-branch
README does provide SharePoint download links for the dataset bundle and
Pokémon fine-tuned SD checkpoint. That improves the reproduction/support value,
but it does not change the roadmap decision: this is the same author/paper
SecMI support family already tracked by DiffAudit, not a non-duplicate second
membership asset with a new mechanism or product-facing response contract.

Do not download the SharePoint dataset/checkpoint zip, scrape LAION/COCO assets,
or train/recreate the target from this repository inside the current roadmap
cycle. Reopen only if the task is explicitly framed as SecMI-LDM reproducibility
maintenance, or if a genuinely independent public-safe artifact appears with:

- a hashable LDM checkpoint or deterministic target recreation recipe,
- exact per-sample member and nonmember manifests,
- generated responses or a deterministic query/response package,
- and a bounded `25/25` or `50/50` scorer with an `AUC < 0.60` or near-zero
  strict-tail stop gate.

## Platform and Runtime Impact

None. This is Research-only watch/support evidence. It is not admitted
evidence, not a Platform product row, and not a Runtime schema input.
