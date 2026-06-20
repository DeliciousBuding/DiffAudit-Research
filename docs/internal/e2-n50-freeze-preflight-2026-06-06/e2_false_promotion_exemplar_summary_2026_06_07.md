# E2 False-Promotion Exemplar Summary

> Date: 2026-06-07
> Scope: thirteen completed measurement-route gap-board/post-C14 checks; not an external
> denominator and not admitted evidence.

## Purpose

This summary converts thirteen no-download gap-board/post-C14 checks into a small
false-promotion baseline object. The point is not to claim new attack
performance. The point is to test whether weak promotion rules would accept
public surfaces that DiffAudit correctly blocks or bounds.

The first four rows cover missing public score/response or gated benchmark
surfaces. The next five add semantic and consumer-boundary controls:
attribution versus membership, classifier defense versus diffusion-generator
audit, copying versus membership, prompt memorization versus immutable member
identity, and dataset-level identification versus per-sample membership. The
first post-C14 expansion row adds a code-public latent-space MIA surface whose
README claims split/checkpoint assets but exposes an empty asset link and
local-path execution commands. The second post-C14 expansion row adds a
music/audio diffusion demo surface whose score-like JSON files are generated
mock data rather than checkpoint-bound adversarial-cost artifacts. The third
post-C14 expansion row adds a DOI-backed text-to-video MIA code snapshot with a
dead related GitHub tag and no row-bound video, feature, score, ROC, metric, or
verifier packet. The fourth post-C14 expansion row adds an official GitHub
repository stub whose README claims an implementation but exposes no code or
row-bound artifacts.

## Rows

| Row | Exemplar type | Author-modeled shortcut pressure | Contract blocker |
| --- | --- | --- | --- |
| `E2SCT-004` GenAI Confessions / STROLL | Artifact-availability false promotion | `artifact_availability_would_promote`; `paper_claim_artifact_link_would_promote` | Public STROLL annotations exist, but row-bound generated outputs, DreamSim scores, metric JSON, and verifier are not public. |
| `E2SCT-012` Shake-to-Leak | Code-availability false promotion | `code_availability_would_promote`; `paper_claim_artifact_link_would_promote` | Private set, checkpoints, responses, SecMI scores, extraction candidates, and metrics are runtime products. |
| `E2SCT-016` MIAHOLD / HOLD++ | Mixed-modality defense metric-code false promotion | `code_availability_would_promote`; `metric_code_split_would_promote`; `paper_claim_artifact_link_would_promote` | Checkpoint-bound scores, ROC arrays, metric JSON/CSV, generated responses, and verifier are not public. |
| `E2SCT-021` ELSA Health Privacy | Gated-benchmark starter-metric false promotion | `code_availability_would_promote`; `metric_code_split_would_promote`; `artifact_availability_would_promote`; `paper_claim_artifact_link_would_promote` | Actual challenge targets, labels, predictions, Noisy Diffusion datasets, metadata, and participant artifacts are gated or submission-bound. |
| `E2SCT-002` DMin | Attribution-vs-membership false promotion | `code_availability_would_promote`; `artifact_availability_would_promote`; `metric_code_split_would_promote`; `paper_claim_artifact_link_would_promote` | Public HF train/test data, LoRA weights, and cached gradients support attribution/influence inspection, not a row-bound member/nonmember MIA packet. |
| `E2SCT-005` DIFFENCE | Classifier-defense consumer-boundary false promotion | `code_availability_would_promote`; `artifact_availability_would_promote`; `metric_code_split_would_promote`; `paper_claim_artifact_link_would_promote` | Official code, Zenodo code snapshot, diffusion-purifier components, classifier-defense configs, and MIA scripts support classifier membership privacy, not admitted diffusion-generator response/score evidence. |
| `E2SCT-013` DCR | Copying-vs-membership false promotion | `code_availability_would_promote`; `artifact_availability_would_promote`; `metric_code_split_would_promote`; `paper_claim_artifact_link_would_promote` | Copying/replication code and caption artifacts are not pointwise membership labels, scores, ROC arrays, metric JSON, or verifier packets. |
| `E2SCT-009` Memorization Anisotropy | Prompt-memorization false promotion | `code_availability_would_promote`; `artifact_availability_would_promote`; `metric_code_split_would_promote`; `paper_claim_artifact_link_would_promote` | Prompt `mem` / `nmem` files and memorization metrics are not immutable image-row membership evidence without row-bound scores and verifier. |
| `E2SCT-014` CDI | Dataset-level-vs-per-sample false promotion | `code_availability_would_promote`; `metric_code_split_would_promote`; `paper_claim_artifact_link_would_promote` | Dataset-level copyrighted-data identification and runtime feature/score generation cannot be promoted to per-sample membership evidence. |
| `E2SCT-011` VAE2Diffusion | Code-and-empty-asset-link false promotion | `code_availability_would_promote`; `metric_code_split_would_promote`; `paper_claim_artifact_link_would_promote` | Public latent-space MIA code and split/checkpoint commands are not row-bound split manifests, checkpoints, scores, ROC arrays, metric JSON, or verifier packets. |
| `E2SCT-020` LSA-Probe | Mock-demo-score false promotion | `code_availability_would_promote`; `artifact_availability_would_promote`; `metric_code_split_would_promote`; `paper_claim_artifact_link_would_promote` | Public demo score-like JSON is generated mock visualization data; implementation, target identities, audio splits, score provenance, ROC/metric packet, and verifier are absent. |
| `E2SCT-019` VidLeaks T2V | T2V-code-snapshot false promotion | `code_availability_would_promote`; `paper_claim_artifact_link_would_promote` | DOI-backed T2V MIA code snapshot and related GitHub URL are not a hashable T2V target, exact video membership split, generated-video packet, score/ROC/metric artifact, or verifier. |
| `E2SCT-024` DME | Official-repo-stub false promotion | `code_availability_would_promote` | The official public GitHub repository is a README-only stub; implementation code, paper protocol, target/split manifest, checkpoint, scores, ROC/metric JSON, and verifier are absent. |

## Paper Value

These rows support a measurement-paper claim about false promotion:

- A code-only rule would accept code-public rows even when the evidence-bearing
  score/response packet is absent.
- An artifact-availability rule would accept STROLL annotations, ELSA starter
  assets, DMin public HF artifacts, DCR caption metadata, or prompt lists
  or LSA-Probe demo JSON without row-bound membership evidence.
- A metric-code/split-visible rule would accept defense, attribution, copying,
  memorization, dataset-inference, or code-public latent-space surfaces despite
  missing the consumer claim's target-bound MIA packet.
- A score-like-demo shortcut would accept generated adversarial-cost and ROC
  JSON even when the generator says the values are mock visualization data.
- A consumer-boundary shortcut would accept a classifier membership-defense
  workflow as diffusion-generator audit evidence because it uses diffusion
  purification and MIA scripts.
- An official-repository shortcut would accept a README-only official repo as an
  implementation surface even when no implementation or audit packet is present.
- DiffAudit blocks all thirteen because target, split, score/response, metric
  provenance, semantic consumer boundary, and surface delta do not jointly pass.

## Boundary

This is not `E2-20260606-N50`, not external adjudication evidence, not admitted
response/score evidence, and not compute release. It is a compact baseline
object for future external-review package design once the corpus denominator is
real.

Do not add a new weak-rule taxonomy here unless it changes reviewer-facing
wording. Keep using the gap-board baseline tags.
