from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_ARTIFACT = Path("workspaces/defense/artifacts/ib-defended-shadow-training-manifest-20260512.json")
REQUIRED_DOCS = (
    "docs/evidence/ib-defended-shadow-reopen-protocol-20260512.md",
    "docs/evidence/ib-reopen-shadow-reference-guard-20260512.md",
    "docs/evidence/ib-defended-shadow-training-manifest-20260512.md",
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
    if payload.get("schema") != "diffaudit.ib_defended_shadow_training_manifest.v1":
        errors.append(f"unsupported schema: {payload.get('schema')!r}")
    if payload.get("status") != "ready":
        errors.append("status must be ready")
    if payload.get("admitted") is not False:
        errors.append("artifact must not mark I-B admitted")
    if payload.get("gpu_release") != "none":
        errors.append("gpu_release must be none")
    if payload.get("role") != "defended-shadow":
        errors.append("role must be defended-shadow")

    identity = payload.get("identity_contract")
    if not isinstance(identity, dict):
        errors.append("identity_contract must be an object")
    else:
        if identity.get("forget_count") != identity.get("matched_nonmember_count"):
            errors.append("forget_count must equal matched_nonmember_count")
        if identity.get("forget_count") != identity.get("forget_unique_count"):
            errors.append("forget_count must equal forget_unique_count")
        if identity.get("matched_nonmember_count") != identity.get("matched_nonmember_unique_count"):
            errors.append("matched_nonmember_count must equal matched_nonmember_unique_count")
        for key in ("forget_member_index_file", "matched_nonmember_index_file"):
            _validate_portable_path(identity.get(key), f"identity_contract.{key}", errors)

    runtime = payload.get("runtime_contract")
    if not isinstance(runtime, dict):
        errors.append("runtime_contract must be an object")
    else:
        if int(runtime.get("num_steps", 0)) <= 0:
            errors.append("runtime_contract.num_steps must be positive")
        if int(runtime.get("batch_size", 0)) <= 0:
            errors.append("runtime_contract.batch_size must be positive")
        if runtime.get("raw_asset_policy") != "no-git-large-artifacts":
            errors.append("runtime_contract.raw_asset_policy must be no-git-large-artifacts")
        _validate_portable_path(runtime.get("training_workspace_root"), "runtime_contract.training_workspace_root", errors)

    shadow_training = payload.get("shadow_training")
    if not isinstance(shadow_training, list):
        errors.append("shadow_training must be a list")
    elif len(shadow_training) < 2:
        errors.append("shadow_training must contain at least two shadows")
    else:
        seen: set[str] = set()
        for position, entry in enumerate(shadow_training):
            if not isinstance(entry, dict):
                errors.append(f"shadow_training[{position}] must be an object")
                continue
            shadow_id = entry.get("shadow_id")
            if not isinstance(shadow_id, str) or not shadow_id.strip():
                errors.append(f"shadow_training[{position}].shadow_id must be non-empty")
            elif shadow_id in seen:
                errors.append(f"duplicate shadow_id: {shadow_id}")
            else:
                seen.add(shadow_id)
            if entry.get("status") != "ready":
                errors.append(f"shadow_training[{position}].status must be ready")
            if entry.get("training_role") != "defended-shadow":
                errors.append(f"shadow_training[{position}].training_role must be defended-shadow")
            for key in ("member_dataset_dir", "checkpoint_root", "output_workspace"):
                _validate_portable_path(entry.get(key), f"shadow_training[{position}].{key}", errors)

    for claim in (
        "admitted defense evidence",
        "adaptive robustness",
        "Platform/Runtime defense row",
        "GPU packet completed",
    ):
        if claim not in (payload.get("blocked_claims") or []):
            errors.append(f"missing blocked claim: {claim}")

    for requirement in (
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

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate_ib_defended_shadow_training_manifest",
        description="Validate the I-B defended-shadow training manifest preflight.",
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
