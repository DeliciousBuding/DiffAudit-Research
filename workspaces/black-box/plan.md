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

Freeze the CPU contract for a recon product-consumable validation packet:
packet identity, strict-tail metric completeness, and Platform/Runtime handoff
boundary. Keep status synchronized with
[../../docs/evidence/non-clid-blackbox-reselection.md](../../docs/evidence/non-clid-blackbox-reselection.md).

## Current Status

Stable admitted baseline plus one selected strengthening lane. `recon` remains
admitted and is now selected for product-consumable strengthening. H2 is held
for image-conditioned portability; CLiD is hold-candidate; variation remains
data-gated.
