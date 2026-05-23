import torch as th
from torch.utils.data import DataLoader
import torchmetrics
import utils
import os

# Evaluate a classifier trained with train.py (check that file for the training code).
# Example usage:

# python eval.py --data_path data/cifar10/eval --model_path model.pt --start 0 --step 1 --end 1000 --loss --mia
# python eval.py --data_path data/cifar10/eval --model_path model.pt --start 0 --step 3 --end 1000 --mia
# python eval.py --data_path data/cifar10/eval --model_path model.pt --start 0 --step 1 --end 1000 --mia

# See arguments below for more options.
# Due to file size limitations, we do not provide data for all experiments but you can generate it using open-source DDPMs.  # noqa: E501


@th.inference_mode()
def main(data_path: str,
         checkpoint_path: str,
         start: int,
         end: int,
         step: int,
         loss_feat: bool,
         grad_x_feat: bool,
         grad_theta_feat: bool,
         ma: bool,
         mia: bool) -> None:

    device = 'cuda' if th.cuda.is_available() else 'cpu'
    th.manual_seed(0)

    dataset = utils.DiffusionTrajectoryFeaturesDataset(data_path=os.path.join(data_path, 'external.pt'),
                                                       start=start,
                                                       end=end,
                                                       step=step,
                                                       loss_feat=loss_feat,
                                                       grad_x_feat=grad_x_feat,
                                                       grad_theta_feat=grad_theta_feat)

    oa = not ma and not mia
    out_features = 2 + oa

    model = utils.LinearClassifier(in_features=dataset.n_features, out_features=out_features).to(device).eval()
    model.load_state_dict(th.load(checkpoint_path))

    normalized_confusion_matrix = th.zeros((out_features, out_features))
    candidate_classes = utils.class_list(ma, mia)
    outputs = {cls_name: [] for cls_name in candidate_classes}

    for cls_idx, cls_name in enumerate(candidate_classes):
        path = os.path.join(data_path, f'{cls_name}.pt')
        dataset = utils.DiffusionTrajectoryFeaturesDataset(data_path=path,
                                                           start=start,
                                                           end=end,
                                                           step=step,
                                                           loss_feat=loss_feat,
                                                           grad_x_feat=grad_x_feat,
                                                           grad_theta_feat=grad_theta_feat)
        dataloader = DataLoader(dataset)

        print(f'Loaded {path} dataset with {len(dataset)} samples.')

        for features, _ in dataloader:
            features = features.to(device)
            output = model(features)
            outputs[cls_name].append(output.cpu())
            normalized_confusion_matrix[cls_idx][output.argmax(dim=1).item()] += 100 / len(dataloader)

    preds = th.cat([output for cls_name in candidate_classes for output in outputs[cls_name]], dim=0)
    targets = th.cat([cls_idx * th.ones(len(outputs[cls_name]))
                      for cls_idx, cls_name in enumerate(candidate_classes)], dim=0).long()
    auc = torchmetrics.AUROC(task="multiclass", num_classes=out_features, average="macro")(preds, targets).item()
    fpr, tpr, _ = torchmetrics.ROC(task="multiclass",
                                   num_classes=out_features,
                                   average=None if not oa else "macro")(preds, targets)
    if not oa:
        tpr, fpr = tpr[ma], fpr[ma]
    fpr1_idx = (fpr <= 0.01).nonzero(as_tuple=False).max()
    tpr, fpr = 100 * tpr[fpr1_idx].item(), 100 * fpr[fpr1_idx].item()
    asr = (th.diag(normalized_confusion_matrix).mean()).item()

    utils.print_normalized_confusion_matrix(normalized_confusion_matrix, candidate_classes)
    print(f"AUC: {100 * auc:.1f}%")
    print(f"TPR @ FPR: {tpr:.1f}% @ {fpr:.1f}%")
    print(f"ASR: {asr:.1f}%")


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--model_path', type=str, required=True)
    parser.add_argument('--start', type=int, default=0)
    parser.add_argument('--end', type=int, default=-1)
    parser.add_argument('--step', type=int, default=1)
    parser.add_argument('--loss', action='store_true')
    parser.add_argument('--grad_x', action='store_true')
    parser.add_argument('--grad_theta', action='store_true')
    parser.add_argument('--ma', action='store_true')
    parser.add_argument('--mia', action='store_true')
    args = parser.parse_args()

    if (not args.loss and not args.grad_x and not args.grad_theta):
        args.loss, args.grad_x, args.grad_theta = True, True, True

    if args.ma and args.mia:
        args.ma, args.mia = False, False

    main(data_path=args.data_path,
         checkpoint_path=args.model_path,
         start=args.start,
         end=args.end,
         step=args.step,
         loss_feat=args.loss,
         grad_x_feat=args.grad_x,
         grad_theta_feat=args.grad_theta,
         ma=args.ma,
         mia=args.mia)
