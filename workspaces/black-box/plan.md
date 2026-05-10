# Black-Box Plan

## Status

- `recon`: strongest main black-box method, but public data limits strict paper-aligned claims.
- `CLiD`: hold-candidate. The prompt-conditioned packet is strong and
  repeat-stable, but prompt controls and attribution block admission as general
  black-box evidence.
- `variation`: API-only support; executable query-contract audit is now
  blocked by missing member/nonmember query images and endpoint.
- `semantic-auxiliary-classifier`: negative-but-useful after low-FPR review;
  not selected for GPU.
- `H2 response-strength`: candidate-only with positive non-overlap signal;
  frozen lowpass follow-up is positive-but-bounded on `DDPM/CIFAR10`; SD/CelebA
  text-to-image transfer is protocol-blocked.
- `simple image-to-image distance`: bounded single-asset evidence on
  SD1.5/CelebA; not a product row and not portability evidence.

## Next Action

Recon product-row promotion is complete. The bounded public-100 step30 rerun
and artifact re-summarization now produce the admitted coherent
upstream-threshold packet (`AUC = 0.837`, `ASR = 0.74`, `TPR@1%FPR = 0.22`,
`TPR@0.1%FPR = 0.11`). The finite-tail confidence review keeps this row
admitted, but blocks wording that treats public-100 zero-FP evidence as
continuous sub-percent FPR calibration. Keep status synchronized with
[../../docs/evidence/recon-product-validation-result.md](../../docs/evidence/recon-product-validation-result.md)
and
[../../docs/evidence/recon-tail-confidence-review.md](../../docs/evidence/recon-tail-confidence-review.md).

## Current Status

Stable admitted baseline after product-consumable strengthening. `recon` remains
the admitted black-box row under the unified metric source. The H2
simple-distance product bridge comparison keeps that signal as Research
evidence only, and the second-asset portability preflight is blocked by missing
query-image/response-contract assets. Variation now has an executable query
contract audit, but it is blocked by missing real member/nonmember query images
and endpoint.

The black-box response-contract acquisition audit also closes as
`needs-assets`: SD1.5/CelebA image-to-image is CPU-eligible but is the same
asset family as the existing simple-distance evidence, while variation and
Kandinsky/Pokemon lack the required split/endpoint contract.
The minimum second-asset package is now specified in
[../../docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](../../docs/evidence/blackbox-response-contract-asset-acquisition-spec.md).
The executable package-level preflight confirms that the current
Kandinsky/Pokemon supplementary root is not enough: it has no member/nonmember
query package, endpoint contract, response manifest, or responses. See
[../../docs/evidence/blackbox-response-contract-package-preflight.md](../../docs/evidence/blackbox-response-contract-package-preflight.md).
The repository-level discovery pass generalizes that finding across the current
black-box package roots: `Download/black-box/datasets` has no package ids,
`Download/black-box/supplementary` has only `clid-mia-supplementary` and
`recon-assets` as supplementary-only directories, and no ready paired
response-contract package exists. See
[../../docs/evidence/blackbox-response-contract-discovery.md](../../docs/evidence/blackbox-response-contract-discovery.md).
Do not release a black-box response-contract GPU task until a candidate package
passes that CPU preflight.

The semantic-auxiliary classifier lane also fails promotion:
best AUC gain over `mean_cos` is `0.001953`, below the `0.01` gate. The next
GPU candidate is not selected; CLiD remains hold-candidate. The current
Research-level resting-state audit records that no black-box CPU sidecar is
currently reducible without new assets or a new protocol. See
[../../docs/evidence/research-resting-state-audit-20260510.md](../../docs/evidence/research-resting-state-audit-20260510.md).
