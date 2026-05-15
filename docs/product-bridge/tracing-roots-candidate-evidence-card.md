# Tracing Roots Candidate Evidence Card

> Status: active Research candidate bridge artifact as of 2026-05-15.

## Verdict

```text
Tracing the Roots has a checked machine-readable candidate card, not an admitted row
```

The OpenReview supplementary packet for `Tracing the Roots` ships fixed CIFAR10
diffusion-trajectory feature tensors and replay code. The bounded local replay
is positive:

| Metric | Value |
| --- | ---: |
| Train samples | `2000` |
| Eval samples | `2000` |
| Selected features | `1002` |
| Eval accuracy | `0.737500` |
| Eval AUC | `0.815826` |
| Eval TPR@1%FPR | `0.134000` |
| Eval TPR@0.1%FPR | `0.038000` |

The machine-readable card is:

[`tracing-roots-candidate-evidence-card.json`](tracing-roots-candidate-evidence-card.json)

This is Research-side feature-packet evidence only. It is not an admitted
Platform/Runtime bundle and does not prove raw image-identity-safe membership.

## Boundary

Allowed:

- Treat the packet as positive Research evidence for diffusion-trajectory
  features under gray-box/white-box access.
- Use the card for internal comparison against other Research candidates.
- Use the blockers to define the smallest raw-provenance or feature-packet
  consumer-boundary handoff.

Blocked:

- Do not show Tracing the Roots as admitted Platform evidence.
- Do not add Tracing the Roots to
  [`../../workspaces/implementation/artifacts/admitted-evidence-bundle.json`](../../workspaces/implementation/artifacts/admitted-evidence-bundle.json).
- Do not treat released feature tensors as raw checkpoint/image/query-response
  evidence.
- Do not download raw CIFAR/CelebA-HQ/FFHQ assets, target checkpoints, or
  generated images from this card alone.

## Live Primary-Source Recheck

On 2026-05-15, the current OpenReview API entry is reachable, lists the paper
as a NeurIPS 2025 poster, and reports a last modification time of
`2026-04-21T14:57:25+08:00`. The current supplementary attachment returns
`200` with `45,499,156` bytes, matching the previously checked packet size.

The current arXiv e-print is `2411.07449v3` with `3,614,846` bytes and SHA256
`f8662fcc4281ca2139fc93eed9819741b65335ee8d7f060abb61d2ad1fda9756`. Its
source archive contains TeX, bibliography, style, and figures only. It does
not add a raw target checkpoint identity, raw member/external sample manifest,
or feature-regeneration script.

## Evidence

- [../evidence/tracing-roots-feature-packet-mia-20260515.md](../evidence/tracing-roots-feature-packet-mia-20260515.md)
- [../../workspaces/gray-box/artifacts/tracing-roots-feature-packet-mia-20260515.json](../../workspaces/gray-box/artifacts/tracing-roots-feature-packet-mia-20260515.json)
