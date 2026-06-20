from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .gitinfo import detect_git
from .hashing import hash_tree, sha256_bytes, sha256_file
from .model import TreeHash
from .util import CheckResult, host_info, json_dumps_canonical, now_iso_local, norm_abs


def _hash_config(config_path: Path) -> tuple[dict[str, Any], str]:
    config_path = config_path.resolve()
    if config_path.is_file():
        content_sha = sha256_file(config_path)
        payload = {
            "kind": "file",
            "path": str(config_path),
            "algorithm": "sha256",
            "sha256": content_sha,
            "size": int(config_path.stat().st_size),
        }
        return payload, content_sha

    files, tree_sha = hash_tree(config_path)
    tree = TreeHash(
        root=str(config_path),
        algorithm="sha256",
        file_count=len(files),
        tree_sha256=tree_sha,
        files=files,
    )
    payload = {"kind": "dir", **tree.to_json()}
    return payload, tree_sha


def run_gate(
    *,
    config_path: Path,
    member_split_root: Path,
    repo_root: Path,
    strict: bool = False,
) -> tuple[CheckResult, dict[str, Any], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []

    config_path = config_path.resolve()
    member_split_root = member_split_root.resolve()
    repo_root = repo_root.resolve()

    if not config_path.exists():
        errors.append(f"config does not exist: {config_path}")

    if not member_split_root.exists() or not member_split_root.is_dir():
        errors.append(f"member_split_root is not an existing directory: {member_split_root}")

    if not repo_root.exists() or not repo_root.is_dir():
        errors.append(f"repo_root is not an existing directory: {repo_root}")

    git = detect_git(repo_root)
    if strict:
        if not git.available:
            errors.append("git is not available on PATH but --strict was set")
        elif not git.is_repo:
            errors.append("repo_root is not a git work tree but --strict was set")
        elif git.commit is None:
            errors.append("could not read git commit but --strict was set")
        elif git.dirty:
            errors.append("repo_root has uncommitted changes but --strict was set")
    else:
        if git.available and git.is_repo and git.dirty:
            warnings.append("repo_root has uncommitted changes (git status not clean)")

    # PIA-specific: expected member split file
    split_file = member_split_root / "CIFAR10_train_ratio0.5.npz"
    if member_split_root.exists() and not split_file.exists():
        warnings.append("expected member split file missing: CIFAR10_train_ratio0.5.npz")

    config_payload: dict[str, Any] | None = None
    config_hash: str | None = None
    if config_path.exists() and (config_path.is_file() or config_path.is_dir()):
        config_payload, config_hash = _hash_config(config_path)

    member_split_files: list[Any] = []
    member_split_tree_sha: str | None = None
    if member_split_root.exists() and member_split_root.is_dir():
        files, tree_sha = hash_tree(member_split_root)
        member_split_files = [f.to_json() for f in files]
        member_split_tree_sha = tree_sha

    ok = len(errors) == 0
    if strict and not ok:
        warnings = []

    check = CheckResult(ok=ok, errors=errors, warnings=warnings)

    manifest: dict[str, Any] = {
        "schema": "pia_next_run.manifest.v1",
        "created_at": now_iso_local(),
        "paths": {
            "config": norm_abs(config_path),
            "member_split_root": norm_abs(member_split_root),
            "repo_root": norm_abs(repo_root),
        },
        "inputs": {
            "config": config_payload,
            "config_sha256": config_hash,
            "member_split_root": {
                "algorithm": "sha256",
                "root": str(member_split_root),
                "file_count": len(member_split_files),
                "tree_sha256": member_split_tree_sha,
                "files": member_split_files,
            },
        },
        "git": git.to_json(),
        "validation": check.to_json(),
    }

    manifest_sha256 = sha256_bytes(json_dumps_canonical(manifest))

    provenance: dict[str, Any] = {
        "schema": "pia_next_run.provenance.v1",
        "created_at": now_iso_local(),
        "manifest_sha256": manifest_sha256,
        "host": host_info(),
        "validation": check.to_json(),
    }

    return check, manifest, provenance


def write_outputs(*, out_dir: Path, manifest: dict[str, Any], provenance: dict[str, Any]) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.json"
    provenance_path = out_dir / "provenance.json"

    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path, provenance_path
