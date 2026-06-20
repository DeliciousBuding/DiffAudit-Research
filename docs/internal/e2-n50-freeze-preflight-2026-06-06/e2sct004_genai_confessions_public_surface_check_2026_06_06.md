# E2SCT-004 GenAI Confessions Public-Surface Check

> Date: 2026-06-06
> Scope: no-download public-surface check for the measurement-route gap board.

## Question

Does `E2SCT-004` expose public row-bound generated outputs, DreamSim scores, or
metric artifacts that can make it an E2 response/score evidence row?

## Checked Public Surface

No archive, image payload, dataset image, model, checkpoint, or generated output
was downloaded. The check used public metadata, small text files, and file
listings only.

| Surface | Observation |
| --- | --- |
| GitHub repo | `https://github.com/hanyfarid/MembershipInference` |
| GitHub head | `refs/heads/main = d72072f3c09562d44e25f829cc864de4207be919` |
| GitHub tree | Recursive tree was observed as `96` entries and `truncated=false` before a later unauthenticated GitHub API rate-limit response. Visible roots are `Carlini`, `Midjourney`, `STROLL`, and `README.md`. |
| GitHub README | Only states the project title and the question: `Has an AI model been trained on your images?` |
| GitHub input lists | `Carlini/intraining/images-and-captions.csv` and `Midjourney/intraining/images-and-captions.csv` expose `file-name`, `caption`, and `url` columns. |
| Zenodo | `https://zenodo.org/records/14573149` / DOI `10.5281/zenodo.14573149` exposes one file, `hanyfarid/MembershipInference-datarelease.zip`, size `133,599,324`, checksum `md5:6ec572d777fd04ef6cdedc712d2b086e`. |
| HF STROLL | `https://huggingface.co/datasets/faridlab/stroll`, SHA `f0a900eca421320d5e74a4dc8ead44db7eda2d40`, public and not gated. |
| HF STROLL annotations | `data/annotations.csv` is `33,312` bytes with ETag `c1a35423b5dc0593dc1ce1311541d95466371670d2859763bcd29adffc9859c6`. It has `100` data rows with columns `image-file-intraining`, `image-file-outoftraining`, `image-caption-base-intraining`, `image-caption-base-outoftraining`, and `image-caption-alternate-intraining`. |
| arXiv API | `https://export.arxiv.org/api/query?id_list=2501.06399` returned `429` during this check; the HF README already cites arXiv `2501.06399`. |

## Finding

`E2SCT-004` is stronger than a code-only row because the public STROLL dataset
does expose a compact row-level input/split/caption surface: `100` paired
`intraining` / `outoftraining` rows with captions. That makes it useful for the
measurement route because weak rules such as `artifact-availability` or
`paper-claim + artifact-link` could plausibly over-promote the claim.

It still does not expose the response/score contract needed for stronger
DiffAudit wording:

- no public row-bound generated-output packet was found;
- no DreamSim score rows were found;
- no metric JSON or ROC/TPR recomputation packet was found;
- no no-training verifier was found;
- the Zenodo record exposes a single large ZIP, not a compact manifest or score
  packet.

## Gate Result

| Gate | Result | Reason |
| --- | --- | --- |
| Target / source identity | `Partial` | Paper/repo/dataset identity is public, but audited target/service identity is not bound to a response packet. |
| Split identity | `Pass-for-input-surface` | STROLL exposes `100` paired `intraining` / `outoftraining` annotation rows. |
| Score or response | `Fail` | No public generated outputs, DreamSim scores, or row-bound response packet were found. |
| Metric provenance | `Fail` | No public metric JSON or verifier was found. |
| Provenance | `Partial` | GitHub, Zenodo, and HF metadata are public; the only Zenodo data-bearing artifact is a large ZIP. |
| Consumer/delta | `Fail` | The current surface supports a false-promotion example, not a consumer-ready membership audit result. |

## Decision

`clean_false_promotion_exemplar_candidate / no_response_score_contract /
no_compute_release`.

Do not count `E2SCT-004` as admitted evidence, a response/score asset, or an
external-audit denominator row. Keep it as a false-promotion exemplar candidate:
it can illustrate why public input/split artifacts plus a paper claim are not
enough for stronger wording.

Allowed wording:

`GenAI Confessions / STROLL exposes a public member/nonmember-style input and
caption surface, but no public row-bound generated outputs, DreamSim scores, or
metric verifier were found; it is a clean false-promotion exemplar candidate,
not admitted response/score evidence.`

## Baseline Tags

- `artifact_availability_would_promote`
- `paper_claim_artifact_link_would_promote`
- `code_availability_would_promote`
- `diffaudit_contract_blocks_or_bounds`

Do not tag `score_only_would_promote` or `metric_code_split_would_promote`
unless a public score/metric packet appears.

## Reopen Condition

Reopen only if the authors expose a compact manifest or small public score/
response packet binding row ids to generated outputs, DreamSim scores, target
or service identity, member/nonmember roles, and recomputable metrics. This
check does not claim the Zenodo ZIP lacks those files internally; it only records
that the allowed public metadata and listings do not expose them. Do not
download the Zenodo ZIP, STROLL PNGs, image URLs, generated payloads, or model
artifacts for this gate.
