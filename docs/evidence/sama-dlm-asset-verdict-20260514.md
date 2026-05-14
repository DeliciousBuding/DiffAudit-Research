# SAMA Diffusion Language Model Asset Verdict

> Date: 2026-05-14
> Status: diffusion-language-model / out-of-scope-for-image-Lane-A / code-only-target-recreation / no download / no GPU release

## Question

Does `Stry233/SAMA` provide a clean non-duplicate Lane A asset for DiffAudit:
target model identity, exact member/nonmember split, query/response or score
coverage, provenance, and a bounded scoring contract?

This is an asset gate, not a reproduction attempt. No model weights, datasets,
Hugging Face gated models, or generated artifacts were downloaded. The check
used only public GitHub metadata, README/config/tree inspection, and small code
snippets.

## Candidate

| Field | Value |
| --- | --- |
| Public repo | `https://github.com/Stry233/SAMA` |
| Paper line | `Membership Inference Attacks Against Fine-tuned Diffusion Language Models` |
| Default branch | `main` |
| Checked commit | `5ac7aa4a2e3765958e1b39a7774d72bbe4ee6dcd` |
| GitHub license metadata | `MIT` |
| Last push | `2026-04-13T20:47:11Z` |
| Repo description | `[ICLR'26] Membership Inference Attacks Against Fine-tuned Diffusion Language Models` |
| Domain | Diffusion language models over NLP datasets, not image or latent image diffusion response contracts |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| GitHub repo metadata | The repository is public, has default branch `main`, and exposes code for SAMA plus baseline membership attacks. No GitHub release assets are published. |
| Root `README.md` | Describes SAMA for diffusion language models and gives a workflow: prepare NLP datasets, train target DLM models, then run attacks. |
| `README.md` environment section | Requires local dataset paths, metadata output paths, W&B project/group values, and optionally `HF_TOKEN` for gated/private Hugging Face models. |
| `README.md` usage | Step 1 prepares datasets, Step 2 trains target DLM models, and Step 3 runs membership inference with `--base-dir`, `--target-model`, and optional `--lora-path`. |
| Repository tree | Contains `attack/`, `dataset/`, `trainer/`, configs, and model architecture code. It does not contain released target checkpoints, LoRA adapters, member/nonmember manifests, or result packets. |
| `dataset/prep.py` | Builds `train.json` and `test.json` by shuffling public NLP datasets such as Wikitext, AG News, and XSum, then splitting by `member_ratio`. These are generated local subsets, not published target membership manifests. |
| `dataset/prep_mimir.py` | Converts `iamgroot42/mimir` entries into local `train.json` member and `test.json` nonmember files for selected MIMIR splits. It is a preparation script, not a frozen DiffAudit artifact. |
| `attack/configs/config_all.yaml` | Defaults `target_model` and tokenizer to local `./` paths, with datasets pointing at local `train_subset.json` / `test_subset.json`; the reference model path is `GSAI-ML/LLaDA-8B-Base`. |
| `attack/run.py` and `attack/attacks/sama.py` | Implement loss/SAMA attacks and can emit metadata, but require a loaded target model plus prepared datasets. They do not publish a ready target/split/score bundle. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for current Lane A. The repo provides training and attack code, but no hashable fine-tuned DLM target checkpoint or fixed LoRA adapter is released. |
| Exact member split | Fail. Member/nonmember data are generated locally by preparation scripts from public NLP datasets or MIMIR splits; the repo does not publish a frozen per-sample target-training membership manifest. |
| Exact nonmember split | Fail. Nonmembers are generated locally in `test.json`, not released as a fixed public DiffAudit split tied to a released target model. |
| Query/response or score coverage | Fail. No reusable query package, model response package, score JSON, or SAMA metadata result bundle is published. |
| Scoring contract | Partial pass as code. SAMA and baseline attacks are implemented, but the scoring contract depends on locally trained or supplied DLM targets and locally prepared datasets. |
| Mechanism delta | Pass as related-method watch, fail for current product lane. Diffusion language model membership is distinct from CommonCanvas, MIDST, Beans, MNIST/Fashion-MNIST, and image LoRA routes, but DiffAudit's active Lane A is image/latent-image diffusion asset acquisition and response contracts. |
| GPU release | Fail. There is no public target checkpoint, exact split manifest, response/score packet, or frozen `25/25` or `50/50` DiffAudit command. |

## Decision

`diffusion-language-model / out-of-scope-for-image-Lane-A /
code-only-target-recreation / no download / no GPU release`.

`Stry233/SAMA` is useful as a related-method reference for membership inference
on diffusion language models. It is not a clean Lane A second asset for the
current DiffAudit image/latent-image roadmap. The decisive blockers are scope
and artifact shape: the public repo provides code to prepare NLP datasets,
train or load DLM targets, and run SAMA, but does not release a fixed target
checkpoint, exact per-sample member/nonmember manifest, or reusable response or
score packet.

Do not download gated language models, train DLM targets, generate MIMIR or NLP
subsets, or launch SAMA GPU jobs inside the current image-diffusion roadmap
cycle. Reopen only if the project explicitly adds a text/DLM membership lane,
or if a public-safe artifact appears with:

- a hashable fine-tuned DLM checkpoint or LoRA adapter,
- exact per-sample member and nonmember manifests tied to that target,
- released attack metadata or a deterministic scoring command,
- and a bounded first packet whose stop gate closes on `AUC < 0.60` or
  near-zero strict-tail recovery.

## Platform and Runtime Impact

None. This is Research-only related-method evidence. It is not admitted
evidence, not a Platform product row, and not a Runtime schema input.
