# E2 Row-Bound Challenger Scout

> Date: 2026-06-06
> Scope: public-source challenger ranking after the `E2Q-005` package check.

This scout asks whether any current candidate should outrank `E2Q-005` as the
next row-bound public evidence target. It uses local E2 preflight files,
subagent read-only reviews, existing evidence notes, and lightweight public
metadata. It does not download datasets, images, weights, archives, or run
GPU/DCU work.

Machine-readable ranking:
[`e2_row_bound_challenger_scout_2026_06_06.csv`](e2_row_bound_challenger_scout_2026_06_06.csv).

## Result

No current public-source candidate outranks `E2Q-005`.

Current ordering:

1. `E2Q-005` Tracing the Roots remains the only single-row package-work
   candidate. Its OpenReview supplement identity, tensor hashes, torch CPU
   shapes, and replay JSON are verified. It remains feature-packet-only and
   provenance-limited, not an N50 row.
2. `E2Q-006` CopyMark is the closest image-diffusion challenger. Its official
   public artifact layer includes image logs, aggregate metric JSONs, and
   selected score tensors. The authenticated no-download recheck in
   [`e2q006_copymark_compact_manifest_gate_2026_06_06.md`](e2q006_copymark_compact_manifest_gate_2026_06_06.md)
   confirms the blocker remains the same: no compact public manifest joins
   filename, member/nonmember role, target/checkpoint identity, per-row score,
   and metric source.
3. `E2Q-004` CLiD has strong numeric score and metric support, but no public
   row-to-COCO image/caption/split/role identity manifest.
4. `E2Q-011` Quantile/SecMI has row-score-like public support, but it is
   third-party SecMI-style evidence and not official quantile-regression
   output.
5. `E2SCT-001` MT-MIA is the best separate tabular/relational lead. It must
   not be pooled with the current image-diffusion denominator without an
   explicit tabular/relational stratum decision.

## CopyMark Manifest Hunt

A narrow CopyMark manifest hunt was attempted because `CopyMark` is the closest
image-diffusion challenger. The earlier unauthenticated GitHub REST tree query
hit rate limit, and GitHub connector code search returned no hits for compact
manifest queries such as `image_log score_result member_scores nonmember_scores
manifest` and `diffusers experiments image_log score_result member nonmember`.
The 2026-06-06 authenticated recheck completed the missing tree/search step:
GitHub `main` is still `069ea0257533fd6d5ec96cbdedccd4a1b70ba9ea`, the
recursive tree has `746` entries and is not truncated, and no compact manifest
or verifier was found. The HF dataset tree exposes only `.gitattributes`,
`README.md`, and the large `datasets.zip`.

Existing evidence in
[`../../evidence/copymark-official-score-artifact-gate-20260515.md`](../../evidence/copymark-official-score-artifact-gate-20260515.md)
already records the key negative boundary: CopyMark exposes useful official
support artifacts, but the public layer is split across image logs, aggregate
ROC/threshold JSONs, tensors/features, and model paths. It still lacks one
row-ID-bound score manifest and a no-training verifier.

## Decision

`E2Q-005` stays first. `CopyMark` remains bounded support / missing-surface
evidence after the authenticated no-download check. Revisit CopyMark only if the
GitHub commit moves, the HF dataset SHA changes with manifest-level files, or
the authors publish a compact public row manifest plus verifier.

The current denominator remains `0`.

Do not build an external adjudication package. Do not run GPU/DCU jobs for E2.
