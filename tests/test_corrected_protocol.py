from __future__ import annotations

import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

import diffaudit.evidence as evidence
from diffaudit.evidence.corrected_protocol import (
    MembershipSplit,
    ProtocolRow,
    build_stratified_row_manifest,
    canonical_protocol_hash,
    derive_noise_seed,
    derive_training_seeds,
    load_member_nonmember_indices,
)


def _write_split(
    path: Path,
    *,
    member: object = (0, 2, 4),
    nonmember: object = (1, 3, 5),
) -> None:
    np.savez(
        path,
        mia_train_idxs=np.asarray(member),
        mia_eval_idxs=np.asarray(nonmember),
    )


def _balanced_row_inputs(
    per_class_per_group: int = 120,
) -> tuple[tuple[int, ...], tuple[int, ...], np.ndarray]:
    member_indices: list[int] = []
    nonmember_indices: list[int] = []
    class_labels: list[int] = []
    for class_id in range(10):
        member_start = len(class_labels)
        class_labels.extend([class_id] * per_class_per_group)
        member_indices.extend(range(member_start, len(class_labels)))

        nonmember_start = len(class_labels)
        class_labels.extend([class_id] * per_class_per_group)
        nonmember_indices.extend(range(nonmember_start, len(class_labels)))
    return tuple(member_indices), tuple(nonmember_indices), np.asarray(class_labels)


def test_load_member_nonmember_indices_reads_valid_split(tmp_path: Path) -> None:
    split_path = tmp_path / "split.npz"
    _write_split(split_path)

    split = load_member_nonmember_indices(split_path, dataset_size=6)

    assert split == MembershipSplit(
        member_indices=(0, 2, 4),
        nonmember_indices=(1, 3, 5),
    )


def test_load_member_nonmember_indices_resolves_supported_dataset(tmp_path: Path) -> None:
    split_path = tmp_path / "CIFAR10_train_ratio0.5.npz"
    _write_split(split_path)

    split = load_member_nonmember_indices(split_root=tmp_path, dataset="cifar10")

    assert split.member_indices == (0, 2, 4)


def test_load_member_nonmember_indices_rejects_unsupported_dataset(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="Unsupported dataset.*imagenet"):
        load_member_nonmember_indices(split_root=tmp_path, dataset="imagenet")


def test_load_member_nonmember_indices_requires_both_keys(tmp_path: Path) -> None:
    split_path = tmp_path / "split.npz"
    np.savez(split_path, mia_train_idxs=np.asarray([0, 1]))

    with pytest.raises(ValueError, match="missing required key.*mia_eval_idxs"):
        load_member_nonmember_indices(split_path)


@pytest.mark.parametrize(
    ("member", "nonmember", "dataset_size", "message"),
    [
        ([[0, 1]], [2, 3], None, "mia_train_idxs must be one-dimensional"),
        ([0, 0], [2, 3], None, "mia_train_idxs contains duplicate indices"),
        ([0, 1], [1, 2], None, "member and nonmember indices overlap"),
        ([-1, 0], [1, 2], None, "indices must be non-negative"),
        ([0, 1], [2, 6], 6, "indices must be smaller than dataset_size=6"),
    ],
)
def test_load_member_nonmember_indices_rejects_invalid_indices(
    tmp_path: Path,
    member: object,
    nonmember: object,
    dataset_size: int | None,
    message: str,
) -> None:
    split_path = tmp_path / "split.npz"
    _write_split(split_path, member=member, nonmember=nonmember)

    with pytest.raises(ValueError, match=message):
        load_member_nonmember_indices(split_path, dataset_size=dataset_size)


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {"split_path": "split.npz", "split_root": "splits", "dataset": "cifar10"},
    ],
)
def test_load_member_nonmember_indices_requires_exactly_one_source(
    arguments: dict[str, object],
) -> None:
    with pytest.raises(ValueError, match="exactly one of split_path or split_root"):
        load_member_nonmember_indices(**arguments)


def test_load_member_nonmember_indices_rejects_noninteger_arrays(tmp_path: Path) -> None:
    split_path = tmp_path / "split.npz"
    _write_split(split_path, member=[0.5, 1.5], nonmember=[2, 3])

    with pytest.raises(ValueError, match="mia_train_idxs must contain integers"):
        load_member_nonmember_indices(split_path)


def test_derive_training_seeds_is_stable_and_material_sensitive() -> None:
    seeds = derive_training_seeds("paper1-corrected-evidence")

    assert seeds == derive_training_seeds("paper1-corrected-evidence")
    assert seeds != derive_training_seeds("paper1-corrected-evidence-other")


def test_derive_training_seeds_returns_unique_positive_31_bit_integers() -> None:
    seeds = derive_training_seeds("paper1-corrected-evidence")

    assert len(seeds) == 8
    assert len(set(seeds)) == 8
    assert all(isinstance(seed, int) and 0 < seed < 2**31 for seed in seeds)
    assert len(derive_training_seeds("paper1-corrected-evidence", count=3)) == 3


def test_derive_training_seeds_rejects_nonpositive_count() -> None:
    with pytest.raises(ValueError, match="count must be positive"):
        derive_training_seeds("paper1-corrected-evidence", count=0)


def test_derive_training_seeds_is_stable_across_processes() -> None:
    code = (
        "from diffaudit.evidence.corrected_protocol import derive_training_seeds; "
        "print(','.join(map(str, derive_training_seeds('paper1-corrected-evidence'))))"
    )
    outputs = []
    for python_hash_seed in ("1", "8675309"):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = python_hash_seed
        env["PYTHONPATH"] = str(Path("src").resolve())
        outputs.append(
            subprocess.check_output(
                [sys.executable, "-c", code],
                env=env,
                text=True,
            ).strip()
        )

    assert outputs[0] == outputs[1]


def test_build_stratified_row_manifest_freezes_balanced_disjoint_rows() -> None:
    member_indices, nonmember_indices, class_labels = _balanced_row_inputs()

    rows = build_stratified_row_manifest(
        member_indices,
        nonmember_indices,
        class_labels,
        random_state=20260711,
    )

    assert len(rows) == 2048
    assert all(isinstance(row, ProtocolRow) for row in rows)
    assert len({row.dataset_index for row in rows}) == len(rows)
    for label, source_indices in ((1, member_indices), (0, nonmember_indices)):
        for split_name in ("calibration", "evaluation"):
            selected = [row for row in rows if row.label == label and row.split == split_name]
            class_counts = Counter(row.class_id for row in selected)
            assert len(selected) == 512
            assert set(class_counts) == set(range(10))
            assert max(class_counts.values()) - min(class_counts.values()) <= 1
            assert {row.dataset_index for row in selected} <= set(source_indices)
            assert all(class_labels[row.dataset_index] == row.class_id for row in selected)


def test_build_stratified_row_manifest_is_deterministic() -> None:
    member_indices, nonmember_indices, class_labels = _balanced_row_inputs()

    first = build_stratified_row_manifest(
        member_indices,
        nonmember_indices,
        class_labels,
        random_state=42,
    )
    repeated = build_stratified_row_manifest(
        member_indices,
        nonmember_indices,
        class_labels,
        random_state=42,
    )
    changed = build_stratified_row_manifest(
        member_indices,
        nonmember_indices,
        class_labels,
        random_state=43,
    )

    assert first == repeated
    assert first != changed


def test_build_stratified_row_manifest_rejects_insufficient_input() -> None:
    member_indices, nonmember_indices, class_labels = _balanced_row_inputs(per_class_per_group=100)

    with pytest.raises(ValueError, match="member.*requires at least 1024 rows"):
        build_stratified_row_manifest(
            member_indices,
            nonmember_indices,
            class_labels,
            random_state=42,
        )


def test_build_stratified_row_manifest_rejects_membership_overlap() -> None:
    member_indices, nonmember_indices, class_labels = _balanced_row_inputs()
    overlapping_nonmember = (member_indices[0], *nonmember_indices[1:])

    with pytest.raises(ValueError, match="member and nonmember indices overlap"):
        build_stratified_row_manifest(
            member_indices,
            overlapping_nonmember,
            class_labels,
            random_state=42,
        )


def test_build_stratified_row_manifest_rejects_duplicate_indices() -> None:
    member_indices, nonmember_indices, class_labels = _balanced_row_inputs()
    duplicate_member = (member_indices[0], member_indices[0], *member_indices[2:])

    with pytest.raises(ValueError, match="member indices contain duplicates"):
        build_stratified_row_manifest(
            duplicate_member,
            nonmember_indices,
            class_labels,
            random_state=42,
        )


def test_build_stratified_row_manifest_rejects_negative_indices() -> None:
    member_indices, nonmember_indices, class_labels = _balanced_row_inputs()
    negative_member = (-1, *member_indices[1:])

    with pytest.raises(ValueError, match="indices must be non-negative"):
        build_stratified_row_manifest(
            negative_member,
            nonmember_indices,
            class_labels,
            random_state=42,
        )


def test_build_stratified_row_manifest_rejects_uncovered_indices() -> None:
    member_indices, nonmember_indices, class_labels = _balanced_row_inputs()
    uncovered_member = (len(class_labels), *member_indices[1:])

    with pytest.raises(ValueError, match="class_labels does not cover dataset index"):
        build_stratified_row_manifest(
            uncovered_member,
            nonmember_indices,
            class_labels,
            random_state=42,
        )


def test_build_stratified_row_manifest_requires_one_dimensional_labels() -> None:
    member_indices, nonmember_indices, class_labels = _balanced_row_inputs()

    with pytest.raises(ValueError, match="class_labels must be one-dimensional"):
        build_stratified_row_manifest(
            member_indices,
            nonmember_indices,
            class_labels[:, None],
            random_state=42,
        )


def test_derive_noise_seed_is_stable_positive_63_bit_integer() -> None:
    seed = derive_noise_seed("paper1-corrected-v1", 123, 500, 7)

    assert seed == derive_noise_seed("paper1-corrected-v1", 123, 500, 7)
    assert isinstance(seed, int)
    assert 0 < seed < 2**63


@pytest.mark.parametrize(
    "arguments",
    [
        ("paper1-corrected-v2", 123, 500, 7),
        ("paper1-corrected-v1", 124, 500, 7),
        ("paper1-corrected-v1", 123, 501, 7),
        ("paper1-corrected-v1", 123, 500, 8),
    ],
)
def test_derive_noise_seed_binds_every_protocol_coordinate(
    arguments: tuple[str, int, int, int],
) -> None:
    baseline = derive_noise_seed("paper1-corrected-v1", 123, 500, 7)

    assert derive_noise_seed(*arguments) != baseline


def test_canonical_protocol_hash_ignores_recursive_mapping_key_order() -> None:
    first = {
        "version": 1,
        "rows": [{"split": "calibration", "dataset_index": 7}],
        "counts": {"nonmember": 512, "member": 512},
    }
    reordered = {
        "counts": {"member": 512, "nonmember": 512},
        "rows": [{"dataset_index": 7, "split": "calibration"}],
        "version": 1,
    }

    digest = canonical_protocol_hash(first)

    assert digest == canonical_protocol_hash(reordered)
    assert len(digest) == 64
    assert all(character in "0123456789abcdef" for character in digest)


def test_canonical_protocol_hash_changes_when_a_value_changes() -> None:
    baseline = {"version": 1, "counts": {"member": 512}}
    changed = {"version": 1, "counts": {"member": 513}}

    assert canonical_protocol_hash(baseline) != canonical_protocol_hash(changed)


@pytest.mark.parametrize(
    "absolute_path",
    [
        f"{'C'}:{chr(92)}private{chr(92)}model.ckpt",
        "/" + "private/model.ckpt",
    ],
)
def test_canonical_protocol_hash_rejects_nested_absolute_paths(absolute_path: str) -> None:
    manifest = {"protocol": {"artifacts": [{"path": absolute_path}]}}

    with pytest.raises(ValueError, match="absolute paths are not allowed"):
        canonical_protocol_hash(manifest)


def test_canonical_protocol_hash_allows_relative_public_paths() -> None:
    digest = canonical_protocol_hash({"split": "data/splits/cifar10.npz"})

    assert len(digest) == 64


def test_evidence_package_exports_corrected_protocol_primitives() -> None:
    expected = {
        "MembershipSplit",
        "ProtocolRow",
        "build_stratified_row_manifest",
        "canonical_protocol_hash",
        "derive_noise_seed",
        "derive_training_seeds",
        "load_member_nonmember_indices",
    }

    assert set(evidence.__all__) == expected
    assert all(hasattr(evidence, name) for name in expected)
