# I-B Shadow-Local GSA Risk Preflight

Date: 2026-05-15

## Verdict

`blocked preflight; true shadow-local GSA-only risk records exist; PIA shadow-local risk still missing; no training run; no GPU release`

This CPU-only preflight converts the existing GSA loss-score export into
per-shadow risk records using each shadow checkpoint's own member/nonmember
split. It reduces the I-B blocker from "no true shadow-local risk records" to
"GSA-only shadow-local risk records exist, but the frozen two-surface PIA+GSA
contract is still incomplete."

Machine-readable artifact:
[`workspaces/defense/artifacts/ib-shadow-local-gsa-risk-preflight-20260515.json`](../../workspaces/defense/artifacts/ib-shadow-local-gsa-risk-preflight-20260515.json).
The per-shadow JSONL and identity-file outputs are local regenerated artifacts
under `workspaces/defense/artifacts/ib-shadow-local-gsa-risk-preflight-20260515/`;
the public repository tracks only the curated flat JSON summary.
Validator: `scripts/validate_ib_shadow_local_gsa_risk_preflight.py`.

## Question

Can existing local GSA loss-score exports produce true shadow-local risk
records for I-B defended-shadow identity selection without launching training
or pretending the older target-risk remap is shadow-local scoring?

## Hypothesis

If at least two shadows have member and nonmember GSA loss-score tensors plus
record IDs from their own shadow checkpoint/split, a CPU preflight can produce
true shadow-local GSA-only top-k identity candidates. This is useful only as a
blocker reduction unless shadow-local PIA records are also produced or the
weaker GSA-only contract is explicitly approved.

## Falsifier

If fewer than two shadows expose enough unique member and nonmember GSA records,
or if the output writes duplicate identity IDs into top-k files, the GSA-only
preflight remains blocked.

## Inputs

- GSA export summary:
  `workspaces/white-box/runs/gsa-loss-score-export-targeted-full-overlap-20260418-r1/summary.json`
- Source exports:
  `shadow_01_member`, `shadow_01_non_member`, `shadow_02_member`,
  `shadow_02_non_member`, `shadow_03_member`, `shadow_03_non_member`
- `top_k`: `32`
- device: CPU

## Result

All three shadows have enough unique GSA member and nonmember records for a
GSA-only k32 preflight. The loss-score direction is `negated` for all three
shadows, consistent with lower raw loss being more member-like. The generated
identity files are de-duplicated by `split_index` before top-k selection.

| Shadow | Status | Records member/nonmember | Unique member/nonmember | Disjoint unique nonmember | Duplicate suffix IDs member/nonmember | Top-k member mean risk | Matched nonmember mean risk |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `shadow-01` | `gsa-risk-ready` | `83 / 80` | `80 / 78` | `76` | `3 / 2` | `0.810994` | `0.805078` |
| `shadow-02` | `gsa-risk-ready` | `81 / 77` | `80 / 75` | `75` | `1 / 2` | `0.808642` | `0.798702` |
| `shadow-03` | `gsa-risk-ready` | `70 / 76` | `69 / 74` | `71` | `1 / 2` | `0.771875` | `0.766036` |

The output explicitly records:

- `true_shadow_local_gsa_risk_scoring = true`
- `true_shadow_local_pia_gsa_risk_scoring = false`
- `gsa_risk_status = complete`
- `status = blocked`
- `gpu_release = none`
- `admitted = false`

## Boundary

This artifact does not run defended-shadow training, does not export
defended-shadow threshold references, does not measure adaptive attackers, does
not measure retained utility, and does not change Platform/Runtime admitted
rows. It also does not satisfy the original PIA+GSA two-surface risk contract:
shadow-local PIA risk records remain missing.

The next valid I-B decision is narrow: either produce shadow-local PIA records
against the same shadow-local identity contract, or explicitly approve a weaker
GSA-only defended-shadow identity contract before any tiny training run.

## Validation

```powershell
python -X utf8 -m diffaudit prepare-shadow-local-gsa-risk-preflight --workspace workspaces/defense/artifacts/ib-shadow-local-gsa-risk-preflight-20260515 --gsa-loss-score-summary workspaces/white-box/runs/gsa-loss-score-export-targeted-full-overlap-20260418-r1/summary.json --shadow-ids shadow-01,shadow-02,shadow-03 --top-k 32 --provenance-status workspace-verified
python -X utf8 scripts/validate_ib_shadow_local_gsa_risk_preflight.py
```
