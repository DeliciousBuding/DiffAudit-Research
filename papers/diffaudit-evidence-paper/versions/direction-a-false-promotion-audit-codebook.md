# Direction A False-Promotion Audit Codebook

Date: 2026-06-08

This codebook defines how a reviewer should inspect the Direction A E2 false-promotion baseline. It is a prepared review protocol, not completed external adjudication, not inter-rater reliability evidence, and not an N50 denominator result.

## Scope

The review packet covers thirteen no-download public-surface checks:

- `E2SCT-004` GenAI Confessions / STROLL
- `E2SCT-012` Shake-to-Leak
- `E2SCT-016` MIAHOLD / HOLD++
- `E2SCT-021` ELSA Health Privacy Challenge
- `E2SCT-002` DMin
- `E2SCT-005` DIFFENCE
- `E2SCT-013` DCR
- `E2SCT-009` Memorization Anisotropy
- `E2SCT-014` CDI copyrighted data identification
- `E2SCT-011` VAE2Diffusion
- `E2SCT-020` LSA-Probe music diffusion
- `E2SCT-019` VidLeaks T2V
- `E2SCT-024` DME

The packet tests whether weak public-surface rules would overpromote a row if
the evidence contract were ignored. It does not ask reviewers to reproduce a
model, download gated payloads, run code, register for a benchmark, or produce
new scores.

## Inputs

Use these paper-relative files:

- `REVIEWER_README.md`: bundled launch brief with the reviewer task, primary
  file order, filename convention, author-keyed files to avoid before labeling,
  and the maintainer aggregation command.
- `versions/direction-a-c14-external-review-launch-protocol.md`: launch
  protocol for reviewer independence, return-file naming, maintainer intake,
  reporting boundaries, and stop rules.
- `data/false_promotion_blinded_review_packet.csv`: blocker-blinded packet for
  independent reviewer inspection. This is the primary reviewer input.
- `data/false_promotion_row_trace.csv`: reviewer-safe row-level public URLs,
  observation dates, and boundary notes for navigation.
- `data/false_promotion_external_review_template.csv`: blank decision template
  for reviewer labels.
- `post-label-author-key/*`: same-team blocker keys, author gate labels,
  generated summaries, source rows, full row trace, claim traces, and cached
  evidence notes in the separate maintainer-only post-label key ZIP. Do not
  share or read these files before finalizing independent labels.

## Weak Rules

A weak rule is any shortcut that creates author-modeled promotion pressure for
a public surface without the full evidence contract.

| Weak rule | Meaning |
| --- | --- |
| `code_availability_would_promote` | Public code, scripts, or configs would be treated as enough to promote the row. |
| `artifact_availability_would_promote` | Public datasets, annotations, prompt lists, weights, example files, or starter packets would be treated as enough. |
| `paper_claim_artifact_link_would_promote` | A paper-to-artifact link would be treated as enough even when the target, split, scores, or metric replay are missing. |
| `metric_code_split_would_promote` | Metric code, split hints, benchmark scripts, or evaluation workflows would be treated as enough without checkpoint-bound score/response artifacts. |
| `score_only_would_promote` | Score rows alone would be treated as enough without target, split, provenance, and consumer-boundary checks. |

## Current Rule Pressure

The prepared 2026-06-07 packet has the following generated weak-rule counts:

| Weak rule | Rows |
| --- | --- |
| `paper_claim_artifact_link_would_promote` | `12 of 13 selected rows` |
| `code_availability_would_promote` | `12 of 13 selected rows` |
| `metric_code_split_would_promote` | `9 of 13 selected rows` |
| `artifact_availability_would_promote` | `7 of 13 selected rows` |
| `score_only_would_promote` | `0 of 13 selected rows` |

These counts instantiate shortcut-rule pressure within this ordered stress
object.
They are not public-surface prevalence, external reviewer reliability, or
evidence-denominator counts.

## Gate Labels

For each row, assign each gate one of `Pass`, `Partial`, `Fail`, or `N/A`.

| Gate | Pass condition |
| --- | --- |
| `target_gate` | The audited model/checkpoint/target identity is fixed, public-safe, and bound to the row. |
| `split_gate` | The member/nonmember or defended/undefended comparison set is fixed and row-bound. |
| `score_or_response_gate` | Public row-level scores, responses, generated samples, feature tensors, or equivalent per-row evidence are available. |
| `metric_gate` | ROC/AUC/low-FPR or task-specific metric artifacts can be replayed or checked without reconstructing the experiment. |
| `semantic_boundary_gate` | The artifact answers the same question as per-sample diffusion membership or the declared consumer boundary. |
| `provenance_gate` | Source identity, hashes, immutable references, and row bindings are sufficient for audit. |
| `consumer_boundary_gate` | The row can be consumed under the paper's admitted/support/candidate boundary without changing the claim type. |

Use the gate values mechanically:

- `Pass`: the pass condition is fully satisfied from public, row-bound material
  available to the reviewer.
- `Partial`: the public surface contains relevant evidence in the right
  category, but the evidence lacks a required binding such as row IDs, target
  hash, checkpoint identity, metric packet, public verifier, or consumer
  boundary.
- `Fail`: the required evidence category is absent, contradicted, or answers a
  different task.
- `N/A`: the gate is definitionally inapplicable to the row's public claim. Do
  not use `N/A` merely because an artifact is missing.

The bundled row-level evidence notes were written before the final C14 template
split semantic-boundary and consumer-boundary labels. If a note uses a combined
`consumer/delta` or equivalent gate, map it as follows: semantic mismatch
between the public artifact and per-sample diffusion-generator membership goes
to `semantic_boundary_gate`; downstream wording or product/report consumption
limitations go to `consumer_boundary_gate`; if both are present, label both.

## Verdict Labels

Use one of these labels in `false_promotion_verdict`:

- `false_promotion_control`: the row is a valid weak-rule stress case, but not
  admitted evidence.
- `semantic_boundary_block`: the public artifact is about a nearby but different
  task, such as attribution, copying, prompt memorization, dataset inference, or
  a gated challenge.
- `artifact_surface_block`: the public surface looks strong but lacks a
  checkpoint-bound score/response packet, ROC/metric JSON, or verifier.
- `needs_external_adjudication`: the row cannot be labeled from the prepared
  packet alone and requires a real external reviewer pass or upstream artifact
  clarification.
- `invalid_row`: the row should be removed from the baseline because the source
  observation is wrong or duplicates another row.

## Review Procedure

1. Read one row at a time from
   `data/false_promotion_blinded_review_packet.csv`.
2. Identify which weak rules could promote the row under a shortcut policy.
3. Use `data/false_promotion_row_trace.csv` only to follow public URLs and
   no-download evidence notes for the same `review_id`.
4. Fill the seven gate columns using only the blocker-blinded packet and cited
   public-surface notes. Do not download large artifacts or execute the upstream
   code.
5. Select the first blocker that prevents admission or denominator use.
6. Write the narrowest allowed wording. The wording must preserve whether the
   row is admitted, support-only, candidate-only, or a false-promotion control.
7. Leave `compute_release` as `no` unless the row has a fixed target, fixed
   split, score/response artifact, metric replay path, provenance, and consumer
   boundary.
8. Do not use LLM/AI assistance for gate labels, verdict labels, first blockers,
   allowed wording, or notes.
9. Return one filled CSV named
   `false_promotion_external_review_<reviewer-id>.csv`, with the same reviewer
   id in all thirteen `reviewer` cells and no changes to row ids, titles,
   allowed-value columns, or row order.
10. Return the reviewer declaration bundled with the packet as
    `REVIEWER_DECLARATION_<reviewer-id>.md`.

The C14 template uses seven gate columns. It extends the earlier E2 six-gate
review form by splitting semantic-boundary and consumer-boundary decisions into
separate gates, because several C14 controls are blocked by task mismatch rather
than artifact absence alone. The blank template exposes controlled columns for
gate labels, verdict labels, and compute-release labels. `first_blocker`,
`allowed_wording`, and `notes` remain reviewer-written text because the point
of the task is to test whether an independent reader can recover the same first
missing surface from the packet.

`first_blocker` means the earliest gate in template column order whose `Fail`
or blocking `Partial` label prevents the next stronger claim. Prefer a compact
phrase of the form `<gate>: <missing surface>`, for example
`score_or_response_gate: no public row-bound score packet`. `allowed_wording`
should be one concise sentence and must not promote a row beyond admitted,
candidate, support-only, false-promotion-control, or invalid-row status.

The `weak_rules_under_test` and `weak_surface_family` columns in the blinded
packet are author-assigned trace categories. They are included so reviewers know
which shortcut pressure the row was selected to test. Reviewers may disagree in
`notes`; the adjudicated labels are the seven gates, verdict, first blocker,
allowed wording, and compute-release field.

If a public URL is dead, rate-limited, or redirects to a different artifact,
record that fact in `notes`. If the row cannot be judged from the pre-label
packet and accessible public surfaces, use `needs_external_adjudication`.
Cached evidence notes live under `post-label-author-key/` and must not be used
before labels are final.

`compute_release` should stay `no` for ordinary C14 rows. Use
`yes_with_full_contract` only if all seven gates pass and the reviewer can
identify a fixed target, fixed split, public row-bound score or response packet,
metric replay path, provenance, and compatible consumer boundary from public
materials alone.

## Future External Adjudication Protocol

An external-label result is not valid until at least two independent reviewers
complete the template from the blocker-blinded packet. A stronger reliability
claim requires three reviewers, majority labels for every gate/verdict column, a
disagreement log for every non-unanimous row, and an explicit statement that
rows labeled `needs_external_adjudication` or `invalid_row` are excluded from
any shortcut-rule count until resolved.

Each returned review must include the bundled reviewer declaration. The
declaration must state that the reviewer did not inspect author-keyed files
before labeling, did not use LLM/AI assistance for gate/verdict/wording
decisions, did not communicate with other reviewers about labels, did not
download large assets or run upstream code, and is not a same-team C14 label
author. Reviewers who inspect the author key after submission cannot revise
their labels for reliability analysis.
The aggregation script machine-checks the returned declaration key/value fields
before accepting reviewer CSVs.

The author adjudication key is used only after reviewer templates are complete.
It supports disagreement analysis against same-team labels; it is not a
substitute for external labels and must not be reported as inter-rater
reliability.

After labels are returned, aggregate them from the Research repository root with
  `python -X utf8 scripts\aggregate_false_promotion_external_review.py`. The
  script accepts one thirteen-row CSV per reviewer, validates the template schema and
allowed labels, writes majority labels and disagreement logs, and compares
majority labels with the author adjudication key. Its `--check` mode validates
that the packet is label-ready even when no reviewer CSV exists. Rows labeled
`needs_external_adjudication` or `invalid_row` remain excluded until resolved.
The aggregation output is still bounded to the supplied reviewers and the thirteen
selected rows; it does not create N50 denominator evidence, field-prevalence
evidence, compute release, or an inter-rater reliability claim by itself.

## Exclusions

The reviewer must not:

- Count the thirteen rows as external adjudication evidence.
- Pool the rows into N50 denominator, field-prevalence, or reproducibility-rate
  claims.
- Treat code, metric scripts, starter packets, prompt lists, annotations,
  dataset-level indicators, classifier-defense workflows, diffusion purifiers,
  or copying metrics as per-sample diffusion-generator membership scores.
- Download Stable Diffusion weights, LAION/ImageNet/COCO payloads, platform-gated
  challenge assets, medical data, full HF parquet payloads, Google Drive
  classifier/diffusion checkpoints, generated images, or upstream checkpoint
  folders.
- Run LoRA/DreamBooth fine-tuning, SecMI/PIA scripts, CDI feature extraction,
  copying metrics, or benchmark submissions for these rows.

## Falsification Criteria

This stress object would force a contract revision if a row has fixed target
identity, fixed membership semantics, row-bound public scores or responses,
replayable metrics, sufficient provenance, and a compatible consumer boundary
but the contract still blocks admission. It would also fail as an instrument
test if an independent reviewer cannot reproduce the same first blocker from
the blocker-blinded packet and row trace.

## Current Status

The 2026-06-08 paper packet has prepared a hard-blind reviewer ZIP, a separate
maintainer-only post-label key ZIP, a blocker-blinded packet, reviewer-safe row
trace, blank template, author adjudication key, and machine-checked
external-label aggregation path. No independent reviewer labels have been
collected. The only paper-safe claim is that these thirteen selected rows are
false-promotion baseline controls for weak-rule, semantic-boundary, and
consumer-boundary stress testing.
