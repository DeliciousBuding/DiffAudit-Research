# CLiD Candidate Evidence Card

> Status: active Research candidate bridge artifact as of 2026-05-15.

## Verdict

```text
CLiD has a checked machine-readable candidate card, not an admitted row
```

The official `zhaisf/CLiD` `inter_output/*` score packet replays on CPU with a
strong target result:

| Metric | Value |
| --- | ---: |
| Selected alpha | `0.9` |
| Shadow AUC | `0.957537` |
| Target AUC | `0.961277` |
| Target ASR | `0.891957` |
| Target TPR@1%FPR | `0.675470` |

The machine-readable card is:

[`clid-candidate-evidence-card.json`](clid-candidate-evidence-card.json)

This is not an admitted Platform/Runtime bundle. It exists so downstream
readers can consume the Research boundary without mining long evidence docs.

## Boundary

Allowed:

- Treat CLiD as strong Research candidate evidence from an official CPU score
  packet.
- Use the card for internal comparison against admitted black-box `recon`.
- Use the blockers to define the smallest next identity-safe protocol step.

Blocked:

- Do not show CLiD as admitted Platform evidence.
- Do not add CLiD to
  [`../../workspaces/implementation/artifacts/admitted-evidence-bundle.json`](../../workspaces/implementation/artifacts/admitted-evidence-bundle.json).
- Do not treat numeric-only score rows as image-identity-safe membership
  evidence.
- Do not download `mia_COCO.zip`, MS-COCO images, Stable Diffusion weights,
  target/shadow checkpoints, or generated images from this card alone.

## Live Access Recheck

On 2026-05-15, authenticated Hugging Face access for
`zsf/COCO_MIA_ori_split1/mia_COCO.zip` still returned `403` for `HEAD`, start
`Range`, and end `Range` probes. That blocks metadata-only ZIP
central-directory inspection and keeps CLiD candidate-only.

## Evidence

- [../evidence/clid-official-inter-output-replay-20260515.md](../evidence/clid-official-inter-output-replay-20260515.md)
- [../evidence/clid-identity-manifest-gate-20260515.md](../evidence/clid-identity-manifest-gate-20260515.md)
- [../evidence/clid-prompt-conditioning-boundary.md](../evidence/clid-prompt-conditioning-boundary.md)
