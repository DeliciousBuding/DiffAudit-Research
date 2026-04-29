# X-155: Post-Trajectory Non-Graybox Reselection

## Question

After `X-154` failed the per-timestep activation-trajectory fire gate, what is the next honest Research lane?

## Reselection

| Candidate | Decision | Reason |
| --- | --- | --- |
| Larger `X-154` packet | reject | The validation-selected trajectory feature failed holdout and low-FPR. Scaling the same observable would be sample-count salvage without a new hypothesis. |
| Post-hoc `trajectory_energy` promotion | reject | It had the only nonzero holdout tail diagnostic, but it was not selected by validation. Promoting it would violate the no-leak contract. |
| Third same-contract `G1-A / X-90` seed | reject | `X-141 / X-142` already froze this as two-seed internal auxiliary evidence, not a headline or default rerun. |
| Larger same-contract `04-H2` | reject | `H2` already closed minimal contract-complete plus `4 / 4` negative-but-useful; no new defense hypothesis exists. |
| Same-table `05-cross-box` rerun | reject | `05` already has promoted `logistic_2feature` support plus `H4` auxiliary-only boundary; no new shared-surface hypothesis is frozen. |
| `I-D` conditional widening | reject | Current `I-D` has bounded conditional truth and a negative actual defense rerun, but no honest bounded successor lane; do not extrapolate `DDPM/CIFAR10`. |
| `04-defense` genuinely new successor-hypothesis expansion | select | After activation-subspace falsification, the largest live innovation gap is defense diversity. This must start CPU-first and may only release GPU if a genuinely new successor family or selection argument is frozen. |

## Verdict

`positive reselection / GPU hold`

The next live lane becomes `X-156 04-defense successor-hypothesis expansion review`. This is a CPU-first review, not a GPU release.

## Control State After X-155

- `active_gpu_question = none`
- `next_gpu_candidate = none until X-156 freezes a genuinely new defense successor contract`
- `current_execution_lane = X-156 04-defense successor-hypothesis expansion review`
- `cpu_sidecar = I-A boundary maintenance`

## Handoff

- `Platform`: no schema or UI change.
- `Runtime-Server`: no runner or endpoint change.
- `Docs/materials`: no public claim change.
