# DurMI TTS Artifact Gate

> Date: 2026-05-15
> Status: TTS cross-modal watch-plus / code-and-splits-and-checkpoints-public / no ready score packet / no dataset-checkpoint download / no GPU release

## Question

Does `DurMI: Duration Loss as a Membership Signal in TTS Models` provide a
clean next DiffAudit asset or a bounded replay packet that should change the
current `active_gpu_question = none` state?

This is an artifact gate, not a reproduction attempt. Only public OpenReview,
supplementary ZIP, and Zenodo metadata were inspected. The multi-GB dataset
archives and checkpoints were not downloaded or executed.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `DurMI: Duration Loss as a Membership Signal in TTS Models` |
| OpenReview forum | `https://openreview.net/forum?id=NvHFk2D2g3` |
| OpenReview venue id | `ICLR.cc/2026/Conference/Rejected_Submission` |
| OpenReview decision note | `Reject` |
| OpenReview supplement | `https://openreview.net/attachment?id=NvHFk2D2g3&name=supplementary_material` |
| Supplement size | `56,140,177` bytes |
| Supplement local SHA256 | `65845e9fa81d88d15a0f54ab01507842554ccfab017c3ffec0c23d8a731753d1` |
| Supplement ZIP entries | `890` entries, `98,715,424` uncompressed bytes |
| Zenodo record | `https://zenodo.org/records/15474571` |
| DOI | `10.5281/zenodo.15474571` |
| Zenodo title | `DurMI: Membership Inference via Duration Loss in Diffusion-Based Text-to-Speech Models` |
| Zenodo publication date | `2025-05-21` |
| Zenodo access / license | `open` / `cc-by-4.0` |
| Domain | Diffusion-based text-to-speech membership inference, not current image/latent-image DiffAudit execution scope |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| OpenReview metadata | Submission title is `DurMI: Duration Loss as a Membership Signal in TTS Models`; the public decision note says `Reject`. The submission still exposes supplementary material. |
| OpenReview supplement ZIP | Contains official implementation material for GradTTS, WaveGrad2, and VoiceFlow attacks/training. File mix is mostly source code: `506` `.py` files, `25` `.txt` files, `21` `.yaml` files, `10` `.json` files, and no precomputed result images or score arrays. |
| Root `README.md` | Claims DurMI uses duration loss for diffusion-based TTS membership inference, gives attack commands, and says attack execution saves JSON files and graphs after running. The release does not include those generated JSON/graph outputs. |
| `attack/GradTTS/attack_durmi.py` | Loads a checkpoint and dataset, computes `dur_loss` for member/nonmember batches, computes AUROC and `TPR@1%FPR`, then writes `gt_durmi_<dataset>.json` and a histogram PNG. These are generated outputs, not shipped artifacts. |
| `attack/GradTTS/attack_baseline.py` | Implements baseline loss-based attacks and writes local JSON/PNG outputs after execution. It requires the checkpoint and data loaders. |
| `attack/GradTTS/grad_tts/params_ljspeech.py` | Binds `train_filelist_path` to `./split/ljspeech/member.txt` and `valid_filelist_path` to `./split/ljspeech/nonmember.txt`. |
| `attack/GradTTS/grad_tts/split/ljspeech/member.txt` | Contains `5,977` unique LJSpeech member WAV rows. |
| `attack/GradTTS/grad_tts/split/ljspeech/nonmember.txt` | Contains `5,977` unique LJSpeech nonmember WAV rows, with `0` WAV-id overlap against the member split. |
| `attack/WaveGrad2/attack_durmi.py` | Reads local `member.txt` and `nonmember.txt`, loads WaveGrad2 configs/checkpoint, computes duration loss, and writes `wg_durmi_<dataset>.json` plus a histogram PNG after execution. The required generated outputs are not present in the ZIP. |
| `attack/VoiceFlow-TTS/attack_durmi.py` | Loads VoiceFlow data loaders and checkpoint, computes duration loss, and writes `vf_gradtts_durmi_<dataset>.json` plus a histogram PNG after execution. The output packet is not present in the ZIP. |
| Zenodo metadata | Publishes `12` files: three dataset archives, three GradTTS checkpoints, three WaveGrad2 checkpoints, and three VoiceFlow checkpoints. File sizes range from `59,460,763` bytes to `8,970,035,645` bytes. |

Zenodo file metadata observed:

| File | Size bytes | Checksum |
| --- | ---: | --- |
| `ljspeech.Egg` | `2,917,654,120` | `md5:db4a4fcae60e3b9f9345cc38a25ba03a` |
| `libritts.Egg` | `8,970,035,645` | `md5:caa6b7303d64ef139c79aa5934a2c6e5` |
| `vctk.egg` | `4,765,836,580` | `md5:916f6157f69c4bcb116c58ee33b5bb06` |
| `gradtts_ljspeech_3k.pt` | `59,460,763` | `md5:1491aa6c4047c973d3c7f5245e71f08f` |
| `gradtts_libritts_3k.pt` | `61,914,913` | `md5:751d987f21a4bd6183796ddf84cf3f74` |
| `gradtts_vctk_3k.pt` | `59,682,318` | `md5:7756b0d18c6686924cd626c7a6e8c660` |
| `wavegrad2_ljspeech_1000000.pth` | `320,755,739` | `md5:fdc9fa02edaff8aea906179fe29042c0` |
| `wavegrad2_librispeech_1000000.pth` | `320,755,739` | `md5:13e79b358ce2bfbf5dbfb031f0bc2c92` |
| `wavegrad2_vctk_1000000.pth` | `320,755,739` | `md5:51b87a6ded3144f9af4ea2796899082b` |
| `voiceflow_ljspeech_3k` | `442,329,154` | `md5:f437542495a8b3b0fce5fcfec2e70659` |
| `voiceflow_libritts_3k` | `479,448,066` | `md5:c98c92612f3805db96e707cd9f057267` |
| `voiceflow_vctk_3k` | `472,744,194` | `md5:1c7887d50dd38cc628ef2365f4f66d2c` |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Partial pass for a future TTS lane. Zenodo publishes named GradTTS, WaveGrad2, and VoiceFlow checkpoints with public sizes/checksums, but those are audio/TTS diffusion targets outside current image/latent-image execution scope. |
| Exact member split | Partial pass. The supplement ships a precise GradTTS LJSpeech member split with `5,977` unique WAV rows. The same level of ready split evidence was not found for every model/dataset pair inside the supplement. |
| Exact nonmember split | Partial pass. The supplement ships a precise GradTTS LJSpeech nonmember split with `5,977` unique WAV rows and `0` overlap with the member WAV ids. |
| Query/response or score coverage | Fail for replay. The supplement contains scripts that generate JSON/PNG result artifacts after running, but no ready `member_dur_losses`, `nonmember_dur_losses`, ROC arrays, metric JSON, or score packet is shipped. |
| Metric contract | Partial pass as code. The DurMI scripts compute AUROC and `TPR@1%FPR` from duration-loss scores. They are not CPU-only ready because they require model/data acquisition and CUDA execution. |
| Mechanism delta | Pass as related-method watch-plus. Duration-predictor loss in diffusion TTS is distinct from image response similarity, PIA denoising loss, SimA score norm, CLiD prompt-conditioned replay, MIDST tabular signals, and graph/T2V/DLM watch items. |
| Current DiffAudit fit | Cross-modal watch-plus. It is scientifically stronger than code-only watch items because target checkpoint metadata and at least one exact split are public, but it requires an explicit TTS/audio membership lane before execution or product consumption. |
| GPU release | Fail. Running it would require downloading multi-GB audio datasets/checkpoints and accepting a new TTS modality contract. No bounded first packet is released in the current roadmap cycle. |

## Decision

`TTS cross-modal watch-plus / code-and-splits-and-checkpoints-public / no ready
score packet / no dataset-checkpoint download / no GPU release`.

DurMI is the strongest cross-modal artifact currently observed because it
publishes code, public checkpoint/data metadata, and an exact GradTTS LJSpeech
member/nonmember split. It still does not change the current execution plan:
the public packet does not ship reusable duration-loss scores, ROC arrays,
metric JSON, or generated result graphs, and the modality is diffusion TTS
rather than image/latent-image DiffAudit.

Stop condition:

- Do not download the Zenodo dataset archives or checkpoints inside the current
  image/latent-image roadmap cycle.
- Do not run GradTTS, WaveGrad2, or VoiceFlow attacks, train TTS models, fetch
  Google Drive TextGrid files, or launch GPU jobs for DurMI unless DiffAudit
  explicitly opens a TTS/audio membership lane.
- Do not add TTS/audio support claims, Runtime schemas, Platform product rows,
  admitted bundle entries, or recommendation logic from this artifact.
- Reopen only if a TTS lane is opened with a consumer-boundary decision, or if
  the authors publish a ready score/ROC/metric packet that can be replayed
  without acquiring multi-GB audio datasets and checkpoints.

## Reflection

This cycle found a legitimate non-duplicate membership signal and did the
minimum evidence check needed to avoid both extremes: it is not dismissed as
paper-only, and it is not promoted into an image-roadmap execution task. The
right state is cross-modal watch-plus with `active_gpu_question = none`,
`next_gpu_candidate = none`, and `CPU sidecar = none selected after DurMI TTS
artifact gate`.

## Platform and Runtime Impact

None. This is Research-only intake evidence. Platform and Runtime should
continue consuming only the admitted `recon / PIA baseline / PIA defended / GSA
/ DPDM W-1` set.
