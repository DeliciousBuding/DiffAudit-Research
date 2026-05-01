# Black-Box Plan

## Status

- `recon`: strongest main black-box method, but public data limits strict paper-aligned claims.
- `CLiD`: hold-candidate. The prompt-conditioned packet is strong and
  repeat-stable, but prompt controls and attribution block admission as general
  black-box evidence.
- `variation`: API-only support; needs real query-image data for stronger claims.
- `semantic-auxiliary-classifier`: current alternative candidate.
- `H2 response-strength`: live candidate with positive non-overlap signal;
  frozen lowpass follow-up is positive-but-bounded on `DDPM/CIFAR10`; SD/CelebA
  text-to-image transfer is protocol-blocked.

## Next Action

Recover or regenerate the recon public-100 score artifacts, then record the
strict-tail value with the updated metric-complete recon summary path. Keep
status synchronized with
[../../docs/evidence/recon-product-validation-contract.md](../../docs/evidence/recon-product-validation-contract.md).

## Current Status

Stable admitted baseline plus one selected strengthening lane. `recon` remains
admitted and is now selected for product-consumable strengthening. The next GPU
candidate is pending score-artifact restore or a bounded rerun. H2 is held for
image-conditioned portability; CLiD is hold-candidate; variation remains
data-gated.
