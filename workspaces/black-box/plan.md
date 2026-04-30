# Black-Box Plan

## Status

- `recon`: strongest main black-box method, but public data limits strict paper-aligned claims.
- `CLiD`: useful supporting method, not promoted to headline.
- `variation`: API-only support; needs real query-image data for stronger claims.
- `semantic-auxiliary-classifier`: current alternative candidate.
- `H2 response-strength`: live candidate with positive non-overlap signal;
  next step is stable runner promotion before one bounded 512 / 512 validation.

## Next Action

Promote the H2 response-strength validation runner out of archived execution
scripts into a stable script or CLI entrypoint. After that, run one bounded
512 / 512 non-overlap validation if GPU budget is available. Keep status
synchronized with [../../docs/evidence/reproduction-status.md](../../docs/evidence/reproduction-status.md).

## Current Status

Stable admitted baseline plus one live candidate. The current candidate is H2
response-strength; it remains below admitted evidence until the next bounded
validation passes its low-FPR gate.
