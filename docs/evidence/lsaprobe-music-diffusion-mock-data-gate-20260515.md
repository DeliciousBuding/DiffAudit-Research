# LSA-Probe Music Diffusion Mock Data Gate

> Date: 2026-05-15
> Status: music/audio cross-modal watch-plus / paper-and-demo-public / demo score data is generated mock data / no score artifact / no model-dataset download / no GPU release

## Question

Does arXiv `2602.01645` / `Membership Inference Attack Against Music
Diffusion Models via Generative Manifold Perturbation` provide a clean Lane A
asset, reusable member/nonmember score packet, or bounded replay target after
the admitted consumer drift audit left `active_gpu_question = none`?

This is an artifact gate, not a reproduction attempt. Only public arXiv source,
GitHub metadata, and small GitHub Pages demo files were inspected. No MAESTRO,
FMA, DiffWave, MusicLDM, checkpoint, or audio payload was downloaded.

## Candidate

| Field | Value |
| --- | --- |
| Paper line | `Membership Inference Attack Against Music Diffusion Models via Generative Manifold Perturbation` |
| arXiv | `https://arxiv.org/abs/2602.01645` |
| arXiv source checked | `https://arxiv.org/e-print/2602.01645` |
| arXiv source size | `1,404,510` bytes |
| arXiv source SHA256 | `6a9d8db89b8a3ae65ee36088d9b3a510b83f3421adee945d5045d56c6d4e2676` |
| arXiv source contents | TeX, bibliography/style files, `ROC.png`, `budget_ablation_swapped.png`, `metric_robustness_swapped_colors.png`, `timestep_ablation_swapped.png`, and `1.jpg` |
| Project repo | `https://github.com/kaslim/LSA-Probe` |
| Project repo commit checked | `594900158e31b5c5b801d3d534dcc44deb8ade7c` |
| Project repo public surface | One `README.md` blob, no releases, no implementation tree |
| Demo page | `https://kaslim.github.io/lsa-probe/` |
| Demo source repo | `https://github.com/kaslim/kaslim.github.io` |
| Demo source commit checked | `a082e61c5a7819486fd031be433f534cf81aa2de` |
| Demo data generator blob | `lsa-probe/generate_demo_data.py`, blob `f84b8bd5a8c50c1e769044e76f41655d51c766dc`, `8,904` bytes |
| Domain | Music/audio diffusion membership inference, not the current image/latent-image DiffAudit execution scope |

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| arXiv source TeX | Defines the `Latent Stability Adversarial Probe` / generative manifold perturbation method, a developer-side white-box attack using latent perturbation stability and perceptual audio distances. It names DiffWave and MusicLDM with MAESTRO v3 and FMA-Large experiments, but ships no Python code, configs, target checkpoints, exact split manifests, score arrays, ROC CSVs, metric JSON, or replay command. |
| Project repo `kaslim/LSA-Probe` | The public tree has only `README.md`. The README marks the work under peer review and says the full implementation and reproducibility instructions will be released upon paper acceptance. No source code, split files, checkpoints, release assets, score rows, or verifier files are present. |
| Demo page HTML | The resources section links code to `kaslim/LSA-Probe`, while the paper and data buttons are `#` placeholders. The page loads `data/adversarial_costs.json`, `data/roc_curves.json`, `data/budget_ablation.json`, `data/metric_comparison.json`, `data/baselines.json`, and `data/main_results.json` from GitHub Pages. |
| GitHub Pages tree | The demo files live in `kaslim/kaslim.github.io`, not the project repo. The `lsa-probe/data/*.json` files are small static web-demo assets, and the same tree includes `generate_demo_data.py`. |
| `generate_demo_data.py` | The script explicitly generates mock data for the interactive demo, sets `np.random.seed(42)`, samples `500` member and `500` nonmember adversarial costs per timestep from gamma distributions, computes demo ROC curves, and hardcodes / simulates budget, metric, baseline, and main-result tables. |
| `data/adversarial_costs.json` | `112,839` bytes, SHA256 `de78ba442f1e0bdaf857c4294e600a177b2121a0bfec0273f2717a518e93ed86`; contains `500 / 500` member/nonmember values for each timestep `0.2`, `0.4`, `0.6`, and `0.8`, but no sample IDs, audio IDs, checkpoint binding, dataset split, model pair, or provenance beyond the mock generator. |
| `data/roc_curves.json` | `13,074` bytes, SHA256 `4cb13908d9dd10698b2e54032310ab5e48f85ff508788733c28359bf163f7929`; contains downsampled demo ROC arrays. The `t_ratio = 0.6` demo AUC is `0.881244`, which is a generated web-demo value and must not be treated as paper experiment evidence. |
| Other demo JSON files | `budget_ablation.json`, `metric_comparison.json`, `baselines.json`, and `main_results.json` are small visualization tables generated or hardcoded by the demo script. They are not raw experiment logs or checkpoint-bound score packets. |

Demo data file metadata:

| File | Size bytes | SHA256 |
| --- | ---: | --- |
| `data/adversarial_costs.json` | `112,839` | `de78ba442f1e0bdaf857c4294e600a177b2121a0bfec0273f2717a518e93ed86` |
| `data/roc_curves.json` | `13,074` | `4cb13908d9dd10698b2e54032310ab5e48f85ff508788733c28359bf163f7929` |
| `data/budget_ablation.json` | `801` | `701122d180ed13773d59baca8d570d3180d04d060c4f1b0ec786bc0abe52ce47` |
| `data/metric_comparison.json` | `431` | `da6c312e3fea533f167234a876a0fc6d6f0d5643d0c8a106dd6b659bc4cb7f0e` |
| `data/baselines.json` | `518` | `b532ca9b6b30f0a74b05383198c8884248575595e149e6c92c2316b37f897481` |
| `data/main_results.json` | `1,089` | `11c7bb51c9aae2983aa9dedfbe447fbf83b0a63eabe8d47d4b1cbadd83e61820` |

## Gate Result

| Gate | Result |
| --- | --- |
| Target model identity | Fail for execution. The paper names DiffWave and MusicLDM, but the public surface ships no target checkpoint hashes, model folders, training logs, or deterministic recreation recipe. |
| Exact member split | Fail. The paper describes training clips / member pools, but no per-audio member manifest, clip IDs, dataset rows, or immutable sample identities are released. |
| Exact nonmember split | Fail. Held-out validation/test and near/cross-domain controls are described, but no nonmember manifest or sample IDs are released. |
| Query/response or score coverage | Fail. The only public score-like values are GitHub Pages mock demo arrays generated by `generate_demo_data.py`; they are not checkpoint-bound adversarial costs or paper score exports. |
| Metric contract | Paper/demo only. The method reports AUC and fixed-FPR TPR-style metrics, but no raw metric packet can be replayed or audited. |
| Mechanism delta | Watch-worthy. Latent-stability adversarial probing over music diffusion models is distinct from current image response-distance, denoising-loss, SimA score-norm, Tracing Roots feature-packet, tabular, graph, TTS duration-loss, and prompt-memorization lines. |
| Current DiffAudit fit | Cross-modal watch-plus only. It is relevant scientifically, but audio/music diffusion is outside the current image/latent-image execution path and lacks reusable public artifacts. |
| GPU release | Fail. Running this would require acquiring music datasets, model checkpoints, and unpublished implementation details. No bounded CPU or GPU sidecar is released. |

## Decision

`music/audio cross-modal watch-plus / paper-and-demo-public / demo score data is
generated mock data / no score artifact / no model-dataset download / no GPU
release`.

LSA-Probe is a useful mechanism watch item because it targets membership
inference for music diffusion models with a non-duplicate latent stability
observable. It is not a current DiffAudit execution lane. The public project
repo intentionally withholds implementation and reproducibility instructions,
and the visible `500 / 500` member/nonmember arrays on the demo site are mock
visualization data generated from seeded random distributions.

Stop condition:

- Do not download MAESTRO, FMA-Large, DiffWave, MusicLDM, audio clips, or model
  checkpoints for this line inside the current image/latent-image roadmap
  cycle.
- Do not treat GitHub Pages `data/*.json` as paper evidence, a score packet, or
  a reusable ROC artifact.
- Do not implement LSA-Probe from the TeX or demo description, run white-box
  audio attacks, launch GPU jobs, or add Runtime/Platform music-audio support
  claims.
- Reopen only if the authors publish implementation plus public-safe target
  model identities, exact member/nonmember manifests, and real adversarial-cost
  score/ROC/metric artifacts, or if DiffAudit explicitly opens a music/audio
  membership lane with a consumer-boundary decision first.

## Reflection

This was the shortest useful Lane A check: it found an apparently promising
music-diffusion candidate, then resolved the only public score-like files as
mock demo data rather than experiment evidence. The correct state is
cross-modal watch-plus with `active_gpu_question = none`,
`next_gpu_candidate = none`, and `CPU sidecar = none selected after LSA-Probe
music diffusion mock-data gate`.

## Platform and Runtime Impact

None. This is Research-only intake evidence. Platform and Runtime should
continue consuming only the admitted `recon / PIA baseline / PIA defended / GSA
/ DPDM W-1` set.
