from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest

import diffaudit.attacks.pia_canonical as pia
from diffaudit.attacks import pia_adapter
from diffaudit.evidence.corrected_protocol import (
    build_paper1_corrected_contract,
    build_protocol_envelope,
)
from diffaudit.training.corrected_ddpm import (
    build_training_config,
    canonical_training_config_hash,
)
from diffaudit.utils.metrics import auc_score, tpr_at_fpr_with_wilson

CODE_COMMIT = "c" * 40
SPLIT_SHA256 = "d" * 64


@pytest.fixture(autouse=True)
def clean_analysis_repository_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        pia_adapter,
        "read_pia_repository_state",
        lambda _root: (CODE_COMMIT, "", ()),
    )


@pytest.fixture(scope="module")
def protocol_envelope() -> dict[str, object]:
    contract = build_paper1_corrected_contract(
        split_filename="CIFAR10_train_ratio0.5.npz",
        split_sha256=SPLIT_SHA256,
        member_indices=tuple(range(25_000)),
        nonmember_indices=tuple(range(25_000, 50_000)),
        class_labels=np.arange(50_000, dtype=np.int64) % 10,
        code_commit=CODE_COMMIT,
    )
    return build_protocol_envelope(contract)


def _noise_id(protocol_hash: str, dataset_index: int) -> str:
    encoded = json.dumps(
        [protocol_hash, dataset_index, 200, "pia-e0"],
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _target_source(
    tmp_path: Path,
    envelope: dict[str, object],
    *,
    seed: int,
    step: int,
    target_offset: float = 0.0,
) -> tuple[dict[str, object], dict[str, object], Path]:
    checkpoint_sha256 = hashlib.sha256(f"{seed}:{step}".encode("ascii")).hexdigest()
    run_label = f"corrected-s{seed}"
    config_hash = canonical_training_config_hash(build_training_config())
    checkpoint_name = f"checkpoint-step{step:06d}.pt"
    manifest_payload = {
        "protocol_hash": envelope["protocol_hash"],
        "split_sha256": SPLIT_SHA256,
        "code_commit": CODE_COMMIT,
        "seed": seed,
        "run_label": run_label,
        "step": step,
        "training_config_hash": config_hash,
        "checkpoint_receipts": {
            checkpoint_name: {
                "checkpoint_sha256": checkpoint_sha256,
                "protocol_hash": envelope["protocol_hash"],
                "code_commit": CODE_COMMIT,
                "run_seed": seed,
                "step": step,
                "run_label": run_label,
                "training_config_hash": config_hash,
            }
        },
    }
    manifest_path = tmp_path / f"training-manifest-{seed}-{step}.json"
    manifest_path.write_text(json.dumps(manifest_payload), encoding="utf-8")
    manifest_sha256 = hashlib.sha256(manifest_path.read_bytes()).hexdigest()

    contract = envelope["contract"]
    assert isinstance(contract, dict)
    evaluation = contract["evaluation"]
    assert isinstance(evaluation, dict)
    manifest_rows = evaluation["rows"]
    assert isinstance(manifest_rows, list)
    protocol_hash = envelope["protocol_hash"]
    assert isinstance(protocol_hash, str)

    packets: dict[str, dict[str, object]] = {}
    for role in ("calibration", "evaluation"):
        rows: list[dict[str, object]] = []
        for raw_row in manifest_rows:
            assert isinstance(raw_row, dict)
            if raw_row["split"] != role:
                continue
            label = int(raw_row["label"])
            dataset_index = int(raw_row["dataset_index"])
            rows.append(
                {
                    "dataset_id": "CIFAR10",
                    "dataset_index": dataset_index,
                    "label": label,
                    "class": int(raw_row["class_id"]),
                    "calibration_or_evaluation": role,
                    "score": float(0.75 * label + 0.1 + target_offset),
                    "noise_id": _noise_id(protocol_hash, dataset_index),
                }
            )
        packets[role] = {
            "schema_version": 1,
            "attack": "pia",
            "variant": "pia",
            "timestep": 200,
            "lp_order": 4,
            "score_form": "negative_lp_norm",
            "score_direction": "higher_is_member",
            "input_range": [-1.0, 1.0],
            "packet_purpose": "corrected_evaluation",
            "run_seed": seed,
            "step": step,
            "checkpoint_sha256": checkpoint_sha256,
            "training_manifest_sha256": manifest_sha256,
            "target_code_commit": CODE_COMMIT,
            "scorer_code_commit": CODE_COMMIT,
            "split_sha256": SPLIT_SHA256,
            "protocol_hash": protocol_hash,
            "rows": rows,
        }
    return packets["calibration"], packets["evaluation"], manifest_path


def _stage_sources(
    tmp_path: Path,
    envelope: dict[str, object],
    stage: str = "stage1",
) -> list[tuple[dict[str, object], dict[str, object], Path]]:
    contract = envelope["contract"]
    assert isinstance(contract, dict)
    h1 = contract["h1"]
    assert isinstance(h1, dict)
    roster = h1["cross_target_rosters"][stage]
    return [
        _target_source(tmp_path, envelope, seed=int(seed), step=int(roster["step"]))
        for seed in roster["seeds"]
    ]


def _protocol_kwargs(envelope: dict[str, object]) -> dict[str, object]:
    return {
        "protocol_envelope": envelope,
        "expected_protocol_hash": envelope["protocol_hash"],
    }


def _analysis_contract_hash(envelope: dict[str, object]) -> str:
    contract = envelope["contract"]
    assert isinstance(contract, dict)
    payload = {
        "pia": contract["pia"],
        "confirmatory_heterogeneity": contract["confirmatory_heterogeneity"],
    }
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@pytest.mark.parametrize("analysis", ["score", "bootstrap", "permutation"])
@pytest.mark.parametrize(
    ("repository_state", "message"),
    [
        (("e" * 40, "", ()), "HEAD"),
        ((CODE_COMMIT, " M src/diffaudit/attacks/pia_canonical.py", ()), "tracked worktree"),
        ((CODE_COMMIT, "", ("src/diffaudit/attacks/untracked.py",)), "untracked scorer"),
    ],
)
def test_confirmatory_execution_rejects_unsealed_repository_state_before_analysis(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
    analysis: str,
    repository_state: tuple[str, str, tuple[str, ...]],
    message: str,
) -> None:
    sources = _stage_sources(tmp_path, protocol_envelope)
    monkeypatch.setattr(
        pia_adapter,
        "read_pia_repository_state",
        lambda _root: repository_state,
    )

    def fail_if_analysis_starts(*_args: object, **_kwargs: object) -> dict[str, object]:
        raise AssertionError("repository gate must run before confirmatory analysis")

    monkeypatch.setattr(pia, "evaluate_calibrated_packets", fail_if_analysis_starts)
    with pytest.raises(ValueError, match=message):
        if analysis == "score":
            pia.score_pia_checkpoints(sources[:1], **_protocol_kwargs(protocol_envelope))
        elif analysis == "bootstrap":
            pia.bootstrap_pia_checkpoints(
                sources,
                **_protocol_kwargs(protocol_envelope),
                n_bootstrap=1000,
                random_state=20260711,
                analysis_mode="cross_target_same_step",
                stage="stage1",
            )
        else:
            pia.full_label_permutation_test_pia(
                sources[0],
                **_protocol_kwargs(protocol_envelope),
                n_permutations=200,
                random_state=20260712,
            )


def test_cross_target_scoring_requires_the_complete_sealed_same_step_roster(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
) -> None:
    sources = _stage_sources(tmp_path, protocol_envelope)
    result = pia.score_pia_checkpoints(
        sources,
        **_protocol_kwargs(protocol_envelope),
        analysis_mode="cross_target_same_step",
        stage="stage1",
    )
    assert len(result["targets"]) == 4
    reversed_result = pia.score_pia_checkpoints(
        list(reversed(sources)),
        **_protocol_kwargs(protocol_envelope),
        analysis_mode="cross_target_same_step",
        stage="stage1",
    )
    if json.dumps(reversed_result, sort_keys=True) != json.dumps(result, sort_keys=True):
        pytest.fail("reversed roster changed canonical score JSON")

    contract = protocol_envelope["contract"]
    assert isinstance(contract, dict)
    h1 = contract["h1"]
    assert isinstance(h1, dict)
    replicate = h1["cross_target_rosters"]["replicate"]
    extra = _target_source(
        tmp_path,
        protocol_envelope,
        seed=int(replicate["seeds"][0]),
        step=int(replicate["step"]),
    )
    mature = h1["cross_target_rosters"]["mature"]
    wrong_step = _target_source(
        tmp_path,
        protocol_envelope,
        seed=int(mature["seeds"][0]),
        step=int(mature["step"]),
    )
    failures = {
        "missing": sources[:-1],
        "extra": [*sources[:-1], extra],
        "duplicate": [*sources[:-1], sources[0]],
        "wrong step": [wrong_step, *sources[1:]],
    }
    for message, invalid_sources in failures.items():
        with pytest.raises(ValueError, match=message):
            pia.score_pia_checkpoints(
                invalid_sources,
                **_protocol_kwargs(protocol_envelope),
                analysis_mode="cross_target_same_step",
                stage="stage1",
            )


def test_full_stage_roster_combines_all_eight_predeclared_targets(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
) -> None:
    result = pia.score_pia_checkpoints(
        _stage_sources(tmp_path, protocol_envelope, stage="full"),
        **_protocol_kwargs(protocol_envelope),
        analysis_mode="cross_target_same_step",
        stage="full",
    )

    assert len(result["targets"]) == 8


@pytest.mark.parametrize("stage", ["replicate", "mature"])
def test_replicate_and_mature_rosters_accept_only_their_complete_seed_sets(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    stage: str,
) -> None:
    sources = _stage_sources(tmp_path, protocol_envelope, stage=stage)
    result = pia.score_pia_checkpoints(
        sources,
        **_protocol_kwargs(protocol_envelope),
        analysis_mode="cross_target_same_step",
        stage=stage,
    )

    assert result["stage"] == stage
    assert len(result["targets"]) == 4
    with pytest.raises(ValueError) as error:
        pia.score_pia_checkpoints(
            sources[:-1],
            **_protocol_kwargs(protocol_envelope),
            analysis_mode="cross_target_same_step",
            stage=stage,
        )
    assert str(error.value) == "cross-target roster has a missing seed"


def test_mature_roster_rejects_the_stage1_step_exactly(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
) -> None:
    with pytest.raises(ValueError) as error:
        pia.score_pia_checkpoints(
            _stage_sources(tmp_path, protocol_envelope, stage="stage1"),
            **_protocol_kwargs(protocol_envelope),
            analysis_mode="cross_target_same_step",
            stage="mature",
        )

    assert str(error.value) == "cross-target roster has a wrong step"


def test_checkpoint_scoring_is_calibration_only_held_out_and_provenance_bound(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
) -> None:
    contract = protocol_envelope["contract"]
    assert isinstance(contract, dict)
    stage1 = contract["h1"]["cross_target_rosters"]["stage1"]
    source = _target_source(
        tmp_path,
        protocol_envelope,
        seed=int(stage1["seeds"][0]),
        step=int(stage1["step"]),
    )
    calibration, evaluation, manifest = source
    for row in calibration["rows"]:
        row["score"] = 0.9 if row["label"] == 1 else 0.2
    for position, row in enumerate(evaluation["rows"]):
        if row["label"] == 1:
            row["score"] = 0.7 if position % 2 == 0 else 0.4
        else:
            row["score"] = 0.7 if position % 2 == 0 else 0.3

    result = pia.score_pia_checkpoints(
        [(calibration, evaluation, manifest)],
        **_protocol_kwargs(protocol_envelope),
    )
    target = result["targets"][0]
    assert result["analysis_code_commit"] == CODE_COMMIT
    assert result["analysis_contract_hash"] == _analysis_contract_hash(protocol_envelope)
    metrics = target["metrics"]
    evaluation_scores = np.asarray([row["score"] for row in evaluation["rows"]])
    evaluation_labels = np.asarray([row["label"] for row in evaluation["rows"]])
    expected_tpr = tpr_at_fpr_with_wilson(
        evaluation_scores,
        evaluation_labels,
        target_fpr=0.01,
    )

    assert metrics["calibration_threshold"] == pytest.approx(0.9)
    assert metrics["evaluation_auc"] == pytest.approx(
        auc_score(evaluation_scores, evaluation_labels)
    )
    assert metrics["tpr_at_1pct_fpr"] == expected_tpr["estimate"]
    assert metrics["tpr_at_1pct_fpr_wilson_95_ci"] == expected_tpr["wilson_95_ci"]
    assert "tpr_at_0_1pct_fpr" not in metrics
    assert len(target["evaluation_rows"]) == 1024
    assert set(target["evaluation_rows"][0]) == {
        "dataset_index",
        "label",
        "class",
        "calibration_or_evaluation",
        "noise_id",
        "score",
    }
    provenance = target["target"]
    assert {
        provenance["target_code_commit"],
        provenance["scorer_code_commit"],
        result["analysis_code_commit"],
    } == {CODE_COMMIT}
    assert {
        "run_seed",
        "step",
        "checkpoint_sha256",
        "training_manifest_sha256",
        "target_code_commit",
        "scorer_code_commit",
        "split_sha256",
        "protocol_hash",
        "calibration_packet_sha256",
        "evaluation_packet_sha256",
    } <= set(provenance)
    assert len(provenance["calibration_packet_sha256"]) == 64
    assert len(provenance["evaluation_packet_sha256"]) == 64
    json.dumps(result, allow_nan=False)

    changed_evaluation = deepcopy(evaluation)
    for row in changed_evaluation["rows"]:
        row["score"] = -float(row["score"])
    changed = pia.score_pia_checkpoints(
        [(calibration, changed_evaluation, manifest)],
        **_protocol_kwargs(protocol_envelope),
    )
    assert changed["targets"][0]["metrics"]["calibration_threshold"] == pytest.approx(0.9)


def test_heterogeneity_uses_range_null_centering_practical_gate_and_holm() -> None:
    keys = ["a" * 64, "b" * 64, "c" * 64]
    observed = np.asarray([0.52, 0.58, 0.68])
    draws = np.asarray(
        [
            [0.50, 0.61, 0.64],
            [0.55, 0.55, 0.70],
            [0.51, 0.60, 0.69],
            [0.54, 0.57, 0.66],
        ]
    )

    result = pia.summarize_pia_heterogeneity(
        keys,
        observed,
        draws,
        alpha=0.05,
        practical_range=0.05,
    )
    null_draws = draws - observed[None, :] + float(observed.mean())
    null_ranges = np.ptp(null_draws, axis=1)
    expected_global_p = (1 + int((null_ranges >= np.ptp(observed)).sum())) / 5

    assert result["global"]["statistic"] == "auc_range"
    assert result["global"]["null_centering"] == "target_observed_to_grand_mean"
    assert result["global"]["observed_range"] == pytest.approx(0.16)
    assert result["global"]["null_ranges"] == pytest.approx(null_ranges.tolist())
    assert result["global"]["p_value"] == pytest.approx(expected_global_p)
    assert result["global"]["practical_range_at_least"] == 0.05
    assert result["global"]["practical_gate"] is True
    assert result["correction"] == "holm"
    assert len(result["pairwise"]) == 3
    assert all(row["test"] == "two_sided_centered_paired_bootstrap" for row in result["pairwise"])
    ordered = sorted(result["pairwise"], key=lambda row: row["raw_p_value"])
    assert [row["adjusted_p_value"] for row in ordered] == sorted(
        row["adjusted_p_value"] for row in ordered
    )

    below_practical = pia.summarize_pia_heterogeneity(
        keys[:2],
        [0.50, 0.549],
        [[0.50, 0.549], [0.51, 0.539]],
        alpha=0.05,
        practical_range=0.05,
    )
    assert below_practical["global"]["practical_gate"] is False
    json.dumps(result, allow_nan=False)


def test_thousand_draws_make_eight_target_holm_rejection_reachable() -> None:
    keys = [f"{index:064x}" for index in range(1, 9)]
    observed = np.linspace(0.50, 0.85, 8)
    draws = np.tile(observed, (1000, 1))

    result = pia.summarize_pia_heterogeneity(
        keys,
        observed,
        draws,
        alpha=0.05,
        practical_range=0.05,
    )

    assert len(result["pairwise"]) == 28
    minimum_reachable_holm = 28 / 1001
    assert minimum_reachable_holm < 0.05
    assert min(row["adjusted_p_value"] for row in result["pairwise"]) == pytest.approx(
        minimum_reachable_holm
    )
    assert all(row["decision"] is True for row in result["pairwise"])


def test_paired_bootstrap_shares_stratified_draws_recalibrates_and_is_sealed(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sources = _stage_sources(tmp_path, protocol_envelope)
    for target_index, (calibration, evaluation, _) in enumerate(sources):
        for packet in (calibration, evaluation):
            for row in packet["rows"]:
                row["score"] = float(
                    0.12 * row["label"]
                    + ((int(row["dataset_index"]) * (target_index + 3)) % 101) / 100.0
                )

    with pytest.raises(ValueError, match="sealed protocol count 1000"):
        pia.bootstrap_pia_checkpoints(
            sources,
            **_protocol_kwargs(protocol_envelope),
            n_bootstrap=999,
            random_state=20260711,
            analysis_mode="cross_target_same_step",
            stage="stage1",
        )
    with pytest.raises(ValueError, match="bootstrap random_state"):
        pia.bootstrap_pia_checkpoints(
            sources,
            **_protocol_kwargs(protocol_envelope),
            n_bootstrap=1000,
            random_state=7,
            analysis_mode="cross_target_same_step",
            stage="stage1",
        )

    calls: list[tuple[np.ndarray, np.ndarray]] = []
    real_evaluate = pia.evaluate_calibrated_packets

    def capture_evaluate(
        calibration_scores: np.ndarray,
        calibration_labels: np.ndarray,
        calibration_indices: np.ndarray,
        evaluation_scores: np.ndarray,
        evaluation_labels: np.ndarray,
        evaluation_indices: np.ndarray,
    ) -> dict[str, object]:
        calls.append((calibration_indices.copy(), evaluation_indices.copy()))
        return real_evaluate(
            calibration_scores,
            calibration_labels,
            calibration_indices,
            evaluation_scores,
            evaluation_labels,
            evaluation_indices,
        )

    monkeypatch.setattr(pia, "evaluate_calibrated_packets", capture_evaluate)
    result = pia.bootstrap_pia_checkpoints(
        sources,
        **_protocol_kwargs(protocol_envelope),
        n_bootstrap=1000,
        random_state=20260711,
        analysis_mode="cross_target_same_step",
        stage="stage1",
    )

    assert len(calls) == 4004
    for offset in range(4, 4004, 4):
        for target_offset in range(1, 4):
            np.testing.assert_array_equal(calls[offset][0], calls[offset + target_offset][0])
            np.testing.assert_array_equal(calls[offset][1], calls[offset + target_offset][1])
    assert result["n_bootstrap"] == 1000
    assert result["random_state"] == 20260711
    assert result["analysis_code_commit"] == CODE_COMMIT
    assert result["analysis_contract_hash"] == _analysis_contract_hash(protocol_envelope)
    assert all(
        {
            row["target"]["target_code_commit"],
            row["target"]["scorer_code_commit"],
            result["analysis_code_commit"],
        }
        == {CODE_COMMIT}
        for row in result["targets"]
    )
    assert result["strata"] == ["calibration_or_evaluation", "label", "class"]
    assert len(result["paired_replicates"]) == 1000
    assert all(len(row["shared_draw_sha256"]) == 64 for row in result["paired_replicates"])
    assert len(result["targets"]) == 4
    assert all(len(row["auc_samples"]) == 1000 for row in result["targets"])
    assert all(len(row["calibration_threshold_samples"]) == 1000 for row in result["targets"])
    assert all(len(row["auc_ci_95"]) == 2 for row in result["targets"])
    assert len(result["pairwise_deltas"]) == 6
    assert all(len(row["samples"]) == 1000 for row in result["pairwise_deltas"])
    assert "heterogeneity_summary" in result
    json.dumps(result, allow_nan=False)

    repeated = pia.bootstrap_pia_checkpoints(
        list(reversed(sources)),
        **_protocol_kwargs(protocol_envelope),
        n_bootstrap=1000,
        random_state=20260711,
        analysis_mode="cross_target_same_step",
        stage="stage1",
    )
    if json.dumps(repeated, sort_keys=True) != json.dumps(result, sort_keys=True):
        pytest.fail("reversed roster changed canonical bootstrap JSON or pair orientation")


def test_full_label_permutation_is_split_class_preserving_recalibrated_and_plus_one(
    tmp_path: Path,
    protocol_envelope: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = protocol_envelope["contract"]
    assert isinstance(contract, dict)
    stage1 = contract["h1"]["cross_target_rosters"]["stage1"]
    source = _target_source(
        tmp_path,
        protocol_envelope,
        seed=int(stage1["seeds"][0]),
        step=int(stage1["step"]),
    )
    for packet in source[:2]:
        for row in packet["rows"]:
            row["score"] = float(
                0.15 * row["label"] + ((int(row["dataset_index"]) * 7) % 101) / 100.0
            )

    with pytest.raises(ValueError, match="sealed protocol count 200"):
        pia.full_label_permutation_test_pia(
            source,
            **_protocol_kwargs(protocol_envelope),
            n_permutations=199,
            random_state=20260712,
        )
    with pytest.raises(ValueError, match="permutation random_state"):
        pia.full_label_permutation_test_pia(
            source,
            **_protocol_kwargs(protocol_envelope),
            n_permutations=200,
            random_state=11,
        )

    calls: list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = []
    real_evaluate = pia.evaluate_calibrated_packets

    def capture_evaluate(
        calibration_scores: np.ndarray,
        calibration_labels: np.ndarray,
        calibration_indices: np.ndarray,
        evaluation_scores: np.ndarray,
        evaluation_labels: np.ndarray,
        evaluation_indices: np.ndarray,
    ) -> dict[str, object]:
        calls.append(
            (
                calibration_labels.copy(),
                calibration_indices.copy(),
                evaluation_labels.copy(),
                evaluation_indices.copy(),
            )
        )
        return real_evaluate(
            calibration_scores,
            calibration_labels,
            calibration_indices,
            evaluation_scores,
            evaluation_labels,
            evaluation_indices,
        )

    monkeypatch.setattr(pia, "evaluate_calibrated_packets", capture_evaluate)
    result = pia.full_label_permutation_test_pia(
        source,
        **_protocol_kwargs(protocol_envelope),
        n_permutations=200,
        random_state=20260712,
    )

    assert len(calls) == 201
    calibration_class = {int(row["dataset_index"]): int(row["class"]) for row in source[0]["rows"]}
    evaluation_class = {int(row["dataset_index"]): int(row["class"]) for row in source[1]["rows"]}

    def class_member_counts(
        labels: np.ndarray,
        indices: np.ndarray,
        class_by_index: dict[int, int],
    ) -> tuple[int, ...]:
        return tuple(
            int(
                labels[
                    np.asarray([class_by_index[int(index)] == class_id for index in indices])
                ].sum()
            )
            for class_id in range(10)
        )

    observed_calibration_counts = class_member_counts(calls[0][0], calls[0][1], calibration_class)
    observed_evaluation_counts = class_member_counts(calls[0][2], calls[0][3], evaluation_class)
    for calibration_labels, calibration_indices, evaluation_labels, evaluation_indices in calls[1:]:
        assert (
            class_member_counts(calibration_labels, calibration_indices, calibration_class)
            == observed_calibration_counts
        )
        assert (
            class_member_counts(evaluation_labels, evaluation_indices, evaluation_class)
            == observed_evaluation_counts
        )
    assert any(not np.array_equal(call[0], calls[0][0]) for call in calls[1:])
    assert any(not np.array_equal(call[2], calls[0][2]) for call in calls[1:])
    assert result["permutation_scheme"] == "within_each_split_and_class"
    assert result["recalibrate_threshold_per_permutation"] is True
    assert result["analysis_code_commit"] == CODE_COMMIT
    assert result["analysis_contract_hash"] == _analysis_contract_hash(protocol_envelope)
    assert {
        result["target"]["target_code_commit"],
        result["target"]["scorer_code_commit"],
        result["analysis_code_commit"],
    } == {CODE_COMMIT}
    assert len(result["null_aucs"]) == 200
    assert len(result["null_calibration_thresholds"]) == 200
    expected_p = (1 + sum(value >= result["observed_auc"] for value in result["null_aucs"])) / 201
    assert result["p_value"] == pytest.approx(expected_p)
    assert result["p_value_correction"] == "plus_one"
    assert len(result["target"]["calibration_packet_sha256"]) == 64
    assert len(result["target"]["evaluation_packet_sha256"]) == 64
    json.dumps(result, allow_nan=False)

    repeated = pia.full_label_permutation_test_pia(
        source,
        **_protocol_kwargs(protocol_envelope),
        n_permutations=200,
        random_state=20260712,
    )
    assert json.dumps(repeated, sort_keys=True) == json.dumps(result, sort_keys=True)
