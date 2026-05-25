# Direction C Corpus v1: Metadata-Only Expansion

> Date: 2026-05-26
> Status: structured from existing DiffAudit evidence notes only; no new
> downloads, repository clones, model runs, or web refresh in this file.

This file upgrades Direction C from a starter protocol to a structured
measurement corpus. It does not claim to be a complete literature survey. It
records two strata:

- `v0`: current DiffAudit evidence surfaces already used by the Direction A
  paper.
- `v1`: ten metadata-only public-surface gates already present in
  `docs/evidence/`, added to reduce DiffAudit-history bias before a standalone
  reproducibility paper is attempted.

The machine-readable table is
[`../data/artifact_corpus_v1.csv`](../data/artifact_corpus_v1.csv).

## Inclusion Boundary

The v1 expansion includes only candidates with an existing evidence note that
already checked a public surface and recorded a no-download decision. No row in
this expansion required fetching model weights, datasets, generated images,
large archives, or source repositories during paperization.

Excluded from this v1 table:

- papers with no existing DiffAudit public-surface note;
- candidates whose only evidence is a copied headline metric;
- candidate surfaces that would require a fresh download to classify;
- private/local artifacts not already represented in the v0 corpus.

## Corpus Summary

| Stratum | Rows | Meaning |
| --- | ---: | --- |
| v0 current DiffAudit evidence | 11 | Admitted controls, candidates, support packets, bounded negatives, and collaborator/local stress cases. |
| v1 metadata-only expansion | 10 | Existing public-surface gates over adjacent diffusion/generative privacy papers and repositories. |
| Total structured rows | 21 | Enough for a Direction C gate matrix, not enough for broad prevalence claims. |

## v1 Expansion Rows

| ID | Candidate | Public surface | Artifact type | Main boundary |
| --- | --- | --- | --- | --- |
| v1-01 | Identity-Focused Inference / Extraction | arXiv `2410.10177v1`; no official repository found | paper source and metadata | identity-level privacy, no row-bound artifacts |
| v1-02 | RAPTA / ADMCD copying mitigation | arXiv `2603.13070v1`; no official repository found | paper source and metadata | copying/mitigation boundary, no score artifacts |
| v1-03 | GUARD surgical mitigation | official `kairanzhao/GUARD` repository | code-public repository | scripts exist, no row-bound score packet |
| v1-04 | BAF LoRA parameter-space mitigation | arXiv `2605.10439v1`; supplementary-code claim only | paper source and metadata | weight-only LoRA mitigation, no row artifacts |
| v1-05 | Broken Memories | arXiv `2605.22050v1`; no official code found | paper source and metadata | memorization mitigation, no prompt/score packet |
| v1-06 | IAR Privacy Attacks | official `sprintml/privacy_attacks_against_iars` repository | code-public repository | image-autoregressive family, no committed score packet |
| v1-07 | Silent Brush / Art Arena | arXiv `2605.17500v1`; metadata-readable code-notebook inventory | public metadata inventory | style leakage boundary, no row-bound membership artifact |
| v1-08 | Trajectory Generation Privacy | arXiv `2605.15246v1`; paper tables only | cross-domain paper source | trajectory domain, no score packet |
| v1-09 | Model Will Tell / DRC | arXiv `2403.08487v1`; no official code found | paper source and metadata | restoration mechanism, missing split-score artifact |
| v1-10 | Discrete DLM withdrawn paper | arXiv `2605.16445v2` withdrawn; no current PDF | withdrawn paper metadata | unstable record, no artifacts |

## v1 Gate Matrix

| ID | Target | Split | Evidence | Metric | Boundary | Delta |
| --- | --- | --- | --- | --- | --- | --- |
| v1-01 | Fail | Fail | Fail | Fail | Fail | Pass |
| v1-02 | Fail | Fail | Fail | Fail | Fail | Pass |
| v1-03 | Fail | Fail | Fail | Fail | Fail | Pass |
| v1-04 | Fail | Fail | Fail | Fail | Fail | Pass |
| v1-05 | Fail | Fail | Fail | Fail | Fail | Pass |
| v1-06 | Fail | Fail | Fail | Fail | Fail | Pass |
| v1-07 | Fail | Fail | Fail | Fail | Fail | Pass |
| v1-08 | Fail | Fail | Fail | Fail | Fail | Pass |
| v1-09 | Partial | Fail | Fail | Fail | Partial | Pass |
| v1-10 | Fail | Fail | Fail | Fail | Fail | Partial |

## What v1 Adds

The v0 corpus was useful but biased toward DiffAudit's active route decisions:
admitted rows, H2, ReDiffuse, CommonCanvas, Tracing Roots, CopyMark, MIDST, and
collaborator packets. v1 adds public-surface gates that are less tied to the
current admitted/candidate decision queue. The new rows are mostly
metadata-only no-artifact cases, including code-public repositories without
row-bound packets and semantic-shift papers whose privacy claims are adjacent
but not consumable by the current per-sample diffusion membership boundary.

This expansion supports three paper claims:

- Artifact availability, code availability, scoreability, and auditability are
  distinct states.
- Missing artifacts are heterogeneous: no official code, code with no score
  packet, withdrawn record, semantic-boundary mismatch, and cross-domain
  mismatch are different failure modes.
- A metadata-only first pass can prevent expensive downloads when the public
  surface already lacks target identity, split binding, row coverage, or
  consumer-boundary fit.

It does not support these claims:

- "Most diffusion MIA papers fail."
- "The original methods are wrong."
- "No public artifact is useful."
- "The corpus is complete for all diffusion or generative-model privacy work."

## Next Direction C Gate

The 2026-05-26 selected-corpus consistency pass reviewed this 21-row table plus
the 17-row fixed-search batch without changing CSV labels. The pass checked that
all gate labels use only `Pass`, `Partial`, or `Fail`; that bounded-negative
rows with passing evidence/metric gates but failing consumer-boundary gates are
intentional route-decision rows; and that fixed-search arXiv metadata rows with
partial target/boundary labels but failing evidence/metric gates remain
metadata-only rows, not scoreable artifacts.

This is a single-reviewer selected-corpus consistency pass, not inter-rater
reliability and not field-wide prevalence evidence. Before forking a standalone
Direction C LaTeX paper, add one more frozen source batch or a second independent
label review. If no new row-bound public packet appears, Direction C can still
be written as a claim-support measurement paper, but its aggregate claims must
remain about this structured corpus only.
