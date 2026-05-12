# SecMI Consumer Contract Review

## Verdict

`structural-support-only; not system-consumable; no GPU release`

SecMI remains a strong full-split gray-box supporting reference, but it should
not be added to the admitted Platform/Runtime consumer bundle. The blocker is
not metric strength. The blocker is the missing consumer contract: adaptive
comparability, product-facing NNS semantics, admitted-row provenance language,
and structured bundle compatibility are not satisfied.

## Question

Can SecMI be represented as a system-consumable gray-box evidence row under the
same quality bar as admitted PIA, or must it remain `research-support-only`?

## Inputs

- [secmi-full-split-admission-boundary-review.md](secmi-full-split-admission-boundary-review.md)
- [secmi-admission-contract-hardening-20260511.md](secmi-admission-contract-hardening-20260511.md)
- [admitted-results-summary.md](admitted-results-summary.md)
- [../product-bridge/admitted-evidence-bundle.md](../product-bridge/admitted-evidence-bundle.md)
- `workspaces/gray-box/artifacts/secmi-full-split-admission-boundary-20260511.json`
- `workspaces/gray-box/artifacts/secmi-admission-contract-hardening-20260511.json`
- `workspaces/implementation/artifacts/admitted-evidence-bundle.json`

No checkpoint was loaded and no GPU task was run.

## Metrics Reviewed

| Row | Samples per split | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | --- | --- | --- | --- | --- |
| PIA admitted baseline | `512` | `0.841339` | `0.786133` | `0.058594` | `0.011719` |
| SecMI stat | `25,000` | `0.885833` | `0.815400` | `0.093960` | `0.007720` |
| SecMI NNS auxiliary head | `25,000` | `0.946286` | `0.879275` | `0.400450` | `0.114000` |

These metrics are strong enough for Research supporting evidence. They are not
enough to make a consumer row.

## Gate Review

| Gate | Status | Reason |
| --- | --- | --- |
| Consumer row semantics | blocked | SecMI stat and NNS are currently modeled as `research-support-only`; there is no admitted-row boundary text equivalent to PIA. |
| NNS product-facing meaning | blocked | NNS is an auxiliary head. The repository does not define what a product should claim from this score or how it differs from the stat head. |
| Adaptive comparability | blocked | Admitted PIA rows carry bounded repeated-query review metadata. SecMI has no comparable adaptive check. |
| Finite-tail language | partially available | The `25k` denominator is strong, but it is not wired into an admitted bundle row with consumer caveats. |
| Cost/provenance structure | partially available | The hardening artifact records `t_sec`, `k`, `batch_size`, and elapsed time, but source/provenance language is still not aligned with admitted gray-box consumer rows. |
| Platform/Runtime schema fit | blocked | Adding SecMI as-is would either violate the admitted bundle contract or require a new consumer-row schema. |

## Decision

SecMI must remain `research-support-only`.

The strongest NNS row is valuable for papers and internal prioritization, but
it should not become a product-facing row until a separate schema and wording
decision exists for auxiliary heads. The stat row is easier to explain, but it
still lacks the admitted-row adaptive and provenance contract. Therefore the
gap is structural, not a missing table entry.

## Handoff

No Platform or Runtime schema change is recommended.

If a future product handoff wants SecMI, the correct request is not "add the
NNS metrics to the admitted bundle." The correct request is a new
`supporting-reference` or `auxiliary-graybox` consumer type with:

- explicit UI wording for auxiliary heads;
- finite-tail denominators and caveats;
- structured cost/provenance;
- adaptive-review status that can be displayed as missing or completed;
- a rule that supporting rows cannot be ranked beside admitted attacks unless
  promoted by a separate review.

## Next Action

Keep validators active and move on. The next research task should not run more
SecMI metrics unless a new consumer schema or adaptive-review protocol is
frozen first.
