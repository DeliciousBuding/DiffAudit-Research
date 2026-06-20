# DiffAudit Evidence Upgrade Roadmap

> Date: 2026-06-06
> Scope: internal research roadmap for moving DiffAudit from paperization polish
> toward CCF-A-grade research evidence.

## 0. Current Verdict

Direction A is a bounded evidence-contracted measurement paper. CCF-A positioning
needs either a larger frozen artifact-surface corpus with external adjudication
or a second independent row-bound response/score asset that survives the
evidence contract.

The current DCU/scnet DDPM line does not change that conclusion. Its best value
is a negative/support boundary: on resource-limited self-trained CIFAR-10 DDPMs,
loss, noise norm, gradient norm, LR fusion, and SecMI-style DDIM trajectory
scores remain around AUC 0.52-0.535 with confidence intervals crossing 0.5. It
should not become the paper's main contribution.

### 2026-06-09 paper release hardening snapshot

The Direction A LaTeX manuscript completed a writing-quality and release-packet
hardening pass. The main text now states C14, H2, and MoFit boundaries as audit
states and next measurement tasks, reducing defensive exclusion prose while
preserving the scientific limits:

- C14: `packet_ready_only`, `n_reviewers=0`, pre-label weak-rule stress control.
- H2: `candidate-only` under missing consumer-boundary and surface-delta
  surfaces.
- MoFit: `support-only`, all six gates non-Pass.
- Excluded claims: N50 denominator, admitted evidence, second public asset, and
  compute release.

Regenerated release artifacts:

- `papers/diffaudit-evidence-paper/paper.pdf` SHA-256:
  `1eed1f456c28d3453742810e1462b74eb32982b118a1a4bf365148f2c6401750`
- anonymous supplement ZIP SHA-256:
  `cbc4c00e51455fd18e09cd4b8bef3187c86c7664becf6797fcaed3c1d5f82058`
- C14 hard-blind review bundle ZIP SHA-256:
  `105a0515cfc4c5fc73e2f3b6e23a5a2413d972a0dcff809b7abfaf93d990f4e4`
- C14 post-label maintainer key ZIP SHA-256:
  `d8e511c8bd8c7b73efa2ca3318ad21b6654cd80eafd8cc718a8100f450634f3e`

Verification passed on 2026-06-09:

- `python -X utf8 scripts\check_paper_release_packet.py`
- targeted `pytest` for citation context, reference integrity, PDF validation,
  manuscript claim audit, and manuscript claim boundary tests (`16 passed`; one
  `.pytest_cache` permission warning)
- `python -X utf8 scripts\run_pr_checks.py`
- LaTeX log scan for undefined references/citations, overfull boxes, and rerun
  warnings
- PDF scan for local paths and stale defensive phrases
- `git diff --check` with LF-to-CRLF warnings only

This improves submission hygiene and reviewability. The CCF-A blocker remains
scientific evidence: independent C14 labels/reliability, a larger frozen
distinct-surface corpus, or a second row-bound public response/score asset.

## 1. Goal

Produce one CCF-A-defensible research object, not a larger pile of weak
experiments.

The acceptable research objects are:

1. **CCF-A measurement paper**
   - Claim-bound evidence measurement for diffusion privacy artifacts.
   - Requires a preregistered, larger, distinct-surface artifact corpus,
     external label audit, and quantitative baselines showing that score-only,
     code-only, or artifact-availability rules falsely promote claims that the
     DiffAudit contract correctly blocks.
2. **CCF-A attack/observable paper**
   - A new response/score observable with strong low-FPR behavior on at least
     two independent target families.
   - Requires row-level response or score packets, target and split identity,
     metric provenance, label-shuffle or permutation controls, and surface-delta
     controls.
3. **CCF-A systems/report-correctness paper**
   - A validated report-correctness system that measurably reduces audit-report
     drift or overclaiming.
   - Requires report-renderer A/B drift reduction, external use, deployment
     evidence, or public-safe evaluator telemetry.

Without one of these evidence objects, the project should continue Direction A
as a bounded measurement paper and stop claiming CCF-A readiness.

## 2. Track Decisions

| Track | Current decision | Why |
| --- | --- | --- |
| Direction A: evidence contract | Continue, but treat as CCF-B-style until new evidence arrives. | It covers admitted, candidate, support, and negative evidence. The current contribution is claim-admission measurement, below a CCF-A scientific result until new evidence arrives. |
| Direction B: H2 output-cloud | Keep as short/workshop candidate. Promote only with a second independent response asset. | H2 is strong inside one response family, but img2img portability fails and consumer/delta gates fail. |
| Direction C: artifact claim-support | Upgrade only if corpus becomes preregistered, larger, distinct-surface, and externally adjudicated. | Current 21/17/10/3 denominators are useful but non-poolable and not prevalence/reliability evidence. |
| Direction D: artifact/report correctness | Hold as release-packet QA until report-drift or external-use evidence exists. | The 2026-06-09 release-wording fault matrix passes `28/28` selected renderer and phrase-guard checks: one current-card acceptance, four renderer rejections, three fixed phrase flags, two fixed clean controls, eight candidate/support promotion mutations, six metadata-only promotion mutations, and four clean boundary phrase controls. These checks are release QA, not systems-effectiveness, external-use, or reviewer-reliability evidence. |
| scnet/DCU DDPM | Close by default after one high-K裁决 if still weak. | More epochs, seeds, timesteps, or DDIM/LR fusion matrices are low-information repeats. |

## 3. High-Value Experiments

### E1. Second Independent Response/Score Asset

**Hypothesis:** DiffAudit becomes publishable at a higher tier if it can show
that the evidence contract admits or blocks a second non-adjacent response/score
asset with row-bound artifacts.

**Data/model requirements:**

- Public target identity or checkpoint hash.
- Exact member/nonmember split or query identities.
- Generated response packet or per-row score packet.
- Metric JSON or enough raw score rows to recompute AUC, ASR, TPR@1%FPR, and
  TPR@0.1%FPR.
- Label-shuffle/permutation controls and a surface-delta boundary.

**Resource plan:** GPU only after a manifest-first preflight. Prefer local
NVIDIA/RTX or larger NVIDIA cluster for standard CUDA pipelines. Do not spend
DCU cycles on assets whose contract cannot be admitted.

**Success standard:**

- AUC >= 0.75 and non-zero TPR@1%FPR on a row-bound packet.
- Controls show random-level behavior under label shuffle or permutation.
- Evidence can update `claim_trace.csv` without weakening admission wording.

**Failure value:** A reviewed blocker strengthens Direction A/C by showing
which public artifact surfaces are missing.

Current manifest-first scout:
[`e1-manifest-first-scout-2026-06-06.md`](e1-manifest-first-scout-2026-06-06.md).
CopyMark was the closest historical second-asset challenger, but the current
authenticated no-download gate still fails because no compact row manifest or
no-training verifier is public. On 2026-06-08, NDSS-324 / Zenodo
`10.5281/zenodo.13371475` became the strongest compute-gated E1 candidate:
its public ZIP central directory exposes fine-tuned Stable Diffusion LoRA
checkpoints plus member/nonmember dataset PKLs, but no score-vector, ROC,
metric JSON, generated-response, or verifier files despite the paper appendix
claiming score vectors are stored in the artifact package. It is not a public
score/response asset yet. The same-day full-ZIP bounded probe verified
the archive but found only `image`/`text` fields in the nested dataset payloads,
no immutable row-id fields, no complete paper-faithful target/shadow
member/nonmember split manifest, and no public score packet. Quantile Diffusion
MIA and Tracing the Roots remain support packets unless their manifest gates
change.

The late 2026-06-09 no-download refresh over the nine-row high-value watchlist
found no gate-changing public-source delta. `E1-NDSS-324`, CopyMark, MoFit,
MIA_SD, SAMA, MIA-EPT, `diffusion_mia`, ReMIA, and OpenLVLM-MIA all kept the
same public identities and the same admission blockers. The field comparison
against the earlier 2026-06-09 refresh had zero gate-critical differences.
Focused NDSS-324 follow-up confirmed unchanged GitHub `main`
`93ee8dd4d12697354cd182461a9aa268b8de63e6`, unchanged Zenodo record `13371475`
with the single `736,366,195` byte ZIP, and no compact manifest, score, ROC,
metric, response, or verifier packet. Focused CopyMark/MoFit follow-up confirmed
unchanged public source identities. MoFit remains the strongest bounded support
follow-up, but it still lacks explicit row IDs, immutable public checkpoint
identity, official metric JSON/ROC/verifier, and surface-delta controls. This
refresh supports the current no-compute decision.

### E2. Measurement Baseline False-Promotion Study

**Hypothesis:** DiffAudit's contract should measurably prevent false claim
promotion compared with weaker review rules.

Concrete protocol: see
[`e2-false-promotion-protocol-2026-06-06.md`](e2-false-promotion-protocol-2026-06-06.md).
The first three-reviewer pilot is archived in
[`e2-pilot-2026-06-06/`](e2-pilot-2026-06-06/). The revised-codebook v2 pilot
outputs are in
[`e2-pilot-2026-06-06-v2/`](e2-pilot-2026-06-06-v2/). The v2 pilot passed the
internal Go/No-Go gate: allowed wording raw agreement is `0.9333`, provenance
agreement is `1.0`, consumer/delta agreement is `0.8`, and the decision is
`go-freeze-n50-preflight`. These outputs support only the internal Go/No-Go
decision and must not be cited as external adjudication evidence.

The current N=50 freeze preflight seed table is in
[`e2-n50-freeze-preflight-2026-06-06/`](e2-n50-freeze-preflight-2026-06-06/).
It contains `51` distinct seed rows and `23` candidate/followup rows, but the
strict freeze triage now says there are `0` directly freezable external
denominator rows. The v1 review covered five existing external candidates:
`E2Q-004` CLiD, `E2Q-005` Tracing the Roots, `E2Q-006` CopyMark, `E2Q-009`
MIDST Blending++, and `E2Q-011` Quantile/SecMI. The immediate follow-ups have
now narrowed: `E2Q-005` completed a 3-reviewer feature-packet review and remains
`bounded-support`; `E2Q-006` completed an authenticated no-download manifest
recheck and remains missing-surface support; `E2Q-004` completed the current
no-download identity check and remains row-to-COCO-manifest-missing support.
The MT-MIA stratum decision is also closed for this cycle: `E2SCT-001` stays
bounded cross-domain support, not a new image-diffusion denominator. Six
review-target rows have no public URL candidate and must stay internal-only unless
a public source replaces the local/restricted evidence note.

A no-download public-surface scout queue now has `28` new candidates after
adding `E2SCT-028` SD-MIA. URL checks reached `41 / 41` public URL candidates.
The 2026-06-07/2026-06-08 detailed checks produced a thirteen-row C14
false-promotion stress object after adding `E2SCT-024` DME as an
official-repo-stub exemplar, then closed the remaining post-C14 expansion queue
to `0` rows. `E2SCT-022`, `E2SCT-023`, `E2SCT-028`, and `E2SCT-025` are
support-only or code-public references, not C14 rows. `E2SCT-003` DurMI is also
closed as support-only TTS/audio cross-modal watch-plus: paper/supplement and
dataset/checkpoint metadata are public, but no ready duration-loss
score/ROC/metric packet or TTS/audio consumer lane exists. `E2SCT-025`
Hyperparameter-Free SecMI is closed as duplicate third-party SecMI-family
support: aggregate README metrics and runnable code are public, but public
per-row scores, ROC/metric packets, verifier artifacts, and independent
consumer-boundary review are absent. The 2026-06-09 SAMA, MIA-EPT,
`lijingwei0502/diffusion_mia`, and ReMIA checks add only DLM/text, tabular,
image-diffusion code-and-split, and tabular aggregate-archive support
surfaces. The `diffusion_mia` repo is
image-diffusion relevant and commits two DDIM CIFAR split files, but it exposes
no public row-bound score/response packet, completed result CSV, metric
artifact, checkpoint-bound verifier, or no-training replay package. The
`aindo-com/remia` archive exposes `2,879` aggregate JSON summaries and no
row-scale score/label arrays, so it also stays outside the image-diffusion
denominator and second-asset route. The
Direction A
paper now has a
packet-ready C14 review bundle, row trace, template, author answer key, and
codebook, but it still has zero independent C14 labels and no reviewer
reliability, N50 denominator, prevalence, admitted-evidence, or compute-release
claim. The next blocker is independent external labeling or new row-bound public
surfaces, not model compute.

**Baselines:**

- Score-only rule: admit if paper or artifact reports high AUC.
- Code-availability rule: admit if a public repository exists.
- Artifact-availability rule: admit if any split/checkpoint/code artifact exists.
- DiffAudit contract: target/split/score-or-response/metric/provenance/
  consumer-boundary/surface-delta gates.

**Corpus:**

- Preregistered distinct-surface corpus, not a cherry-picked evidence-note set.
- Target minimum: 50 distinct diffusion/privacy artifact surfaces.
- Include accepted papers, arXiv papers, official repos, HF/Zenodo/OpenReview
  artifacts, and known negative/support cases.

**Success standard:**

- Quantify false-promotion and false-blocking against external adjudication.
- Report agreement and disagreement categories with external label audit.
- Show at least several examples where weaker rules would overclaim and
  DiffAudit's allowed wording changes the claim state.

**Failure value:** If contract decisions do not differ meaningfully from simple
baselines, Direction A should be downgraded to an internal artifact note.

### E3. NVIDIA Standard-UNet Calibration

**Hypothesis:** The weak DCU results are caused by constrained SafeConv/training
quality, not by a general failure of gray-box diffusion MIA.

**Scope:**

- Standard CUDA Conv UNet, CIFAR-10, Research-admitted PIA/SecMI-compatible
  split and attack contract.
- One target scale-up, not a seed/timestep matrix.

**Success standard:**

- Reaches the admitted PIA/SecMI neighborhood, or at least AUC >= 0.70 with
  non-zero low-FPR recovery.

**Current status:** deferred. This is not on the default queue while E2 is
unrun. Reopen only if a standard CUDA target can test a new paper-changing
hypothesis with one bounded run.

**Failure value:** Closes self-trained CIFAR-10 DDPM as a paper-upgrading path
and prevents further DCU/SafeConv effort.

### E4. DCU Closure Evidence

**Hypothesis:** AUC 0.52-0.535 on TC192 is the true ceiling, not K=500 noise.

**Current status:** closed as a weak negative/support line. TC192 e18 focused
results did not produce paper-upgrading signal. Keep the manifest and one-page
negative verdict for auditability; do not run K=2000/K=5000 or same-family
matrices by default.

## 4. Stop Rules

Stop these unless a new hypothesis changes a paper decision:

- More TC64/TC128/TC192 epochs, seeds, or timestep matrices.
- TC256 on 16GB DCU.
- LR fusion, DDIM interval, noise-norm, or loss-score grids around the same weak
  CIFAR-10 checkpoints.
- Same-cache H2 feature sweeps, KDE/shadow-density/repeat-count tuning, or
  response-cloud cosmetic ablations.
- Broad no-download metadata sweeps that only re-find existing weak surfaces.
- New validators, dashboards, databases, daemons, or Platform/Runtime schema
  around candidate-only evidence.

## 4.1 2026-06-06 Seven-Day Execution Board

The next seven days are evidence-object triage, not paper polish and not
compute saturation.

1. **E2 corpus freeze path**
   - Advance only no-download public-source refresh, duplicate review, and
     six-gate annotation.
   - `E2Q-005` single-row feature-packet review is complete. Three reviewers unanimously
     selected `bounded-support`; the aggregation decision is
     `accept_feature_packet_review_row` with target/provenance still `Partial`.
     See
     [`e2-n50-freeze-preflight-2026-06-06/e2q005_external_style_review_aggregation_2026_06_06.md`](e2-n50-freeze-preflight-2026-06-06/e2q005_external_style_review_aggregation_2026_06_06.md).
   - Do not call `E2Q-005` N50 evidence, external adjudication, black-box
     response evidence, or raw-provenance evidence.
2. **E1 CopyMark manifest-first gate**
   - Current authenticated no-download recheck is complete and still fails the
     compact manifest gate. GitHub `main` remains at
     `069ea0257533fd6d5ec96cbdedccd4a1b70ba9ea`; no compact manifest or
     no-training verifier was found; the HF dataset exposes only README plus a
     `5,662,307,542` byte `datasets.zip`.
   - See
     [`e2-n50-freeze-preflight-2026-06-06/e2q006_copymark_compact_manifest_gate_2026_06_06.md`](e2-n50-freeze-preflight-2026-06-06/e2q006_copymark_compact_manifest_gate_2026_06_06.md).
   - No HF zip, image folder, model folder, score-regeneration script, or GPU
     job is released. Recheck only if the GitHub commit, HF dataset SHA, or
     author-published artifact surface changes.
3. **CLiD / MT-MIA route decision**
   - The decision is recorded in
     [`e2-n50-freeze-preflight-2026-06-06/e2_next_route_decision_2026_06_06.md`](e2-n50-freeze-preflight-2026-06-06/e2_next_route_decision_2026_06_06.md).
   - `E2Q-004` CLiD remains identity-missing bounded support; retry only if a
     public row-to-COCO manifest appears or HF access allows metadata-only
     manifest inspection.
   - `E2SCT-001` MT-MIA remains bounded cross-domain support; do not open a
     tabular/relational stratum in the current image-diffusion N50 cycle.
4. **C14 false-promotion packet**
   - The thirteen-row C14 false-promotion stress object is assembled for the
     paper packet and remains pre-label. It has zero independent reviewer
     labels. Its allowed status is author-keyed stress control, with no
     reliability, prevalence, N50 denominator, admitted score/response, or
     compute-release claim.
   - The 2026-06-08 paper-facing wording pass tightened this boundary in the
     compiled manuscript: C14 is described as a hard-blind pre-label packet;
     the reported signal is author-keyed blockers plus weak-rule pressure. The release
     checker now forbids earlier overloading around `reviewer packet`,
     `support`, MoFit `replay`, and H2 `positive` wording. This was an
     intermediate paper-facing pass; the current paper and supplement hashes
     are recorded after the later method and reviewer-risk passes below.
   - A later 2026-06-08 paper-method pass made the manuscript more
     implementation-checkable without upgrading claims: `main.tex` now includes
     a gate-assignment procedure box; `check_paper_release_packet.py` checks
     citation/BibTeX hygiene plus reportable/non-reportable gate consistency,
     `first_blocker`, `replay_tier`, and candidate non-admission wording; and
     the H2 figure now includes a code-generated portability-boundary inset for
     img2img `25/25` and diagnostic `10/10` rows.
   - The follow-up reviewer-risk pass changed the main title/framing from
     `protocol evaluation` to a claim-admission protocol with boundary cases,
     added the Blind-MIA split-confound citation, renamed H2 as a
     metric-strength boundary case, and then tightened the title/contribution
     language to `A Claim-Admission Protocol for Diffusion
     Membership-Inference Scores: Boundary Cases and Evidence States`. C14 is
     now phrased as a pre-label stress object with comparison framing removed.
     This makes the C14/H2 presentation harder to overread: split
     gates require membership semantics, not merely two convenient source
     pools, and high AUC alone does not satisfy the admission path. Current
     `paper.pdf` remains 10 pages on letter paper, SHA-256
     `C7B19A8F8A8EA158ED5194E2C7371A9755F9657D96416CF6031DE51FA865A2F9`.
     The anonymous supplement ZIP SHA-256 is
     `69C3573355FA1183A49B0FCD299F13C1D7D471BDA65431CE32F44811AC0AE88B`.
     This improves review robustness only; it is not external adjudication,
     N50 evidence, admitted evidence, or compute release.
   - A follow-up release-gate pass now makes the pre-label C14 status artifact
     mandatory. `run_pr_checks.py` refreshes the C14 aggregation output, and
     `check_paper_release_packet.py` requires
     `false_promotion_external_review_packet_status.csv` plus the status
     Markdown to exist. In the current no-reviewer state it rejects drift away
     from `packet_ready_only`, any stale label-dependent CSV, missing
     no-reviewer/not-external-adjudication boundary text, or any nonzero
     external-adjudication, reliability, or compute-release switch.
   - `E2SCT-024` DME is included only as an official-repo-stub exemplar: its
     public repository is a one-commit README-only surface with no
     implementation, protocol, target/split manifest, checkpoint, score rows,
     ROC/metric JSON, or verifier.
   - `E2SCT-028` SD-MIA is closed as support-only code-public pre-training T2I
     MIA reference. It is recent and relevant, but the public tree does not
     commit row-bound score/response packets, split manifests, ROC/metric JSON,
     or verifier artifacts. Do not add it to C14 unless a future row-level check
     creates a clean exemplar and the paper assets/review bundle are regenerated.
   - `E2SCT-025` Hyperparameter-Free SecMI is closed as support-only duplicate
     SecMI-family evidence. Its README reports strong aggregate CIFAR-100 AUC/TPR
     and source code is public, but per-row score arrays, ROC/metric JSON,
     trained attacker weights, generated response packets, no-training verifier,
     and non-adjacent consumer-boundary evidence are absent. Do not add it to C14,
     N50, admitted rows, or compute queues unless a future public packet changes
     those gates.
   - A 2026-06-08 targeted live discovery pass checked SimA, SD-MIA, SAMA/DLM,
     and DEB after the post-C14 queue reached `0`; no public row-bound
     score/response packet, verifier, or compute-release target appeared. See
     [`e2-n50-freeze-preflight-2026-06-06/e2_targeted_public_artifact_discovery_2026_06_08.md`](e2-n50-freeze-preflight-2026-06-06/e2_targeted_public_artifact_discovery_2026_06_08.md).
   - A second 2026-06-08 targeted live discovery pass checked LSA-Probe, MIAGM,
     Memorization-LDM/GitHub+Zenodo, Health Privacy Challenge, SecMI,
     Reconstruction-based Attack, GSA, FSECLab MIA-Diffusion, and MIA_SD. It
     also found no public row-bound score/response packet, verifier, external
     denominator row, C14 row, admitted evidence, or compute-release target.
     `osquera/MIA_SD` has result-like committed files, but no immutable
     target/split manifest, score schema, metric JSON, checkpoint identity, or
     no-training verifier was observed. See
     [`e2-n50-freeze-preflight-2026-06-06/e2_targeted_public_artifact_discovery_2026_06_08_b.md`](e2-n50-freeze-preflight-2026-06-06/e2_targeted_public_artifact_discovery_2026_06_08_b.md).
   - A file-level MIA_SD follow-up confirmed that `dtu-400-target-loss.csv` is
     a training-loss time series, not row-level membership scores, and that the
     public source notes plus result-like pickle/ROC files still lack immutable
     row IDs, score schema, metric JSON, checkpoint identity, and a no-training
     verifier. That pass kept MIA_SD out of current C14, out of the external
     denominator, out of admitted evidence, and out of compute-release targets.
     See
     [`e2-n50-freeze-preflight-2026-06-06/e2_miasd_result_file_preflight_2026_06_08.md`](e2-n50-freeze-preflight-2026-06-06/e2_miasd_result_file_preflight_2026_06_08.md).
   - A dedicated `E2SCT-029` MIA_SD public-surface check then re-labeled the
     repo only as a C14-v2 candidate public-result-surface row. The public tree
     exposes result-like pickle files, ROC PGF files, and static pickle-key
     evidence for labels/predictions/ROC arrays, but the experiments' images
     are explicitly unpublished, row identities are not public, the target
     checkpoint identity is not immutable/public, and pickle is not a safe
     release verifier format. Treat MIA_SD as a C14-v2 public-result-surface
     candidate only. See
     [`e2-n50-freeze-preflight-2026-06-06/e2sct029_mia_sd_public_surface_check_2026_06_08.md`](e2-n50-freeze-preflight-2026-06-06/e2sct029_mia_sd_public_surface_check_2026_06_08.md).
   - A third 2026-06-08 targeted public-surface pass checked `Stry233/SAMA` and
     `kaslim/LSA-Probe` after the MoFit paper-facing update. `SAMA` exposes
     useful runtime metadata schema pressure for diffusion-language-model MIA,
     but no committed target identity, immutable member/nonmember row manifest,
     score/metadata packet, ROC/metric JSON, or no-training verifier.
     `LSA-Probe` remains implementation-pending. Neither row changes C14, N50
     denominator evidence, admitted evidence, second response/score asset
     status, or compute release. See
     [`e2-n50-freeze-preflight-2026-06-06/e2_targeted_public_artifact_discovery_2026_06_08_c.md`](e2-n50-freeze-preflight-2026-06-06/e2_targeted_public_artifact_discovery_2026_06_08_c.md).
   - A fourth 2026-06-08 targeted pass combined current-date R125 DreamBooth
     review with cross-modal/tabular scouting. MIA-KDE is the closest weak
     challenger because the public tree exposes `*_MIA_Distances.7z` archive
     entries and names TabDDPM among generators, but no no-download row-score
     CSV, ROC/metric JSON, manifest, target identity, or verifier is visible.
     Tab-MIA has member labels but targets tabular LLM privacy and lacks public
     attack-score packets; DOMIAS and Synthetic-Data-Privacy expose code/API
     paths whose score outputs are runtime products. ImageAuditor is paper-only
     IRAG/T2I retrieval-database membership pressure, and the 2022 T2I MIA
     OpenReview line is historical paper-only support; neither exposes an
     official row-bound artifact packet. Strong-filename GitHub searches also
   found no new compact score packet. This pass raises targeted post-queue
   discovery coverage to `20` candidates with `0` new row-bound score/response
   artifacts. See
   [`e2-n50-freeze-preflight-2026-06-06/e2_targeted_public_artifact_discovery_2026_06_08_d.md`](e2-n50-freeze-preflight-2026-06-06/e2_targeted_public_artifact_discovery_2026_06_08_d.md).
   - A fifth 2026-06-08 current arXiv/GitHub primary-source refresh checked
     SD-MIA (`2605.27020`), Silent Brush (`2605.17500`), Data-Free FL hardware
     MIA (`2604.19891`), DISCO-TAB (`2604.01481`), and Risk In Context
     (`2507.17066`). SD-MIA remains the already-covered `E2SCT-028` surface
     with unchanged GitHub HEAD and no public row-bound artifact; Silent Brush
     remains a semantic-shift/style-leakage watch; the other three rows are
     hardware-FL or tabular/ICL privacy surfaces outside the current
     image/latent-diffusion denominator. This pass found `0` new row-bound
     score/response artifacts and should prevent duplicate rescans unless a
     primary source changes. See
     [`e2-n50-freeze-preflight-2026-06-06/e2_targeted_public_artifact_discovery_2026_06_08_e.md`](e2-n50-freeze-preflight-2026-06-06/e2_targeted_public_artifact_discovery_2026_06_08_e.md).
   - A 2026-06-08 MoFit preflight found the strongest public score-surface lead
     in this cycle. `JoonsungJeon/MoFit` publishes compact COCO train/test text
     score files plus caption JSONL, and replaying the public `mia_th_COCO.py`
     logic over the four text files gives best `alpha = 0.55`, `ASR = 0.883`,
     `AUC = 0.941948`, `TPR@1%FPR = 0.488`, and `TPR@0.1%FPR = 0.324` on
     `500 / 500` rows. This is a high-priority support/candidate surface, not
     admitted evidence: target checkpoint identity is still local-path based,
     result rows lack explicit row IDs, row binding to caption JSONL has only a
     DiffAudit-side candidate caption-order manifest; score-file certification
     is absent, and the metric JSON/ROC plus
     bootstrap/permutation controls are DiffAudit-side checks over implicit
     score-file positions; upstream official row-bound controls are absent.
     The label-permutation null is random-level (mean AUC `0.500805`, 95%
     interval `[0.465629, 0.535924]`). Use MoFit as the public score-file
     boundary case. Exclude it from C14, N50, admitted rows, second-asset status,
     and compute queues until target identity, score-row binding,
     consumer-boundary, and surface-delta gates change.
     See
     [`e2-n50-freeze-preflight-2026-06-06/e2_mofit_public_score_surface_preflight_2026_06_08.md`](e2-n50-freeze-preflight-2026-06-06/e2_mofit_public_score_surface_preflight_2026_06_08.md).
   - A 2026-06-08 current-date recheck of FMIA/Frequency Components found no
     new public row-bound score/response surface beyond the older
     code-and-split-manifest OpenReview supplement. The note remains version
     `2` / `ICLR.cc/2026/Conference/Rejected_Submission`, and the supplement
     HEAD remains a `1,783,018` byte ZIP. Treat `E2SCT-030` as a current-date
     recheck of the older FMIA/`E2SCT-008` scout surface, not a new independent
     public-surface candidate. Keep it out of C14, N50, admitted rows,
     second-asset status, and compute queues unless a future attachment or
     author packet exposes row-bound scores/responses and a no-training
     verifier. See
     [`e2-n50-freeze-preflight-2026-06-06/e2sct030_frequency_components_public_surface_check_2026_06_08.md`](e2-n50-freeze-preflight-2026-06-06/e2sct030_frequency_components_public_surface_check_2026_06_08.md).
   - Dedicated 2026-06-08 artifact follow-ups also closed R125 DreamBooth,
     LAION-MI, and MIDM without changing the upgrade route. LAION-MI remains a
     strong L1 split artifact: the current HF dataset exposes `members=13,396`,
     `nonmembers=26,874`, and only `url`/`caption` rows, with no public
     score/response, ROC/metric packet, checkpoint hash, verifier, or
     surface-delta control. R125 DreamBooth / `ronketer/diffusion-membership-inference`
     still exposes notebook/report media and six scalar reconstruction losses,
     but the target LoRA/checkpoint and query set remain private-runtime
     artifacts with no public manifest or verifier. MIDM remains code-public
     watch-plus: GitHub HEAD is
     `a7e7be0e00da5ea9473a0e9e1d0091fec638c8c0`, but the current tree does not
     commit a row manifest, score/result packet, ROC/metric JSON, notebook
     outputs, target checkpoint hash, or no-training verifier. Keep all three
     out of C14, N50, admitted rows, second-asset status, and compute queues. See
     [`e2-n50-freeze-preflight-2026-06-06/e2q013_ronketer_dreambooth_public_surface_followup_2026_06_08.md`](e2-n50-freeze-preflight-2026-06-06/e2q013_ronketer_dreambooth_public_surface_followup_2026_06_08.md),
     [`e2-n50-freeze-preflight-2026-06-06/e2q020_laion_mi_dataset_surface_followup_2026_06_08.md`](e2-n50-freeze-preflight-2026-06-06/e2q020_laion_mi_dataset_surface_followup_2026_06_08.md)
     and
     [`e2-n50-freeze-preflight-2026-06-06/e2q022_midm_public_surface_followup_2026_06_08.md`](e2-n50-freeze-preflight-2026-06-06/e2q022_midm_public_surface_followup_2026_06_08.md).
5. **Direction A gate decision**
   - Current-cycle choice: build the measurement-upgrade path
     (larger corpus + external audit + false-promotion baselines). Keep the
     second-asset observable route closed in this cycle.
   - If the corpus route cannot produce row-bound external denominator evidence,
      keep Direction A as a bounded measurement submission path and keep
      CCF-A-level claims out of the paper.

Compute policy:

- Day 1-2: evidence review only; no GPU/DCU, no large downloads.
- Day 3-4: CPU/package work only; `E2Q-005`, CopyMark manifest, CLiD identity,
  MT-MIA stratum decision, and schema gates. These gates are now closed for the
  current cycle, and none releases compute.
- Day 5: at most one bounded small run, only after target/checkpoint identity,
  exact split/query ids, row-bound score/response plan, metric provenance,
  controls, consumer/delta boundary, and duplicate/stratum policy pass.
- Day 6: evaluate and stop if AUC is near random, CI crosses `0.5`, low-FPR is
  `0`, or untrained/control baselines are comparable.
- Day 7: approve a long run only if the bounded run can update `claim_trace.csv`
  or the evidence contract without weakening admitted wording.

## 5. Minimum Engineering Platform

Engineering exists only to increase research throughput and auditability.

Must build:

- `scnet/experiments/index.jsonl`: one row per HPC run with hypothesis,
  decision value, command, job id, script hash, checkpoint, result path,
  key metrics, status, failure class, and next action.
- `scnet/output/cancon-results/MANIFEST.json`: machine-readable result index
  with metrics and file hashes.
- `scnet/scripts/cancon/`: mirror of the exact remote scripts that produced
  train/eval results.
- A tiny failure classifier for OOM, time limit, missing module, bad dataset
  read, cancelled-after-progress, and no-log-progress hang.
- One reproduction checklist that states success thresholds and stop conditions
  before GPU/DCU work starts.
- `scripts/check_e2_freeze_preflight.py`: offline schema and boundary guard
  for the current E2 preflight tables, so scout/candidate rows are not silently
  promoted into external denominator evidence.

Do not build:

- Web dashboards, database services, general scheduler frameworks, or container
  platforms.
- Full experiment-matrix generators for weak lines.
- Platform/Runtime integration for Research-only candidates.

## 6. Research Operating Loop

Every cycle must produce exactly one of:

- `asset verdict`
- `metric verdict`
- `paper-roadmap update`
- `evidence packet`

Every cycle must state:

- What claim would change if this succeeds?
- What claim would be closed if this fails?
- Which paper track receives the result?
- Which stop rule prevents further same-family expansion?

Subagents should be used by default for:

- artifact scout / external surface refresh,
- experiment-value critique,
- reviewer-risk critique,
- engineering-platform audit.

The main agent owns final roadmap truth and result promotion.

## 7. 2026-06-06 Cross-Review Verdict

Four side reviews were run before finalizing this roadmap:

- **Measurement-route review:** The measurement-upgrade direction is
  scientifically plausible,
  but the measurement path needed an executable false-promotion protocol. This
  produced
  [`e2-false-promotion-protocol-2026-06-06.md`](e2-false-promotion-protocol-2026-06-06.md).
- **Experiment-value review:** DCU/scnet DDPM has value only as weak
  negative/support evidence after the focused TC192 adjudication. It should not
  become a main paper contribution.
- **Engineering-platform review:** The right engineering scope is a JSONL run
  index, result manifest, script mirror, log classifier, and reproduction
  checklist. No dashboard, database, scheduler framework, or Platform/Runtime
  integration is justified.
- **Docs-consistency review:** Root and Research roadmaps needed to stop saying
  Phase B polish was the active Research posture. They now point to the
  evidence-object gate and this roadmap.

Cross-review conclusion: E2 v2 passed the internal Go/No-Go gate without
upgrading Direction A. Next step: freeze a public-source-first corpus, then
label C14 under the launch protocol. The current freeze handoff is
[`e2_public_source_freeze_ledger_2026_06_09.md`](e2-n50-freeze-preflight-2026-06-06/e2_public_source_freeze_ledger_2026_06_09.md):
`11` rows, with `bounded_support=1`, `packet_ready_only=1`,
`no_current_upgrade=9`, and compute-release rows at `0`. N50 adjudication
packets wait until the denominator is freezable. Strict triage says the current
`23` review-target rows include internal-only rows, restricted/local packets,
weak controls, metadata-only rows, and duplicate/support risks. Second-asset
scouting is manifest-first and bounded. Same-family DCU expansion is closed.

## 8. Next Two Weeks

1. Execute independent C14 reviewer labeling, or continue targeted discovery for a new
   row-bound public surface. The C14 packet is prepared for labeling; it is
   not a result until independent reviewer CSVs exist and the conservative
   aggregation status allows only the claims the paper states.
2. Build a new freeze-candidate table only from rows with public-source refresh
   plus a concrete artifact surface; keep internal H2/CommonCanvas/ReDiffuse and
   restricted SD ReDiffuse rows out of the external denominator.
3. Apply distinct-surface de-duplication and stratification before counting
   toward `E2-20260606-N50`; repeated paper/title/repo variants must prove a
   distinct target, split, score, response, or consumer boundary.
4. Build N50 blind-adjudication packages only after each selected row has a new
   E2 row id, refreshed source URL, artifact/score/response surface summary,
   duplicate-surface review, and row-bound gate notes.
5. Keep E1 scouting manifest-first. CopyMark currently fails the compact
   manifest gate and is not a second-asset candidate in this cycle. NDSS-324's
   full ZIP has now been verified but still fails row-id, complete split, and
   score-packet gates. No GPU job is allowed unless a future public
   manifest/verifier changes one of those gates.
6. Keep scnet run index and synced manifest as audit hygiene for the closed DCU
   line, not as the research critical path.
7. Continue the measurement-upgrade path: larger corpus + external audit +
   baseline false-promotion study. Keep the observable-push branch and MT-MIA
   tabular/relational stratum closed unless a new public row-bound asset changes
   the current route decision.
8. Keep the Stage 2.5 integrity gate active for the paper packet. On
   2026-06-09, `reference_integrity_audit.csv` verified all `27` bibliography
   entries through DOI handles, arXiv abstracts, or official source URLs, and
   `check_paper_release_packet.py` now rejects missing, unverified, or
   identifier-drifted reference-audit rows. This improves submission hygiene
   and auditability; it does not change the CCF-A blocker. The blocker remains
   independent C14 labels, a larger externally adjudicated public-surface
   corpus, or a second independent row-bound score/response asset.

If this path cannot yield a viable external denominator and audit object, keep
Direction A as bounded measurement work and stop spending compute on same-family
weak experiments.
