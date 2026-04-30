# Black-Box Plan

## Status

- `recon`: strongest main black-box method, but public data limits strict paper-aligned claims.
- `CLiD`: useful supporting method, not promoted to headline.
- `variation`: API-only support; needs real query-image data for stronger claims.
- `semantic-auxiliary-classifier`: current alternative candidate.
- `H2 response-strength`: live candidate with positive non-overlap signal;
  raw-primary 512 / 512 validation is negative-but-useful. Mid-band lowpass
  recovered strict-tail signal on the saved cache; the follow-up contract is
  frozen in the evidence docs.

## Next Action

Review whether one second-packet lowpass H2 follow-up is worth running under
[../../docs/evidence/h2-lowpass-followup-contract.md](../../docs/evidence/h2-lowpass-followup-contract.md).
Keep status synchronized with [../../docs/evidence/reproduction-status.md](../../docs/evidence/reproduction-status.md).

## Current Status

Stable admitted baseline plus one live candidate. The current candidate is H2
response-strength; raw-primary validation failed its strict low-FPR gate, so no
GPU task is active unless the cutoff-0.50 follow-up contract is explicitly
selected.
