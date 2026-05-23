import torch as th
from torch.utils.data import DataLoader
import utils

# Train a linear classifier on the diffusion trajectory features.
# Example usage:

# python train.py --data_path data/cifar10/train --model_path model.pt --start 0 --step 1 --end 1000 --loss --mia
# python train.py --data_path data/cifar10/train --model_path model.pt --start 0 --step 3 --end 1000 --mia
# python train.py --data_path data/cifar10/train --model_path model.pt --start 0 --step 1 --end 1000 --mia

# See arguments below for more options.
# Due to file size limitations, we do not provide data for all experiments but you can generate it using open-source DDPMs.  # noqa: E501


def main(data_path: str,
         batch_size: int,
         num_workers: int,
         epochs: int,
         save_path: str,
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

    dataset = utils.DiffusionTrajectoryFeaturesDataset(data_path,
                                                       start=start,
                                                       end=end,
                                                       step=step,
                                                       loss_feat=loss_feat,
                                                       grad_x_feat=grad_x_feat,
                                                       grad_theta_feat=grad_theta_feat,
                                                       ma=ma,
                                                       mia=mia)
    oa = not ma and not mia
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    print(f'Loaded dataset with {len(dataset)} samples and {len(dataloader)} batches of size {batch_size}.')

    model = utils.LinearClassifier(in_features=dataset.n_features, out_features=2 + oa).to(device)
    utils.calculate_var_mean(dataset, model)
    optimizer = th.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=10)
    scheduler = th.optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.8)
    print(f'Initialized model ({device}) with {sum(p.numel() for p in model.parameters())} parameters.')

    for epoch in range(1, epochs + 1):
        avg_loss = 0
        avg_acc = 0
        for features, target in dataloader:
            features, target = features.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(features)
            loss = th.nn.functional.cross_entropy(output, target)
            avg_acc += 100 * (output.argmax(dim=1) == target).float().mean().item() / len(dataloader)
            avg_loss += loss.item() / len(dataloader)
            loss.backward()
            optimizer.step()
        scheduler.step()
        print(f'Epoch {str(epoch).zfill(len(str(epochs)))}/{epochs}, loss: {avg_loss:.4f}, accuracy: {avg_acc:.2f}%')

    th.save(model.state_dict(), save_path)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--data_path', type=str, required=True)
    parser.add_argument('--batch_size', type=int, default=50)
    parser.add_argument('--num_workers', type=int, default=0)
    parser.add_argument('--epochs', type=int, default=100)
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
         batch_size=args.batch_size,
         num_workers=args.num_workers,
         epochs=args.epochs,
         save_path=args.model_path,
         start=args.start,
         end=args.end,
         step=args.step,
         loss_feat=args.loss,
         grad_x_feat=args.grad_x,
         grad_theta_feat=args.grad_theta,
         ma=args.ma,
         mia=args.mia)
