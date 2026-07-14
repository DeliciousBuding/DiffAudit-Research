from __future__ import annotations

import inspect
import json
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
    build_paper1_corrected_contract,
    build_stratified_row_manifest,
    canonical_protocol_hash,
    derive_noise_seed,
    derive_training_seeds,
    load_member_nonmember_indices,
    paper1_pia_contract,
)
from diffaudit.evidence.h1_confirmatory import h1_scorer_contract
from diffaudit.evidence.training_config import build_training_config


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


def _tight_row_inputs() -> tuple[tuple[int, ...], tuple[int, ...], np.ndarray]:
    member_indices: list[int] = []
    nonmember_indices: list[int] = []
    class_labels: list[int] = []
    for class_id, class_count in enumerate((103, 103, 103, 103, 102, 102, 102, 102, 102, 102)):
        member_start = len(class_labels)
        class_labels.extend([class_id] * class_count)
        member_indices.extend(range(member_start, len(class_labels)))

        nonmember_start = len(class_labels)
        class_labels.extend([class_id] * class_count)
        nonmember_indices.extend(range(nonmember_start, len(class_labels)))
    return tuple(member_indices), tuple(nonmember_indices), np.asarray(class_labels)


def _asymmetric_capacity_row_inputs() -> tuple[tuple[int, ...], tuple[int, ...], np.ndarray]:
    member_counts = (103, 103, 103, 103, 103, 103, 102, 102, 102, 102)
    nonmember_counts = (102, 102, 103, 103, 103, 103, 103, 103, 102, 102)
    member_indices: list[int] = []
    nonmember_indices: list[int] = []
    class_labels: list[int] = []
    for class_id, (member_count, nonmember_count) in enumerate(
        zip(member_counts, nonmember_counts, strict=True)
    ):
        member_start = len(class_labels)
        class_labels.extend([class_id] * member_count)
        member_indices.extend(range(member_start, len(class_labels)))

        nonmember_start = len(class_labels)
        class_labels.extend([class_id] * nonmember_count)
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


def test_derive_training_seeds_matches_sha256_known_vector() -> None:
    assert derive_training_seeds("paper1-corrected-evidence") == (
        1746574482,
        1403859882,
        1877216607,
        120492209,
        1624907720,
        761208184,
        1867632528,
        1918927372,
    )


def test_derive_training_seeds_returns_unique_positive_31_bit_integers() -> None:
    seeds = derive_training_seeds("paper1-corrected-evidence")

    assert len(seeds) == 8
    assert len(set(seeds)) == 8
    assert all(isinstance(seed, int) and 0 < seed < 2**31 for seed in seeds)
    assert len(derive_training_seeds("paper1-corrected-evidence", count=3)) == 3


@pytest.mark.parametrize("invalid_count", [1.5, True, 0, -1])
def test_derive_training_seeds_rejects_invalid_count(invalid_count: object) -> None:
    with pytest.raises(ValueError, match="count must be a positive integer"):
        derive_training_seeds(
            "paper1-corrected-evidence",
            count=invalid_count,  # type: ignore[arg-type]
        )


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


def test_build_stratified_row_manifest_uses_feasible_tight_class_capacity() -> None:
    member_indices, nonmember_indices, class_labels = _tight_row_inputs()

    rows = build_stratified_row_manifest(
        member_indices,
        nonmember_indices,
        class_labels,
        random_state=42,
    )

    assert len(rows) == 2048
    for label in (0, 1):
        for split_name in ("calibration", "evaluation"):
            counts = Counter(
                row.class_id for row in rows if row.label == label and row.split == split_name
            )
            assert sum(counts.values()) == 512
            assert max(counts.values()) - min(counts.values()) <= 1


def test_build_stratified_row_manifest_shares_class_counts_across_membership() -> None:
    member_indices, nonmember_indices, class_labels = _balanced_row_inputs()

    rows = build_stratified_row_manifest(
        member_indices,
        nonmember_indices,
        class_labels,
        random_state=42,
    )

    for split_name in ("calibration", "evaluation"):
        member_counts = tuple(
            sum(
                row.label == 1 and row.split == split_name and row.class_id == class_id
                for row in rows
            )
            for class_id in range(10)
        )
        nonmember_counts = tuple(
            sum(
                row.label == 0 and row.split == split_name and row.class_id == class_id
                for row in rows
            )
            for class_id in range(10)
        )
        assert member_counts == nonmember_counts


def test_build_stratified_row_manifest_uses_joint_membership_capacities() -> None:
    member_indices, nonmember_indices, class_labels = _asymmetric_capacity_row_inputs()

    rows = build_stratified_row_manifest(
        member_indices,
        nonmember_indices,
        class_labels,
        random_state=42,
    )

    for split_name in ("calibration", "evaluation"):
        vectors = [
            tuple(
                sum(
                    row.label == label and row.split == split_name and row.class_id == class_id
                    for row in rows
                )
                for class_id in range(10)
            )
            for label in (0, 1)
        ]
        assert vectors[0] == vectors[1]


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


@pytest.mark.parametrize(
    ("member_indices", "nonmember_indices", "message"),
    [
        ((0, 1.9), (2, 3), "member indices must contain integers"),
        ((0, 1), (2, 3.9), "nonmember indices must contain integers"),
        ((0, True), (2, 3), "member indices must contain integers"),
    ],
)
def test_build_stratified_row_manifest_rejects_noninteger_source_indices(
    member_indices: tuple[object, ...],
    nonmember_indices: tuple[object, ...],
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        build_stratified_row_manifest(
            member_indices,  # type: ignore[arg-type]
            nonmember_indices,  # type: ignore[arg-type]
            np.asarray([0, 1, 2, 3]),
            random_state=42,
        )


@pytest.mark.parametrize("invalid_label", [0.9, True])
def test_build_stratified_row_manifest_rejects_noninteger_source_class_labels(
    invalid_label: object,
) -> None:
    labels = np.asarray([invalid_label, 1, 2, 3], dtype=object)

    with pytest.raises(ValueError, match="class_labels for source rows must contain integers"):
        build_stratified_row_manifest((0, 1), (2, 3), labels, random_state=42)


@pytest.mark.parametrize("invalid_label", [-1, 10])
def test_build_stratified_row_manifest_rejects_source_class_ids_outside_cifar10(
    invalid_label: int,
) -> None:
    labels = np.asarray([invalid_label, 1, 2, 3])

    with pytest.raises(ValueError, match="source class IDs must be in range 0..9"):
        build_stratified_row_manifest((0, 1), (2, 3), labels, random_state=42)


@pytest.mark.parametrize(
    ("calibration_count", "evaluation_count", "message"),
    [
        (1.5, 512, "n_calibration_per_group must be a non-negative integer"),
        (True, 512, "n_calibration_per_group must be a non-negative integer"),
        (-1, 512, "n_calibration_per_group must be a non-negative integer"),
        (512, 1.5, "n_evaluation_per_group must be a non-negative integer"),
        (512, False, "n_evaluation_per_group must be a non-negative integer"),
        (512, -1, "n_evaluation_per_group must be a non-negative integer"),
    ],
)
def test_build_stratified_row_manifest_rejects_invalid_counts(
    calibration_count: object,
    evaluation_count: object,
    message: str,
) -> None:
    member_indices, nonmember_indices, class_labels = _balanced_row_inputs()

    with pytest.raises(ValueError, match=message):
        build_stratified_row_manifest(
            member_indices,
            nonmember_indices,
            class_labels,
            n_calibration_per_group=calibration_count,  # type: ignore[arg-type]
            n_evaluation_per_group=evaluation_count,  # type: ignore[arg-type]
            random_state=42,
        )


def test_build_stratified_row_manifest_rejects_zero_total_count() -> None:
    member_indices, nonmember_indices, class_labels = _balanced_row_inputs()

    with pytest.raises(ValueError, match="at least one row count must be positive"):
        build_stratified_row_manifest(
            member_indices,
            nonmember_indices,
            class_labels,
            n_calibration_per_group=0,
            n_evaluation_per_group=0,
            random_state=42,
        )


def test_paper1_corrected_row_manifest_wrapper_freezes_group_sizes() -> None:
    member_indices, nonmember_indices, class_labels = _balanced_row_inputs()
    builder = evidence.build_paper1_corrected_row_manifest

    rows = builder(
        member_indices,
        nonmember_indices,
        class_labels,
        random_state=42,
    )

    assert "n_calibration_per_group" not in inspect.signature(builder).parameters
    assert "n_evaluation_per_group" not in inspect.signature(builder).parameters
    assert len(rows) == 2048
    assert Counter((row.label, row.split) for row in rows) == {
        (1, "calibration"): 512,
        (1, "evaluation"): 512,
        (0, "calibration"): 512,
        (0, "evaluation"): 512,
    }


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
        f"{chr(92)}private{chr(92)}model.ckpt",
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


def test_paper1_h1_contract_freezes_the_legacy_42_dimensional_feature_layout() -> None:
    contract = h1_scorer_contract()

    assert contract["packet_schema_version"] == 1
    assert contract["packet_format"] == "h1-feature-packet-v2"
    assert contract["packet_purposes"] == ["corrected_evaluation", "preflight_benchmark"]
    definition = contract["feature_definition"]
    assert definition["sites"] == ["late_down", "mid_0", "mid_1", "early_up"]
    assert definition["timesteps"] == [100, 400, 700]
    assert definition["channels_per_site"] == {
        "late_down": 256,
        "mid_0": 256,
        "mid_1": 256,
        "early_up": 256,
    }
    assert definition["per_channel_statistics"] == ["mu_abs", "var", "sparsity"]
    assert definition["scalar_statistics"] == [
        "mu_abs_mean",
        "var_mean",
        "sparsity_mean",
    ]
    assert definition["pca_input_dimension"] == 9216
    assert definition["scalar_feature_dimension"] == 36
    assert definition["lr_input_dimension"] == 42
    assert definition["pca_feature_order"] == "site_then_timestep_then_statistic_then_channel"
    assert definition["scalar_feature_order"] == "timestep_then_site_then_statistic"
    assert definition["lr_feature_order"] == ["scalar_features", "pca_components"]
    extraction = contract["extraction"]
    assert extraction["batch_size"] == 16
    assert extraction["device_policy"] == "cuda_required_for_confirmatory"
    assert extraction["determinism"] == dict(build_training_config().determinism)
    assert set(extraction["evaluator_environment"]) == {
        "python",
        "pytorch",
        "cuda",
        "cudnn",
        "gpu_name",
        "gpu_uuid",
    }


def test_paper1_pia_contract_freezes_one_outcome_blind_preflight_identity() -> None:
    contract = paper1_pia_contract()

    assert contract["packet_purposes"] == [
        "corrected_evaluation",
        "preflight_benchmark",
    ]
    assert contract["preflight_identity"] == {
        "run_seed": 1746574482,
        "step": 2_000,
    }
    extraction = contract["extraction"]
    assert extraction["batch_size"] == 8
    assert extraction["device"] == "cpu"
    assert extraction["weights_key"] == "ema"
    assert set(extraction["evaluator_environment"]) == {
        "os",
        "platform",
        "machine",
        "cpu_model",
        "python",
        "pytorch",
        "torch_num_threads",
        "torch_num_interop_threads",
        "blas_backend",
        "mkl_available",
        "mkldnn_available",
        "openmp_available",
        "omp_num_threads",
        "mkl_num_threads",
        "parallel_info",
    }
    assert contract["upstream"] == {
        "repository_url": "https://github.com/kong13661/PIA.git",
        "commit": "0d7e08a5a07f44931692d52d54d0ce41aff8f54c",
        "required_file_sha256": {
            "DDPM/attack.py": "362a58e30fe7a123edd107d2dda3716874d84e98001611ec9159006b7eb4da61",
            "DDPM/components.py": (
                "d61ebadb4643741116e2b08f61a4db7f4805dd84efdc15d6e0447cc357b4871a"
            ),
            "DDPM/dataset_utils.py": (
                "7766a985246ce868e861a751a651d3740419456106ea1277a357fdf1b6a9ce82"
            ),
            "DDPM/model.py": "b8714f85649dadc9223c0e77d63ee24515be4a87dba25a796c8d611f0cff17ed",
        },
    }
    assert "preflight" not in h1_scorer_contract()["cross_target_rosters"]


def test_paper1_protocol_seals_non_circular_preflight_and_formal_run_label_templates() -> None:
    contract = build_paper1_corrected_contract(
        split_filename="CIFAR10_train_ratio0.5.npz",
        split_sha256="a" * 64,
        member_indices=tuple(range(25_000)),
        nonmember_indices=tuple(range(25_000, 50_000)),
        class_labels=np.arange(50_000, dtype=np.int64) % 10,
        code_commit="b" * 40,
    )

    assert contract["training"]["run_label_templates"] == {
        "preflight": "corrected-preflight-s{seed}",
        "formal": "corrected-s{seed}",
    }
    serialized = json.dumps(contract["training"]["run_label_templates"], sort_keys=True)
    assert "protocol_hash" not in serialized
    assert "{" + "protocol" not in serialized


def test_evidence_package_exports_corrected_protocol_primitives() -> None:
    expected = {
        "MembershipSplit",
        "ProtocolRow",
        "build_paper1_corrected_contract",
        "build_paper1_corrected_row_manifest",
        "build_protocol_envelope",
        "build_stratified_row_manifest",
        "canonical_protocol_hash",
        "derive_noise_seed",
        "derive_training_seeds",
        "load_member_nonmember_indices",
        "load_protocol_envelope",
        "verify_paper1_contract",
    }

    assert set(evidence.__all__) == expected
    assert all(hasattr(evidence, name) for name in expected)
