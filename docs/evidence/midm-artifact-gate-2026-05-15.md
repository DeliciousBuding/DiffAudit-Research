# MIDM Artifact Gate

> Date: 2026-05-15
> Status: split-and-metric-code-present / score-packet-missing / gated-or-inaccessible-checkpoint / no download / no GPU release

## Question

Can `HailongHuPri/MIDM` become the next clean Lane A execution asset for
DiffAudit, instead of another watch-only paper reference?

This is an artifact gate only. It inspects the public GitHub repository,
README, notebook, and scripts. No FFHQ image archive, Google Drive checkpoint,
HDF5 score packet, or model output was downloaded or executed.

## Candidate

| Field | Value |
| --- | --- |
| Repository | `https://github.com/HailongHuPri/MIDM` |
| Repo description | `Loss and Likelihood Based Membership Inference of Diffusion Models` |
| Paper | `Membership Inference of Diffusion Models` / arXiv `2301.09956` |
| Default branch inspected | `main` |
| Latest repo push observed | `2023-12-01T12:51:10Z` |
| License field | none exposed through GitHub repo metadata |
| Target family | FFHQ DDPM example from the repository README |
| Public checkpoint link | Google Drive file id `1b69vT1dWzseXIFSz--2n8dsd_Zxiipu2` |

The Google Drive page probe returned HTTP `401` in this environment, so the
checkpoint was not public-fetchable here and no file size/hash could be verified.

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| `README.md` | Describes FFHQ thumbnails128x128 preprocessing, `ffhq_1000.h5py` training images, `ffhq_1000_idx.npy` training indices, a DDPM checkpoint link, and loss/likelihood attack scripts. |
| `data_process.py` | Builds `ffhq_all.h5py`, `ffhq_1000.h5py`, `ffhq_1000_idx.npy`, and TFRecords from local FFHQ images; default `--num_images` is `1000`. |
| `attacking_diffusion_models/loss_attack.py` | Loads `ffhq_1000_idx.npy` as member indices, takes following indices as nonmembers, builds `1000/1000` labels, writes `loss_ffhq_1000_ddpm.h5py`, and computes TPR at fixed FPR. |
| `attacking_diffusion_models/likelihood_attack.py` | Mirrors the same member/nonmember loading path, writes `likelihood_ffhq_1000_ddpm.h5py`, and computes fixed-FPR TPR for likelihood scores. |
| `attacking_diffusion_models/compute_metrics.py` | Implements TPR at fixed FPR and ROC plotting helpers. |
| `attacking_diffusion_models/Example.ipynb` | Shows the intended `loss_attack.py` / `likelihood_attack.py` flow and labels as `np.zeros(1000)` plus `np.ones(1000)`, but contains no executed outputs or embedded metric values. |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Partial pass. The repo names an FFHQ DDPM example and a Google Drive checkpoint, but the checkpoint page returned `401` here and its hash/size/training recipe binding could not be verified. |
| Exact member split | Partial pass. The intended member identity is `ffhq_1000_idx.npy` from local preprocessing, but the actual index file is generated locally and not committed as a public artifact. |
| Exact nonmember split | Partial pass. Scripts define nonmembers as following indices from `ffhq_all.h5py`, but no public fixed nonmember manifest is released. |
| Query/response or score coverage | Fail. The repo does not ship `loss_ffhq_1000_ddpm.h5py`, `likelihood_ffhq_1000_ddpm.h5py`, ROC CSVs, metric JSON, or notebook outputs. |
| Metric contract | Pass as code. The scripts define low-FPR TPR metrics on `1000/1000` labels, which is stronger than many paper-only watch candidates. |
| Download justification | Fail for this cycle. The missing piece is not a small manifest; execution would require FFHQ thumbnails, a checkpoint that was not accessible here, and full score generation. |
| Current DiffAudit fit | Watch-plus. MIDM is a genuine image diffusion MIA method with better split/metric code than most watch items, but it is not a ready score packet. |
| GPU release | Fail. No bounded packet has public target hash, fixed member/nonmember manifests, ready scores, and stop condition. |

## Decision

`split-and-metric-code-present / score-packet-missing /
gated-or-inaccessible-checkpoint / no download / no GPU release`.

MIDM is worth retaining above generic related-method watch because it is
image-diffusion-specific, defines a `1000/1000` membership evaluation flow, and
has concrete loss/likelihood attack scripts. It still does not satisfy the
current Lane A execution gate because the public repo does not provide the fixed
member/nonmember manifests or ready score packet, and the advertised DDPM
checkpoint was not fetchable for metadata in this environment.

Smallest valid reopen condition:

- A public `ffhq_1000_idx.npy` plus nonmember manifest, or a hashable artifact
  that fixes the exact member/nonmember identities;
- A public DDPM checkpoint with verifiable size/hash and training binding; and
- A ready loss/likelihood HDF5 score packet, ROC CSV, metric JSON, or a bounded
  command that can generate one without acquiring FFHQ from scratch.

Stop condition:

- Do not download FFHQ thumbnails, request or scrape checkpoint access, train
  DDPM, or run loss/likelihood scoring from scratch in the current roadmap
  cycle.
- Do not convert MIDM into Platform/Runtime rows, recommendation logic, or
  admitted evidence.

## Reflection

This cycle tested a stronger image-diffusion candidate surfaced by independent
search. It found a real metric contract but no executable artifact packet, so
the decision does not change: `active_gpu_question = none`,
`next_gpu_candidate = none`, and `CPU sidecar = none selected`.

## Platform and Runtime Impact

None. This is Research-only intake evidence. Platform and Runtime should
continue consuming only the admitted `recon / PIA baseline / PIA defended / GSA
/ DPDM W-1` set.
