# Direction C Fixed-Search Batch 2026-05-26

> Status: frozen metadata-only batch.
> Scope: independent fixed-source/search process for Direction C.
> No downloads: no repositories cloned, no model/data/image archives fetched, no
> arXiv e-prints downloaded, and no CPU/GPU experiments released.

This batch adds an independent selection layer for the Direction C
claim-support paper. It is not a broad literature survey and it does not add a
new admitted DiffAudit evidence row. Its value is methodological: the search
date, sources, exact queries, no-download policy, inclusion decisions, and
six-gate labels are frozen before any aggregate paper claim is written.

The machine-readable table is
[`../data/artifact_corpus_fixed_search_20260526.csv`](../data/artifact_corpus_fixed_search_20260526.csv).

## Fixed Protocol

| Field | Value |
| --- | --- |
| Batch ID | `fs20260526` |
| Frozen date | 2026-05-26 |
| Reviewer | `opus` |
| Sources | GitHub repository search; arXiv API metadata search |
| Excluded sources | OpenReview, Hugging Face, Papers with Code, and Zenodo were not added in this batch because the goal was a small fixed pass, not a crawler. |
| Download policy | Metadata/tree/API only; no clone, no large file, no model, no dataset, no generated image packet, no e-print tarball, no experiment. |
| Inclusion unit | Public paper or repository surface returned by a fixed query, plus one row for empty fixed-query result sets. |
| Gate labels | Target identity, split, evidence, metric, boundary, and mechanism-delta gates use `Pass`, `Partial`, or `Fail`. |
| Claim scope | Selection-process evidence and artifact-surface taxonomy only; no prevalence claim over all diffusion MIA work. |

## Exact Queries

GitHub repository queries:

| Query | Top-level result |
| --- | --- |
| `diffusion membership inference` | `ronketer/diffusion-membership-inference` |
| `MIA diffusion` | `fseclab-osaka/mia-diffusion` |
| `diffusion privacy attack` | `Divya1201/diffusion-privacy-attacks` |
| `Stable Diffusion membership inference` | no direct repository hit |
| `diffusion memorization membership` | no direct repository hit |
| `membership inference diffusion models` | no direct repository hit |
| `generative model membership inference` | no direct repository hit |

arXiv API metadata queries:

| Query | Role |
| --- | --- |
| `all:"membership inference" AND all:diffusion` | Main diffusion MIA paper search. |
| `all:membership AND all:inference AND all:diffusion AND all:model` | Broader diffusion-model MIA search. |
| `all:memorization AND all:diffusion AND all:privacy` | Memorization/privacy adjacent search. |
| `all:"Stable Diffusion" AND all:"membership inference"` | Stable Diffusion specific search. |
| `ti:diffusion membership inference` | Recorded as a noisy query example; it returned non-diffusion/RAG and unrelated membership results. |

## Flow Summary

| Step | Count | Note |
| --- | ---: | --- |
| Fixed GitHub queries | 7 | Four returned no direct repo hits; three returned one direct visible repo each. |
| Fixed arXiv queries | 5 | Four useful all-field queries plus one noisy title-only query. |
| Machine-readable rows recorded | 17 | Includes direct hits, duplicate/covered lines, metadata-only rows, empty-result rows, and one query-noise row. |
| New code-public surface not already represented in v1 | 1 | `Divya1201/diffusion-privacy-attacks`; metadata/tree only. |
| Existing covered surfaces re-found | 2 | `ronketer/diffusion-membership-inference` and `fseclab-osaka/mia-diffusion`. |
| New admitted audit rows | 0 | No row-bound public target/split/score/response packet appeared. |
| New heavy work released | 0 | Stop rule held. |

## Included Surfaces

| ID | Surface | Result | Claim-support role |
| --- | --- | --- | --- |
| `fs20260526-github-01` | `ronketer/diffusion-membership-inference` | Existing DreamBooth forensics gate re-found. | Course-notebook / private-target example. |
| `fs20260526-github-02` | `fseclab-osaka/mia-diffusion` | Existing official-code-public gate re-found. | Code-public but no checkpoint-bound replay packet. |
| `fs20260526-github-03` | `Divya1201/diffusion-privacy-attacks` | New small code-public surface. | Code-public, but no target checkpoint, immutable split, response packet, score rows, ROC, metric JSON, or verifier output. |
| `fs20260526-arxiv-01` | `Membership Inference Attacks against Diffusion Models` | Duplicate of FSECLab paper line. | Fixed-search provenance for a covered code-public line. |
| `fs20260526-arxiv-02` to `fs20260526-arxiv-09` | arXiv paper metadata rows | Relevant paper metadata only. | Evidence that metadata discovery is easier than row-bound artifact discovery. |
| `fs20260526-arxiv-noise-01` | RAG membership result from title query | Query noise. | Records why title-only query strings were not enough. |

## Gate Summary

| Category | Rows | Boundary meaning |
| --- | ---: | --- |
| Existing gate re-found | 3 | Search process independently rediscovered surfaces already known to be non-admitted. |
| New metadata/code-public but no packet | 1 | One new repository has code but lacks audit-ready row binding. |
| Metadata-only relevant paper rows | 8 | Relevant enough for corpus context, insufficient for audit claims without artifact chasing. |
| Empty-result rows | 4 | Fixed GitHub queries can return no direct public repository surface. |
| Query-noise rows | 1 | Exact query strings can still produce semantically wrong results. |
| New admitted rows | 0 | No row can bypass `claim_register.md`. |

## What This Batch Supports

- Direction C can now cite an independent fixed-search batch rather than only
  existing DiffAudit history.
- Code availability, paper discoverability, metadata relevance, and audit-ready
  row binding remain distinct states.
- Negative search outcomes and noisy query results are part of the measurement
  method, not material to hide.
- The fixed-search table can seed a gate heatmap and corpus-flow diagram.

## What This Batch Does Not Support

- It does not show that most diffusion MIA papers lack artifacts.
- It does not show that original methods are wrong.
- It does not provide a new second asset for Direction B.
- It does not justify downloading LAION, CIFAR, CelebA, Stable Diffusion
  weights, generated images, or repository payloads.
- It does not promote Direction C to a standalone full paper by itself; it
  promotes Direction C from anecdotal starter corpus to a stronger
  claim-support section and a plausible reproducibility-paper plan.

## Next Gate

Before Direction C becomes a standalone LaTeX manuscript, run one
gate-label-consistency pass over `artifact_corpus_v1.csv` and
`artifact_corpus_fixed_search_20260526.csv`. The consistency pass should
record disagreements and resolutions, not create a new crawler or downloader.
