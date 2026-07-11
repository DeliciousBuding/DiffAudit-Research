"""Torch-free canonical configuration for corrected Paper 1 target training."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


def _freeze_mapping(value: Mapping[str, object]) -> Mapping[str, object]:
    frozen: dict[str, object] = {}
    for key, item in value.items():
        if isinstance(item, Mapping):
            frozen[key] = _freeze_mapping(item)
        elif isinstance(item, list | tuple):
            frozen[key] = tuple(item)
        else:
            frozen[key] = item
    return MappingProxyType(frozen)


def _thaw_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _thaw_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_value(item) for item in value]
    return value


@dataclass(frozen=True, slots=True)
class TrainingConfig:
    precision: Mapping[str, object]
    model: Mapping[str, object]
    diffusion: Mapping[str, object]
    optimizer: Mapping[str, object]
    scheduler: Mapping[str, object]
    ema_decay: float
    grad_clip: float
    transform: Mapping[str, object]
    data: Mapping[str, object]
    determinism: Mapping[str, object]
    checkpointing: Mapping[str, object]
    runtime: Mapping[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "precision": _thaw_value(self.precision),
            "model": _thaw_value(self.model),
            "diffusion": _thaw_value(self.diffusion),
            "optimizer": _thaw_value(self.optimizer),
            "scheduler": _thaw_value(self.scheduler),
            "ema_decay": self.ema_decay,
            "grad_clip": self.grad_clip,
            "transform": _thaw_value(self.transform),
            "data": _thaw_value(self.data),
            "determinism": _thaw_value(self.determinism),
            "checkpointing": _thaw_value(self.checkpointing),
            "runtime": _thaw_value(self.runtime),
        }


def build_training_config() -> TrainingConfig:
    """Return the single frozen training configuration sealed by the protocol."""

    return TrainingConfig(
        precision=_freeze_mapping({"dtype": "float32", "amp": False}),
        model=_freeze_mapping(
            {
                "architecture": "UNet",
                "T": 1_000,
                "channels": 128,
                "channel_multipliers": [1, 2, 2, 2],
                "attention_levels": [1],
                "num_res_blocks": 2,
                "dropout": 0.1,
            }
        ),
        diffusion=_freeze_mapping(
            {
                "schedule": "linear",
                "timesteps": 1_000,
                "beta_1": 0.0001,
                "beta_T": 0.02,
                "mean_type": "epsilon",
                "variance_type": "fixedlarge",
            }
        ),
        optimizer=_freeze_mapping(
            {"name": "Adam", "learning_rate": 0.0002, "betas": [0.9, 0.999], "eps": 1e-8}
        ),
        scheduler=_freeze_mapping(
            {"name": "LambdaLR", "policy": "linear_warmup", "warmup_steps": 5_000}
        ),
        ema_decay=0.9999,
        grad_clip=1.0,
        transform=_freeze_mapping(
            {
                "operations": ["ToTensor", "Normalize"],
                "normalize_mean": [0.5, 0.5, 0.5],
                "normalize_std": [0.5, 0.5, 0.5],
                "random_augmentation": False,
            }
        ),
        data=_freeze_mapping(
            {
                "dataset": "CIFAR10",
                "train_size": 50_000,
                "member_size": 25_000,
                "member_only": True,
                "batch_size": 64,
                "drop_last": True,
                "shuffle": False,
                "sampler": "DeterministicEpochBatchSampler",
            }
        ),
        determinism=_freeze_mapping(
            {
                "deterministic_algorithms": True,
                "cudnn_benchmark": False,
                "cudnn_deterministic": True,
                "allow_tf32_matmul": False,
                "allow_tf32_cudnn": False,
                "cublas_workspace_config": ":4096:8",
                "seed_python": True,
                "seed_numpy": True,
                "seed_torch_cpu": True,
                "seed_torch_cuda": True,
                "worker_rng_independent": True,
            }
        ),
        checkpointing=_freeze_mapping(
            {
                "save_every": 2_000,
                "sample_every": 50_000,
                "quality_sample_size": 64,
                "save_final": True,
                "save_on_signal": "next_step_boundary",
                "atomic_replace": True,
                "weights_only_load": True,
                "retention": "retain_all_corrected_checkpoints",
            }
        ),
        runtime=_freeze_mapping(
            {
                "num_workers": 4,
                "pin_memory": "cuda_available",
                "persistent_workers": True,
                "non_blocking_device_transfer": True,
                "device_policy": "cuda_if_available_else_cpu",
            }
        ),
    )


def canonical_training_config_hash(config: TrainingConfig) -> str:
    canonical = json.dumps(
        config.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()
