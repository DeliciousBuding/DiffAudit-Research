from __future__ import annotations

import inspect
from pathlib import Path

import numpy as np
import pytest
import torch

import diffaudit.attacks.pia_canonical as pia
from diffaudit.utils.metrics import auc_score


def _api(name: str):
    value = getattr(pia, name, None)
    assert callable(value), f"missing canonical PIA API: {name}"
    return value


class AnalyticEquationOracle:
    """Closed-form Eq. 9 regression oracle with no membership semantics."""

    def __init__(self, residual: float = 0.35) -> None:
        self.residual = residual
        self.queries: list[int] = []

    def __call__(self, inputs: torch.Tensor, timesteps: torch.Tensor) -> torch.Tensor:
        assert inputs.min() >= -1 and inputs.max() <= 1
        timestep = int(timesteps[0])
        assert torch.all(timesteps == timestep)
        self.queries.append(timestep)
        base = torch.full_like(inputs, 0.1)
        if timestep == 200:
            base += self.residual
        return base


def _rows(ids: np.ndarray) -> torch.Tensor:
    result = torch.zeros(len(ids), 3, 2, 2, dtype=torch.float64)
    result[:, 0, 0, 0] = torch.from_numpy(ids).to(torch.float64) / 1000
    return result


def _labels(member_count: int, nonmember_count: int) -> np.ndarray:
    return np.concatenate(
        [np.ones(member_count, dtype=np.int64), np.zeros(nonmember_count, dtype=np.int64)]
    )


def _balanced_accuracy(labels: np.ndarray, predictions: np.ndarray) -> float:
    tpr = float(predictions[labels == 1].mean())
    tnr = float((predictions[labels == 0] == 0).mean())
    return (tpr + tnr) / 2.0


def test_eq9_matches_hand_calculation_and_exact_query_contract() -> None:
    oracle = AnalyticEquationOracle()
    scores, residuals = pia.score_pia_canonical(
        oracle,
        _rows(np.array([1, 2, 3, 4])),
        torch.linspace(1e-4, 0.02, 1000, dtype=torch.float64),
        diagnostics=True,
    )

    expected = np.linalg.norm(np.full(12, 0.35), ord=4)
    np.testing.assert_allclose(residuals.numpy(), expected, rtol=1e-6, atol=1e-6)
    np.testing.assert_allclose(scores.numpy(), -residuals.numpy(), rtol=1e-6, atol=1e-6)
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
        pia.score_pia_canonical(
            AnalyticEquationOracle(), bad_input, torch.linspace(1e-4, 0.02, 1000)
        )


def test_timestep_lp_and_beta_contract_are_frozen() -> None:
    rows = torch.zeros(2, 3, 2, 2)
    betas = torch.linspace(1e-4, 0.02, 1000)
    with pytest.raises(ValueError, match="timestep must be 200"):
        pia.score_pia_canonical(AnalyticEquationOracle(), rows, betas, timestep=199)
    with pytest.raises(ValueError, match="lp_order must be 4"):
        pia.score_pia_canonical(AnalyticEquationOracle(), rows, betas, lp_order=2)
    with pytest.raises(ValueError, match="1000"):
        pia.score_pia_canonical(AnalyticEquationOracle(), rows, betas[:-1])


class NonFiniteOracle:
    def __init__(self, failure: str) -> None:
        self.failure = failure
        self.calls = 0

    def __call__(self, inputs: torch.Tensor, timesteps: torch.Tensor) -> torch.Tensor:
        del timesteps
        self.calls += 1
        if self.failure == "first_epsilon" and self.calls == 1:
            return torch.full_like(inputs, torch.nan)
        if self.failure == "x_t" and self.calls == 1:
            inputs.fill_(torch.inf)
            return torch.zeros_like(inputs)
        if self.failure == "second_epsilon" and self.calls == 2:
            return torch.full_like(inputs, torch.inf)
        if self.failure == "distance":
            magnitude = torch.finfo(inputs.dtype).max * 0.75
            return torch.full_like(inputs, magnitude if self.calls == 1 else -magnitude)
        return torch.zeros_like(inputs)


@pytest.mark.parametrize("failure", ["first_epsilon", "x_t", "second_epsilon", "distance"])
def test_scorer_rejects_every_non_finite_numeric_stage(failure: str) -> None:
    with pytest.raises(ValueError, match="finite|x_t|distance|score"):
        pia.score_pia_canonical(
            NonFiniteOracle(failure),
            torch.zeros(2, 3, 2, 2),
            torch.linspace(1e-4, 0.02, 1000),
        )


class MemorizationBankEpsilonModel(torch.nn.Module):
    """Label-blind toy epsilon model loaded from a CPU checkpoint."""

    def __init__(
        self,
        member_bank: torch.Tensor,
        *,
        alpha_bar_t: torch.Tensor,
        signal: float,
    ) -> None:
        super().__init__()
        self.register_buffer("member_bank", member_bank.clone())
        self.register_buffer("alpha_bar_t", alpha_bar_t.clone())
        self.signal = float(signal)

    def forward(self, inputs: torch.Tensor, timesteps: torch.Tensor) -> torch.Tensor:
        base = torch.full_like(inputs, 0.1)
        timestep = int(timesteps[0])
        assert torch.all(timesteps == timestep)
        if timestep == 0 or self.signal == 0.0:
            return base
        reconstructed_x0 = (
            inputs - (1.0 - self.alpha_bar_t).sqrt() * base
        ) / self.alpha_bar_t.sqrt()
        distances = torch.amax(
            torch.abs(
                reconstructed_x0.flatten(start_dim=1)[:, None, :]
                - self.member_bank.flatten(start_dim=1)[None, :, :]
            ),
            dim=2,
        )
        matched = distances.min(dim=1).values <= 1e-8
        return base + (~matched).to(inputs.dtype).view(-1, 1, 1, 1) * self.signal


def _save_and_load_memorization_checkpoint(
    path: Path,
    *,
    member_bank: torch.Tensor,
    alpha_bar_t: torch.Tensor,
    signal: float,
) -> MemorizationBankEpsilonModel:
    torch.save(
        {
            "member_bank": member_bank,
            "alpha_bar_t": alpha_bar_t,
            "signal": torch.tensor(signal, dtype=member_bank.dtype),
        },
        path,
    )
    checkpoint = torch.load(path, map_location="cpu", weights_only=True)
    return MemorizationBankEpsilonModel(
        checkpoint["member_bank"],
        alpha_bar_t=checkpoint["alpha_bar_t"],
        signal=float(checkpoint["signal"]),
    )


def _checkpoint_scores(
    model: MemorizationBankEpsilonModel,
    member_ids: np.ndarray,
    nonmember_ids: np.ndarray,
    betas: torch.Tensor,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ids = np.concatenate([member_ids, nonmember_ids])
    scores = pia.score_pia_canonical(model, _rows(ids), betas).numpy()
    return scores, _labels(len(member_ids), len(nonmember_ids)), ids


def test_label_blind_loaded_checkpoint_clears_the_full_synthetic_control_gate(
    tmp_path: Path,
) -> None:
    betas = torch.linspace(1e-4, 0.02, 1000, dtype=torch.float64)
    alpha_bar_t = torch.cumprod(1.0 - betas, dim=0)[200]
    calibration_member = np.arange(1, 129)
    calibration_nonmember = np.arange(129, 257)
    evaluation_member = np.arange(257, 385)
    evaluation_nonmember = np.arange(385, 513)
    member_bank = _rows(np.concatenate([calibration_member, evaluation_member]))

    positive_model = _save_and_load_memorization_checkpoint(
        tmp_path / "positive.pt",
        member_bank=member_bank,
        alpha_bar_t=alpha_bar_t,
        signal=0.35,
    )
    zero_model = _save_and_load_memorization_checkpoint(
        tmp_path / "zero.pt",
        member_bank=member_bank,
        alpha_bar_t=alpha_bar_t,
        signal=0.0,
    )
    assert "labels" not in inspect.signature(positive_model.forward).parameters

    calibration_scores, calibration_labels, calibration_ids = _checkpoint_scores(
        positive_model, calibration_member, calibration_nonmember, betas
    )
    evaluation_scores, evaluation_labels, evaluation_ids = _checkpoint_scores(
        positive_model, evaluation_member, evaluation_nonmember, betas
    )
    zero_scores, zero_labels, _ = _checkpoint_scores(
        zero_model, evaluation_member, evaluation_nonmember, betas
    )

    result = _api("aggregate_synthetic_checkpoint_positive_control")(
        calibration_scores,
        calibration_labels,
        calibration_ids,
        evaluation_scores,
        evaluation_labels,
        evaluation_ids,
        zero_scores,
        zero_labels,
    )

    assert set(calibration_ids).isdisjoint(evaluation_ids)
    assert result["status"] == "synthetic_checkpoint_positive_control_passed"
    assert result["evidence_scope"] == "synthetic_checkpoint_positive_control_only"
    assert result["real_model_evidence"] is False
    assert result["metrics"]["evaluation_auc"] >= 0.95
    assert result["metrics"]["evaluation_balanced_accuracy"] >= 0.90
    assert result["metrics"]["evaluation_fpr"] <= 0.05
    assert result["metrics"]["negative_score_auc"] <= 0.05
    assert 0.45 <= result["metrics"]["zero_signal_auc"] <= 0.55
    assert 0.45 <= result["metrics"]["permutation_auc_mean"] <= 0.55
    assert result["metrics"]["evaluation_auc"] > result["metrics"]["permutation_auc_max"]


def test_synthetic_checkpoint_positive_control_rejects_32_per_class() -> None:
    labels = _labels(32, 32)
    scores = np.concatenate([np.ones(32), np.zeros(32)])

    with pytest.raises(ValueError, match="exactly 128 members and 128 nonmembers"):
        _api("aggregate_synthetic_checkpoint_positive_control")(
            scores,
            labels,
            np.arange(64),
            scores,
            labels,
            np.arange(100, 164),
            np.zeros(64),
            labels,
        )


def test_threshold_depends_only_on_calibration_and_heldout_metrics_are_fixed_direction() -> None:
    calibration_scores = np.array([0.9, 0.8, 0.2, 0.1])
    evaluation_scores = np.array([0.7, 0.7, 0.3, 0.3])
    first = pia.evaluate_calibrated_packets(
        calibration_scores,
        np.array([1, 1, 0, 0]),
        np.arange(4),
        evaluation_scores,
        np.array([1, 0, 1, 0]),
        np.arange(10, 14),
    )
    relabeled_evaluation = pia.evaluate_calibrated_packets(
        calibration_scores,
        np.array([1, 1, 0, 0]),
        np.arange(4),
        evaluation_scores,
        np.array([0, 1, 0, 1]),
        np.arange(10, 14),
    )

    assert first["calibration_threshold"] == relabeled_evaluation["calibration_threshold"]
    assert first["evaluation_auc"] == pytest.approx(
        auc_score(evaluation_scores, np.array([1, 0, 1, 0]))
    )
    assert first["tpr_at_1pct_fpr"] == 0.0
    assert first["tpr_at_1pct_fpr_fpr_cap"] == 0.01
    assert len(first["tpr_at_1pct_fpr_wilson_95_ci"]) == 2
    assert "tpr_at_0_1pct_fpr" not in first
    assert first["evaluation_balanced_accuracy"] == _balanced_accuracy(
        np.array([1, 0, 1, 0]), first["predictions"]
    )
    with pytest.raises(ValueError, match="disjoint"):
        pia.evaluate_calibrated_packets(
            calibration_scores,
            np.array([1, 1, 0, 0]),
            np.arange(4),
            evaluation_scores,
            np.array([1, 0, 1, 0]),
            np.array([3, 10, 11, 12]),
        )


def test_threshold_tie_includes_all_negative_candidate_and_minimizes_fpr() -> None:
    scores = np.array([0.1, 0.2, 0.8, 0.9])
    labels = np.array([1, 1, 0, 0])

    threshold = pia.calibrate_membership_threshold(scores, labels)
    applied = pia.apply_membership_threshold(scores, labels, threshold)

    assert np.isfinite(threshold)
    assert threshold > float(scores.max())
    assert applied["evaluation_balanced_accuracy"] == pytest.approx(0.5)
    assert applied["evaluation_fpr"] == 0.0
    np.testing.assert_array_equal(applied["predictions"], np.zeros(4, dtype=np.int64))
