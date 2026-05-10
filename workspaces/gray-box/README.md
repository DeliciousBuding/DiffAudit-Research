# Gray-Box Workspace

## Current Status

- Direction: partial-observation membership inference (PIA, SecMI, TMIA-DM) and defense evaluation.
- Main method: `PIA` is the strongest admitted local DDPM/CIFAR10 gray-box line.
- Defense reference: stochastic dropout is a provisional defended comparator,
  not validated privacy protection.
- Active candidate: ReDiffuse 750k exact-replay packet is a possible next GPU
  candidate, but not released. `resnet_collaborator_replay` passed CPU
  preflight; 800k remains blocked.
- GPU: none released.

## Files

| File | Purpose |
| --- | --- |
| [plan.md](plan.md) | Current status and next steps. |

## Archive

Closed notes are in
[../../legacy/workspaces/gray-box/2026-04/](../../legacy/workspaces/gray-box/2026-04/).
