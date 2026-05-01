# CLiD Adaptive Prompt-Perturbation Contract

This note defines the next CPU-first CLiD admission design. It does not admit
CLiD and does not schedule a GPU run by itself.

## Verdict

```text
next CLiD work is a prompt-control design gate, not another same-contract GPU packet
```

The prompt-neutral packet showed that the current positive CLiD signal depends
on the prompt-conditioned bridge. The next useful question is narrower:

```text
Can CLiD retain strict-tail membership signal when prompt information is
controlled, swapped, or otherwise prevented from acting as a split shortcut?
```

## Perturbation Modes

The local perturbation tool supports two CPU metadata controls:

| Mode | Purpose | Promotion relevance |
| --- | --- | --- |
| `fixed` | Rewrites every member and nonmember prompt to one neutral prompt such as `a face`. | Tests whether the signal survives without prompt variation. The first run failed this gate. |
| `swap-split-prompts` | Swaps member and nonmember prompt text by row while preserving image files and row counts. | Tests whether prompt text itself is acting as a split shortcut. This is the next CPU-ready control. |
| `within-split-shuffle` | Shuffles prompt text inside each split while preserving split-level prompt distribution. | Tests whether image-prompt pairing matters after split-level prompt distribution is preserved. |

Command shape:

```powershell
python -X utf8 scripts/perturb_clid_bridge_prompts.py `
  --run-root <ignored-run-root> `
  --mode within-split-shuffle `
  --seed 0
```

The tool only rewrites `datasets/member/metadata.jsonl` and
`datasets/nonmember/metadata.jsonl` inside an ignored run root. It does not
create evidence by itself; score generation and review remain separate gates.

## Admission Gate

A new CLiD GPU packet is worth running only if the planned packet has all of:

| Gate | Requirement |
| --- | --- |
| Matched identity | same member and nonmember image identity across original and prompt-control contracts |
| Prompt-control mode | at least one fixed or swapped-prompt control |
| Strict-tail primary metric | `TPR@0.1%FPR` reported and nonzero under the control |
| Nuisance checks | row alignment, duplicate image hashes, duplicate prompts, and text-length AUC reviewed |
| Boundary result | report both the prompt-conditioned result and the prompt-control result side by side |

The first swapped-prompt control is recorded in
[clid-swapped-prompt-control.md](clid-swapped-prompt-control.md), and the first
within-split shuffle control is recorded in
[clid-within-split-shuffle-control.md](clid-within-split-shuffle-control.md).
Both survive with nonzero strict-tail signal but degrade sharply, so the next
review should check whether an image-only control or independent prompt-control
repeat answers a genuinely new question.
The second within-split shuffle seed weakens the residual to `TPR@0.1%FPR =
0.08` and loses auxiliary permutation significance.

The prompt-text-only nuisance baseline is recorded in
[clid-prompt-text-only-review.md](clid-prompt-text-only-review.md). It shows
moderate prompt split separability but weak strict-tail signal, so prompt text
alone does not explain the original CLiD repeat.

The control attribution review is recorded in
[clid-control-attribution.md](clid-control-attribution.md). It shows that CLiD
auxiliary features lose row-wise correlation under prompt controls, while
feature 0 remains more stable.

## Current State

- GPU task: none selected.
- CPU sidecar: move CLiD to hold unless a new protocol can isolate image
  identity from prompt-conditioned auxiliary behavior. Do not run another
  same-protocol CLiD GPU packet.
- Product impact: none. Platform and Runtime should continue treating CLiD as
  candidate-only.
