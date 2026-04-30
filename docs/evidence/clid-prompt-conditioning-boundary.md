# CLiD Prompt-Conditioning Boundary

This card is the canonical boundary for the current CLiD line.

## Verdict

```text
CLiD is a prompt-conditioned positive candidate; it is not admitted general
black-box membership evidence.
```

The evidence separates three facts:

| Question | Evidence | Result |
| --- | --- | --- |
| Does the CLiD bridge produce a usable score packet? | [clid-score-schema-gate.md](clid-score-schema-gate.md), [clid-tiny-score-bridge.md](clid-tiny-score-bridge.md) | yes, but the 8/8 packet is smoke-scale only |
| Is the 100/100 signal strong and repeat-stable under the original prompt-conditioned contract? | [clid-100-score-packet.md](clid-100-score-packet.md), [clid-repeat-stability.md](clid-repeat-stability.md) | yes |
| Does the signal survive a prompt-neutral control on the same images? | [clid-prompt-perturbation.md](clid-prompt-perturbation.md) | no |
| Does the signal survive row-wise prompt swapping across splits? | [clid-swapped-prompt-control.md](clid-swapped-prompt-control.md) | partially; degraded but nonzero strict-tail signal |
| Does the signal survive prompt shuffling inside each split? | [clid-within-split-shuffle-control.md](clid-within-split-shuffle-control.md) | weakly; further degraded but nonzero strict-tail signal |

## Evidence Snapshot

| Metric | First 100/100 packet | Repeat packet | Prompt-neutral control | Swapped-prompt control | Within-split shuffle |
| --- | ---: | ---: | ---: | ---: | ---: |
| AUC | 1.0 | 1.0 | 0.5862 | 0.72885 | 0.64105 |
| ASR | 1.0 | 1.0 | 0.585 | 0.67 | 0.645 |
| TPR@1%FPR | 1.0 | 1.0 | 0.02 | 0.21 | 0.12 |
| TPR@0.1%FPR | 1.0 | 1.0 | 0.02 | 0.21 | 0.12 |
| Feature 0 AUC | 0.9072 | 0.9084 | 0.5848 | 0.6376 | 0.6094 |
| CLiD auxiliary AUC | 1.0 | 1.0 | 0.57175 | 0.7218 | 0.63815 |

The repeat used fresh runtime noise and preserved the strong prompt-conditioned
signal. The prompt-neutral control used the same member and nonmember images but
rewrote all prompts to `a face`; the strict low-FPR signal collapsed. The
swapped-prompt control moved member and nonmember prompt text across splits by
row; strict-tail signal remained nonzero but degraded sharply. The within-split
shuffle preserved split-level prompt distribution while breaking image-prompt
pairing; the signal weakened further but did not collapse to the fixed-prompt
control level.

## Claim Boundary

Allowed claim:

- CLiD found a strong and repeat-stable prompt-conditioned separation on the
  current SD/CelebA bridge packet.
- The current result is useful for studying how prompt contracts interact with
  membership-risk surfaces.
- The current result is not explained by fixed prompt text alone, because the
  swapped-prompt control preserves a weaker strict-tail signal.
- Preserving split-level prompt distribution is not enough to recover the
  original signal, because within-split shuffle remains weaker than the original
  prompt-conditioned packet.
- Future CLiD reports must state the prompt contract and include a
  prompt-neutral or prompt-perturbed control.

Disallowed claim:

- CLiD is admitted black-box membership evidence.
- CLiD replaces `recon` as the strongest black-box line.
- The result generalizes to prompt-neutral, unconditional, or commercial
  diffusion settings.
- The result proves conditional-diffusion privacy risk beyond the tested bridge
  contract.

## Next Admission Test

Do not schedule another CLiD GPU packet until the next hypothesis can separate
prompt information from membership signal. A promotable next test needs:

| Gate | Requirement |
| --- | --- |
| Prompt contract | one frozen prompt-conditioned contract and one matched prompt-control contract |
| Sample identity | same member/nonmember split identity across both contracts |
| Low-FPR primary metric | report `TPR@1%FPR` and `TPR@0.1%FPR`; AUC alone is insufficient |
| Nuisance review | prompt length, duplicate prompts, duplicate images, and row alignment checked |
| Promotion criterion | strict-tail signal survives the prompt-control comparison without relying on prompt-only separability |

Until that test exists, the next CPU sidecar is adaptive prompt-perturbation
design, not more GPU execution.

The concrete CPU contract is recorded in
[clid-adaptive-prompt-perturbation-contract.md](clid-adaptive-prompt-perturbation-contract.md).

## Product Boundary

No Platform or Runtime schema change is needed. Platform may describe CLiD as an
internal research candidate only if it also states that the current positive
result is prompt-conditioned and not admitted evidence.
