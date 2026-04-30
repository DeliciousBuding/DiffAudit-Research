# Black-Box Plan

## Status

- `recon`: strongest main black-box method, but public data limits strict paper-aligned claims.
- `CLiD`: useful supporting method, not promoted to headline.
- `variation`: API-only support; needs real query-image data for stronger claims.
- `semantic-auxiliary-classifier`: current alternative candidate.
- `H2 response-strength`: live candidate with positive non-overlap signal;
  frozen lowpass follow-up is positive-but-bounded on `DDPM/CIFAR10`; SD/CelebA
  text-to-image transfer is protocol-blocked.

## Next Action

Choose the next black-box slot after the H2 protocol block: CLiD, recon,
variation, or a stricter image-to-image H2 contract. Keep status synchronized
with [../../docs/evidence/reproduction-status.md](../../docs/evidence/reproduction-status.md).

## Current Status

Stable admitted baseline plus one live candidate. The current candidate is H2
response-strength; it is positive-but-bounded on `DDPM/CIFAR10`, but no GPU
task is active because the default SD/CelebA text-to-image contract is not H2
compatible.
