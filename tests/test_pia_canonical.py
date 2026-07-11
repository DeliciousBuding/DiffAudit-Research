from __future__ import annotations

import numpy as np
import pytest
import torch
from sklearn.metrics import balanced_accuracy_score, roc_auc_score

from diffaudit.attacks.pia_canonical import (
    apply_membership_threshold,
    calibrate_membership_threshold,
    evaluate_calibrated_packets,
    score_pia_canonical,
)


class AnalyticOracle:
    def __init__(self, member_ids: set[int], *, signal: float = 0.35) -> None:
        self.member_ids = member_ids
        self.signal = signal
        self.queries: list[int] = []
        self._batch_membership: torch.Tensor | None = None

    def __call__(self, inputs: torch.Tensor, timesteps: torch.Tensor) -> torch.Tensor:
        assert inputs.min() >= -1 and inputs.max() <= 1
        assert timesteps.shape == (inputs.shape[0],)
        timestep = int(timesteps[0])
        assert torch.all(timesteps == timestep)
        self.queries.append(timestep)
        base = torch.full_like(inputs, 0.1)
        if timestep == 0:
            ids = torch.round(inputs[:, 0, 0, 0] * 1000).to(torch.int64)
            self._batch_membership = torch.tensor(
                [int(item) in self.member_ids for item in ids], device=inputs.device
            ).view(-1, 1, 1, 1)
        if timestep == 200 and self.signal:
            assert self._batch_membership is not None
            base = base + (~self._batch_membership).to(inputs.dtype) * self.signal
        return base


def _rows(ids: np.ndarray) -> torch.Tensor:
    result = torch.zeros(len(ids), 3, 2, 2, dtype=torch.float64)
    result[:, 0, 0, 0] = torch.from_numpy(ids).to(torch.float64) / 1000
    return result


def _scores(member_ids: np.ndarray, nonmember_ids: np.ndarray, signal: float = 0.35):
    ids = np.concatenate([member_ids, nonmember_ids])
    labels = np.concatenate([np.ones(len(member_ids)), np.zeros(len(nonmember_ids))])
    oracle = AnalyticOracle(set(map(int, member_ids)), signal=signal)
    scores, residuals = score_pia_canonical(
        oracle, _rows(ids), torch.linspace(1e-4, 0.02, 1000, dtype=torch.float64), diagnostics=True
    )
    return scores.numpy(), residuals.numpy(), labels, oracle


def test_eq9_matches_hand_calculation_and_exact_query_contract() -> None:
    scores, residuals, _, oracle = _scores(np.array([1, 2]), np.array([3, 4]))
    expected_nonmember = np.linalg.norm(np.full(12, 0.35), ord=4)
    np.testing.assert_allclose(residuals[:2], 0.0, rtol=1e-6, atol=1e-6)
    np.testing.assert_allclose(residuals[2:], expected_nonmember, rtol=1e-6, atol=1e-6)
    np.testing.assert_allclose(scores, -residuals, rtol=1e-6, atol=1e-6)
    assert oracle.queries == [0, 200]


@pytest.mark.parametrize(
    "bad_input, message",
    [
        (torch.zeros(2, 3, 2), "four-dimensional"),
        (torch.full((2, 3, 2, 2), 1.01), r"\[-1, 1\]"),
        (torch.zeros(2, 3, 2, 2, dtype=torch.int64), "floating point"),
    ],
)
def test_input_contract_rejects_invalid_rows(bad_input: torch.Tensor, message: str) -> None:
    with pytest.raises((TypeError, ValueError), match=message):
        score_pia_canonical(AnalyticOracle(set()), bad_input, torch.linspace(1e-4, 0.02, 1000))


def test_timestep_lp_and_beta_contract_are_frozen() -> None:
    rows = torch.zeros(2, 3, 2, 2)
    betas = torch.linspace(1e-4, 0.02, 1000)
    with pytest.raises(ValueError, match="timestep must be 200"):
        score_pia_canonical(AnalyticOracle(set()), rows, betas, timestep=199)
    with pytest.raises(ValueError, match="lp_order must be 4"):
        score_pia_canonical(AnalyticOracle(set()), rows, betas, lp_order=2)
    with pytest.raises(ValueError, match="1000"):
        score_pia_canonical(AnalyticOracle(set()), rows, betas[:-1])


def test_cpu_positive_control_and_calibration_only_threshold_gate() -> None:
    cal_member, cal_nonmember = np.arange(1, 129), np.arange(201, 329)
    eval_member, eval_nonmember = np.arange(401, 529), np.arange(601, 729)
    cal_scores, _, cal_labels, _ = _scores(cal_member, cal_nonmember)
    eval_scores, _, eval_labels, _ = _scores(eval_member, eval_nonmember)
    threshold = calibrate_membership_threshold(cal_scores, cal_labels)
    evaluated = apply_membership_threshold(eval_scores, eval_labels, threshold)
    positive_auc = roc_auc_score(eval_labels, eval_scores)
    assert positive_auc >= 0.95
    assert evaluated["balanced_accuracy"] >= 0.90
    assert evaluated["fpr"] <= 0.05
    assert roc_auc_score(eval_labels, -eval_scores) <= 0.05

    zero_scores, _, zero_labels, _ = _scores(eval_member, eval_nonmember, signal=0.0)
    assert roc_auc_score(zero_labels, zero_scores) == pytest.approx(0.5)

    rng = np.random.default_rng(20260712)
    null_aucs = [roc_auc_score(rng.permutation(eval_labels), eval_scores) for _ in range(200)]
    assert 0.45 <= float(np.mean(null_aucs)) <= 0.55
    assert positive_auc > max(null_aucs)
    assert balanced_accuracy_score(eval_labels, evaluated["predictions"]) >= 0.90


def test_threshold_depends_only_on_calibration_labels_and_rejects_overlap() -> None:
    cal_scores = np.array([0.9, 0.8, 0.2, 0.1])
    eval_scores = np.array([0.7, 0.3])
    first = evaluate_calibrated_packets(
        cal_scores,
        np.array([1, 1, 0, 0]),
        np.arange(4),
        eval_scores,
        np.array([1, 0]),
        np.arange(10, 12),
    )
    relabeled_eval = evaluate_calibrated_packets(
        cal_scores,
        np.array([1, 1, 0, 0]),
        np.arange(4),
        eval_scores,
        np.array([0, 1]),
        np.arange(10, 12),
    )
    changed_cal = evaluate_calibrated_packets(
        cal_scores,
        np.array([1, 0, 1, 0]),
        np.arange(4),
        eval_scores,
        np.array([1, 0]),
        np.arange(10, 12),
    )
    assert first["threshold"] == relabeled_eval["threshold"]
    assert first["threshold"] != changed_cal["threshold"]
    with pytest.raises(ValueError, match="disjoint"):
        evaluate_calibrated_packets(
            cal_scores,
            np.array([1, 1, 0, 0]),
            np.arange(4),
            eval_scores,
            np.array([1, 0]),
            np.array([3, 10]),
        )
