from __future__ import annotations

import inspect
import json
import math
import warnings
from copy import deepcopy
from importlib.metadata import version
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from sklearn.exceptions import ConvergenceWarning

import diffaudit.evidence.h1_confirmatory as h1_module
from diffaudit.evidence import corrected_protocol as protocol
from diffaudit.evidence.corrected_protocol import (
    build_protocol_envelope,
    canonical_protocol_hash,
    derive_noise_seed,
    derive_training_seeds,
)
from diffaudit.evidence.h1_confirmatory import (
    benchmark_h1_refit_runtime,
    bootstrap_h1_checkpoints,
    fit_h1_model,
    full_label_permutation_test,
    score_h1_checkpoints,
    summarize_h1_heterogeneity,
    tpr_at_1pct_fpr_with_wilson,
    validate_h1_feature_packets,
    wilson_interval,
)
from diffaudit.evidence.h1_extraction import write_h1_feature_packet
from diffaudit.evidence.training_config import (
    build_training_config,
    canonical_training_config_hash,
)

_CODE_COMMIT = "c" * 40
_SPLIT_SHA256 = "d" * 64
_TRAINING_SEEDS = derive_training_seeds("paper1-corrected-evidence")
_PRODUCTION_H1_CONTRACT = h1_module.h1_scorer_contract()


@pytest.fixture(autouse=True)
def _bounded_feature_layout(monkeypatch: pytest.MonkeyPatch) -> None:
    contract = deepcopy(_PRODUCTION_H1_CONTRACT)
    definition = contract["feature_definition"]
    definition["pca_input_dimension"] = 8
    definition["scalar_feature_dimension"] = 4
    definition["lr_input_dimension"] = 10
    monkeypatch.setattr(h1_module, "h1_scorer_contract", lambda: deepcopy(contract))


@pytest.mark.parametrize("filename", ["environment.yml", "environment.gpu-cu128.yml"])
def test_environment_pins_the_protocol_sklearn_version(filename: str) -> None:
    environment = (Path(__file__).parents[1] / filename).read_text(encoding="utf-8")

    assert f"scikit-learn=={version('scikit-learn')}" in environment


def _make_setup(
    *,
    target_count: int = 1,
    separable: bool = True,
    reverse_evaluation: bool = False,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    pca_rows: list[list[float]] = []
    scalar_rows: list[list[float]] = []
    manifest_rows: list[dict[str, object]] = []
    dataset_index = 0
    for split in ("calibration", "evaluation"):
        for membership in (0, 1):
            for class_id in range(10):
                count = 52 if class_id < 2 else 51
                for ordinal in range(count):
                    signal = 0.0
                    if separable:
                        direction = 1.0 if membership == 1 else -1.0
                        if split == "evaluation" and reverse_evaluation:
                            direction *= -1.0
                        signal = 4.0 * direction
                    values = [
                        signal + 0.01 * class_id + 0.001 * ordinal,
                        math.sin(ordinal + 1.0),
                        math.cos(ordinal + 1.0),
                        float(ordinal % 7),
                        float((ordinal * 3) % 11),
                        float(class_id % 3),
                        float(ordinal % 2),
                        float(class_id),
                    ]
                    row = {
                        "dataset_index": dataset_index,
                        "label": membership,
                        "class": class_id,
                        "calibration_or_evaluation": split,
                        "noise_id": {
                            "namespace": "paper1-corrected-v1",
                            "dataset_index": dataset_index,
                            "entries": [
                                {
                                    "timestep": timestep,
                                    "draw": 0,
                                    "seed": derive_noise_seed(
                                        "paper1-corrected-v1",
                                        dataset_index,
                                        timestep,
                                        0,
                                    ),
                                }
                                for timestep in (100, 400, 700)
                            ],
                        },
                    }
                    rows.append(row)
                    pca_rows.append(values)
                    scalar_rows.append(values[:4])
                    manifest_rows.append(
                        {
                            "dataset_index": dataset_index,
                            "label": membership,
                            "class_id": class_id,
                            "split": split,
                        }
                    )
                    dataset_index += 1

    training_config = build_training_config()
    envelope = build_protocol_envelope(
        {
            "protocol_namespace": "paper1-corrected-evidence",
            "dataset": {
                "name": "CIFAR10",
                "size": 50_000,
                "split": {
                    "filename": "CIFAR10_train_ratio0.5.npz",
                    "sha256": _SPLIT_SHA256,
                    "member_count": 25_000,
                    "nonmember_count": 25_000,
                },
            },
            "training": {
                "seeds": list(_TRAINING_SEEDS),
                "batch_size": 32,
                "interim_steps": 100_000,
                "mature_steps": 200_000,
                "deterministic": True,
                "member_only": True,
                "training_config": training_config.to_dict(),
                "training_config_hash": canonical_training_config_hash(training_config),
            },
            "evaluation": {"rows": manifest_rows},
            "h1": h1_module.h1_scorer_contract(),
            "pia": protocol.paper1_pia_contract(),
            "common_noise": {
                "namespace": "paper1-corrected-v1",
                "algorithm": "diffaudit-common-noise-seed-v1",
                "timesteps": [100, 400, 700],
                "draws": [0],
            },
            "branch_rules": {
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
            },
            "confirmatory_heterogeneity": {
                "global_test_alpha": 0.05,
                "practical_auc_range_at_least": 0.05,
                "global_statistic": "auc_range",
                "global_null": "paired_stratified_refit_bootstrap_null_centering",
                "pairwise_test": "two_sided_centered_paired_bootstrap",
                "pairwise_correction": "holm",
                "report_all_pairwise_deltas": True,
            },
            "code_commit": _CODE_COMMIT,
        }
    )
    protocol_hash = envelope["protocol_hash"]

    checkpoint_hashes = "01234567"
    packets: list[dict[str, object]] = [
        {
            "schema_version": 1,
            "packet_format": "h1-feature-packet-v2",
            "packet_purpose": "corrected_evaluation",
            "provenance": {
                "dataset_id": "CIFAR10",
                "run_seed": _TRAINING_SEEDS[target_index],
                "step": 100_000,
                "attack": "H1",
                "checkpoint_sha256": checkpoint_hashes[target_index] * 64,
                "training_manifest_sha256": "89abcdef"[target_index] * 64,
                "target_code_commit": _CODE_COMMIT,
                "scorer_code_commit": "e" * 40,
                "split_sha256": _SPLIT_SHA256,
                "protocol_hash": protocol_hash,
                "run_label": f"corrected-s{_TRAINING_SEEDS[target_index]}",
                "extraction_config": deepcopy(envelope["contract"]["h1"]["extraction"]),
                "extraction_config_hash": canonical_protocol_hash(
                    envelope["contract"]["h1"]["extraction"]
                ),
                "evaluator_environment": deepcopy(
                    envelope["contract"]["h1"]["extraction"]["evaluator_environment"]
                ),
            },
            "rows": deepcopy(rows),
            "pca_features": np.asarray(pca_rows, dtype=np.float32),
            "scalar_features": np.asarray(scalar_rows, dtype=np.float32),
        }
        for target_index in range(target_count)
    ]
    return envelope, packets


def _protocol_kwargs(envelope: dict[str, object]) -> dict[str, object]:
    return {
        "protocol_envelope": envelope,
        "expected_protocol_hash": envelope["protocol_hash"],
    }


@pytest.mark.parametrize("location", ["protocol", "config"])
def test_h1_rejects_resigned_legacy_batch64_training_contract(location: str) -> None:
    envelope, packets = _make_setup()
    changed_contract = deepcopy(envelope["contract"])
    if location == "protocol":
        changed_contract["training"]["batch_size"] = 64
    else:
        changed_contract["training"]["training_config"]["data"]["batch_size"] = 64
    changed_envelope = build_protocol_envelope(changed_contract)
    for packet in packets:
        for row in packet["rows"]:
            row["protocol_hash"] = changed_envelope["protocol_hash"]

    with pytest.raises(ValueError, match="training"):
        score_h1_checkpoints(packets, **_protocol_kwargs(changed_envelope))


def test_score_h1_checkpoint_separates_signal_and_keeps_fixed_direction() -> None:
    envelope, packets = _make_setup(separable=True)

    result = score_h1_checkpoints(packets, **_protocol_kwargs(envelope))

    assert result["targets"][0]["metrics"]["auc"] > 0.99
    reversed_envelope, reversed_packets = _make_setup(
        separable=True,
        reverse_evaluation=True,
    )
    reversed_result = score_h1_checkpoints(
        reversed_packets,
        **_protocol_kwargs(reversed_envelope),
    )
    assert reversed_result["targets"][0]["metrics"]["auc"] < 0.01


def test_score_h1_checkpoint_reports_chance_for_nonseparable_rows() -> None:
    envelope, packets = _make_setup(separable=False)

    result = score_h1_checkpoints(packets, **_protocol_kwargs(envelope))

    assert result["targets"][0]["metrics"]["auc"] == pytest.approx(0.5, abs=0.01)


def test_evaluation_feature_changes_cannot_change_fitted_calibration_model() -> None:
    envelope, packets = _make_setup()
    changed_packet = deepcopy(packets[0])
    evaluation = np.asarray(
        [row["calibration_or_evaluation"] == "evaluation" for row in changed_packet["rows"]]
    )
    changed_packet["pca_features"][evaluation] *= -1000.0
    changed_packet["scalar_features"][evaluation] *= -1000.0

    original_model = fit_h1_model(packets[0], **_protocol_kwargs(envelope))
    changed_model = fit_h1_model(changed_packet, **_protocol_kwargs(envelope))

    np.testing.assert_allclose(original_model.pca.mean_, changed_model.pca.mean_)
    np.testing.assert_allclose(original_model.pca.components_, changed_model.pca.components_)
    np.testing.assert_allclose(
        original_model.classifier.coef_,
        changed_model.classifier.coef_,
    )


def test_fitted_model_reports_the_exact_frozen_lr_contract() -> None:
    envelope, packets = _make_setup()

    model = fit_h1_model(packets[0], **_protocol_kwargs(envelope))
    params = model.realized_logistic_regression

    assert model.sklearn_version == envelope["contract"]["h1"]["sklearn_version"]
    assert params["penalty"] in ("l2", "deprecated")
    assert params["dual"] is False
    assert params["l1_ratio"] == 0.0
    assert model.pca.svd_solver == "randomized"
    assert model.pca.n_oversamples == 10
    assert model.pca.iterated_power == 4
    assert model.pca.power_iteration_normalizer == "QR"


def test_production_shape_randomized_pca_fit_completes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from diffaudit.evidence import h1_confirmatory as h1

    rng = np.random.default_rng(7)
    pca_features = rng.normal(size=(1024, 9216)).astype(np.float32)
    scalar_features = rng.normal(size=(1024, 36)).astype(np.float32)
    labels = np.asarray([0, 1] * 512)

    monkeypatch.setattr(h1, "h1_scorer_contract", lambda: deepcopy(_PRODUCTION_H1_CONTRACT))
    model = h1._fit_h1_arrays(pca_features, scalar_features, labels, _PRODUCTION_H1_CONTRACT)

    assert model.pca.components_.shape == (6, 9216)
    assert model.classifier.coef_.shape == (1, 42)


def test_fit_and_predict_lock_the_same_scalar_then_pca_column_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rng = np.random.default_rng(19)
    pca_features = rng.normal(size=(64, 8)).astype(np.float32)
    scalar_features = np.column_stack(
        [np.arange(64, dtype=np.float32) + 1000.0 * (column + 1) for column in range(4)]
    )
    labels = np.asarray([0, 1] * 32)
    captured: list[np.ndarray] = []
    original_fit = h1_module.LogisticRegression.fit

    def capture_fit(self: object, features: np.ndarray, target: np.ndarray) -> object:
        captured.append(features.copy())
        return original_fit(self, features, target)

    monkeypatch.setattr(h1_module.LogisticRegression, "fit", capture_fit)
    model = h1_module._fit_h1_arrays(
        pca_features,
        scalar_features,
        labels,
        h1_module.h1_scorer_contract(),
    )

    assert len(captured) == 1
    np.testing.assert_allclose(captured[0][:, :4], scalar_features)
    np.testing.assert_allclose(captured[0][:, 4:], model.pca.transform(pca_features))

    predicted: list[np.ndarray] = []

    class SpyClassifier:
        classes_ = np.asarray([0, 1])

        def predict_proba(self, features: np.ndarray) -> np.ndarray:
            predicted.append(features.copy())
            return np.column_stack(
                [np.full(features.shape[0], 0.5), np.full(features.shape[0], 0.5)]
            )

    model.classifier = SpyClassifier()
    model.predict_scores(pca_features, scalar_features)

    assert len(predicted) == 1
    np.testing.assert_allclose(predicted[0], captured[0])


def test_convergence_warning_is_a_hard_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    from diffaudit.evidence import h1_confirmatory as h1

    envelope, packets = _make_setup()

    def warning_fit(self: object, features: np.ndarray, labels: np.ndarray) -> object:
        warnings.warn("did not converge", ConvergenceWarning, stacklevel=2)
        return self

    monkeypatch.setattr(h1.LogisticRegression, "fit", warning_fit)

    with pytest.raises(ConvergenceWarning, match="did not converge"):
        fit_h1_model(packets[0], **_protocol_kwargs(envelope))


def test_reaching_max_iter_without_warning_is_a_hard_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from diffaudit.evidence import h1_confirmatory as h1

    envelope, packets = _make_setup()
    original_fit = h1.LogisticRegression.fit

    def capped_fit(self: object, features: np.ndarray, labels: np.ndarray) -> object:
        fitted = original_fit(self, features, labels)
        fitted.n_iter_[:] = fitted.max_iter
        return fitted

    monkeypatch.setattr(h1.LogisticRegression, "fit", capped_fit)

    with pytest.raises(RuntimeError, match="reached max_iter"):
        fit_h1_model(packets[0], **_protocol_kwargs(envelope))


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda packets: packets[0]["rows"][1].__setitem__(
                "dataset_index", packets[0]["rows"][0]["dataset_index"]
            ),
            "duplicate row identity",
        ),
        (
            lambda packets: packets[0]["rows"][0].__setitem__("label", True),
            "label must be integer 0 or 1",
        ),
        (
            lambda packets: packets[0]["rows"][0].__setitem__("class", True),
            "class must be an integer",
        ),
        (
            lambda packets: packets[0]["rows"][0].__setitem__("dataset_index", True),
            "dataset_index must be a non-negative integer",
        ),
        (
            lambda packets: packets[0]["provenance"].__setitem__("run_seed", True),
            "run_seed must be a positive integer",
        ),
        (
            lambda packets: packets[0]["provenance"].__setitem__("step", True),
            "step must be a positive integer",
        ),
        (
            lambda packets: packets[0]["pca_features"].__setitem__((0, 0), float("nan")),
            "pca_features must contain only finite",
        ),
        (
            lambda packets: packets[0]["scalar_features"].__setitem__((0, 0), float("inf")),
            "scalar_features must contain only finite",
        ),
        (
            lambda packets: packets[0].__setitem__(
                "pca_features", packets[0]["pca_features"][:, :-1]
            ),
            "pca_features shape",
        ),
        (
            lambda packets: packets[0]["provenance"].__setitem__("checkpoint_sha256", "abc"),
            "checkpoint_sha256 must be 64 lowercase hex",
        ),
        (
            lambda packets: packets[0]["provenance"].__setitem__("split_sha256", "abc"),
            "split_sha256 must be 64 lowercase hex",
        ),
        (
            lambda packets: packets[0]["provenance"].__setitem__("protocol_hash", "abc"),
            "protocol_hash must be 64 lowercase hex",
        ),
    ],
)
def test_packet_validator_rejects_invalid_row_contract(
    mutate: Any,
    message: str,
) -> None:
    envelope, packets = _make_setup()
    mutate(packets)

    with pytest.raises(ValueError, match=message):
        validate_h1_feature_packets(packets, **_protocol_kwargs(envelope))


def test_packet_validator_rejects_calibration_evaluation_overlap() -> None:
    envelope, packets = _make_setup()
    calibration_row = packets[0]["rows"][0]
    evaluation_row = next(
        row for row in packets[0]["rows"] if row["calibration_or_evaluation"] == "evaluation"
    )
    evaluation_row["dataset_index"] = calibration_row["dataset_index"]

    with pytest.raises(ValueError, match="duplicate row identity"):
        validate_h1_feature_packets(packets, **_protocol_kwargs(envelope))


def test_packet_validator_rejects_unbalanced_class_membership_cell() -> None:
    envelope, packets = _make_setup()
    packets[0]["rows"][0]["class"] = 9

    with pytest.raises(ValueError, match="class-balanced"):
        validate_h1_feature_packets(packets, **_protocol_kwargs(envelope))


def test_packet_validator_rejects_non_json_packet_metadata() -> None:
    envelope, packets = _make_setup()
    packets[0]["not_json"] = object()

    with pytest.raises(ValueError, match="feature packet fields must exactly match"):
        validate_h1_feature_packets(packets, **_protocol_kwargs(envelope))


def test_packet_validator_rejects_noncanonical_noise_identity() -> None:
    envelope, packets = _make_setup()
    packets[0]["rows"][1]["noise_id"] = packets[0]["rows"][0]["noise_id"]

    with pytest.raises(ValueError, match="canonical common-noise derivation"):
        validate_h1_feature_packets(packets, **_protocol_kwargs(envelope))


def test_packet_validator_rejects_extra_row_fields() -> None:
    envelope, packets = _make_setup()
    packets[0]["rows"][0]["unexpected"] = "drift"

    with pytest.raises(ValueError, match="row fields must exactly match"):
        validate_h1_feature_packets(packets, **_protocol_kwargs(envelope))


def test_preflight_packet_validates_but_all_scientific_scoring_rejects_it() -> None:
    envelope, packets = _make_setup()
    packet = packets[0]
    packet["packet_purpose"] = "preflight_benchmark"
    packet["provenance"]["step"] = 2000
    packet["provenance"]["run_label"] = "corrected-preflight-s1746574482"

    validated = validate_h1_feature_packets([packet], **_protocol_kwargs(envelope))
    assert validated["row_count_per_checkpoint"] == 2048
    with pytest.raises(ValueError, match="preflight_benchmark.*forbidden"):
        score_h1_checkpoints([packet], **_protocol_kwargs(envelope))


def test_exported_v2_packet_is_consumed_by_the_h1_validator(tmp_path: Path) -> None:
    envelope, packets = _make_setup()
    packet = packets[0]
    output = tmp_path / "packet"
    write_h1_feature_packet(
        output,
        packet_purpose=packet["packet_purpose"],
        provenance=packet["provenance"],
        rows=packet["rows"],
        pca_features=packet["pca_features"],
        scalar_features=packet["scalar_features"],
    )

    validated = validate_h1_feature_packets([output], **_protocol_kwargs(envelope))
    assert validated["row_count_per_checkpoint"] == 2048
    assert validated["pca_feature_dimension"] == 8
    assert validated["scalar_feature_dimension"] == 4


def test_canonical_packet_validation_does_not_copy_feature_matrices() -> None:
    envelope, packets = _make_setup()
    packet = packets[0]

    _, validated = h1_module._validate_packets(
        [packet],
        **_protocol_kwargs(envelope),
        require_corrected_evaluation=False,
    )

    assert validated[0].pca_features is packet["pca_features"]
    assert validated[0].scalar_features is packet["scalar_features"]


def test_refit_runtime_benchmark_returns_time_only(monkeypatch: pytest.MonkeyPatch) -> None:
    envelope, packets = _make_setup()
    calls = 0

    def fake_fit(*_args: object, **_kwargs: object) -> object:
        nonlocal calls
        calls += 1
        return object()

    monkeypatch.setattr(h1_module, "_fit_h1_arrays", fake_fit)
    summary = benchmark_h1_refit_runtime(
        packets[0],
        **_protocol_kwargs(envelope),
        fit_count=3,
    )

    assert calls == 3
    assert set(summary) == {
        "fit_count",
        "total_seconds",
        "seconds_per_fit",
        "calibration_rows",
        "pca_input_dimension",
        "scalar_feature_dimension",
    }
    assert not ({"auc", "tpr", "accuracy", "score"} & set(summary))


def test_packet_validator_rejects_non_float32_feature_matrices() -> None:
    envelope, packets = _make_setup()
    packets[0]["pca_features"] = packets[0]["pca_features"].astype(np.float64)

    with pytest.raises(ValueError, match="dtype must be float32"):
        validate_h1_feature_packets(packets, **_protocol_kwargs(envelope))


@pytest.mark.parametrize("batch_size", [1, 2])
def test_packet_validator_rejects_extraction_batch_drift(batch_size: int) -> None:
    envelope, packets = _make_setup()
    packets[0]["provenance"]["extraction_config"]["batch_size"] = batch_size
    packets[0]["provenance"]["extraction_config_hash"] = canonical_protocol_hash(
        packets[0]["provenance"]["extraction_config"]
    )

    with pytest.raises(ValueError, match="extraction_config"):
        validate_h1_feature_packets(packets, **_protocol_kwargs(envelope))


def test_packet_validator_allows_same_frozen_batch_across_packets() -> None:
    envelope, packets = _make_setup(target_count=2)

    validated = validate_h1_feature_packets(packets, **_protocol_kwargs(envelope))

    assert len(validated["checkpoint_sha256s"]) == 2


@pytest.mark.parametrize(
    "field",
    ["split_sha256", "protocol_hash", "target_code_commit", "scorer_code_commit", "noise_id"],
)
def test_packet_validator_rejects_cross_packet_provenance_drift(field: str) -> None:
    envelope, packets = _make_setup(target_count=2)
    if field == "noise_id":
        packets[1]["rows"][0][field] = "drift"
    elif field.endswith("commit"):
        packets[1]["provenance"][field] = "f" * 40
    elif field.endswith("sha256") or field == "protocol_hash":
        packets[1]["provenance"][field] = "e" * 64

    with pytest.raises(
        ValueError,
        match="target_code_commit|protocol_hash|split_sha256|noise_id|scorer commit drift",
    ):
        validate_h1_feature_packets(packets, **_protocol_kwargs(envelope))


def test_packet_validator_requires_same_locked_rows_across_checkpoints() -> None:
    envelope, packets = _make_setup(target_count=2)
    left = packets[1]["rows"][0]
    right = next(
        row
        for row in packets[1]["rows"]
        if row["calibration_or_evaluation"] == left["calibration_or_evaluation"]
        and row["class"] == left["class"]
        and row["label"] != left["label"]
    )
    left["label"], right["label"] = right["label"], left["label"]

    with pytest.raises(ValueError, match="locked.*row provenance"):
        validate_h1_feature_packets(packets, **_protocol_kwargs(envelope))


def test_scorer_rejects_resigned_fit_parameter_drift_and_bool_substitution() -> None:
    envelope, packets = _make_setup()
    for changed_value in (100, True):
        contract = deepcopy(envelope["contract"])
        contract["h1"]["logistic_regression"]["constructor"]["max_iter"] = changed_value
        changed_envelope = build_protocol_envelope(contract)
        packets[0]["provenance"]["protocol_hash"] = changed_envelope["protocol_hash"]

        with pytest.raises(ValueError, match="fixed H1 scorer contract"):
            score_h1_checkpoints(packets, **_protocol_kwargs(changed_envelope))


@pytest.mark.parametrize(("field", "value"), [("run_seed", 42), ("step", 123)])
def test_scorer_rejects_off_protocol_checkpoint_identity(field: str, value: int) -> None:
    envelope, packets = _make_setup()
    packets[0]["provenance"][field] = value

    with pytest.raises(ValueError, match=f"{field}.*sealed protocol"):
        score_h1_checkpoints(packets, **_protocol_kwargs(envelope))


def test_scorer_rejects_resigned_partial_protocol_contract() -> None:
    envelope, packets = _make_setup()
    contract = envelope["contract"]
    partial_envelope = build_protocol_envelope(
        {
            "dataset": contract["dataset"],
            "evaluation": contract["evaluation"],
            "h1": contract["h1"],
            "code_commit": contract["code_commit"],
        }
    )
    packets[0]["provenance"]["protocol_hash"] = partial_envelope["protocol_hash"]

    with pytest.raises(ValueError, match="protocol top-level fields"):
        score_h1_checkpoints(
            packets,
            protocol_envelope=partial_envelope,
            expected_protocol_hash=partial_envelope["protocol_hash"],
        )


def test_scorer_requires_external_trusted_protocol_hash() -> None:
    envelope, packets = _make_setup()

    with pytest.raises(ValueError, match="trusted expected_protocol_hash"):
        score_h1_checkpoints(
            packets,
            protocol_envelope=envelope,
            expected_protocol_hash="e" * 64,
        )


@pytest.mark.parametrize("failure", ["duplicate_seed", "mixed_step", "wrong_stage"])
def test_cross_target_mode_rejects_invalid_roster(failure: str) -> None:
    envelope, packets = _make_setup(target_count=4)
    stage = "stage1"
    if failure == "duplicate_seed":
        packets[1]["provenance"]["run_seed"] = packets[0]["provenance"]["run_seed"]
    elif failure == "mixed_step":
        packets[1]["provenance"]["step"] = 200_000
    else:
        stage = "replicate"

    with pytest.raises(ValueError, match="roster|stage step|unique run_seed"):
        score_h1_checkpoints(
            packets,
            **_protocol_kwargs(envelope),
            analysis_mode="cross_target_same_step",
            stage=stage,
        )


def test_cross_target_stage_locks_the_exact_step() -> None:
    envelope, packets = _make_setup(target_count=4)
    for packet in packets:
        packet["provenance"]["step"] = 200_000

    mature = score_h1_checkpoints(
        packets,
        **_protocol_kwargs(envelope),
        analysis_mode="cross_target_same_step",
        stage="mature",
    )
    assert mature["stage"] == "mature"

    for index, packet in enumerate(packets):
        packet["provenance"]["run_seed"] = _TRAINING_SEEDS[index + 4]
    with pytest.raises(ValueError, match="stage step"):
        score_h1_checkpoints(
            packets,
            **_protocol_kwargs(envelope),
            analysis_mode="cross_target_same_step",
            stage="replicate",
        )

    full_envelope, full_packets = _make_setup(target_count=8)
    for packet in full_packets:
        packet["provenance"]["step"] = 200_000
    with pytest.raises(ValueError, match="stage step"):
        score_h1_checkpoints(
            full_packets,
            **_protocol_kwargs(full_envelope),
            analysis_mode="cross_target_same_step",
            stage="full",
        )


def test_heterogeneity_summary_uses_centered_paired_bootstrap_and_full_holm_family() -> None:
    keys = ["a", "b", "c", "d"]
    identical = summarize_h1_heterogeneity(
        keys,
        [0.7, 0.7, 0.7, 0.7],
        [[0.69 + index * 0.0001] * 4 for index in range(200)],
        alpha=0.05,
        practical_range=0.05,
    )
    assert identical["global"]["decision"] is False
    assert identical["global"]["p_value"] == 1.0

    observed = [0.9, 0.5, 0.5, 0.5]
    draws = [
        [value + ((replicate + target) % 3 - 1) * 0.001 for target, value in enumerate(observed)]
        for replicate in range(200)
    ]
    separated = summarize_h1_heterogeneity(
        keys,
        observed,
        draws,
        alpha=0.05,
        practical_range=0.05,
    )
    assert separated["global"]["decision"] is True
    assert separated["global"]["practical_gate"] is True
    assert len(separated["pairwise"]) == 6
    assert [(row["left"], row["right"]) for row in separated["pairwise"]] == [
        ("a", "b"),
        ("a", "c"),
        ("a", "d"),
        ("b", "c"),
        ("b", "d"),
        ("c", "d"),
    ]
    assert all("raw_p_value" in row and "adjusted_p_value" in row for row in separated["pairwise"])


def test_tpr_at_one_percent_uses_maximum_point_not_a_curve_point_above_cap() -> None:
    positive_scores = np.asarray([100, 90, 80, 70, 60, 50, 40, 30, 20, 10], dtype=float)
    negative_scores = np.asarray([65, 55, 45, *range(-100, -297, -1)], dtype=float)
    scores = np.concatenate([positive_scores, negative_scores])
    labels = np.concatenate(
        [np.ones(positive_scores.size, dtype=int), np.zeros(negative_scores.size, dtype=int)]
    )

    metric = tpr_at_1pct_fpr_with_wilson(scores, labels)

    assert metric["estimate"] == pytest.approx(0.6)
    assert metric["wilson_95_ci"] == pytest.approx(wilson_interval(6, 10))


@pytest.mark.parametrize(
    ("successes", "total", "expected_edge"),
    [(0, 512, 0.0), (512, 512, 1.0)],
)
def test_wilson_interval_has_exact_probability_boundary(
    successes: int,
    total: int,
    expected_edge: float,
) -> None:
    lower, upper = wilson_interval(successes, total)

    assert 0.0 <= lower <= upper <= 1.0
    assert (lower if successes == 0 else upper) == expected_edge


def test_bootstrap_refits_and_uses_shared_paired_draws(monkeypatch: pytest.MonkeyPatch) -> None:
    from diffaudit.evidence import h1_confirmatory as h1

    envelope, packets = _make_setup(target_count=4)
    fitted_calibration_features: list[np.ndarray] = []

    class FakeModel:
        sklearn_version = "test"
        realized_logistic_regression: dict[str, object] = {}

        def predict_scores(
            self, pca_features: np.ndarray, scalar_features: np.ndarray
        ) -> np.ndarray:
            del scalar_features
            return pca_features[:, 0]

    def fit_spy(
        pca_features: np.ndarray,
        scalar_features: np.ndarray,
        labels: np.ndarray,
        contract: dict[str, object],
    ):
        del scalar_features, labels, contract
        fitted_calibration_features.append(pca_features.copy())
        return FakeModel()

    monkeypatch.setattr(h1, "_fit_h1_arrays", fit_spy)

    with pytest.raises(ValueError, match="sealed protocol count 200"):
        bootstrap_h1_checkpoints(
            packets,
            **_protocol_kwargs(envelope),
            n_bootstrap=199,
            random_state=20260711,
            analysis_mode="cross_target_same_step",
            stage="stage1",
        )
    with pytest.raises(ValueError, match="bootstrap random_state"):
        bootstrap_h1_checkpoints(
            packets,
            **_protocol_kwargs(envelope),
            n_bootstrap=200,
            random_state=7,
            analysis_mode="cross_target_same_step",
            stage="stage1",
        )

    result = bootstrap_h1_checkpoints(
        packets,
        **_protocol_kwargs(envelope),
        n_bootstrap=200,
        random_state=20260711,
        analysis_mode="cross_target_same_step",
        stage="stage1",
    )

    assert len(fitted_calibration_features) == 804
    for offset in range(4, 804, 4):
        for target_offset in range(1, 4):
            np.testing.assert_array_equal(
                fitted_calibration_features[offset],
                fitted_calibration_features[offset + target_offset],
            )
    assert len(result["paired_replicates"]) == 200
    assert len(result["pairwise_deltas"][0]["samples"]) == 200
    assert len(result["targets"][0]["auc_samples"]) == 200
    assert "observed_auc" in result["targets"][0]
    assert "heterogeneity_summary" in result
    repeated = bootstrap_h1_checkpoints(
        packets,
        **_protocol_kwargs(envelope),
        n_bootstrap=200,
        random_state=20260711,
        analysis_mode="cross_target_same_step",
        stage="stage1",
    )
    assert json.dumps(repeated, sort_keys=True) == json.dumps(result, sort_keys=True)
    json.dumps(result, allow_nan=False)


def test_permutation_requires_200_and_refits_every_full_label_draw(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from diffaudit.evidence import h1_confirmatory as h1

    envelope, packets = _make_setup()
    parameter = inspect.signature(full_label_permutation_test).parameters["random_state"]
    assert parameter.default is inspect.Parameter.empty
    with pytest.raises(TypeError, match="random_state"):
        full_label_permutation_test(
            packets[0],
            **_protocol_kwargs(envelope),
            n_permutations=200,
        )
    with pytest.raises(ValueError, match="sealed protocol count"):
        full_label_permutation_test(
            packets[0],
            **_protocol_kwargs(envelope),
            n_permutations=199,
            random_state=20260712,
        )
    with pytest.raises(ValueError, match="permutation random_state"):
        full_label_permutation_test(
            packets[0],
            **_protocol_kwargs(envelope),
            n_permutations=200,
            random_state=11,
        )

    fitted_labels: list[np.ndarray] = []

    class FakeModel:
        sklearn_version = "test"
        realized_logistic_regression: dict[str, object] = {}

        def predict_scores(
            self, pca_features: np.ndarray, scalar_features: np.ndarray
        ) -> np.ndarray:
            del scalar_features
            return pca_features[:, 0]

    def fake_fit(
        pca_features: np.ndarray,
        scalar_features: np.ndarray,
        labels: np.ndarray,
        contract: dict[str, object],
    ):
        del pca_features, scalar_features, contract
        fitted_labels.append(labels.copy())
        return FakeModel()

    monkeypatch.setattr(h1, "_fit_h1_arrays", fake_fit)
    result = full_label_permutation_test(
        packets[0],
        **_protocol_kwargs(envelope),
        n_permutations=200,
        random_state=20260712,
    )

    assert len(fitted_labels) == 201
    assert any(not np.array_equal(labels, fitted_labels[0]) for labels in fitted_labels[1:])
    assert all(int(labels.sum()) == 512 for labels in fitted_labels)
    assert len(result["null_aucs"]) == 200
    expected_p = (1 + sum(value >= result["observed_auc"] for value in result["null_aucs"])) / 201
    assert result["p_value"] == pytest.approx(expected_p)
    assert result["permutation_scheme"] == "within_each_split_and_class"
    json.dumps(result, allow_nan=False)
    repeated = full_label_permutation_test(
        packets[0],
        **_protocol_kwargs(envelope),
        n_permutations=200,
        random_state=20260712,
    )
    assert json.dumps(repeated, sort_keys=True) == json.dumps(result, sort_keys=True)


def test_scoring_rows_carry_complete_provenance_and_result_is_json_safe() -> None:
    envelope, packets = _make_setup()

    result = score_h1_checkpoints(packets, **_protocol_kwargs(envelope))

    target = result["targets"][0]
    assert "tpr_at_0_1pct_fpr" not in target["metrics"]
    row = target["evaluation_rows"][0]
    assert set(row) == {
        "dataset_index",
        "label",
        "class",
        "calibration_or_evaluation",
        "noise_id",
        "score",
    }
    assert set(target["target"]) == {
        "dataset_id",
        "run_seed",
        "step",
        "attack",
        "checkpoint_sha256",
        "training_manifest_sha256",
        "target_code_commit",
        "scorer_code_commit",
        "split_sha256",
        "protocol_hash",
        "run_label",
        "extraction_config",
        "extraction_config_hash",
        "evaluator_environment",
    }
    assert row["calibration_or_evaluation"] == "evaluation"
    json.dumps(result, allow_nan=False)
