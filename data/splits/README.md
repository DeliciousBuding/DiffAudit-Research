# Data Splits

Member/nonmember split indices for reproducible MIA evaluation.

## What These Are

Each `.npz` file contains a fixed random split of a dataset's training set
into member and nonmember subsets at the specified ratio (default 0.5 = 50/50).
The splits are generated once and frozen for reproducibility across all
experiments.

## Contents

| File | Dataset | Size | Member | Nonmember |
|------|---------|------|--------|-----------|
| `CIFAR10_train_ratio0.5.npz` | CIFAR-10 | 392 KB | 25,000 | 25,000 |
| `CIFAR100_train_ratio0.5.npz` | CIFAR-100 | 392 KB | 25,000 | 25,000 |
| `STL10_train_ratio0.5.npz` | STL-10 | 782 KB | 50,000 | 50,000 |

## How Generated

Splits are created by `scripts/util/bootstrap_research_env.py` during
environment setup and committed to Git for reproducibility.

## Consumers

| Script | Uses |
|--------|------|
| `scripts/e2/*.py` | External evaluation freeze preflight |
| `scripts/h1/*.py` | Activation subspace scouts |
| `scripts/h2/*.py` | Score-vector sidecar and output-cloud geometry |
| `scripts/e3/*.py` | Calibration evaluation |
| `scripts/black-box/*.py` | Black-box response contract scouts |
| `scripts/gray-box/*.py` | Gray-box tri-score and PIA |
| `scripts/white-box/*.py` | White-box GSA and influence |
| `scripts/defense/*.py` | Defense training and evaluation |
