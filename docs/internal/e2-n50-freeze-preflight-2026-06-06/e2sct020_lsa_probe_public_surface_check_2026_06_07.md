# E2SCT-020 LSA-Probe Public-Surface Check

> Date: 2026-06-07
> Mode: no-download metadata/raw-page check
> Decision: mock-demo-score false-promotion exemplar only / not admitted / not denominator / no_compute_release

## Scope

This check refreshes `E2SCT-020` after the ten-row C14 baseline. It uses only
public metadata, raw README/page files, small GitHub Pages demo files, and
arXiv API metadata. It does not download audio datasets, model checkpoints,
archives, generated audio, or arXiv source, and it does not run code.

Sources checked:

- `https://github.com/kaslim/LSA-Probe`
- `https://raw.githubusercontent.com/kaslim/LSA-Probe/HEAD/README.md`
- `https://github.com/kaslim/LSA-Probe/releases`
- `https://kaslim.github.io/lsa-probe/`
- `https://raw.githubusercontent.com/kaslim/kaslim.github.io/main/lsa-probe/generate_demo_data.py`
- `https://raw.githubusercontent.com/kaslim/kaslim.github.io/main/lsa-probe/data/adversarial_costs.json`
- `https://raw.githubusercontent.com/kaslim/kaslim.github.io/main/lsa-probe/data/roc_curves.json`
- `https://raw.githubusercontent.com/kaslim/kaslim.github.io/main/lsa-probe/data/main_results.json`
- `https://export.arxiv.org/api/query?id_list=2602.01645`

## Findings

| Surface | Current finding |
| --- | --- |
| Project repo API | GitHub REST API returned 403 rate-limit, so this check used raw README, releases page, and GitHub HTML fallback. |
| Project README | Raw README status `200`, length `309`, SHA-256 `a3ea7ebf72e5855490206266a8ef176f553037a8c609ca43829a2b77e9eb9089`; it says the full implementation and reproducibility instructions will be released upon paper acceptance. |
| GitHub releases | Releases page status `200`, release tag links `0`, and no-releases page text present. |
| GitHub HTML fallback | Project page status `200`; selected file/title scan found `README.md` only and the same acceptance-gated implementation wording. |
| Demo page | GitHub Pages demo status `200`, length `31908`, and links back to `github.com/kaslim/LSA-Probe`. |
| Demo generator | Raw `generate_demo_data.py` status `200`, length `8884`, SHA-256 `2cb6c50583e221b45447d9af401a62a57c9ebe6cac93a55e2a762644f914d7b9`; header says it generates mock data for the interactive demo. The code uses `np.random.seed(42)`, `N_SAMPLES = 500`, gamma-distributed member/nonmember draws, ROC computation, and writes demo JSON files. |
| Demo JSON | `adversarial_costs.json`, `roc_curves.json`, and `main_results.json` are public and small, but they are generated demo artifacts with no audio IDs, target checkpoint binding, exact split manifests, score provenance, replay command, or metric verifier. |
| arXiv metadata | arXiv API reports publication timestamp `2026-02-02T05:04:37Z`; the summary frames the task as membership inference for generative music models. |

## False-Promotion Interpretation

`E2SCT-020` is a clean weak-rule stress case:

- A paper-artifact-link rule would be attracted by the paper, project repo, and
  public demo.
- A code-availability rule would be attracted by a GitHub code link, even
  though the project README says implementation and reproducibility
  instructions are withheld until acceptance.
- An artifact-availability rule would be attracted by the public demo and
  `data/*.json` files.
- A metric/split-visible rule would be attracted by score-like adversarial-cost
  and ROC JSON, even though those values are generated mock visualization data.

DiffAudit blocks the row because the public surface has no implementation
tree, fixed target identities, exact member/nonmember audio manifests,
checkpoint-bound adversarial-cost score packet, ROC/metric artifact, or ready
verifier.

## Boundary

Do not count `E2SCT-020` as admitted evidence, external-denominator evidence,
field prevalence evidence, completed external adjudication, or reviewer
reliability evidence. It is a mock-demo-score false-promotion exemplar only.

Do not launch GPU/DCU work from this row. Do not download MAESTRO, FMA-Large,
DiffWave, MusicLDM, audio clips, checkpoints, or generated audio. Do not treat
GitHub Pages `data/*.json` as paper score evidence. Reopen only if the authors
publish implementation plus public-safe target model identities, exact
member/nonmember manifests, and real adversarial-cost score/ROC/metric
artifacts, or if DiffAudit explicitly opens a music/audio membership lane with
a consumer-boundary decision.
