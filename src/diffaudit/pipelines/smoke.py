"""Minimal smoke pipeline for early audit experiments."""

from __future__ import annotations

from diffaudit.config import AuditConfig


def build_smoke_summary(config: AuditConfig) -> dict[str, object]:
    return {
        "run_name": config.task.name,
        "model_family": config.task.model_family,
        "access_level": config.task.access_level,
        "dataset_id": config.assets.dataset_id,
        "model_id": config.assets.model_id,
        "attack_method": config.attack.method,
        "num_samples": config.attack.num_samples,
        "output_dir": config.report.output_dir,
    }
