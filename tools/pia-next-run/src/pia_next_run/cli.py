from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .gate import run_gate, write_outputs


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pia-next-run",
        description="Validate PIA next-run intake and emit manifest+provenance JSON.",
    )
    p.add_argument("--config", required=True, type=Path, help="PIA runtime config file or directory.")
    p.add_argument("--member-split-root", required=True, type=Path, help="Directory containing member split files.")
    p.add_argument("--repo-root", required=True, type=Path, help="Repository root for the run (used for git provenance).")
    p.add_argument(
        "--out-dir",
        type=Path,
        default=Path("."),
        help="Output directory for manifest.json and provenance.json (default: current directory).",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Fail if git is unavailable, repo_root is not a git work tree, or repo is dirty.",
    )
    p.add_argument(
        "--stdout",
        action="store_true",
        help="Print manifest+provenance JSON to stdout instead of writing files.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    check, manifest, provenance = run_gate(
        config_path=args.config,
        member_split_root=args.member_split_root,
        repo_root=args.repo_root,
        strict=bool(args.strict),
    )

    if args.stdout:
        payload = {"manifest": manifest, "provenance": provenance}
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    else:
        manifest_path, provenance_path = write_outputs(out_dir=args.out_dir, manifest=manifest, provenance=provenance)
        sys.stdout.write(f"OK={str(check.ok).lower()} manifest={manifest_path} provenance={provenance_path}\n")
        if check.errors:
            for e in check.errors:
                sys.stdout.write(f"ERROR {e}\n")
        if check.warnings:
            for w in check.warnings:
                sys.stdout.write(f"WARN {w}\n")

    return 0 if check.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
