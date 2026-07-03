# R125 DreamBooth Forensics Asset Verdict

> Date: 2026-05-14
> Status: course-notebook / GDrive-private-target / artifact-incomplete / no download / no GPU release

## Question

Does `ronketer/diffusion-membership-inference` provide a clean non-duplicate
Lane A asset for DiffAudit: target model identity, exact member/nonmember
split, query/response or score coverage, provenance, and a bounded scoring
contract?

This is an asset gate, not a reproduction attempt. No SD1.5 weights, notebook
outputs, GDrive artifacts, or report assets were downloaded beyond public
GitHub metadata/notebook inspection.

## Candidate

| Field | Value |
| --- | --- |
| Public repo | `https://github.com/ronketer/diffusion-membership-inference` |
| Default branch | `main` |
| Checked date | 2026-05-14 |
| GitHub license metadata | none |
| Last push | `2026-04-14T16:20:26Z` |
| Repo description | none |
| Domain | Stable Diffusion v1.5 DreamBooth/LoRA personalization, SDEdit, and reconstruction-MSE forensics |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| GitHub root tree | The repository contains notebooks, a course PDF, `main.py`, `pyproject.toml`, a report PDF, and report images. It does not contain released LoRA/checkpoint weights, a target model artifact, or a machine-readable member/nonmember manifest. |
| `README.md` | Describes a Colab/GPU exploratory pipeline for Stable Diffusion v1.5 DreamBooth + LoRA, SDEdit, and a lightweight membership-forensics probe using reconstruction MSE. |
| `README.md` setup | Requires Hugging Face access to `runwayml/stable-diffusion-v1-5` and asks the user to run notebook sections in Google Colab. |
| `README.md` reported threshold | Reports a forensics threshold around `0.085`, with training MSE around `0.07` and unseen MSE around `0.11`. |
| `ex5.ipynb` training cells | Pulls Hugging Face Diffusers DreamBooth LoRA training code, uploads or snapshots a dataset, and saves checkpoints under Colab/GDrive paths such as `/content/gdrive/MyDrive/IMPR_Ex5/rubber_duck_outputs/checkpoint-*`. |
| `ex5.ipynb` forensics cell | Uses `base_path = "/content/gdrive/MyDrive/IMPR_Ex5/ex5_forensics_supplementary"`, `forensics_model_path = f"{base_path}/checkpoint-1500"`, and scans images from the same private GDrive folder. |
| `ex5.ipynb` forensics output | Shows six sorted scores: `e.png = 0.06714`, `b.png = 0.06812`, `f.png = 0.07269`, `a.png = 0.09753`, `d.png = 0.10400`, `c.png = 0.11230`. |
| `reports/images/` | Contains illustrative report images and figures, including training-loss and forensics-score plots, but not the private `a.png` through `f.png` query set, not the `checkpoint-1500` LoRA, and not a score manifest with labels. |
| `main.py` | Placeholder that only prints `Hello from ex05!`. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail. The effective target is SD1.5 plus a private Colab/GDrive LoRA checkpoint at `checkpoint-1500`; the checkpoint is not released in the GitHub repo. |
| Exact member split | Fail. The notebook output implies three low-MSE training images, but the repository does not publish a machine-readable member list or the exact private training images. |
| Exact nonmember split | Fail. The notebook output implies three high-MSE unseen images, but the repository does not publish a nonmember manifest or the exact private holdout images. |
| Query/response or score coverage | Partial only. The notebook embeds six scalar MSE values, but no reusable query images, labels, target checkpoint, generated responses, or score JSON are released. |
| Scoring contract | Partial pass. The code defines a reconstruction-MSE probe at timestep `500` with seed `42`, but it depends on private GDrive artifacts and a Colab execution state. |
| Mechanism delta | Partial pass. DreamBooth/LoRA personalization forensics is adjacent to Beans member-LoRA and MIA_SD fine-tuned SD, but the notebook-specific thresholding route is not an admitted or runnable DiffAudit packet. |
| GPU release | Fail. There is no public target LoRA, exact split, query package, or frozen `25/25` or `50/50` scoring command. |

## Decision

`course-notebook / GDrive-private-target / artifact-incomplete / no download /
no GPU release`.

`ronketer/diffusion-membership-inference` is useful as a small public example
of DreamBooth/LoRA reconstruction-MSE forensics, but it is not a clean Lane A
second asset. The decisive blocker is not GPU capacity. The blocker is that the
target LoRA checkpoint and forensics query set live in private Colab/GDrive
paths, while the public repo only provides notebooks, report media, and six
embedded scalar scores.

Do not download SD1.5 weights, recreate the private DreamBooth training run,
scrape report images into a pseudo-split, or treat the six embedded MSE values
as an admitted score packet. Reopen only if a public-safe artifact appears
with:

- a hashable LoRA or fine-tuned SD checkpoint,
- exact per-sample member and nonmember manifests,
- the corresponding query images or generated response package,
- and a bounded scorer command whose first packet closes on `AUC < 0.60` or
  near-zero strict-tail recovery.

## Platform and Runtime Impact

None. This is Research-only watch evidence. It is not admitted evidence, not a
Platform product row, and not a Runtime schema input.
