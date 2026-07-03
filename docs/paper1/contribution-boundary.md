# Paper 1 Contribution Boundary

**Last updated**: 2026-06-18

## Repository-to-Paper Mapping

```text
Research/                    → Paper 1 (DiffAudit independent MIA audit)
  docs/evidence/             admitted rows, reproduction status, CLiD case
  docs/paper1/               Paper 1 evidence package (this directory)
  workspaces/                H2 candidate, PIA, Recon detailed docs

Retrace-Baseline/            → watermark paper team (collaboration)
  outputs/baseline_tree_ring/ Tree-Ring results (our contribution to their paper)
  outputs/baseline_gs/       Gaussian Shading results (pending)
  outputs/baseline_ss/       Stable Signature results (pending)
  src/collapse/              Key-leakage collapse experiments (their task)

scnet/                       → Paper 1 external evidence (closed, weak-signal only)
  output/                    DCU experiment results, MANIFEST

Defense-Transfer/            → Separate line (blocked, not in Paper 1)
Platform/                    → Not relevant to papers
Runtime-Server/              → Not relevant to papers
```

## What Paper 1 Owns

- All MIA experiment results in Research/ (admitted, killed, candidate)
- CLiD spurious signal case study
- H2 non-portable candidate
- scnet DCU weak-signal evidence
- The WSN taxonomy and 10-point diagnostic protocol
- All writing, figures, analysis

## What Paper 1 Does NOT Own

- Tree-Ring, Gaussian Shading, Stable Signature results → belong to the watermark paper team
- Key-leakage collapse experiments → belong to the watermark paper team
- Defense-Transfer experiments → separate blocked line
- Platform/Runtime code → not paper-relevant

## Author Attribution

| Paper | Lead | Contributor Role |
|-------|------|-----------------|
| Paper 1 (MIA audit) | DiffAudit Research Team | All experiments, writing, analysis |
| Watermark paper | Collaborator A | New watermark scheme (their core contribution) |
| Watermark paper | Authors | Baseline reproduction + collapse experiments |

## Data Sharing Rules

1. Paper 1 data (Research/) can be shared as anonymous artifact package
2. Watermark baseline data (Retrace-Baseline/) should NOT be shared without watermark paper team approval
3. scnet DCU data is external closed evidence — use as weak-signal support only
4. Do NOT mix Research MIA data into the watermark paper
5. Do NOT mix watermark baseline data into Paper 1

## Anonymous Submission Checklist

Before Paper 1 submission:
- [ ] Create anonymous copy of Research/docs/paper1/
- [ ] Strip local workspace paths, personal user-home paths, and personal names
- [ ] Replace GitHub URLs with anonymous artifact links
- [ ] Remove author-identifying metadata from all figures and tables
- [ ] Verify no watermark baseline data leaked into Paper 1 materials
