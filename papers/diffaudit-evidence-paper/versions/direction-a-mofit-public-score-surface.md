# Direction A: MoFit Public Score Surface

> Date: 2026-06-08
> Scope: paper-facing note for the MoFit public COCO score replay.

## Decision

MoFit is included as a bounded support-only row in the Direction A
negative/support evidence discussion. It is not admitted evidence, not an N50
denominator row, not a second independent public asset, and not compute release.

## Evidence

The official MoFit repository exposes compact COCO result text files. The
bounded verifier `scripts/replay_mofit_public_coco_scores.py` fetches four
official public COCO text files, verifies size/hash/row/column checks, and
replays the public `Eval/mia_th_COCO.py` score logic.

The public COCO score replay reaches:

- alpha: `0.55`
- ASR: `0.883`
- AUC: `0.941948`
- TPR@1%FPR: `0.488` under the strict `FPR <= 1%` finite-tail rule (`5 / 500` false positives)
- TPR@0.1%FPR: `0.324` under the strict `FPR <= 0.1%` finite-tail rule (`0 / 500` false positives)

The current workspace now records derived audit outputs in the anonymous
supplement:

- `data/mofit_public_score_metrics.json`: best metrics, low-FPR denominator
  note, 1000-sample row bootstrap CI, 1000-sample permutation null, and caption
  file metadata.
- `data/mofit_public_score_alpha_sweep.csv`: alpha sweep with finite low-FPR
  denominator columns.
- `data/mofit_public_score_file_manifest.csv`: public file size/hash/shape
  checks plus header and row-order anchor hashes with sanitized previews.
- `data/mofit_public_score_roc.csv`: best-alpha threshold/ROC rows.
- `data/mofit_public_score_position_manifest.csv`: implicit train/test
  file-position anchors.
- `data/mofit_public_gate_status.csv`: machine-readable six-gate status for
  target identity, split identity, score/response coverage, metric provenance,
  consumer boundary, and surface delta; support-only and all six non-Pass.
- `data/mofit_public_caption_position_manifest.csv`: first-500 support-only
  caption-order anchors, including caption filename and row/text hashes.

With seed `20260608`, the derived controls give AUC bootstrap 95% CI
`[0.929991, 0.955904]` and permutation-null AUC mean `0.500805`
(`p_value_auc_ge_observed=0.000999`). These are row-position controls over the
public score files, not external labels or admitted row binding.

## Boundary

The replay is high scoring, and the new caption-order manifest makes the
support-only row order easier to audit. The official public surface still lacks
explicit score row IDs, immutable public target checkpoint identity, official
machine-readable metric JSON/ROC arrays, and official permutation/control
packets. Row binding to caption JSONL order is plausible but not
manifest-certified by the score files. The derived workspace audit outputs make
the replay more inspectable; they do not repair the missing public row-binding
and target-identity gates.

Allowed wording: MoFit is a support-only public score-surface replay that
remains blocked by row-binding and target-identity gates, with all six gates
non-Pass.

Forbidden wording: MoFit is admitted DiffAudit evidence, C14 evidence, N50
denominator evidence, a completed second asset, or a compute-release target.
