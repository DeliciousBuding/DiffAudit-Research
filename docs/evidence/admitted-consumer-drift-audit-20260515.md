# Admitted Consumer Drift Audit

Date: 2026-05-15

## Verdict

`synchronized / admitted-only boundary intact / no schema change / no GPU release`

This Lane C audit checks whether the 2026-05-15 watch, watch-plus,
support-only, and candidate-only results changed the Platform/Runtime
consumer boundary. They did not. The admitted bundle still contains only the
five reviewed consumer rows, and recent defense, cross-modal, score-packet,
paper-source, withdrawn, and artifact-incomplete lines remain excluded.

## Question

After the DualMD/DistillMD, DIFFENCE, MIAHOLD/HOLD++, Quantile Diffusion MIA,
Noise Aggregation, ReproMIA, DMin, ELSA, Memorization Anisotropy, FERMI,
DurMI, GenAI Confessions, SimA, FMIA, CLiD, StablePrivateLoRA, MIDM, GGDM,
Diffusion Memorization, Tracing the Roots, and related 2026-05-15 gates, did
any Research-only evidence become Platform/Runtime-consumable?

## Falsifier

This audit would fail if any of the following were true:

- an admitted-row validator failed;
- `admitted-evidence-bundle.json` admitted a candidate, watch, support-only,
  withdrawn, defense-watch, related-method, or artifact-incomplete row;
- the bundle row count changed without a reviewed promotion note;
- the recon product evidence card drifted from the admitted black-box row;
- SecMI, CLiD, I-B, or another guarded boundary became consumer-visible
  without a product-bridge handoff and schema decision.

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

All commands passed on 2026-05-15.

## Observed Consumer Bundle

`workspaces/implementation/artifacts/admitted-evidence-bundle.json` remains:

- `schema`: `diffaudit.admitted_evidence_bundle.v1`
- `status`: `admitted-only`
- `audience`: `platform-runtime`
- `row_count`: `5`

Platform and Runtime may consume only these rows:

| Row | Consumer status |
| --- | --- |
| `recon` | admitted |
| `PIA baseline` | admitted |
| `PIA defended` | admitted |
| `GSA` | admitted |
| `DPDM W-1` | admitted |

The recon product evidence card still points to the admitted black-box packet
with `AUC = 0.837`, `ASR = 0.74`, `TPR@1%FPR = 0.22`, and
`TPR@0.1%FPR = 0.11`.

## Explicitly Excluded

The following recent lines remain outside admitted product evidence:

- defense watch-plus lines: DualMD/DistillMD, DIFFENCE, MIAHOLD/HOLD++, and
  StablePrivateLoRA;
- score-packet or feature-packet candidates: CLiD, Tracing the Roots, and the
  third-party Quantile/SecMI-style replay;
- paper-source, withdrawn, or artifact-incomplete watches: Noise Aggregation,
  ReproMIA, DMin, ELSA, Memorization Anisotropy, FERMI, SimA, FMIA, MIDM, and
  Diffusion Memorization;
- cross-modal or out-of-scope watches: DurMI, GGDM, SAMA, VidLeaks, and
  related TTS/audio, graph, DLM, or T2V evidence;
- black-box boundary watches without reusable response/score packets, such as
  GenAI Confessions.

These items may be cited as Research context, limitations, related work,
future work, or internal candidate comparison only. They must not produce a
Platform product row, Runtime schema field, recommendation rule, defense
claim, or new download/GPU task without a separate reviewed promotion.

## Decision

Do not update `docs/evidence/admitted-results-summary.md`, the admitted
machine-readable bundle, Platform schemas, Runtime schemas, or product copy
from the recent watch/candidate gates.

The next useful work should be a non-duplicate asset or mechanism with public
target identity, exact member/nonmember split, and reusable response/score
coverage. Do not repeat another no-drift audit unless a guard fails, a new
consumer-visible artifact appears, or a reviewed promotion is proposed.
