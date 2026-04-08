# 2026-04-08 Unified Attack-Defense Table

## 主基线

- dataset: `CIFAR-10`
- model family: `DDPM`
- scope: `current admitted main results only`

## 当前统一总表

| track | attack | defense | model | AUC | ASR | TPR@1%FPR | TPR@0.1%FPR | quality/cost | evidence level | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| black-box | `recon DDIM public-100 step30` | `none` | `Stable Diffusion v1.5 + DDIM` | `0.849` | `0.51` | `1.0` | `n/a` | `100 public samples; runtime-mainline` | `runtime-mainline` | current black-box main evidence |
| gray-box | `PIA GPU512 baseline` | `none` | `CIFAR-10 DDPM` | `0.841339` | `0.786133` | `0.058594` | `0.011719` | `512 samples per split; 171.214752s` | `runtime-mainline` | current gray-box baseline reference |
| gray-box | `PIA GPU512 baseline` | `provisional G-1 = stochastic-dropout` | `CIFAR-10 DDPM` | `0.82938` | `0.769531` | `0.023438` | `0.009766` | `512 samples per split; 131.89636s` | `runtime-mainline` | current gray-box defended main result |
| white-box | `GSA 1k-3shadow` | `none` | `CIFAR-10 DDPM` | `0.97514` | `0.919` | `0.55` | `0.205` | `1k target eval + 3 shadows` | `runtime-mainline` | current white-box attack main evidence |
| white-box | `GSA 1k-3shadow` | `W-1 strong-v3 full-scale` | `DPDM / Diffusion-DP` | `0.488783` | `0.4985` | `0.009` | `0.0` | `full-scale defended comparator` | `runtime-smoke` | current white-box defended main result |
| white-box | `GSA 1k-3shadow` | `W-1 strong-v2 full-scale` | `DPDM / Diffusion-DP` | `0.490813` | `0.496` | `0.006` | `0.0` | `full-scale defended comparator` | `runtime-smoke` | defended reference rung kept for comparison |

## 当前解释口径

- This table only contains the current main evidence rows, not every historical run.
- `variation / Towards` is intentionally excluded here because it remains a formal local secondary track rather than the current black-box main evidence.
- `SecMI` is intentionally excluded here because it is now a `blocked baseline`.
- `provisional G-1` means the defense signal is consistent across `GPU128 / GPU256 / GPU512`, but still lacks same-scale repeat confirmation and paper-aligned provenance.
- `W-1 strong-v3 full-scale` is the current white-box defended main result; `strong-v2 full-scale` remains in-table as the direct comparison rung.
