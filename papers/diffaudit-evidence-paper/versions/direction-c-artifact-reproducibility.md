# Version C: Selected-Corpus Artifact Claim Support

## Research Team

| Role | Owner | Responsibility |
| --- | --- | --- |
| Measurement lead | Claim-support lead | Define candidate-inclusion protocol and failure taxonomy. |
| Artifact engineer | Provenance audit lead | Check manifests, hashes, row binding, replay commands, and metrics. |
| Table/figure lead | Corpus visualization lead | Build gate heatmap, artifact funnel, and signal-vs-completeness plot. |
| Cherry-pick auditor | Selection-bias critic | Ensure corpus selection is frozen before conclusions. |

## Target Paper

| Field | Choice |
| --- | --- |
| Working title | When Diffusion MIA Scores Are Not Audit Evidence: A Selected-Corpus Claim-Support Study |
| Paper type | Selected-corpus artifact claim-support measurement paper |
| Venue posture | SaTML, MLSys, or FAccT methods track; reproducibility venue only if replay rows are separated from metadata-only rows |
| Current status | v0/v1 corpus, 2026-05-26 fixed-search batch, and a selected-corpus gate-label consistency pass exist; plausible second manuscript only under selected-corpus claims |

## Abstract Draft

In a frozen selected corpus of DiffAudit evidence notes and a small fixed
GitHub/arXiv metadata search, we study which claims each diffusion MIA artifact
surface can support. Artifact availability is not the same as auditability, and
metadata-only evidence is not the same as reproduction. We code rows through
six gates: target identity, split semantics, score or response coverage, metric
provenance, consumer-boundary fit, and surface delta. The selected corpus
contains useful but different strata: positive feature packets, weak bounded
scouts, source-confounded collaborator/local packets, metadata-only public
surfaces, and internal admitted controls. This paper argues for reporting what
survives reusable, row-bound, finite-tail, consumer-safe constraints without
treating selected-corpus counts as field-wide prevalence.

## Core Thesis

The scientific object is not whether public artifacts are "good" or "bad." The
object is what exact claim each coded artifact surface can support after row
binding, metric provenance, consumer-boundary checks, and surface-delta checks.

## Main Claims

| Claim | Evidence | Boundary |
| --- | --- | --- |
| C1: Scoreability is weaker than auditability in the selected corpus. | Tracing Roots, CLiD, CopyMark, ReDiffuse, CommonCanvas, MIDST notes, v1 corpus, and fixed-search batch | Selected-corpus claim only; not a field-wide prevalence claim. |
| C2: Positive feature packets can still be non-admitted. | Tracing Roots AUC `0.815826` | Feature packet lacks raw image/checkpoint consumer surface. |
| C3: Weak bounded scouts are useful exclusions. | ReDiffuse `0.4996/0.5053`, CommonCanvas `0.5148`, MIDST `0.598079` | Does not disprove original methods. |
| C4: Source confounding must be audited before membership claims. | SD ReDiffuse AUC `0.710319`, source-only AUC `1.0` | Cross-source stress test, not same-distribution MIA. |

## Section Spine

| Section | Job |
| --- | --- |
| Introduction | Explain why artifact availability is not the same as scientific reuse. |
| Selected-Corpus Protocol | Freeze inclusion criteria and covered sources before reporting outcomes. |
| Six Gates | Define exact checks and examples of pass/partial/fail. |
| Results | Gate matrix as coded rows in this corpus; replayable positives, weak scouts, source confounds, and metadata-only rows are not pooled as one reproducibility denominator. |
| Lessons | State how future papers can publish reusable MIA evidence. |
| Threats | Address cherry-picking, local environment bias, and partial artifacts. |

## Minimum Next Work

| Work | Why it matters |
| --- | --- |
| Use the completed selected-corpus consistency pass as the current gate matrix. | Prevents one-reviewer labels from being silently treated as unreviewed aggregate evidence. |
| Add one broader fixed-source pass or a second reviewer only if targeting standalone aggregate claims. | Prevents selected-corpus claims from becoming field-wide prevalence claims. |
| Add checksums/URLs only where already recorded or easily verified. | Keeps the paper reproducible without downloading large assets. |

## Refused Work

| Refused | Reason |
| --- | --- |
| Ranking papers by "failure" | Scientifically hostile and inaccurate. |
| Full dataset/model downloads | The paper is about artifact surface, not recreating every experiment. |
| Broad claims about all diffusion MIA papers | Current corpus is not yet broad enough. |

## Decision

The v1 corpus and fixed-search rows now pass a selected-corpus consistency
review with no invalid gate values, evidence/metric contradictions, or label
promotions; four empty-result `delta_gate` labels were demoted from `Partial` to
`Fail`. This can become a stronger standalone measurement paper than Direction B
only if the corpus grows or receives a second independent label review without
heavy GPU work or field-wide overclaiming.
