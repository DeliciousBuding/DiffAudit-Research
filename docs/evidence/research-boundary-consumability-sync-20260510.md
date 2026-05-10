# Research Boundary-Consumability Sync

> Date: 2026-05-10
> Status: synchronized; no GPU release

## Question

After the recent candidate closures, can downstream consumers read the Research
state without confusing internal candidates with admitted evidence?

## Scope

This is a CPU-only documentation and evidence-boundary review. It does not
change metrics, run models, or update Platform/Runtime schemas.

Reviewed sources:

- [admitted-results-summary.md](admitted-results-summary.md)
- [reproduction-status.md](reproduction-status.md)
- [innovation-evidence-map.md](innovation-evidence-map.md)
- [research-boundary-card.md](research-boundary-card.md)
- [../product-bridge/README.md](../product-bridge/README.md)
- [blackbox-response-contract-second-asset-intake-20260511.md](blackbox-response-contract-second-asset-intake-20260511.md)
- [graybox-triscore-truth-hardening-review.md](graybox-triscore-truth-hardening-review.md)
- [rediffuse-exact-replay-packet.md](rediffuse-exact-replay-packet.md)

## Consumer Boundary

| Evidence class | Current rows | Consumer rule |
| --- | --- | --- |
| Admitted evidence | `recon`, `PIA baseline`, `PIA defended`, `GSA + DPDM W-1` | May be used by Runtime/Platform as verified evidence with stated limitations. `PIA defended` is the stochastic-dropout comparator row. |
| Internal candidate | ReDiffuse, CDI/TMIA-DM/PIA tri-score, cross-box fusion, H2/simple-distance, CLiD | May guide Research planning and internal comparison only. Do not expose as admitted audit evidence. |
| Needs assets | Black-box second response-contract package, variation real-query line, simple-distance portability | Do not run GPU or productize until package/query/response contracts pass CPU preflight. |
| Negative-but-useful | GSA loss-score LR rescue, semantic-aux low-FPR, several activation/trajectory scouts | Preserve as pruning evidence; do not revive without a distinct hypothesis. |

## Verdict

`synchronized`.

The admitted set remains unchanged:

- black-box: `recon`
- gray-box: `PIA baseline` and `PIA defended`
- white-box: `GSA + DPDM W-1`

Recent positive candidates remain explicitly non-admitted:

- ReDiffuse exact replay: modest AUC, weak strict-tail evidence.
- Gray-box tri-score: AUC and low-FPR fields beat admitted PIA across frozen
  packets, but the contract is internal-only and ASR is not stable enough for a
  support claim.
- Cross-box fusion: useful AUC movement, no stable low-FPR dominance.
- H2/simple-distance: bounded single-asset evidence only; no portability.

Recent blockers remain explicit:

- Black-box second response-contract package is still `needs-assets`.
- No current GPU candidate is selected.
- No Platform or Runtime schema change is authorized.

## Next Action

Do not open a GPU task from this sync. The next model task must be one of:

- a real second response-contract package that passes CPU preflight,
- a genuinely distinct white-box observable with low-FPR primary gate,
- a new I-B/I-C/I-D successor hypothesis with falsifier and existing assets,
- or another system-consumable boundary sync if downstream docs drift.

## Platform and Runtime Impact

No schema change. Platform and Runtime should continue consuming only the
admitted rows listed in [admitted-results-summary.md](admitted-results-summary.md)
and the recon product card under `docs/product-bridge/`.
