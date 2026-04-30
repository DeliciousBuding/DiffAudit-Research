# CLiD 100/100 Score Packet

This note records the first bounded CLiD score packet that clears the frozen
score-summary gate. It is a candidate result under review, not admitted
evidence.

## Verdict

```text
positive bounded candidate; review before admission
```

The packet passes the score-summary gate:

| Field | Value |
| --- | --- |
| Run | `clid-local-bridge-100-20260501-r1` |
| Mode | `local-bridge-pair-summary` |
| Member rows | 100 |
| Nonmember rows | 100 |
| Best alpha | 0.9 |
| AUC | 1.0 |
| ASR | 1.0 |
| TPR@1%FPR | 1.0 |
| TPR@0.1%FPR | 1.0 |
| Schema status | `ready` |
| Promotion status | `eligible` |

## Sanity Check

The signal is not only a best-alpha artifact:

| Surface | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| Feature 0 | 0.9072 | 0.835 | 0.41 | 0.41 |
| CLiD auxiliary feature | 1.0 | 1.0 | 1.0 | 1.0 |

The CLiD auxiliary feature is the dominant separator on this packet. That makes
the result promising, but also requires adaptive review before admission.

The first integrity review is recorded in
[clid-candidate-integrity-review.md](clid-candidate-integrity-review.md). It
does not find obvious row-alignment, duplicate-image, duplicate-prompt, or
text-length leakage, but still requires a repeat or perturbation before
admission.

## Boundary

- This does not change admitted evidence.
- This does not replace `recon`.
- This does not change Platform or Runtime schemas.
- Raw score files and generated bridge payloads remain ignored under
  `workspaces/black-box/runs/`.
- Next step is stability and leakage review: repeat or perturb the packet,
  verify row alignment, and check whether the signal survives a stricter
  held-out protocol.
