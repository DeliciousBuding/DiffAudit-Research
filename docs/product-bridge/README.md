# Product Bridge

This directory explains how Research feeds DiffAudit Platform and Runtime.

Platform should only consume results that have explicit status and clear
limitations. Research provides three kinds of output:

| Output | What it means |
| --- | --- |
| Verified result | A reviewed experiment result that can be shown as audit evidence. |
| Candidate result | A result useful for internal comparison, not yet ready for external use. |
| Constraint note | A known limitation that prevents overclaiming in Platform UI. |

Current cross-box status: cross-box score sharing is candidate-only. It can
inform internal ranking and future research selection, but it should not appear
as admitted Platform evidence until low-FPR stability is established. See
[../evidence/cross-box-boundary-status.md](../evidence/cross-box-boundary-status.md).

Current CLiD status: CLiD is candidate-only. The prompt-conditioned packet is
strong and repeat-stable, but prompt-neutral perturbation collapses the signal.
It can guide research planning, but it should not appear as admitted Platform
evidence. See
[../evidence/clid-prompt-conditioning-boundary.md](../evidence/clid-prompt-conditioning-boundary.md).

Current recon status: recon is the admitted black-box product row. The active
row uses a unified upstream-threshold metric source and reports all four
headline metrics. See
[recon-product-validation-handoff.md](recon-product-validation-handoff.md).

Current H2 image-to-image simple-distance status: the simple-distance signal has
bounded single-asset evidence on the SD1.5/CelebA-style contract, but it is not
yet a Platform row. Treat it as a Research-side candidate for a future product
bridge comparison against recon. See
[../evidence/h2-img2img-simple-distance-admission-result.md](../evidence/h2-img2img-simple-distance-admission-result.md).

## Documents

| Document | Purpose |
| --- | --- |
| [runtime.md](runtime.md) | Notes for Runtime integration. |
| [asset-registry-local-api.md](asset-registry-local-api.md) | Data registry contract for Runtime consumers. |
| [local-api.md](local-api.md) | Historical local API notes. |
| [recon-artifact-replay-guidance.md](recon-artifact-replay-guidance.md) | How to interpret recon debug traces. |
| [recon-product-validation-handoff.md](recon-product-validation-handoff.md) | Current product boundary for the promoted recon black-box row. |

## Integration Rules

- Platform copy must reflect the actual experiment status.
- Don't present smoke tests or negative results as validated audit methods.
- Runtime integration requires stable input/output contracts.
- Before changing schemas or report format across repositories, create a
  handoff note here first.
