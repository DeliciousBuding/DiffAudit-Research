# Black-Box Plan

## Status

- `recon`: strongest main black-box method, but public data limits strict paper-aligned claims.
- `CLiD`: next selected bounded lane; local bridge preparation succeeded, and
  artifact-schema validation is the next CPU step.
- `variation`: API-only support; needs real query-image data for stronger claims.
- `semantic-auxiliary-classifier`: current alternative candidate.
- `H2 response-strength`: live candidate with positive non-overlap signal;
  frozen lowpass follow-up is positive-but-bounded on `DDPM/CIFAR10`; SD/CelebA
  text-to-image transfer is protocol-blocked.

## Next Action

Freeze the CLiD bridge output contract and low-FPR gate before any GPU packet.
Keep status synchronized with [../../docs/evidence/reproduction-status.md](../../docs/evidence/reproduction-status.md).

## Current Status

Stable admitted baseline plus one selected next lane. `recon` remains admitted;
H2 is held for image-conditioned portability; CLiD is the next CPU-first
prompt-conditioned black-box lane, with bridge preparation complete.
