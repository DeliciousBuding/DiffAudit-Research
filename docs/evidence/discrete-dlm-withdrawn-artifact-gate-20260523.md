# Discrete DLM Withdrawn Artifact Gate

> Date: 2026-05-23
> Live refresh: 2026-05-25
> Status: withdrawn arXiv / DLM paper-source-only / no official code / no artifact packet / no download / no GPU release

## Question

Does arXiv `2605.16445` / `Membership Inference Attacks on Discrete
Diffusion Language Models` provide a current, public, reusable DiffAudit
artifact after the `eidetic` lightweight triage sync?

This is an artifact verdict. It exists because the abstract reports strong
membership-inference metrics for Masked Diffusion Language Models, so the
paper could otherwise look like a new mechanism lane.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `Membership Inference Attacks on Discrete Diffusion Language Models` |
| Public source | `https://arxiv.org/abs/2605.16445` |
| Current arXiv state | Withdrawn current version; arXiv shows no current PDF |
| Submitted / withdrawn | v1 submitted 2026-05-15; v2 withdrawn 2026-05-19 |
| Author | Shailesh Kasivelrajan |
| Domain | Discrete / masked diffusion language models over text, not the current image or latent-image DiffAudit lane |
| Public repo search | `gh search repos` for the exact title and for `discrete diffusion language models membership inference` returned no repositories |
| Public code search | `gh search code "2605.16445"` returned no official code hits; a 2026-05-25 exact-title refresh found only a paper-index JSON aggregator |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| Current arXiv abstract page | The record says the paper has been withdrawn, the current version is v2, and no PDF is available for the withdrawn version. A 2026-05-25 live refresh still shows `arXiv:2605.16445v2` as withdrawn with `No PDF available`; `https://arxiv.org/pdf/2605.16445` and `https://arxiv.org/e-print/2605.16445` both returned `404`. |
| Current arXiv abstract | Reports a `46`-dimensional reconstruction-loss feature vector across four masking ratios, XGBoost/MLP classifiers, MIMIR-domain mean `AUC = 0.878`, peak `AUC = 0.930` on Pile CC, and a `K = 3` shadow-model transfer attack with mean `AUC = 0.858`. |
| Current arXiv comments | Says citations and co-authors need verification and a new version will be submitted. This makes the current scientific record explicitly unstable. |
| GitHub repository search | No official public repository was found by exact-title, arXiv-id, author, or topic-style GitHub repository search. |
| GitHub code search | No official code hit was found. A 2026-05-25 `2605.16445` code search returned unrelated numeric-data hits, and exact-title code search found only a paper-index JSON aggregator. |
| Local Research index search | No prior DiffAudit evidence note referenced this arXiv identifier or title. |

## Gate Result

| Gate | Result |
| --- | --- |
| Current scientific record | Fail. The current arXiv record is withdrawn. |
| Official public code | Fail. No official public repository or code hit was found. |
| Target model identity | Fail. No hashable MDLM target checkpoint, LoRA, or frozen model artifact is public. |
| Exact member split | Fail. No member manifest or text-row IDs are released. |
| Exact nonmember split | Fail. No nonmember manifest or text-row IDs are released. |
| Query/response or score coverage | Fail. No prompt/text packet, response packet, score rows, ROC arrays, metric JSON, or verifier output is released. |
| Current DiffAudit fit | Fail for execution. The domain is text/DLM and the public surface is withdrawn paper metadata only, so it does not reopen the current image/latent-image asset lane. |

## Decision

`withdrawn arXiv / DLM paper-source-only / no official code / no artifact
packet / no download / no GPU release`.

The line is useful only as a watch signal that DLM membership inference may
become relevant if a corrected paper and artifacts appear. It is not a current
DiffAudit execution lane.

Do not download MIMIR, MDLM checkpoints, language-model weights, tokenizer
artifacts, or text datasets for this line. Do not implement the reconstruction
loss / XGBoost / MLP feature path from the abstract. Reopen only if a current
non-withdrawn version plus official public code, immutable target/split
manifests, reusable score or response packets, ROC/metric artifacts, and a
reviewed text/DLM consumer boundary appear.

## Platform and Runtime Impact

None. This gate does not change admitted Platform/Runtime rows, Runtime
schemas, product copy, recommendation logic, downloads, CPU sidecars, or GPU
release.
