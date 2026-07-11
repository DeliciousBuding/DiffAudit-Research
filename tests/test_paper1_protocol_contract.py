from __future__ import annotations

import hashlib
import inspect
from collections import Counter
from copy import deepcopy
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pytest

from diffaudit.evidence import corrected_protocol as protocol
from diffaudit.evidence.training_config import (
    build_training_config,
    canonical_training_config_hash,
)

_SPLIT_SHA256 = "a" * 64
_CODE_COMMIT = "b" * 40


def _api(name: str):
    value = getattr(protocol, name, None)
    assert callable(value), f"missing protocol API: {name}"
    return value


@pytest.fixture(scope="module")
def paper1_inputs() -> tuple[tuple[int, ...], tuple[int, ...], np.ndarray]:
    return (
        tuple(range(25_000)),
        tuple(range(25_000, 50_000)),
        np.arange(50_000, dtype=np.int64) % 10,
    )


@pytest.fixture(scope="module")
def paper1_split_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    split_path = tmp_path_factory.mktemp("paper1-source") / "CIFAR10_train_ratio0.5.npz"
    np.savez(
        split_path,
        mia_train_idxs=np.arange(25_000, dtype=np.int64),
        mia_eval_idxs=np.arange(25_000, 50_000, dtype=np.int64),
    )
    return split_path


@pytest.fixture(scope="module")
def paper1_contract(
    paper1_inputs: tuple[tuple[int, ...], tuple[int, ...], np.ndarray],
    paper1_split_path: Path,
) -> dict[str, object]:
    member_indices, nonmember_indices, class_labels = paper1_inputs
    return _api("build_paper1_corrected_contract")(
        split_filename="CIFAR10_train_ratio0.5.npz",
        split_sha256=hashlib.sha256(paper1_split_path.read_bytes()).hexdigest(),
        member_indices=member_indices,
        nonmember_indices=nonmember_indices,
        class_labels=class_labels,
        code_commit=_CODE_COMMIT,
    )


def test_paper1_contract_builder_has_no_free_scientific_size_or_threshold_parameters() -> None:
    signature = inspect.signature(_api("build_paper1_corrected_contract"))

    assert set(signature.parameters) == {
        "split_filename",
        "split_sha256",
        "member_indices",
        "nonmember_indices",
        "class_labels",
        "code_commit",
    }


def test_paper1_contract_freezes_exact_scientific_shape(
    paper1_contract: dict[str, object],
    paper1_split_path: Path,
) -> None:
    assert set(paper1_contract) == {
        "protocol_namespace",
        "dataset",
        "training",
        "evaluation",
        "h1",
        "pia",
        "common_noise",
        "branch_rules",
        "confirmatory_heterogeneity",
        "code_commit",
    }
    assert paper1_contract["protocol_namespace"] == "paper1-corrected-evidence"
    assert paper1_contract["dataset"] == {
        "name": "CIFAR10",
        "size": 50_000,
        "split": {
            "filename": "CIFAR10_train_ratio0.5.npz",
            "sha256": hashlib.sha256(paper1_split_path.read_bytes()).hexdigest(),
            "member_count": 25_000,
            "nonmember_count": 25_000,
        },
    }
    assert paper1_contract["training"] == {
        "seeds": [
            1746574482,
            1403859882,
            1877216607,
            120492209,
            1624907720,
            761208184,
            1867632528,
            1918927372,
        ],
        "batch_size": 64,
        "interim_steps": 100_000,
        "mature_steps": 200_000,
        "deterministic": True,
        "member_only": True,
        "training_config": build_training_config().to_dict(),
        "training_config_hash": canonical_training_config_hash(build_training_config()),
    }
    assert paper1_contract["h1"] == {
        "sites": ["late_down", "mid_0", "mid_1", "early_up"],
        "timesteps": [100, 400, 700],
        "score_direction": "higher_is_member",
        "feature_scaler": "none",
        "sklearn_version": version("scikit-learn"),
        "pca": {
            "n_components": 6,
            "svd_solver": "randomized",
            "whiten": False,
            "random_state": 42,
            "n_oversamples": 10,
            "iterated_power": 4,
            "power_iteration_normalizer": "QR",
        },
        "bootstrap_replicates": 200,
        "permutation_replicates": 200,
        "cross_target_rosters": {
            "stage1": [1746574482, 1403859882, 1877216607, 120492209],
            "replicate": [1624907720, 761208184, 1867632528, 1918927372],
            "full": [
                1746574482,
                1403859882,
                1877216607,
                120492209,
                1624907720,
                761208184,
                1867632528,
                1918927372,
            ],
        },
        "logistic_regression": {
            "logical_penalty": "l2",
            "constructor": {
                "dual": False,
                "l1_ratio": 0.0,
                "C": 1.0,
                "fit_intercept": True,
                "class_weight": "balanced",
                "solver": "lbfgs",
                "max_iter": 5000,
                "tol": 0.0001,
                "random_state": 42,
            },
        },
    }
    assert paper1_contract["pia"] == {"validation_status": "positive_control_required"}
    assert paper1_contract["common_noise"] == {
        "namespace": "paper1-corrected-v1",
        "algorithm": "diffaudit-common-noise-seed-v1",
        "timesteps": [100, 400, 700],
        "draws": [0],
    }
    assert paper1_contract["branch_rules"] == {
        "STOP": {
            "first_stage_target_count": 4,
            "attacks": ["H1", "PIA"],
            "all_auc_95pct_upper_bounds_below": 0.55,
        },
        "REPLICATE": {
            "first_stage_target_count": 4,
            "same_attack_minimum_target_count": 2,
            "auc_point_estimate_at_least": 0.55,
            "auc_95pct_lower_bound_above": 0.50,
            "full_label_permutation_null_calibrated": True,
            "minimum_full_label_permutations": 200,
            "target_steps": 100_000,
        },
        "MATURE": {
            "condition": "not_STOP_and_not_REPLICATE",
            "target_count": 4,
            "target_steps": 200_000,
        },
    }
    assert paper1_contract["confirmatory_heterogeneity"] == {
        "global_test_alpha": 0.05,
        "practical_auc_range_at_least": 0.05,
        "global_statistic": "auc_range",
        "global_null": "paired_stratified_refit_bootstrap_null_centering",
        "pairwise_test": "two_sided_centered_paired_bootstrap",
        "pairwise_correction": "holm",
        "report_all_pairwise_deltas": True,
    }
    assert paper1_contract["code_commit"] == _CODE_COMMIT


def test_paper1_contract_inlines_four_balanced_disjoint_512_row_groups(
    paper1_contract: dict[str, object],
) -> None:
    assert set(paper1_contract["evaluation"]) == {"rows"}
    rows = paper1_contract["evaluation"]["rows"]

    assert len(rows) == 2048
    assert all(set(row) == {"dataset_index", "label", "class_id", "split"} for row in rows)
    assert len({row["dataset_index"] for row in rows}) == 2048
    assert Counter((row["label"], row["split"]) for row in rows) == {
        (1, "calibration"): 512,
        (1, "evaluation"): 512,
        (0, "calibration"): 512,
        (0, "evaluation"): 512,
    }
    for label in (0, 1):
        for split_name in ("calibration", "evaluation"):
            counts = Counter(
                row["class_id"]
                for row in rows
                if row["label"] == label and row["split"] == split_name
            )
            assert set(counts) == set(range(10))
            assert max(counts.values()) - min(counts.values()) <= 1


def test_verify_paper1_contract_accepts_path_and_returns_detached_contract(
    tmp_path: Path,
    paper1_contract: dict[str, object],
    paper1_inputs: tuple[tuple[int, ...], tuple[int, ...], np.ndarray],
    paper1_split_path: Path,
) -> None:
    envelope = protocol.build_protocol_envelope(paper1_contract)
    manifest_path = tmp_path / "paper1-protocol.json"
    manifest_path.write_text(__import__("json").dumps(envelope), encoding="utf-8")

    verified = _api("verify_paper1_contract")(
        manifest_path,
        split_path=paper1_split_path,
        class_labels=paper1_inputs[2],
        expected_code_commit=_CODE_COMMIT,
    )

    assert verified == paper1_contract
    envelope["contract"]["training"]["seeds"][0] = 1
    assert verified["training"]["seeds"][0] == 1746574482


def _resign_with_mutation(
    paper1_contract: dict[str, object],
    mutator,
) -> dict[str, object]:
    changed = deepcopy(paper1_contract)
    mutator(changed)
    return protocol.build_protocol_envelope(changed)


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda value: value["evaluation"]["rows"].pop(), "2048"),
        (lambda value: value["training"]["seeds"].__setitem__(1, 0), "seeds"),
        (
            lambda value: value["training"]["training_config"]["runtime"].update(num_workers=0),
            "training",
        ),
        (
            lambda value: value["training"].update(training_config_hash="f" * 64),
            "training",
        ),
        (
            lambda value: value["training"]["seeds"].__setitem__(1, value["training"]["seeds"][0]),
            "seeds",
        ),
        (
            lambda value: value["branch_rules"]["STOP"].update(
                all_auc_95pct_upper_bounds_below=0.56
            ),
            "branch_rules",
        ),
        (lambda value: value["common_noise"].update(draws=[0, 1]), "common_noise"),
        (lambda value: value["dataset"]["split"].update(sha256="A" * 64), "dataset"),
        (lambda value: value.update(code_commit="not-a-commit"), "code_commit"),
    ],
)
def test_verify_paper1_contract_rejects_resigned_scientific_drift(
    paper1_contract: dict[str, object],
    paper1_inputs: tuple[tuple[int, ...], tuple[int, ...], np.ndarray],
    paper1_split_path: Path,
    mutator,
    message: str,
) -> None:
    envelope = _resign_with_mutation(paper1_contract, mutator)

    with pytest.raises(ValueError, match=message):
        _api("verify_paper1_contract")(
            envelope,
            split_path=paper1_split_path,
            class_labels=paper1_inputs[2],
            expected_code_commit=_CODE_COMMIT,
        )


@pytest.mark.parametrize(
    "mutator",
    [
        lambda row: row.update(label=0),
        lambda row: row.update(class_id=(row["class_id"] + 1) % 10),
        lambda row: row.update(dataset_index=50_000),
    ],
)
def test_verify_paper1_contract_rejects_invalid_row_identity_or_balance(
    paper1_contract: dict[str, object],
    paper1_inputs: tuple[tuple[int, ...], tuple[int, ...], np.ndarray],
    paper1_split_path: Path,
    mutator,
) -> None:
    envelope = _resign_with_mutation(
        paper1_contract,
        lambda value: mutator(value["evaluation"]["rows"][0]),
    )

    with pytest.raises(ValueError, match="evaluation rows"):
        _api("verify_paper1_contract")(
            envelope,
            split_path=paper1_split_path,
            class_labels=paper1_inputs[2],
            expected_code_commit=_CODE_COMMIT,
        )


def _swap_balanced_class_ids(contract: dict[str, object]) -> None:
    rows = contract["evaluation"]["rows"]
    first = next(row for row in rows if row["label"] == 1 and row["split"] == "calibration")
    second = next(
        row
        for row in rows
        if row["label"] == 1
        and row["split"] == "calibration"
        and row["class_id"] != first["class_id"]
    )
    first["class_id"], second["class_id"] = second["class_id"], first["class_id"]


def _swap_balanced_membership_labels(contract: dict[str, object]) -> None:
    rows = contract["evaluation"]["rows"]
    member = next(row for row in rows if row["label"] == 1 and row["split"] == "calibration")
    nonmember = next(
        row
        for row in rows
        if row["label"] == 0
        and row["split"] == member["split"]
        and row["class_id"] == member["class_id"]
    )
    member["label"], nonmember["label"] = nonmember["label"], member["label"]


def _swap_balanced_calibration_evaluation(contract: dict[str, object]) -> None:
    rows = contract["evaluation"]["rows"]
    calibration = next(row for row in rows if row["label"] == 1 and row["split"] == "calibration")
    evaluation = next(
        row
        for row in rows
        if row["label"] == calibration["label"]
        and row["class_id"] == calibration["class_id"]
        and row["split"] == "evaluation"
    )
    calibration["split"], evaluation["split"] = evaluation["split"], calibration["split"]


@pytest.mark.parametrize(
    "mutator",
    [
        _swap_balanced_class_ids,
        _swap_balanced_membership_labels,
        _swap_balanced_calibration_evaluation,
    ],
)
def test_verify_paper1_contract_rejects_resigned_balance_preserving_semantic_tamper(
    paper1_contract: dict[str, object],
    paper1_inputs: tuple[tuple[int, ...], tuple[int, ...], np.ndarray],
    paper1_split_path: Path,
    mutator,
) -> None:
    envelope = _resign_with_mutation(paper1_contract, mutator)

    with pytest.raises(ValueError, match="source truth"):
        _api("verify_paper1_contract")(
            envelope,
            split_path=paper1_split_path,
            class_labels=paper1_inputs[2],
            expected_code_commit=_CODE_COMMIT,
        )


def test_verify_paper1_contract_rejects_resigned_external_commit_mismatch(
    paper1_contract: dict[str, object],
    paper1_inputs: tuple[tuple[int, ...], tuple[int, ...], np.ndarray],
    paper1_split_path: Path,
) -> None:
    envelope = _resign_with_mutation(
        paper1_contract,
        lambda contract: contract.update(code_commit="d" * 40),
    )

    with pytest.raises(ValueError, match="expected_code_commit"):
        _api("verify_paper1_contract")(
            envelope,
            split_path=paper1_split_path,
            class_labels=paper1_inputs[2],
            expected_code_commit=_CODE_COMMIT,
        )


@pytest.mark.parametrize(
    ("updates", "message"),
    [
        ({"split_filename": "/private/split.npz"}, "split_filename"),
        ({"split_sha256": "A" * 64}, "split_sha256"),
        ({"code_commit": "B" * 40}, "code_commit"),
    ],
)
def test_paper1_contract_builder_rejects_noncanonical_identity_fields(
    paper1_inputs: tuple[tuple[int, ...], tuple[int, ...], np.ndarray],
    updates: dict[str, str],
    message: str,
) -> None:
    member_indices, nonmember_indices, class_labels = paper1_inputs
    arguments = {
        "split_filename": "CIFAR10_train_ratio0.5.npz",
        "split_sha256": _SPLIT_SHA256,
        "member_indices": member_indices,
        "nonmember_indices": nonmember_indices,
        "class_labels": class_labels,
        "code_commit": _CODE_COMMIT,
    }
    arguments.update(updates)

    with pytest.raises(ValueError, match=message):
        _api("build_paper1_corrected_contract")(**arguments)


def test_paper1_contract_builder_rejects_non_partition_split(
    paper1_inputs: tuple[tuple[int, ...], tuple[int, ...], np.ndarray],
) -> None:
    member_indices, nonmember_indices, class_labels = paper1_inputs
    incomplete_nonmembers = nonmember_indices[:-1]

    with pytest.raises(ValueError, match="complete 25000/25000 partition"):
        _api("build_paper1_corrected_contract")(
            split_filename="CIFAR10_train_ratio0.5.npz",
            split_sha256=_SPLIT_SHA256,
            member_indices=member_indices,
            nonmember_indices=incomplete_nonmembers,
            class_labels=class_labels,
            code_commit=_CODE_COMMIT,
        )
