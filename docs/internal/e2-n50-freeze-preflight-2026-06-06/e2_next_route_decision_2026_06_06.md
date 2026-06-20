# E2 下一路线决策

> Date: 2026-06-06
> Scope: no-download route decision after E2Q-005 review and CopyMark gate.

## 结论

本轮不打开 `E2SCT-001` MT-MIA 的 tabular/relational stratum，也不继续把
`E2Q-004` CLiD 当作第二 response/score asset 追。当前 CCF-A 升级路线应转向
larger distinct-surface corpus + external audit + false-promotion baseline，
而不是继续 asset hunt 或释放 GPU/DCU。

这不是说 MT-MIA 和 CLiD 没有价值。它们的价值分别是：

- MT-MIA：真实公开的 relational-tabular synthetic-data score-packet support；
  可用于将来单独的 cross-domain evidence-contract stratum，但不能并入当前
  image-diffusion denominator。
- CLiD：强 numeric score/support signal；但没有公开 row-to-COCO identity
  manifest，不能把 numeric score rows 绑定到 immutable image/caption/split/role。

因此，`E2-20260606-N50` 仍保持 `0` directly freezable external denominator
rows，Day 5 small run gate 不触发。

Guard sentence: CLiD 仍是 identity-missing bounded support；MT-MIA 不在当前 image-diffusion N50 周期打开 tabular/relational stratum。

## Public-Surface Checks

### CLiD

Current public checks:

- GitHub: `https://github.com/zhaisf/CLiD`
- `refs/heads/main`: `b108e70b0fbca23bea6e2fa052e48ee032bb8698`
- GitHub root page still exposes code, `inter_output/`, `poster/`, `train_sh/`,
  and evaluator/training scripts, but no public `data/` manifest directory.
- GitHub `inter_output/` lists numeric-score subdirectories `CLID`, `PFAMI`,
  `PIA`, and `SecMI`.
- Hugging Face: `https://huggingface.co/datasets/zsf/COCO_MIA_ori_split1/tree/main`
  remains gated. The page states that files can be listed but not accessed; the
  preview lists `.gitattributes`, `README.md`, and `mia_COCO.zip`.

Decision:

`E2Q-004` remains bounded support / identity-missing evidence. Do not count it
in N50, do not download `mia_COCO.zip`, and do not run CLiD GPU/XGBoost/prompt
control work. Reopen only if authors publish a row manifest mapping each
`inter_output/*` row to COCO image/caption/split/role, or if authorized HF
metadata-only inspection exposes the same binding without image payload access.

### MT-MIA

Current public checks:

- GitHub: `https://github.com/joshward96/MT-MIA`
- `refs/heads/master`: `d02aebb9241b383f08a4f89cc32054cf283c2ec6`
- The repository README says it includes pre-processed real data in `data/`,
  pre-generated synthetic data in `synth_data/`, and attack results in
  `results/`; it also states RelDiff generation required about `450` H200
  GPU-hours.
- GitHub `data/` lists `airbnb`, `airlines`, `california`, and `toy`.
- GitHub `results/` lists `clava_ddpm`, `reldiff`, `rtf`, and `toy.json`.

Decision:

MT-MIA is stronger than paper-only tabular watch items, but it is not an
image-diffusion response/score asset. It also lacks per-score row IDs and a
current DiffAudit relational-tabular consumer boundary. Opening a separate
tabular/relational stratum would create a second thesis with its own
denominator, adjudication rules, baselines, and overclaiming risks. That is not
the highest-value move for the current Direction A manuscript.

Keep MT-MIA as `bounded_cross_domain_support`. Reopen only if DiffAudit
explicitly chooses a cross-domain evidence-contract paper, or if the authors
publish row-ID-bound verifier artifacts that make a relational-tabular stratum
scientifically separable from the image-diffusion denominator.

If a future cross-domain stratum is explicitly opened, the smallest useful check
is one no-download row-binding probe on `clava_ddpm / airbnb / seed_42`: inspect
only small text/config/schema surfaces plus one official JSONL score sample and
ask whether public split order plus stable relational entity IDs can bind the
`2,000` score positions to member/nonmember entities. If order-only inference is
the only binding, stop at bounded support.

## Route Decision

For the current CCF-A push, choose the measurement route:

1. freeze a larger distinct-surface corpus only from public, row-auditable
   artifact surfaces;
2. add external label audit after the denominator is real, not before;
3. measure false-promotion against score-only, code-availability, and
   artifact-availability baselines;
4. report MT-MIA, CLiD, CopyMark, and E2Q-005 only with their bounded wording
   unless a new public artifact changes their six-gate status.

Stop condition: if the corpus route still cannot produce a real external
denominator, Direction A remains a bounded measurement paper and should not be
called CCF-A-ready.
