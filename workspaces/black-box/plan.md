# Black-Box Plan

## Status

- `recon`: strongest main black-box method, but public data limits strict paper-aligned claims.
- `CLiD`: next selected bounded lane; local bridge preparation succeeded, and
  bridge contract validation passed. Score-summary gate is defined and wired
  into artifact summarization; the 8/8 tiny score bridge is reusable but not
  promotable.
- `variation`: API-only support; needs real query-image data for stronger claims.
- `semantic-auxiliary-classifier`: current alternative candidate.
- `H2 response-strength`: live candidate with positive non-overlap signal;
  frozen lowpass follow-up is positive-but-bounded on `DDPM/CIFAR10`; SD/CelebA
  text-to-image transfer is protocol-blocked.

## Next Action

Scope a 100 member / 100 nonmember CLiD score bridge under the frozen schema.
Keep status synchronized with
[../../docs/evidence/reproduction-status.md](../../docs/evidence/reproduction-status.md).

## Current Status

Stable admitted baseline plus one selected next lane. `recon` remains admitted;
H2 is held for image-conditioned portability; CLiD is the next bounded
prompt-conditioned black-box lane. The tiny bridge passed schema validation but
failed promotion by sample count.
