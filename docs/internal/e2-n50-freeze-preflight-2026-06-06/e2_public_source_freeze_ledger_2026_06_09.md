# E2 Public-Source Freeze Ledger

> Date: 2026-06-09
> Scope: handoff ledger for the next public-source-first freeze cycle.

This ledger gives the next reviewer one current entrypoint for the CCF-A
upgrade route. It combines the feature-packet review row, the prepared C14
review packet, and the high-value public-asset delta refresh. It records
the current state of each row and the surface that must appear before a
stronger claim can be made.

## Counts

- ledger rows: `11`
- bounded-support feature-packet rows: `1`
- C14 pre-label packets: `1`
- high-value rows with no current upgrade: `9`
- compute-release rows: `0`
- high-value refresh snapshot: `2026-06-09T11:40:53.841513+00:00`

## Lane Counts

- `c14_v2_candidate_result_surface`: `1`
- `compact_manifest_watch`: `1`
- `future_vlm_stratum_scout`: `1`
- `pre_label_external_review_packet`: `1`
- `second_asset_watch_compute_gated`: `1`
- `single_row_feature_packet_review`: `1`
- `support_score_file_boundary`: `1`
- `support_sidecar_dlm`: `1`
- `support_sidecar_image_code_split`: `1`
- `support_sidecar_tabular`: `1`
- `support_sidecar_tabular_archive`: `1`

## Ledger

| Row | Lane | State | Next action | Missing surfaces |
| --- | --- | --- | --- | --- |
| E2Q-005 | single_row_feature_packet_review | `bounded_support` | use as reviewer-calibration example; keep outside denominator counts | target checkpoint identity; raw sample IDs |
| C14-PACKET | pre_label_external_review_packet | `packet_ready_only` | collect reviewer CSVs and declarations before aggregation | reviewer CSVs; independence declarations; majority labels; reliability thresholds |
| E1-NDSS-324 | second_asset_watch_compute_gated | `no_current_upgrade` | Check whether public identity changed or compact row-score/metric/verifier surfaces appeared | row-bound score/response packet; metric verifier; immutable row identifiers |
| E2Q-006 | compact_manifest_watch | `no_current_upgrade` | Check GitHub and HF identity plus manifest/verifier filename changes | compact row manifest; target hashes; no-training verifier |
| E2-MOFIT | support_score_file_boundary | `no_current_upgrade` | Check whether target checkpoint identity row manifest metric JSON or surface-delta controls appeared | target checkpoint identity; explicit row IDs; official metric JSON/ROC; surface-delta control |
| E2SCT-029 | c14_v2_candidate_result_surface | `no_current_upgrade` | Check whether safe CSV/JSON verifier public row IDs images or checkpoint identity appeared | safe public row IDs; public input images; immutable checkpoint identity; verifier |
| E2SCT-031 | support_sidecar_dlm | `no_current_upgrade` | Check whether committed result packets or row-bound metadata appeared | target model identity; member/nonmember row manifest; score packet; metric artifact |
| E2SCT-032 | support_sidecar_tabular | `no_current_upgrade` | Check whether public row predictions labels metric JSON or verifier appeared | row-bound predictions or scores; labels; metric JSON/CSV; verifier |
| E2SCT-033 | support_sidecar_image_code_split | `no_current_upgrade` | Check whether result CSV score packet checkpoint identity or verifier appeared | result CSV; row-bound scores/responses; metric JSON; checkpoint-bound verifier |
| E2SCT-034 | support_sidecar_tabular_archive | `no_current_upgrade` | Check whether row-scale score or label arrays appeared | row-scale score arrays; row labels; metric verifier |
| E2SCT-035 | future_vlm_stratum_scout | `no_current_upgrade` | Check whether row-bound attack scores responses metric JSON or verifier appeared | row-bound attack scores or responses; metric JSON/CSV; no-training verifier; VLM consumer boundary |

## Claim Rule

Use this ledger as an execution table. The paper may cite a row only at
the state recorded above. Stronger wording needs the missing surfaces in
that row plus the existing release-packet checks.

Current paper-facing state: the C14 packet stays pre-label, the N50
denominator count stays at zero, admitted-row and second-asset states
are unchanged, and compute release stays closed.
