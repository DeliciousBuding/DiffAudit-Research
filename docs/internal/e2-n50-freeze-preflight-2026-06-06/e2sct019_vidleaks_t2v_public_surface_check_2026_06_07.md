# E2SCT-019 VidLeaks T2V Public-Surface Check

> Date: 2026-06-07
> Mode: no-download metadata/API check plus prior local archive verdict
> Decision: t2v-code-snapshot false-promotion exemplar only / not admitted / not denominator / no_compute_release

## Scope

This check closes `E2SCT-019` after the post-C14 queue. It uses Zenodo
metadata/API, the related GitHub URL, and the existing local VidLeaks asset
verdict. It does not download the Zenodo ZIP, clone the upstream repository,
fetch video datasets, download text-to-video models, generate videos, call
Gemini, run VBench, or execute attack scripts.

Sources checked:

- `https://zenodo.org/records/17972831`
- `https://zenodo.org/api/records/17972831`
- `https://github.com/wangli-codes/T2V_MIA/tree/v1.0.1`
- `docs/evidence/vidleaks-t2v-asset-verdict-20260514.md`

## Findings

| Surface | Current finding |
| --- | --- |
| Zenodo record | Status `200`, length `68516`, SHA-256 `d1fdb76b2d3d145333ba3e9c35fadad4d77cb2e5bc84a0e53d230f60557a8b7e`; title `wangli-codes/T2V_MIA: v1.0.1`. |
| Zenodo API | Status `200`, length `4536`, SHA-256 `e385b51b68a15cf23d02ec41d02ac26fa9734a4b5f64ca8f7b5db3f9e6c89266`; DOI `10.5281/zenodo.17972831`, version `v1.0.1`, publication date `2025-12-18`, license `cc-by-4.0`. |
| File catalog | The visible file is `wangli-codesT2V_MIA-v1.0.1.zip`, size `1,521,848`, checksum `md5:001e45be0e4229aead4f14011d12610d`. The ZIP was not downloaded in this check. |
| Related GitHub URL | Zenodo points to `https://github.com/wangli-codes/T2V_MIA/tree/v1.0.1`; the direct public page returned `404 Not Found` during this check. |
| Prior local archive verdict | The 2026-05-14 local note records that a prior archive inspection found README/script surfaces and ROC plot PNGs, but no generated videos, metric CSVs, captions, response manifests, score JSON, target model weights, or exact member/nonmember video manifests. |

## False-Promotion Interpretation

`E2SCT-019` is a clean post-C14 false-promotion exemplar:

- a paper-artifact-link rule would be attracted by a DOI-backed software record;
- a code-availability rule would be attracted by the visible code snapshot;
- a cross-modal novelty shortcut could overstate text-to-video relevance as
  current image-diffusion evidence.

DiffAudit blocks admission because the observed public surface has no
evidence-bearing target/split/score packet:

- no hashable AnimateDiff, InstructVideo, Mira, or endpoint target identity;
- no exact per-video member/nonmember manifest;
- no generated video response packet;
- no row-bound feature CSV, Gemini caption packet, VBench metric packet, score
  rows, ROC CSV, metric JSON, or verifier;
- the live related GitHub tag is not publicly reachable.

## Decision

`t2v_code_snapshot_false_promotion / no_target_split_score_contract /
no_compute_release`.

Add `E2SCT-019` to the C14 false-promotion baseline as a
`t2v-code-snapshot false-promotion` row. Do not count it as admitted evidence, a
response/score asset, an external-audit denominator row, completed external
adjudication, reviewer reliability evidence, or compute release.

Allowed wording:

`VidLeaks exposes a DOI-backed text-to-video MIA code snapshot, but the current
public surface has a dead related GitHub tag, no hashable T2V target identity,
no exact member/nonmember video manifests, no generated videos, no row-bound
feature/score/ROC/metric packet, and no verifier; it is a false-promotion
baseline control, not admitted response/score evidence.`

## Baseline Tags

- `code_availability_would_promote`
- `paper_claim_artifact_link_would_promote`
- `diffaudit_contract_blocks_or_bounds`

Do not tag `artifact_availability_would_promote` unless the public surface adds
the actual row-bound video, feature, score, ROC, or metric packet. Do not tag
`score_only_would_promote` unless public score rows appear.

## Reopen Condition

Reopen as a text-to-video asset only if public-safe artifacts appear with a
hashable T2V target checkpoint or endpoint contract, exact per-video member and
nonmember manifests tied to that target, generated videos or extracted
feature/score packets, ROC/metric artifacts, and a bounded verifier command.
Do not download WebVid-10M, MiraData, Panda-70M, AnimateDiff, InstructVideo,
Mira weights, generated videos, Gemini/VBench outputs, or upstream archives for
this gate. Do not launch GPU/DCU work from this row.
