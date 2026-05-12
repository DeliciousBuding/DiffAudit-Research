# External Diffusion Benchmark Provenance Scan

> Date: 2026-05-12
> Status: needs provenance / no GPU release

## Question

After MNIST/DDPM raw-loss, `x0` residual, and tiny known-split raw-loss sanity
all failed to give useful signal, the next good route is not another same-family
MSE variant. A higher-value route is an external diffusion benchmark with
documented target-model training membership.

This scan asks whether obvious Hugging Face diffusion candidates can be used as
a true second membership benchmark without inventing provenance.

## Candidate Scan

| Candidate | Dataset claim | Membership provenance status | Decision |
| --- | --- | --- | --- |
| `1aurent/ddpm-mnist` | MNIST DDPM | Semantically cleaner because MNIST train/test split can be used, but simple raw-loss and `x0` residual scouts are weak. | Keep only if a sharper mechanism appears. |
| Fashion-MNIST DDPM/UNet candidates | Model cards indicate Fashion-MNIST-style training. | Cards found in this quick scan do not clearly freeze the exact training split or prove test images were held out from target training. | Not ready as a true benchmark. |
| CelebA DDPM candidates | Some cards point to CelebA generation. | At least one model card leaves training-data details incomplete; CelebA identity/partition files exist locally, but model training membership is not proven by that alone. | Not ready as a true benchmark. |
| Generic CIFAR-10 DDPM checkpoints | Often advertised as CIFAR-10 DDPM. | CIFAR-10 is already the old asset family, and public checkpoint cards/discussions do not always prove train-only membership. | Do not use as the second benchmark. |

## Rule

Do not treat "trained on dataset X" as enough. For a true membership benchmark,
the project needs one of:

1. A model card or paper that explicitly states the target was trained only on a
   known split and leaves a known held-out split unused.
2. A locally trained/fine-tuned target where the project controls and records
   the member and nonmember identities.
3. A response contract from a model provider or collaborator that ships target
   model identity, member/nonmember query identities, responses, and provenance.

## Verdict

`needs provenance / no GPU release`.

The scan did not find an immediately usable external second benchmark. That is
useful because it prevents a common overclaim: using a dataset label as a
membership label. The next external-benchmark step should be acquisition or
paper/model-card vetting, not scoring.

Route decision:

- Do not download large external weights until provenance is clear.
- Do not use Fashion-MNIST/CelebA/CIFAR cards as true membership evidence based
  only on dataset names.
- If no external target has provenance, the project needs a controlled
  known-split target plus a sharper mechanism than raw denoising MSE.

## Platform and Runtime Impact

None. This scan changes Research route selection only and does not change
admitted product rows.
