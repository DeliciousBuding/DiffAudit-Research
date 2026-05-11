# Research Task Queue

> Last refreshed: 2026-05-11

This file classifies future research tasks by status and priority. It is not a
timeline. Historical run IDs and dated notes are in `legacy/`.

## Current State

| Field | Value |
| --- | --- |
| Active work | `I-A finite-tail / adaptive boundary hardening` |
| Active GPU task | none running |
| Next GPU candidate | none selected |
| CPU sidecar | CPU-only admitted-evidence strict-tail and adaptive-language review |
| Gray-box status | PIA remains admitted; tri-score is positive-but-bounded internal candidate; ReDiffuse candidate-only |
| Non-gray-box GPU | none selected |

## Decision Inbox

| Candidate | Track | Mode | Gate | Blocker | Next action |
| --- | --- | --- | --- | --- | --- |
| black-box second response-contract acquisition | black-box | needs_query_split | local skeleton exists; package probe returns `needs_query_split`; query-source audit found no reusable local Pokemon/Kandinsky images or responses | missing member/nonmember query images and response coverage | acquire/build at least `25/25` real query images plus responses, then rerun package probe |
| gray-box tri-score successor | gray-box | hold | X-88/X-141/X-142 tri-score truth-hardening closed positive-but-bounded | same-contract expansion would not change admission or product story | reopen only with a genuinely new scorer, surface, or adaptive/low-FPR falsifier |
| Kandinsky/Pokemon response-contract package | black-box | CPU-only | package preflight executable; supplementary root present | missing query split, endpoint contract, response manifest, and responses | build/acquire package; do not GPU-scale |
| ReDiffuse future reopen | gray-box | hold | exact replay shows modest AUC but weak strict-tail evidence | no admitted promotion; 800k shortcut remains blocked | reopen only with new scorer hypothesis or stricter paper-faithful contract |
| SecMI admission contract | gray-box | CPU-only | full-split stat/NNS evidence is strong and now evidence-ready; supporting-reference and admission-hardening validators exist | not admitted; NNS product-facing contract and adaptive-review contract are still missing | keep validator active; do not promote or release GPU until a separate CPU-first consumer contract is reviewed |
| GSA loss-score LR stability | white-box | CPU-only | leave-one-shadow-out review failed release gate | LR did not beat threshold in enough held-out/target folds | closed; do not GPU-scale |
| CLiD boundary maintenance | black-box | CPU-only | prompt-control boundary anchor and validator exist | no independent image-identity protocol | keep as hold-candidate; no GPU |
| Variation real-query line | black-box | CPU/API-only | query-contract audit | missing member/nonmember query images and endpoint | hold until assets exist |
| Simple-distance portability | black-box | needs assets | second image-to-image or repeated-response contract | no valid second asset contract | hold |
| I-A finite-tail / adaptive boundary | system / I-A | active CPU-first | admitted rows exist and are product-consumable, but strict-tail and adaptive language must stay exact | candidate/admitted leakage or overclaiming finite empirical tails as calibrated sub-percent FPR | audit admitted summaries, bundle docs, product bridge, and validators; patch only if contract drift is found |
| White-box distinct family | white-box | closed | diagonal-Fisher stability board ties `raw_grad_l2_sq` under shadow-frozen target transfer | no distinct score advantage | do not run larger same-score packet; reopen only with a genuinely different observable or paper-backed contract |
| Research boundary-consumability sync | system | synchronized | admitted-vs-candidate boundary synced after candidate closures | none | keep docs synchronized; no GPU |
| I-B risk-targeted unlearning successor | defense | hold | full-split attack-side reviews show small reductions; adaptive-defense contract exists | no defended-shadow/adaptive attacker run or retained-utility metric | keep hold; do not GPU-scale until the required reopen contract is implemented |
| I-C cross-permission successor | cross-permission | hold | translated-contract falsifier is negative at the support boundary | no same-spec gray-box evaluator or matched comparator release board | hold until a new same-spec evaluator contract exists |

## Active

### I-A Finite-Tail / Adaptive Boundary Hardening

- `mode`: CPU-only
- `status`: active follow-up after diagonal-Fisher closure
- `goal`: keep admitted evidence product-consumable without overstating
  finite empirical tails, defended/adaptive robustness, or DDPM/CIFAR10
  provenance.
- `latest trigger`: diagonal-Fisher self-influence closed as
  `negative-but-useful`; black-box response-contract remains asset-blocked.
- `GPU cap`: none
- `integration`: no schema change; Research-only feasibility audit

Current evidence:

- [../../docs/evidence/post-secmi-next-lane-reselection-20260511.md](../../docs/evidence/post-secmi-next-lane-reselection-20260511.md)
- [../../docs/evidence/whitebox-influence-curvature-feasibility-scout-20260511.md](../../docs/evidence/whitebox-influence-curvature-feasibility-scout-20260511.md)
- [../../docs/evidence/gsa-diagonal-fisher-feasibility-microboard-20260511.md](../../docs/evidence/gsa-diagonal-fisher-feasibility-microboard-20260511.md)
- [../../docs/evidence/gsa-diagonal-fisher-layer-scope-review-20260511.md](../../docs/evidence/gsa-diagonal-fisher-layer-scope-review-20260511.md)
- [../../docs/evidence/gsa-diagonal-fisher-stability-board-20260511.md](../../docs/evidence/gsa-diagonal-fisher-stability-board-20260511.md)
- [../../docs/evidence/post-fisher-next-lane-reselection-20260511.md](../../docs/evidence/post-fisher-next-lane-reselection-20260511.md)
- [../white-box/artifacts/whitebox-influence-curvature-feasibility-20260511.json](../white-box/artifacts/whitebox-influence-curvature-feasibility-20260511.json)

Restart conditions:

- do not run a larger same-contract tri-score packet; it is closed as
  internal-only positive-but-bounded evidence.
- continue constructing a second response-contract asset package only against
  the frozen skeleton; do not call empty templates ready assets.
- do not fill the Pokemon/Kandinsky skeleton with CelebA/recon tensors or
  weights-only material.
- do not run 800k ReDiffuse metrics as an automatic shortcut.
- do not run larger ReDiffuse packets without a new scorer hypothesis and CPU
  preflight.
- do not GPU-scale GSA loss-score LR from the current stability review.
- do not reopen diagonal-Fisher from the current stability board; it ties
  `raw_grad_l2_sq` and has no GPU release.
- do not expose ReDiffuse, tri-score, cross-box fusion, GSA LR, H2/simple-distance,
  CLiD, or response-contract acquisition as admitted Platform evidence.
- do not admit SecMI stat or NNS rows until a separate consumer-row schema,
  NNS product-facing decision, adaptive-review protocol, finite-tail semantics,
  and provenance language are reviewed.
- do not GPU-scale I-B from existing attack-side threshold-transfer diagnostics
  until defended-shadow or adaptive-attacker review is specified.
- do not GPU-scale I-C same-pair replay without a same-spec evaluator and
  matched random comparator contract.
- do not call an influence/curvature scout distinct unless it defines a signal
  that is not scalar loss, gradient norm, GSA loss-score LR, or the prior
  activation-subspace observable.
- do not release GPU for the influence/curvature scout until a CPU micro-board
  retains selected-layer raw gradient coordinates and compares against required
  baselines.
- do not run a larger same-score diagonal-Fisher packet; the first CPU
  micro-board failed target-transfer orientation and baseline comparison.
- do not release GPU from the stability board; `up_blocks.1.attentions.0.to_v`
  failed to beat `raw_grad_l2_sq`.

## Ready

### Public Documentation Sync

- `mode`: CPU-only repository hygiene
- `why ready`: run only when docs or repository surface become stale.
- `release gate`: no model run; preserve CLI arguments, JSON output fields, and
  workspace artifact schemas.

## Hold

### CLiD Prompt-Conditioned Diagnostic Lane

- `mode`: black-box candidate
- `reason for hold`: original prompt-conditioned packet is strong, but fixed
  prompt, swapped-prompt, within-split shuffle, prompt-text-only, and control
  attribution reviews show prompt-conditioned auxiliary instability.
- `reopen trigger`: new protocol that isolates image identity from
  prompt-conditioned auxiliary behavior and keeps low-FPR metrics primary.

### Stable Diffusion / CelebA Adapter Contract Watch

- `mode`: future black-box data acquisition
- `reason for hold`: current assets do not provide a second valid
  image-to-image or repeated-response portability contract.
- `reopen trigger`: image-to-image or unconditional-state endpoint contract
  with fixed repeats, response images, split source, and low-FPR gate.

### Cross-Box Successor-Hypothesis Watch

- `mode`: cross-track support
- `reason for hold`: existing score-sharing packets are useful internally, but
  do not establish stable low-FPR gains.
- `reopen trigger`: a new shared-surface or calibration hypothesis with
  low-FPR as the primary gate.

### White-Box Distinct-Family Watch

- `mode`: distinct-family watch
- `reason for hold`: activation-subspace, cross-layer, and trajectory variants
  all failed release gates.
- `reopen trigger`: a genuinely different observable or paper-backed family,
  not another same-observable activation scout.

### Selective / Suspicion-Gated Routing

- `mode`: defense candidate
- `reason for hold`: fixed-budget low-FPR tail matching is real, but gate-leak
  and oracle-route falsifiers block promotion.
- `reopen trigger`: new detector or adaptive-attacker contract that directly
  addresses both falsifiers.

### Response-Strength Black-Box Candidate

- `mode`: black-box candidate
- `reason for hold`: positive-but-bounded on `DDPM/CIFAR10`, but not admitted
  or portable.
- `reopen trigger`: a cross-asset black-box contract with dataset, model, split,
  and query-budget boundaries.

### Variation Real-Query Line

- `mode`: API-only black-box
- `reason for hold`: missing real query-image set and real endpoint.
- `reopen trigger`: `Download/black-box/datasets/variation-query-set` contains
  member/nonmember images and a real endpoint contract is available.

## Needs Data

| Need | Blocker | Data rule |
| --- | --- | --- |
| Cross-box transfer / portability | missing paired model contracts, paired split contracts, and one shared-surface hypothesis | do not schedule execution until required paired data is present in `Download/` or documented through workspace manifests |
| Conditional diffusion wider-family validation | current `DDPM/CIFAR10` results cannot generalize to conditional diffusion | raw datasets, weights, and supplementary files belong under `<DIFFAUDIT_ROOT>/Download/`, not Git |
| Simple-distance second asset | no valid second image-to-image or repeated-response contract | follow [../../docs/evidence/blackbox-response-contract-asset-acquisition-spec.md](../../docs/evidence/blackbox-response-contract-asset-acquisition-spec.md) before GPU |

## Closed

| Task | Result |
| --- | --- |
| Post-ReDiffuse reselection | Selects black-box second response-contract acquisition; no GPU release. |
| Gray-box tri-score consolidation | Positive-but-bounded internal evidence; no admitted promotion and no GPU release. |
| Gray-box tri-score truth-hardening | Positive-but-bounded internal evidence; no admitted promotion, no product promotion, and no GPU release. |
| PIA stochastic-dropout truth-hardening | Positive boundary hardening; no GPU release. |
| Non-gray-box reselection | Selected black-box response-contract acquisition audit; no GPU release. |
| Black-box response-contract acquisition audit | Needs-assets; no GPU release. |
| ReDiffuse checkpoint-portability gate | blocked-by-scoring-contract; 800k checkpoint compatibility is not enough to release metrics. |
| ReDiffuse ResNet contract scout | blocked-by-contract-mismatch; current Research `resnet` mode is not exact collaborator replay. |
| ReDiffuse exact replay preflight | CPU preflight passed; `resnet_collaborator_replay` mode is available, no GPU release yet. |
| ReDiffuse 750k exact replay | Candidate-only; modest AUC but weak strict-tail evidence, no admitted promotion. |
| SecMI full-split admission boundary | Evidence-ready supporting reference; not admitted until consumer-boundary/adaptive-review contract exists. |
| SecMI admission contract hardening | Supporting-reference-hardened; SecMI stat and NNS remain Research-only rows with no GPU release. |
| Post-SecMI next-lane reselection | Selected white-box influence/curvature feasibility scout as CPU-first; no GPU release. |
| White-box influence/curvature feasibility | CPU contract ready; GSA assets are ready with workspace-scoped upstream checkout; no GPU release. |
| GSA diagonal-Fisher micro-board | Negative-but-useful; selected-layer raw gradients are extractable, but the diagonal-Fisher score failed target transfer. |
| GSA diagonal-Fisher layer scope | Mixed but not GPU-ready; one tiny layer-scope row transfers but ties `raw_grad_l2_sq`. |
| GSA diagonal-Fisher stability board | Negative-but-useful; the remaining layer ties `raw_grad_l2_sq` at `4` samples per split, closing the line. |
| Post-Fisher next-lane reselection | Selected CPU-only I-A finite-tail / adaptive boundary hardening; no GPU release. |
| Kandinsky/Pokemon response-contract package preflight | needs-assets; supplementary root exists, but no member/nonmember query package or response contract exists. |
| GSA loss-score shadow stability | negative-but-useful; leave-one-shadow-out LR failed the distinct-scorer release gate. |
| Research resting-state audit | No active GPU candidate or reducible CPU sidecar until assets or a new hypothesis arrive. |
| Black-box response-contract asset-acquisition spec | needs-assets; minimum second-asset package defined; no GPU release. |
| Black-box response-contract discovery | needs-assets; discovery found no paired second response-contract package under black-box dataset/supplementary roots. |
| Black-box response-contract second-asset intake | needs-assets; post-tri-score refresh found no ready paired package. |
| Research boundary-consumability sync | synchronized admitted-vs-candidate boundary; no GPU release and no schema change. |
| Admitted evidence bundle | Synchronized; complete admitted consumer set exported as checked machine-readable bundle. |
| I-B risk-targeted unlearning successor scope | hold; small attack-side reductions are not enough without defended-shadow/adaptive review. |
| ReDiffuse collaborator bundle intake | Positive intake; complete enough for bounded compatibility review, not admitted evidence. |
| ReDiffuse 750k direct-distance packet | Positive compatibility packet at 64/64; not comparable with PIA/SecMI without scoring-mode caveat. |
| Recon tail confidence review | Admitted-finite-tail-only; recon remains black-box product row. |
| Semantic-auxiliary low-FPR review | Negative-but-useful; no GPU packet selected. |
| Variation query-contract audit | Blocked by missing real query images and endpoint. |
| H2 simple-distance product bridge comparison | Recon remains product row; simple-distance remains Research evidence only. |
| CLiD prompt-conditioned probing | Hold-candidate; strong original packet but prompt controls block admission. |
| Cross-box evidence boundary hardening | Candidate-only; current packets do not establish stable low-FPR gains. |
| Shared utility extraction | Metrics, JSON I/O, Gaussian helpers, and schedule helpers now have a package home. |
| Information architecture reset | Public docs, internal docs, workspace archives, and data boundaries were reorganized. |

Older closed entries are traceable through
[`legacy/execution-log/2026-04-29/README.md`](../../legacy/execution-log/2026-04-29/README.md).
