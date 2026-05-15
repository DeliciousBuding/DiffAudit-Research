# CPSample Defense Artifact Gate

> Date: 2026-05-15
> Status: ICLR OpenReview code supplement / defense watch-plus / score-text
> fragments present / checkpoint-split artifacts missing / no download /
> no GPU release / no admitted row

## Question

Does CPSample provide a current DiffAudit defense-aware membership-inference
asset, or should it remain a defense watch-plus item until checkpoint-bound
score artifacts and a consumer contract exist?

This was a Lane A/B defense artifact gate. It inspected the official
OpenReview note, PDF, supplementary ZIP tree, README, configs, attack runner,
loss code, and small committed `inference_attacks/*.txt` score-text fragments.
No CIFAR-10, CelebA, LSUN, Stable Diffusion, model checkpoint, generated image
set, classifier weight, denoiser weight, or GPU job was downloaded or executed.

## Public Surface

| Field | Value |
| --- | --- |
| OpenReview forum | `https://openreview.net/forum?id=LIBLIlk5M9` |
| Title | `CPSample: Classifier Protected Sampling for Guarding Training Data During Diffusion` |
| Authors | Joshua Kazdan, Hao Sun, Jiaqi Han, Felix Petersen, Frederick Vu, Stefano Ermon |
| Venue | `ICLR 2025 Poster` |
| OpenReview cdate / mdate | `2024-09-24T03:30:31.911Z` / `2025-03-02T08:11:05.180Z` |
| PDF | OpenReview `/pdf/7b8681546f672eb1d730320e8f9cb2840a57ebf1.pdf`; `19,229,130` bytes; SHA256 `B6B7DCC0B827C0790C21D6035E73A32574C007808D178B5002C4941BC89C58BE` |
| Supplement | OpenReview `/attachment/7a8e7e3aed65bef0fc49695eb16494ce28587c58.zip`; `1,557,183` bytes; SHA256 `6664AEB475CBD3ED2F1628DBC29B56E8D20DAAF7A34A53A34FA72400BCA8B3BC` |
| Supplement root | `DiffDP-main/` with `29` files totaling `2,025,437` extracted bytes |
| Main tree | `README.md`, `configs/{bedroom,celeba,church,cifar10}.yml`, `datasets/*.py`, `functions/{denoising,losses}.py`, `models/*.py`, `runners/{classifier,diffusion}.py`, `main.py`, `requirements.txt`, `jupyter_scripts/CPSample_Guided_Generation.ipynb`, `images/CelebASim.png`, and `inference_attacks/*.txt` |
| License / release | No license file, GitHub repo, release tag, or immutable package version was found in the inspected public surface. |

## What Is Present

| Source | Finding |
| --- | --- |
| Paper claim | CPSample changes diffusion sampling with a classifier trained on random labels. The paper reports reduced nearest-neighbor similarity for fine-tuned CIFAR-10, CelebA, and LSUN Church generation, and reports CIFAR-10 reconstruction-error membership-test statistics. |
| Paper Table 1 | Similarity-threshold high-match rates fall from `6.25%` to `0.00%` on CIFAR-10, `12.5%` to `0.10%` on CelebA, and `0.73%` to `0.04%` on LSUN Church under the paper's selected CPSample settings. |
| Paper Table 3 | CIFAR-10 mean reconstruction-error membership-test statistics are `DDIM = 138, p ≈ 0`; Ambient corruption baselines are near non-significant; CPSample reports `0.59, p = 0.28` for `alpha = 0.5`, `0.23, p = 0.41` for `alpha = 0.25`, and `-0.86, p = 0.81` for `alpha = 0.001`. |
| README / code | The supplement provides training, fine-tuning, sampling, and `--inference_attack` commands, but the pretrained denoiser/classifier links are TODO Google Drive placeholders. Preparing the subset is also marked TODO. |
| `functions/losses.py` | The `inference_attack_loss` computes a classifier-gradient-corrected denoising reconstruction error, then returns a batch mean squared residual. |
| `runners/diffusion.py` | `inference_attack()` loads runtime `ckpt.pth` files from local log directories, iterates a dataset loader, and appends batch mean losses to a local `inference_attack.txt`. |
| `datasets/__init__.py` | CIFAR/CelebA/LSUN loaders can split data using runtime shuffles and optional subset indices, but the supplement does not ship the exact paper subset-index manifest. |
| `inference_attacks/*.txt` | Four small score-text fragments are present: `full_prot.txt` (`n = 239`, mean `92.299517`), `full_unprot.txt` (`n = 181`, mean `133.306075`), `sub_prot.txt` (`n = 160`, mean `90.478344`), and `sub_unprot.txt` (`n = 105`, mean `84.945813`). They are not accompanied by row identities, train/test labels, ROC arrays, metric JSON, checkpoint hashes, or a verifier command. |

## Gate Result

| Gate | Result |
| --- | --- |
| Defense mechanism identity | Pass as watch-plus. CPSample is a real defense mechanism with official ICLR paper and runnable-looking code supplement. |
| Target/checkpoint identity | Fail for current release. The public surface needs local `ckpt.pth` denoiser/classifier checkpoints, but does not publish immutable checkpoint hashes or working pretrained links. |
| Member/nonmember identity | Fail for current DiffAudit admission. CIFAR-10 train/test semantics are described, and subset code exists, but exact subset indices for fine-tuned CIFAR-10/CelebA/LSUN targets are not shipped. |
| Score/metric packet | Partial but insufficient. The four text files are useful evidence that some attack-loss outputs were committed, but they have mismatched row counts, no row labels, no member/nonmember binding, no ROC arrays, no AUC/ASR/TPR-at-FPR metrics, and no metric JSON. |
| Adaptive defense contract | Fail. DiffAudit would need a defended target, undefended comparator, adaptive attacker, retained-utility metric, checkpoint identity, and row-bound attack outputs before any defense claim could become product-consumable. |
| Download justification | Hold. The supplement was small enough to inspect, but running it would require datasets and missing model artifacts; no additional data/model download is justified by the current boundary. |
| GPU release | Fail. The current decision is artifact-boundary only; no CPU sidecar or GPU job is selected. |

## Decision

`ICLR OpenReview code supplement / defense watch-plus / score-text fragments
present / checkpoint-split artifacts missing / no download / no GPU release /
no admitted row`.

CPSample is stronger than paper-only defense items because the official
OpenReview supplement contains actual diffusion/classifier code and small
attack-loss text fragments. It is still not a current DiffAudit defense-aware
asset. The public package does not bind the score fragments to immutable
member/nonmember rows, does not ship the target/checkpoint identities needed to
replay the results, and does not provide a ready metric/verifier packet.

Keep CPSample as Research-only defense watch-plus. Do not cite its paper
statistics or `inference_attacks/*.txt` fragments as admitted defense evidence,
and do not promote it into Platform/Runtime rows or product copy.

Smallest valid reopen condition:

- the authors publish checkpoint-bound denoiser/classifier artifacts or hashes;
- exact train/test/subset row identities are released for the reported targets;
- protected and unprotected score rows are bound to those identities;
- ROC arrays or metric JSON include AUC/ASR/TPR-at-FPR or an explicitly
  reviewed defense-specific metric contract; and
- DiffAudit defines the defended target, undefended comparator, adaptive
  attacker, and retained-utility boundary before any product-facing use.

Stop condition:

- Do not download CIFAR-10, CelebA, LSUN, Stable Diffusion weights, denoiser
  checkpoints, classifier checkpoints, generated images, or missing Google
  Drive placeholders for CPSample in the current roadmap cycle.
- Do not run `python main.py`, train classifiers, fine-tune denoisers, generate
  protected/unprotected images, run `--inference_attack`, or launch CPU/GPU
  sidecars from this gate.
- Do not promote CPSample into admitted evidence, Runtime schemas, defense
  recommendations, or Platform product copy without the reopen artifacts and a
  consumer-boundary review.

## Reflection

This gate finds a real defense mechanism and a better public artifact surface
than README-only defenses, but it does not change the current project decision.
The useful signal is "watch for checkpoint-bound defense artifacts"; the
discipline is not to turn paper-level robustness claims or unlabeled text losses
into a system-consumable defense row.

Current slots remain `active_gpu_question = none`, `next_gpu_candidate = none`,
and `CPU sidecar = none selected after CPSample defense artifact gate`.

## Platform and Runtime Impact

None. CPSample is not admitted evidence and does not change the current
Platform/Runtime consumer set or schema. A future product integration would
need a defense-aware row type with protected/undefended comparators, retained
utility, adaptive-attacker limits, and row-bound score artifacts.
