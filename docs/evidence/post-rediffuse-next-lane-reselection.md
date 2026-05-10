# Post-ReDiffuse Next-Lane Reselection

> Date: 2026-05-10
> Status: selected CPU-first black-box asset acquisition; no GPU release

## Question

After the ReDiffuse exact-replay packet closed as candidate-only, which lane
should Research pursue next?

## Current Facts

- ReDiffuse 750k exact replay has modest AUC but weak strict-tail evidence; it
  is not admitted and does not justify an 800k shortcut.
- PIA remains the admitted gray-box line; no immediate gray-box GPU candidate is
  selected.
- GSA loss-score LR failed leave-one-shadow-out stability and should not be
  GPU-scaled.
- Existing black-box simple-distance evidence is promising but single-asset; it
  cannot support portability claims without a second response contract.
- The manifest already defines the missing black-box assets:
  `BB-DS-01` second response-contract query set and `BB-SUP-03` response packet.

## Reselection

Selected next lane:

```text
black-box second response-contract acquisition
```

This is CPU-first and asset-first. It should not release GPU until a portable
package exists with member/nonmember query identities, split metadata, endpoint
or response provenance, repeated-response policy, and response manifest.

## Why This Is Highest Value

This lane addresses the largest current scientific gap: portability beyond the
single SD/CelebA-style image-to-image packet and beyond local DDPM/CIFAR10. It
also directly supports product-consumable evidence because black-box response
contracts are closer to Runtime/Platform deployment assumptions than another
same-family gray-box rescue.

## Rejected Alternatives

- ReDiffuse 800k: rejected because 750k exact replay is only candidate evidence
  with weak strict-tail signal.
- GSA loss-score LR: rejected because the stability gate failed.
- CLiD prompt-conditioned continuation: rejected because prompt controls already
  bound the claim to diagnostic status.
- White-box distinct family: held until a genuinely new observable or
  paper-backed family is available.

## Next Action

Build or acquire a minimal second response-contract package under the manifest
rules, then run the existing package preflight. If the package is still missing,
the correct verdict remains `needs-assets`, not GPU-ready.

## Platform and Runtime Impact

No schema changes. If a package is acquired later, Runtime may need only a
handoff describing endpoint identity, response policy, and replay boundaries.
