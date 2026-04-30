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

Command shape:

```powershell
python -X utf8 scripts/perturb_clid_bridge_prompts.py `
  --run-root <ignored-run-root> `
  --mode swap-split-prompts
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

If the swapped-prompt control also collapses, CLiD remains useful only as a
prompt-conditioned diagnostic surface. If it survives with nonzero strict-tail
signal, the next review should check whether prompt text and image identity are
both necessary or whether one surface is sufficient.

## Current State

- GPU task: none selected.
- CPU sidecar: prepare a swapped-prompt control packet from the existing CLiD
  bridge structure when a reversible ignored run root is available.
- Product impact: none. Platform and Runtime should continue treating CLiD as
  candidate-only.
