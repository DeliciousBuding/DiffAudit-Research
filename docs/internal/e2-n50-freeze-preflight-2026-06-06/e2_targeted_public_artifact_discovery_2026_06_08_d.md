# E2 Targeted Public Artifact Discovery, Pass D

> Date: 2026-06-08
> Mode: no-download GitHub/HF/source scout + read-only subagent scout
> Decision: no new row-bound public score/response artifact found; no C14 expansion; no compute release

## Scope

This pass follows the LAION-MI/MIDM dedicated follow-ups and checks two kinds
of surfaces:

1. current-date public surface drift for `E2Q-013`
   `ronketer/diffusion-membership-inference`;
2. cross-modal/tabular public artifacts that might look like score/manifest
   challengers after the image-diffusion queue reached `0` expansion rows.

The pass is deliberately no-download. It reads GitHub repository metadata,
recursive tree path names, README text, notebook JSON structure, Hugging Face
dataset metadata surfaced by a read-only scout, and GitHub code-search results.
It does not clone repositories, download archives, unpickle notebooks, download
datasets/checkpoints/model weights/images, execute code, train targets, or use
GPU/DCU resources.

## Local Current-Date Checks

| Candidate | Public surface | Live observation | Blocking surface | Decision |
| --- | --- | --- | --- | --- |
| R125 DreamBooth / `ronketer/diffusion-membership-inference` | GitHub repo and raw notebooks | Current `main` HEAD is `eb2df6fdfaddeefbabdd1dc1f04b9dee32174ed4`; latest commit is `2026-04-14T16:20:26Z` and only updates/organizes README. The tree has `39` entries and is not truncated. README SHA-256 is `2dedb244cef2b9f9099212f8a903960f2eef8f2679ae7d8a70df4fe589941b72`. The large notebook has `21` cells, `57` outputs, `6` execution counts, and six reconstruction-loss scalars. | The effective target LoRA/checkpoint path remains `/content/gdrive/MyDrive/IMPR_Ex5/ex5_forensics_supplementary/checkpoint-1500`; the query images are private runtime artifacts; no public member/nonmember manifest, query-label-score join, score/metric JSON, ROC artifact, or verifier is committed. | Current-date support-only follow-up. Keep out of second-asset, N50, C14, admitted evidence, and compute release. |
| MIA-KDE / `PyCoder913/MIA-KDE` | GitHub repo and arXiv-linked README | Public repo; `master` pushed `2026-03-12T11:08:45Z`; tree has `21` entries and is not truncated. `Datasets/` exposes `MIMIC_MIA_Distances.7z`, `Nexoid_MIA_Distances.7z`, `Texas100X_MIA_Distances.7z`, and `UKCensus_MIA_Distances.7z`. README SHA-256 is `0d720759e705f5277cea578717c91fb95dedfb42942e0548ddca065c472a1a54` and names CTGAN, ADS-GAN, DPGAN, TabDDPM, TVAE, and Bayesian Network generators. | The potentially useful distances are only archive entries at the public tree layer. No no-download row-score CSV, ROC JSON, metric JSON, manifest, target identity, split identity, or no-training verifier is visible. | Closest tabular weak challenger, but watch-plus only. It does not alter the current image-diffusion measurement route. |
| Strong-filename GitHub code search | GitHub code search | Searches for `member_scores`, `nonmember_scores`, `attack_results.json`, `TPR@1%FPR`, `AUROC`, `TabDDPM` + MIA/ROC, and diffusion-membership score patterns returned no new route-relevant file hits. | Filename search did not surface a compact public score/response packet outside already-known rows. | Negative search evidence only. Continue manifest-first; do not release compute. |

The R125 current-date details are recorded separately in
[`e2q013_ronketer_dreambooth_public_surface_followup_2026_06_08.md`](e2q013_ronketer_dreambooth_public_surface_followup_2026_06_08.md).

## Read-Only Scout Results

A parallel read-only cross-modal/tabular scout found no candidate that changes
the CCF-A route. Its strongest observations were:

| Candidate | Public surface | Blocking surface | Verdict |
| --- | --- | --- | --- |
| MIA-KDE | Public repo and `*_MIA_Distances.7z` archive entries for four datasets. | Score-like distances are compressed archive contents, not no-download row-bound score/ROC/manifest/verifier files. | Best weak challenger; watch-plus only. |
| Tab-MIA | Hugging Face JSONL-style data with member labels plus GitHub scripts. | LLM fine-tuning privacy target, not diffusion/synthetic generator; no public per-row attack-score packet observed. | Useful support/false-promotion row, not a route upgrade. |
| DOMIAS | Public API/code for synthetic-data MIA and reported `MIA_performance` / `MIA_scores` interface. | Scores and datasets are generated at runtime; no committed row-bound score packet or verifier. | Mechanism reference only. |
| Synthetic-Data-Privacy | Public tabular datasets, code, analysis notebook, and small Zenodo software ZIP. | CTGAN/TVAE/CTAB-GAN+/mixup targets and scores are runtime products; no committed row-score/ROC/metric manifest observed. | Reproducibility/code artifact only. |

A parallel read-only image/T2I scout also found no new row-bound candidate:

| Candidate | Public surface | Blocking surface | Verdict |
| --- | --- | --- | --- |
| ImageAuditor | arXiv `2606.03354v1`; no official repo/hash found in the primary-source scout. | The consumer boundary is IRAG/T2I retrieval-database membership rather than diffusion training-set membership, and the public surface is paper/PDF only. | Watch-only consumer-boundary pressure; not Direction A denominator evidence. |
| Membership Inference Attacks Against Text-to-image Generation Models | arXiv `2210.00968v1` and withdrawn OpenReview `J41IW8Z7mE`; no official anonymous URL or repo commit/hash visible. | Paper-reported metrics only; no public target/split packet, score/response rows, metric JSON, or verifier. | Historical paper-only reference; not a row-bound candidate. |

## Decision

This pass found no new public row-bound diffusion MIA score or response packet.
It does not change the paper-facing evidence state:

- C14 selected stress rows remain `13`.
- Directly freezable external denominator rows remain `0`.
- Dedicated artifact-follow-up surfaces now checked after the three targeted
  passes are `3`: R125 DreamBooth, LAION-MI, and MIDM.
- New row-bound score/response artifacts from targeted post-queue discovery
  remain `0`; the fourth pass includes image/T2I, cross-modal, and tabular
  scouts.
- New row-bound score/response artifacts from dedicated artifact follow-up
  remain `0`.
- `active_gpu_question = none`.
- `next_gpu_candidate = none`.
- `CPU sidecar = none selected`.

The scientific value of this pass is boundary-setting: it prevents public
notebook outputs, compressed tabular distance archives, and code/API contracts
from being mistaken for row-bound evidence packets. That directly supports the
paper's false-promotion thesis, but it is not external adjudication and it does
not create an admitted evidence row.

## Stop Rule

Do not download the MIA-KDE `.7z` archives, Tab-MIA datasets beyond metadata,
DOMIAS runtime datasets, Synthetic-Data-Privacy generated outputs, R125
notebook assets, Stable Diffusion weights, LoRA checkpoints, or Google Drive
artifacts. Reopen only if a public source exposes target identity, immutable
member/nonmember row IDs, committed score/metadata rows, metric provenance,
and a no-training verifier.
