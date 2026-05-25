# Version C: Public Artifact Reproducibility

## Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Measurement lead | opus | Define candidate-inclusion protocol and failure taxonomy. |
| Artifact engineer | haiku | Check manifests, hashes, row binding, replay commands, and metrics. |
| Table/figure lead | sonnet | Build gate heatmap, artifact funnel, and signal-vs-completeness plot. |
| Cherry-pick auditor | opus | Ensure corpus selection is frozen before conclusions. |

## Target Paper

| Field | Choice |
| --- | --- |
| Working title | When Diffusion MIA Scores Are Not Evidence: A Reproducibility Study of Public Artifacts |
| Paper type | Reproducibility / measurement paper |
| Venue posture | SaTML, MLSys, NeurIPS Datasets and Benchmarks, FAccT methods track |
| Current status | v0/v1 corpus, 2026-05-26 fixed-search batch, and a selected-corpus gate-label consistency pass exist; plausible second manuscript only under selected-corpus claims |

## Abstract Draft

Diffusion membership inference papers increasingly publish code, checkpoints,
score packets, or supplementary files, but these artifacts do not always support
the claims downstream users want to make. We audit public artifact surfaces
through six gates: target identity, member split, nonmember split, score or
response coverage, metric provenance, consumer-boundary fit, and surface delta.
Across the
current DiffAudit candidate set, artifacts often become useful research
evidence while failing to become portable audit evidence. Tracing the Roots
ships a positive feature-packet replay with AUC `0.815826`, but lacks raw
checkpoint and sample provenance for image-level consumption. ReDiffuse STL-10
is locally scoreable but random-level under bounded denoising-loss and score-norm
scouts. CommonCanvas provides a real `50/50` response packet but weak scorers.
MIDST remains below the reopen floor. Stable Diffusion ReDiffuse is replayable
but source-confounded. This paper argues for reporting what survives reusable,
row-bound, finite-tail, consumer-safe constraints.

## Core Thesis

The scientific object is not whether public artifacts are "good" or "bad." The
object is what exact claim each artifact can support after row binding,
metric provenance, consumer-boundary checks, and surface-delta checks.

## Main Claims

| Claim | Evidence | Boundary |
| --- | --- | --- |
| C1: Public scoreability is weaker than auditability. | Tracing Roots, CLiD, CopyMark, ReDiffuse, CommonCanvas, MIDST notes, v1 corpus, and fixed-search batch | Selected-corpus claim only; not a field-wide prevalence claim. |
| C2: Positive feature packets can still be non-admitted. | Tracing Roots AUC `0.815826` | Feature packet lacks raw image/checkpoint consumer surface. |
| C3: Weak bounded scouts are useful exclusions. | ReDiffuse `0.4996/0.5053`, CommonCanvas `0.5148`, MIDST `0.598079` | Does not disprove original methods. |
| C4: Source confounding must be audited before membership claims. | SD ReDiffuse AUC `0.710319`, source-only AUC `1.0` | Cross-source stress test, not same-distribution MIA. |

## Section Spine

| Section | Job |
| --- | --- |
| Introduction | Explain why artifact availability is not the same as scientific reuse. |
| Corpus Protocol | Freeze inclusion criteria before reporting outcomes. |
| Six Gates | Define exact checks and examples of pass/partial/fail. |
| Results | Gate matrix, replayable positives, weak scouts, source confounds. |
| Lessons | State how future papers can publish reusable MIA evidence. |
| Threats | Address cherry-picking, local environment bias, and partial artifacts. |

## Minimum Next Work

| Work | Why it matters |
| --- | --- |
| Use the completed selected-corpus consistency pass as the current gate matrix. | Prevents one-reviewer labels from being silently treated as unreviewed aggregate evidence. |
| Add one broader fixed-source pass or a second reviewer only if targeting a standalone reproducibility paper. | Prevents selected-corpus claims from becoming field-wide prevalence claims. |
| Add checksums/URLs only where already recorded or easily verified. | Keeps the paper reproducible without downloading large assets. |

## Refused Work

| Refused | Reason |
| --- | --- |
| Ranking papers by "failure" | Scientifically hostile and inaccurate. |
| Full dataset/model downloads | The paper is about artifact surface, not recreating every experiment. |
| Broad claims about all diffusion MIA papers | Current corpus is not yet broad enough. |

## Decision

The v1 corpus and fixed-search rows now pass a selected-corpus consistency
review without CSV label changes. This can become a stronger standalone
measurement paper than Direction B only if the corpus grows or receives a second
independent label review without heavy GPU work or field-wide overclaiming.
