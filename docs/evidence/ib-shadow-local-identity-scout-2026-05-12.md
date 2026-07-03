# I-B Shadow-Local Identity Scout

Date: 2026-05-12

## Verdict

`blocked semantic scout; two-shadow remap mechanically possible; no GPU release`

The current target k32 identity contract cannot train defended shadows because
the target forget IDs are mostly absent from the shadow member datasets. This
CPU scout checks the next narrower question: can existing target-level risk
records be filtered into each shadow split to form a shadow-local-looking k32
identity contract?

Result: `shadow-01` and `shadow-02` can mechanically provide `32` member and
`32` nonmember IDs after filtering target-level risk records into their own
member/nonmember splits. `shadow-03` is blocked because it has only `31`
target-risk-ranked member IDs in its member split. The machine-readable
artifact still keeps top-level `status=blocked` because this is a
target-risk-filtered remap, not true shadow-local PIA/GSA risk scoring.

Artifact:
[`workspaces/defense/artifacts/ib-shadow-local-identity-scout-20260512.json`](../../workspaces/defense/artifacts/ib-shadow-local-identity-scout-20260512.json).
Validator: `scripts/validate_ib_shadow_local_identity_scout.py`.

## Question

Can existing GSA shadow assets support a defensible shadow-local identity
contract that unblocks I-B, without fabricating a fake training contract?

## Hypothesis

If at least two shadows have `top_k=32` target-risk-ranked member IDs inside
their shadow member split and `top_k=32` target-risk-ranked nonmember IDs
inside their shadow nonmember split, then a two-shadow remap is mechanically
possible. That still does not prove true shadow-local risk scoring unless the
risk records are recomputed from each shadow model/split.

## Falsifier

If fewer than two shadows expose both `32` member and `32` nonmember filtered
records, even a remapped contract is blocked. If the only available scores are
target-level records, a true shadow-local claim remains blocked even when the
mechanical count passes.

## Result

The scout used existing local assets only:

- assets root: `workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1`
- member risk records: `workspaces/defense/runs/risk-targeted-unlearning-prep-full-overlap-20260418-r1/member-risk-records.jsonl`
- nonmember risk records: `workspaces/defense/runs/risk-targeted-unlearning-prep-full-overlap-20260418-r1/nonmember-risk-records.jsonl`
- shadow IDs: `shadow-01`, `shadow-02`, `shadow-03`
- `top_k`: `32`

Observed target-risk-record availability after filtering into each shadow split:

| Shadow | Available member records | Available nonmember records | Selected member IDs | Selected nonmember IDs | Mechanical result |
| --- | ---: | ---: | ---: | ---: | --- |
| `shadow-01` | `42` | `42` | `32/32` | `32/32` | candidate remap |
| `shadow-02` | `44` | `34` | `32/32` | `32/32` | candidate remap |
| `shadow-03` | `31` | `33` | `31/32` | `32/32` | blocked |

Top-k mean target-level risks:

| Shadow | Member mean | Nonmember mean |
| --- | ---: | ---: |
| `shadow-01` | `0.546333` | `0.569835` |
| `shadow-02` | `0.574583` | `0.506642` |
| `shadow-03` | `0.505353` over `31` member IDs | `0.538304` |

## Boundary

This scout does not write new forget files, execute training, export
defended-shadow threshold references, measure retained utility, run adaptive
attackers, or admit a defense result. It deliberately blocks the stronger
claim `true shadow-local risk scoring` because the risk records came from the
target-level PIA/GSA full-overlap prep.

The decision value is narrow but useful: the line no longer needs to guess
whether a two-shadow remap is possible. It is possible for `shadow-01` and
`shadow-02`, but using it for training requires an explicit semantic decision.
The cleaner path is to recompute shadow-local PIA/GSA risk records; the faster
path is to approve the two-shadow remap as a weaker contract and label all
downstream results accordingly.

## Validation

```powershell
conda run -n diffaudit-research python -X utf8 -m diffaudit prepare-shadow-local-identity-scout --workspace workspaces/defense/artifacts/ib-shadow-local-identity-scout-20260512 --assets-root workspaces/white-box/assets/gsa-cifar10-1k-3shadow-epoch300-rerun1 --member-risk-records workspaces/defense/runs/risk-targeted-unlearning-prep-full-overlap-20260418-r1/member-risk-records.jsonl --nonmember-risk-records workspaces/defense/runs/risk-targeted-unlearning-prep-full-overlap-20260418-r1/nonmember-risk-records.jsonl --shadow-ids shadow-01,shadow-02,shadow-03 --top-k 32 --provenance-status workspace-verified
conda run -n diffaudit-research python scripts/validate_ib_shadow_local_identity_scout.py
```
