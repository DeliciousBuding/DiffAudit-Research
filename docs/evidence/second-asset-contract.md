# Second-Asset Contract

> Date: 2026-05-23
> Status: Research-side contract definition / no GPU release / no candidate selection
>
> This document defines the minimum requirements a candidate must satisfy to be
> considered a genuine "second asset" -- a new diffusion model target family that
> expands evidence beyond the current single (DDPM, CIFAR-10) surface.

## 1. Why a Second Asset

All five admitted Platform/Runtime evidence rows share one asset family:

| Row | Track | Method | Model | Dataset |
| --- | --- | --- | --- | --- |
| recon DDIM public-100 step30 | black-box | recon | Stable Diffusion v1.5 + DDIM | public subset |
| PIA GPU512 baseline | gray-box | PIA | CIFAR-10 DDPM | CIFAR-10 |
| PIA GPU512 + dropout defense | gray-box | PIA | CIFAR-10 DDPM (defended) | CIFAR-10 |
| GSA 1k-3shadow | white-box | GSA | CIFAR-10 DDPM | CIFAR-10 |
| GSA 1k-3shadow + DPDM W-1 | white-box | GSA | DPDM / Diffusion-DP | CIFAR-10 |

Four of five rows use a single target model family (DDPM on CIFAR-10 32x32
unconditional). The fifth uses DPDM, which is a DP-trained variant of the same
architecture. This is one surface.

For scientific validity, the claim "diffusion model membership can be audited"
must be demonstrated on at least one genuinely different target family -- a
different dataset, a different architecture, a different conditioning paradigm,
or a different modality with authentic member/nonmember ground truth.

## 2. Existing Admitted Asset Pattern (Reference)

Every admitted row conforms to this pattern:

### 2.1 Target Identity

- **Model architecture**: Specified (DDPM, DPDM)
- **Checkpoint**: Workspace-verified checkpoint directory with fixed state dict
- **Format**: Accelerate checkpoint directory (white-box) or raw `.pt` (gray-box)
- **Training provenance**: CIFAR-10 dataset, known training recipe
- **Hash-ability**: Checkpoint is locally stored and workspace-verified, though
  not every admitted row stores a public SHA-256 of the checkpoint file itself

### 2.2 Split Contract

- **Member definition**: Derived from CIFAR-10 train split (50,000 images)
- **Nonmember definition**: Derived from CIFAR-10 test split (10,000 images)
- **Index manifests**: Exact numpy `.npz` arrays with `mia_train_idxs`,
  `mia_eval_idxs`, and `ratio` (where applicable)
- **Verifiability**: Split file is stored with the asset bundle; indices are
  reproducible by re-extracting from the canonical CIFAR-10 archive

### 2.3 Score Contract

- **Resolution**: Row-level -- one score per evaluated sample
- **Packet size**: Known cardinality (e.g., 512 per split for PIA, 2000 for GSA)
- **Score type**: Continuous scalar (loss value, classifier activation,
  DreamSim distance)
- **Format**: JSON summary with metric arrays; canonical summary.json per run

### 2.4 Metric Contract

Four standard headline metrics:

- **AUC**: Area under the ROC curve
- **ASR**: Attack success rate at a fixed threshold
- **TPR@1%FPR**: True positive rate at 1% false positive rate
- **TPR@0.1%FPR**: True positive rate at 0.1% false positive rate

### 2.5 Low-FPR Interpretation

All admitted rows use the same finite-empirical-tail interpretation:

- The nonmember denominator (N) is fixed and known
- TPR@1%FPR uses approximately N/100 false positives
- TPR@0.1%FPR uses approximately N/1000 false positives
- These are finite packet readouts, not continuous calibrated estimates
- The minimum nonzero FPR is 1/N

### 2.6 Provenance

- **Asset grade**: `single-machine-real-asset` or `real-asset-closed-loop`
- **Evidence level**: `runtime-mainline` (or `runtime-smoke` for DPDM)
- **Status**: `workspace-verified`
- **Source**: Canonical dataset archive (cifar-10-python.tar.gz) with known
  provenance
- **Run output**: Canonical summary.json from a recorded run

## 3. Minimum Second-Asset Contract

A candidate must clear all six gates. If any gate fails, the candidate cannot
serve as a second asset for the purposes of scientific portability claims.

### Gate 1: Target Identity

| Requirement | What it means |
| --- | --- |
| Architecture specified | Model class, parameter count, and architecture name (e.g., DDPM, DiT, EDM, TabDDPM, LDM) must be documented. |
| Checkpoint exists | A frozen, trained model checkpoint must be publicly accessible or locally stored with a verifiable SHA-256 hash. Training code alone is insufficient. |
| Checkpoint is accessible | The checkpoint link must resolve (HTTP 200 or equivalent). Google Drive links returning HTTP 401 or 403 are gated. |
| Training provenance is known | The dataset used to train the target, and the training recipe (epochs, hyperparameters, data preprocessing), must be documented. |
| Identity is fixed | The checkpoint must not change between evaluations. A "download and train" instruction is not a fixed identity. |

**Fail if**: checkpoint is missing, inaccessible, unverifiable, or merely
"download and train from scratch."

### Gate 2: Split Contract

| Requirement | What it means |
| --- | --- |
| Member split exists | An exact member sample manifest (indices, filenames, or row IDs) must be publicly available or locally stored with a verifiable hash. |
| Nonmember split exists | An exact nonmember manifest, drawn from the same domain but disjoint from the training set, must be available with the same standard. |
| Membership semantics are clear | The membership definition must be unambiguous and match standard MIA practice (member = was in the training set of the target model). |
| Split cardinality is known | Exact member/nonmember counts must be published. Unknown or approximate sizes are not acceptable. |
| Split is hash-able | The split file must be stored as a fixed artifact (`.npz`, `.npy`, `.json`, `.csv`) with a verifiable SHA-256 hash. |
| Split provenance is documented | The source dataset and the split derivation method must be documented. A split with no provenance trace is not verifiable. |

**Fail if**: split indices are missing, sizes are approximate, the split
derivation is undocumented, or the published manifest cannot be rebinded to
the public surface (e.g., row identifiers no longer resolve).

### Gate 3: Query/Response or Score Coverage

| Requirement | What it means |
| --- | --- |
| Row-level scores exist | One score per evaluated sample, stored as a vector of length N (member + nonmember count). Aggregate-only metrics are insufficient. |
| Score packet is public or stored | The score array must be publicly downloadable or stored in the DiffAudit workspace with a verifiable hash. |
| Score type is specified | The meaning of the score (loss, likelihood, distance, classifier confidence, error ratio) must be documented. |
| Labels are complete | Every score has a corresponding member/nonmember label. |
| Generation is bounded | If scores are not precomputed, the command to generate them must have a known, bounded cost (GPU hours, wall-clock time). "Train and run everything" is not bounded. |

**Fail if**: only aggregate metrics exist, score arrays are missing, labels are
incomplete, or the path to generate scores is unbounded.

### Gate 4: Metric Contract

| Requirement | What it means |
| --- | --- |
| All four headline metrics | AUC, ASR, TPR@1%FPR, TPR@0.1%FPR must be computable or published. |
| Finite tail interpretation | The nonmember denominator must be reported so that FPR granularity can be assessed. |
| Minimum nonzero FPR | Must be stated (1/N where N is the nonmember count). |
| Metric source is verifiable | Metrics must be traceable to a specific score array or run summary. Declared metrics without score provenance are not verifiable. |

**Fail if**: only AUC is reported, the nonmember denominator is unknown, or
metrics are copied from a paper without artifact backing.

### Gate 5: Provenance and Verifiability

| Requirement | What it means |
| --- | --- |
| All assets are hash-able | Checkpoint, split file, score array, and metric summary should each have a verifiable hash or be stored in the DiffAudit workspace under version control. |
| No single-point-of-failure provenance | The checkpoint must not depend on a single researcher's local disk or an ephemeral Google Drive link. |
| Replay is defined | A bounded command exists that can reproduce the scores from the checkpoint and split. |
| Paper provenance is not enough | A paper result without public artifacts does not satisfy this gate. |

**Fail if**: artifacts are paper-only, Google-Drive-only, or require contacting
authors for the critical missing piece.

### Gate 6: Surface Delta (the "second" in second asset)

| Requirement | What it means |
| --- | --- |
| Different from current surface | The candidate must differ from the current DDPM/CIFAR-10 surface in at least one dimension: dataset, model architecture, conditioning paradigm, or modality. |
| Delta is documented | The specific difference must be stated explicitly (e.g., "same DDPM architecture, but CIFAR-100 dataset instead of CIFAR-10"). |
| Delta provides scientific value | A cosmetic change (different random seed, different training epoch) is not a genuine second surface. |

**Acceptable deltas**:

| Category | Example | Scientific value |
| --- | --- | --- |
| Same architecture, different dataset | DDPM on CIFAR-100 or STL-10 | Tests generalization of MIA across visual domains |
| Different architecture, same dataset | DiT on CIFAR-10, EDM on CIFAR-10 | Tests whether architecture affects auditability |
| Conditional diffusion | Stable Diffusion + exact member LoRA | Tests whether conditioning changes the attack surface |
| Different modality | TabDDPM on tabular data, graph diffusion, audio diffusion | Tests whether diffusion MIA extends beyond image domains |

**Not acceptable as second surface**:

- Same DDPM/CIFAR-10 with a different attack method (this is a different method, not a different asset)
- Same DDPM/CIFAR-10 with a different defense (this is a different defense, not a different asset)
- Same DDPM/CIFAR-10 with a different random seed or training epoch (no genuine surface delta)

## 4. Quick Assessment of Current Paths

### 4.1 Same-family: DDPM on CIFAR-100 / STL-10 / Tiny-IN

| Gate | Status |
| --- | --- |
| Target identity | **Fail**. ReDiffuse OpenReview supplement has DDPM attack/training code and exact split manifests, but no trained checkpoint. Same for FMIA OpenReview supplement. |
| Split contract | **Pass**. Exact `.npz` manifests with hashes exist: CIFAR100 (25000/25000), STL10 (50000/50000), Tiny-IN (50000/50000). |
| Score coverage | **Fail**. No score packets, no generated responses, no ROC CSVs. |
| Metric contract | **Fail**. No published metrics for these specific checkpoints. |
| Provenance | **Partial**. Splits are hashable but checkpoints and scores are missing. |
| Surface delta | **Pass**. Different dataset is a genuine surface delta. |

**Shortest path to closure**: Train a DDPM on CIFAR-100 from scratch using the
published split indices, then run PIA or GSA on the trained checkpoint. This
requires GPU time (estimate: comparable to the existing DDPM/CIFAR-10 training
cost) and produces a self-trained checkpoint rather than a public third-party
checkpoint. The scientific value is that the split indices are from a
third-party paper (ReDiffuse), even if the checkpoint is locally trained.

**Risk**: A self-trained checkpoint is weaker evidence than a public
third-party checkpoint. The training recipe must be documented and reproducible
for the result to be independently verifiable.

### 4.2 MIDM FFHQ

| Gate | Status |
| --- | --- |
| Target identity | **Fail**. The advertised Google Drive checkpoint returned HTTP 401. |
| Split contract | **Partial**. Scripts generate `ffhq_1000_idx.npy` locally, but no fixed public manifest exists. |
| Score coverage | **Fail**. No `loss_ffhq_1000_ddpm.h5py` or metric JSON published. |
| Metric contract | **Partial**. Code defines TPR-at-fixed-FPR metrics on 1000/1000 labels. |
| Provenance | **Fail**. Checkpoint and splits are not independently verifiable. |
| Surface delta | **Pass**. FFHQ (face images, 128x128) is a different domain than CIFAR-10. |

**Verdict**: Gated. Reopen only if the checkpoint becomes accessible and score
packets are published.

### 4.3 CopyMark / LAION-mi

| Gate | Status |
| --- | --- |
| Target identity | **Partial**. Stable Diffusion is public, but the specific LoRA/member setup depends on public parquet row binding. |
| Split contract | **Fail**. Official member numeric filenames do not map to current public `members.parquet` rows; public parquet exposes only `url` and `caption` columns. |
| Score coverage | **Partial**. Official score artifacts exist, but row binding is broken. |
| Metric contract | **Partial**. Metrics exist in official artifacts. |
| Provenance | **Fail**. Public surface cannot rebind scores to members. |
| Surface delta | **Pass**. Stable Diffusion + LAION subset is a different conditioning paradigm. |

**Verdict**: Blocked. Reopen only if authors publish a compact row-binding
manifest or restore the public identifier column.

### 4.4 MIDST TabDDPM (Tabular)

| Gate | Status |
| --- | --- |
| Target identity | **Pass**. MIDST challenge provides 70 TabDDPM model folders (30 train + 20 dev + 20 final) with synthetic tables. |
| Split contract | **Pass**. MIDST challenge rows have known labels (100 members, 100 nonmembers per model within the challenge phases). |
| Score coverage | **Partial**. Local scouts have generated row-level scores (nearest-neighbor distance, EPT error profile, shadow-distributional divergence). |
| Metric contract | **Pass** for local scouts. Scores exist but transfer-phase signal is weak (dev+final AUC ~0.53). |
| Provenance | **Pass**. Local scouts stored in workspace artifacts. |
| Surface delta | **Pass**. Tabular data is a genuinely different modality. |

**Verdict**: Weak signal on transfer phases blocks promotion. The train-phase
AUC is strong (0.85+ for EPT), but dev/final does not carry the signal
(AUC ~0.53). This is valuable as cross-modal support evidence but not as an
admitted second asset. Reopen only if a new public artifact or a genuinely new
tabular-diffusion membership observable changes the dev/final transfer story.

### 4.5 MT-MIA Relational Tabular

| Gate | Status |
| --- | --- |
| Target identity | **Partial**. Generator family (ClavaDDPM, RelDiff), dataset, and seed are fixed, but trained checkpoint identities are not provided. Uses pre-generated synthetic tables instead. |
| Split contract | **Pass**. Public `split/mem` and `split/non_mem` relational CSVs. |
| Score coverage | **Pass**. 18 official JSONL score/metric packets with 2000 scores each. |
| Metric contract | **Pass**. AUC and fixed-FPR TPR values in official packets. |
| Provenance | **Pass** for score packets (public, hashable). Checkpoint provenance is missing. |
| Surface delta | **Pass**. Relational tabular diffusion is a different modality. |

**Verdict**: Stronger than MIDST and FERMI, and stronger than most watch items.
The 18 score packets are public, hashable, and contain both scores and metrics.
The blocking factor is the cross-modal scope boundary: current Platform/Runtime
admits only image/latent diffusion evidence. The generator uses precomputed
synthetic tables rather than frozen checkpoints. This is the strongest
candidate for a cross-modal second-asset expansion once a consumer-boundary
decision for relational tabular is made.

### 4.6 DurMI (TTS/Audio)

| Gate | Status |
| --- | --- |
| Target identity | **Partial**. OpenReview supplement has attack code; Zenodo has checkpoint metadata but no ready score arrays. |
| Split contract | **Partial**. GradTTS LJSpeech split (5977/5977) documented but not published as a fixed manifest file. |
| Score coverage | **Fail**. No duration-loss score arrays, ROC arrays, or metric JSON. |
| Metric contract | **Fail**. No published metrics. |
| Provenance | **Fail**. No ready verifier output. |
| Surface delta | **Pass**. TTS/audio is a different modality. |

**Verdict**: Watch-plus. Requires ready score arrays and a TTS consumer-boundary
decision. Not the most accessible path.

## 5. Recommendation

### Most Accessible Path: ReDiffuse DDPM on CIFAR-100

The ReDiffuse OpenReview supplement provides:
- Exact split manifests for CIFAR-100 (25000/25000) with SHA-256 hashes
- Attack/training code for DDPM
- A documented training recipe

What would close the gap:
1. Train a DDPM on CIFAR-100 using the published split indices (member =
   `mia_train_idxs` from the manifest)
2. Publish the checkpoint with a SHA-256 hash
3. Run PIA or GSA scoring against the checkpoint
4. Publish the score arrays and the four headline metrics

This is the shortest path because:
- The split contract is already satisfied by a third-party source
- The attack code is already workspace-compatible (PIA, GSA)
- The training recipe is documented
- CIFAR-100 is small enough for a bounded GPU budget

The cost is training a DDPM from scratch, which is non-trivial GPU work, but
the result would be a clean second surface: same architecture (DDPM), different
dataset (CIFAR-100), third-party split provenance (ReDiffuse).

### Strongest Cross-Modal Path: MT-MIA Relational Tabular

The MT-MIA repository provides 18 ready score packets with exact splits. This
is the only path that already has public score artifacts. The blocking factor
is purely a consumer-boundary scope decision: relational tabular membership is
not currently within the Platform/Runtime admitted scope.

A consumer-boundary decision to admit relational tabular evidence would unlock
this path with zero additional GPU work.

### Paths Not Worth Reopening

| Candidate | Reason |
| --- | --- |
| MIDM FFHQ | Checkpoint inaccessible (Google Drive 401); no score packets |
| CopyMark LAION-mi | Row-binding gap; public surface cannot rebind scores to members |
| MIDST TabDDPM | Transfer signal is weak; three scouts all confirmed |
| FMIA CIFAR-100/STL-10 | Same gap as ReDiffuse (no checkpoint) but ReDiffuse has better workspace compatibility |
| LSA-Probe | Mock demo data; no real score artifacts |
| GGDM | Code-only Zenodo archive; no checkpoint/split/score |
| FERMI | Paper-only; no code or artifacts |
| Noise Aggregation | Paper-only; no code or artifacts |
| TMIA-DM | Paper-only; no code or artifacts |

## 6. Using This Contract

When a new candidate appears (from paper search, OpenReview supplement, GitHub
release, or collaborator transfer), evaluate it against the six gates in order.
A candidate that passes gates 1-5 but fails gate 6 is a "same-surface
extension" (not a second asset). A candidate that passes gates 1-3 but fails
gate 4 or 5 is a "score-incomplete watch" (useful for future reference but not
ready).

Only a candidate that passes all six gates can be proposed as a genuine second
asset for the purposes of scientific portability claims.

## 7. Revision History

| Date | Change |
| --- | --- |
| 2026-05-23 | Initial contract definition. Documents the minimum six-gate standard and assesses current paths. |
