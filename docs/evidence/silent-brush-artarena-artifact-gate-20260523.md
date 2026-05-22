# Silent Brush / Art Arena Artifact Gate

> Date: 2026-05-23
> Status: style-leakage semantic-shift watch / anonymous code-notebook inventory only / no row-bound membership artifact / no download / no GPU release / no admitted row

## Question

Does arXiv `2605.17500` / `The Silent Brush: Evaluating Artistic Style
Leakage in AI Art Generation` expose a public DiffAudit-ready target, split,
score packet, or verifier that should change the active Research slots?

This was selected as a single Lane A metadata gate because it is a recent
text-to-image diffusion-adjacent privacy paper and the arXiv abstract advertises
code and evaluation resources at `https://anonymous.4open.science/r/ArtArena-EBE4`.
The check used arXiv API metadata, arXiv source headers, anonymous repository
file-inventory endpoints, and GitHub repository/code searches. It did not clone
the anonymous repository, download the arXiv source tarball, download artwork
datasets, model weights, generated images, or run evaluation code.

## Public Surface

| Field | Value |
| --- | --- |
| Paper line | `The Silent Brush: Evaluating Artistic Style Leakage in AI Art Generation` |
| arXiv | `https://arxiv.org/abs/2605.17500v1` |
| Published / updated | `2026-05-17T15:18:49Z` |
| Authors | Ninad Joshi, Ashutosh Ranjan, Vivek Srivastava, Shirish Karande |
| Claimed resource URL | `https://anonymous.4open.science/r/ArtArena-EBE4` |
| arXiv source header | `application/gzip`, `Content-Length = 35,598,493`; not downloaded because the artifact gate did not need the large source payload |
| Anonymous inventory endpoint | `/api/repo/ArtArena-EBE4/files` returns a root file list; `tree`, `readme`, and `contents` endpoints returned `401 Unauthorized`, and raw file content was not metadata-readable through the probed endpoints |
| GitHub search | exact-title repository search returned `0`; `2605.17500` repository search returned `0`; `ArtArena-EBE4` code search returned `0`; exact-title code search returned only paper-index aggregator hits, not an official artifact repository |

The anonymous root inventory exposes a code/notebook evaluation surface:

```text
ArtArena.ipynb                325,918 bytes
CSD/
ET_eval.py                    26,923 bytes
ET_eval_fixed.py              28,975 bytes
ET_eval_new.py                25,153 bytes
ET_infer.py                    7,378 bytes
FT_models.py                  41,983 bytes
MD_eval.py                    21,363 bytes
MD_eval_fix.py                22,279 bytes
MD_infer.py                   11,181 bytes
MD_infer_FT.py                 9,135 bytes
README.md                     11,053 bytes
figures/
get_leadger.py                27,294 bytes
prep_ET.py                     9,335 bytes
prep_FT_dataset.py             4,300 bytes
prep_MD.py                     6,741 bytes
```

The subdirectory metadata that was readable remains code/figure oriented:

```text
CSD/model.py                   3,463 bytes
CSD/utils.py                  28,322 bytes
figures/Page3.pdf            703,976 bytes
figures/SDsem.pdf            485,392 bytes
figures/teaser1.pdf          544,794 bytes
```

No target checkpoint hash, immutable member/nonmember artwork manifest,
generated image packet, per-row membership score file, ROC array, metric JSON,
or ready verifier was visible from the metadata-readable surface.

## Claim Boundary

The paper is privacy-relevant, but its claim is not the current DiffAudit
per-sample membership contract. The abstract frames Silent Brush as unintended
style resurfacing in generated images, and introduces Art Arena to measure how
strongly artwork styles are encoded, interact, and appear without explicit
prompt mention.

That is a style-leakage / copyright-evaluation boundary. It is related to
membership inference, but it is not a row-bound member/nonmember MIA packet and
does not expose the score artifacts needed for Platform or Runtime consumption.
Treating it as a MIA result would blur the project boundary rather than improve
the evidence base.

## Gate Result

| Gate | Result |
| --- | --- |
| Current image/latent-image fit | Partial. The paper evaluates text-to-image diffusion systems, but the claim is style leakage rather than per-sample membership inference. |
| Target identity | Fail. The paper mentions Stable Diffusion v1.5, SDXL, and SANA-1.5-style systems, but the checked public surface does not expose paper-bound model revisions, checkpoint hashes, or target bundles. |
| Exact member split | Fail. No immutable artwork/member IDs, image filenames, URLs, artist splits, seeds, or manifests are visible from the metadata-readable resource surface. |
| Exact nonmember split | Fail. No row-bound nonmember or holdout manifest is visible. |
| Query/response or score coverage | Fail. The checked surface exposes code/notebook file names, not generated image packets, per-row MIA scores, ROC arrays, metric JSON, or verifier output. |
| Mechanism delta | Fail for current execution. Art Arena is a style-leakage evaluation protocol, not a non-adjacent MIA scorer with row-bound artifacts. |
| Download justification | Fail. Downloading artwork data, generated images, model weights, or the large arXiv source tarball would not evaluate a released membership score packet. |
| GPU release | Fail. The blocker is semantic boundary plus missing row-bound artifacts, not local compute. |

## Decision

`style-leakage semantic-shift watch / anonymous code-notebook inventory only /
no row-bound membership artifact / no download / no GPU release / no admitted
row`.

Silent Brush / Art Arena should remain Research-only related privacy evidence.
It is useful as a reminder that style leakage and copyright evaluation are
adjacent to membership privacy, but it does not reopen the current Lane A asset
path and does not justify dataset, model, source-tarball, or GPU work.

Current slots become `active_gpu_question = none`, `next_gpu_candidate = none`,
and `CPU sidecar = none selected after Silent Brush / Art Arena artifact gate`.

Smallest valid reopen condition:

- authors publish official non-anonymous artifacts with exact artwork
  member/nonmember manifests, target model revisions or hashes, generated
  response packets, per-row membership-style scores, ROC arrays, metric JSON,
  and a verifier; or
- DiffAudit explicitly opens a reviewed style-leakage / copyright-evaluation
  consumer boundary with schemas separate from per-sample membership rows.

Stop condition:

- Do not download artwork datasets, generated images, SD1.5/SDXL/SANA weights,
  anonymous repository archives, or the large arXiv source tarball from this
  gate.
- Do not run `ArtArena.ipynb`, `ET_eval.py`, `MD_eval.py`, `prep_*`, or style
  extraction / fine-tuning pipelines from this gate.
- Do not add Platform/Runtime rows, schemas, product copy, or recommendation
  logic until a reviewed style-leakage consumer boundary or row-bound
  membership artifacts exist.

## Platform and Runtime Impact

None. Platform and Runtime continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
