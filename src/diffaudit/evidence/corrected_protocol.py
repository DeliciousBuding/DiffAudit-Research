"""Corrected-evidence protocol primitives for Paper 1."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Literal

import numpy as np

_SPLIT_FILENAMES = {"cifar10": "CIFAR10_train_ratio0.5.npz"}
_CLASS_IDS = tuple(range(10))


def _digest_parts(*parts: object) -> bytes:
    encoded = "\0".join(str(part) for part in parts).encode("utf-8")
    return hashlib.sha256(encoded).digest()


def _balanced_class_counts(
    count: int,
    *,
    random_state: int,
    membership: str,
    split: str,
) -> dict[int, int]:
    base, remainder = divmod(count, len(_CLASS_IDS))
    class_order = sorted(
        _CLASS_IDS,
        key=lambda class_id: _digest_parts(
            "diffaudit-row-class-order-v1",
            random_state,
            membership,
            split,
            class_id,
        ),
    )
    counts = {class_id: base for class_id in _CLASS_IDS}
    for class_id in class_order[:remainder]:
        counts[class_id] += 1
    return counts


def _reject_absolute_paths(value: object) -> None:
    if isinstance(value, str):
        if PureWindowsPath(value).is_absolute() or PurePosixPath(value).is_absolute():
            raise ValueError("absolute paths are not allowed in public protocol manifests")
        return
    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            _reject_absolute_paths(key)
            _reject_absolute_paths(nested_value)
        return
    if isinstance(value, (list, tuple)):
        for nested_value in value:
            _reject_absolute_paths(nested_value)


@dataclass(frozen=True, slots=True)
class MembershipSplit:
    """Validated member and nonmember dataset indices."""

    member_indices: tuple[int, ...]
    nonmember_indices: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class ProtocolRow:
    """One frozen dataset row in a corrected-evidence protocol split."""

    dataset_index: int
    label: Literal[0, 1]
    class_id: int
    split: Literal["calibration", "evaluation"]


def canonical_protocol_hash(protocol: Mapping[str, object]) -> str:
    """Hash a public-safe protocol mapping using recursive canonical JSON."""

    _reject_absolute_paths(protocol)
    payload = json.dumps(
        protocol,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def derive_noise_seed(
    protocol_namespace: str,
    dataset_index: int,
    timestep: int,
    draw: int,
) -> int:
    """Derive a stable common-noise seed without generating a tensor."""

    digest = _digest_parts(
        "diffaudit-common-noise-seed-v1",
        protocol_namespace,
        dataset_index,
        timestep,
        draw,
    )
    return int.from_bytes(digest[:8], "big") % (2**63 - 1) + 1


def build_stratified_row_manifest(
    member_indices: Sequence[int],
    nonmember_indices: Sequence[int],
    class_labels: Sequence[int],
    *,
    n_calibration_per_group: int = 512,
    n_evaluation_per_group: int = 512,
    random_state: int,
) -> tuple[ProtocolRow, ...]:
    """Build deterministic class-stratified calibration and evaluation rows."""

    member = tuple(int(index) for index in member_indices)
    nonmember = tuple(int(index) for index in nonmember_indices)
    labels = np.asarray(class_labels)
    if labels.ndim != 1:
        raise ValueError("class_labels must be one-dimensional")
    for membership, source_indices in (("member", member), ("nonmember", nonmember)):
        if len(set(source_indices)) != len(source_indices):
            raise ValueError(f"{membership} indices contain duplicates")
        if any(index < 0 for index in source_indices):
            raise ValueError("indices must be non-negative")
        if any(index >= labels.size for index in source_indices):
            raise ValueError("class_labels does not cover dataset index")
    if set(member) & set(nonmember):
        raise ValueError("member and nonmember indices overlap")

    total_required = n_calibration_per_group + n_evaluation_per_group
    rows: list[ProtocolRow] = []
    for membership, label, source_indices in (
        ("member", 1, member),
        ("nonmember", 0, nonmember),
    ):
        if len(source_indices) < total_required:
            raise ValueError(f"{membership} group requires at least {total_required} rows")

        calibration_counts = _balanced_class_counts(
            n_calibration_per_group,
            random_state=random_state,
            membership=membership,
            split="calibration",
        )
        evaluation_counts = _balanced_class_counts(
            n_evaluation_per_group,
            random_state=random_state,
            membership=membership,
            split="evaluation",
        )
        pools = {
            class_id: [index for index in source_indices if int(labels[index]) == class_id]
            for class_id in _CLASS_IDS
        }

        for class_id in _CLASS_IDS:
            calibration_count = calibration_counts[class_id]
            evaluation_count = evaluation_counts[class_id]
            required = calibration_count + evaluation_count
            if len(pools[class_id]) < required:
                raise ValueError(
                    f"{membership} class {class_id} requires {required} rows, "
                    f"found {len(pools[class_id])}"
                )
            ranked = sorted(
                pools[class_id],
                key=lambda index: _digest_parts(
                    "diffaudit-row-selection-v1",
                    random_state,
                    membership,
                    class_id,
                    index,
                ),
            )
            rows.extend(
                ProtocolRow(index, label, class_id, "calibration")
                for index in ranked[:calibration_count]
            )
            rows.extend(
                ProtocolRow(index, label, class_id, "evaluation")
                for index in ranked[calibration_count:required]
            )

    return tuple(rows)


def derive_training_seeds(seed_material: str | bytes, count: int = 8) -> tuple[int, ...]:
    """Derive deterministic training seeds from stable seed material."""

    if count <= 0:
        raise ValueError("count must be positive")
    material = seed_material.encode("utf-8") if isinstance(seed_material, str) else seed_material
    seeds: list[int] = []
    seen: set[int] = set()
    counter = 0
    while len(seeds) < count:
        digest = hashlib.sha256(
            b"diffaudit-training-seed-v1\0" + material + b"\0" + counter.to_bytes(8, "big")
        ).digest()
        seed = int.from_bytes(digest[:4], "big") & 0x7FFF_FFFF
        if seed > 0 and seed not in seen:
            seeds.append(seed)
            seen.add(seed)
        counter += 1
    return tuple(seeds)


def load_member_nonmember_indices(
    split_path: str | Path | None = None,
    *,
    split_root: str | Path | None = None,
    dataset: str | None = None,
    dataset_size: int | None = None,
) -> MembershipSplit:
    """Load and validate the canonical member and nonmember index arrays."""

    if (split_path is None) == (split_root is None):
        raise ValueError("provide exactly one of split_path or split_root")
    if split_path is None:
        normalized_dataset = str(dataset).lower()
        if normalized_dataset not in _SPLIT_FILENAMES:
            raise ValueError(f"Unsupported dataset for membership split: {dataset}")
        split_path = Path(split_root) / _SPLIT_FILENAMES[normalized_dataset]

    with np.load(Path(split_path), allow_pickle=False) as payload:
        required_keys = ("mia_train_idxs", "mia_eval_idxs")
        for key in required_keys:
            if key not in payload:
                raise ValueError(f"Membership split is missing required key: {key}")
        member = np.asarray(payload["mia_train_idxs"])
        nonmember = np.asarray(payload["mia_eval_idxs"])

    for key, values in (("mia_train_idxs", member), ("mia_eval_idxs", nonmember)):
        if values.ndim != 1:
            raise ValueError(f"{key} must be one-dimensional")
        if not np.issubdtype(values.dtype, np.integer):
            raise ValueError(f"{key} must contain integers")
        if np.unique(values).size != values.size:
            raise ValueError(f"{key} contains duplicate indices")

    if np.intersect1d(member, nonmember).size:
        raise ValueError("member and nonmember indices overlap")
    if np.any(member < 0) or np.any(nonmember < 0):
        raise ValueError("indices must be non-negative")
    if dataset_size is not None and (
        np.any(member >= dataset_size) or np.any(nonmember >= dataset_size)
    ):
        raise ValueError(f"indices must be smaller than dataset_size={dataset_size}")

    return MembershipSplit(
        member_indices=tuple(int(value) for value in member),
        nonmember_indices=tuple(int(value) for value in nonmember),
    )
