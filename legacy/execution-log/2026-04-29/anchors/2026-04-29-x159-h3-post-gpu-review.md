# X-159: H3 Post-GPU Review / Implementation-Hardening Decision

## Question

After X157 and X158, should `04-H3 selective / suspicion-gated all-steps routing` be promoted, expanded to a larger GPU packet, or narrowed into a CPU-only implementation-hardening contract?

## Inputs Reviewed

- `workspaces/implementation/2026-04-29-x156-04-defense-successor-hypothesis-expansion-review.md`
- `workspaces/implementation/2026-04-29-x157-h3-selective-gate-cached-scout.md`
- `workspaces/implementation/2026-04-29-x158-h3-gated-runtime-gpu-scout.md`
- `workspaces/gray-box/runs/x157-h3-selective-gate-cached-scout-20260429-r2-allsteps-primary/summary.json`
- `workspaces/gray-box/runs/x158-h3-gated-runtime-gpu-scout-20260429-r1/summary.json`
- `workspaces/gray-box/runs/x159-h3-post-gpu-review-20260429-r1/summary.json`

## CPU Review Execution

Script:

- `legacy/execution-log/2026-04-29/scripts/run_x159_h3_post_gpu_review.py`

Command:

```powershell
python -X utf8 legacy/execution-log/2026-04-29/scripts/run_x159_h3_post_gpu_review.py
```

Artifact:

- `workspaces/gray-box/runs/x159-h3-post-gpu-review-20260429-r1/summary.json`

## Evidence Read

X158 is a real positive signal at the narrow low-FPR tail:

| Surface | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR |
| --- | ---: | ---: | ---: | ---: |
| baseline adaptive | `0.781250` | `0.773438` | `0.078125` | `0.078125` |
| all-steps dropout adaptive | `0.769775` | `0.765625` | `0.046875` | `0.046875` |
| selective gated adaptive | `0.778076` | `0.773438` | `0.046875` | `0.046875` |

Gate:

- requested gate fraction: `0.20`
- actual gate fraction: `0.203125`
- member gate fraction: `0.296875`
- nonmember gate fraction: `0.109375`

The low-FPR result is therefore not a cached-only artifact: the fresh GPU scout preserves the same tail-matching pattern at roughly one-fifth routed samples.

## Hardening Gates

| Gate | Result | Interpretation |
| --- | --- | --- |
| cached low-FPR tail match | pass | X157 selective `all_steps` matched full all-steps at both low-FPR metrics |
| fresh low-FPR tail match | pass | X158 selective gate matched full all-steps at both low-FPR metrics |
| fresh gate budget | pass | X158 routed `0.203125`, within one-sample tolerance of the `0.20` contract |
| full-metric privacy dominance | fail | selective gate is weaker than full all-steps on attack-side AUC/ASR (`+0.008301 / +0.007813`) |
| deployable no-leak gate | fail | current detector is same-packet baseline PIA score tail, so it is an audit-time owner-side selector, not a clean runtime detector |
| budget-fixed adaptive attacker | fail | repeated-query scoring exists, but the branch has not tested a fixed-budget attacker that reallocates queries against the gated policy |

## Verdict

`positive hardening / GPU hold`

H3 should be kept, but only as a candidate-only quality / perturbation-exposure idea. It should not be promoted into the admitted defense line, should not receive a larger `128 / 128` GPU packet, and should not trigger Runtime or Platform changes.

## Frozen Boundary

Allowed next work:

- CPU-only candidate runner contract review
- define how a future audit pipeline would report gate provenance, gate fraction, and detector identity
- define a stricter attacker model before any new GPU release

Not allowed:

- claim validated privacy
- claim H3 beats full all-steps dropout
- claim deployable cheap runtime cost reduction
- expand same H3 packet without a new gate or attacker contract
- use SimA as detector until it has a stronger local contract

## Control State After X-159

- `active_gpu_question = none`
- `next_gpu_candidate = none`
- `next live lane = X-160 non-graybox next-lane reselection after H3 review`
- `cpu_sidecar = I-A low-FPR / adaptive-attacker boundary maintenance`

## Handoff

- `Platform`: no UI/schema change. If H3 later graduates, present it as `candidate / audit-time gate`, not as admitted defense.
- `Runtime-Server`: no endpoint change. A future candidate runner would need explicit gate provenance, detector identity, gate fraction, and adaptive-attacker fields.
- `Docs/materials`: do not advertise H3 as validated privacy. The honest one-line read is: "selective all-steps gating matched full all-steps low-FPR tail on one fresh 64/64 packet while routing about 20%, but remains candidate-only."
