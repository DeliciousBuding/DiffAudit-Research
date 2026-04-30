# Black-Box Plan

## Status

- `recon`: strongest main black-box method, but public data limits strict paper-aligned claims.
- `CLiD`: useful supporting method, not promoted to headline.
- `variation`: API-only support; needs real query-image data for stronger claims.
- `semantic-auxiliary-classifier`: current alternative candidate.
- `H2 response-strength`: live candidate with positive non-overlap signal;
  frozen lowpass follow-up is positive-but-bounded on `DDPM/CIFAR10`.

## Next Action

Decide whether the next black-box research slot should define a cross-asset H2
contract or switch back to `recon` / API-only candidate work. Keep status
synchronized with [../../docs/evidence/reproduction-status.md](../../docs/evidence/reproduction-status.md).

## Current Status

Stable admitted baseline plus one live candidate. The current candidate is H2
response-strength; it is positive-but-bounded on `DDPM/CIFAR10`, but no GPU
task is active because the next claim requires cross-asset portability rather
than more same-family scaling.
