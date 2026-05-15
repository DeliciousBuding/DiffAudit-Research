from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_ARTIFACT = Path("workspaces/defense/artifacts/ib-shadow-local-gsa-risk-preflight-20260515.json")
REQUIRED_DOCS = (
    "docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md",
    "docs/evidence/ib-reopen-shadow-reference-guard-20260512.md",
    "docs/evidence/ib-defended-shadow-training-manifest-20260512.md",
    "docs/evidence/ib-shadow-local-identity-scout-20260512.md",
    "docs/evidence/ib-shadow-local-gsa-risk-preflight-20260515.md",
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
    if payload.get("schema") != "diffaudit.ib_shadow_local_gsa_risk_preflight.v1":
        errors.append(f"unsupported schema: {payload.get('schema')!r}")
    if payload.get("status") != "blocked":
        errors.append("status must remain blocked because PIA shadow-local risk is missing")
    if payload.get("preflight_status") != "complete":
        errors.append("preflight_status must be complete")
    if payload.get("gsa_risk_status") not in {"complete", "insufficient-shadow-coverage"}:
        errors.append("gsa_risk_status must be complete or insufficient-shadow-coverage")
    if payload.get("admitted") is not False:
        errors.append("artifact must not mark I-B admitted")
    if payload.get("gpu_release") != "none":
        errors.append("gpu_release must be none")
    if payload.get("contract_semantics") != "true-shadow-local-gsa-only-risk-scoring":
        errors.append("contract_semantics must preserve GSA-only boundary")
    top_k = int(payload.get("top_k", 0))
    if top_k <= 0:
        errors.append("top_k must be positive")

    _validate_portable_path(payload.get("gsa_loss_score_summary"), "gsa_loss_score_summary", errors)
    artifact_paths = payload.get("artifact_paths")
    if not isinstance(artifact_paths, dict):
        errors.append("artifact_paths must be an object")
    else:
        _validate_portable_path(artifact_paths.get("summary"), "artifact_paths.summary", errors)

    provenance = payload.get("risk_record_provenance")
    if not isinstance(provenance, dict):
        errors.append("risk_record_provenance must be an object")
    else:
        if provenance.get("true_shadow_local_gsa_risk_scoring") is not True:
            errors.append("true_shadow_local_gsa_risk_scoring must be true")
        if provenance.get("true_shadow_local_pia_gsa_risk_scoring") is not False:
            errors.append("true_shadow_local_pia_gsa_risk_scoring must be false")
        if provenance.get("semantic_origin") != "shadow checkpoint scored against its own shadow member/nonmember split":
            errors.append("risk_record_provenance.semantic_origin must identify shadow-local GSA scoring")
        _validate_portable_path(provenance.get("gsa_loss_score_summary"), "risk_record_provenance.gsa_loss_score_summary", errors)

    gsa_ready_shadows = payload.get("gsa_ready_shadows")
    if not isinstance(gsa_ready_shadows, list):
        errors.append("gsa_ready_shadows must be a list")
        gsa_ready_shadows = []
    elif payload.get("gsa_risk_status") == "complete" and len(gsa_ready_shadows) < 2:
        errors.append("complete gsa_risk_status requires at least two GSA-ready shadows")

    entries = payload.get("shadow_risk_preflight")
    if not isinstance(entries, list):
        errors.append("shadow_risk_preflight must be a list")
    else:
        seen: set[str] = set()
        for position, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"shadow_risk_preflight[{position}] must be an object")
                continue
            shadow_id = entry.get("shadow_id")
            if not isinstance(shadow_id, str) or not shadow_id.strip():
                errors.append(f"shadow_risk_preflight[{position}].shadow_id must be non-empty")
            elif shadow_id in seen:
                errors.append(f"duplicate shadow_id: {shadow_id}")
            else:
                seen.add(shadow_id)
            entry_status = entry.get("status")
            if entry_status not in {"gsa-risk-ready", "blocked"}:
                errors.append(f"shadow_risk_preflight[{position}].status must be gsa-risk-ready or blocked")
            counts = entry.get("risk_record_counts")
            if not isinstance(counts, dict):
                errors.append(f"shadow_risk_preflight[{position}].risk_record_counts must be an object")
            else:
                required = int(counts.get("required_per_split", 0))
                if required <= 0:
                    errors.append(f"shadow_risk_preflight[{position}].required_per_split must be positive")
                if entry_status == "gsa-risk-ready":
                    if int(counts.get("unique_member", 0)) < required:
                        errors.append(f"shadow_risk_preflight[{position}].unique_member count is below required")
                    if int(counts.get("unique_nonmember", 0)) < required:
                        errors.append(f"shadow_risk_preflight[{position}].unique_nonmember count is below required")
                    if int(counts.get("unique_nonmember_disjoint_from_forget", 0)) < required:
                        errors.append(
                            f"shadow_risk_preflight[{position}].unique_nonmember_disjoint_from_forget count is below required"
                        )
            for key in ("candidate_forget_member_indices", "candidate_matched_nonmember_indices"):
                indices = entry.get(key)
                if not isinstance(indices, list):
                    errors.append(f"shadow_risk_preflight[{position}].{key} must be a list")
                elif len(indices) != len({int(value) for value in indices}):
                    errors.append(f"shadow_risk_preflight[{position}].{key} must contain unique IDs")
            forget_ids = entry.get("candidate_forget_member_indices")
            matched_ids = entry.get("candidate_matched_nonmember_indices")
            if isinstance(forget_ids, list) and isinstance(matched_ids, list):
                if {int(value) for value in forget_ids} & {int(value) for value in matched_ids}:
                    errors.append(
                        f"shadow_risk_preflight[{position}] candidate forget and matched nonmember IDs must be disjoint"
                    )
            paths = entry.get("artifact_paths")
            if not isinstance(paths, dict):
                errors.append(f"shadow_risk_preflight[{position}].artifact_paths must be an object")
            else:
                for key in (
                    "member_risk_records",
                    "nonmember_risk_records",
                    "forget_member_index_file",
                    "matched_nonmember_index_file",
                ):
                    value = paths.get(key)
                    _validate_portable_path(value, f"shadow_risk_preflight[{position}].artifact_paths.{key}", errors)

    for claim in (
        "true shadow-local PIA/GSA risk scoring",
        "defended-shadow training release",
        "admitted defense evidence",
        "adaptive robustness",
        "Platform/Runtime defense row",
        "GPU packet completed",
    ):
        if claim not in (payload.get("blocked_claims") or []):
            errors.append(f"missing blocked claim: {claim}")

    for requirement in (
        "produce shadow-local PIA risk records or explicitly approve GSA-only defended-shadow semantics",
        "write fixed per-shadow forget and matched-nonmember identity files only after semantic approval",
        "execute tiny defended-shadow training",
        "export defended-shadow threshold references",
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

    if "shadow-local PIA risk records are still missing from the defended-shadow contract" not in (
        payload.get("errors") or []
    ):
        errors.append("artifact must preserve the missing PIA risk-record blocker")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate_ib_shadow_local_gsa_risk_preflight",
        description="Validate the I-B shadow-local GSA-only risk preflight artifact.",
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
