# Non-CLiD Black-Box Reselection

This note supersedes the earlier CLiD selection after prompt-control closure.
It records the CPU-only decision for the next black-box model-mainline slot.

## Verdict

```text
select recon product-consumable strengthening as the next black-box lane
```

CLiD moves to hold-candidate. H2 response-strength remains positive but blocked
for SD/CelebA text-to-image portability. `variation` is still data-gated. The
highest-value next step is therefore not another exploratory method, but a
bounded strengthening pass on the admitted `recon` black-box baseline.

## Decision Matrix

| Lane | Current status | Decision | Reason |
| --- | --- | --- | --- |
| `recon` | admitted black-box baseline | select | It is already evidence-ready and directly consumable by Platform/Runtime, but needs tighter strict-tail, repeat, and limitation packaging before being treated as the durable black-box product row. |
| `CLiD` | hold-candidate | hold | Prompt-conditioned packet is strong, but prompt controls and attribution show auxiliary instability. |
| H2 response-strength | positive-but-bounded candidate | hold | Repeated DDPM/CIFAR10 signal exists, but SD/CelebA text-to-image is protocol-incompatible. |
| `variation` | code-ready | hold | Real query-image set and endpoint are not present. |
| semantic-auxiliary classifiers | candidate support | scope later | Useful as a diagnostic support surface, not the next primary black-box row without a low-FPR admission contract. |

## Selected Next Question

```text
Can the recon black-box baseline be turned into a stricter system-consumable
evidence packet without changing its claim boundary?
```

The next work should stay within the current claim:

- `recon` demonstrates membership leakage risk under minimal black-box
  permissions.
- The claim remains bounded by controlled public-subset and proxy-shadow-member
  semantics.
- It is not a final real-world exploit, not a paper-complete benchmark, and not
  evidence for unrelated conditional diffusion settings.

## Required Gate

Before scheduling GPU:

- Define the exact recon packet identity: sample count, DDIM step, split source,
  model/checkpoint identity, and artifact schema.
- Ensure all product-facing metrics are explicit, including whether
  `TPR@0.1%FPR` is computable or intentionally unavailable.
- Compare against the existing admitted row
  `recon DDIM public-100 step30` without changing CLI arguments or artifact
  schemas.
- Produce a compact review packet that Platform/Runtime can cite without
  reading workspace run payloads.

## Next GPU Candidate

```text
recon product-consumable validation packet, pending CPU contract
```

No GPU task is active now. A GPU run is only justified after the CPU contract
freezes the packet identity and metric completeness checks.

## Product Boundary

- No Platform or Runtime schema change is required yet.
- If the recon packet becomes the stable black-box product row, add a handoff in
  `docs/product-bridge/` before changing sibling repositories.
- Raw artifacts, score matrices, generated images, and run payloads remain
  outside Git.
