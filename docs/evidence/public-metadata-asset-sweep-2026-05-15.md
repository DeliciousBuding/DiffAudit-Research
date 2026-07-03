# Public Metadata Asset Sweep

> Date: 2026-05-15
> Status: public metadata sweep / only known CLiD and CopyMark HF surfaces / CLiD ZIP still range-inaccessible with auth / no new replay packet / no download / no GPU release / no admitted row

## Question

After the DIFFENCE Zenodo snapshot sync and the lightweight GitHub triage, does
fresh public metadata from Hugging Face or GitHub expose a non-duplicate
image/latent-image diffusion-MIA replay packet with target identity,
member/nonmember semantics, and response or score artifacts?

This sweep used authenticated Hugging Face metadata, small dataset README
reads, GitHub repository search, and GitHub code search. It did not download
Hugging Face ZIP payloads, image folders, model weights, checkpoints, generated
responses, or full external repositories, and it did not run attack scripts or
GPU jobs.

## Surfaces Checked

| Surface | Result |
| --- | --- |
| Hugging Face dataset search terms | `diffusion membership inference`, `membership inference diffusion`, `MIA diffusion`, `COCO_MIA`, `CopyMark`, `SecMI`, `CLiD`, `privacy diffusion model` |
| Relevant HF hits | `zsf/COCO_MIA_ori_split1` and `chumengl/copymark` only |
| Lexical false positives | `clides/*`, `CliDyn/*`, `SWE-Arena/cli_data`, and other unrelated `CLiD` string matches |
| GitHub repository search | Recent broad queries returned survey/awesome repos or unrelated infrastructure, not new artifact-bearing diffusion-MIA repos |
| GitHub code search | Exact artifact queries such as `member_scores_all_steps.pth` and `COCO_MIA_ori_split1` only returned already-covered CopyMark, CLiD, or DiffAudit evidence files |

## Hugging Face Findings

Authenticated metadata access is available for the local account, but it does
not change the CLiD boundary.

| Dataset | Metadata finding | Decision impact |
| --- | --- | --- |
| `zsf/COCO_MIA_ori_split1` | `private = false`, `gated = auto`, `lastModified = 2025-01-04T07:57:18Z`, `3` siblings: `.gitattributes` (`2,307` bytes), `README.md` (`871` bytes), and `mia_COCO.zip` (`1,620,731,171` bytes, blob `d5f7fa657f00e2867ce38a060a2e7c4661e2f8be`) | Still CLiD candidate-only. The dataset card says the ZIP is a randomly selected MS-COCO packet processed for CLiD fine-tuning, but it exposes no public image ID, caption, row order, member/nonmember, or score manifest preview. Authenticated `HEAD` and `Range: bytes=-1048576` against `mia_COCO.zip` still returned `403`, so ZIP central-directory inspection is not available without resolving access/download policy. |
| `chumengl/copymark` | `private = false`, `gated = false`, `lastModified = 2024-06-17T06:12:46Z`, `3` siblings: `.gitattributes` (`2,307` bytes), `README.md` (`36` bytes), and `datasets.zip` (`5,662,307,542` bytes, blob `c097608a500782a0d84938541d9472d9c0db190f`) | Already covered by the CopyMark provenance and official score-artifact gates. Downloading the `5.66` GB ZIP would not answer a new current decision because the useful small score/ROC/log artifacts are already committed in `caradryanl/CopyMark`, and the missing blockers remain checkpoint hashes, row-ID-bound score manifests, small immutable packets, and ready verifiers. |

The CLiD dataset README remains descriptive only: it links the NeurIPS 2024
CLiD paper and official code, and says the dataset was randomly selected from
MS-COCO and processed for CLiD. It does not publish row identities or split
manifests.

## GitHub Findings

The exact code searches were intentionally artifact-shaped rather than paper
title-shaped:

| Query | New artifact result |
| --- | --- |
| `score_result_test.json diffusion` | no new non-DiffAudit artifact hit |
| `member_scores_all_steps.pth` | only `caradryanl/CopyMark` and existing DiffAudit evidence |
| `mia_eval_idxs diffusion` | no new non-DiffAudit artifact hit |
| `COCO_MIA_ori_split1` | only `zhaisf/CLiD` and existing DiffAudit evidence |
| `AUROC TPR_at_1_threshold diffusion` | no new non-DiffAudit artifact hit |

The broader repository searches for recent pushed repositories containing
`membership inference`, `stable diffusion`, `member nonmember`, `AUROC`, or
`score` mostly returned survey lists, awesome lists, and unrelated application
repositories. They did not expose a new candidate with target checkpoint
identity, exact member/nonmember rows, response packets, score rows, ROC arrays,
metric JSON, or a verifier.

## Decision

`public metadata sweep / only known CLiD and CopyMark HF surfaces /
CLiD ZIP still range-inaccessible with auth / no new replay packet / no
download / no GPU release / no admitted row`.

This closes the immediate Hugging Face/GitHub metadata branch for the current
cycle. The only relevant HF assets are the already-known CLiD and CopyMark
surfaces:

- CLiD remains strong candidate evidence, but still cannot be promoted because
  its public score rows are numeric-only and the gated ZIP does not expose a
  metadata-only manifest or central directory through authenticated range
  access.
- CopyMark remains official Research-side score-artifact support evidence, but
  the HF dataset ZIP is too large and not decision-changing because the public
  GitHub tree already exposes the useful small score/ROC/image-log artifacts.

Current slots remain `active_gpu_question = none`,
`next_gpu_candidate = none`, and
`CPU sidecar = none selected after public metadata asset sweep`.

Smallest valid reopen condition:

- CLiD publishes or exposes a row manifest mapping `inter_output/*` rows to
  immutable MS-COCO image IDs, captions, target/shadow split, and
  member/nonmember role; or authenticated metadata-only ZIP inspection becomes
  possible without downloading image payloads.
- CopyMark publishes a compact row-ID-bound score manifest, checkpoint hashes,
  a no-training verifier, or a small immutable data/checkpoint packet that
  avoids the full HF ZIP and model-folder downloads.
- A new public repository or dataset appears with a genuinely new, small
  score/response/ROC/metric/verifier packet rather than only code, README,
  notebooks, figures, or large raw image/model archives.

Stop condition:

- Do not download `zsf/COCO_MIA_ori_split1/mia_COCO.zip`,
  `chumengl/copymark/datasets.zip`, image folders, Stable Diffusion weights,
  CommonCanvas/LDM/Kohaku/COCO/LAION payloads, or target/shadow checkpoints.
- Do not clone large external repositories by default, run CLiD/CopyMark/PIA/
  PFAMI/SecMI/GSA scripts, regenerate features, fit attack models, or launch
  GPU work from this sweep.
- Do not change Platform/Runtime admitted rows, schemas, recommendation logic,
  product copy, or admitted evidence bundles.

## Platform and Runtime Impact

None. Platform and Runtime continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
