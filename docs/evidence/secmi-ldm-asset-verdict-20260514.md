# SecMI-LDM Asset Verdict

> Date: 2026-05-14
> Status: diffusers-fork / support-family / artifact-incomplete / no download / no GPU release

## Question

Does `jinhaoduan/SecMI-LDM` provide a clean non-duplicate Lane A asset for
DiffAudit: target model identity, exact member/nonmember split, query/response
coverage, provenance, and a bounded scoring contract?

This is an asset gate, not a reproduction attempt. No checkpoint, dataset, or
large artifact was downloaded.

## Candidate

| Field | Value |
| --- | --- |
| Public repo | `https://github.com/jinhaoduan/SecMI-LDM` |
| Default branch | `secmi-ldm` |
| Checked commit | `83eff37e06aadf078a79755164a5cf531bd34b04` |
| GitHub license metadata | `Apache-2.0` |
| Description | `SecMI on Latent Diffusion Model (LDM)` |
| Prior DiffAudit relation | Same SecMI author family as the already tracked SecMI supporting-reference line |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| GitHub repo metadata | The repository is a fork-style codebase with default branch `secmi-ldm`, last pushed at `2024-03-04T18:55:55Z`. |
| Root `README.md` on `secmi-ldm` | The README is the stock Hugging Face Diffusers README, not a project-specific artifact card or reproduction contract. |
| Root tree | Most files are a Diffusers source tree. The only project-specific public entries found at the top-level scan were `scripts/secmi_ldm_pokemon.sh`, `scripts/secmi_sd_laion.sh`, and `src/mia/secmi.py`. |
| `scripts/secmi_ldm_pokemon.sh` | Invokes `python -m src.mia.secmi --dataset pokemon --dataset-root ./datasets --ckpt-path ./checkpoints/sd-pokemon-checkpoint`; it assumes local dataset and checkpoint directories. |
| `scripts/secmi_sd_laion.sh` | Invokes the same runner with `--dataset laion`, local `./datasets`, and `runwayml/stable-diffusion-v1-5`; it does not provide a member/nonmember response packet. |
| `src/mia/secmi.py` | Loads Pokémon with `load_from_disk(dataset_root/pokemon)`, COCO with `coco_split.yaml`, and LAION from local `laion-2.5k/images` plus `captions.npy`; these artifacts are referenced as local files, not published manifests. |
| `src/mia/secmi.py` checkpoint handling | The script hardcodes `/home/jd3734@drexel.edu/workspace/SecMI-LDM/checkpoints/sd-pokemon-checkpoint` before running, overriding the CLI checkpoint path. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail. The Pokémon LDM target is a local `sd-pokemon-checkpoint` path, not a released hashable checkpoint or deterministic target recreation bundle. |
| Exact member split | Fail. The Pokémon, COCO, and LAION loaders reference local datasets/split files but do not publish a per-sample target-training membership manifest. |
| Exact nonmember split | Fail. COCO `coco_split.yaml` and local LAION/Pokémon assets are assumed, not released as a fixed DiffAudit-ready split package. |
| Query/response coverage | Fail. The repository computes reverse-denoise scores from local samples and checkpoints; it does not publish generated responses or a reusable query/response packet. |
| Scoring contract | Partial pass. `src/mia/secmi.py` defines a SecMI-style reverse-denoise score, but the target artifacts and split inputs needed to run it are not public. |
| Mechanism delta | Fail for Lane A. This is a SecMI LDM variant in the same author/support family as the existing SecMI reference, not a clean second asset independent from the already tracked gray-box SecMI line. |
| GPU release | Fail. There is no frozen public target, split, response package, metric command, or stop condition. |

## Decision

`diffusers-fork / support-family / artifact-incomplete / no download / no GPU
release`.

`jinhaoduan/SecMI-LDM` is useful as a related code reference for SecMI-style
latent-diffusion scoring, but it is not a clean Lane A second asset. The public
surface is a Diffusers fork plus a small SecMI runner that assumes local
datasets, local split files, and a local Pokémon checkpoint. This repeats the
existing SecMI support-family route instead of providing an independently
verifiable target/split/query-response asset.

Do not download or reconstruct the Pokémon checkpoint, scrape LAION/COCO assets,
or train/recreate the target from this repository inside the current roadmap
cycle. Reopen only if a public-safe artifact appears with:

- a hashable LDM checkpoint or deterministic target recreation recipe,
- exact per-sample member and nonmember manifests,
- generated responses or a deterministic query/response package,
- and a bounded `25/25` or `50/50` scorer with an `AUC < 0.60` or near-zero
  strict-tail stop gate.

## Platform and Runtime Impact

None. This is Research-only watch/support evidence. It is not admitted
evidence, not a Platform product row, and not a Runtime schema input.
