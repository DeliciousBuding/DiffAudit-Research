# Research Resting-State Audit

> Date: 2026-05-10
> Status: temporary resting state; no GPU release

## Question

Does Research currently have any active GPU candidate, reducible CPU sidecar, or
bounded blocker that can be advanced without new external assets or a new
falsifiable hypothesis?

## Checklist

| Requirement | Evidence | Verdict |
| --- | --- | --- |
| Active GPU question is absent. | `ROADMAP.md` and `challenger-queue.md` list no active GPU task. | pass |
| Next GPU candidate is absent. | ReDiffuse is closed as candidate-only / hold; black-box response-contract acquisition is `needs-assets`. | pass |
| Black-box blocker is not reducible locally. | The acquisition audit and asset spec require a second response-contract package before CPU preflight can reopen execution. | blocked by assets |
| CLiD sidecar has no reducible next action. | CLiD remains prompt-conditioned only; all prompt-control reviews block admission until a new image-identity protocol exists. | hold |
| Variation sidecar has no reducible next action. | The query-contract audit is blocked by missing member/nonmember query images and endpoint. | hold |
| Simple-distance portability has no reducible next action. | The only CPU-eligible path is same-family SD1.5/CelebA; second-asset spec is required before GPU. | hold |
| ReDiffuse has no reducible next action. | Direct-distance is candidate-only; ResNet parity was negative; 800k metrics are blocked without a new scorer or checkpoint-portability hypothesis. | hold |
| Platform/Runtime handoff is not needed. | No admitted result, schema field, report format, or product recommendation changed. | pass |

## Verdict

`temporary resting state`.

Research should not release a GPU task or open a same-observable CPU rerun from
the current state. The next cycle should start only if one of the restart
conditions below is satisfied.

## Restart Conditions

1. A second black-box response-contract package lands under `Download/` and
   satisfies the acquisition spec CPU preflight.
2. A new ReDiffuse scorer or checkpoint-portability hypothesis appears that is
   not direct-distance replay and can be falsified CPU-first.
3. A new CLiD protocol isolates image identity from prompt-conditioned
   auxiliary behavior.
4. A distinct white-box or cross-box observable appears with a frozen packet
   identity and low-FPR primary gate.
5. Platform or Runtime requests a specific system-consumable evidence sync that
   cannot be answered from the admitted result table.

## Current Slots

| Slot | Value |
| --- | --- |
| Active GPU question | none running |
| Next GPU candidate | none selected |
| CPU sidecar | none currently reducible |
| Active work | temporary resting state: needs external assets or new hypothesis |

## Platform and Runtime Impact

No Platform or Runtime changes are needed.
