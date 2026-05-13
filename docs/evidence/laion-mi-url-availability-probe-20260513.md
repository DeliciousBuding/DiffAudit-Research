# LAION-mi URL Availability Probe

> Date: 2026-05-13
> Status: fixed `25/25` probe failed / metadata-only watch / no GPU release

## Taste Check

This probe executes the smallest follow-up from
[laion-mi-asset-verdict-20260513.md](laion-mi-asset-verdict-20260513.md). It
does not download a large image set, generate responses, or invoke Stable
Diffusion. It only checks whether the public URL/caption metadata can yield a
balanced tiny query set.

## Probe Contract

| Field | Value |
| --- | --- |
| Dataset | `antoniaaa/laion_mi` |
| Splits | `members`, `nonmembers` |
| Fixed subset | first `25` rows from each split |
| Network action | `HEAD`, with fallback `GET` range `bytes=0-4095` |
| Success criterion | HTTP `2xx/3xx` with `Content-Type` starting `image/` |
| Stored payloads | none |

## Result

| Split | Checked | Image OK | Image OK rate |
| --- | ---: | ---: | ---: |
| `members` | `25` | `11` | `0.44` |
| `nonmembers` | `25` | `16` | `0.64` |

Failure classes were mixed: `403`, `404`, `401`, `410`, `503`, HTML responses,
and TLS/timeout failures. Some `200` responses were HTML rather than image
payloads, so they are not usable as query images.

## Decision

`fixed 25/25 probe failed / metadata-only watch / no GPU release`.

LAION-mi remains useful as a paper-backed metadata asset, but the current public
URLs do not recover enough balanced images for the promised fixed `25/25` tiny
packet. The line therefore does not move to response generation, scorer design,
or GPU execution.

Smallest valid reopen condition:

- A cached or mirrored image subset with public-safe provenance for both
  splits, or a later URL probe policy that predefines a larger deterministic
  scan and still freezes the final recovered `25/25` subset before scoring.

Stop condition:

- Do not build response-generation tooling around live LAION-mi URLs. Without a
  recoverable fixed query set, the asset stays `metadata-only watch`.

## Platform and Runtime Impact

None. This remains Research-only negative intake evidence and does not modify
admitted product rows.
