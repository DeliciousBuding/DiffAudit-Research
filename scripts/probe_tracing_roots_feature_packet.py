"""Probe the Tracing the Roots supplementary feature packet.

The upstream supplement ships precomputed diffusion trajectory feature tensors,
not raw images or model checkpoints. This script keeps the replay bounded:
train one linear member-vs-external classifier on the train feature split and
report low-FPR membership metrics on the eval feature split.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable

import torch as th
from sklearn.metrics import accuracy_score, roc_auc_score, roc_curve
from torch.utils.data import DataLoader, TensorDataset


class LinearClassifier(th.nn.Module):
    def __init__(self, in_features: int) -> None:
        super().__init__()
        self.fc = th.nn.Linear(in_features=in_features, out_features=1)
        self.register_buffer("mean", th.zeros(1, in_features))
        self.register_buffer("std", th.ones(1, in_features))

    def forward(self, features: th.Tensor) -> th.Tensor:
        normalized = (features - self.mean) / self.std.clamp_min(1e-12)
        return self.fc(normalized).squeeze(1)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_tensor(path: Path) -> th.Tensor:
    return th.load(path, map_location="cpu", weights_only=True)


def select_features(
    tensor: th.Tensor,
    start: int,
    end: int,
    step: int,
    use_loss: bool,
    use_grad_x: bool,
    use_grad_theta: bool,
) -> th.Tensor:
    total_timesteps = tensor.shape[1] // 3
    if end == -1:
        end = total_timesteps
    slices = []
    if use_loss:
        slices.append(tensor[:, start:end:step])
    if use_grad_x:
        slices.append(tensor[:, total_timesteps + start : total_timesteps + end : step])
    if use_grad_theta:
        slices.append(tensor[:, 2 * total_timesteps + start : 2 * total_timesteps + end : step])
    if not slices:
        raise ValueError("At least one feature family must be selected.")
    return th.cat(slices, dim=1).float()


def load_split(
    data_root: Path,
    split: str,
    start: int,
    end: int,
    step: int,
    use_loss: bool,
    use_grad_x: bool,
    use_grad_theta: bool,
) -> tuple[th.Tensor, th.Tensor, dict[str, dict[str, object]]]:
    features = []
    labels = []
    summary: dict[str, dict[str, object]] = {}
    for label, cls_name in ((1, "member"), (0, "external")):
        path = data_root / split / f"{cls_name}.pt"
        tensor = load_tensor(path)
        selected = select_features(tensor, start, end, step, use_loss, use_grad_x, use_grad_theta)
        features.append(selected)
        labels.append(th.full((selected.shape[0],), label, dtype=th.float32))
        summary[f"{split}/{cls_name}"] = {
            "path": str(path),
            "sha256": sha256(path),
            "raw_shape": list(tensor.shape),
            "selected_shape": list(selected.shape),
            "dtype": str(tensor.dtype),
            "has_nan": bool(th.isnan(tensor).any().item()),
            "mean": float(tensor.float().mean().item()),
            "std": float(tensor.float().std().item()),
        }
    return th.cat(features, dim=0), th.cat(labels, dim=0), summary


def best_tpr_at_fpr(fpr: Iterable[float], tpr: Iterable[float], cap: float) -> float:
    return max((float(t) for f, t in zip(fpr, tpr) if float(f) <= cap), default=0.0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=1000)
    parser.add_argument("--step", type=int, default=3)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    parser.add_argument("--loss", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--grad-x", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--grad-theta", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    if args.device == "auto":
        device = "cuda" if th.cuda.is_available() else "cpu"
    else:
        device = args.device
    if device == "cuda" and not th.cuda.is_available():
        raise RuntimeError("CUDA was requested but is not available.")

    th.manual_seed(args.seed)

    train_x, train_y, train_summary = load_split(
        args.data_root,
        "train",
        args.start,
        args.end,
        args.step,
        args.loss,
        args.grad_x,
        args.grad_theta,
    )
    eval_x, eval_y, eval_summary = load_split(
        args.data_root,
        "eval",
        args.start,
        args.end,
        args.step,
        args.loss,
        args.grad_x,
        args.grad_theta,
    )

    model = LinearClassifier(train_x.shape[1]).to(device)
    var, mean = th.var_mean(train_x, dim=0, keepdim=True)
    model.mean.copy_(mean)
    model.std.copy_(var.sqrt())

    loader = DataLoader(
        TensorDataset(train_x, train_y),
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,
    )
    optimizer = th.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=10)
    scheduler = th.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.8)

    last_loss = 0.0
    last_acc = 0.0
    model.train()
    for _ in range(args.epochs):
        total_loss = 0.0
        total_acc = 0.0
        for features, target in loader:
            features, target = features.to(device), target.to(device)
            optimizer.zero_grad()
            logits = model(features)
            loss = th.nn.functional.binary_cross_entropy_with_logits(logits, target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() / len(loader)
            total_acc += ((logits >= 0).float() == target).float().mean().item() / len(loader)
        scheduler.step()
        last_loss = total_loss
        last_acc = total_acc

    model.eval()
    with th.inference_mode():
        scores = model(eval_x.to(device)).cpu()
    y_true = eval_y.numpy()
    y_score = scores.numpy()
    y_pred = (scores >= 0).float().numpy()
    fpr, tpr, _ = roc_curve(y_true, y_score)

    result = {
        "candidate": "Tracing the Roots supplementary CIFAR10 MIA feature packet",
        "date": "2026-05-15",
        "data_root": str(args.data_root),
        "contract": {
            "train_split": "data/cifar10/train/{member,external}.pt",
            "eval_split": "data/cifar10/eval/{member,external}.pt",
            "positive_class": "member",
            "feature_shape_source": "[loss trajectory, grad_x trajectory, grad_theta trajectory]",
            "start": args.start,
            "end": args.end,
            "step": args.step,
            "loss": args.loss,
            "grad_x": args.grad_x,
            "grad_theta": args.grad_theta,
            "seed": args.seed,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
        },
        "device": device,
        "tensor_summary": train_summary | eval_summary,
        "train": {
            "n_samples": int(train_x.shape[0]),
            "n_features": int(train_x.shape[1]),
            "final_loss": float(last_loss),
            "final_accuracy": float(last_acc),
        },
        "eval": {
            "n_samples": int(eval_x.shape[0]),
            "auc": float(roc_auc_score(y_true, y_score)),
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "tpr_at_1pct_fpr": best_tpr_at_fpr(fpr, tpr, 0.01),
            "tpr_at_0_1pct_fpr": best_tpr_at_fpr(fpr, tpr, 0.001),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["eval"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
