# ReDiffuse ResNet Contract Scout

> Date: 2026-05-10
> Status: blocked-by-contract-mismatch; no GPU release

## Question

Can the current Research ReDiffuse `resnet` scoring mode be treated as an exact
replay of the collaborator `nns_attack` contract?

## Method

CPU-only static contract scout:

```powershell
python -X utf8 scripts\review_rediffuse_resnet_contract_scout.py
```

The scout reads the collaborator `attack.py` from the portable ReDiffuse bundle
layout and compares its second-stage ResNet scorer semantics against
`src/diffaudit/attacks/rediffuse_adapter.py`. It does not score samples, train a
scorer, or use GPU.

## Result

| Gate | Value |
| --- | --- |
| Collaborator contract detected | true |
| Research adapter contract detected | true |
| Semantic mismatch count | `2` |
| Exact replay ready | false |
| Release gate passed | false |

Detected mismatches:

- The collaborator `nns_attack` initializes `test_acc_best = 0` and writes
  `test_acc_best_ckpt` when `test_acc > test_acc_best`, but never updates
  `test_acc_best`. The current Research adapter updates `best_acc` and restores
  the true best held-out epoch.
- The collaborator flow negates member and nonmember logits before ROC and its
  ROC treats lower scores as member-like. The current Research adapter returns
  unnegated logits into project metric helpers where higher scores are treated
  as member-like.

## Verdict

`blocked-by-contract-mismatch`.

The previous 750k ResNet parity packet is still useful as a bounded Research
variant, but it is not exact collaborator replay. Therefore the 800k ReDiffuse
shortcut remains closed: checkpoint compatibility plus the current `resnet`
mode is not enough to release a GPU metrics packet.

## Next Action

If ReDiffuse remains worth pursuing, implement an explicit exact replay mode
that mirrors the collaborator checkpoint-selection and score-orientation
contract, then rerun a tiny CPU characterization before any GPU packet. If that
is not worth the complexity, keep ReDiffuse closed as candidate-only and move to
a different lane.

## Platform and Runtime Impact

No Platform or Runtime changes are needed.
