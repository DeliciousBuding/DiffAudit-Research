# Tracing the Roots Feature-Packet MIA Verdict

> Date: 2026-05-15
> Status: executable supplementary feature packet / positive MIA metric / provenance-limited / no GPU release / no admitted promotion

## Question

Does `Tracing the Roots: Leveraging Temporal Dynamics in Diffusion
Trajectories for Origin Attribution` provide a non-duplicate, immediately
executable diffusion membership packet after the CDI and StyleMI gates left no
active GPU candidate or CPU sidecar?

This is a bounded metric verdict. It only tests the released CIFAR10
supplementary diffusion-trajectory feature tensors. It does not download raw
CIFAR images, train or query a diffusion model, or reconstruct the paper's
larger experiments.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `Tracing the Roots: Leveraging Temporal Dynamics in Diffusion Trajectories for Origin Attribution` |
| Public source | `https://openreview.net/forum?id=mE74JKHTCE` |
| Supplement checked | `https://openreview.net/attachment?id=mE74JKHTCE&name=supplementary_material` |
| Downloaded supplement size | `45,499,156` bytes |
| Supplement SHA256 | `62e9ae3833bcc0f102612d05898262eea2b6025fe8949a72c3f055a8534c7b41` |
| Released code | `train.py`, `eval.py`, `utils.py` |
| Released data | `data/cifar10/{train,eval}/{member,external}.pt` |
| Claim semantics tested here | Binary member-vs-external MIA on precomputed diffusion trajectory features |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| OpenReview forum | The paper is public and exposes supplementary material. |
| Supplement central directory | The zip contains Python training/evaluation code and four CIFAR10 feature tensors: train/eval member and train/eval external. |
| `utils.py` | Defines feature layout as loss trajectory, image-gradient trajectory, and parameter-gradient trajectory, each across diffusion timesteps. It also defines MIA mode as `member` vs `external`. |
| `train.py` and `eval.py` | Provide a linear-classifier replay path for the feature tensors. Upstream `eval.py` requires `torchmetrics`, which is not in the local `diffaudit-research` environment, so DiffAudit replay used a local sklearn metric probe with the same binary feature contract. |

## Contract

- Data root: `tmp/tracing-roots-supp-20260515/data/cifar10` after extracting
  the OpenReview supplement.
- Train split: `train/member.pt` and `train/external.pt`.
- Eval split: `eval/member.pt` and `eval/external.pt`.
- Raw tensor shape per file: `1000 x 3000`.
- Selected feature shape per file: `1000 x 1002` using `start=0`,
  `end=1000`, `step=3`, and all three feature families.
- Positive class: `member`.
- Scorer: standardized linear classifier trained on train member/external
  tensors and evaluated on held-out eval member/external tensors.
- Device: local CUDA via `diffaudit-research`.
- Stop gate: one replay of the released `step=3` all-feature example shape;
  no timestep, feature-family, seed, classifier, or regularization matrix.

## Command

Run from `Research/` after downloading and extracting the OpenReview
supplement under `tmp/tracing-roots-supp-20260515`:

```powershell
conda run -n diffaudit-research python -X utf8 scripts\probe_tracing_roots_feature_packet.py `
  --data-root tmp\tracing-roots-supp-20260515\data\cifar10 `
  --output workspaces\gray-box\artifacts\tracing-roots-feature-packet-mia-20260515.json `
  --epochs 100 `
  --step 3 `
  --end 1000 `
  --device auto
```

## Result

Artifact:

`workspaces/gray-box/artifacts/tracing-roots-feature-packet-mia-20260515.json`

| Metric | Value |
| --- | ---: |
| Train samples | `2000` |
| Eval samples | `2000` |
| Selected features | `1002` |
| Final train accuracy | `0.776000` |
| Eval accuracy | `0.737500` |
| Eval AUC | `0.815826` |
| TPR@1%FPR | `0.134000` |
| TPR@0.1%FPR | `0.038000` |

The released feature packet gives a real, non-trivial held-out MIA signal. It
is materially stronger than the recent weak Fashion-MNIST, MIDST, Beans,
CommonCanvas, LAION-mi, StyleMI, and CDI immediate-execution outcomes.

## Gate Result

| Gate | Result |
| --- | --- |
| Target identity | Partial pass. The paper and supplement identify the CIFAR10 diffusion-trajectory feature setting, but the supplement does not include the raw target checkpoint identity or raw sample IDs needed to regenerate the features. |
| Exact member split | Pass at feature-packet level. `train/member.pt` and `eval/member.pt` are released with fixed counts and hashes. |
| Exact nonmember split | Pass at feature-packet level. `train/external.pt` and `eval/external.pt` are released with fixed counts and hashes. |
| Query/response or score coverage | Pass for feature-score execution, not for raw image query/response. The packet is sufficient for classifier replay and metric computation, but not for Platform-style black-box response evidence. |
| Metric contract | Pass. AUC, accuracy, TPR@1%FPR, and TPR@0.1%FPR are computed on a held-out eval feature split. |
| Mechanism delta | Pass. Full diffusion-trajectory loss and gradient features are distinct from recent raw denoising loss, score norm, score-Jacobian sensitivity, CLIP/pixel response similarity, response stability, and dataset-inference CDI gates. |
| Current DiffAudit fit | Positive-but-provenance-limited. This is a clean Research-side metric packet and a useful gray-box/white-box mechanism reference, but not an admitted product row. |
| GPU release | No. The replay is already a small feature-packet run; no model/data GPU job is released. |

## Decision

`executable supplementary feature packet / positive MIA metric /
provenance-limited / no GPU release / no admitted promotion`.

This candidate breaks the previous idle state more usefully than another
paper-only artifact gate: it ships runnable code plus a fixed `1000/1000`
member/external train split and a fixed `1000/1000` held-out eval split. The
one-shot replay obtains `AUC = 0.815826` and finite low-FPR recovery.

The limitation is equally important: the public supplement is a feature packet,
not a raw target/checkpoint/image/query-response bundle. DiffAudit should treat
it as Research-side evidence for a trajectory-feature mechanism and as a
candidate boundary note, not as an admitted Platform/Runtime row or a black-box
response-contract benchmark.

Do not expand this into timestep, feature-family, seed, classifier, optimizer,
or regularization sweeps. Reopen only if one of these appears:

- raw target checkpoint identity plus raw member/external sample manifests;
- a way to regenerate the trajectory features from public model/data assets;
- a consumer-boundary decision that explicitly allows feature-packet evidence
  to support a non-black-box Research claim.

## Platform and Runtime Impact

None. This is Research-only evidence. It does not add a Platform product row,
does not change Runtime schemas, and does not promote Tracing the Roots to the
admitted bundle.
