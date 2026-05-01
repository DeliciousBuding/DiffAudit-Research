# H2 Simple-Distance Product Bridge Comparison

This note compares the new H2 image-to-image simple-distance evidence against
the admitted recon black-box product row. It decides whether the simple-distance
line is ready for Platform consumption.

## Verdict

```text
not product-row ready; keep as bounded Research evidence and test portability next
```

The simple-distance admission packet is a real black-box signal on the current
SD1.5/CelebA-style image-to-image contract. It is stronger than the admitted
recon row on headline AUC, ASR, and finite zero-false-positive tail. It is not
yet a product row because the evidence base is smaller, single-asset, and not
represented in the unified attack-defense table schema.

Recon remains the admitted black-box Platform row.

## Side-by-Side Status

| Field | Recon product row | H2 img2img simple distance |
| --- | --- | --- |
| Product status | admitted Platform-consumable row | Research-side bounded evidence |
| Evidence anchor | [../evidence/recon-product-validation-result.md](../evidence/recon-product-validation-result.md) | [../evidence/h2-img2img-simple-distance-admission-result.md](../evidence/h2-img2img-simple-distance-admission-result.md) |
| Product handoff | [recon-product-validation-handoff.md](recon-product-validation-handoff.md) | this comparison only |
| Unified table | yes | no |
| Sample size | 100 member / 100 nonmember | 25 member / 25 nonmember |
| Asset family | Stable Diffusion v1.5 + DDIM recon packet | Stable Diffusion v1.5 + CelebA-style image-to-image |
| AUC | 0.837 | 0.8768 |
| ASR | 0.74 | 0.84 |
| Strict-tail result | 11/100 TP at 0 FP | 11/25 TP at 0 FP |
| Low-FPR interpretation | zero-FP empirical tail on 100 nonmembers | zero-FP empirical tail on 25 nonmembers |
| Portability | product-controlled public-100 packet | single-asset only |
| Runtime schema impact | none; existing fields | none selected |

## Decision Rationale

Simple-distance should not be promoted directly despite better point metrics:

- The 25/25 packet has less tail resolution than recon's 100/100 packet.
- It is tied to one image-to-image response contract and one asset family.
- It is not yet exported through the unified attack-defense table.
- Its current score is a one-feature response-distance statistic, not an
  H2 response-strength curve.
- Platform needs stable limitations and artifact semantics before adding a row.

The result does justify continued Research investment:

- The effect survived three non-overlapping packets.
- The 25/25 packet passed a predeclared AUC and zero-FP gate.
- Same-cache H2 logistic did not beat simple distance, so the simpler statistic
  is the honest mainline.
- The signal is cheap enough to retest under a portability preflight before any
  product integration work.

## Product Rule

Platform may mention this only as internal Research progress, not as an
available audit method.

Allowed internal wording:

- "Research has identified a bounded image-to-image response-distance signal on
  the SD1.5/CelebA-style contract."
- "The result motivates a portability check before product integration."

Blocked public/product wording:

- Do not call it a new Platform attack row.
- Do not claim conditional-diffusion-general privacy risk.
- Do not say H2 response-strength has transferred to SD/CelebA.
- Do not compare `TPR@0.1%FPR` as calibrated sub-percent FPR; both rows report
  finite zero-false-positive empirical tails.

## Promotion Gate

The simple-distance line can be reconsidered for a product row only after all
of the following are true:

| Gate | Requirement |
| --- | --- |
| Portability | A second asset-family or endpoint contract passes a predeclared packet. |
| Scale | At least 100 member / 100 nonmember or an explicit reason why a smaller packet is product-acceptable. |
| Schema | A compact artifact summary maps into `auc`, `asr`, `tpr_at_1pct_fpr`, `tpr_at_0_1pct_fpr`, `quality_cost`, `evidence_level`, `boundary`, and `source`. |
| Boundary | The result remains separate from H2 response-strength claims. |
| Product copy | Limitations are written before Platform UI consumption. |

## Next Research Step

Do not schedule another same-asset GPU packet. The next useful CPU task is a
second-asset portability preflight that answers whether the current local assets
can support a valid image-to-image or equivalent repeated-response contract.

If no second asset is available, return to recon product-consumable
strengthening rather than scaling the same single-asset signal.
