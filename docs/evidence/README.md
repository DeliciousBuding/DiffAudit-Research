# Evidence

This directory contains the public evidence overview.

| Document | Purpose |
| --- | --- |
| [reproduction-status.md](reproduction-status.md) | Per-track reproduction status stages. |
| [admitted-results-summary.md](admitted-results-summary.md) | Reviewed verified results summary. |
| [innovation-evidence-map.md](innovation-evidence-map.md) | Mapping from research claims to evidence status. |
| [cross-box-boundary-status.md](cross-box-boundary-status.md) | Current cross-box candidate boundary and next research question. |
| [deb-medical-diffusion-artifact-gate-20260515.md](deb-medical-diffusion-artifact-gate-20260515.md) | DEB medical diffusion artifact gate; paper-source-only grey-box discrete-codebook / intermediate-trajectory MIA mechanism watch with no code, target/split/score/ROC/metric artifacts, verifier, download, GPU release, or admitted row. |
| [daily-research-review-20260515.md](daily-research-review-20260515.md) | Progress review after DSiRe / LoRA-WiSE and CPSample gates; confirms no active GPU, no CPU sidecar, no Platform/Runtime drift, and clean next-gate selection rules. |
| [cpsample-defense-artifact-gate-20260515.md](cpsample-defense-artifact-gate-20260515.md) | CPSample defense artifact gate; ICLR OpenReview supplement ships diffusion/classifier code and small attack-loss text fragments, but no checkpoint-bound row/metric/verifier artifacts, so no download, GPU release, or admitted row. |
| [dsire-lora-wise-dataset-size-boundary-20260515.md](dsire-lora-wise-dataset-size-boundary-20260515.md) | DSiRe / LoRA-WiSE dataset-size boundary gate; official code and public LoRA weight benchmark are strong future weight-only privacy evidence, but the claim is aggregate dataset-size recovery, not per-sample MIA, so no download, GPU release, or admitted row. |
| [hyperfree-secmi-reproduction-gate-20260515.md](hyperfree-secmi-reproduction-gate-20260515.md) | Hyperparameter-free SecMI reproduction gate; third-party SecMI-family code/report surface with claimed CIFAR-100 metrics, but no reusable score rows, ROC arrays, metric JSON, verifier, download, GPU release, or admitted row. |
| [dme-dual-model-entropy-artifact-gate-20260515.md](dme-dual-model-entropy-artifact-gate-20260515.md) | DME dual-model entropy gate; official complexity-bias diffusion-MIA repo is README-only with no code, paper link, split/checkpoint/score/ROC/metric artifacts, verifier, download, GPU release, or admitted row. |
| [fremia-frequency-filter-artifact-gate-20260515.md](fremia-frequency-filter-artifact-gate-20260515.md) | FreMIA frequency-filter gate; ICML 2026 direct diffusion MIA with paper tables/figures and a stub official repo, but no code, split/checkpoint/score/ROC/metric artifacts, verifier, download, GPU release, or admitted row. |
| [copymark-official-score-artifact-gate-20260515.md](copymark-official-score-artifact-gate-20260515.md) | Official CopyMark score-artifact gate; member/nonmember logs, aggregate ROC/threshold JSONs, selected score tensors, and laion_ridar/mixing results are public, but no compact row-ID-bound score manifest, checkpoint hash, small immutable data packet, ready verifier, download, GPU release, or admitted row. |
| [cross-box-successor-scope-20260512.md](cross-box-successor-scope-20260512.md) | CPU-only successor scoping that closes cross-box as hold until a new observable or second response-contract package exists. |
| [black-box-response-strength-preflight.md](black-box-response-strength-preflight.md) | H2 response-strength candidate status and latest validation verdict. |
| [h2-lowpass-followup-contract.md](h2-lowpass-followup-contract.md) | Frozen CPU contract for deciding whether H2 lowpass deserves another bounded GPU packet. |
| [midfreq-same-noise-residual-preflight-20260512.md](midfreq-same-noise-residual-preflight-20260512.md) | CPU-only cache audit for the distinct mid-frequency same-noise residual observable; blocks GPU until a residual cache exists. |
| [midfreq-residual-scorer-contract-20260512.md](midfreq-residual-scorer-contract-20260512.md) | CPU scorer contract for band-pass same-noise residual scoring. |
| [midfreq-residual-collector-contract-20260512.md](midfreq-residual-collector-contract-20260512.md) | CPU-compatible collector function contract for matched `x_t` / `tilde_x_t` residual states. |
| [midfreq-residual-tiny-runner-contract-20260512.md](midfreq-residual-tiny-runner-contract-20260512.md) | CPU-only synthetic tiny runner contract proving the residual cache schema. |
| [midfreq-residual-real-asset-preflight-20260512.md](midfreq-residual-real-asset-preflight-20260512.md) | CPU-only real-asset `4/4` preflight proving the residual cache schema works with the collaborator 750k checkpoint and CIFAR10 split; no GPU release. |
| [midfreq-residual-signcheck-20260512.md](midfreq-residual-signcheck-20260512.md) | Frozen `64/64` GPU sign-check for the same-noise residual observable; candidate-only, not admitted evidence. |
| [midfreq-residual-stability-decision-20260512.md](midfreq-residual-stability-decision-20260512.md) | CPU-only decision releasing exactly one seed-stability packet for the candidate residual line. |
| [midfreq-residual-stability-result-20260512.md](midfreq-residual-stability-result-20260512.md) | Seed-only stability result for the residual line; candidate-stable-but-bounded, no admitted promotion. |
| [midfreq-residual-comparator-audit-20260512.md](midfreq-residual-comparator-audit-20260512.md) | CPU-only comparator audit showing the current residual signal is not proven mid-frequency-specific. |
| [post-midfreq-next-lane-reselection-20260512.md](post-midfreq-next-lane-reselection-20260512.md) | CPU-only reselection after residual comparator audit; selects SecMI consumer-contract review. |
| [secmi-consumer-contract-review-20260512.md](secmi-consumer-contract-review-20260512.md) | CPU-only review keeping SecMI as structural supporting evidence, not a system-consumable row. |
| [tmia-dm-temporal-artifact-gate-20260515.md](tmia-dm-temporal-artifact-gate-20260515.md) | Fresh public-surface recheck for the known TMIA-DM temporal-noise / noise-gradient mechanism; CRAD paper/PDF only, no official code, checkpoint-bound scores, immutable splits, ROC/metric artifacts, or verifier output. |
| [quantile-diffusion-mia-secmia-terror-replay-20260515.md](quantile-diffusion-mia-secmia-terror-replay-20260515.md) | Third-party SecMI-style `t_error` score-packet replay from `neilkale/quantile-diffusion-mia`; support-only, not official Quantile Regression output or an admitted row. |
| [dualmd-distillmd-defense-artifact-gate-20260515.md](dualmd-distillmd-defense-artifact-gate-20260515.md) | OpenReview DDMD supplement-code gate; code and DDPM split-index files are public, but checkpoint-bound score/ROC/metric artifacts are missing, so no download, GPU release, or admitted row. |
| [diffence-classifier-defense-artifact-gate-20260515.md](diffence-classifier-defense-artifact-gate-20260515.md) | Official DIFFENCE classifier-defense code gate; split-index files are public, but diffusion is a pre-inference defense component and checkpoint-bound score artifacts are missing, so no download, GPU release, or admitted row. |
| [miahold-higher-order-langevin-artifact-gate-20260515.md](miahold-higher-order-langevin-artifact-gate-20260515.md) | Official MIAHOLD/HOLD++ defense-code gate; split and attack code are public, but checkpoint-bound score artifacts are missing, so no download, GPU release, or admitted row. |
| [shake-to-leak-code-artifact-gate-20260515.md](shake-to-leak-code-artifact-gate-20260515.md) | Official Shake-to-Leak code gate; fine-tuning-amplified generative privacy code is public, but target checkpoints, immutable member/nonmember manifests, generated private sets, score/ROC/metric artifacts, and ready verifier output are missing, so no download, GPU release, or admitted row. |
| [fseclab-mia-diffusion-code-artifact-gate-20260515.md](fseclab-mia-diffusion-code-artifact-gate-20260515.md) | Official FSECLab DDIM/DCGAN diffusion-MIA code gate; attack/evaluation code and FID stats are public, but checkpoint-bound score/ROC/metric artifacts and immutable split manifests are missing, so no download, GPU release, or admitted row. |
| [mtmia-relational-diffusion-score-packet-gate-20260515.md](mtmia-relational-diffusion-score-packet-gate-20260515.md) | MT-MIA relational tabular diffusion gate; official ClavaDDPM/RelDiff split, synthetic-output, and score/metric packets are public, but remain cross-modal support-only with no dataset/model download, GPU release, or admitted row. |
| [lsaprobe-music-diffusion-mock-data-gate-20260515.md](lsaprobe-music-diffusion-mock-data-gate-20260515.md) | LSA-Probe music/audio diffusion gate; paper and demo are public, but the visible `data/*.json` score-like files are mock demo data generated from seeded random distributions, so no dataset/checkpoint download, GPU release, or admitted row. |
| [h2-cross-asset-contract-preflight.md](h2-cross-asset-contract-preflight.md) | CPU-only portability check for H2 beyond DDPM/CIFAR10. |
| [h2-image-to-image-contract.md](h2-image-to-image-contract.md) | CPU contract that reopens H2 portability only under image-to-image response observation. |
| [h2-img2img-micro-result.md](h2-img2img-micro-result.md) | First frozen SD/CelebA image-to-image H2 micro-packet verdict. |
| [h2-img2img-simple-distance-review.md](h2-img2img-simple-distance-review.md) | CPU review of the simple high-strength image-to-image response-distance signal. |
| [h2-img2img-simple-distance-stability-contract.md](h2-img2img-simple-distance-stability-contract.md) | Frozen non-overlapping stability contract for the simple image-to-image distance signal. |
| [h2-img2img-simple-distance-stability-result.md](h2-img2img-simple-distance-stability-result.md) | Non-overlapping stability result for the simple image-to-image distance signal. |
| [h2-img2img-simple-distance-admission-contract.md](h2-img2img-simple-distance-admission-contract.md) | Frozen 25/25 admission-scale contract for the simple image-to-image distance signal. |
| [h2-img2img-simple-distance-admission-result.md](h2-img2img-simple-distance-admission-result.md) | Admission-scale result for the simple image-to-image distance signal. |
| [h2-simple-distance-portability-preflight.md](h2-simple-distance-portability-preflight.md) | CPU-only preflight for second-asset simple-distance portability. |
| [black-box-next-lane-selection.md](black-box-next-lane-selection.md) | CPU-only reselection of the next black-box research lane after H2. |
| [non-clid-blackbox-reselection.md](non-clid-blackbox-reselection.md) | Superseding CPU-only reselection after CLiD prompt-control closure. |
| [non-graybox-reselection-20260510.md](non-graybox-reselection-20260510.md) | CPU reselection after ReDiffuse and I-A closure; selects response-contract acquisition audit. |
| [post-rediffuse-next-lane-reselection.md](post-rediffuse-next-lane-reselection.md) | CPU reselection after ReDiffuse exact-replay closure; selects second response-contract acquisition. |
| [blackbox-response-contract-acquisition-audit.md](blackbox-response-contract-acquisition-audit.md) | CPU audit showing local second response-contract assets are missing; no GPU release. |
| [blackbox-response-contract-asset-acquisition-spec.md](blackbox-response-contract-asset-acquisition-spec.md) | Minimal portable asset package and CPU gate required to reopen a second black-box response contract. |
| [blackbox-response-contract-package-preflight.md](blackbox-response-contract-package-preflight.md) | Executable package-level preflight for the Kandinsky/Pokemon second-contract candidate. |
| [blackbox-response-contract-discovery.md](blackbox-response-contract-discovery.md) | Repository-level discovery pass showing no paired second response-contract package is currently present. |
| [blackbox-response-contract-second-asset-intake-20260511.md](blackbox-response-contract-second-asset-intake-20260511.md) | Post-tri-score intake refresh confirming no ready second response-contract package is present. |
| [blackbox-response-contract-protocol-scaffold-20260511.md](blackbox-response-contract-protocol-scaffold-20260511.md) | CPU-only scaffold dry-run that freezes the next response-contract package handoff layout without releasing GPU work. |
| [blackbox-response-contract-skeleton-create-20260511.md](blackbox-response-contract-skeleton-create-20260511.md) | CPU-only local skeleton creation and probe showing the package now exists but still needs real query images and responses. |
| [blackbox-response-contract-query-source-audit-20260511.md](blackbox-response-contract-query-source-audit-20260511.md) | CPU-only local asset audit showing existing Kandinsky/Pokemon material cannot fill the response-contract query split or responses. |
| [beans-lora-member-denoising-loss-scout-20260513.md](beans-lora-member-denoising-loss-scout-20260513.md) | CUDA known-split Beans member-LoRA scout showing conditional denoising-loss is weak even after repairing pseudo-membership semantics. |
| [post-response-contract-reselection-20260511.md](post-response-contract-reselection-20260511.md) | CPU-only reselection selecting admitted evidence hardening after response-contract, white-box, and I-D successors fail release gates. |
| [admitted-evidence-bundle-20260511.md](admitted-evidence-bundle-20260511.md) | CPU-only export of the complete admitted Platform/Runtime consumer set as a checked machine-readable bundle. |
| [admitted-consumer-drift-audit-20260515.md](admitted-consumer-drift-audit-20260515.md) | CPU-only no-drift audit proving 2026-05-15 watch, watch-plus, support-only, and candidate-only gates did not change the admitted Platform/Runtime consumer boundary. |
| [admitted-consumer-drift-audit-20260512.md](admitted-consumer-drift-audit-20260512.md) | CPU-only no-drift audit proving recent candidate closures did not change the admitted Platform/Runtime consumer boundary. |
| [secmi-full-split-admission-boundary-review.md](secmi-full-split-admission-boundary-review.md) | CPU-only review showing full-split SecMI is evidence-ready supporting gray-box evidence, but not admitted Platform/Runtime evidence. |
| [secmi-admission-contract-hardening-20260511.md](secmi-admission-contract-hardening-20260511.md) | CPU-only hardening that keeps SecMI stat and NNS as Research-only supporting rows. |
| [post-secmi-next-lane-reselection-20260511.md](post-secmi-next-lane-reselection-20260511.md) | CPU-only reselection selecting the white-box influence/curvature feasibility scout. |
| [whitebox-influence-curvature-feasibility-scout-20260511.md](whitebox-influence-curvature-feasibility-scout-20260511.md) | CPU-only white-box influence/curvature feasibility contract; no method result or GPU release yet. |
| [gsa-diagonal-fisher-feasibility-microboard-20260511.md](gsa-diagonal-fisher-feasibility-microboard-20260511.md) | CPU-only selected-layer diagonal-Fisher micro-board result; negative-but-useful and no GPU release. |
| [gsa-diagonal-fisher-layer-scope-review-20260511.md](gsa-diagonal-fisher-layer-scope-review-20260511.md) | CPU-only layer-scope review for diagonal-Fisher self-influence; mixed but not GPU-ready. |
| [gsa-diagonal-fisher-stability-board-20260511.md](gsa-diagonal-fisher-stability-board-20260511.md) | CPU-only stability board closing diagonal-Fisher self-influence as negative-but-useful; no GPU release. |
| [post-fisher-next-lane-reselection-20260511.md](post-fisher-next-lane-reselection-20260511.md) | CPU-only reselection selecting I-A finite-tail / adaptive boundary hardening after diagonal-Fisher closure. |
| [ia-finite-tail-adaptive-boundary-audit-20260511.md](ia-finite-tail-adaptive-boundary-audit-20260511.md) | CPU-only no-drift audit for admitted strict-tail, adaptive, and candidate/admitted boundaries. |
| [research-boundary-consumability-sync-20260510.md](research-boundary-consumability-sync-20260510.md) | Downstream-consumer boundary sync after ReDiffuse, tri-score, GSA LR, and response-contract closures. |
| [ib-risk-targeted-unlearning-successor-scope.md](ib-risk-targeted-unlearning-successor-scope.md) | CPU scoping review that keeps I-B risk-targeted unlearning on hold until defended-shadow/adaptive review is specified. |
| [ib-defense-aware-reopen-scout-20260512.md](ib-defense-aware-reopen-scout-20260512.md) | CPU scout showing I-B still lacks an executable defended-shadow/adaptive-attacker reopen contract. |
| [ib-defense-reopen-protocol-audit-20260512.md](ib-defense-reopen-protocol-audit-20260512.md) | Code-aware audit confirming the current I-B review path borrows undefended shadow threshold transfer and cannot release GPU work. |
| [ib-defended-shadow-reopen-protocol-20260512.md](ib-defended-shadow-reopen-protocol-20260512.md) | Machine-checkable CPU reopen protocol for future I-B defended-shadow/adaptive-attacker work; still no GPU release. |
| [ib-reopen-shadow-reference-guard-20260512.md](ib-reopen-shadow-reference-guard-20260512.md) | CPU guard that makes defended-shadow reopen mode reject old undefended shadow threshold references. |
| [ib-defended-shadow-training-manifest-20260512.md](ib-defended-shadow-training-manifest-20260512.md) | Coverage-aware CPU manifest blocking the current I-B defended-shadow training contract before any GPU run. |
| [ib-shadow-local-identity-scout-20260512.md](ib-shadow-local-identity-scout-20260512.md) | CPU semantic scout showing a two-shadow target-risk remap is mechanically possible but not true shadow-local risk scoring. |
| [ic-cross-permission-successor-scope.md](ic-cross-permission-successor-scope.md) | CPU scoping review that keeps I-C cross-permission / translated-contract work on hold until a same-spec evaluator exists. |
| [post-ib-next-lane-reselection-20260512.md](post-ib-next-lane-reselection-20260512.md) | CPU-only reselection after I-B protocol audit; selects I-C same-spec evaluator feasibility scout. |
| [ic-same-spec-evaluator-feasibility-scout-20260512.md](ic-same-spec-evaluator-feasibility-scout-20260512.md) | CPU-only I-C feasibility scout showing current translated-alias probes are not same-spec evaluator release surfaces. |
| [research-resting-state-audit-20260510.md](research-resting-state-audit-20260510.md) | Current audit showing Research has no active GPU candidate or reducible CPU sidecar until assets or a new hypothesis arrive. |
| [gsa-loss-score-shadow-stability-review.md](gsa-loss-score-shadow-stability-review.md) | CPU-only leave-one-shadow-out review falsifying the immediate GSA loss-score LR distinct-scorer rescue path. |
| [variation-query-contract-audit.md](variation-query-contract-audit.md) | Executable audit for deciding whether the variation black-box line has real query images and endpoint readiness. |
| [semantic-aux-low-fpr-review.md](semantic-aux-low-fpr-review.md) | CPU-only low-FPR review for the semantic-auxiliary classifier lane. |
| [recon-product-validation-contract.md](recon-product-validation-contract.md) | CPU contract for the next recon product-consumable validation packet. |
| [recon-product-validation-result.md](recon-product-validation-result.md) | Bounded recon product-validation rerun and metric-source boundary. |
| [recon-tail-confidence-review.md](recon-tail-confidence-review.md) | Finite-sample confidence review for admitted recon strict-tail metrics. |
| [rediffuse-collaborator-integration-report.md](rediffuse-collaborator-integration-report.md) | Intake and runtime integration report for the collaborator ReDiffuse bundle and 750k checkpoint. |
| [rediffuse-collaborator-bundle-intake.md](rediffuse-collaborator-bundle-intake.md) | Asset-level intake record for the collaborator ReDiffuse bundle. |
| [rediffuse-runtime-smoke-result.md](rediffuse-runtime-smoke-result.md) | CPU and CUDA compatibility smoke result for the ReDiffuse adapter. |
| [rediffuse-cifar10-small-packet.md](rediffuse-cifar10-small-packet.md) | Bounded 64/64 CIFAR10 candidate packet on the direct-distance ReDiffuse surface. |
| [rediffuse-800k-runtime-probe.md](rediffuse-800k-runtime-probe.md) | CPU runtime compatibility probe for the existing PIA 800k checkpoint under the ReDiffuse adapter. |
| [rediffuse-resnet-parity-packet.md](rediffuse-resnet-parity-packet.md) | Negative-but-useful 750k ResNet scoring-contract parity packet for ReDiffuse. |
| [rediffuse-direct-distance-boundary-review.md](rediffuse-direct-distance-boundary-review.md) | CPU boundary review closing ReDiffuse direct-distance as candidate-only with no automatic 800k GPU release. |
| [rediffuse-checkpoint-portability-gate.md](rediffuse-checkpoint-portability-gate.md) | CPU gate showing 800k checkpoint portability is blocked by unresolved scorer contract. |
| [rediffuse-resnet-contract-scout.md](rediffuse-resnet-contract-scout.md) | CPU scout showing the current Research ResNet mode is not exact collaborator replay. |
| [rediffuse-exact-replay-preflight.md](rediffuse-exact-replay-preflight.md) | CPU preflight for explicit collaborator checkpoint-selection replay mode. |
| [rediffuse-exact-replay-packet.md](rediffuse-exact-replay-packet.md) | Bounded 750k exact-replay packet verdict for the collaborator ReDiffuse baseline. |
| [graybox-triscore-consolidation-review.md](graybox-triscore-consolidation-review.md) | CPU consolidation of existing CDI/TMIA-DM/PIA tri-score packets as positive-but-bounded internal evidence. |
| [graybox-triscore-truth-hardening-review.md](graybox-triscore-truth-hardening-review.md) | CPU truth-hardening gate showing tri-score stays positive-but-bounded and internal-only. |
| [recon-product-row-validation-guard.md](recon-product-row-validation-guard.md) | System-consumable guard for the admitted recon product row. |
| [../product-bridge/recon-product-evidence-card.md](../product-bridge/recon-product-evidence-card.md) | Product-facing machine-readable evidence-card contract for the admitted recon row. |
| [../product-bridge/admitted-evidence-bundle.md](../product-bridge/admitted-evidence-bundle.md) | Product-facing machine-readable bundle contract for the complete admitted consumer set. |
| [clid-bridge-contract.md](clid-bridge-contract.md) | Local CLiD bridge artifact contract and next score-schema gate. |
| [clid-score-schema-gate.md](clid-score-schema-gate.md) | CLiD score-summary schema and low-FPR promotion gate. |
| [clid-tiny-score-bridge.md](clid-tiny-score-bridge.md) | First GPU smoke-scale CLiD score bridge verdict. |
| [clid-100-score-packet.md](clid-100-score-packet.md) | First bounded CLiD score packet that clears the score-summary gate. |
| [clid-candidate-integrity-review.md](clid-candidate-integrity-review.md) | CPU integrity review for the CLiD 100/100 candidate. |
| [clid-repeat-stability.md](clid-repeat-stability.md) | Independent repeat stability for the CLiD 100/100 candidate. |
| [clid-prompt-perturbation.md](clid-prompt-perturbation.md) | Prompt-neutral perturbation result and CLiD admission boundary. |
| [clid-prompt-conditioning-boundary.md](clid-prompt-conditioning-boundary.md) | Canonical CLiD prompt-conditioned claim boundary and next admission test. |
| [clid-adaptive-prompt-perturbation-contract.md](clid-adaptive-prompt-perturbation-contract.md) | CPU-first prompt-control contract for the next CLiD admission design. |
| [clid-swapped-prompt-control.md](clid-swapped-prompt-control.md) | Swapped-prompt CLiD control and updated prompt-conditioning interpretation. |
| [clid-within-split-shuffle-control.md](clid-within-split-shuffle-control.md) | Within-split prompt shuffle CLiD control and prompt-image contract boundary. |
| [clid-prompt-text-only-review.md](clid-prompt-text-only-review.md) | Prompt-text-only nuisance baseline for the CLiD 100/100 bridge. |
| [clid-control-attribution.md](clid-control-attribution.md) | Control-packet attribution comparing strict-tail retention and feature correlations. |
| [research-boundary-card.md](research-boundary-card.md) | Limitations card for downstream consumers. |
| [pia-stochastic-dropout-truth-hardening-review.md](pia-stochastic-dropout-truth-hardening-review.md) | CPU review hardening admitted PIA + stochastic-dropout formal, adaptive, and low-FPR boundaries. |
| [workspace-evidence-index.md](workspace-evidence-index.md) | Where active and archived workspace evidence lives. |

Evidence labels define the project boundary. Do not promote smoke tests,
blocked runs, or negative results into stronger claims without a reviewed
conclusion.
