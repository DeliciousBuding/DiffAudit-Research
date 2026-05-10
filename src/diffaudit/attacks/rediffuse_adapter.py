"""Runtime adapter for the collaborator-provided DDIM ReDiffuse bundle."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader, Subset
from torchvision import datasets as tv_datasets
from torchvision import transforms as tv_transforms

from diffaudit.attacks.rediffuse import (
    default_bundle_root,
    default_checkpoint_path,
    default_dataset_root,
    probe_rediffuse_assets,
    write_json,
)
from diffaudit.utils.io import torch_load_safe
from diffaudit.utils.metrics import metric_bundle


@dataclass(frozen=True)
class ReDiffuseModules:
    components: ModuleType
    model_unet: ModuleType
    resnet: ModuleType


@dataclass(frozen=True)
class ReDiffuseDefaults:
    T: int = 1000
    ch: int = 128
    ch_mult: tuple[int, ...] = (1, 2, 2, 2)
    attn: tuple[int, ...] = (1,)
    num_res_blocks: int = 2
    dropout: float = 0.1
    beta_1: float = 0.0001
    beta_T: float = 0.02
    image_size: int = 32


def _load_module(module_name: str, module_path: Path, bundle_root: Path) -> ModuleType:
    inserted = False
    bundle_string = str(bundle_root)
    if bundle_string not in sys.path:
        sys.path.insert(0, bundle_string)
        inserted = True
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Unable to load module from {module_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if inserted:
            try:
                sys.path.remove(bundle_string)
            except ValueError:
                pass


def load_rediffuse_modules(bundle_root: str | Path | None = None) -> ReDiffuseModules:
    bundle = Path(bundle_root) if bundle_root else default_bundle_root()
    unique = abs(hash(bundle.resolve()))
    return ReDiffuseModules(
        components=_load_module(
            f"diffaudit_rediffuse_components_{unique}",
            bundle / "components.py",
            bundle,
        ),
        model_unet=_load_module(
            f"diffaudit_rediffuse_model_unet_{unique}",
            bundle / "model_unet.py",
            bundle,
        ),
        resnet=_load_module(
            f"diffaudit_rediffuse_resnet_{unique}",
            bundle / "resnet.py",
            bundle,
        ),
    )


def build_rediffuse_unet(
    model_module: ModuleType,
    defaults: ReDiffuseDefaults | None = None,
) -> torch.nn.Module:
    config = defaults or ReDiffuseDefaults()
    return model_module.UNet(
        T=config.T,
        ch=config.ch,
        ch_mult=list(config.ch_mult),
        attn=list(config.attn),
        num_res_blocks=config.num_res_blocks,
        dropout=config.dropout,
    )


def load_rediffuse_model(
    checkpoint_path: str | Path,
    model_module: ModuleType,
    device: str = "cpu",
    weights_key: str = "ema_model",
    defaults: ReDiffuseDefaults | None = None,
) -> tuple[torch.nn.Module, dict[str, Any]]:
    model = build_rediffuse_unet(model_module, defaults=defaults)
    checkpoint = torch_load_safe(checkpoint_path, map_location=device, weights_only=True)
    if not isinstance(checkpoint, dict):
        raise TypeError("ReDiffuse checkpoint must be a dict-like torch checkpoint")
    if weights_key not in checkpoint:
        raise KeyError(f"ReDiffuse checkpoint does not contain weights key: {weights_key}")
    state_dict = {
        (key[7:] if key.startswith("module.") else key): value
        for key, value in checkpoint[weights_key].items()
    }
    load_result = model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model, {
        "weights_key": weights_key,
        "missing_keys": len(load_result.missing_keys),
        "unexpected_keys": len(load_result.unexpected_keys),
        "checkpoint_step": int(checkpoint["step"]) if "step" in checkpoint else None,
    }


def build_rediffuse_attacker(
    components_module: ModuleType,
    model: torch.nn.Module,
    device: str,
    attack_num: int = 1,
    interval: int = 200,
    average: int = 10,
    k: int = 100,
    defaults: ReDiffuseDefaults | None = None,
):
    config = defaults or ReDiffuseDefaults()
    attacker_cls = getattr(components_module, "ReDiffuseAttacker", None)
    if attacker_cls is None:
        raise ValueError("ReDiffuseAttacker not found in collaborator components.py")
    betas = torch.linspace(config.beta_1, config.beta_T, config.T, device=device)

    class RuntimeEpsGetter(components_module.EpsGetter):
        def __call__(
            self,
            xt: torch.Tensor,
            condition: torch.Tensor | None = None,
            noise_level: torch.Tensor | None = None,
            t: int | None = None,
        ) -> torch.Tensor:
            del condition, noise_level
            timestep = torch.ones([xt.shape[0]], device=xt.device, dtype=torch.long) * int(t or 0)
            return self.model(xt, t=timestep)

    return attacker_cls(
        betas,
        int(interval),
        int(attack_num),
        int(k),
        RuntimeEpsGetter(model),
        int(average),
        lambda x: x * 2 - 1,
    )


def _load_split_indices(split_path: Path) -> tuple[list[int], list[int]]:
    split = np.load(split_path, allow_pickle=False)
    return (
        [int(value) for value in split["mia_train_idxs"].tolist()],
        [int(value) for value in split["mia_eval_idxs"].tolist()],
    )


def _build_loader(
    dataset_root: Path,
    indices: list[int],
    max_samples: int,
    batch_size: int,
) -> DataLoader:
    transform = tv_transforms.Compose([tv_transforms.ToTensor()])
    dataset = tv_datasets.CIFAR10(
        root=str(dataset_root),
        train=True,
        transform=transform,
        download=False,
    )
    selected = indices[: int(max_samples)]
    return DataLoader(
        Subset(dataset, selected),
        batch_size=int(batch_size),
        shuffle=False,
        num_workers=0,
    )


def _score_batch_distance(
    attacker,
    batch: torch.Tensor,
    device: str,
    norm: int = 1,
) -> torch.Tensor:
    intermediates, denoised = attacker(batch.to(device))
    # Match the collaborator runner's first-step surface, but use a direct
    # distance score for bounded smoke packets instead of training a classifier.
    distance = (intermediates[0] - denoised[0]).abs().pow(norm).flatten(1).mean(dim=1)
    return (-distance).detach().cpu()


def _score_batch_residual_features(
    attacker,
    batch: torch.Tensor,
    device: str,
    norm: int = 1,
) -> torch.Tensor:
    intermediates, denoised = attacker(batch.to(device))
    return (intermediates[0] - denoised[0]).abs().pow(norm).detach().cpu()


def _score_loader_distance(
    attacker,
    loader: DataLoader,
    device: str,
    norm: int = 1,
) -> torch.Tensor:
    scores: list[torch.Tensor] = []
    with torch.no_grad():
        for batch, _label in loader:
            scores.append(_score_batch_distance(attacker, batch, device=device, norm=norm))
    if not scores:
        return torch.empty(0)
    return torch.cat(scores)


def _collect_residual_features(
    attacker,
    loader: DataLoader,
    device: str,
    norm: int = 1,
) -> torch.Tensor:
    features: list[torch.Tensor] = []
    with torch.no_grad():
        for batch, _label in loader:
            features.append(_score_batch_residual_features(attacker, batch, device=device, norm=norm))
    if not features:
        return torch.empty(0, 3, 32, 32)
    return torch.cat(features)


class _MembershipResidualDataset(torch.utils.data.Dataset):
    def __init__(self, member_features: torch.Tensor, nonmember_features: torch.Tensor):
        self.data = torch.cat([member_features, nonmember_features])
        self.labels = torch.cat([
            torch.ones(member_features.shape[0]),
            torch.zeros(nonmember_features.shape[0]),
        ]).reshape(-1)

    def __len__(self) -> int:
        return int(self.data.shape[0])

    def __getitem__(self, index: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.data[index], self.labels[index]


def _split_resnet_features(
    member_features: torch.Tensor,
    nonmember_features: torch.Tensor,
    train_portion: float,
    batch_size: int,
) -> tuple[DataLoader, DataLoader, int]:
    if member_features.shape[0] != nonmember_features.shape[0]:
        raise ValueError("member and nonmember feature counts must match")
    if member_features.shape[0] < 2:
        raise ValueError("ResNet scorer needs at least two samples per split")
    train_count = int(member_features.shape[0] * float(train_portion))
    train_count = max(1, min(train_count, member_features.shape[0] - 1))
    train_dataset = _MembershipResidualDataset(
        member_features[:train_count],
        nonmember_features[:train_count],
    )
    test_dataset = _MembershipResidualDataset(
        member_features[train_count:],
        nonmember_features[train_count:],
    )
    return (
        DataLoader(train_dataset, batch_size=int(batch_size), shuffle=True, num_workers=0),
        DataLoader(test_dataset, batch_size=int(batch_size), shuffle=False, num_workers=0),
        train_count,
    )


def _train_resnet_scorer_epoch(
    model: torch.nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: str,
) -> float:
    model.train()
    correct = 0
    total = 0
    for data, label in loader:
        data = data.to(device)
        label = label.to(device).reshape(-1, 1)
        logits = model(data)
        # MSE is retained intentionally to match the collaborator script's
        # second-stage scorer contract before any independent tuning.
        loss = ((logits - label) ** 2).mean()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        predictions = (logits >= 0.5).to(label.dtype)
        correct += int((predictions == label).sum().item())
        total += int(label.shape[0])
    return correct / max(total, 1)


def _eval_resnet_scorer(
    model: torch.nn.Module,
    loader: DataLoader,
    device: str,
) -> tuple[float, torch.Tensor, torch.Tensor]:
    model.eval()
    correct = 0
    total = 0
    member_scores: list[torch.Tensor] = []
    nonmember_scores: list[torch.Tensor] = []
    with torch.no_grad():
        for data, label in loader:
            data = data.to(device)
            label = label.to(device).reshape(-1, 1)
            logits = model(data)
            predictions = (logits >= 0.5).to(label.dtype)
            correct += int((predictions == label).sum().item())
            total += int(label.shape[0])
            logits_cpu = logits.detach().cpu().reshape(-1)
            labels_cpu = label.detach().cpu().reshape(-1)
            member_scores.append(logits_cpu[labels_cpu == 1])
            nonmember_scores.append(logits_cpu[labels_cpu == 0])
    return (
        correct / max(total, 1),
        torch.cat(member_scores).reshape(-1),
        torch.cat(nonmember_scores).reshape(-1),
    )


def _score_resnet_scorer(
    resnet_module: ModuleType,
    member_features: torch.Tensor,
    nonmember_features: torch.Tensor,
    device: str,
    train_portion: float,
    epochs: int,
    lr: float,
    batch_size: int,
    checkpoint_policy: str = "best_heldout",
) -> tuple[torch.Tensor, torch.Tensor, dict[str, Any]]:
    if checkpoint_policy not in {"best_heldout", "collaborator_counter"}:
        raise ValueError(f"Unsupported ReDiffuse ResNet checkpoint policy: {checkpoint_policy}")
    train_loader, test_loader, train_count = _split_resnet_features(
        member_features,
        nonmember_features,
        train_portion=train_portion,
        batch_size=batch_size,
    )
    model = resnet_module.ResNet18(num_channels=3, num_classes=1).to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=float(lr), momentum=0.9, weight_decay=5e-4)
    best_state: dict[str, torch.Tensor] | None = None
    best_acc = -1.0
    collaborator_acc_counter = 0.0
    train_acc = 0.0
    for _epoch in range(int(epochs)):
        train_acc = _train_resnet_scorer_epoch(model, train_loader, optimizer, device=device)
        test_acc, _member_scores, _nonmember_scores = _eval_resnet_scorer(model, test_loader, device=device)
        if checkpoint_policy == "best_heldout" and test_acc > best_acc:
            best_acc = test_acc
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
        elif checkpoint_policy == "collaborator_counter" and test_acc > collaborator_acc_counter:
            # The collaborator script initializes test_acc_best=0 and never
            # updates it. Preserve that contract explicitly instead of
            # silently treating the scorer as a true best-epoch selector.
            best_acc = test_acc
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}
    if best_state is not None:
        model.load_state_dict(best_state)
    _test_acc, member_scores, nonmember_scores = _eval_resnet_scorer(model, test_loader, device=device)
    return (
        member_scores.detach().cpu(),
        nonmember_scores.detach().cpu(),
        {
            "resnet_train_count_per_split": int(train_count),
            "resnet_test_count_per_split": int(member_scores.shape[0]),
            "resnet_train_acc_last": round(float(train_acc), 6),
            "resnet_test_acc_best": round(float(best_acc), 6),
            "resnet_epochs": int(epochs),
            "resnet_lr": float(lr),
            "resnet_batch_size": int(batch_size),
            "resnet_checkpoint_policy": checkpoint_policy,
            "resnet_score_orientation": "raw_logits_higher_is_member",
            "resnet_orientation_note": (
                "Raw logits are project-metric equivalent to the collaborator "
                "negated-logit plus member-lower ROC convention."
            ),
        },
    )


def _metrics_from_scores(member_scores: torch.Tensor, nonmember_scores: torch.Tensor) -> dict[str, Any]:
    labels = np.concatenate([
        np.ones(len(member_scores), dtype=np.int64),
        np.zeros(len(nonmember_scores), dtype=np.int64),
    ])
    scores = np.concatenate([
        member_scores.numpy(),
        nonmember_scores.numpy(),
    ])
    return {
        **metric_bundle(scores, labels),
        "member_score_mean": round(float(member_scores.mean().item()), 6),
        "nonmember_score_mean": round(float(nonmember_scores.mean().item()), 6),
    }


def probe_rediffuse_runtime(
    bundle_root: str | Path | None = None,
    checkpoint_path: str | Path | None = None,
    dataset_root: str | Path | None = None,
    device: str = "cpu",
    attack_num: int = 1,
    interval: int = 200,
    average: int = 10,
    k: int = 100,
) -> tuple[int, dict[str, Any]]:
    try:
        asset_probe = probe_rediffuse_assets(
            bundle_root=bundle_root,
            checkpoint_path=checkpoint_path,
            dataset_root=dataset_root,
        )
        if asset_probe["status"] != "ready":
            return 1, asset_probe
        paths = asset_probe["paths"]
        modules = load_rediffuse_modules(paths["bundle_root"])
        model, load_info = load_rediffuse_model(paths["checkpoint"], modules.model_unet, device=device)
        attacker = build_rediffuse_attacker(
            modules.components,
            model,
            device=device,
            attack_num=attack_num,
            interval=interval,
            average=average,
            k=k,
        )
        preview_batch = torch.rand(1, 3, 32, 32, device=device)
        preview_intermediates, preview_denoised = attacker(preview_batch)
    except (FileNotFoundError, ValueError, KeyError, TypeError, ImportError, RuntimeError) as exc:
        return 1, {
            "status": "blocked",
            "track": "gray-box",
            "method": "rediffuse",
            "mode": "runtime-probe",
            "device": device,
            "error": str(exc),
        }
    except Exception as exc:
        return 2, {
            "status": "error",
            "track": "gray-box",
            "method": "rediffuse",
            "mode": "runtime-probe",
            "device": device,
            "error": f"{type(exc).__name__}: {exc}",
        }

    return 0, {
        "status": "ready",
        "track": "gray-box",
        "method": "rediffuse",
        "mode": "runtime-probe",
        "device": device,
        "checks": {
            **asset_probe["checks"],
            "modules_loaded": True,
            "model_loaded": True,
            "attacker_instantiated": True,
            "preview_forward": True,
        },
        "paths": paths,
        "runtime": {
            "attack_num": int(attack_num),
            "interval": int(interval),
            "average": int(average),
            "k": int(k),
        },
        "load_info": load_info,
        "preview": {
            "intermediates_shape": list(preview_intermediates.shape),
            "denoised_shape": list(preview_denoised.shape),
        },
        "provenance": asset_probe["provenance"],
    }


def run_rediffuse_runtime_packet(
    workspace: str | Path,
    bundle_root: str | Path | None = None,
    checkpoint_path: str | Path | None = None,
    dataset_root: str | Path | None = None,
    device: str = "cpu",
    max_samples: int = 8,
    batch_size: int = 4,
    attack_num: int = 1,
    interval: int = 200,
    average: int = 10,
    k: int = 100,
    norm: int = 1,
    scoring_mode: str = "first_step_distance_mean",
    scorer_train_portion: float = 0.2,
    scorer_epochs: int = 15,
    scorer_lr: float = 0.001,
    scorer_batch_size: int = 128,
    provenance_status: str = "collaborator-grounded",
    mode: str = "runtime-packet",
) -> dict[str, Any]:
    started_at = time.perf_counter()
    workspace_path = Path(workspace)
    workspace_path.mkdir(parents=True, exist_ok=True)

    exit_code, readiness = probe_rediffuse_runtime(
        bundle_root=bundle_root,
        checkpoint_path=checkpoint_path,
        dataset_root=dataset_root,
        device=device,
        attack_num=attack_num,
        interval=interval,
        average=average,
        k=k,
    )
    if exit_code != 0:
        result = {
            "status": "blocked",
            "track": "gray-box",
            "method": "rediffuse",
            "mode": mode,
            "device": device,
            "workspace": str(workspace_path),
            "artifact_paths": {"summary": str(workspace_path / "summary.json")},
            "runtime_probe": readiness,
            "checks": {"runtime_probe_ready": False},
        }
        write_json(workspace_path / "summary.json", result)
        return result

    paths = readiness["paths"]
    modules = load_rediffuse_modules(paths["bundle_root"])
    model, load_info = load_rediffuse_model(paths["checkpoint"], modules.model_unet, device=device)
    attacker = build_rediffuse_attacker(
        modules.components,
        model,
        device=device,
        attack_num=attack_num,
        interval=interval,
        average=average,
        k=k,
    )
    member_indices, nonmember_indices = _load_split_indices(Path(paths["split"]))
    member_loader = _build_loader(
        dataset_root=Path(paths["dataset_root"]),
        indices=member_indices,
        max_samples=max_samples,
        batch_size=batch_size,
    )
    nonmember_loader = _build_loader(
        dataset_root=Path(paths["dataset_root"]),
        indices=nonmember_indices,
        max_samples=max_samples,
        batch_size=batch_size,
    )
    scorer_info: dict[str, Any] = {}
    normalized_scoring_mode = "first_step_distance_mean" if scoring_mode == "direct-distance" else scoring_mode
    if normalized_scoring_mode == "first_step_distance_mean":
        member_scores = _score_loader_distance(attacker, member_loader, device=device, norm=norm)
        nonmember_scores = _score_loader_distance(attacker, nonmember_loader, device=device, norm=norm)
    elif normalized_scoring_mode in {"resnet", "resnet_collaborator_replay"}:
        member_features = _collect_residual_features(attacker, member_loader, device=device, norm=norm)
        nonmember_features = _collect_residual_features(attacker, nonmember_loader, device=device, norm=norm)
        member_scores, nonmember_scores, scorer_info = _score_resnet_scorer(
            modules.resnet,
            member_features=member_features,
            nonmember_features=nonmember_features,
            device=device,
            train_portion=scorer_train_portion,
            epochs=scorer_epochs,
            lr=scorer_lr,
            batch_size=scorer_batch_size,
            checkpoint_policy="collaborator_counter"
            if normalized_scoring_mode == "resnet_collaborator_replay"
            else "best_heldout",
        )
    else:
        raise ValueError(f"Unsupported ReDiffuse scoring mode: {scoring_mode}")
    metrics = _metrics_from_scores(member_scores, nonmember_scores)

    scores_path = workspace_path / "scores.json"
    scores_payload = {
        "member_scores": [round(float(value), 6) for value in member_scores.tolist()],
        "nonmember_scores": [round(float(value), 6) for value in nonmember_scores.tolist()],
        "member_indices": member_indices[: int(max_samples)],
        "nonmember_indices": nonmember_indices[: int(max_samples)],
    }
    write_json(scores_path, scores_payload)

    result = {
        "status": "ready",
        "track": "gray-box",
        "method": "rediffuse",
        "mode": mode,
        "device": device,
        "workspace": str(workspace_path),
        "artifact_paths": {
            "summary": str(workspace_path / "summary.json"),
            "scores": str(scores_path),
        },
        "contract_stage": "candidate-baseline",
        "asset_grade": "single-machine-real-asset",
        "provenance_status": provenance_status,
        "evidence_level": mode,
        "checks": {
            **readiness["checks"],
            "runtime_probe_ready": True,
            "member_scores_generated": True,
            "nonmember_scores_generated": True,
        },
        "runtime": {
            "bundle_root": paths["bundle_root"],
            "checkpoint": paths["checkpoint"],
            "dataset_root": paths["dataset_root"],
            "split": paths["split"],
            "weights_key": load_info["weights_key"],
            "checkpoint_step": load_info["checkpoint_step"],
            "max_samples": int(max_samples),
            "num_samples": int(member_scores.shape[0]),
            "batch_size": int(batch_size),
            "attack_num": int(attack_num),
            "interval": int(interval),
            "average": int(average),
            "k": int(k),
            "norm": int(norm),
            "scoring_mode": normalized_scoring_mode,
            **scorer_info,
            "elapsed_seconds": round(time.perf_counter() - started_at, 6),
        },
        "sample_count_per_split": int(member_scores.shape[0]),
        "metrics": metrics,
        "provenance": readiness["provenance"],
        "notes": [
            "This is a bounded ReDiffuse compatibility packet, not an admitted benchmark result.",
            "Default scores use a direct first-step distance surface; resnet_collaborator_replay preserves the collaborator checkpoint-selection contract.",
        ],
    }
    write_json(workspace_path / "summary.json", result)
    return result


def run_rediffuse_runtime_smoke(
    workspace: str | Path,
    bundle_root: str | Path | None = None,
    checkpoint_path: str | Path | None = None,
    dataset_root: str | Path | None = None,
    device: str = "cpu",
    max_samples: int = 8,
    batch_size: int = 4,
    attack_num: int = 1,
    interval: int = 200,
    average: int = 10,
    k: int = 100,
    norm: int = 1,
    scoring_mode: str = "first_step_distance_mean",
    scorer_train_portion: float = 0.2,
    scorer_epochs: int = 15,
    scorer_lr: float = 0.001,
    scorer_batch_size: int = 128,
) -> dict[str, Any]:
    return run_rediffuse_runtime_packet(
        workspace=workspace,
        bundle_root=bundle_root,
        checkpoint_path=checkpoint_path,
        dataset_root=dataset_root,
        device=device,
        max_samples=max_samples,
        batch_size=batch_size,
        attack_num=attack_num,
        interval=interval,
        average=average,
        k=k,
        norm=norm,
        scoring_mode=scoring_mode,
        scorer_train_portion=scorer_train_portion,
        scorer_epochs=scorer_epochs,
        scorer_lr=scorer_lr,
        scorer_batch_size=scorer_batch_size,
        mode="runtime-smoke",
    )


def cleanup_workspace(workspace: str | Path) -> None:
    shutil.rmtree(Path(workspace), ignore_errors=True)
