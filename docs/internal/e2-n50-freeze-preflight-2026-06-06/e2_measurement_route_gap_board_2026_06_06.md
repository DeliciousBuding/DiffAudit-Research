# E2 Measurement Route Gap Board

> Date: 2026-06-06
> Scope: next execution board for larger corpus + external audit +
> false-promotion baselines.

## 执行结论

当前路线不再追第二 response/score asset，也不释放 GPU/DCU。下一步是把
`E2-20260606-N50` 从 seed/candidate table 推进成真正可盲审的 public-surface
denominator。

这里的 denominator 指“可交给外部审稿人盲标的公开 artifact surface”，不是
“已 admitted row”。一个行可以在最终 allowed wording 中是 `blocked`、
`candidate-only` 或 `bounded-support`，只要它的公开来源、consumer question 和
first blocker 足够清楚，就能为 false-promotion measurement 提供科学价值。

## 当前缺口

- `0` rows are directly freezable into the external denominator.
- `E2Q-005` is usable only as a feature-packet review-row example, not N50
  evidence.
- `E2Q-004` CLiD, `E2Q-006` CopyMark, and `E2SCT-001` MT-MIA are closed for
  current-cycle second-asset work.
- The useful work is now public-source refresh + duplicate/semantic boundary +
  baseline false-promotion classification.

## Next No-Download Checks

| Priority | Row | Decision value | Current blocker | Smallest next check | Stop condition |
| --- | --- | --- | --- | --- | --- |
| 1 | `E2SCT-004` GenAI Confessions black-box | Best current black-box response-surface candidate; useful for testing whether data-public / metric-reported rules over-promote. | Generated outputs or DreamSim scores are not publicly row-bound. | Inspect GitHub plus Zenodo catalog/file listing only; ask whether generated outputs, DreamSim scores, target/service identity, labels, and row roles are visible before any archive download. | If only raw input images/captions or a large archive exists, keep as candidate-only false-promotion row. |
| 2 | `E2SCT-012` Shake-to-Leak | Runnable-code and fine-tuning leakage surface; good test for code-availability overpromotion. | Frozen checkpoint, private-set manifest, generated response packet, or score arrays are not visible. | Inspect public tree/README/release metadata for immutable target/split/score artifacts only. | If reproducing requires local SD/LAION/person-data generation, stop as code-public support. |
| 3 | `E2SCT-016` MIAHOLD HOLD++ | Mixed audio/CIFAR defense surface; useful for modality/defense boundary and checkpoint-score absence. | Checkpoint-bound membership scores or ROC rows are not visible. | Inspect split file names and public score/evaluation CSV absence; no audio/CIFAR/checkpoint download. | If evidence is only code/examples/checkpoints without row-bound scores, keep as mixed-modality defense support. |
| 4 | `E2SCT-021` ELSA Health Privacy Challenge | Benchmark/starter packet that can expose gated-data false promotion. | Real challenge targets are gated; public toy/starter assets may not be membership evidence. | Separate public toy examples from real gated challenge assets using repo metadata and docs. | If actual targets/labels/scores are gated, use only as benchmark-context false-promotion row. |
| 5 | `E2SCT-002` DMin | Artifact-rich data-attribution surface; tests attribution-vs-membership semantic overpromotion. | Data attribution is not member/nonmember inference. | Check whether any pointwise membership labels, scores, metrics, or consumer question exist in public metadata. | If only attribution/influence artifacts exist, classify as related-method blocked row. |
| 6 | `E2SCT-013` DCR copying manifest | Copying/memorization semantic-shift row; useful for boundary between copying and MIA claims. | Caption/copying artifacts are not pointwise membership scores. | Inspect public caption/metric surfaces for any true member/nonmember score or response packet. | If no membership labels/scores exist, keep as copying-context blocked row. |
| 7 | `E2SCT-009` Memorization Anisotropy | Prompt memorization row; useful for prompt-list / training-identity overpromotion. | Prompt splits are not bound to immutable train/member identity and row scores. | Inspect public prompt lists and score arrays only. | If prompt lists cannot be tied to training membership identity, keep as memorization-context support. |
| 8 | `E2SCT-014` CDI copyrighted data identification | Dataset-level identification boundary row; useful for dataset-level vs per-sample MIA wording. | Dataset-level CDI is not per-sample membership evidence. | Inspect feature/score output availability and whether the consumer question is dataset-level only. | If outputs are dataset-level or attack config only, classify as dataset-level boundary row, not MIA denominator evidence. |

## Completed Gap Checks

- `E2SCT-004` GenAI Confessions / STROLL:
  [`e2sct004_genai_confessions_public_surface_check_2026_06_06.md`](e2sct004_genai_confessions_public_surface_check_2026_06_06.md).
  Result: clean false-promotion exemplar candidate. STROLL exposes `100`
  paired `intraining` / `outoftraining` annotation rows, but no public
  row-bound generated outputs, DreamSim scores, metric JSON, or verifier were
  found. Do not admit the row, do not make it an external-audit denominator row,
  and do not release compute.
- `E2SCT-012` Shake-to-Leak:
  [`e2sct012_shake_to_leak_public_surface_check_2026_06_06.md`](e2sct012_shake_to_leak_public_surface_check_2026_06_06.md).
  Result: code-availability false-promotion exemplar. The public repo is
  runnable and mechanism-relevant, but its private set, checkpoints, responses,
  SecMI scores, extraction candidates, and metrics are runtime products. Do not
  admit the row, do not make it an external-audit denominator row, and do not
  release compute.
- `E2SCT-016` MIAHOLD/HOLD++:
  [`e2sct016_miahold_public_surface_check_2026_06_07.md`](e2sct016_miahold_public_surface_check_2026_06_07.md).
  Result: mixed-modality defense false-promotion exemplar. Public code, split
  hints, CIFAR HOLD configuration, and PIA-style metric code are visible, but
  checkpoint-bound scores, ROC arrays, metric JSON/CSV, generated responses,
  and a verifier are not public. Do not admit the row, do not make it an
  external-audit denominator row, and do not release compute.
- `E2SCT-021` ELSA Health Privacy:
  [`e2sct021_elsa_health_privacy_public_surface_check_2026_06_07.md`](e2sct021_elsa_health_privacy_public_surface_check_2026_06_07.md).
  Result: gated-benchmark false-promotion exemplar. The public starter package
  exposes MIA code, example labels/predictions, and a metric contract, but
  actual challenge targets, labels, predictions, Noisy Diffusion datasets,
  metadata, and participant artifacts are platform-gated or submission-bound.
  Do not admit the row, do not make it an external-audit denominator row, and
  do not release compute.
- `E2SCT-002` DMin:
  [`e2sct002_dmin_public_surface_check_2026_06_07.md`](e2sct002_dmin_public_surface_check_2026_06_07.md).
  Result: attribution-vs-membership false-promotion exemplar. The public repo,
  HF train/test dataset, LoRA weights, and cached gradient/influence artifacts
  are visible, but they support training-data attribution/influence inspection,
  not row-bound member/nonmember MIA scores, ROC arrays, metric JSON, or a
  verifier. Do not admit the row, do not make it an external-audit denominator
  row, and do not release compute.
- `E2SCT-005` DIFFENCE:
  [`e2sct005_diffence_public_surface_check_2026_06_07.md`](e2sct005_diffence_public_surface_check_2026_06_07.md).
  Result: classifier-defense consumer-boundary false-promotion exemplar.
  Official code, a Zenodo code snapshot, diffusion-purifier components,
  classifier-defense configs, and MIA scripts are visible, but the protected
  target is classifier membership privacy and results are runtime products
  after downloading external checkpoints. Do not admit the row, do not make it
  an external-audit denominator row, and do not release compute.
- `E2SCT-013` DCR:
  [`e2sct013_dcr_public_surface_check_2026_06_07.md`](e2sct013_dcr_public_surface_check_2026_06_07.md).
  Result: copying-vs-membership false-promotion exemplar. The public repo
  exposes copying/retrieval code, metric workflow, and caption-manifest
  metadata, but no member/nonmember MIA labels, row-bound membership scores,
  ROC arrays, metric JSON, or verifier. Do not admit the row, do not make it
  an external-audit denominator row, and do not release compute.
- `E2SCT-009` Memorization Anisotropy:
  [`e2sct009_memorization_anisotropy_public_surface_check_2026_06_07.md`](e2sct009_memorization_anisotropy_public_surface_check_2026_06_07.md).
  Result: prompt-memorization false-promotion exemplar. The public repo and
  OpenReview surface expose official code, prompt `mem` / `nmem` files, and a
  memorization metric, but no immutable image-row member/nonmember manifest,
  row-bound scores, metric JSON, ROC arrays, or verifier. Do not admit the row,
  do not make it an external-audit denominator row, and do not release compute.
- `E2SCT-014` CDI copyrighted data identification:
  [`e2sct014_cdi_public_surface_check_2026_06_07.md`](e2sct014_cdi_public_surface_check_2026_06_07.md).
  Result: dataset-level-vs-per-sample false-promotion exemplar. The public repo
  exposes CDI/MIA configs, feature extraction, score computation, and evaluation
  actions, but its consumer claim is dataset-level copyrighted-data
  identification and the feature/score packets are runtime products. Do not
  admit the row, do not make it an external-audit denominator row, and do not
  release compute.
- Twelve-row summary:
  [`e2_false_promotion_exemplar_summary_2026_06_07.md`](e2_false_promotion_exemplar_summary_2026_06_07.md).
  Result: compact false-promotion baseline object covering artifact-availability,
  code-availability, metric-code/split-visible, gated-starter overpromotion,
  attribution-vs-membership, classifier-defense consumer boundary,
  copying-vs-membership, prompt-memorization, dataset-level-vs-per-sample
  semantic boundaries, code-and-empty-asset-link overpromotion, and
  mock-demo-score and t2v-code-snapshot overpromotion.
  This is not `E2-20260606-N50`, not external adjudication evidence, and not a
  compute release.
- `E2SCT-011` VAE2Diffusion:
  [`e2sct011_vae2diffusion_public_surface_check_2026_06_07.md`](e2sct011_vae2diffusion_public_surface_check_2026_06_07.md).
  Result: code-and-empty-asset-link false-promotion exemplar. The public paper
  and repo expose latent-space MIA code, broad membership-improvement claims,
  split/checkpoint/cache commands, and an empty split/checkpoint download link,
  but no immutable split manifests, target checkpoint hashes, response/feature
  caches, per-sample scores, ROC arrays, metric JSON/CSV, or verifier. It
  expands the summary to `10` prepared false-promotion baseline rows. Do not
  admit the row, do not make it an external-audit denominator row, and do not
  release compute.
- `E2SCT-020` LSA-Probe:
  [`e2sct020_lsa_probe_public_surface_check_2026_06_07.md`](e2sct020_lsa_probe_public_surface_check_2026_06_07.md).
  Result: mock-demo-score false-promotion exemplar. The public paper, project
  repo, GitHub Pages demo, score-like JSON files, and demo generator look
  strong under weak rules, but the implementation is withheld and the score-like
  arrays are generated mock visualization data without target identities, exact
  audio splits, score provenance, metric packet, or verifier. It expands the
  summary to `11` prepared false-promotion baseline rows. Do not admit the row,
  do not make it an external-audit denominator row, and do not release compute.
- `E2SCT-019` VidLeaks T2V:
  [`e2sct019_vidleaks_t2v_public_surface_check_2026_06_07.md`](e2sct019_vidleaks_t2v_public_surface_check_2026_06_07.md).
  Result: t2v-code-snapshot false-promotion exemplar. The DOI-backed Zenodo
  record and code snapshot look strong under paper-link and code-availability
  rules, but the related GitHub tag is dead and no hashable T2V target, exact
  video membership split, generated-video packet, score/ROC/metric artifact, or
  verifier is public. It expands the summary to `12` prepared
  false-promotion baseline rows. Do not admit the row, do not make it an
  external-audit denominator row, and do not release compute.
- `E2SCT-022` Tabular Privacy Leakage TDM:
  [`e2sct022_tabular_privacy_leakage_tdm_public_surface_check_2026_06_07.md`](e2sct022_tabular_privacy_leakage_tdm_public_surface_check_2026_06_07.md).
  Result: support-only / tabular-lane watch-plus. The arXiv paper and official
  MIDST toolkit surface are useful false-promotion pressure, but the current
  public surface does not expose a paper-bound Berka/Diabetes replay packet,
  target identity, exact split manifests, score rows, ROC arrays, metric JSON,
  or no-training verifier. It does not expand C14 and is no longer a pending
  first-look queue row.
- `E2SCT-023` FERMI:
  [`e2sct023_fermi_public_surface_check_2026_06_07.md`](e2sct023_fermi_public_surface_check_2026_06_07.md).
  Result: paper-source-only / reported-metric support. The arXiv paper and HTML
  surface report tabular-diffusion MIA results, but no official public code,
  target/split packet, score rows, ROC arrays, metric JSON, or verifier were
  observed. It does not expand C14 and is no longer a pending first-look queue
  row.
- Post-C14 expansion queue:
  [`e2_false_promotion_expansion_queue_2026_06_07.md`](e2_false_promotion_expansion_queue_2026_06_07.md).
  Result: after closing `E2SCT-022` and `E2SCT-023` as support-only / watch-plus
  and adding `E2SCT-019` as a C14 false-promotion exemplar, the latest
  no-download metadata refresh leaves `0` next public-surface rows after
  excluding completed C14 exemplars and checked support-only rows. This does
  not create admitted or N50 evidence and does not release compute.
- `E2SCT-031` SAMA DLM:
  [`e2sct031_sama_dlm_public_surface_check_2026_06_09.md`](e2sct031_sama_dlm_public_surface_check_2026_06_09.md).
  Result: support-only DLM public-code artifact. The public repo fixes code
  commit `5ac7aa4a2e3765958e1b39a7774d72bbe4ee6dcd` and exposes attack/training
  code plus local configs, but no committed target model identity, immutable
  member/nonmember row manifest, ready score/response packet, ROC/metric
  artifact, provenance hashes, surface-delta control, or verifier. Do not admit
  the row, do not make it a C14/N50 or image-diffusion denominator row, and do
  not release compute.
- `E2SCT-032` MIA-EPT tabular:
  [`e2sct032_miaept_tabular_public_surface_check_2026_06_09.md`](e2sct032_miaept_tabular_public_surface_check_2026_06_09.md).
  Result: support-only tabular-diffusion public-result-page artifact. Main
  commit `6890ee833ad90b9fd8b3b3b06abd41613a4b316d` is code-only, while
  `gh-pages` commit `3fa8f0ee6e1f7401572aca869f9735b6af170dd0` exposes ROC
  images/PDFs and top-line metrics. No public row-bound score/prediction table,
  member/nonmember labels, immutable challenge row manifest, metric JSON/CSV,
  or verifier was found. Do not admit the row, do not make it a C14/N50 or
  image-diffusion denominator row, and do not release compute.
- `E2SCT-034` ReMIA tabular:
  [`e2sct034_remia_tabular_public_result_archive_check_2026_06_09.md`](e2sct034_remia_tabular_public_result_archive_check_2026_06_09.md).
  Result: support-only tabular synthetic-data aggregate-result archive. Main
  commit `84da2feee749b56639f8c8d9a6bbfffdbc0e87b3` is fixed for this check,
  and the public `experiments.tar.xz` archive contains `2,879` JSON files, no
  CSV files, and no row-scale score/label arrays. Do not admit the row, do not
  make it a C14/N50 or image-diffusion denominator row, and do not release
  compute.
- Broad multimodal/LLM sidecar search:
  Result: no current public primary-source artifact changes Direction A.
  `OpenLVLM-MIA` is the strongest future scout only if a separate VLM
  controlled-benchmark stratum opens; it has public labels/model surfaces but
  no row-bound attack-score/response metric packet in the current lane.
  `SimMIA/WikiMIA-25`, `FiMMIA`, `TS-RaMIA`, and the black-box
  generative-music MIA paper are support/watch surfaces only. Do not admit any
  row, do not make them C14/N50 or second-public-asset evidence, and do not
  release compute.

## Baseline Tags To Assign

For each checked row, assign only these tags before any external package:

- `score_only_would_promote`
- `code_availability_would_promote`
- `artifact_availability_would_promote`
- `paper_claim_artifact_link_would_promote`
- `metric_code_split_would_promote`
- `diffaudit_contract_blocks_or_bounds`

Do not add a new baseline unless it changes a reviewer-facing claim. The
current value is to measure false promotion against plausible weak rules, not
to invent a larger taxonomy.

## Stop Rule

Stop the gap-board work if a check only restates a known semantic mismatch or
requires large payload access. Negative rows are valuable only when they show a
specific false-promotion mechanism that an external reviewer can adjudicate
from public sources.

No new taxonomy, package-building, or external audit packet is allowed until at
least some rows become public-source-clear denominator candidates or clean
false-promotion exemplars.

The thirteen false-promotion exemplars now satisfy the condition for a next
bounded expansion pass only if a new queue row appears through a dedicated
row-level no-download public-surface check. The post-C14 expansion queue is not
itself a result.
