# Direction C Broader Source Pass 2026-05-27

> Status: frozen API-metadata batch.
> Scope: no-download Hugging Face Hub, Zenodo, and OpenReview source pass for
> Direction C.

This batch addresses one reviewer-facing weakness in the Direction C plan: the
2026-05-26 fixed-search batch covered GitHub and arXiv only. The 2026-05-27 pass
adds three additional public metadata sources without downloading models,
datasets, PDFs, repositories, or archives.

The machine-readable table is
[`../data/artifact_corpus_broader_source_20260527.csv`](../data/artifact_corpus_broader_source_20260527.csv).

## Fixed Protocol

| Field | Value |
| --- | --- |
| Batch ID | `bs20260527` |
| Frozen date | 2026-05-27 |
| Reviewer | Direction C review lead |
| Sources | Hugging Face Hub model API, Zenodo records API, OpenReview notes search API |
| Queries | `diffusion membership inference`; `diffusion memorization privacy`; `stable diffusion membership inference` |
| Download policy | API metadata only; no model files, datasets, Spaces execution, Zenodo files, PDFs, proceedings crawl, repository clone, or experiment. |
| Inclusion unit | Source-query observation, with titled OpenReview records separated from untitled search-hit noise. |
| Claim scope | Metadata-screening/query hygiene and search-surface boundary only; no prevalence, reproducibility, replayability, or artifact-quality claim. |

## Flow Summary

| Step | Count | Note |
| --- | ---: | --- |
| Hugging Face Hub model queries | 3 | All returned zero model records for the fixed terms. |
| Zenodo title-exact record queries | 3 | All returned zero title-exact records for the fixed terms. |
| OpenReview note-search queries | 3 | Two returned only untitled/no-paper search hits in the first ten results. |
| Titled OpenReview paper surfaces | 1 distinct paper | Four duplicate WACV/CoRR records for `Towards More Realistic Membership Inference Attacks on Large Diffusion Models`. |
| New distinct artifact surfaces | 0 | The titled OpenReview paper duplicates the 2026-05-26 arXiv metadata row. |
| New admitted audit rows | 0 | No target/split/score/response packet appeared under the no-download protocol. |
| New heavy work released | 0 | Stop rule held. |

## What This Supports

- Direction C can now say that the current no-download metadata pass is not
  limited to GitHub and arXiv.
- The pass records that source APIs can produce empty, noisy, duplicate, and
  titled metadata states that must not be treated as replay evidence.
- The OpenReview duplicate strengthens provenance for an already-known paper
  surface without adding a new scoreable or admitted row.

## What This Does Not Support

- It does not make Direction C a field-wide survey.
- It does not add the `10-20` new artifact surfaces previously listed as the
  target for stronger standalone aggregate claims.
- It does not establish inter-rater reliability, external label audit, or
  artifact-quality prevalence.
- It does not justify any model, dataset, PDF, repository, or archive download.
- It does not promote the duplicate OpenReview paper surface beyond metadata
  support.

## Decision

The broader source pass is useful as metadata-screening/query hygiene, not as a route to
stronger aggregate claims. Direction C may cite it as a second no-download
source family alongside the GitHub/arXiv fixed-search batch, but standalone
CCF-B-style aggregate claims still require a larger distinct-surface frozen corpus with new
distinct surfaces or an external label audit protocol if reliability is claimed.
