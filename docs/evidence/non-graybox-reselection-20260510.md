# Non-Gray-Box Reselection

> Date: 2026-05-10
> Status: CPU selection complete; no GPU release

## Question

After ReDiffuse closed as candidate-only and I-A truth-hardening completed,
which non-gray-box lane should receive the next active research slot?

## Candidates Reviewed

| Candidate | Current state | Decision |
| --- | --- | --- |
| Black-box `recon` | Admitted product row is already strengthened. Finite-tail caveat is documented. | Do not rerun without a new product or asset question. |
| Black-box `CLiD` | Strong prompt-conditioned packet, but prompt controls and attribution block admission. | Hold until a new image-identity protocol exists. |
| Black-box `variation` | Query-contract audit is executable, but member/nonmember query images and endpoint are missing. | Needs data/endpoint. |
| H2 response-strength | Positive DDPM/CIFAR10 candidate with lowpass stabilization, but SD/CelebA text-to-image transfer is protocol-blocked. | Reopen only through a compatible query-budget and response contract. |
| Simple image-to-image distance | Bounded single-asset evidence exists; second-asset portability is blocked. | Needs second asset. |
| White-box distinct family | GSA/DPDM admitted comparator exists; same-family activation/trajectory variants failed release gates. | Hold until a genuinely different observable appears. |
| Cross-box fusion | Useful AUC movement, but unstable low-FPR gains. | No fusion rerun; use only for hypothesis selection. |

## Selection

Select a CPU-only `black-box response-contract acquisition audit`.

Rationale:

- It is the only non-gray-box path that could reopen a meaningful GPU task
  without repeating a closed observable.
- It directly targets the current blocker: lack of a compatible
  response-strength or simple-distance response contract outside the existing
  DDPM/CIFAR10 packet.
- It preserves low-FPR discipline because no execution is released until the
  audit freezes target asset identity, comparator surface, query budget,
  adaptive-attacker boundary, and low-FPR gate.

## Frozen Next Task

Create a CPU-only audit that answers:

```text
Do local `Download/` assets contain any second black-box response-strength or
simple-distance contract with member/nonmember query images, observable
responses, controlled repeats, and a documented query budget?
```

Minimum required fields:

| Field | Requirement |
| --- | --- |
| Asset identity | dataset/model/source path recorded through portable `Download/` layout |
| Split | member/nonmember query images or equivalent target identities |
| Response surface | image-to-image, repeated response images, or equivalent observable output |
| Query budget | fixed repeats or fixed stochastic samples |
| Comparator | simple-distance or response-strength baseline available on the same cache |
| Low-FPR gate | finite empirical strict-tail reporting; no calibrated sub-percent overclaim |
| Adaptive boundary | what an adaptive caller can change and what is fixed |

## Verdict

Positive reselection, CPU-only.

- No GPU task is released.
- The next active task is `black-box response-contract acquisition audit`.
- If no compatible second asset exists, record `needs-assets` and switch to the
  next CPU lane instead of rerunning same-asset H2 or CLiD.

## Platform and Runtime Impact

No Platform or Runtime changes are needed.
