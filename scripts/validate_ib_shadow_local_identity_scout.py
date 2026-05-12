from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_ARTIFACT = Path("workspaces/defense/artifacts/ib-shadow-local-identity-scout-20260512.json")
REQUIRED_DOCS = (
    "docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md",
    "docs/evidence/ib-reopen-shadow-reference-guard-20260512.md",
    "docs/evidence/ib-defended-shadow-training-manifest-20260512.md",
    "docs/evidence/ib-shadow-local-identity-scout-20260512.md",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_portable_path(value: Any, field: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be non-empty")
        return
    if "\\" in value:
        errors.append(f"{field} must use forward slashes")
    if Path(value).is_absolute():
        errors.append(f"{field} must be relative")


def validate(payload: Any, *, repo_root: Path | None = None) -> list[str]:
    repo_root = Path.cwd() if repo_root is None else repo_root
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["artifact must be a JSON object"]
    if payload.get("schema") != "diffaudit.ib_shadow_local_identity_scout.v1":
        errors.append(f"unsupported schema: {payload.get('schema')!r}")
    if payload.get("status") != "blocked":
        errors.append("status must remain blocked because this scout is not true shadow-local risk scoring")
    if payload.get("scout_status") != "complete":
        errors.append("scout_status must be complete")
    if payload.get("mechanical_status") not in {"candidate-contract", "insufficient-shadow-coverage"}:
        errors.append("mechanical_status must be candidate-contract or insufficient-shadow-coverage")
    if payload.get("admitted") is not False:
        errors.append("artifact must not mark I-B admitted")
    if payload.get("gpu_release") != "none":
        errors.append("gpu_release must be none")
    if payload.get("contract_semantics") != "target-risk-filtered-shadow-split-remap":
        errors.append("contract_semantics must preserve remap boundary")
    if int(payload.get("top_k", 0)) <= 0:
        errors.append("top_k must be positive")

    provenance = payload.get("risk_record_provenance")
    if not isinstance(provenance, dict):
        errors.append("risk_record_provenance must be an object")
    else:
        if provenance.get("true_shadow_local_risk_scoring") is not False:
            errors.append("true_shadow_local_risk_scoring must be false")
        if provenance.get("semantic_origin") != "target-level PIA/GSA full-overlap risk records":
            errors.append("risk_record_provenance.semantic_origin must identify target-level records")
        for key in ("member_risk_records_path", "nonmember_risk_records_path"):
            _validate_portable_path(provenance.get(key), f"risk_record_provenance.{key}", errors)

    mechanically_possible = payload.get("mechanically_possible_shadows")
    if not isinstance(mechanically_possible, list):
        errors.append("mechanically_possible_shadows must be a list")
        mechanically_possible = []
    elif payload.get("mechanical_status") == "candidate-contract" and len(mechanically_possible) < 2:
        errors.append("candidate-contract mechanical_status requires at least two mechanically possible shadows")

    entries = payload.get("shadow_identity_scout")
    if not isinstance(entries, list):
        errors.append("shadow_identity_scout must be a list")
    else:
        seen: set[str] = set()
        for position, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"shadow_identity_scout[{position}] must be an object")
                continue
            shadow_id = entry.get("shadow_id")
            if not isinstance(shadow_id, str) or not shadow_id.strip():
                errors.append(f"shadow_identity_scout[{position}].shadow_id must be non-empty")
            elif shadow_id in seen:
                errors.append(f"duplicate shadow_id: {shadow_id}")
            else:
                seen.add(shadow_id)
            entry_status = entry.get("status")
            if entry_status not in {"candidate-contract", "blocked"}:
                errors.append(f"shadow_identity_scout[{position}].status must be candidate-contract or blocked")
            entry_possible = entry.get("mechanically_possible")
            if entry_status == "candidate-contract" and entry_possible is not True:
                errors.append(f"shadow_identity_scout[{position}] candidate-contract must be mechanically_possible")
            if entry_status == "blocked" and entry_possible is True:
                errors.append(f"shadow_identity_scout[{position}] blocked entry must not be mechanically_possible")
            counts = entry.get("target_risk_record_counts")
            if not isinstance(counts, dict):
                errors.append(f"shadow_identity_scout[{position}].target_risk_record_counts must be an object")
            else:
                required = int(counts.get("required_per_split", 0))
                if required <= 0:
                    errors.append(f"shadow_identity_scout[{position}].required_per_split must be positive")
                if entry_status == "candidate-contract":
                    if int(counts.get("member_available", 0)) < required:
                        errors.append(f"shadow_identity_scout[{position}].member_available is below required")
                    if int(counts.get("nonmember_available", 0)) < required:
                        errors.append(f"shadow_identity_scout[{position}].nonmember_available is below required")
            for key in ("member_dataset_dir", "nonmember_dataset_dir", "checkpoint_root"):
                _validate_portable_path(entry.get(key), f"shadow_identity_scout[{position}].{key}", errors)

    for claim in (
        "true shadow-local risk scoring",
        "defended-shadow training release",
        "admitted defense evidence",
        "adaptive robustness",
        "Platform/Runtime defense row",
        "GPU packet completed",
    ):
        if claim not in (payload.get("blocked_claims") or []):
            errors.append(f"missing blocked claim: {claim}")

    for requirement in (
        "produce true shadow-local PIA/GSA risk records or explicitly approve the two-shadow remap semantics",
        "write fixed per-shadow forget and matched-nonmember identity files only after semantic approval",
        "execute tiny defended-shadow training",
        "run explicit defended-shadow reopen review",
        "measure retained utility",
        "show strict-tail improvement under defended-shadow threshold references",
    ):
        if requirement not in (payload.get("remaining_requirements") or []):
            errors.append(f"missing remaining requirement: {requirement}")

    docs = payload.get("evidence_docs")
    if not isinstance(docs, list):
        errors.append("evidence_docs must be a list")
    else:
        for doc in REQUIRED_DOCS:
            if doc not in docs:
                errors.append(f"missing evidence doc: {doc}")
            elif not (repo_root / doc).is_file():
                errors.append(f"evidence doc does not exist: {doc}")

    if not payload.get("errors"):
        errors.append("artifact must include errors preserving semantic blocker")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate_ib_shadow_local_identity_scout",
        description="Validate the I-B shadow-local identity scout artifact.",
    )
    parser.add_argument("--artifact", type=Path, default=None)
    args = parser.parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]
    artifact = args.artifact if args.artifact is not None else repo_root / DEFAULT_ARTIFACT
    if not artifact.is_absolute():
        artifact = repo_root / artifact
    errors = validate(_load_json(artifact), repo_root=repo_root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK {artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
