"""Reusable H2 response-strength scoring utilities.

This module intentionally contains only cache/scoring logic. GPU response
collection belongs in a thin runner so future validation packets do not depend
on archived X-run scripts.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from diffaudit.utils.metrics import metric_bundle, round6

METRIC_KEYS = ("auc", "asr", "tpr_at_1pct_fpr", "tpr_at_0_1pct_fpr")
DEFAULT_TIMESTEPS = (40, 80, 120, 160)


def select_split_indices(member_split_path: str | Any, membership: str, offset: int, packet_size: int) -> list[int]:
    """Select a contiguous non-overlap packet from a PIA-style split file."""

    split_payload = np.load(member_split_path)
    if membership == "member":
        raw_indices = split_payload["mia_train_idxs"].tolist()
    elif membership == "nonmember":
        raw_indices = split_payload["mia_eval_idxs"].tolist()
    else:
        raise ValueError(f"Unknown membership: {membership}")
    start = int(offset)
    end = start + int(packet_size)
    selected = [int(value) for value in raw_indices[start:end]]
    if len(selected) != int(packet_size):
        raise ValueError(
            f"Requested {packet_size} {membership} samples at offset {offset}, but only got {len(selected)}"
        )
    return selected


def metric_delta(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    """Return rounded metric differences for the common admission metrics."""

    return {key: round6(float(left[key]) - float(right[key])) for key in METRIC_KEYS}


def score_metrics(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    """Compute H2-compatible metrics including class-conditional means."""

    labels_i64 = np.asarray(labels, dtype=np.int64)
    scores_f64 = np.asarray(scores, dtype=np.float64)
    metrics = metric_bundle(scores_f64, labels_i64)
    metrics["member_score_mean"] = round6(float(scores_f64[labels_i64 == 1].mean()))
    metrics["nonmember_score_mean"] = round6(float(scores_f64[labels_i64 == 0].mean()))
    return metrics


def bootstrap_metric_ci(
    labels: np.ndarray,
    scores: np.ndarray,
    *,
    seed: int,
    iters: int,
) -> dict[str, dict[str, float]]:
    """Bootstrap confidence intervals over member/nonmember resamples."""

    if iters <= 0:
        return {}
    labels_i64 = np.asarray(labels, dtype=np.int64)
    scores_f64 = np.asarray(scores, dtype=np.float64)
    rng = np.random.default_rng(seed)
    member_scores = scores_f64[labels_i64 == 1]
    nonmember_scores = scores_f64[labels_i64 == 0]
    values: dict[str, list[float]] = {key: [] for key in METRIC_KEYS}
    for _ in range(int(iters)):
        boot_member = rng.choice(member_scores, size=member_scores.shape[0], replace=True)
        boot_nonmember = rng.choice(nonmember_scores, size=nonmember_scores.shape[0], replace=True)
        boot_labels = np.concatenate(
            [
                np.ones(boot_member.shape[0], dtype=np.int64),
                np.zeros(boot_nonmember.shape[0], dtype=np.int64),
            ]
        )
        boot_scores = np.concatenate([boot_member, boot_nonmember])
        metrics = score_metrics(boot_labels, boot_scores)
        for key in METRIC_KEYS:
            values[key].append(float(metrics[key]))
    return {
        key: {
            "p025": round6(float(np.percentile(items, 2.5))),
            "p975": round6(float(np.percentile(items, 97.5))),
        }
        for key, items in values.items()
    }


def evaluate_h2_simple_scores(
    labels: np.ndarray,
    min_distances: np.ndarray,
    timesteps: np.ndarray,
    *,
    seed: int,
    bootstrap_iters: int = 0,
) -> dict[str, Any]:
    """Evaluate simple H2 distance scorers against membership labels."""

    labels_i64 = np.asarray(labels, dtype=np.int64)
    distances = np.asarray(min_distances, dtype=np.float32)
    timestep_values = np.asarray(timesteps, dtype=np.int64)
    if distances.ndim != 2:
        raise ValueError("min_distances must have shape [sample, timestep]")
    if distances.shape[1] != timestep_values.shape[0]:
        raise ValueError("timesteps length must match min_distances second dimension")

    candidates: list[dict[str, Any]] = []
    for idx, timestep in enumerate(timestep_values.tolist()):
        scores = -distances[:, idx]
        candidates.append(
            {
                "name": f"single_timestep_{int(timestep)}",
                "score_orientation": "negative_min_distance_higher_is_member",
                "metrics": score_metrics(labels_i64, scores),
                "ci95": bootstrap_metric_ci(labels_i64, scores, seed=seed + idx, iters=bootstrap_iters),
            }
        )

    mean_scores = -distances.mean(axis=1)
    if distances.shape[1] > 1:
        slope = np.polyfit(timestep_values.astype(float), distances.T, deg=1)[0]
    else:
        slope = np.zeros(distances.shape[0], dtype=float)
    candidates.append(
        {
            "name": "mean_min_distance",
            "score_orientation": "negative_mean_min_distance_higher_is_member",
            "metrics": score_metrics(labels_i64, mean_scores),
            "ci95": bootstrap_metric_ci(labels_i64, mean_scores, seed=seed + 20, iters=bootstrap_iters),
        }
    )
    candidates.append(
        {
            "name": "negative_slope",
            "score_orientation": "negative_distance_slope_higher_is_member",
            "metrics": score_metrics(labels_i64, -slope),
            "ci95": bootstrap_metric_ci(labels_i64, -slope, seed=seed + 21, iters=bootstrap_iters),
        }
    )
    best_by_auc = max(candidates, key=lambda item: float(item["metrics"]["auc"]))
    best_by_low_fpr = max(
        candidates,
        key=lambda item: (
            float(item["metrics"]["tpr_at_1pct_fpr"]),
            float(item["metrics"]["tpr_at_0_1pct_fpr"]),
            float(item["metrics"]["auc"]),
        ),
    )
    return {
        "candidates": candidates,
        "best_by_auc": {"name": best_by_auc["name"], "metrics": best_by_auc["metrics"]},
        "best_by_low_fpr": {"name": best_by_low_fpr["name"], "metrics": best_by_low_fpr["metrics"]},
    }


def evaluate_logistic_holdout(
    labels: np.ndarray,
    features: np.ndarray,
    *,
    seed: int,
    repeats: int,
    bootstrap_iters: int = 0,
) -> dict[str, Any]:
    """Evaluate a balanced logistic scorer with repeated stratified holdout."""

    labels_i64 = np.asarray(labels, dtype=np.int64)
    features_f32 = np.asarray(features, dtype=np.float32)
    per_class_count = int(min((labels_i64 == 1).sum(), (labels_i64 == 0).sum()))
    if per_class_count < 2:
        raise ValueError("labels must contain at least two members and two nonmembers")
    fold_count = max(2, min(4, per_class_count))
    splitter = RepeatedStratifiedKFold(
        n_splits=fold_count,
        n_repeats=int(repeats),
        random_state=int(seed),
    )
    prediction_sum = np.zeros(labels_i64.shape[0], dtype=np.float64)
    prediction_count = np.zeros(labels_i64.shape[0], dtype=np.int64)
    fold_metrics: list[dict[str, Any]] = []
    coefficients: list[list[float]] = []
    for fold_idx, (train_idx, test_idx) in enumerate(splitter.split(features_f32, labels_i64)):
        classifier = make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2000, class_weight="balanced", random_state=int(seed) + fold_idx),
        )
        classifier.fit(features_f32[train_idx], labels_i64[train_idx])
        scores = classifier.predict_proba(features_f32[test_idx])[:, 1]
        prediction_sum[test_idx] += scores
        prediction_count[test_idx] += 1
        fold_metrics.append(
            {
                "fold": int(fold_idx),
                "train_size": int(train_idx.shape[0]),
                "test_size": int(test_idx.shape[0]),
                "metrics": score_metrics(labels_i64[test_idx], scores),
            }
        )
        coefficients.append(
            [
                round6(float(value))
                for value in classifier.named_steps["logisticregression"].coef_[0].tolist()
            ]
        )

    if not np.all(prediction_count > 0):
        missing = np.where(prediction_count == 0)[0].tolist()
        raise RuntimeError(f"Some samples were never evaluated by holdout splits: {missing[:8]}")
    aggregate_scores = prediction_sum / prediction_count
    aggregate_metrics = score_metrics(labels_i64, aggregate_scores)
    return {
        "score_orientation": "holdout_predicted_member_probability",
        "splitter": {
            "name": "RepeatedStratifiedKFold",
            "n_splits": int(fold_count),
            "n_repeats": int(repeats),
            "random_state": int(seed),
        },
        "aggregate_metrics": aggregate_metrics,
        "aggregate_ci95": bootstrap_metric_ci(
            labels_i64,
            aggregate_scores,
            seed=int(seed) + 100,
            iters=bootstrap_iters,
        ),
        "fold_metrics": fold_metrics,
        "mean_coefficients": [
            round6(float(value))
            for value in np.asarray(coefficients, dtype=float).mean(axis=0).tolist()
        ],
        "prediction_count": {
            "min": int(prediction_count.min()),
            "max": int(prediction_count.max()),
            "mean": round6(float(prediction_count.mean())),
        },
        "aggregate_scores": [round6(float(value)) for value in aggregate_scores.tolist()],
    }


def radial_radius(height: int, width: int) -> np.ndarray:
    fy = np.fft.fftfreq(int(height))[:, None]
    fx = np.fft.fftfreq(int(width))[None, :]
    max_radius = float(np.sqrt(0.5**2 + 0.5**2))
    return (np.sqrt(fx * fx + fy * fy) / max_radius).astype(np.float32)


def build_frequency_mask(
    height: int,
    width: int,
    kind: str,
    *,
    cutoff: float | None = None,
    cutoff_high: float | None = None,
) -> np.ndarray:
    radius = radial_radius(height, width)
    if kind == "full":
        mask = np.ones((height, width), dtype=np.float32)
    elif kind == "lowpass":
        if cutoff is None:
            raise ValueError("lowpass requires cutoff")
        mask = (radius <= float(cutoff)).astype(np.float32)
    elif kind == "highpass":
        if cutoff is None:
            raise ValueError("highpass requires cutoff")
        mask = (radius > float(cutoff)).astype(np.float32)
    elif kind == "bandpass":
        if cutoff is None or cutoff_high is None:
            raise ValueError("bandpass requires cutoff and cutoff_high")
        mask = ((radius > float(cutoff)) & (radius <= float(cutoff_high))).astype(np.float32)
    else:
        raise ValueError(f"Unknown mask kind: {kind}")
    return mask[None, :, :]


def apply_frequency_mask(images: np.ndarray, mask: np.ndarray) -> np.ndarray:
    images_f32 = np.asarray(images, dtype=np.float32)
    mask_f32 = np.asarray(mask, dtype=np.float32)
    if float(mask_f32.min()) == 1.0 and float(mask_f32.max()) == 1.0:
        return images_f32.copy()
    spectrum = np.fft.fftn(images_f32, axes=(-2, -1))
    filtered = np.fft.ifftn(spectrum * mask_f32, axes=(-2, -1)).real
    return filtered.astype(np.float32)


def compute_lowpass_min_distances(
    inputs: np.ndarray,
    responses: np.ndarray,
    *,
    cutoff: float,
) -> np.ndarray:
    """Compute lowpass-filtered min repeat RMSE for H2 response caches."""

    inputs_f32 = np.asarray(inputs, dtype=np.float32)
    responses_f32 = np.asarray(responses, dtype=np.float32)
    if responses_f32.ndim != inputs_f32.ndim + 2:
        raise ValueError("responses must have shape [sample, timestep, repeat, ...input_shape]")
    mask = build_frequency_mask(int(inputs_f32.shape[-2]), int(inputs_f32.shape[-1]), "lowpass", cutoff=cutoff)
    filtered_inputs = apply_frequency_mask(inputs_f32, mask)
    filtered_responses = apply_frequency_mask(responses_f32, mask)
    delta = filtered_responses - filtered_inputs[:, None, None, :, :, :]
    distances = np.sqrt(np.mean(delta * delta, axis=(3, 4, 5))).astype(np.float32)
    return distances.min(axis=2).astype(np.float32)


def evaluate_h2_response_cache(
    labels: np.ndarray,
    timesteps: np.ndarray,
    min_distances: np.ndarray,
    *,
    seed: int,
    holdout_repeats: int,
    bootstrap_iters: int = 0,
) -> dict[str, Any]:
    """Evaluate the primary H2 logistic scorer and simple comparators."""

    labels_i64 = np.asarray(labels, dtype=np.int64)
    timestep_values = np.asarray(timesteps, dtype=np.int64)
    distances = np.asarray(min_distances, dtype=np.float32)
    simple = evaluate_h2_simple_scores(
        labels_i64,
        distances,
        timestep_values,
        seed=seed,
        bootstrap_iters=bootstrap_iters,
    )
    logistic = evaluate_logistic_holdout(
        labels_i64,
        distances,
        seed=seed,
        repeats=holdout_repeats,
        bootstrap_iters=bootstrap_iters,
    )
    best_simple_low = simple["best_by_low_fpr"]["metrics"]
    best_simple_auc = simple["best_by_auc"]["metrics"]
    logistic_metrics = logistic["aggregate_metrics"]
    return {
        "simple": simple,
        "logistic": logistic,
        "gates": {
            "best_simple_by_low_fpr": simple["best_by_low_fpr"],
            "logistic_minus_best_simple_by_low_fpr": metric_delta(logistic_metrics, best_simple_low),
            "logistic_beats_simple_low_fpr": bool(
                float(logistic_metrics["tpr_at_1pct_fpr"]) > float(best_simple_low["tpr_at_1pct_fpr"])
                and float(logistic_metrics["tpr_at_0_1pct_fpr"])
                >= float(best_simple_low["tpr_at_0_1pct_fpr"])
            ),
            "logistic_auc_not_worse_than_best_simple_auc": bool(
                float(logistic_metrics["auc"]) >= float(best_simple_auc["auc"])
            ),
        },
    }


def build_alpha_bars(device: str, timesteps: int = 1000):
    import torch

    betas = torch.linspace(0.0001, 0.02, int(timesteps), device=device, dtype=torch.float32)
    return torch.cumprod(1.0 - betas, dim=0)


def partial_ddim_denoise(
    model: Any,
    x0_pixels: Any,
    *,
    timestep: int,
    alpha_bars: Any,
    generator: Any,
    stride: int,
    device: str,
) -> Any:
    import torch

    x0 = x0_pixels.to(device) * 2.0 - 1.0
    strength_t = int(timestep)
    if strength_t <= 0:
        return torch.clamp(x0_pixels, 0.0, 1.0).detach().cpu()
    if strength_t >= int(alpha_bars.shape[0]):
        raise ValueError(f"timestep must be < {alpha_bars.shape[0]}: {strength_t}")

    noise = torch.randn(x0.shape, generator=generator, device=device, dtype=x0.dtype)
    alpha_t = alpha_bars[strength_t].view(1, 1, 1, 1)
    x_t = alpha_t.sqrt() * x0 + (1.0 - alpha_t).sqrt() * noise

    current_t = strength_t
    step = max(int(stride), 1)
    while current_t > 0:
        previous_t = max(current_t - step, 0)
        t_tensor = torch.full((x_t.shape[0],), current_t, device=device, dtype=torch.long)
        eps = model(x_t, t=t_tensor)

        alpha_cur = alpha_bars[current_t].view(1, 1, 1, 1)
        alpha_prev = alpha_bars[previous_t].view(1, 1, 1, 1)
        x0_pred = (x_t - (1.0 - alpha_cur).sqrt() * eps) / alpha_cur.sqrt()
        x0_pred = torch.clamp(x0_pred, -1.0, 1.0)
        if previous_t == 0:
            x_t = x0_pred
        else:
            x_t = alpha_prev.sqrt() * x0_pred + (1.0 - alpha_prev).sqrt() * eps
        current_t = previous_t

    return torch.clamp((x_t + 1.0) / 2.0, 0.0, 1.0).detach().cpu()


def collect_strength_responses(
    model: Any,
    loader: Any,
    *,
    device: str,
    alpha_bars: Any,
    timesteps: list[int],
    repeats: int,
    denoise_stride: int,
    seed: int,
    sample_offset: int,
) -> tuple[Any, np.ndarray, np.ndarray]:
    """Collect H2 response clouds and raw RMSE distances from a packet loader."""

    import torch

    inputs: list[Any] = []
    response_batches: list[np.ndarray] = []
    distance_batches: list[np.ndarray] = []
    running_offset = int(sample_offset)
    model.eval()
    with torch.no_grad():
        for batch, _ in loader:
            batch = batch.detach().cpu()
            batch_responses = np.zeros(
                (batch.shape[0], len(timesteps), int(repeats), batch.shape[1], batch.shape[2], batch.shape[3]),
                dtype=np.float16,
            )
            batch_distances = np.zeros((batch.shape[0], len(timesteps), int(repeats)), dtype=np.float32)
            for strength_idx, timestep in enumerate(timesteps):
                for repeat_idx in range(int(repeats)):
                    generator = torch.Generator(device=device)
                    generator.manual_seed(
                        int(seed)
                        + int(timestep) * 100_000
                        + int(repeat_idx) * 10_000
                        + int(running_offset)
                    )
                    output = partial_ddim_denoise(
                        model,
                        batch,
                        timestep=int(timestep),
                        alpha_bars=alpha_bars,
                        generator=generator,
                        stride=denoise_stride,
                        device=device,
                    )
                    distances = torch.sqrt(((output - batch) ** 2).mean(dim=(1, 2, 3)))
                    batch_responses[:, strength_idx, repeat_idx] = output.numpy().astype(np.float16)
                    batch_distances[:, strength_idx, repeat_idx] = distances.numpy().astype(np.float32)
            inputs.append(batch)
            response_batches.append(batch_responses)
            distance_batches.append(batch_distances)
            running_offset += int(batch.shape[0])
    return (
        torch.cat(inputs, dim=0),
        np.concatenate(response_batches, axis=0),
        np.concatenate(distance_batches, axis=0),
    )
