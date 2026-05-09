# ReDiffuse Direct-Distance Boundary Review

> Date: 2026-05-10
> Status: closed as candidate-only; no GPU release

## Question

After the negative 750k ResNet parity packet, should Research still release an
800k ReDiffuse metrics packet using the direct-distance scorer?

## Evidence Reviewed

| Evidence | Result | Boundary |
| --- | --- | --- |
| [rediffuse-cifar10-small-packet.md](rediffuse-cifar10-small-packet.md) | 750k direct-distance packet: `AUC = 0.8125`, `ASR = 0.773438`, `TPR@1%FPR = 0.078125`, `TPR@0.1%FPR = 0.078125`. | Positive compatibility signal, but not collaborator-style scoring and not admitted evidence. |
| [rediffuse-resnet-parity-packet.md](rediffuse-resnet-parity-packet.md) | 750k ResNet parity packet: `AUC = 0.411982`, `ASR = 0.538462`, low-FPR metrics `0.0`, best held-out ResNet accuracy `0.5`. | Negative for paper-faithful scoring parity at the frozen gate. |
| [rediffuse-800k-runtime-probe.md](rediffuse-800k-runtime-probe.md) | Existing PIA 800k checkpoint loads under the ReDiffuse bundle and passes CPU preview forward. | Runtime compatibility only; no membership metrics. |

## Analysis

The direct-distance scorer is useful as an engineering and exploratory signal:
it proves that the collaborator bundle, checkpoint, split, dataset, and
Research adapter can produce nontrivial member/nonmember separation.

It should not be treated as a ReDiffuse paper-faithful result. The direct
distance surface and collaborator-style ResNet scorer answer different
questions. The parity packet was designed to bridge that gap and failed at the
frozen `64/64` gate. Running the same direct-distance surface on the 800k
checkpoint would test portability of a Research-specific proxy, not ReDiffuse
method parity.

An 800k direct-distance packet could still be useful later if a new hypothesis
is explicitly about checkpoint-step portability of the proxy score. That is not
the current highest-value question because it would not affect admitted
PIA/SecMI evidence, Platform/Runtime output, or the collaborator-style baseline
claim.

## Verdict

Close the current ReDiffuse lane as `candidate-only / scoring-contract
unresolved`.

- No 800k ReDiffuse GPU packet is released.
- Do not compare direct-distance ReDiffuse metrics with admitted PIA/SecMI as
  equivalent baselines.
- Keep the 800k note as runtime compatibility evidence only.
- Reopen ReDiffuse only with a new CPU contract, such as a better-scoped
  second-stage scorer hypothesis or an explicit checkpoint-portability
  hypothesis for the direct-distance proxy.

## Next Research Direction

Return the active slot to CPU-first truth-hardening:

- I-A formal/adaptive/low-FPR boundary maintenance for admitted gray-box
  `PIA + stochastic-dropout`.
- Non-gray-box reselection only if I-A has no reducible boundary issue.
- No GPU task is selected.

## Platform and Runtime Impact

No Platform or Runtime changes are needed.
