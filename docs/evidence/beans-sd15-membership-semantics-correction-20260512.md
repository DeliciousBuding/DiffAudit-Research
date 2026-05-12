# Beans SD1.5 Membership Semantics Correction

> Date: 2026-05-12
> Status: semantics-corrected; no GPU release

## Question

Do the `member` and `nonmember` labels in
`response-contract-beans-sd15-20260512` represent membership in the response
model training set?

## Finding

No.

The package uses:

- `member`: first `25` images from `AI-Lab-Makerere/beans` train split
- `nonmember`: first `25` images from `AI-Lab-Makerere/beans` validation split
- response model: local `stable-diffusion-v1-5` image-to-image

That split is a real dataset split and a useful query/response contract, but it
is not proven membership in the SD1.5 training set. Therefore the package is a
second-query response-contract debug packet, not a true membership-inference
benchmark.

## Impact

The package readiness result remains valid:

- `25 / 25` query images exist.
- `25 / 25` deterministic responses exist.
- The package probe returns `status = ready`.

But the simple-distance and CLIP-distance scorer results must be interpreted as
debug signals on a pseudo-member split, not evidence that the attack transfers
to real SD1.5 membership.

## Corrected Boundary

- Keep: `response-contract-beans-sd15-20260512` is useful for testing package
  format, response capture, scoring code, and query/response observables.
- Do not claim: Beans train images are SD1.5 members.
- Do not claim: Beans validation images are SD1.5 nonmembers.
- Do not use this package for admitted attack evidence.
- Do not release GPU based on this package.

## Next Action

Stop treating Beans/SD1.5 as the main second membership benchmark. The next
true mainline step needs one of:

- a generator with known training data and a held-out nonmember split,
- a response contract from a model trained or fine-tuned on a known dataset,
- a repeated-response contract where the target question is explicitly not
  membership in model training data.

Until then, Beans/SD1.5 can remain a local contract/debug asset only.

## Platform and Runtime Impact

None. This correction prevents overclaiming and does not change product rows.
