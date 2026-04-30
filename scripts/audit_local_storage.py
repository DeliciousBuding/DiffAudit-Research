"""Audit and optionally relocate large local-only Research assets.

The default mode is read-only. Use ``--execute`` to move ignored local assets
out of the Research checkout and leave junctions/symlinks behind for existing
local commands.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from pathlib import Path


HEAVY_RUN_DIR_NAMES = {
    "bridged-model",
    "checkpoint-final",
    "checkpoints",
    "datasets",
    "generated",
    "generated-images",
    "score-artifacts",
}

LOCAL_PATH_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("local DiffAudit Windows path", re.compile(r"D:(?:\\+|/+)+Code(?:\\+|/+)+DiffAudit")),
    ("local Ding Windows path", re.compile(r"C:(?:\\+|/+)+Users(?:\\+|/+)+Ding")),
    ("local Ding WSL path", re.compile(r"/mnt/c/Users/" + "Ding", re.IGNORECASE)),
)

LOCAL_PATH_SCAN_EXCLUDE_DIRS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
}

LOCAL_PATH_SCAN_EXCLUDE_FILES = {
    "scripts/check_public_surface.py",
}

LOCAL_PATH_TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".jsonl",
    ".log",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class MoveCandidate:
    category: str
    source: str
    target: str
    size_mb: float
    tracked_files: int
    action: str
    reason: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _size_bytes(path: Path) -> int:
    if _is_link_or_reparse(path):
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    for current, dirnames, filenames in os.walk(path, topdown=True, followlinks=False):
        current_path = Path(current)
        kept_dirs = []
        for dirname in dirnames:
            child = current_path / dirname
            if not _is_link_or_reparse(child):
                kept_dirs.append(dirname)
        dirnames[:] = kept_dirs
        for filename in filenames:
            item = current_path / filename
            try:
                if not _is_link_or_reparse(item):
                    total += item.stat().st_size
            except OSError:
                continue
    return total


def _to_mb(size: int) -> float:
    return round(size / (1024 * 1024), 2)


def _rel(path: Path, root: Path) -> str:
    return path.absolute().relative_to(root.absolute()).as_posix()


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.absolute().relative_to(parent.absolute())
        return True
    except ValueError:
        return False


def _is_link_or_reparse(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attrs = path.lstat().st_file_attributes
    except (AttributeError, OSError):
        return False
    return bool(attrs & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def _tracked_files(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        text=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    return {p.decode("utf-8", errors="replace") for p in result.stdout.split(b"\0") if p}


def _tracked_files_under(path: Path, root: Path, tracked_files: set[str]) -> list[str]:
    rel = path.absolute().relative_to(root.absolute()).as_posix().rstrip("/")
    prefix = rel + "/"
    return sorted(p for p in tracked_files if p == rel or p.startswith(prefix))


def _add_candidate(
    candidates: list[MoveCandidate],
    *,
    root: Path,
    source: Path,
    target: Path,
    category: str,
    reason: str,
    min_mb: float,
    tracked_files: set[str],
) -> None:
    if not source.exists():
        return
    size = _size_bytes(source)
    if _to_mb(size) < min_mb:
        return
    tracked = _tracked_files_under(source, root, tracked_files)
    action = "move_and_link"
    if _is_link_or_reparse(source):
        action = "already_linked"
    elif tracked:
        action = "blocked_tracked_files"
    elif target.exists():
        action = "preserve_source_and_link_existing_target"
    candidates.append(
        MoveCandidate(
            category=category,
            source=_rel(source, root),
            target=str(target.resolve()),
            size_mb=_to_mb(size),
            tracked_files=len(tracked),
            action=action,
            reason=reason,
        )
    )


def _whitebox_asset_candidates(
    root: Path,
    archive_root: Path,
    min_mb: float,
    tracked_files: set[str],
) -> list[MoveCandidate]:
    candidates: list[MoveCandidate] = []
    base = root / "workspaces" / "white-box" / "assets"
    if not base.exists():
        return candidates
    for child in base.iterdir():
        if not child.is_dir():
            continue
        if child.name == "gsa":
            sources = [child / "checkpoints"]
        else:
            sources = [child]
        for source in sources:
            _add_candidate(
                candidates,
                root=root,
                source=source,
                target=archive_root / _rel(source, root),
                category="generated_artifact",
                reason="white-box checkpoints and local training assets do not belong inside the Git checkout",
                min_mb=min_mb,
                tracked_files=tracked_files,
            )
    return candidates


def _graybox_asset_candidates(
    root: Path,
    download_root: Path,
    min_mb: float,
    tracked_files: set[str],
) -> list[MoveCandidate]:
    specs = [
        (
            root / "workspaces" / "gray-box" / "assets" / "pia" / "sources",
            download_root / "gray-box" / "supplementary" / "pia-upstream-assets" / "raw",
            "misplaced_raw_asset",
            "PIA source archives belong in Download raw intake",
        ),
        (
            root / "workspaces" / "gray-box" / "assets" / "pia" / "checkpoints",
            download_root / "gray-box" / "supplementary" / "pia-upstream-assets" / "contents" / "checkpoints",
            "misplaced_raw_asset",
            "PIA upstream checkpoints belong in Download raw intake",
        ),
        (
            root / "workspaces" / "gray-box" / "assets" / "pia" / "datasets",
            download_root / "gray-box" / "supplementary" / "pia-upstream-assets" / "contents" / "datasets",
            "misplaced_raw_asset",
            "PIA upstream dataset payloads belong in Download raw intake",
        ),
        (
            root / "workspaces" / "gray-box" / "assets" / "secmi" / "sources",
            download_root / "gray-box" / "supplementary" / "secmi-onedrive" / "raw",
            "misplaced_raw_asset",
            "SecMI source archives belong in Download raw intake",
        ),
        (
            root / "workspaces" / "gray-box" / "assets" / "secmi" / "checkpoints",
            download_root / "gray-box" / "weights" / "secmi-cifar-bundle" / "contents" / "checkpoints",
            "misplaced_raw_asset",
            "SecMI checkpoints belong in Download canonical weights",
        ),
    ]
    candidates: list[MoveCandidate] = []
    for source, target, category, reason in specs:
        _add_candidate(
            candidates,
            root=root,
            source=source,
            target=target,
            category=category,
            reason=reason,
            min_mb=min_mb,
            tracked_files=tracked_files,
        )
    return candidates


def _run_artifact_candidates(
    root: Path,
    archive_root: Path,
    min_mb: float,
    tracked_files: set[str],
) -> list[MoveCandidate]:
    candidates: list[MoveCandidate] = []
    runs_root = root / "workspaces"
    if not runs_root.exists():
        return candidates
    for lane_runs in runs_root.glob("*/runs"):
        if not lane_runs.is_dir():
            continue
        for item in lane_runs.rglob("*"):
            if not item.is_dir():
                continue
            if item.name not in HEAVY_RUN_DIR_NAMES:
                continue
            _add_candidate(
                candidates,
                root=root,
                source=item,
                target=archive_root / _rel(item, root),
                category="generated_artifact",
                reason="large run payloads are local artifacts; Git keeps summaries and verdicts",
                min_mb=min_mb,
                tracked_files=tracked_files,
            )
    return candidates


def _scratch_candidates(
    root: Path,
    archive_root: Path,
    min_mb: float,
    tracked_files: set[str],
) -> list[MoveCandidate]:
    candidates: list[MoveCandidate] = []
    for base_name in ("outputs", "tmp"):
        base = root / base_name
        if not base.exists():
            continue
        for child in base.iterdir():
            if not child.is_dir():
                continue
            _add_candidate(
                candidates,
                root=root,
                source=child,
                target=archive_root / _rel(child, root),
                category="cache_tmp",
                reason=f"{base_name}/ is local scratch and should not be a Research handoff surface",
                min_mb=min_mb,
                tracked_files=tracked_files,
            )
    return candidates


def _external_bloat(root: Path, min_mb: float) -> list[dict[str, object]]:
    external = root / "external"
    if not external.exists():
        return []
    findings: list[dict[str, object]] = []
    for child in external.iterdir():
        if not child.is_dir():
            continue
        size_mb = _to_mb(_size_bytes(child))
        if size_mb < min_mb:
            continue
        findings.append(
            {
                "category": "external_clone_bloat",
                "path": _rel(child, root),
                "size_mb": size_mb,
                "action": "review_only",
                "reason": "external clones are allowed, but weights/caches inside them should be moved separately",
            }
        )
    return findings


def collect_candidates(
    root: Path,
    min_mb: float,
    archive_subdir: str | None = None,
) -> tuple[list[MoveCandidate], list[dict[str, object]]]:
    diffaudit_root = root.parent
    download_root = diffaudit_root / "Download"
    archive_root = _archive_root(root, archive_subdir)
    tracked_files = _tracked_files(root)
    candidates: list[MoveCandidate] = []
    candidates.extend(_graybox_asset_candidates(root, download_root, min_mb, tracked_files))
    candidates.extend(_whitebox_asset_candidates(root, archive_root, min_mb, tracked_files))
    candidates.extend(_run_artifact_candidates(root, archive_root, min_mb, tracked_files))
    candidates.extend(_scratch_candidates(root, archive_root, min_mb, tracked_files))
    return candidates, _external_bloat(root, min_mb)


def _default_archive_subdir() -> str:
    return date.today().isoformat()


def _archive_root(root: Path, archive_subdir: str | None) -> Path:
    subdir = archive_subdir or _default_archive_subdir()
    return root.parent / "Archive" / "research-local-artifacts" / subdir


def _make_link(source: Path, target: Path) -> None:
    if os.name == "nt":
        try:
            os.symlink(target, source, target_is_directory=target.is_dir())
            return
        except OSError:
            # Developer Mode or privilege policy may block directory symlinks.
            # Fall back to a junction, which is the most compatible Windows
            # repair link for local research asset directories.
            pass
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(source), str(target)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    else:
        source.symlink_to(target, target_is_directory=target.is_dir())


def _execute_candidate(root: Path, candidate: MoveCandidate, archive_root: Path) -> dict[str, object]:
    source = (root / candidate.source).absolute()
    target = Path(candidate.target).resolve()
    allowed_target_roots = [root.parent / "Download", root.parent / "Archive"]
    if not _is_within(source, root):
        raise RuntimeError(f"Refusing to move outside repo root: {source}")
    if not any(_is_within(target, allowed) for allowed in allowed_target_roots):
        raise RuntimeError(f"Refusing target outside Download/Archive: {target}")
    if candidate.tracked_files:
        return {**asdict(candidate), "executed": False, "result": "blocked_tracked_files"}
    if candidate.action == "already_linked" or _is_link_or_reparse(source):
        return {**asdict(candidate), "executed": False, "result": "already_linked"}
    if not source.exists():
        return {**asdict(candidate), "executed": False, "result": "source_missing"}

    if target.exists():
        preserve = archive_root / "preserved-source-conflicts" / candidate.source
        preserve.parent.mkdir(parents=True, exist_ok=True)
        if preserve.exists():
            return {**asdict(candidate), "executed": False, "result": "preserve_target_exists"}
        shutil.move(str(source), str(preserve))
        try:
            _make_link(source, target)
        except Exception:
            shutil.move(str(preserve), str(source))
            raise
        return {
            **asdict(candidate),
            "executed": True,
            "result": "preserved_source_and_linked_existing_target",
            "preserved_source": str(preserve.resolve()),
        }

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), str(target))
    try:
        _make_link(source, target)
    except Exception:
        shutil.move(str(target), str(source))
        raise
    return {**asdict(candidate), "executed": True, "result": "moved_and_linked"}


def _tracked_large_files(root: Path, min_mb: float) -> list[dict[str, object]]:
    result = subprocess.run(
        ["git", "ls-tree", "-r", "-l", "HEAD"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return []
    findings: list[dict[str, object]] = []
    for line in result.stdout.splitlines():
        parts = line.split(None, 4)
        if len(parts) != 5 or parts[3] == "-":
            continue
        size_mb = _to_mb(int(parts[3]))
        if size_mb >= min_mb:
            findings.append({"path": parts[4], "size_mb": size_mb})
    return findings


def _local_path_leaks(root: Path) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for current, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        dirnames[:] = [
            dirname for dirname in dirnames if dirname not in LOCAL_PATH_SCAN_EXCLUDE_DIRS
        ]
        current_path = Path(current)
        for filename in filenames:
            file_path = current_path / filename
            if file_path.suffix.lower() not in LOCAL_PATH_TEXT_SUFFIXES:
                continue
            try:
                rel = _rel(file_path, root)
            except ValueError:
                continue
            if rel in LOCAL_PATH_SCAN_EXCLUDE_FILES:
                continue
            try:
                lines = file_path.open(encoding="utf-8", errors="strict")
            except OSError:
                continue
            with lines:
                try:
                    for line_number, line in enumerate(lines, start=1):
                        for label, pattern in LOCAL_PATH_PATTERNS:
                            if pattern.search(line):
                                findings.append(
                                    {
                                        "path": rel,
                                        "line": line_number,
                                        "category": label,
                                    }
                                )
                                break
                except UnicodeDecodeError:
                    continue
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(_repo_root()), help="Research repository root")
    parser.add_argument("--min-mb", type=float, default=10.0, help="minimum size included in the audit")
    parser.add_argument(
        "--archive-subdir",
        default=None,
        help="subdirectory under Archive/research-local-artifacts; defaults to current date",
    )
    parser.add_argument("--execute", action="store_true", help="move local-only candidates and leave links")
    parser.add_argument("--json-out", default=None, help="optional JSON report path")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    archive_root = _archive_root(root, args.archive_subdir)
    candidates, external = collect_candidates(root, args.min_mb, args.archive_subdir)
    payload: dict[str, object] = {
        "schema": "diffaudit.local_storage_audit.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "min_mb": args.min_mb,
        "tracked_large_files": _tracked_large_files(root, args.min_mb),
        "move_candidates": [asdict(candidate) for candidate in candidates],
        "external_clone_bloat": external,
        "local_path_leaks": _local_path_leaks(root),
    }

    if args.execute:
        payload["executions"] = [
            _execute_candidate(root, candidate, archive_root) for candidate in candidates
        ]

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
