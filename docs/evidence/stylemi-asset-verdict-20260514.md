# StyleMI Asset Verdict

> Date: 2026-05-14
> Status: paper-only / style-mimicry-relevant / artifact-incomplete / no code / no download / no GPU release

## Question

Does `StyleMI: An Image Processing-Based Method for Detecting Unauthorized
Style Mimicry in Fine-Tuned Diffusion Models in a More Realistic Scenario`
provide a clean non-duplicate Lane A asset for DiffAudit: target model identity,
exact member/nonmember split, query/response or score coverage, provenance, and
a bounded scoring contract?

This is an asset gate, not a reproduction attempt. No model, artwork dataset,
artist corpus, generated image, or paper artifact was downloaded.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `StyleMI: An Image Processing-Based Method for Detecting Unauthorized Style Mimicry in Fine-Tuned Diffusion Models in a More Realistic Scenario` |
| DOI | `10.1109/access.2025.3574053` |
| Venue | `IEEE Access`, volume `13`, pages `97364-97375` |
| Publication year | `2025` |
| Crossref title check | Matches the StyleMI paper title |
| Domain | Style-mimicry detection for fine-tuned diffusion models; related to membership/style ownership but not a released DiffAudit response contract |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| Crossref DOI metadata | Confirms the paper title, DOI, venue, volume, pages, and 2025 publication metadata. |
| Web search for code/artifacts | Searches for the exact paper title, DOI, `StyleMI`, GitHub, code, and dataset did not find a public code repository or artifact package. |
| Local Research duplicate check | No existing Research evidence or workspace entry for `StyleMI`, `3574053`, or the style-mimicry title was found. |
| GitHub repository search | `gh search repos "StyleMI diffusion"` returned no matching public repository. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail. Public metadata identifies the paper topic, but no hashable fine-tuned diffusion checkpoint, endpoint contract, or deterministic target recreation package was found. |
| Exact member split | Fail. No per-artist or per-image style training membership manifest was found. |
| Exact nonmember split | Fail. No held-out artist/image manifest or negative split package was found. |
| Query/response or score coverage | Fail. No generated image responses, image-processing feature packets, score CSV/JSON, or reusable attack outputs were found. |
| Scoring contract | Fail for execution. The title indicates an image-processing method, but the public surface found in this gate does not expose runnable code or a frozen metric command. |
| Mechanism delta | Pass as watch. Style-mimicry membership/ownership detection is distinct from CommonCanvas pixel/CLIP distance, Fashion-MNIST denoising losses, MIDST tabular scoring, and T2V/DLM related-method lines. |
| GPU release | Fail. There is no target, split, response/score packet, command, or stop gate. |

## Decision

`paper-only / style-mimicry-relevant / artifact-incomplete / no code / no
download / no GPU release`.

StyleMI is worth retaining as a related style-mimicry watch item, but it is not
a clean current DiffAudit Lane A asset. The public surface found in this gate is
paper metadata, not an executable artifact package.

Do not train style LoRAs, scrape artist images, reconstruct artist datasets, or
invent style/member splits from the paper title. Reopen only if public-safe
artifacts appear with:

- a hashable fine-tuned diffusion target or deterministic target recreation
  recipe,
- exact per-image or per-artist member and nonmember manifests,
- generated images, image-processing features, or score packets,
- and a bounded `25/25` or `50/50` first packet with an explicit low-FPR stop
  gate.

## Platform and Runtime Impact

None. This is Research-only watch evidence. It is not admitted evidence, not a
Platform product row, and not a Runtime schema input.
