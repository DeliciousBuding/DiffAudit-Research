# Black-Box Plan

## Status

- `recon`: strongest main black-box method, but public data limits strict paper-aligned claims.
- `CLiD`: hold-candidate. The prompt-conditioned packet is strong and
  repeat-stable, but prompt controls and attribution block admission as general
  black-box evidence. The current machine-readable boundary is
  [../../docs/evidence/clid-image-identity-boundary-contract-20260511.md](../../docs/evidence/clid-image-identity-boundary-contract-20260511.md).
- `variation`: API-only support; executable query-contract audit is now
  blocked by missing member/nonmember query images and endpoint.
- `semantic-auxiliary-classifier`: negative-but-useful after low-FPR review;
  not selected for GPU.
- `H2 response-strength`: candidate-only with positive non-overlap signal;
  frozen lowpass follow-up is positive-but-bounded on `DDPM/CIFAR10`; SD/CelebA
  text-to-image transfer is protocol-blocked.
- `simple image-to-image distance`: bounded single-asset evidence on
  SD1.5/CelebA; not a product row and not portability evidence.
- `mid-frequency same-noise residual`: distinct paper-backed observable gap;
  scorer, collector functions, synthetic tiny cache writer, real-asset `4/4`
  preflight, and frozen `64/64` sign-check are implemented. The line is
  candidate-stable-but-bounded after the seed-only repeat retained signal, but
  the comparator audit narrows the claim to same-noise residual rather than
  proven mid-frequency specificity. It is not admitted evidence and
  same-contract GPU expansion is closed.

## Next Action

Recon product-row promotion is complete. The bounded public-100 step30 rerun
and artifact re-summarization now produce the admitted coherent
upstream-threshold packet (`AUC = 0.837`, `ASR = 0.74`, `TPR@1%FPR = 0.22`,
`TPR@0.1%FPR = 0.11`). The finite-tail confidence review keeps this row
admitted, but blocks wording that treats public-100 zero-FP evidence as
continuous sub-percent FPR calibration. Keep status synchronized with
[../../docs/evidence/recon-product-validation-result.md](../../docs/evidence/recon-product-validation-result.md)
and
[../../docs/evidence/recon-tail-confidence-review.md](../../docs/evidence/recon-tail-confidence-review.md).

## Current Status

Stable admitted baseline after product-consumable strengthening. `recon` remains
the admitted black-box row under the unified metric source. The H2
simple-distance product bridge comparison keeps that signal as Research
evidence only, and the second-asset portability preflight is blocked by missing
query-image/response-contract assets. Variation now has an executable query
contract audit, but it is blocked by missing real member/nonmember query images
and endpoint.

The black-box response-contract acquisition audit also closes as
`needs-assets`: SD1.5/CelebA image-to-image is CPU-eligible but is the same
asset family as the existing simple-distance evidence, while variation and
Kandinsky/Pokemon lack the required split/endpoint contract.
The minimum second-asset package is now specified in
[../../docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](../../docs/evidence/blackbox-response-contract-asset-acquisition-spec.md).
The executable package-level preflight confirms that the current
Kandinsky/Pokemon supplementary root is not enough: it has no member/nonmember
query package, endpoint contract, response manifest, or responses. See
[../../docs/evidence/blackbox-response-contract-package-preflight.md](../../docs/evidence/blackbox-response-contract-package-preflight.md).
The repository-level discovery pass generalizes that finding across the current
black-box package roots: `Download/black-box/datasets` has no package ids,
`Download/black-box/supplementary` has only `clid-mia-supplementary` and
`recon-assets` as supplementary-only directories, and no ready paired
response-contract package exists. See
[../../docs/evidence/blackbox-response-contract-discovery.md](../../docs/evidence/blackbox-response-contract-discovery.md).
The post-tri-score intake refresh reconfirms the same status and preserves the
machine-readable discovery output under
`workspaces/black-box/artifacts/blackbox-response-contract-second-asset-intake-20260511.json`;
see
[../../docs/evidence/blackbox-response-contract-second-asset-intake-20260511.md](../../docs/evidence/blackbox-response-contract-second-asset-intake-20260511.md).
Do not release a black-box response-contract GPU task until a candidate package
passes that CPU preflight. The current active CPU sidecar is the
Kandinsky/Pokemon package scaffold dry-run for
`response-contract-pokemon-kandinsky-20260511`, recorded in
[../../docs/evidence/blackbox-response-contract-protocol-scaffold-20260511.md](../../docs/evidence/blackbox-response-contract-protocol-scaffold-20260511.md).
It freezes a handoff layout only. The local skeleton has now been created and
the follow-up probe returns `needs_query_split`; real query images, splits,
response files, provenance, and integrity hashes are still missing. See
[../../docs/evidence/blackbox-response-contract-skeleton-create-20260511.md](../../docs/evidence/blackbox-response-contract-skeleton-create-20260511.md).
The local query-source audit confirms that `public-kandinsky-pokemon` contains
weights only and cannot fill the query/response package. Do not mix CelebA or
recon tensor assets into this Pokemon/Kandinsky package. See
[../../docs/evidence/blackbox-response-contract-query-source-audit-20260511.md](../../docs/evidence/blackbox-response-contract-query-source-audit-20260511.md).

A more practical near-term response-contract candidate is now
`AI-Lab-Makerere/beans` plus the local SD1.5 image-to-image pipeline. The beans
dataset supplies enough real train/validation/test query images, and the local
SD1.5 image-to-image pipeline loads offline and produced a one-image CPU
response smoke. This is only a second-query-dataset candidate, not a second
generator-family result. If asset construction continues, prefer a fresh
`response-contract-beans-sd15-20260512` package over further polishing the
empty Pokemon/Kandinsky skeleton. See
[../../docs/evidence/beans-sd15-response-contract-scout-20260512.md](../../docs/evidence/beans-sd15-response-contract-scout-20260512.md).
That package now exists locally with `25/25` query images and `25/25`
deterministic local SD1.5 responses, and the existing CPU package probe returns
`status = ready`. This does not release GPU or prove a signal; it only unlocks
tiny CPU scorer design. See
[../../docs/evidence/beans-sd15-response-contract-ready-20260512.md](../../docs/evidence/beans-sd15-response-contract-ready-20260512.md).
After semantic review, the package is contract/debug only: beans train versus
validation is not proven SD1.5 training membership. Keep the package for
response-contract and scorer plumbing, but do not cite it as true membership
evidence. See
[../../docs/evidence/beans-sd15-membership-semantics-correction-20260512.md](../../docs/evidence/beans-sd15-membership-semantics-correction-20260512.md).
The first tiny scorer, raw query-response pixel distance, is weak on this
package: MSE gives `AUC = 0.5088` and MAE gives `AUC = 0.4992`. Do not scale
this exact scorer or treat it as true SD1.5 membership evidence. See
[../../docs/evidence/beans-sd15-simple-distance-scout-20260512.md](../../docs/evidence/beans-sd15-simple-distance-scout-20260512.md).
The second cheap scorer, local CLIP image-embedding distance, is also weak:
under the lower-distance member convention it gives `AUC = 0.4224`, and the
reverse direction is only `0.5776`. Do not expand simple distance scoring
without a different mechanism or true membership split. See
[../../docs/evidence/beans-sd15-clip-distance-scout-20260512.md](../../docs/evidence/beans-sd15-clip-distance-scout-20260512.md).

The next black-box portability gate is now a membership-semantics gate, not a
package-format gate. A true second membership benchmark must identify the
target model, its real training or fine-tuning members, held-out nonmembers, and
a reproducible query/response contract. Beans/SD1.5 fails that gate but remains
useful for contract debugging. MNIST/DDPM passes the cleaner split test, but raw
loss is weak, so only a different scorer hypothesis should reopen it. See
[../../docs/evidence/true-second-membership-benchmark-scope-20260512.md](../../docs/evidence/true-second-membership-benchmark-scope-20260512.md).

As a separate second-scene sanity check, a tiny CPU-only MNIST/DDPM scout tested
raw PIA-style noise-prediction loss on `1aurent/ddpm-mnist` using first `16`
MNIST train images as members and first `16` test images as nonmembers. The
result was near-random (`AUC = 0.496094`, `best ASR = 0.562500`). A
same-split per-timestep guard peaked at only `AUC = 0.578125`, so direct
raw-loss transfer is closed unless a sharper scorer hypothesis appears. See
[../../docs/evidence/mnist-ddpm-pia-portability-smoke-20260512.md](../../docs/evidence/mnist-ddpm-pia-portability-smoke-20260512.md).

The CLiD line is now explicitly guarded as a prompt-conditioned diagnostic
candidate, not image-identity membership evidence. The prompt-conditioned
repeat has `TPR@0.1%FPR = 1.0`, but the best prompt-control strict-tail value
is `0.21`, and fixed-prompt / prompt-text-only controls are `0.02`. Do not run
another CLiD GPU packet unless a new CPU-first protocol can isolate image
identity from prompt-image pairing and auxiliary-score behavior.

The mid-frequency same-noise residual scout is now the active black-box
candidate. It is not covered by the existing H2/H3 lowpass, highpass, or
bandpass response-cache work because those caches only store final
inputs/responses and distance summaries. The synthetic residual cache runner
and real-asset `4/4` preflight established the cache schema, and the frozen
`64/64` sign-check on the collaborator 750k checkpoint produced
`AUC = 0.733398`, `ASR = 0.710938`, and finite `4/64` zero-FP recovery. This is
candidate-only. The seed-only repeat at the same timestep and band retained
signal with `AUC = 0.719238`, `ASR = 0.6875`, and finite `3/64` zero-FP
recovery. Same-contract GPU expansion is now closed. The stability result is
[../../docs/evidence/midfreq-residual-stability-result-20260512.md](../../docs/evidence/midfreq-residual-stability-result-20260512.md);
the comparator audit is
[../../docs/evidence/midfreq-residual-comparator-audit-20260512.md](../../docs/evidence/midfreq-residual-comparator-audit-20260512.md);
the stability decision is
[../../docs/evidence/midfreq-residual-stability-decision-20260512.md](../../docs/evidence/midfreq-residual-stability-decision-20260512.md);
the sign-check is
[../../docs/evidence/midfreq-residual-signcheck-20260512.md](../../docs/evidence/midfreq-residual-signcheck-20260512.md);
the CPU scorer is
tracked in
[../../docs/evidence/midfreq-residual-scorer-contract-20260512.md](../../docs/evidence/midfreq-residual-scorer-contract-20260512.md);
the collector functions are tracked in
[../../docs/evidence/midfreq-residual-collector-contract-20260512.md](../../docs/evidence/midfreq-residual-collector-contract-20260512.md);
the tiny runner contract is
[../../docs/evidence/midfreq-residual-tiny-runner-contract-20260512.md](../../docs/evidence/midfreq-residual-tiny-runner-contract-20260512.md);
the real-asset preflight is
[../../docs/evidence/midfreq-residual-real-asset-preflight-20260512.md](../../docs/evidence/midfreq-residual-real-asset-preflight-20260512.md);
the cache audit is
[../../docs/evidence/midfreq-same-noise-residual-preflight-20260512.md](../../docs/evidence/midfreq-same-noise-residual-preflight-20260512.md).

The semantic-auxiliary classifier lane also fails promotion:
best AUC gain over `mean_cos` is `0.001953`, below the `0.01` gate. The next
GPU candidate is not selected; CLiD remains hold-candidate. The older
Research-level resting-state audit remains useful historical context, but the
current reducible task is post-midfreq next-lane reselection. See
[../../docs/evidence/research-resting-state-audit-20260510.md](../../docs/evidence/research-resting-state-audit-20260510.md).
