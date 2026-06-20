# E2SCT-009 Memorization Anisotropy Public-Surface Check

> Date: 2026-06-07
> Scope: no-download public-surface check for the measurement-route gap board.

## Question

Does `E2SCT-009` expose row-bound membership evidence, or is it a prompt
memorization surface that weak prompt-list and metric-code rules could
over-promote?

## Checked Public Surface

No prompt file, supplement ZIP, model, checkpoint, generated output, or score
artifact was downloaded. The check used GitHub metadata, file listings, README
text, and OpenReview note metadata.

| Surface | Observation |
| --- | --- |
| GitHub repo | `https://github.com/rohanasthana/memorization-anisotropy` |
| GitHub head | `refs/heads/main = 97e991bac4171ad0547c5779c31180ea8e9f672e` |
| GitHub tree | Recursive tree was observed as `25` entries and `truncated=false`. |
| Visible files | `detect_eval.py`, `detect_mem.py`, `local_model/pipe.py`, `utils.py`, and prompt files including `RV_mem`, `RV_nmem`, `sd1_mem`, `sd1_nmem`, `sd2_mem`, and `sd2_nmem`. |
| GitHub README | Describes official ICLR 2026 code for detecting and mitigating memorization in diffusion models through anisotropy of log-probability. It says memorized and non-memorized prompt data comes from a prior memorization repository. |
| OpenReview | `HTPGy5ydAY`, title `Detecting and Mitigating Memorization in Diffusion Models through Anisotropy of the Log-Probability`, venue `ICLR 2026 Poster`, with public PDF and supplementary attachment metadata. |

## Finding

`E2SCT-009` is useful for a false-promotion baseline because prompt files and a
published detection metric make the surface look strong. A weak rule could
promote a prompt memorization detector into pointwise membership evidence.

The public surface still lacks the DiffAudit response/score contract:

- no immutable target checkpoint and member/nonmember image-row manifest was
  found;
- no public row-bound membership score packet was found;
- no ROC arrays, metric JSON, or verifier were found in public metadata;
- prompt `mem` / `nmem` labels are not enough to bind row-level training
  membership identity for an audit claim.

## Gate Result

| Gate | Result | Reason |
| --- | --- | --- |
| Target / source identity | `Partial` | Repo and paper identity are public, but prompt labels are not bound to a fixed row-level membership audit target. |
| Split identity | `Partial` | Prompt `mem` / `nmem` files are visible, but not immutable image-row member/nonmember labels. |
| Score or response | `Fail` | No public row-bound score arrays or generated response packet were found. |
| Metric provenance | `Partial` | Metric code and paper description are public, but no frozen metric JSON/ROC/verifier packet is public. |
| Provenance | `Partial` | GitHub/OpenReview metadata is public; supplement contents were not downloaded for this no-download gate. |
| Consumer/delta | `Fail` | Prompt memorization detection cannot be promoted to per-sample membership audit evidence without row binding. |

## Decision

`prompt_memorization_false_promotion / no_response_score_contract /
no_compute_release`.

Do not count `E2SCT-009` as admitted evidence, a response/score asset, or an
external-audit denominator row. Keep it as a prompt-memorization false-promotion
exemplar.

Allowed wording:

`Memorization Anisotropy exposes public prompt-list and metric-code surfaces for
diffusion memorization detection, but no public immutable member/nonmember
image-row manifest, row-bound scores, metric JSON, ROC arrays, or verifier were
found; it is a prompt-memorization false-promotion exemplar, not admitted
response/score evidence.`

## Baseline Tags

- `code_availability_would_promote`
- `artifact_availability_would_promote`
- `paper_claim_artifact_link_would_promote`
- `metric_code_split_would_promote`
- `diffaudit_contract_blocks_or_bounds`

Do not tag `score_only_would_promote` unless a public row-bound membership score
packet appears.

## Reopen Condition

Reopen only if a compact public packet appears that binds target checkpoint,
member/nonmember row IDs, prompt or image identities, row-bound scores or
responses, metric provenance, ROC/TPR recomputation, and a verifier. Do not
download prompt files, OpenReview attachments, models, generated outputs, or
score-producing artifacts for this gate.
