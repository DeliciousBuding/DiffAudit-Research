"""Build the signed Paper 1 corrected-evidence protocol manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

from diffaudit.evidence.corrected_protocol import (
    build_paper1_corrected_contract,
    build_protocol_envelope,
    load_member_nonmember_indices,
    verify_paper1_contract,
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_cifar10_train_targets(dataset_root: Path) -> Sequence[int]:
    from torchvision.datasets import CIFAR10

    dataset = CIFAR10(root=str(dataset_root), train=True, download=False)
    return dataset.targets


def build_corrected_protocol(
    *,
    split_path: str | Path,
    dataset_root: str | Path,
    code_commit: str,
) -> dict[str, object]:
    """Build an envelope from a complete split and local CIFAR10 targets."""

    normalized_split_path = Path(split_path)
    split = load_member_nonmember_indices(normalized_split_path, dataset_size=50_000)
    targets = _load_cifar10_train_targets(Path(dataset_root))
    contract = build_paper1_corrected_contract(
        split_filename=normalized_split_path.name,
        split_sha256=_sha256_file(normalized_split_path),
        member_indices=split.member_indices,
        nonmember_indices=split.nonmember_indices,
        class_labels=targets,
        code_commit=code_commit,
    )
    envelope = build_protocol_envelope(contract)
    verify_paper1_contract(
        envelope,
        split_path=normalized_split_path,
        class_labels=targets,
    )
    return envelope


def write_protocol_envelope(
    output: str | Path,
    envelope: dict[str, object],
    *,
    force: bool,
) -> bool:
    """Write an indented envelope, preserving identical existing content."""

    output_path = Path(output)
    if output_path.exists():
        try:
            existing = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            existing = None
        if existing == envelope:
            return False
        if not force:
            raise FileExistsError(
                f"{output_path} already contains different content; pass --force to replace it"
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(envelope, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return True


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the signed Paper 1 corrected-evidence protocol manifest."
    )
    parser.add_argument("--split-path", required=True, type=Path)
    dataset_group = parser.add_mutually_exclusive_group(required=True)
    dataset_group.add_argument("--dataset-root", dest="dataset_root", type=Path)
    dataset_group.add_argument("--cifar10-root", dest="dataset_root", type=Path)
    parser.add_argument("--code-commit", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--force", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    envelope = build_corrected_protocol(
        split_path=args.split_path,
        dataset_root=args.dataset_root,
        code_commit=args.code_commit,
    )
    wrote = write_protocol_envelope(args.output, envelope, force=args.force)
    print(f"{'Wrote' if wrote else 'Unchanged'} {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
