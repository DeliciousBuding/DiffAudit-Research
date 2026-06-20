"""Export the anonymous supplement packet for the evidence paper."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path


ZIP_ROOT = "diffaudit-evidence-paper"
ZIP_TIMESTAMP = (2026, 6, 7, 0, 0, 0)
TEXT_SUFFIXES = {".bib", ".csv", ".json", ".md", ".tex", ".txt"}
PRIVATE_SURFACE_PATTERNS = [
    r"(?<![A-Za-z0-9_])[A-Za-z]:(?:\\\\|\\)[A-Za-z0-9_. -]",
    r"\\Users\\[A-Za-z0-9_. -]",
    r"/home/[A-Za-z0-9_. -]",
    r"/mnt/[A-Za-z0-9_. -]",
    r"OPENAI_API_KEY",
    r"sk-[A-Za-z0-9_-]{12,}",
]


@dataclass(frozen=True)
class SupplementItem:
    category: str
    rel_path: str
    source_path: Path
    archive_name: str
    size_bytes: int
    sha256: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def normalize_manifest_relpath(rel_path: str, errors: list[str]) -> str:
    rel = rel_path.replace("\\", "/")
    require(bool(rel), "empty manifest path", errors)
    require(not rel.startswith("/"), f"absolute manifest path is not allowed: {rel_path!r}", errors)
    require(".." not in Path(rel).parts, f"parent traversal is not allowed: {rel_path!r}", errors)
    return rel


def scan_text_for_private_surface(path: Path, rel_path: str, errors: list[str]) -> None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return
    text = path.read_text(encoding="utf-8", errors="replace")
    for pattern in PRIVATE_SURFACE_PATTERNS:
        require(
            not re.search(pattern, text, flags=re.IGNORECASE),
            f"{rel_path} contains private-surface pattern: {pattern}",
            errors,
        )


def load_manifest(paper: Path, errors: list[str]) -> dict:
    manifest_path = paper / "asset_manifest.json"
    require(manifest_path.exists(), "asset_manifest.json is missing", errors)
    if not manifest_path.exists():
        return {}
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def collect_items(paper: Path, manifest: dict, errors: list[str]) -> list[SupplementItem]:
    requested: list[tuple[str, str]] = []
    excluded: set[str] = set()
    raw_excluded = manifest.get("anonymous_supplement_excluded", [])
    require(isinstance(raw_excluded, list), "asset_manifest.json anonymous_supplement_excluded must be a list", errors)
    if isinstance(raw_excluded, list):
        excluded = {normalize_manifest_relpath(str(path), errors) for path in raw_excluded}
    for category in ("generated", "curated", "paper_sources"):
        paths = manifest.get(category)
        require(isinstance(paths, list), f"asset_manifest.json missing list: {category}", errors)
        if isinstance(paths, list):
            requested.extend((category, path) for path in paths)
    requested.extend(
        [
            ("release_file", "asset_manifest.json"),
            ("release_file", "paper.pdf"),
        ]
    )

    seen_archive_names: set[str] = set()
    items: list[SupplementItem] = []
    for category, raw_rel in requested:
        rel = normalize_manifest_relpath(str(raw_rel), errors)
        if rel in excluded:
            continue
        source_path = paper / rel
        require(source_path.exists(), f"supplement source path is missing: {rel}", errors)
        if not source_path.exists():
            continue
        scan_text_for_private_surface(source_path, rel, errors)
        archive_name = f"{ZIP_ROOT}/{rel}"
        require(archive_name not in seen_archive_names, f"duplicate archive path: {archive_name}", errors)
        seen_archive_names.add(archive_name)
        items.append(
            SupplementItem(
                category=category,
                rel_path=rel,
                source_path=source_path,
                archive_name=archive_name,
                size_bytes=source_path.stat().st_size,
                sha256=sha256_file(source_path),
            )
        )
    return sorted(items, key=lambda item: item.archive_name)


def manifest_rows(items: list[SupplementItem]) -> list[dict[str, str]]:
    return [
        {
            "category": item.category,
            "source_path": item.rel_path,
            "archive_name": item.archive_name,
            "size_bytes": str(item.size_bytes),
            "sha256": item.sha256,
        }
        for item in items
    ]


def write_manifest_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = ["category", "source_path", "archive_name", "size_bytes", "sha256"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_zip(zip_path: Path, items: list[SupplementItem], supplement_manifest: Path) -> str:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for item in items:
            info = zipfile.ZipInfo(item.archive_name, date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, item.source_path.read_bytes())
        info = zipfile.ZipInfo(f"{ZIP_ROOT}/SUPPLEMENT_MANIFEST.csv", date_time=ZIP_TIMESTAMP)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(info, supplement_manifest.read_bytes())
    return sha256_file(zip_path)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_output_zip(zip_path: Path, supplement_manifest: Path, items: list[SupplementItem], errors: list[str]) -> None:
    sha_path = zip_path.with_name(f"{zip_path.name}.sha256")
    require(zip_path.exists(), f"supplement ZIP is missing: {zip_path}", errors)
    require(supplement_manifest.exists(), f"supplement manifest is missing: {supplement_manifest}", errors)
    require(sha_path.exists(), f"supplement sha256 file is missing: {sha_path}", errors)
    if not zip_path.exists() or not supplement_manifest.exists():
        return

    expected_rows = manifest_rows(items)
    actual_rows = read_csv(supplement_manifest)
    require(actual_rows == expected_rows, "supplement manifest does not match current asset_manifest inputs", errors)

    expected_entries = {row["archive_name"] for row in expected_rows}
    expected_entries.add(f"{ZIP_ROOT}/SUPPLEMENT_MANIFEST.csv")
    with zipfile.ZipFile(zip_path, "r") as archive:
        archive_entries = set(archive.namelist())
        require(archive_entries == expected_entries, "supplement ZIP entries do not match current asset_manifest inputs", errors)
        for item in items:
            payload = archive.read(item.archive_name)
            require(str(len(payload)) == str(item.size_bytes), f"{item.archive_name} size drifted in ZIP", errors)
            require(hashlib.sha256(payload).hexdigest() == item.sha256, f"{item.archive_name} sha256 drifted in ZIP", errors)
        require(
            archive.read(f"{ZIP_ROOT}/SUPPLEMENT_MANIFEST.csv") == supplement_manifest.read_bytes(),
            "ZIP SUPPLEMENT_MANIFEST.csv does not match local supplement manifest",
            errors,
        )

    if sha_path.exists():
        expected_sha = sha_path.read_text(encoding="utf-8").split()[0]
        require(sha256_file(zip_path) == expected_sha, "supplement sha256 file does not match ZIP bytes", errors)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the supplement input set without writing the ZIP.",
    )
    parser.add_argument(
        "--check-output",
        action="store_true",
        help="Validate the existing ZIP, manifest, and sha256 against current inputs.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output ZIP path. Defaults to GONE - re-run export_paper_supplement.py to regenerate (was: papers/diffaudit-evidence-paper/build/anonymous-supplement.zip).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    paper = repo_root / "papers" / "diffaudit-evidence-paper"
    errors: list[str] = []

    manifest = load_manifest(paper, errors)
    items = collect_items(paper, manifest, errors) if manifest else []
    require(bool(items), "supplement item list is empty", errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    output = args.output or (paper / "build" / "diffaudit-evidence-paper-anonymous-supplement.zip")
    supplement_manifest = output.parent / "anonymous_supplement_manifest.csv"

    if args.check_output:
        validate_output_zip(output, supplement_manifest, items, errors)
        if errors:
            for error in errors:
                print(f"ERROR: {error}")
            raise SystemExit(1)
        print(f"Anonymous supplement output check passed ({len(items)} files).")
        return

    if args.check:
        print(f"Anonymous supplement export check passed ({len(items)} files).")
        return

    output.parent.mkdir(parents=True, exist_ok=True)
    rows = manifest_rows(items)
    write_manifest_csv(supplement_manifest, rows)
    zip_sha = write_zip(output, items, supplement_manifest)
    sha_path = output.with_name(f"{output.name}.sha256")
    sha_path.write_text(f"{zip_sha}  {output.name}\n", encoding="utf-8")

    print(f"Wrote {output}")
    print(f"Wrote {supplement_manifest}")
    print(f"Wrote {sha_path}")
    print(f"Supplement files: {len(items)}")
    print(f"SHA256: {zip_sha}")


if __name__ == "__main__":
    main()
