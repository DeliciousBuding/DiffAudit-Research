# Recon Product Validation Handoff

> Status: promoted as current black-box admitted row on 2026-05-01.

## Product Row

| Field | Value |
| --- | --- |
| Track | `black-box` |
| Method | `recon DDIM public-100 step30` |
| Model family | Stable Diffusion v1.5 + DDIM |
| Evidence level | `runtime-mainline` |
| Metric source | `upstream_threshold_reimplementation` |
| AUC | `0.837` |
| ASR | `0.74` |
| TPR@1%FPR | `0.22` |
| TPR@0.1%FPR | `0.11` |
| Canonical table | `workspaces/implementation/artifacts/unified-attack-defense-table.json` |
| Evidence anchor | `docs/evidence/recon-product-validation-result.md` |

## Platform Copy Boundary

Allowed product copy:

- Recon provides a verified black-box privacy-risk signal on a controlled
  public-100 Stable Diffusion packet.
- The admitted row now reports all four headline metrics from one coherent
  threshold-style metric source.
- The strict-tail signal is nonzero at `TPR@0.1%FPR = 0.11`, interpreted as
  zero false positives out of 100 target nonmembers with 11 true positives out
  of 100 target members.

Blocked product copy:

- Do not call this a paper-complete reproduction.
- Do not present this as a general conditional-diffusion result.
- Do not remove the controlled public-subset and proxy-shadow-member caveats.
- Do not compare the new low-FPR values against older recon rows without
  stating that the metric source changed.
- Do not describe `TPR@0.1%FPR` as fine-grained sub-percent calibration; the
  target nonmember split has 100 rows, so the empirical strict-tail point is a
  zero-false-positive gate.

## Runtime Boundary

No Runtime schema change is required. The promoted row uses existing fields:
`auc`, `asr`, `tpr_at_1pct_fpr`, and `tpr_at_0_1pct_fpr`.

Runtime consumers should treat `metric_source =
upstream_threshold_reimplementation` as explanatory metadata, not a required
new schema field.
