# Recon Product Validation Contract

This note freezes the CPU contract for the selected recon strengthening lane.
It does not promote a new result and does not authorize a GPU run yet.

## Verdict

```text
CPU metric field implemented; strict-tail value validated; metric-source
reconciled and promoted as current black-box row
```

The admitted recon row is the strongest black-box evidence, but it is not yet a
complete product-consumable packet. The historical summaries report
`AUC / ASR / TPR@1%FPR`; `TPR@0.1%FPR` was missing from the recon mainline
summary. The code path now emits `tpr_at_0_1pct_fpr` for new recon summaries,
and the bounded public-100 rerun validates a nonzero strict-tail value. The
artifact summary now reimplements the upstream threshold semantics so all four
headline fields can be read from one coherent source.

## Frozen Candidate Packet

| Field | Value |
| --- | --- |
| Method | `recon` |
| Baseline to strengthen | `recon DDIM public-100 step30` |
| Dataset size | 100 target member, 100 target nonmember, 100 shadow member proxy, 100 shadow nonmember |
| Model family | Stable Diffusion v1.5 + DDIM |
| Scheduler | `ddim` |
| Inference steps | `30` |
| Validation images per query | `1` |
| Evaluation method | `threshold` |
| Existing admitted metrics | AUC `0.849`, ASR `0.51`, TPR@1%FPR `1.0`, TPR@0.1%FPR unavailable |
| Claim boundary | controlled public subset, proxy-shadow-member semantics, risk-exists claim only |

The current evidence source is the black-box row in
`workspaces/implementation/artifacts/unified-attack-defense-table.json` and the
existing runtime summary under
`experiments/recon-runtime-mainline-ddim-public-100-step30/summary.json`.

## CPU Checks

Current status:

- `tpr_at_0_1pct_fpr` is now emitted in recon runtime and artifact-mainline
  summaries.
- Characterization tests cover both artifact-mainline and runtime-mainline
  summaries.
- The bounded public-100 rerun is recorded in
  [recon-product-validation-result.md](recon-product-validation-result.md).
- The artifact summary now uses `metric_source =
  upstream_threshold_reimplementation` for headline fields and keeps raw
  feature-0 metrics only for comparison.

Post-promotion requirements:

- Keep output schema backward-compatible: the new field is additive; existing
  fields are unchanged.
- Keep product copy bounded to controlled public-subset and proxy-shadow-member
  semantics.

## GPU Gate

No next GPU task is selected. The bounded GPU candidate has already run:

```text
recon-runtime-mainline-ddim-public-100-step30-product-validation
```

Do not schedule another recon GPU run unless the promotion review identifies a
specific gap that cannot be answered from the existing score artifacts.
Generated images, score artifacts, raw tensors, and run payloads must remain
ignored outside the public evidence path.

## Platform / Runtime Handoff

No sibling repository change is needed yet. If the packet passes with complete
metrics, create a product-bridge handoff that exposes:

- method and packet identity,
- all four headline metrics,
- quality/cost notes,
- claim boundary,
- missing paper-alignment caveats.

Do not let Platform display recon as a general exploit or paper-complete
benchmark.
