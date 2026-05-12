# True Second Membership Benchmark Scope

> Date: 2026-05-12
> Status: scope frozen; no GPU release

## Taste Check

This note exists to stop the next cycle from polishing weak or semantically
invalid directions. It is not a new tool request and it does not authorize a
larger experiment.

The current Research question is simple: can the attack signal transfer outside
the old DDPM/CIFAR10 loop on a second benchmark with real membership semantics?

## What Counts

A true second membership benchmark must have all of the following:

1. Known target model or generator identity.
2. Known member set used to train or fine-tune that target model.
3. Known nonmember set that was held out from that target model.
4. Query and response contract that can be reproduced or audited.
5. A first scorer whose result can change the next route decision.

If the split is only a dataset train/validation split, but not a model-training
membership split, it is not a membership benchmark.

## Candidate Status

| Candidate | Status | Reason |
| --- | --- | --- |
| Beans/SD1.5 | contract/debug only | The package has real beans queries and local SD1.5 responses, but beans train/validation is not proven membership in SD1.5 training data. |
| MNIST/DDPM via `1aurent/ddpm-mnist` | semantically valid, raw-loss weak | MNIST train/test gives cleaner member/nonmember semantics for the public DDPM, but the `16 / 16` raw PIA-style loss scout was near-random and the per-timestep guard peaked only at `AUC = 0.578125`. |
| Pokemon/Kandinsky skeleton | invalid for now | Local material is weights-only and lacks real query split, response manifest, and response coverage. |
| SD1.5/CelebA simple-distance family | not a second benchmark | It is the same asset family as existing simple-distance evidence and should not be used as the portability answer. |

## Next Valid Experiment

The smallest useful next step is one of:

1. A new MNIST/DDPM scorer that is not raw noise-prediction MSE, with a frozen
   reason it could expose a different signal.
2. A tiny self-trained or fine-tuned diffusion target with an explicit
   train/held-out split, then one simple scorer on a small fixed sample.
3. A real external response contract where the model-training member and
   nonmember sets are documented.

Do not run another Beans/SD1.5 pixel or CLIP-distance variant. Do not expand the
MNIST/DDPM raw-loss table. Do not start GPU until the benchmark has true
membership semantics, a metric contract, and a stop condition.

## Decision

The mainline is not blocked by missing code. It is blocked by missing
membership-valid second benchmark evidence.

So the next Research cycle should choose exactly one high-decision-value path:
either design a sharper MNIST/DDPM scorer or construct a tiny known-split target.
Both are better than adding more package validators, route guards, or
same-contract ablations.

## Platform and Runtime Impact

None. This note changes Research routing only and does not modify admitted
Platform/Runtime rows.
