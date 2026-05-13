# MIA_SD Face LDM Asset Verdict

> Date: 2026-05-13
> Status: code-and-result-artifacts / private-images-missing / no download / no GPU release

## Question

Does `osquera/MIA_SD` provide a clean second membership asset for DiffAudit:
released target identity, per-sample member/nonmember split, query/response
coverage, and a runnable scoring contract?

This is a Lane A asset gate, not a reproduction attempt. No model weights,
images, or large result arrays were downloaded.

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| `https://github.com/osquera/MIA_SD` | Public repository exists at HEAD `513084a3fbde7ad8e51500711346dd892cacdff2`; repository metadata has no license. |
| root `README.md` | The code runs `experiment.py --run_all`, but explicitly says the images used are not published and must be added for the scripts to run. |
| root listing | Contains scripts, plots, result files, CLIP embedding arrays, `dtu-400-target-loss.csv`, and `images_attack_model/*` result folders. |
| `target_model/README.md` | Describes how to fine-tune SD1.5 on user-provided images, auto-caption them with BLIP, and run inference; it does not provide a released target checkpoint. |
| `target_model/fine_tune.sh` | Uses `runwayml/stable-diffusion-v1-5`, placeholder `TRAIN_PATH`, placeholder `OUT_PATH`, 400 epochs, and seed `0`; no frozen dataset path or published checkpoint artifact is provided. |
| `experiment.py` | Expects local `images_attack_model/<experiment>/0` and `1` folders plus generated and test folders such as `DTU_gen_vs_AAU_gen_v1`, `DTU_vs_AAU_unseen_test`, and `DTU_400_vs_Gen`; these are not a published per-sample query/response manifest. |
| `get_dtu_img.py` | Scrapes DTU staff images from a live website, confirming the training/query image source is dynamic and not a frozen released artifact. |
| `dtu-400-target-loss.csv` | Contains a Weights & Biases-style loss trace with columns such as `Step` and `train_loss`; it is not a per-sample member/nonmember score packet. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Not released. The repo contains fine-tuning scripts, not a checkpoint or hashable target model artifact. |
| Member split | Not released. The intended DTU/LFW/AAU images are local/private or scraped; no exact member IDs are published. |
| Nonmember split | Not released. Test folder names appear in code, but no per-sample nonmember manifest is published. |
| Query/response coverage | Not released. Generated outputs and image folders required by `experiment.py` are not included as a reusable query/response package. |
| License/provenance | Blocked. The repository has no license, and the images are explicitly unpublished. |
| Minimal scorer contract | Not ready. Existing CSV/plot/pickle artifacts are result traces, not a reusable packet with exact sample identities. |

## Decision

`code-and-result-artifacts / private-images-missing / no download / no GPU release`.

`MIA_SD` is a useful related code reference for face-image membership
experiments against fine-tuned Stable Diffusion, but it is not a clean asset
for DiffAudit. The missing blocker is not local CUDA capacity. The blocker is
that the released material lacks:

- a hashable target checkpoint,
- exact target member identities,
- exact held-out nonmember identities,
- a public-safe query/response package,
- a license/provenance boundary suitable for public documentation.

Do not scrape DTU/AAU/LFW images, fine-tune SD1.5 for 400 epochs, reconstruct
the private folders, or build a scorer from the committed plots/result traces.
Reopen only if the authors publish a checkpoint plus an exact split manifest or
a public-safe query/response packet.

## Reflection

This was a useful Lane A check because it avoided repeating the Beans-style
pseudo-membership error. The candidate looks closer to a real fine-tuned face
membership scenario than generic model cards, but it fails at the same core
artifact boundary: target membership identities are not publicly reproducible.

## Platform and Runtime Impact

None. This is Research-only related-method evidence. It is not admitted
evidence, not a product row, and not a Runtime schema input.
