# E2 Public Surface Metadata Refresh

> Refreshed at: 2026-06-09T11:40:53.841513+00:00
> Scope: no-download public metadata only; not artifact admission.

## Artifact Surface Hints

- `score_or_metric_surface_hint`: 7
- `split_checkpoint_surface_hint`: 1
- `split_response_surface_hint`: 1

## Follow-Up Buckets

- `priority_gate_review`: 9

## Identity Delta Status

- `identity_matched`: 9

## Compact Reopen Hints

- `compact_artifact_filename_hint_only`: 1
- `filename_hint_manual_gate_review_needed`: 2
- `no_compact_reopen_surface_hint`: 6

## Rows

| Row | Title | Identity delta | Reopen hint | Artifact hint | Follow-up |
| --- | --- | --- | --- | --- | --- |
| E1-NDSS-324 | NDSS-324 Reconstruction-based Attack Zenodo | `identity_matched` | `no_compact_reopen_surface_hint` | `split_response_surface_hint` | `priority_gate_review` |
| E2Q-006 | CopyMark compact manifest gate | `identity_matched` | `filename_hint_manual_gate_review_needed` | `score_or_metric_surface_hint` | `priority_gate_review` |
| E2-MOFIT | MoFit public score-surface replay | `identity_matched` | `filename_hint_manual_gate_review_needed` | `score_or_metric_surface_hint` | `priority_gate_review` |
| E2SCT-029 | MIA_SD public result surface | `identity_matched` | `no_compact_reopen_surface_hint` | `score_or_metric_surface_hint` | `priority_gate_review` |
| E2SCT-031 | SAMA DLM public-code surface | `identity_matched` | `no_compact_reopen_surface_hint` | `score_or_metric_surface_hint` | `priority_gate_review` |
| E2SCT-032 | MIA-EPT tabular result-page surface | `identity_matched` | `no_compact_reopen_surface_hint` | `score_or_metric_surface_hint` | `priority_gate_review` |
| E2SCT-033 | Diffusion MIA code-and-split surface | `identity_matched` | `no_compact_reopen_surface_hint` | `split_checkpoint_surface_hint` | `priority_gate_review` |
| E2SCT-034 | ReMIA tabular aggregate result archive | `identity_matched` | `no_compact_reopen_surface_hint` | `score_or_metric_surface_hint` | `priority_gate_review` |
| E2SCT-035 | OpenLVLM-MIA VLM controlled benchmark scout | `identity_matched` | `compact_artifact_filename_hint_only` | `score_or_metric_surface_hint` | `priority_gate_review` |

## Boundary

This high-value delta refresh records public metadata identity only: GitHub HEAD/tree identity, Hugging Face SHA, Zenodo file-list identity, OpenReview/arXiv metadata, and small public manifest/verifier filenames if they appear. It does not download archives, datasets, model shards, image/audio/video payloads, unpickle result files, run notebooks, execute attacks, or launch CPU/GPU/DCU reproduction.

A source identity change is not admission evidence by itself. A row can reopen only when the public surface exposes a compact row manifest, safe row-bound score/response or prediction packet, metric JSON/ROC verifier, target/checkpoint identity, provenance hashes, and a label-shuffle, permutation, or surface-delta control. If those objects are absent, the current boundary remains: no C14/N50 update, no admitted evidence, no second public score/response asset, and no compute release.
