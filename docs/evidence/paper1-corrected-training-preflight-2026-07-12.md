# Paper 1: corrected training preflight

> **SUPERSEDED by 2026-07-18 Route C closed matrix.**
> Long-training blocker language below is historical. Do not resume formal training from this memo.


- **Date**: 2026-07-12
- **Status**: superseded by outcome-blind evaluation-contract repair
- **Verdict**: Batch size 32 passed the training and exact-resume resource gate, but the first formal matrix was stopped before outcomes when the canonical PIA post-training path was found incomplete.

## Scope

This preflight tested only the corrected member-only training contract and its
artifact chain. It did not inspect H1, PIA, AUC, or any other membership outcome.
The run used the first predeclared seed, 25,000 fixed member rows, the frozen
split SHA256, and corrected-only output labels.

## Resource correction before outcomes

The initial batch-64 attempt was stopped before completion. Observed GPU memory
reached about 7.9 GiB on an 8 GiB device, leaving only tens of MiB free, and
2,000 steps had not completed after about 22 minutes. This failed the frozen
6.0k steps/hour and VRAM-headroom gates.

Before any corrected metric was viewed, the canonical training config was
changed once to batch size 32. No model, optimizer, schedule, precision, seed,
or step horizon was changed. The protocol was then rebuilt and hash-sealed.

## Passing run

The replacement run used three segments to exercise resume:

| Segment | Wall time | Approx. throughput |
| --- | ---: | ---: |
| 0 -> 200 | 57 s | 12.6k steps/hour |
| 200 -> 400 | 67 s | 10.7k steps/hour, including resume overhead |
| 400 -> 2,000 | 459 s | 12.5k steps/hour |
| Active total | 583 s | 12.3k steps/hour |

Observed runtime bounds:

- fresh-run GPU allocation: about 5.50 GiB;
- resume peak GPU allocation: about 6.74 GiB;
- minimum observed free GPU memory: about 1.21 GiB;
- maximum observed temperature: 71 C;
- maximum observed power draw: about 103 W;
- no OOM or observed thermal throttling.

## Artifact checks

The run produced checkpoints at steps 200, 400, and 2,000. For every checkpoint:

- the on-disk SHA256 matches its manifest receipt;
- checkpoint metadata records the same protocol hash, split SHA256, code commit,
  seed, step, and batch-32 training-config hash;
- the manifest retains all three receipts after resume;
- `weights_only=True` loading succeeds on CPU;
- log terminal events report the expected final step without interruption.

Generated checkpoints and logs remain outside Git under the configured download
and training-output roots.

## Decision

The corrected training implementation passes Stage 0's training, resource,
resume, and receipt gates. This does not release the four 100k targets. The next
required gate is a complete evaluation benchmark on the 2,000-step checkpoint:

1. extract H1 activations only for the locked calibration/evaluation rows;
2. derive common noise from the sealed row/timestep/draw contract;
3. emit strict row-bound H1 and PIA score packets;
4. time the full H1 + PIA evaluation and project the worst non-STOP branch with
   a 10% failure buffer.

No long training begins until that projection fits the available GPU window.

## Outcome-blind formal-matrix abort

The full H1 and canonical PIA timing projection subsequently fit the available
window. A formal Stage 1 launch therefore began on the frozen target matrix.
During an independent audit of the commands that would consume the completed
100k checkpoints, two remaining P0 gaps were found before any membership score
or metric was generated:

1. the formal canonical PIA exporter accepted legacy `ema_model`/`net_model`
   checkpoint keys but not the corrected trainer's `ema` key;
2. the PIA path did not yet expose the predeclared complete-roster paired
   bootstrap, global AUC-range test, and Holm family required for the paper
   decision.

The first target was stopped at step 22,000. Its final saved checkpoint receipt
matched its on-disk SHA256; the other three targets had not started. This partial
target is an infrastructure-abort artifact and MUST NOT be resumed or scored.

Because no corrected outcome had been viewed, the protocol was reopened rather
than patched after results. The repair adds corrected EMA loading, explicit
analysis repository-state provenance, canonical target ordering, PIA
confirmatory statistics, and 1,000 paired bootstrap draws for both H1 and PIA.
The increase from 200 to 1,000 is required because 200 plus-one draws make Holm
rejection mathematically unreachable for the 28 pairs in an eight-target set.

Long training remains blocked until the repaired code is committed, a new
protocol hash is sealed, and the necessary dry-run/resource preflight is
repeated with fresh output labels. The aborted target and its protocol are never
part of corrected evidence.
