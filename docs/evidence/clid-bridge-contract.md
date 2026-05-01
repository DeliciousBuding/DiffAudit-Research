# CLiD Bridge Contract

This note records the current CLiD local bridge contract. It is a preparation
gate for the next prompt-conditioned black-box lane, not benchmark evidence.

## Verdict

```text
prepared bridge contract is reusable
```

The first bridge contract review passed on `clid-local-bridge-preflight-20260501-r1`:

| Check | Result |
| --- | --- |
| `config.json` present and shaped | pass |
| `analysis.md` present | pass |
| localized upstream script present | pass |
| upstream script markers | pass |
| member metadata rows | 8 / 8 |
| member exported images | 8 / 8 |
| nonmember metadata rows | 8 / 8 |
| nonmember exported images | 8 / 8 |
| balanced export | pass |

The review command is:

```powershell
python scripts/review_clid_bridge_contract.py `
  --run-root workspaces/black-box/runs/<clid-bridge-run>
```

Run payloads stay ignored under `workspaces/black-box/runs/`. The committed
contract is the schema and verdict, not the exported images or localized
script.

## Current Contract

A prepared CLiD bridge run must contain:

| Artifact | Purpose |
| --- | --- |
| `config.json` | run metadata, asset references, export counts |
| `analysis.md` | human-readable boundary note |
| `mia_CLiD_clip_local.py` | localized upstream CLiD entrypoint |
| `datasets/member/metadata.jsonl` | member file/prompt rows |
| `datasets/member/*.png` | exported member query images |
| `datasets/nonmember/metadata.jsonl` | nonmember file/prompt rows |
| `datasets/nonmember/*.png` | exported nonmember query images |

Required metadata keys:

```text
file_name
text
```

## Next Contract

Before any GPU CLiD packet, freeze the score output schema:

| Field | Requirement |
| --- | --- |
| split identity | member and nonmember rows must remain aligned to exported metadata |
| scorer family | CLiD score matrix and threshold summary must be separate fields |
| metrics | report AUC, ASR, TPR@1%FPR, TPR@0.1%FPR when sample size permits |
| low-FPR gate | no promotion without nonzero strict-tail signal on a held-out target split |
| artifact boundary | generated images and raw score matrices remain ignored; commit summaries only |

The frozen schema gate is recorded in
[clid-score-schema-gate.md](clid-score-schema-gate.md).

## Boundary

- This does not change admitted evidence.
- This does not change Platform or Runtime schemas.
- This does not authorize a large CLiD GPU packet.
- This only establishes that the local bridge output contract is clean enough
  for the next CPU schema step.
