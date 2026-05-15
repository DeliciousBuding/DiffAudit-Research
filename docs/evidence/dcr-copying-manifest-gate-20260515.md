# DCR Copying Manifest Gate

> Date: 2026-05-15
> Status: copying/memorization semantic-shift watch-plus / code-and-caption-manifest-public / split-link-unavailable / no MIA score packet / no download / no GPU release / no admitted row

## Question

Does `somepago/DCR` / `Understanding and Mitigating Copying in Diffusion
Models` provide a usable DiffAudit target identity, split manifest, response, or
score packet?

This gate was opened after a non-duplicate external scout flagged DCR as the
strongest remaining official-repo candidate. The scope is deliberately
manifest-first: inspect public GitHub metadata, README, tree shape, small raw
snippets, and the LAION-10k Google Drive folder availability. No LAION image
payload, split archive, model checkpoint, generated image set, retrieval output,
or training asset was downloaded.

## Public Surface

| Field | Value |
| --- | --- |
| Repository | `https://github.com/somepago/DCR` |
| Repository description | Official PyTorch repo for the CVPR 2023 and NeurIPS 2023 diffusion replication/copying papers. |
| Main commit inspected | `bac8b5fbf739c75be6a187f97e2b81e0fd51115c` (`2023-11-22T20:54:04Z`) |
| README paper links | CVPR 2023 `Diffusion Art or Digital Forgery?` and arXiv `2305.20086` / `Understanding and Mitigating Copying in Diffusion Models` |
| Public tree evidence | `diff_train.py`, `diff_inference.py`, `diff_retrieval.py`, `sd_mitigation.py`, `datasets.py`, `embedding_search/*`, `metrics/*`, and `miscdata/laion_combined_captions.json` |
| Caption manifest | `miscdata/laion_combined_captions.json` is committed at `9,969,183` bytes and maps LAION-10k-style image paths to multiple captions. |
| README LAION split link | `https://drive.google.com/drive/folders/1TT1x1yT2B-mZNXuQPg7gqAhxN_fWCD__?usp=sharing` |
| Drive availability check | `curl -I -L` and PowerShell `Invoke-WebRequest` returned HTTP `404 Not Found` on 2026-05-15. |

## What Is Present

DCR has a real official code surface for diffusion replication/copying:

- fine-tuning scripts for Stable Diffusion with duplication and mitigation
  options;
- inference from a fine-tuned model;
- retrieval/similarity code that compares generated images against training
  images;
- committed LAION-style caption metadata;
- metric helpers for FID and precision/recall-style image evaluation;
- embedding-search utilities for similarity retrieval.

The `diff_retrieval.py` path computes similarity matrices, top matches,
histograms, FID-like summaries, and CLIP alignment metrics. Its default output
is local retrieval artifacts such as `similarity.pth` and `similarity_wtrain.pth`
under `ret_plots/...`, plus optional W&B logging; these outputs are not
committed as reusable paper score packets.

## What Is Missing

DCR does not satisfy the current DiffAudit per-sample MIA contract:

- the primary claim is copying/replication and mitigation, not member/nonmember
  inference over a protected target;
- no immutable public member/nonmember MIA split was found;
- the README LAION-10k Drive folder link currently returns HTTP `404`;
- no target checkpoints or model hashes are committed;
- no generated image response package is committed;
- no per-sample MIA score rows, ROC arrays, low-FPR metric JSON, or verifier
  outputs are committed;
- GitHub code searches for repository-local `member`, `score`, `ROC`, and
  `similarity.pth` result artifacts did not find a ready MIA packet.

The committed caption JSON improves provenance for a copying/privacy story, but
it does not bind rows to target-model membership labels or attack scores.

## Decision

`copying/memorization semantic-shift watch-plus / code-and-caption-manifest-public
/ split-link-unavailable / no MIA score packet / no download / no GPU release /
no admitted row`.

DCR is more concrete than a paper-only watch item because the official repo and
caption metadata are public. It is still not a DiffAudit execution lane because
it would require restoring or replacing the unavailable LAION split, acquiring
training images, fine-tuning or loading targets, generating images, and running
retrieval from scratch. That would answer a copying/replication question, not
the current per-sample membership-inference product contract.

Smallest valid reopen condition:

- a public, available LAION-10k split or equivalent manifest with immutable image
  identities and labels; plus
- public target checkpoints or generated response packets; plus
- committed per-sample similarity/MIA score rows, ROC arrays, metric JSON, or a
  ready verifier; or
- an explicit consumer-boundary decision opening a separate copying/memorization
  privacy lane outside admitted MIA rows.

Stop condition:

- Do not download LAION image payloads, Drive split folders, Stable Diffusion
  weights, generated image sets, or retrieval outputs for DCR in the current
  cycle.
- Do not fine-tune Stable Diffusion, run DCR inference, run retrieval, or launch
  GPU work from this gate.
- Do not promote DCR into Platform/Runtime admitted rows or MIA product copy.

## Platform and Runtime Impact

None. DCR remains a Research-only copying/memorization privacy watch-plus item.
Platform and Runtime should continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
