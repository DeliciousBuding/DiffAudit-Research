# CopyMark CommonCanvas Response Preflight

> Date: 2026-05-12
> Status: blocked by response generation environment / no GPU release

## Question

Can the fixed CopyMark/CommonCanvas `50/50` query split immediately advance to
deterministic response generation?

## Taste Check

This preflight is a stop/go check, not environment building. If the current
machine cannot generate CommonCanvas responses without a new setup detour, the
right move is to record the blocker and avoid pretending the package is ready
for scoring.

## Evidence

Current local Python:

```text
torch = 2.11.0+cpu
torch.cuda.is_available() = False
diffusers = installed
transformers = installed
```

Machine GPU visibility:

```text
NVIDIA GeForce RTX 4070 Laptop GPU, 8188 MiB total, about 3033 MiB free
```

Local model cache check:

```text
C:\Users\Ding\.cache\huggingface has no CommonCanvas/CommonCanvas-XL-C hit
```

The query package itself exists under `<DIFFAUDIT_ROOT>/Download` and the
package probe already reached `needs_responses`, so the blocker is not query
split construction.

## Verdict

`blocked by response generation environment / no GPU release`.

The next valuable action is not a scorer and not another package validator. It
is one of:

1. Provide or locate a CUDA-capable Python environment plus local
   `common-canvas/CommonCanvas-XL-C` weights.
2. Generate deterministic responses elsewhere and attach them under the fixed
   response manifest.
3. If neither is feasible, mark the CopyMark/CommonCanvas package
   `query-only / blocked` and switch to another second-asset route.

No full dataset download is needed for this blocker. No GPU experiment is
released until the package probe returns `ready`.

## Platform and Runtime Impact

None. This is Research-side response-generation readiness only.
