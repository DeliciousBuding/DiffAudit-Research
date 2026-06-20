# E2 Codebook Refinement Notes

> Date: 2026-06-06
> Scope: internal notes for the E2 blind-pilot codebook revision.

## 1. V1 Pilot Verdict

The first E2 internal blind pilot is useful but not ready for `N=50` freeze.

- reviewers: `A`, `B`, `C`
- rows reviewed: `15`
- allowed wording raw all-reviewer agreement: `0.6667`
- allowed wording mean pairwise kappa: `0.6565`
- provenance gate raw all-reviewer agreement: `0.6`
- consumer/delta gate raw all-reviewer agreement: `0.6667`
- decision: `revise-codebook-rerun-small-pilot`

Weaker-baseline false-promotion examples exist, so the measurement route is not
dead. The problem is codebook ambiguity, mainly around provenance and
consumer/delta gates.

## 2. V2 Pilot Verdict

The revised-codebook v2 pilot passed the internal Go/No-Go gate.

- reviewers: `D`, `E`, `F`
- rows reviewed: `15`
- allowed wording raw all-reviewer agreement: `0.9333`
- allowed wording mean pairwise kappa: `0.9355`
- provenance gate raw all-reviewer agreement: `1.0`
- consumer/delta gate raw all-reviewer agreement: `0.8`
- decision: `go-freeze-n50-preflight`

This is enough to move into `N=50` freeze preflight. It is not external
adjudication evidence and must not be cited as a paper result.

## 3. Main Ambiguity Classes

| Class | Rows | Problem | Refinement |
| --- | --- | --- | --- |
| Metadata-only wording | `E2P-011`, `E2P-012` | Reviewers split between `candidate-only` and `blocked` for paper metadata without artifact surface. | Define metadata-only public paper rows as `blocked` when no target/split/score/response/metric artifact is visible in the row packet. Use `candidate-only` only when at least one concrete public artifact surface exists but fails row-bound gates. |
| Code-only artifact surface | `E2P-007`, `E2P-009`, `E2P-010` | Public code can look like a candidate, but reviewer wording varies when no row packet exists. | Code-only rows with no target-bound scores/responses and no verifier should default to `candidate-only` if the source is current and relevant; use `blocked` if the row lacks current paper/source availability or the claim target cannot be identified. |
| Bounded negative/support evidence | `E2P-005` | Reviewers split between `candidate-only` and `bounded-support` for weak but executable negative/support packets. | If a row has exact split plus row-level score packet and supports a negative or boundary claim, label `bounded-support` even when the metric is weak. Reserve `candidate-only` for positive audit claims that cannot be admitted. |
| Public split without scores | `E2P-013`, `E2P-014`, `E2P-015` | Split/code surfaces produce disagreement on consumer/delta and wording. | Public split/code without committed row scores is `bounded-support` only when it can support a limited missing-surface or reproduction-context claim; otherwise `candidate-only`. Consumer/delta should be `Fail` unless the row can support a downstream audit/report statement. |
| Official score artifacts without compact manifest | `E2P-004` | CopyMark is useful support, but consumer/delta is ambiguous. | Treat official aggregate score/log/tensor artifacts as `bounded-support`; consumer/delta is `Fail` until row id, split label, target/checkpoint hash, and verifier are bound in one manifest. |

## 4. Gate Clarifications

### Provenance Gate

`Pass` requires enough source identity for another reviewer to locate the same
evidence surface without guessing. For the final `N=50`, this means public URL
plus immutable artifact identity or hash. In the internal pilot, local
`docs/evidence/...` notes can be source summaries, but provenance should be
`Partial` unless the underlying public artifact is itself stable.

### Consumer/Delta Gate

`Pass` requires the evidence to support a downstream audit/report statement at
the claimed wording. Strong metrics, public code, public split files, or
mechanism evidence do not pass this gate by themselves. Use:

- `Pass`: admitted report row with row-bound metric and consumer boundary.
- `Partial`: bounded negative/support claim with exact local packet or public
  split/code surface, but not positive audit admission.
- `Fail`: source-confounded, missing row scores/responses, no verifier, or no
  downstream consumer path.

### Allowed Wording

- `admitted`: target, split, row packet, metric provenance, provenance, and
  consumer/delta gates are all sufficient for the audit/report claim.
- `bounded-support`: evidence can support a limited negative, missing-surface,
  reproduction-context, or mechanism-support claim without positive audit
  admission.
- `candidate-only`: relevant public source/artifact exists, but the row cannot
  yet support a bounded claim with stable evidence.
- `blocked`: metadata-only, withdrawn, inaccessible, irrelevant, or no concrete
  artifact/source surface.

## 5. N50 Preflight Plan

1. Use the v2 instructions for all future E2 blind-review packages.
2. Start from
   [`e2-n50-freeze-preflight-2026-06-06/`](e2-n50-freeze-preflight-2026-06-06/):
   `51` distinct seed rows and `23` actionable candidate/followup rows, but
   strict triage currently finds `0` rows directly freezable into the external
   denominator.
3. Treat only `E2Q-004`, `E2Q-005`, `E2Q-006`, `E2Q-009`, and `E2Q-011` as
   current external candidates, and only after public-source refresh,
   duplicate-surface review, and row-bound artifact inspection.
4. Use the `27` new public-surface scout rows only as no-download source-refresh
   input. They do not count toward `E2-20260606-N50` until they pass
   distinct-surface review and six-gate annotation.
5. Freeze `E2-20260606-N50` only after the selected rows are public-source
   refreshed and blind-review ready. Do not treat the v2 pilot, preflight seed
   table, URL checks, or scout queue as external adjudication evidence.
