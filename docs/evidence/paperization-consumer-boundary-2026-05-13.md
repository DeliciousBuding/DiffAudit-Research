# Paperization Consumer Boundary Verdict

> Date: 2026-05-13
> Status: synchronized / paperization boundary updated / no schema change

## Taste Check

This is a Lane C consumer verdict after the Beans LoRA delta-sensitivity
metric verdict. The question is not whether another weak/candidate line needs
more experiments. The question is whether recent negative and watch results
changed what Platform, Runtime, or paperization materials may cite as admitted
evidence.

## Evidence Checked

| Artifact | Result |
| --- | --- |
| `docs/evidence/admitted-results-summary.md` | Still contains only the five verified admitted rows. |
| `workspaces/implementation/artifacts/admitted-evidence-bundle.json` | Still the checked Platform/Runtime admitted bundle. |
| `workspaces/implementation/artifacts/unified-attack-defense-table.json` | Validated by `scripts/validate_attack_defense_table.py`. |
| `docs/product-bridge/README.md` | Updated to list recent weak/watch lines as Research-only and non-product. |
| `docs/evidence/innovation-evidence-map.md` | Updated so paperization can cite recent weak/watch lines only as limitations or future-work hooks. |

String checks over the admitted summary and machine-readable admitted artifacts
found no `CommonCanvas`, `MIDST`, `Beans`, `Quantile`, `MIAGM`, `LAION`,
`Zenodo`, `Noise as a Probe`, or `Kohaku` entries. Those names appear only in
boundary, candidate, watch, or limitation documents.

## Decision

`synchronized / paperization boundary updated / no schema change`.

Paperization and consumer-facing materials may cite only the admitted evidence
rows as product-consumable results:

- `recon`
- `PIA baseline`
- `PIA defended`
- `GSA`
- `DPDM W-1`

Recent weak/watch lines must stay out of admitted Platform/Runtime claims:

- CommonCanvas / CopyMark: true second response contract, but weak across
  pixel, CLIP, prompt-response consistency, multi-seed stability, and
  conditional denoising-loss.
- MIDST TabDDPM: exact-label external benchmark, but nearest-neighbor and
  shadow-distributional transfer are weak.
- Beans LoRA: repaired known-split target, but conditional denoising-loss and
  parameter-delta sensitivity are both weak.
- Quantile Regression: mechanism reference, but artifact-incomplete.
- MIAGM: code reference, but target/split/generated-distribution artifacts are
  incomplete.
- Noise as a Probe: mechanism-relevant, but reproduction-incomplete.
- Zenodo fine-tuned diffusion: paper-and-code-backed watch, but exact target
  split manifest is still missing.
- LAION-mi: metadata-ready, but fixed URL probe failed to recover a balanced
  tiny query set.
- Kohaku / Danbooru: broad training-source provenance only, not a target
  member manifest.

No Platform row, Runtime schema, admitted bundle, recommendation logic, or
public product copy change is released.

## Reflection

This cycle changed the consumer boundary rather than the model score. It is
valuable because the recent research work produced many weak/watch results
that are scientifically useful as limitations, but dangerous if they leak into
system-facing admitted claims.

## Next Gate

Keep `active_gpu_question = none`, `next_gpu_candidate = none`, and
`CPU sidecar = none selected`. The next Research cycle should not reopen
CommonCanvas, MIDST, or Beans LoRA adjacent variants. It may proceed only with
a new clean asset, a genuinely new observable family, or a paperization task
that compresses negative evidence without changing admitted status.
