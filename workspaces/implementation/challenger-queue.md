# DiffAudit Research — Challenger Queue

> **Last refreshed**: 2026-04-17
> **Purpose**: Keep the innovation funnel aligned with current repo truth after closure-round reviews
> **Rule**: This queue is for future candidate generation, bounded follow-up, or asset-triggered reopen only. It is not a substitute for admitted/mainline status.

---

## Current Queue Truth

- `active GPU question = none`
- gray-box currently has no immediate next-family execution lane
- white-box currently has no immediate next-hypothesis execution lane
- the next live CPU-first priority should therefore move to:
  - `distinct white-box defended-family import / selection`

This queue should now be read with three distinctions:

1. `ready-for-selection`
   - honest CPU-first candidate-generation or review work
2. `hold / not-requestable`
   - real line exists, but current repo truth says do not schedule execution
3. `needs-assets`
   - may still be valuable, but cannot honestly progress without new data/models/contracts

---

## Top 3 Priorities

### 1. `WB-CH-1` Distinct white-box defended-family import / selection

- `status`: `ready-for-selection`
- `expected value`: ⭐⭐
- `mode`: `CPU-only candidate generation`
- `why now`:
  - `DP-LoRA` is already bounded and frozen below new GPU release
  - `GSA2` is same-family corroboration only
  - `Finding NeMo` is still `not-requestable`

### 2. `GB-CH-2` Ranking-sensitive variable search

- `status`: `ready-for-selection`
- `expected value`: ⭐⭐
- `mode`: `CPU-only hypothesis writing`
- `why next`:
  - it stays within gray-box without reopening dead latent-diffusion branches
  - it can still generate a bounded disagreement question without forcing GPU first

### 3. `XB-CH-2` Transfer / portability probes

- `status`: `needs-assets`
- `expected value`: ⭐⭐
- `mode`: `asset-triggered review`
- `why third`:
  - still potentially valuable cross-box
  - but it remains below ready CPU-only selection because honest contracts are still missing

---

## Current Candidates

### Black-box

#### `BB-CH-1` Caption/semantic-family refresh

- `status`: `reviewed / closed-negative`
- `expected value`: ⭐
- `reason`:
  - the refresh review found no honest ready next-family promotion candidate
  - visible options collapse into same-family continuation, boundary-only work, needs-assets, or gray-box-owned audit expansion
  - do not reopen black-box candidate generation unless a real new family or asset/boundary shift appears

#### `BB-CH-2` Variation real-asset unblock

- `status`: `needs-assets`
- `expected value`: ⭐⭐
- `blocker`:
  - `query_image_root / query images`
  - plus endpoint/proxy, budget, and frozen parameters

#### `BB-CH-3` Semantic-auxiliary-classifier scoring follow-up

- `status`: `hold`
- `expected value`: ⭐
- `reason`:
  - current scoring/fusion review already closed as `negative but useful`
  - do not reopen without a genuinely new feature-family hypothesis

### Gray-box

#### `GB-CH-1` Second gray-box defense mechanism

- `status`: `reviewed / selected`
- `expected value`: ⭐⭐
- `note`:
  - selected mechanism is `TMIA-DM late-window + temporal-striding(stride=2)`
  - keep it as the second gray-box defense mechanism, not as a project-wide replacement defense
  - do not reopen gray-box defense selection unless a genuinely different mechanism appears

#### `GB-CH-2` Ranking-sensitive variable search

- `status`: `ready-for-selection`
- `expected value`: ⭐⭐
- `note`:
  - keep below release until a concrete disagreement/ranking hypothesis is written

#### `GB-CH-3` Noise as a Probe latent-diffusion promotion path

- `status`: `hold`
- `expected value`: ⭐
- `reason`:
  - promotion-gap review already closed negatively
  - contract-shift review also closed negatively
  - do not reopen unless a real contract shift appears

### White-box

#### `WB-CH-1` Distinct defended-family import / selection

- `status`: `ready-for-selection`
- `expected value`: ⭐⭐
- `note`:
  - this is candidate generation only
  - not `DP-LoRA` reruns
  - not `GSA2` scale-up
  - not `Finding NeMo` reopen under current contract

#### `WB-CH-2` `Finding NeMo`

- `status`: `not-requestable`
- `expected value`: ⭐⭐
- `reason`:
  - protocol mismatch on current admitted assets
  - still held under separate future reconsideration boundary

#### `WB-CH-3` `GSA2`

- `status`: `hold`
- `expected value`: ⭐
- `reason`:
  - positive same-family corroboration already exists
  - does not create a new white-box family

### Cross-box

#### `XB-CH-1` Cross-threat-model agreement follow-up

- `status`: `hold`
- `expected value`: ⭐⭐
- `reason`:
  - current agreement review already landed positively
  - reopen only if a new box-level verdict changes the project narrative

#### `XB-CH-2` Transfer / portability probes

- `status`: `needs-assets`
- `expected value`: ⭐⭐
- `reason`:
  - still lacks honest paired model/dataset contracts

---

## Negative / Closed Items To Not Reopen Blindly

- `PIA + SecMI` naive fusion
- `Recon + CLiD` fusion
- `structural memorization` under current faithful approximation
- `Noise as a Probe` defended-extension on current `SD1.5` contract
- immediate latent-diffusion same-surface board for `Noise as a Probe`
- white-box defense breadth on the current candidate set

---

## Recommended Next Order

1. `WB-CH-1` distinct white-box defended-family import / selection
2. `GB-CH-2` ranking-sensitive variable search
3. `XB-CH-2` transfer / portability probes

This order is deliberately CPU-first and does **not** authorize any new GPU run by itself.
