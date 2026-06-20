"""Replay MoFit's public COCO score-like text files.

This script is a bounded public-surface verifier for the 2026-06-08 MoFit
preflight. It fetches four small public score-like text files and two small
public caption JSONL files from the official MoFit GitHub repository, checks
their byte hashes, and mirrors the public ``Eval/mia_th_COCO.py`` scoring
logic. It does not clone the repository, download images, download checkpoints,
inspect numpy/pickle payloads, or run model code.

The result is support-only public score-surface replay evidence. It does not
admit MoFit into the DiffAudit evidence contract because target checkpoint
identity, explicit score row IDs, official row-bound metric packets, and
surface-delta controls are still missing. The optional bootstrap and permutation
controls are DiffAudit-side checks over implicit score-file positions, and the
caption-position manifest is only a support-only order anchor, not upstream
external-label, certified row-binding, or surface-delta evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from sklearn import metrics
from sklearn.preprocessing import RobustScaler


BASE_URL = "https://raw.githubusercontent.com/JoonsungJeon/MoFit/main/Results/COCO"
CAPTION_BASE_URL = "https://raw.githubusercontent.com/JoonsungJeon/MoFit/main/data/Captions/COCO"
EXPECTED = {
    "best_alpha": 0.55,
    "best_asr": 0.883,
    "best_threshold": 0.02012921206,
    "auc": 0.941948,
    "tpr_at_1fpr": 0.488,
    "tpr_at_01fpr": 0.324,
}
BEST_KEY_MAP = {
    "best_alpha": "alpha",
}
BOUNDARY_NOTE = (
    "support-only: public compact score-like text replay; not admitted "
    "evidence, not C14/N50 denominator evidence, and not compute release"
)
PATH_LIKE_RE = re.compile(r"(?:(?:[A-Za-z]:)?[/\\][A-Za-z0-9_. -]+){2,}")


def sanitized_preview(text: str, limit: int = 180) -> str:
    return PATH_LIKE_RE.sub("<path>", text[:limit])


@dataclass(frozen=True)
class PublicScoreFile:
    role: str
    filename: str
    encoded_filename: str
    expected_size: int
    expected_sha256: str
    expected_columns: int
    expected_rows: int = 500

    @property
    def url(self) -> str:
        return f"{BASE_URL}/{self.encoded_filename}"


FILES = [
    PublicScoreFile(
        role="vlm_train",
        filename="COCO_blip_500images_train_t_[140].txt",
        encoded_filename="COCO_blip_500images_train_t_%5B140%5D.txt",
        expected_size=29027,
        expected_sha256="957a4d00c82d2b06566b06f87dffb69393be979ed25c1ff3d5c6c59cee54eee5",
        expected_columns=6,
    ),
    PublicScoreFile(
        role="vlm_test",
        filename="COCO_blip_500images_test_t_[140].txt",
        encoded_filename="COCO_blip_500images_test_t_%5B140%5D.txt",
        expected_size=29531,
        expected_sha256="5a28de5f8fa243dcbd5a2ee4727fe202dc2ef6223f8edd204e78df33bf16bd18",
        expected_columns=6,
    ),
    PublicScoreFile(
        role="emb_train",
        filename="COCO_emb_500images_train_t_[140].txt",
        encoded_filename="COCO_emb_500images_train_t_%5B140%5D.txt",
        expected_size=13690,
        expected_sha256="8252bdacc461d6daebabe7549c522e4c0e9fa384aea1cd3a5f0574e4879405d4",
        expected_columns=3,
    ),
    PublicScoreFile(
        role="emb_test",
        filename="COCO_emb_500images_test_t_[140].txt",
        encoded_filename="COCO_emb_500images_test_t_%5B140%5D.txt",
        expected_size=13797,
        expected_sha256="6263c7d84d328b140d27dbdeff1e26b471a0d32d786228d3a54337212fe68b85",
        expected_columns=3,
    ),
]


@dataclass(frozen=True)
class PublicCaptionFile:
    role: str
    split: str
    filename: str
    expected_size: int
    expected_sha256: str
    expected_git_blob_sha: str
    expected_rows: int

    @property
    def url(self) -> str:
        return f"{CAPTION_BASE_URL}/{self.filename}"


CAPTION_FILES = [
    PublicCaptionFile(
        role="members",
        split="train",
        filename="blip2_members_2500_captions.jsonl",
        expected_size=179789,
        expected_sha256="a1ea4ce2efd412f242c9524eb508d020a060ff4ffe2609987719a0bcc80cf101",
        expected_git_blob_sha="c04b46f1d95daf1547e71e894d511d8d39708e6d",
        expected_rows=2500,
    ),
    PublicCaptionFile(
        role="non_members",
        split="test",
        filename="blip2_non_members_2458_captions.jsonl",
        expected_size=177451,
        expected_sha256="4e500699d2cba3986599d1bc7ab59f66bbfbe8120f787fe8f519514b678cc3a1",
        expected_git_blob_sha="5740b8ed2691e83fbf59c5f3622a9d77e71652ef",
        expected_rows=2458,
    ),
]


def fetch_file(spec: PublicScoreFile, timeout: float) -> tuple[str, np.ndarray, dict[str, object]]:
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(spec.url, timeout=timeout) as response:
                payload = response.read()
            break
        except (TimeoutError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt == 3:
                raise
            time.sleep(float(attempt))
    else:
        raise RuntimeError(f"failed to fetch {spec.url}") from last_error
    sha256 = hashlib.sha256(payload).hexdigest()
    text = payload.decode("utf-8")
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError(f"{spec.filename} is empty")
    header = lines[0]
    data_lines = lines[1:]
    parsed_rows: list[list[float]] = []
    for line_no, line in enumerate(data_lines, start=2):
        try:
            parsed_rows.append([float(cell) for cell in line.split("\t")])
        except ValueError as exc:
            raise ValueError(f"{spec.filename}:{line_no} contains a non-numeric cell") from exc
    widths = {len(row) for row in parsed_rows}
    if len(widths) > 1:
        raise ValueError(f"{spec.filename} is not rectangular: observed column counts {sorted(widths)}")
    rows = np.asarray(parsed_rows, dtype=float) if parsed_rows else np.empty((0, 0), dtype=float)
    column_count = int(rows.shape[1]) if rows.ndim == 2 else 0
    metadata = {
        "role": spec.role,
        "filename": spec.filename,
        "url": spec.url,
        "size_bytes": len(payload),
        "sha256": sha256,
        "rows": int(rows.shape[0]),
        "columns": column_count,
        "expected_columns": spec.expected_columns,
        "header_sha256": hashlib.sha256(header.encode("utf-8")).hexdigest(),
        "header_preview": sanitized_preview(header),
        "first_row_sha256": hashlib.sha256(data_lines[0].encode("utf-8")).hexdigest() if data_lines else "",
        "middle_row_sha256": hashlib.sha256(data_lines[len(data_lines) // 2].encode("utf-8")).hexdigest()
        if data_lines
        else "",
        "last_row_sha256": hashlib.sha256(data_lines[-1].encode("utf-8")).hexdigest() if data_lines else "",
        "first_row_preview": data_lines[0][:120] if data_lines else "",
        "size_matches": int(len(payload) == spec.expected_size),
        "sha256_matches": int(sha256 == spec.expected_sha256),
        "rows_match": int(rows.shape[0] == spec.expected_rows),
        "columns_match": int(column_count == spec.expected_columns),
    }
    return header, rows, metadata


def fetch_caption_file(spec: PublicCaptionFile, timeout: float) -> tuple[list[dict[str, str]], dict[str, object]]:
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(spec.url, timeout=timeout) as response:
                payload = response.read()
            break
        except (TimeoutError, urllib.error.URLError) as exc:
            last_error = exc
            if attempt == 3:
                raise
            time.sleep(float(attempt))
    else:
        raise RuntimeError(f"failed to fetch {spec.url}") from last_error

    sha256 = hashlib.sha256(payload).hexdigest()
    text = payload.decode("utf-8")
    raw_lines = [line for line in text.splitlines() if line.strip()]
    rows: list[dict[str, str]] = []
    for line_no, line in enumerate(raw_lines, start=1):
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{spec.filename}:{line_no} is not valid JSONL") from exc
        filename = str(item.get("filename", ""))
        caption = str(item.get("caption", ""))
        if not filename or not caption:
            raise ValueError(f"{spec.filename}:{line_no} missing filename or caption")
        rows.append(
            {
                "filename": filename,
                "caption": caption,
                "row_sha256": hashlib.sha256(line.encode("utf-8")).hexdigest(),
                "caption_sha256": hashlib.sha256(caption.encode("utf-8")).hexdigest(),
                "caption_preview": sanitized_preview(caption, limit=100),
            }
        )

    metadata = {
        "role": spec.role,
        "split": spec.split,
        "filename": spec.filename,
        "url": spec.url,
        "size_bytes": len(payload),
        "sha256": sha256,
        "git_blob_sha": spec.expected_git_blob_sha,
        "rows": len(rows),
        "first_row_sha256": rows[0]["row_sha256"] if rows else "",
        "middle_row_sha256": rows[len(rows) // 2]["row_sha256"] if rows else "",
        "last_row_sha256": rows[-1]["row_sha256"] if rows else "",
        "first_filename": rows[0]["filename"] if rows else "",
        "first_caption_preview": rows[0]["caption_preview"] if rows else "",
        "size_matches": int(len(payload) == spec.expected_size),
        "sha256_matches": int(sha256 == spec.expected_sha256),
        "rows_match": int(len(rows) == spec.expected_rows),
    }
    return rows, metadata


def require_expected_files(file_meta: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    for row in file_meta:
        role = row["role"]
        if not row["size_matches"]:
            errors.append(f"{role} size mismatch: {row['size_bytes']}")
        if not row["sha256_matches"]:
            errors.append(f"{role} sha256 mismatch: {row['sha256']}")
        if not row["rows_match"]:
            errors.append(f"{role} row-count mismatch: {row['rows']}")
        if not row["columns_match"]:
            errors.append(f"{role} column-count mismatch: {row['columns']} != {row['expected_columns']}")
    return errors


def require_expected_caption_files(caption_meta: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    for row in caption_meta:
        role = row["role"]
        if not row["size_matches"]:
            errors.append(f"{role} caption size mismatch: {row['size_bytes']}")
        if not row["sha256_matches"]:
            errors.append(f"{role} caption sha256 mismatch: {row['sha256']}")
        if not row["rows_match"]:
            errors.append(f"{role} caption row-count mismatch: {row['rows']}")
    return errors


def load_public_scores(timeout: float) -> tuple[dict[str, np.ndarray], list[dict[str, object]]]:
    arrays: dict[str, np.ndarray] = {}
    metadata: list[dict[str, object]] = []
    for spec in FILES:
        _header, rows, meta = fetch_file(spec, timeout)
        arrays[spec.role] = rows
        metadata.append(meta)
    return arrays, metadata


def load_public_captions(timeout: float) -> tuple[dict[str, list[dict[str, str]]], list[dict[str, object]]]:
    rows_by_split: dict[str, list[dict[str, str]]] = {}
    metadata: list[dict[str, object]] = []
    for spec in CAPTION_FILES:
        rows, meta = fetch_caption_file(spec, timeout)
        rows_by_split[spec.split] = rows
        metadata.append(meta)
    return rows_by_split, metadata


def threshold_sweep(train: np.ndarray, test: np.ndarray, n_points: int = 2000) -> list[dict[str, float | int]]:
    train_vector = np.asarray(train, dtype=float).reshape(-1)
    test_vector = np.asarray(test, dtype=float).reshape(-1)
    all_values = np.concatenate((train_vector, test_vector), axis=0)
    max_value = float(np.max(all_values))
    min_value = float(np.min(all_values))
    if max_value == min_value:
        raise ValueError("cannot sweep thresholds over a constant score vector")

    rows: list[dict[str, float | int]] = []
    step = (max_value - min_value) / n_points

    # Keep np.arange to mirror MoFit's public Eval/mia_th_COCO.py threshold sweep.
    for threshold in np.arange(min_value, max_value, step):
        tp = int((train_vector <= threshold).sum())
        tn = int((test_vector > threshold).sum())
        fp = int((test_vector <= threshold).sum())
        fn = int((train_vector > threshold).sum())
        tpr = tp / (tp + fn)
        fpr = fp / (fp + tn)
        asr = (tp + tn) / (tp + tn + fp + fn)
        rows.append(
            {
                "threshold": float(threshold),
                "tp": tp,
                "fp": fp,
                "tn": tn,
                "fn": fn,
                "tpr": float(tpr),
                "fpr": float(fpr),
                "asr": float(asr),
            }
        )
    return rows


def best_tpr_under_fpr(rows: list[dict[str, float | int]], target_fpr: float) -> dict[str, float | int]:
    eligible = [row for row in rows if float(row["fpr"]) <= target_fpr]
    if not eligible:
        return rows[0]
    return max(eligible, key=lambda row: (float(row["tpr"]), -float(row["fpr"]), float(row["asr"])))


def get_threshold_metrics(train: np.ndarray, test: np.ndarray, n_points: int = 2000) -> dict[str, Any]:
    rows = threshold_sweep(train, test, n_points=n_points)
    all_values = np.concatenate((np.asarray(train, dtype=float).reshape(-1), np.asarray(test, dtype=float).reshape(-1)))
    fpr_arr = np.asarray([float(row["fpr"]) for row in rows])
    tpr_arr = np.asarray([float(row["tpr"]) for row in rows])
    best_row = max(rows, key=lambda row: (float(row["asr"]), metrics.auc(fpr_arr, tpr_arr)))
    train_count = int(np.asarray(train).reshape(-1).shape[0])
    test_count = int(np.asarray(test).reshape(-1).shape[0])
    hit_1pct = best_tpr_under_fpr(rows, 0.01)
    hit_01pct = best_tpr_under_fpr(rows, 0.001)
    return {
        "best_threshold": float(best_row["threshold"]),
        "best_asr": float(best_row["asr"]),
        "auc": float(metrics.auc(fpr_arr, tpr_arr)),
        "tpr_at_1fpr": float(hit_1pct["tpr"]),
        "tpr_at_01fpr": float(hit_01pct["tpr"]),
        "fpr_at_1fpr": float(hit_1pct["fpr"]),
        "fpr_at_01fpr": float(hit_01pct["fpr"]),
        "fp_at_1fpr": int(hit_1pct["fp"]),
        "fp_at_01fpr": int(hit_01pct["fp"]),
        "n_train": train_count,
        "n_test": test_count,
        "fpr_1pct_false_positive_budget": float(test_count * 0.01),
        "fpr_01pct_false_positive_budget": float(test_count * 0.001),
        "fpr_denominator_note": "Low-FPR values use max TPR under the FPR budget and are quantized by 500 public test rows; 0.1% FPR is a zero-FP strict tail.",
        "max_value": float(np.max(all_values)),
        "min_value": float(np.min(all_values)),
    }


@dataclass(frozen=True)
class ScoreComponents:
    train_target: np.ndarray
    test_target: np.ndarray
    vlm_train: np.ndarray
    vlm_test: np.ndarray


def prepare_score_components(arrays: dict[str, np.ndarray]) -> ScoreComponents:
    train_target = np.array([[row[-2]] for row in arrays["emb_train"]])
    test_target = np.array([[row[-2]] for row in arrays["emb_test"]])
    vlm_train = np.array([[-row[-2]] for row in arrays["vlm_train"]])
    vlm_test = np.array([[-row[-2]] for row in arrays["vlm_test"]])

    target_scaled = RobustScaler().fit_transform(np.concatenate((train_target, test_target), axis=0))
    train_target = target_scaled[: len(train_target)]
    test_target = target_scaled[len(train_target) :]
    vlm_scaled = RobustScaler().fit_transform(np.concatenate((vlm_train, vlm_test), axis=0))
    vlm_train = vlm_scaled[: len(vlm_train)]
    vlm_test = vlm_scaled[len(vlm_train) :]
    return ScoreComponents(train_target=train_target, test_target=test_target, vlm_train=vlm_train, vlm_test=vlm_test)


def combine_scores(components: ScoreComponents, alpha: float) -> tuple[np.ndarray, np.ndarray]:
    train = (1 - alpha) * components.vlm_train + alpha * components.train_target
    test = (1 - alpha) * components.vlm_test + alpha * components.test_target
    return train, test


def replay_scores(arrays: dict[str, np.ndarray]) -> tuple[list[dict[str, Any]], dict[str, Any], ScoreComponents]:
    components = prepare_score_components(arrays)
    rows: list[dict[str, float]] = []
    for alpha in np.linspace(0, 1.0, 21):
        train, test = combine_scores(components, float(alpha))
        metrics_row = get_threshold_metrics(train, test)
        rows.append({"alpha": float(alpha), **metrics_row})

    best = max(rows, key=lambda row: (row["best_asr"], row["auc"]))
    return rows, best, components


def signed_auc(train: np.ndarray, test: np.ndarray) -> float:
    train_vector = np.asarray(train, dtype=float).reshape(-1)
    test_vector = np.asarray(test, dtype=float).reshape(-1)
    labels = np.concatenate((np.ones_like(train_vector), np.zeros_like(test_vector)))
    scores = -np.concatenate((train_vector, test_vector))
    return float(metrics.roc_auc_score(labels, scores))


def bootstrap_auc(train: np.ndarray, test: np.ndarray, samples: int, rng: np.random.Generator) -> dict[str, object]:
    if samples <= 0:
        return {"samples": 0}
    train_vector = np.asarray(train, dtype=float).reshape(-1)
    test_vector = np.asarray(test, dtype=float).reshape(-1)
    values: list[float] = []
    for _ in range(samples):
        boot_train = train_vector[rng.integers(0, len(train_vector), len(train_vector))]
        boot_test = test_vector[rng.integers(0, len(test_vector), len(test_vector))]
        values.append(signed_auc(boot_train, boot_test))
    arr = np.asarray(values, dtype=float)
    return {
        "samples": samples,
        "auc_mean": float(np.mean(arr)),
        "auc_std": float(np.std(arr, ddof=1)) if samples > 1 else 0.0,
        "auc_ci95_low": float(np.quantile(arr, 0.025)),
        "auc_ci95_high": float(np.quantile(arr, 0.975)),
        "boundary": "row bootstrap over implicit public score-file positions; support-only stability only",
    }


def permutation_null_auc(
    train: np.ndarray,
    test: np.ndarray,
    samples: int,
    rng: np.random.Generator,
    observed_auc: float,
) -> dict[str, object]:
    if samples <= 0:
        return {"samples": 0}
    train_vector = np.asarray(train, dtype=float).reshape(-1)
    test_vector = np.asarray(test, dtype=float).reshape(-1)
    labels = np.concatenate((np.ones_like(train_vector), np.zeros_like(test_vector)))
    scores = -np.concatenate((train_vector, test_vector))
    values: list[float] = []
    for _ in range(samples):
        values.append(float(metrics.roc_auc_score(rng.permutation(labels), scores)))
    arr = np.asarray(values, dtype=float)
    return {
        "samples": samples,
        "auc_mean": float(np.mean(arr)),
        "auc_std": float(np.std(arr, ddof=1)) if samples > 1 else 0.0,
        "auc_ci95_low": float(np.quantile(arr, 0.025)),
        "auc_ci95_high": float(np.quantile(arr, 0.975)),
        "p_value_auc_ge_observed": float((np.sum(arr >= observed_auc) + 1) / (samples + 1)),
        "boundary": "label permutation over implicit public score-file positions; not an external-label control",
    }


def build_position_manifest(arrays: dict[str, np.ndarray]) -> list[dict[str, object]]:
    role_specs = {spec.role: spec for spec in FILES}
    rows: list[dict[str, object]] = []
    for split, emb_role, vlm_role in [
        ("train", "emb_train", "vlm_train"),
        ("test", "emb_test", "vlm_test"),
    ]:
        count = min(int(arrays[emb_role].shape[0]), int(arrays[vlm_role].shape[0]))
        for index in range(count):
            rows.append(
                {
                    "split": split,
                    "implicit_position": index,
                    "emb_file": role_specs[emb_role].filename,
                    "emb_line_number": index + 2,
                    "vlm_file": role_specs[vlm_role].filename,
                    "vlm_line_number": index + 2,
                    "row_id_type": "implicit_file_position_only",
                    "boundary": "no explicit public row id; not admitted row binding",
                }
            )
    return rows


def build_caption_position_manifest(
    arrays: dict[str, np.ndarray],
    captions_by_split: dict[str, list[dict[str, str]]],
) -> list[dict[str, object]]:
    score_position_rows = build_position_manifest(arrays)
    caption_specs = {spec.split: spec for spec in CAPTION_FILES}
    rows: list[dict[str, object]] = []
    for score_row in score_position_rows:
        split = str(score_row["split"])
        index = int(score_row["implicit_position"])
        captions = captions_by_split.get(split, [])
        if index >= len(captions):
            continue
        caption_row = captions[index]
        caption_spec = caption_specs[split]
        rows.append(
            {
                "split": split,
                "implicit_position": index,
                "emb_file": score_row["emb_file"],
                "emb_line_number": score_row["emb_line_number"],
                "vlm_file": score_row["vlm_file"],
                "vlm_line_number": score_row["vlm_line_number"],
                "caption_role": caption_spec.role,
                "caption_file": caption_spec.filename,
                "caption_line_number": index + 1,
                "caption_filename": caption_row["filename"],
                "caption_row_sha256": caption_row["row_sha256"],
                "caption_text_sha256": caption_row["caption_sha256"],
                "caption_preview": caption_row["caption_preview"],
                "row_id_type": "caption_order_support_only",
                "boundary": "support-only caption JSONL order anchor only; score rows still lack explicit row IDs",
            }
        )
    return rows


def build_gate_status_rows(best: dict[str, Any]) -> list[dict[str, object]]:
    return [
        {
            "surface": "mofit-coco-public-score",
            "gate": "target_identity",
            "status": "Partial",
            "observed_surface": "Public score-file headers reference the COCO target by local checkpoint path.",
            "first_blocker": "No immutable public checkpoint identity or checkpoint hash for sd-COCO-checkpoint-3.",
            "allowed_claim": "support-only public score-surface replay only",
            "forbidden_claim": "admitted evidence; N50 denominator; second public asset; compute release",
        },
        {
            "surface": "mofit-coco-public-score",
            "gate": "split_identity",
            "status": "Partial",
            "observed_surface": "Public score files expose train/test rows and public caption JSONL files expose member/nonmember caption order.",
            "first_blocker": "Score rows do not embed public row IDs and caption-order binding is not certified by the score files.",
            "allowed_claim": "support-only caption-order anchor",
            "forbidden_claim": "manifest-certified row binding",
        },
        {
            "surface": "mofit-coco-public-score",
            "gate": "score_or_response_coverage",
            "status": "Partial",
            "observed_surface": "Four compact public text files expose 500 member and 500 nonmember score-like rows.",
            "first_blocker": "Rows are numeric arrays without explicit row IDs or public response packets.",
            "allowed_claim": "support-only public score-file replay",
            "forbidden_claim": "row-bound admitted score packet",
        },
        {
            "surface": "mofit-coco-public-score",
            "gate": "metric_provenance",
            "status": "Partial",
            "observed_surface": (
                f"DiffAudit replay mirrors public Eval/mia_th_COCO.py and obtains AUC {float(best['auc']):.6f}, "
                f"ASR {float(best['best_asr']):.3f}, TPR@1%FPR {float(best['tpr_at_1fpr']):.3f}, "
                f"and TPR@0.1%FPR {float(best['tpr_at_01fpr']):.3f}."
            ),
            "first_blocker": "Official machine-readable metric JSON/ROC/verifier and official control packet were not observed.",
            "allowed_claim": "support-only DiffAudit-side metric replay from public text files",
            "forbidden_claim": "official upstream metric packet",
        },
        {
            "surface": "mofit-coco-public-score",
            "gate": "consumer_boundary",
            "status": "Fail",
            "observed_surface": "Replay outputs are useful for paper-side audit inspection.",
            "first_blocker": "A downstream audit consumer still lacks immutable target identity and certified row binding.",
            "allowed_claim": "support-only evidence for claim-boundary discussion",
            "forbidden_claim": "consumer-admitted audit row",
        },
        {
            "surface": "mofit-coco-public-score",
            "gate": "surface_delta",
            "status": "Fail",
            "observed_surface": "The current check is one COCO public score-file surface.",
            "first_blocker": "No non-adjacent second response/score asset or official surface-delta control packet is present.",
            "allowed_claim": "support-only single public score-surface lead",
            "forbidden_claim": "completed second independent public asset",
        },
    ]


def check_expected(best: dict[str, float], tolerance: float) -> list[str]:
    errors: list[str] = []
    for key, expected in EXPECTED.items():
        actual = best[BEST_KEY_MAP.get(key, key)]
        if abs(actual - expected) > tolerance:
            errors.append(f"{key} drifted: expected {expected}, got {actual}")
    return errors


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if public file bytes or replay metrics drift")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    parser.add_argument("--timeout", type=float, default=30.0, help="per-file HTTP timeout in seconds")
    parser.add_argument("--tolerance", type=float, default=1e-6, help="numeric tolerance for --check")
    parser.add_argument("--output-csv", type=Path, help="optional CSV path for alpha sweep results")
    parser.add_argument("--file-manifest-csv", type=Path, help="optional CSV path for fetched file metadata")
    parser.add_argument("--metrics-json", type=Path, help="optional JSON path for replay metrics and controls")
    parser.add_argument("--roc-csv", type=Path, help="optional CSV path for best-alpha threshold/ROC rows")
    parser.add_argument("--position-manifest-csv", type=Path, help="optional CSV path for implicit row-position anchors")
    parser.add_argument("--gate-status-csv", type=Path, help="optional CSV path for six-gate support-only/admission status")
    parser.add_argument(
        "--caption-manifest-csv",
        type=Path,
        help="optional CSV path for support-only caption-order anchors for the first 500 score positions",
    )
    parser.add_argument("--bootstrap-samples", type=int, default=0, help="optional row-bootstrap AUC sample count")
    parser.add_argument("--permutation-samples", type=int, default=0, help="optional label-permutation null AUC sample count")
    parser.add_argument("--random-seed", type=int, default=20260608, help="random seed for bootstrap/permutation controls")
    args = parser.parse_args(argv)

    arrays, file_meta = load_public_scores(args.timeout)
    captions_by_split, caption_meta = load_public_captions(args.timeout)
    rows, best, components = replay_scores(arrays)
    best_train, best_test = combine_scores(components, float(best["alpha"]))
    best_roc_rows = threshold_sweep(best_train, best_test)
    position_manifest = build_position_manifest(arrays)
    caption_position_manifest = build_caption_position_manifest(arrays, captions_by_split)
    gate_status_rows = build_gate_status_rows(best)
    rng = np.random.default_rng(args.random_seed)
    controls = {
        "random_seed": args.random_seed,
        "bootstrap_auc": bootstrap_auc(best_train, best_test, args.bootstrap_samples, rng),
        "permutation_null_auc": permutation_null_auc(
            best_train,
            best_test,
            args.permutation_samples,
            rng,
            observed_auc=float(best["auc"]),
        ),
    }
    result = {
        "status": "mofit_public_coco_score_replay",
        "boundary": BOUNDARY_NOTE,
        "expected": EXPECTED,
        "best": best,
        "low_fpr_denominator_note": best.get("fpr_denominator_note"),
        "controls": controls,
        "file_metadata": file_meta,
        "caption_file_metadata": caption_meta,
        "position_manifest_summary": {
            "rows": len(position_manifest),
            "row_id_type": "implicit_file_position_only",
            "boundary": "no explicit public row IDs; position manifest is not admitted row binding",
        },
        "caption_position_manifest_summary": {
            "rows": len(caption_position_manifest),
            "row_id_type": "caption_order_support_only",
            "boundary": "support-only caption JSONL order anchor only; score rows still lack explicit row IDs or certified row binding",
        },
        "gate_status_summary": {
            "rows": len(gate_status_rows),
            "boundary": "machine-readable gate status for support-only wording; not admission",
        },
        "alpha_sweep": rows,
    }

    errors: list[str] = []
    if args.check:
        errors.extend(require_expected_files(file_meta))
        errors.extend(require_expected_caption_files(caption_meta))
        errors.extend(check_expected(best, args.tolerance))

    if args.output_csv:
        write_csv(
            args.output_csv,
            rows,
            [
                "alpha",
                "best_asr",
                "best_threshold",
                "auc",
                "tpr_at_1fpr",
                "tpr_at_01fpr",
                "fpr_at_1fpr",
                "fpr_at_01fpr",
                "fp_at_1fpr",
                "fp_at_01fpr",
                "n_train",
                "n_test",
                "fpr_1pct_false_positive_budget",
                "fpr_01pct_false_positive_budget",
                "fpr_denominator_note",
                "max_value",
                "min_value",
            ],
        )
    if args.file_manifest_csv:
        write_csv(
            args.file_manifest_csv,
            file_meta,
            [
                "role",
                "filename",
                "url",
                "size_bytes",
                "sha256",
                "rows",
                "columns",
                "expected_columns",
                "header_sha256",
                "header_preview",
                "first_row_sha256",
                "middle_row_sha256",
                "last_row_sha256",
                "first_row_preview",
                "size_matches",
                "sha256_matches",
                "rows_match",
                "columns_match",
            ],
        )
    if args.metrics_json:
        args.metrics_json.parent.mkdir(parents=True, exist_ok=True)
        args.metrics_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.roc_csv:
        write_csv(
            args.roc_csv,
            best_roc_rows,
            ["threshold", "tp", "fp", "tn", "fn", "tpr", "fpr", "asr"],
        )
    if args.position_manifest_csv:
        write_csv(
            args.position_manifest_csv,
            position_manifest,
            [
                "split",
                "implicit_position",
                "emb_file",
                "emb_line_number",
                "vlm_file",
                "vlm_line_number",
                "row_id_type",
                "boundary",
            ],
        )
    if args.gate_status_csv:
        write_csv(
            args.gate_status_csv,
            gate_status_rows,
            [
                "surface",
                "gate",
                "status",
                "observed_surface",
                "first_blocker",
                "allowed_claim",
                "forbidden_claim",
            ],
        )
    if args.caption_manifest_csv:
        write_csv(
            args.caption_manifest_csv,
            caption_position_manifest,
            [
                "split",
                "implicit_position",
                "emb_file",
                "emb_line_number",
                "vlm_file",
                "vlm_line_number",
                "caption_role",
                "caption_file",
                "caption_line_number",
                "caption_filename",
                "caption_row_sha256",
                "caption_text_sha256",
                "caption_preview",
                "row_id_type",
                "boundary",
            ],
        )

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("MoFit public COCO score replay")
        print(f"Boundary: {BOUNDARY_NOTE}")
        print(
            "Best: "
            f"alpha={best['alpha']:.2f}, "
            f"ASR={best['best_asr']:.6f}, "
            f"AUC={best['auc']:.6f}, "
            f"TPR@1%FPR={best['tpr_at_1fpr']:.6f}, "
            f"TPR@0.1%FPR={best['tpr_at_01fpr']:.6f}"
        )
        print("Files:")
        for row in file_meta:
            print(
                f"- {row['role']}: rows={row['rows']}, size={row['size_bytes']}, "
                f"columns={row['columns']}, sha256={row['sha256']}, "
                "checks(size/sha/rows/columns)="
                f"{row['size_matches']}/{row['sha256_matches']}/{row['rows_match']}/{row['columns_match']}"
            )
        print("Caption files:")
        for row in caption_meta:
            print(
                f"- {row['role']}: rows={row['rows']}, size={row['size_bytes']}, "
                f"sha256={row['sha256']}, checks(size/sha/rows)="
                f"{row['size_matches']}/{row['sha256_matches']}/{row['rows_match']}"
            )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if args.check:
        print("MoFit public COCO score replay check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
