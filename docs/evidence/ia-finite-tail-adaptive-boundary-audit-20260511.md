# I-A Finite-Tail / Adaptive Boundary Audit

Date: 2026-05-11

## Verdict

`synchronized`; no GPU task is released.

The post-Fisher reselection selected a CPU-only I-A boundary audit before
opening another model lane. The audit found no admitted/candidate leakage in
the checked consumer surface and no immediate Platform/Runtime schema change.

## Checks

```powershell
python -X utf8 scripts/validate_attack_defense_table.py
python -X utf8 scripts/export_recon_product_evidence_card.py --check
python -X utf8 scripts/validate_secmi_supporting_contract.py
```

All three checks passed.

Manual public-surface review covered:

- [admitted-results-summary.md](admitted-results-summary.md)
- [admitted-evidence-bundle-20260511.md](admitted-evidence-bundle-20260511.md)
- [../product-bridge/README.md](../product-bridge/README.md)
- [../../README.md](../../README.md)

## Findings

- Admitted rows remain limited to the checked consumer set: recon, PIA
  baseline, PIA defended, GSA, and DPDM W-1.
- PIA strict-tail language still states that `TPR@0.1%FPR` is a finite
  empirical point over 512 target nonmembers, not calibrated continuous
  sub-percent FPR.
- PIA defended remains a provisional defended comparator with bounded
  repeated-query adaptive review, not validated privacy protection.
- SecMI remains a Research-only supporting reference guarded by
  `validate_secmi_supporting_contract.py`.
- ReDiffuse, tri-score, cross-box fusion, GSA LR, H2/simple-distance, CLiD,
  and response-contract acquisition remain outside admitted evidence.

## Next Action

Do not spend the next CPU slot on another no-drift governance pass unless a
validator fails. The next scientific slot should move to a genuinely new
cross-box successor scoping question or another bounded hypothesis that can
change project-level story without requiring immediate GPU.
