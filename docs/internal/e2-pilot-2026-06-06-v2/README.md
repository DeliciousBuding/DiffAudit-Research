# E2 Blind Review Pilot V2

> Date: 2026-06-06
> Scope: internal revised-codebook blind pilot; not external adjudication evidence.

This rerun uses the same 15 row template as the first E2 pilot, but reviewers
must apply the clarified codebook in
[`../e2-codebook-refinement-2026-06-06.md`](../e2-codebook-refinement-2026-06-06.md).

Purpose:

- test whether provenance and consumer/delta ambiguity is reduced;
- verify whether allowed wording raw agreement reaches `>= 0.70`;
- decide whether E2 can move toward `N=50` freeze preflight.

Current verdict:

- v2 passed the internal Go/No-Go gate.
- aggregation decision: `go-freeze-n50-preflight`
- allowed wording raw agreement: `0.9333`
- provenance agreement: `1.0`
- consumer/delta agreement: `0.8`
- next step:
  [`../e2-n50-freeze-preflight-2026-06-06/`](../e2-n50-freeze-preflight-2026-06-06/)

Inputs:

- `e2_blind_review_template.csv`
- `e2_false_promotion_pilot_rows.csv`
- `e2_reviewer_instructions_v2.md`

Expected reviewer files:

- `e2_blind_review_D.csv`
- `e2_blind_review_E.csv`
- `e2_blind_review_F.csv`

Aggregation command:

```powershell
python -X utf8 scripts\aggregate_e2_blind_review.py --pilot-dir docs\internal\e2-pilot-2026-06-06-v2
```

Boundary:

Do not cite this as a paper result. It is an internal codebook calibration pass
that supports only the E2 Go/No-Go decision.
