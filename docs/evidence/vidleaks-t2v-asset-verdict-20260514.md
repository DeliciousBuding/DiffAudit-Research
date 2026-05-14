# VidLeaks Text-to-Video Asset Verdict

> Date: 2026-05-14
> Status: text-to-video / code-snapshot-only / live-repo-unavailable / artifact-incomplete / no model-video download / no GPU release

## Question

Does `VidLeaks` / `wangli-codes/T2V_MIA` provide a clean non-duplicate Lane A
asset for DiffAudit: target model identity, exact member/nonmember split,
query/response or score coverage, provenance, and a bounded scoring contract?

This is an asset gate, not a reproduction attempt. No text-to-video model
weights, WebVid/MiraData/Panda videos, generated videos, Gemini outputs, or
VBench artifacts were downloaded. A small Zenodo software snapshot was inspected
only for file-list and README/script evidence, then the temporary zip was
removed.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `VidLeaks: Membership Inference Attacks Against Text-to-Video Models` |
| Zenodo record | `https://zenodo.org/records/17972831` |
| DOI | `10.5281/zenodo.17972831` |
| Zenodo title | `wangli-codes/T2V_MIA: v1.0.1` |
| Publication date | `2025-12-18` |
| License metadata | `cc-by-4.0` |
| Code snapshot | `wangli-codesT2V_MIA-v1.0.1.zip`, `1,521,848` bytes, `md5:001e45be0e4229aead4f14011d12610d` |
| Related GitHub URL | `https://github.com/wangli-codes/T2V_MIA/tree/v1.0.1` |
| Live GitHub status | `404 / Not Found` for `wangli-codes/T2V_MIA` during the 2026-05-14 check |
| Domain | Text-to-video membership inference over generated video metrics, not the current image/latent-image response-contract lane |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| Zenodo metadata | Describes an implementation of VidLeaks for text-to-video membership inference and points to a GitHub repository. The record contains a single small code snapshot, not model/video assets. |
| Live GitHub probe | `gh repo view wangli-codes/T2V_MIA` and direct content/ref API calls returned repository not found. The source repo was not available for live branch/tag inspection. |
| Zip central directory | Contains `README.md`, `caption/geminiapi.py`, `evaluation/Vbench.md`, `methods/method.md`, attack scripts, frame extraction scripts, and ROC plot PNGs. It does not contain target T2V model weights, generated videos, dataset manifests, CSV feature packets, or score JSON. |
| `README.md` dataset section | Instructs users to download WebVid-10M, MiraData, and Panda-70M from official sources. The snapshot does not publish a frozen member/nonmember video split. |
| `README.md` methods section | References AnimateDiff, InstructVideo, and Mira as target text-to-video generation models and points users to model subdirectories or external repos. It does not release fixed target checkpoints or generated video responses. |
| `README.md` caption/evaluation sections | Requires a Gemini API key for caption extraction and uses VBench background consistency over user-provided video paths. These are runtime dependencies, not released response artifacts. |
| `methods/method.md` | Links to external AnimateDiff, InstructVideo, and Mira repositories. The `methods/` subdirectories in the snapshot are empty placeholders. |
| `script/attack1_labels.py` | Trains/evaluates a classifier from local feature CSVs under paths such as `../methods/animatediff/multi_metrics/{temp_name}_member_25_8` and `frame_clip/member_25_8_sample_0.csv`. |
| `script/attack2_nomember.py` | Builds a nonmember calibration baseline from local `member` / `nomember` feature CSVs and emits ROC data, but the required CSVs are not in the snapshot. |
| `script/attack3_query.py` | Scores query-only features from local `member_25_8` and `nomember_25_8` metric/CLIP CSV paths. It defines metrics, not a released target response package. |
| `script/roc_data*/*.png` | Contains illustrative ROC curve images only. The plotted source CSVs or per-sample score manifests are not released. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for current Lane A. The paper/repo names AnimateDiff, InstructVideo, and Mira, but no hashable target checkpoint, endpoint contract, or generated video response bundle is released in the snapshot. |
| Exact member split | Fail. Script paths imply local `member_25_8` feature files, but no per-video target-training membership manifest or source videos are published. |
| Exact nonmember split | Fail. Script paths imply local `nomember_25_8` feature files, but no fixed public nonmember manifest or held-out video package is released. |
| Query/response or score coverage | Fail. The snapshot includes code and ROC plot PNGs, not generated videos, metric CSVs, captions, response manifests, or score JSON. |
| Scoring contract | Partial pass as code. The three attack scripts define supervised, reference-based, and query-only scoring over local feature CSVs. They are not runnable as a DiffAudit packet without external videos, generated responses, and feature extraction outputs. |
| Mechanism delta | Pass as related-method watch. Text-to-video membership over background consistency, prompt adherence, captions, and frame metrics is distinct from current image-diffusion candidates, but it is outside the active image/latent-image Lane A asset target. |
| GPU release | Fail. There is no frozen target, exact split, generated video package, feature/score packet, or bounded `25/25` or `50/50` command. |

## Decision

`text-to-video / code-snapshot-only / live-repo-unavailable /
artifact-incomplete / no model-video download / no GPU release`.

VidLeaks is useful as a related-method watch item for future text-to-video
membership work. It is not a clean current DiffAudit Lane A asset. The public
Zenodo release is a small code snapshot whose live GitHub backing repository
was unavailable during this check. The snapshot expects external datasets,
external T2V model repos, Gemini caption extraction, VBench metric extraction,
and local `member` / `nomember` CSV feature files that are not published.

Do not download WebVid-10M, MiraData, Panda-70M, AnimateDiff/InstructVideo/Mira
weights, generated videos, or Gemini/VBench outputs inside the current
image-diffusion roadmap cycle. Reopen only if the project explicitly adds a
text-to-video membership lane, or if a public-safe artifact appears with:

- a hashable target T2V checkpoint or endpoint contract,
- exact per-video member and nonmember manifests tied to that target,
- generated videos or extracted feature/score packets,
- and a bounded first packet whose stop gate closes on `AUC < 0.60` or
  near-zero strict-tail recovery.

## Platform and Runtime Impact

None. This is Research-only related-method/watch evidence. It is not admitted
evidence, not a Platform product row, and not a Runtime schema input.
