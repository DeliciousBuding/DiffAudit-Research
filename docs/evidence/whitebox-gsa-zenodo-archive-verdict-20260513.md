# White-box GSA Zenodo Archive Verdict

> Date: 2026-05-13
> Status: admitted-family archive / not a new second asset / no full download / no GPU release

## Question

Does Zenodo `10.5281/zenodo.14928092` provide a new Lane A membership asset
for DiffAudit, or is it an artifact archive for the already admitted
white-box GSA family?

This is an asset-identity verdict. No `DDPM.zip`, checkpoint payload, dataset
payload, or GPU job was downloaded or executed.

## Public Evidence Checked

| Source | Finding |
| --- | --- |
| `https://zenodo.org/records/14928092` | The record is titled `White-box Membership Inference Attacks against Diffusion Models`, is a Zenodo conference-paper record for the PoPETs 2025 paper, and lists DOI `10.5281/zenodo.14928092`. |
| Zenodo file listing | The record exposes `DDPM.zip` at `6.7 GB` with checksum `md5:d1e5ae01e2f0e18ec8f8d16d80bcf2f9`, plus `README.md`, `new_environment.yml`, and `LICENSE`. |
| Zenodo description | The record says it is the repository for `White-box Membership Inference Attacks against Diffusion Models`, accepted by PoPETs 2025, and notes that README/environment files were added in the 2026-02-25 version. |
| PoPETs paper | The paper names Gradient attack based on Subsampling and Aggregation, or GSA, as its white-box diffusion MIA framework and links the public code repository. |
| `https://github.com/py85252876/GSA` README | The repository describes gradient attacks on DDPM and Imagen, dataset preprocessing, target/shadow member and nonmember sets, gradient extraction, and evaluation with `Accuracy`, `AUC`, and `TPR`. |
| DiffAudit admitted bundle | DiffAudit already admits the white-box `GSA 1k-3shadow` row and the `GSA 1k-3shadow / W-1 strong-v3 full-scale` defended comparator row for Platform/Runtime consumption. |

The Zenodo API request returned a transient `504 Gateway Time-out` during this
cycle, so the decision relies on the public record page, paper, and repository
README. That is sufficient for the current identity decision because the
question is whether this is a new Lane A asset, not whether to replay GSA.

## Gate Result

| Gate | Result |
| --- | --- |
| New target family | Fail for Lane A. This is the GSA white-box family already represented in DiffAudit admitted evidence, not a new black-box or conditional-diffusion second asset. |
| Target model identity | Reproduction archive likely contains DDPM-related artifacts, but the public record page alone does not expose a tiny per-sample manifest that justifies full archive download in this cycle. |
| Member/nonmember split | The public GSA README documents target/shadow member and nonmember dataset construction, but this cycle did not find a small manifest on the public record page that would make `DDPM.zip` a new ready packet. |
| Query/response coverage | Not applicable as a black-box response contract. This is a white-box gradient-access artifact family. |
| Consumer boundary | Already handled. Current Platform/Runtime admitted rows include GSA and DPDM W-1; this record does not add a new row or schema field. |
| Minimal next action | No full download. Reopen only for reproducibility maintenance if Research decides to refresh the admitted GSA artifact provenance, not for Lane A second-asset search. |

## Decision

`admitted-family archive / not a new second asset / no full download / no GPU
release`.

Zenodo `10.5281/zenodo.14928092` is useful for provenance and future
reproducibility of the admitted white-box GSA line. It is not a fresh Lane A
asset and should not be used to justify a new `6.7 GB` download, GPU replay, or
second-response-contract task.

Do not promote this into:

- a black-box second asset,
- a conditional Stable Diffusion asset,
- a new Platform/Runtime admitted row,
- a fresh GPU candidate,
- another GSA loss-score / gradient ablation route.

Smallest valid reopen condition:

- A reproducibility-maintenance task explicitly needs to refresh the admitted
  GSA artifact provenance and has a bounded manifest-first plan; or
- A future public manifest exposes a small, exact, reusable target/shadow split
  packet that changes the admitted GSA maintenance surface.

## Reflection

This cycle prevented a bad expansion: a large archive looked like a new asset
candidate only because it was external and substantial. After identity checking,
it is the already admitted GSA family. The correct action is to record the
boundary and keep searching for genuinely new assets or mechanisms rather than
spending GPU or disk on an adjacent admitted-family replay.

## Platform and Runtime Impact

None. Platform/Runtime already consume the admitted `GSA` and `DPDM W-1` rows
through the checked admitted bundle. This verdict does not change schemas,
recommendation logic, product copy, or admitted evidence membership.
