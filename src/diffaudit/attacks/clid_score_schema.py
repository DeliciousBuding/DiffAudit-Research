"""Schema gate for CLiD score summaries before GPU packet promotion."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL_KEYS = (
    "status",
    "track",
    "method",
    "mode",
    "split_identity",
    "score_outputs",
    "metrics",
    "low_fpr_gate",
)

REQUIRED_SPLIT_KEYS = (
    "member_rows",
    "nonmember_rows",
    "alignment",
    "held_out_target_split",
)

REQUIRED_OUTPUT_KEYS = (
    "scorer_family",
    "raw_score_matrices",
    "threshold_summary",
)

REQUIRED_METRICS = (
    "auc",
    "asr",
    "tpr_at_1pct_fpr",
    "tpr_at_0_1pct_fpr",
)

REQUIRED_GATE_KEYS = (
    "minimum_samples_per_split",
    "strict_tail_metric",
    "promotion_requires",
    "passed",
)


def _read_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return payload


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_portable_reference(value: Any) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    normalized = value.replace("\\", "/")
    if ":" in normalized or normalized.startswith("/") or normalized.startswith("//"):
        return False
    return True


def validate_clid_score_summary(summary_path: str | Path) -> dict[str, Any]:
    """Validate the portable CLiD score-summary contract.

    This validates contract shape and promotion eligibility only. It does not
    convert a score summary into admitted evidence.
    """

    path = Path(summary_path)
    payload = _read_json_object(path) if path.is_file() else {}

    missing_top_level = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in payload]
    split_identity = payload.get("split_identity", {})
    score_outputs = payload.get("score_outputs", {})
    metrics = payload.get("metrics", {})
    low_fpr_gate = payload.get("low_fpr_gate", {})

    split_missing = [
        key
        for key in REQUIRED_SPLIT_KEYS
        if not isinstance(split_identity, dict) or key not in split_identity
    ]
    output_missing = [
        key
        for key in REQUIRED_OUTPUT_KEYS
        if not isinstance(score_outputs, dict) or key not in score_outputs
    ]
    metric_missing = [
        key
        for key in REQUIRED_METRICS
        if not isinstance(metrics, dict) or key not in metrics
    ]
    gate_missing = [
        key
        for key in REQUIRED_GATE_KEYS
        if not isinstance(low_fpr_gate, dict) or key not in low_fpr_gate
    ]

    member_rows = split_identity.get("member_rows", 0) if isinstance(split_identity, dict) else 0
    nonmember_rows = split_identity.get("nonmember_rows", 0) if isinstance(split_identity, dict) else 0
    minimum_samples = (
        low_fpr_gate.get("minimum_samples_per_split", 0)
        if isinstance(low_fpr_gate, dict)
        else 0
    )
    strict_tail_metric = (
        str(low_fpr_gate.get("strict_tail_metric", ""))
        if isinstance(low_fpr_gate, dict)
        else ""
    )
    strict_tail_value = (
        metrics.get(strict_tail_metric)
        if isinstance(metrics, dict) and strict_tail_metric in metrics
        else None
    )

    checks = {
        "summary_json": path.is_file(),
        "top_level_keys": not missing_top_level,
        "method_is_clid": payload.get("method") == "clid",
        "track_is_black_box": payload.get("track") == "black-box",
        "mode_is_score_summary": payload.get("mode") == "score-summary",
        "split_identity_keys": not split_missing,
        "balanced_split_rows": (
            isinstance(member_rows, int)
            and isinstance(nonmember_rows, int)
            and member_rows > 0
            and member_rows == nonmember_rows
        ),
        "held_out_target_split": (
            isinstance(split_identity, dict)
            and split_identity.get("held_out_target_split") is True
        ),
        "score_output_keys": not output_missing,
        "portable_artifact_references": (
            isinstance(score_outputs, dict)
            and all(
                _is_portable_reference(score_outputs.get(key))
                for key in ("raw_score_matrices", "threshold_summary")
            )
        ),
        "metric_keys": not metric_missing,
        "metrics_numeric": (
            isinstance(metrics, dict)
            and all(_is_number(metrics.get(key)) for key in REQUIRED_METRICS)
        ),
        "gate_keys": not gate_missing,
        "strict_tail_metric_declared": strict_tail_metric in REQUIRED_METRICS,
        "minimum_sample_gate": (
            isinstance(member_rows, int)
            and isinstance(nonmember_rows, int)
            and isinstance(minimum_samples, int)
            and member_rows >= minimum_samples
            and nonmember_rows >= minimum_samples
        ),
        "strict_tail_nonzero": _is_number(strict_tail_value) and float(strict_tail_value) > 0.0,
        "low_fpr_gate_consistent": (
            isinstance(low_fpr_gate, dict)
            and low_fpr_gate.get("passed")
            == (
                isinstance(member_rows, int)
                and isinstance(nonmember_rows, int)
                and isinstance(minimum_samples, int)
                and member_rows >= minimum_samples
                and nonmember_rows >= minimum_samples
                and _is_number(strict_tail_value)
                and float(strict_tail_value) > 0.0
            )
        ),
    }

    schema_missing = [
        key
        for key in (
            "summary_json",
            "top_level_keys",
            "method_is_clid",
            "track_is_black_box",
            "mode_is_score_summary",
            "split_identity_keys",
            "balanced_split_rows",
            "held_out_target_split",
            "score_output_keys",
            "portable_artifact_references",
            "metric_keys",
            "metrics_numeric",
            "gate_keys",
            "strict_tail_metric_declared",
            "low_fpr_gate_consistent",
        )
        if not checks[key]
    ]
    promotion_missing = [
        key
        for key in ("minimum_sample_gate", "strict_tail_nonzero")
        if not checks[key]
    ]
    schema_ready = not schema_missing
    promotion_ready = schema_ready and not promotion_missing and low_fpr_gate.get("passed") is True

    return {
        "status": "ready" if schema_ready else "blocked",
        "track": "black-box",
        "method": "clid",
        "mode": "score-schema-review",
        "summary_path": path.as_posix(),
        "checks": checks,
        "missing": schema_missing,
        "promotion_missing": promotion_missing,
        "missing_top_level_keys": missing_top_level,
        "missing_split_keys": split_missing,
        "missing_score_output_keys": output_missing,
        "missing_metric_keys": metric_missing,
        "missing_gate_keys": gate_missing,
        "promotion_status": "eligible" if promotion_ready else "not_eligible",
        "verdict": (
            "score schema is reusable and promotion gate passed"
            if promotion_ready
            else (
                "score schema is reusable but promotion gate did not pass"
                if schema_ready
                else "score schema is incomplete"
            )
        ),
        "next_action": (
            "review as bounded GPU candidate"
            if promotion_ready
            else (
                "collect larger held-out score packet before promotion"
                if schema_ready
                else "fix score summary schema before execution"
            )
        ),
    }
