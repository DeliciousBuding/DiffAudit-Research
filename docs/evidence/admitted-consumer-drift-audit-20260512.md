# Admitted Consumer Drift Audit

Date: 2026-05-12

## Verdict

`synchronized; no drift; no GPU release; no Platform/Runtime schema change`

The audit checked whether recent candidate closures and hold decisions had
silently changed the system-consumable evidence boundary. They had not. The
admitted bundle still contains only the five reviewed consumer rows, and all
candidate, hold, supporting-reference, and needs-assets rows remain excluded.

## Question

After mid-frequency residual, SecMI consumer-contract review, I-B protocol
audit, and I-C same-spec feasibility closure, did any Research-only or
candidate-only result drift into Platform/Runtime-consumable evidence?

## Falsifier

This audit would fail if any of the following were true:

- an admitted-row validator failed;
- `admitted-evidence-bundle.json` admitted a candidate, hold, support-only, or
  needs-assets row;
- the bundle row count changed without an explicit promotion note;
- the recon product evidence card drifted from the reviewed admitted row;
- SecMI, CLiD, I-B, or another candidate lane became consumer-visible without a
  handoff and schema decision.

None of these conditions occurred.

## Commands

```powershell
python -X utf8 scripts/validate_attack_defense_table.py
python -X utf8 scripts/export_admitted_evidence_bundle.py --check
python -X utf8 scripts/export_recon_product_evidence_card.py --check
python -X utf8 scripts/validate_secmi_supporting_contract.py
python -X utf8 scripts/validate_clid_identity_boundary.py
python -X utf8 scripts/validate_ib_adaptive_defense_contract.py
```

All commands passed.

## Reviewed Artifacts

- `workspaces/implementation/artifacts/admitted-evidence-bundle.json`
- `workspaces/implementation/artifacts/recon-product-evidence-card.json`
- [admitted-results-summary.md](admitted-results-summary.md)
- [../product-bridge/README.md](../product-bridge/README.md)
- [secmi-consumer-contract-review-20260512.md](secmi-consumer-contract-review-20260512.md)
- [clid-image-identity-boundary-contract-20260511.md](clid-image-identity-boundary-contract-20260511.md)
- [ib-adaptive-defense-contract-20260511.md](ib-adaptive-defense-contract-20260511.md)
- [ic-same-spec-evaluator-feasibility-scout-20260512.md](ic-same-spec-evaluator-feasibility-scout-20260512.md)

## Consumer Boundary

Platform and Runtime may consume only the admitted bundle rows:

| Row | Consumer status |
| --- | --- |
| `recon` | admitted |
| `PIA baseline` | admitted |
| `PIA defended` | admitted |
| `GSA` | admitted |
| `DPDM W-1` | admitted |

The bundle remains:

- `schema`: `diffaudit.admitted_evidence_bundle.v1`
- `status`: `admitted-only`
- `audience`: `platform-runtime`
- `row_count`: `5`

The recon product evidence card remains the admitted black-box card with
finite-tail caveats and the reviewed `100 / 100` public packet:

| Metric | Value |
| --- | --- |
| `AUC` | `0.837` |
| `ASR` | `0.74` |
| `TPR@1%FPR` | `0.22` |
| `TPR@0.1%FPR` | `0.11` |

## Explicitly Excluded

These rows remain outside admitted product evidence:

- ReDiffuse exact replay and direct-distance packets;
- SecMI stat and NNS supporting-reference rows;
- CDI/TMIA-DM/PIA tri-score fusion;
- cross-box score sharing and cross-permission probes;
- H2/simple-distance and mid-frequency residual candidates;
- CLiD prompt-conditioned diagnostics;
- GSA loss-score LR and diagonal-Fisher successor attempts;
- black-box response-contract package work until real query/response assets
  exist;
- I-B risk-targeted unlearning until defended-shadow and adaptive-attacker
  contracts exist;
- I-C translated-alias / same-spec feasibility work until a same-spec evaluator
  and matched comparator contract exist.

## Decision

Do not update `docs/evidence/admitted-results-summary.md` and do not change
Platform or Runtime schemas. The admitted consumer boundary is already guarded
by validators and exporters. The next Research slot should select a scientific
question with decision value, not repeat another no-drift audit unless a guard
fails.
