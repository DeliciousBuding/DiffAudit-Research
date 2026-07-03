# IAR Privacy Attacks Artifact Gate

> Date: 2026-05-23
> Status: image-autoregressive privacy watch-plus / official code-public / no committed score packet / large ImageNet and model assets required / no download / no GPU release / no admitted row

## Question

Does arXiv `2502.02514` / `Privacy Attacks on Image AutoRegressive Models`
expose a public DiffAudit-ready target, split, score packet, or verifier that
should change the active Research slots?

This was selected as a single Lane A metadata gate because it is recent
image-generation privacy work with explicit membership inference, dataset
inference, and extraction claims. The check used arXiv API metadata, the
official GitHub repository metadata/tree, and the official README. It did not
clone the repository, download ImageNet, download upstream model repositories,
download model weights, generate samples, or run MIA/DI/extraction scripts.

## Public Surface

| Field | Value |
| --- | --- |
| Paper line | `Privacy Attacks on Image AutoRegressive Models` |
| arXiv | `https://arxiv.org/abs/2502.02514v5` |
| Published / updated | `2025-02-04T17:33:08Z` / `2026-04-09T17:05:17Z` |
| Venue note | `Accepted at ICML2025` |
| Official code | `https://github.com/sprintml/privacy_attacks_against_iars` |
| Repository state | default branch `main`, size `1,134` KB, created `2025-02-03T10:00:25Z`, updated `2026-03-20T18:40:46Z`, pushed `2026-02-09T10:50:08Z`, no license, no releases observed |
| Scope | image autoregressive models, not current diffusion/latent-image target family |

The official repository exposes real attack code and configs, including:

```text
README.md
environment.yaml
main.py
analysis/mia_performance.py
analysis/di.py
analysis/distance_score.py
analysis/plot_memorization.py
conf/attack/llm_mia_cfg.yaml
conf/attack/llm_mia_loss.yaml
conf/attack/mem_info.yaml
conf/attack/gen_memorized.yaml
conf/attack/find_memorized.yaml
conf/model/var_16.yaml
conf/model/var_20.yaml
conf/model/var_24.yaml
conf/model/var_30.yaml
conf/model/rar_b.yaml
conf/model/rar_l.yaml
conf/model/rar_xl.yaml
conf/model/rar_xxl.yaml
conf/model/mar_b.yaml
conf/model/mar_l.yaml
conf/model/mar_h.yaml
src/attacks/llm_mia.py
src/attacks/llm_mia_loss.py
src/attacks/mem_info.py
src/attacks/gen_memorized.py
src/attacks/find_memorized.py
src/models/VAR.py
src/models/RAR.py
src/models/MAR.py
```

The README execution path requires local setup and runtime artifact generation:
clone `FoundationVision/VAR`, `LTH14/mar`, and `bytedance/1d-tokenizer`;
download ImageNet LSVRC 2012 train and validation splits; allow scripts to
download models; run membership inference separately on `train` and `val`; run
`analysis/mia_performance.py` to create local plots; run `analysis/di.py` to
create `analysis/plots/di/di_results.csv`; and run distributed extraction
commands with `n_samples_eval=140000` across GPU shards before generating
local `{model}_memorized_train.csv` files.

No committed result packet was visible in the checked public tree: no frozen
ImageNet member/nonmember row manifest, no model-weight hashes, no generated
sample packet, no per-row MIA scores, no ROC arrays, no metric JSON, no
committed `di_results.csv`, no committed memorization CSV, and no no-training
verifier output.

## Claim Boundary

The paper is scientifically relevant privacy evidence. The arXiv abstract
reports a new IAR MIA with `TPR@FPR=1% = 94.57%` for IARs versus `6.38%` for
comparable diffusion-model attacks, dataset inference with as few as `4`
samples versus `200` for diffusion models, and extraction of `698` training
samples from `VAR-d30`.

The boundary is still not a current DiffAudit execution lane. The target
family is image autoregressive generation, while the active product and
research consumer contract is diffusion / latent-image membership evidence.
The public repository is code-public, but it is not a bounded replay artifact:
the score, ROC, metric, and extraction outputs are generated locally after
large data/model setup.

## Gate Result

| Gate | Result |
| --- | --- |
| Current image/latent-image fit | Partial. The task is image-generation privacy, but the target models are autoregressive, not diffusion or latent-image diffusion. |
| Target identity | Fail for replay. Model config names are public, but no paper-bound model hashes or frozen downloaded weight manifest is committed. |
| Exact member split | Fail. The README uses ImageNet train, but no immutable row IDs or compact member manifest is committed. |
| Exact nonmember split | Fail. The README uses ImageNet validation, but no immutable nonmember manifest is committed. |
| Query/response or score coverage | Fail. MIA, DI, and memorization outputs are generated locally; no per-row score, ROC, metric JSON, DI CSV, or memorization CSV packet is committed. |
| Mechanism delta | Pass as watch-plus. IAR privacy is a non-duplicate image-generation privacy direction and the claims are strong enough to monitor. |
| Download justification | Fail. Running the code would require ImageNet, upstream model repos, model downloads, and distributed GPU extraction without a committed replay target. |
| GPU release | Fail. The blocker is missing replay artifacts and a target-family boundary, not local compute. |

## Decision

`image-autoregressive privacy watch-plus / official code-public / no committed
score packet / large ImageNet and model assets required / no download / no GPU
release / no admitted row`.

Keep IAR Privacy Attacks as Research-only watch-plus evidence. It is useful for
framing privacy risk beyond diffusion models, but it does not reopen the
current Lane A diffusion asset path and does not justify ImageNet/model
downloads, upstream repo cloning, MIA/DI execution, extraction generation, or
GPU release.

Current slots become `active_gpu_question = none`, `next_gpu_candidate = none`,
and `CPU sidecar = none selected after IAR privacy artifact gate`.

Smallest valid reopen condition:

- authors publish compact public score/ROC/metric packets, immutable ImageNet
  row manifests, model hashes, generated sample packets, and a no-training
  verifier; or
- DiffAudit explicitly opens an image-autoregressive consumer boundary separate
  from diffusion/latent-image admitted rows.

Stop condition:

- Do not download ImageNet train/validation, VAR/RAR/MAR weights, generated
  samples, memorization candidates, or extraction outputs from this gate.
- Do not clone `FoundationVision/VAR`, `LTH14/mar`, `bytedance/1d-tokenizer`,
  or the full IAR repository for execution from this gate.
- Do not run `main.py`, `analysis/mia_performance.py`, `analysis/di.py`,
  `mem_info`, `gen_memorized`, `find_memorized`, or distributed GPU extraction
  from this gate.
- Do not add Platform/Runtime rows, schemas, product copy, or recommendation
  logic until a reviewed IAR consumer boundary or row-bound replay artifacts
  exist.

## Platform and Runtime Impact

None. Platform and Runtime continue consuming only the admitted `recon / PIA
baseline / PIA defended / GSA / DPDM W-1` set.
