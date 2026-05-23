import argparse
from pathlib import Path

import torch as th
from sklearn.metrics import accuracy_score, roc_auc_score, roc_curve
from torch.utils.data import DataLoader

import utils


def summarize(root: Path) -> None:
    for split in ("train", "eval"):
        for cls in ("member", "external"):
            tensor = th.load(root / split / f"{cls}.pt", map_location="cpu")
            print(
                f"{split}/{cls}: shape={tuple(tensor.shape)} dtype={tensor.dtype} "
                f"nan={th.isnan(tensor).any().item()} mean={tensor.float().mean().item():.6g} "
                f"std={tensor.float().std().item():.6g}"
            )


def run(root: Path, epochs: int, start: int, end: int, step: int) -> None:
    th.manual_seed(0)
    device = "cuda" if th.cuda.is_available() else "cpu"

    train_dataset = utils.DiffusionTrajectoryFeaturesDataset(
        str(root / "train"),
        start=start,
        end=end,
        step=step,
        loss_feat=True,
        grad_x_feat=True,
        grad_theta_feat=True,
        mia=True,
    )
    model = utils.LinearClassifier(
        in_features=train_dataset.n_features,
        out_features=2,
    ).to(device)
    utils.calculate_var_mean(train_dataset, model)

    loader = DataLoader(train_dataset, batch_size=50, shuffle=True, num_workers=0)
    optimizer = th.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=10)
    scheduler = th.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.8)

    for epoch in range(1, epochs + 1):
        total_loss = 0.0
        total_acc = 0.0
        for features, target in loader:
            features, target = features.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(features)
            loss = th.nn.functional.cross_entropy(output, target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() / len(loader)
            total_acc += (output.argmax(dim=1) == target).float().mean().item() / len(loader)
        scheduler.step()
        if epoch in {1, epochs}:
            print(f"epoch={epoch} loss={total_loss:.6f} acc={100 * total_acc:.2f}")

    model.eval()
    y_true = []
    y_score = []
    y_pred = []
    with th.inference_mode():
        for cls_idx, cls in enumerate(("member", "external")):
            dataset = utils.DiffusionTrajectoryFeaturesDataset(
                str(root / "eval" / f"{cls}.pt"),
                start=start,
                end=end,
                step=step,
                loss_feat=True,
                grad_x_feat=True,
                grad_theta_feat=True,
            )
            loader = DataLoader(dataset, batch_size=128, shuffle=False, num_workers=0)
            for features, _ in loader:
                output = model(features.to(device)).cpu()
                # Positive class is member. The upstream two-class model emits
                # logits [member_logit, zero_external_logit].
                y_score.extend((output[:, 0] - output[:, 1]).tolist())
                y_pred.extend(output.argmax(dim=1).tolist())
                y_true.extend([cls_idx] * output.shape[0])

    y_member = [1 if y == 0 else 0 for y in y_true]
    pred_member = [1 if y == 0 else 0 for y in y_pred]
    auc = roc_auc_score(y_member, y_score)
    fpr, tpr, _ = roc_curve(y_member, y_score)
    tpr_1 = max((t for f, t in zip(fpr, tpr) if f <= 0.01), default=0.0)
    tpr_001 = max((t for f, t in zip(fpr, tpr) if f <= 0.001), default=0.0)
    print(f"device={device} n_train={len(train_dataset)} n_eval={len(y_true)} n_features={train_dataset.n_features}")
    print(f"auc={auc:.6f} accuracy={accuracy_score(y_member, pred_member):.6f}")
    print(f"tpr_at_1pct_fpr={tpr_1:.6f} tpr_at_0.1pct_fpr={tpr_001:.6f}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/cifar10"))
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=1000)
    parser.add_argument("--step", type=int, default=3)
    args = parser.parse_args()
    summarize(args.root)
    run(args.root, args.epochs, args.start, args.end, args.step)


if __name__ == "__main__":
    main()
