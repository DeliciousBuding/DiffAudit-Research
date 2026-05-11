# Post-SecMI Next-Lane Reselection

> Date: 2026-05-11
> Status: selected CPU-first white-box feasibility scout
> GPU release: none

## Question

After SecMI admission-contract hardening, which lane should become the next
active Research task without reopening a closed same-family run or spending GPU
on missing assets?

## Current State

SecMI is now `supporting-reference-hardened`, not admitted. The validator and
artifact prevent SecMI stat or NNS rows from silently entering the
Platform/Runtime admitted bundle.

The remaining high-value lanes are constrained:

| Lane | State | Decision |
| --- | --- | --- |
| Black-box second response-contract | `needs_query_split` | No GPU. The local skeleton lacks real member/nonmember query images and response coverage. |
| ReDiffuse | `candidate-only` | No GPU. 750k exact replay has modest AUC and weak strict-tail evidence; 800k shortcut stays blocked. |
| Gray-box tri-score | `internal-only positive-but-bounded` | No GPU. Same-contract expansion would not change the admitted/product story. |
| SecMI | `supporting-reference-hardened` | No GPU. Admission requires a separate consumer-row and adaptive-review contract. |
| I-B / I-C | `hold` | No GPU. I-B needs defended-shadow/adaptive review; I-C needs a same-spec evaluator and matched comparator. |
| White-box distinct family | `open` | Select CPU-first feasibility scout. |

## Selected Lane

`white-box influence/curvature feasibility scout`

Hypothesis: the current DDPM/CIFAR10 white-box assets and GSA extraction
interfaces may expose enough first-order information to define an
influence-style or curvature-proxy observable that is genuinely distinct from
the closed GSA loss-score LR and activation-subspace variants.

Falsifier: if the current code and artifacts expose only scalar loss, gradient
norms, or activation masks already covered by closed GSA/activation work, or if
they lack a stable member/nonmember identity and comparator contract, this lane
must close as `blocked` or `hold` without GPU.

Minimum CPU contract before any GPU can be discussed:

- Identify the exact signal family: influence, curvature proxy, or reject as
  unavailable.
- Show the signal is not just GSA scalar loss, gradient norm, or the prior
  activation-subspace observable under a new name.
- Freeze member/nonmember identity, comparator, metrics, and low-FPR gate.
- Define whether existing code can run a tiny canary without new checkpoints or
  raw tensors in Git.
- Predeclare stop conditions for `blocked`, `negative-but-useful`, or future
  tiny GPU release.

## Verdict

`selected-cpu-first`.

No model run is released. The next task is a feasibility audit that can end
cleanly if the white-box distinct observable is not genuinely available.

## Handoff

No Platform or Runtime schema change is needed. This is Research-internal
candidate selection only.
