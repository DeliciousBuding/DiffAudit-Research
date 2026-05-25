# Claim Register

## Allowed Main Claims

| ID | Claim | Evidence | Boundary |
| --- | --- | --- | --- |
| C1 | DiffAudit can report five admitted diffusion privacy audit rows under a unified metric and boundary contract. | `admitted-results-summary.md`, `admitted-evidence-bundle.json` | Admitted within workspace/runtime-mainline semantics only. |
| C2 | White-box access exposes a much stronger membership signal than the current admitted black-box and gray-box rows. | GSA AUC `0.998192`; recon AUC `0.837`; PIA AUC `0.841339` | GSA is an upper-bound comparator, not a final benchmark. |
| C3 | The H2 output-cloud geometry scorer finds a strong Research-side membership signal that is not reducible to seed-to-output distance. | H2 output-cloud AUC `0.961529`, raw H2 AUC `0.905693`, label-shuffle AUC `0.507595` | Candidate only; not admitted or portable by default. |
| C4 | H2 output-cloud geometry survives shared-position seed-offset control and cross-cache transfer. | Shared-position AUC `0.967819`; seed `177` AUC `0.956192`; transfer mean AUC `0.959755` | Still one response-contract family. |
| C5 | Several plausible second-asset routes are blocked by missing public artifacts, weak transferred signal, or consumer-boundary mismatch. | ReDiffuse, CommonCanvas, MIDST, Tracing Roots, CopyMark, SD ReDiffuse evidence notes | Use as measurement/negative evidence, not as a claim that all such methods fail. |
| C6 | The Direction C v1 corpus structures 21 existing evidence-note surfaces into artifact strata and six-gate labels. | `data/artifact_corpus_v1.csv`, `versions/direction-c-corpus-v1.md` | Structured starter corpus only; not a prevalence claim over all diffusion MIA papers. |
| C7 | The 2026-05-26 Direction C fixed-search batch adds an independent metadata-only selection process over GitHub and arXiv. | `data/artifact_corpus_fixed_search_20260526.csv`, `versions/direction-c-fixed-search-batch-20260526.md` | Selection-process evidence only; it found no new admitted audit row and does not support field-wide prevalence claims. |
| C8 | The selected v1 and fixed-search corpora can be summarized as gate-label counts for claim-control drafting. | `data/artifact_gate_summary.csv`, `figures/artifact_gate_summary.pdf` | Counts describe coded rows in these selected corpora only; not field-wide prevalence or standalone reproducibility evidence. |

## Candidate or Support-Only Claims

| ID | Claim | Evidence | Required wording |
| --- | --- | --- | --- |
| S1 | Tracing the Roots feature tensors contain membership signal. | AUC `0.815826`, TPR@1%FPR `0.134000` | "positive feature-packet evidence", not admitted Platform/Runtime evidence. |
| S2 | SecMI/NNS support the importance of gray-box trajectory signals. | SecMI stat AUC `0.885833`; NNS AUC `0.946286` | "supporting reference", not admitted row. |
| S3 | Collaborator SD ReDiffuse is replayable but source-confounded. | AUC `0.710319`; source-only AUC `1.000000` | "cross-source stress test", not same-distribution membership. |
| S4 | Quantile diffusion public scores are useful same-family support. | CIFAR10 AUC `0.843853`; CIFAR100 AUC `0.782126` | "SecMI-style support packet", not official Quantile Regression result. |

## Prohibited Claims

| ID | Claim not allowed | Reason |
| --- | --- | --- |
| P1 | DiffAudit proves general membership inference for all diffusion models. | Current evidence is permission- and asset-bound. |
| P2 | H2 output-cloud geometry is a new admitted black-box product row. | img2img portability is weak/unstable and no consumer contract exists. |
| P3 | ReDiffuse STL-10 disproves ReDiffuse. | The local scout is short-budget and intentionally bounded. |
| P4 | Tracing Roots can be consumed as a raw image audit. | It is feature-packet evidence without raw checkpoint/sample/regeneration assets. |
| P5 | TPR@0.1%FPR values are calibrated sub-percent rates. | They are finite empirical packet readouts. |
| P6 | Direction C v1 proves that most public diffusion MIA artifacts fail. | v1 is selected from existing DiffAudit notes and is not a complete fixed-search corpus. |
| P7 | The fixed-search batch proves the field lacks audit-ready artifacts. | The batch is small, metadata-only, and selected to support claim-boundary measurement, not prevalence estimation. |
| P8 | Gate-summary counts prove public artifact prevalence or reproducibility rates. | The counts summarize selected coded rows only; standalone aggregate claims still require broader or second-review evidence. |
