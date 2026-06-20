# E2SCT-003 DurMI TTS Public-Surface Check

> Date: 2026-06-08
> Mode: no-download metadata/file-listing check
> Decision: support-only / TTS-audio watch-plus; not C14; not admitted; not denominator; no_compute_release

## Scope

This check closes the current E2 public-surface pass for `E2SCT-003` DurMI.
It uses OpenReview metadata, a no-download supplement HEAD check, Zenodo record
metadata, Zenodo file listing, and the existing local DurMI evidence card. It
does not download the OpenReview supplement, Zenodo archives, audio datasets,
TTS checkpoints, TextGrid files, generated outputs, or run code.

Sources checked:

- `https://openreview.net/forum?id=NvHFk2D2g3`
- `https://api2.openreview.net/notes?forum=NvHFk2D2g3&details=invitation`
- `https://openreview.net/attachment?id=NvHFk2D2g3&name=supplementary_material`
- `https://zenodo.org/records/15474571`
- `https://zenodo.org/api/records/15474571`
- `docs/evidence/durmi-tts-artifact-gate-20260515.md`

## Findings

| Surface | Current finding |
| --- | --- |
| OpenReview submission | The forum includes the submission note `NvHFk2D2g3`, title `DurMI: Duration Loss as a Membership Signal in TTS Models`, venue id `ICLR.cc/2026/Conference/Rejected_Submission`, and public PDF plus supplementary-material flags. The forum query returned `20` notes, including decision/rebuttal material. |
| OpenReview supplement metadata | A no-download `HEAD` request to `supplementary_material` returned status `200`, content type `application/zip`, and content length `56,140,177`. This proves reachability only; it does not inspect or admit the ZIP contents in this pass. |
| Zenodo record | Zenodo API record `15474571` reports DOI `10.5281/zenodo.15474571`, title `DurMI: Membership Inference via Duration Loss in Diffusion-Based Text-to-Speech Models`, publication date `2025-05-21`, open access, and `12` listed files. |
| Zenodo files | The public listing exposes three dataset archives (`ljspeech.Egg`, `libritts.Egg`, `vctk.egg`) and nine GradTTS/WaveGrad2/VoiceFlow checkpoint or model files. File sizes range from `59,460,763` bytes to `8,970,035,645` bytes. |
| Existing split evidence | The existing evidence card records a prior supplement inspection with a precise GradTTS LJSpeech split: `5,977` unique member WAV rows, `5,977` unique nonmember WAV rows, and `0` WAV-id overlap. This check did not redownload the supplement. |
| Missing replay packet | The current public metadata/file listing does not expose ready duration-loss score arrays, ROC arrays, metric JSON, generated result graphs, or a no-training verifier. The existing evidence card records that DurMI scripts generate JSON/PNG outputs after local execution. |

## Interpretation

`E2SCT-003` is stronger than ordinary paper-only support because the public
surface exposes a real paper/supplement, open Zenodo dataset/checkpoint
metadata, and existing evidence for at least one exact TTS member/nonmember
split. This is exactly the kind of row that weak rules can over-promote:

- paper-claim plus artifact link;
- checkpoint/data availability;
- split visibility for one TTS setting;
- runnable attack-code surface in the supplement.

DiffAudit still blocks the row from C14, N50, and admitted evidence because the
current public surface does not expose a ready row-bound duration-loss score or
response packet:

- no public per-row `member_dur_losses` / `nonmember_dur_losses` score arrays;
- no ROC arrays;
- no metric JSON;
- no generated result graph packet that can be tied to immutable rows;
- no no-training verifier;
- no current TTS/audio consumer-boundary lane for Platform or Runtime.

The blocker is not compute availability. Running DurMI would require accepting
a new TTS/audio modality contract and downloading multi-GB datasets/checkpoints
before a public score packet exists.

## Decision

`support_only_tts_audio_watch_plus /
checkpoint_split_metadata_without_ready_score_packet /
row_bound_duration_loss_score_packet_missing / no_compute_release`.

Do not count `E2SCT-003` as a C14 false-promotion exemplar, admitted evidence,
external-denominator evidence, completed external adjudication, reviewer
reliability evidence, or compute release. Keep it as support-only TTS/audio
watch-plus and as an example of checkpoint-plus-split weak-rule pressure.

Do not download Zenodo audio datasets, TTS checkpoints, TextGrid files,
OpenReview supplement archives, generated results, or media payloads. Do not
run GradTTS, WaveGrad2, VoiceFlow, DurMI attacks, metric scripts, CPU sidecars,
GPU/DCU jobs, or Platform/Runtime schema work from this gate.

Reopen only if public row-bound duration-loss score/ROC/metric/verifier
artifacts appear, or if DiffAudit explicitly opens a TTS/audio membership lane
with a reviewed consumer-boundary decision.
