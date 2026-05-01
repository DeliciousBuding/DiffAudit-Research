# Variation Query Contract Audit

> Status: blocked as of 2026-05-01.

## Verdict

```text
variation remains data/endpoint gated; no GPU or API task selected
```

The `variation` black-box line now has an executable query-contract audit:

```powershell
python -X utf8 scripts/audit_variation_query_contract.py `
  --query-root ..\Download\black-box\datasets\variation-query-set `
  --min-split-count 25
```

The current local state is blocked:

| Requirement | Current state |
| --- | --- |
| Query root | Missing at `<DOWNLOAD_ROOT>/black-box/datasets/variation-query-set`. |
| Member query images | `0`, below the 25-image scout minimum. |
| Nonmember query images | `0`, below the 25-image scout minimum. |
| Endpoint contract | Missing; `DIFFAUDIT_VARIATION_ENDPOINT` is not configured for this audit. |
| Promotion gate | Not reachable until a held-out member/nonmember query split and endpoint exist. |

## Contract

The minimum scout contract is:

- `member/` and `nonmember/` query-image directories.
- At least `25` real query images per split.
- A real endpoint contract, supplied by `--endpoint` or
  `DIFFAUDIT_VARIATION_ENDPOINT`.
- Low-FPR reporting remains primary; the first admitted packet must report
  strict-tail behavior on a held-out member/nonmember query split.

The audit intentionally does not create images and does not call any endpoint.
It only decides whether scheduling the variation line would answer a real
research question.

## Decision

- Do not schedule variation GPU/API execution now.
- Do not use flat synthetic query smokes as evidence.
- Variation can reopen only after the query set and endpoint contract are
  present.
- Until then, the next non-recon black-box slot should stay CPU-first and
  should not consume GPU.
