"""Convert CIFAR-10 member images to .pt file for fast training.
Set DIFFAUDIT_DATA / DIFFAUDIT_OUTPUT env vars to override defaults.
"""
import sys, os, torch
from torchvision import transforms

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DATA = os.environ.get('DIFFAUDIT_DATA', os.path.join(_REPO, 'Download'))
_SUPP = os.path.join(_DATA, 'shared', 'supplementary', 'rediffuse-openreview-supplement', 'extracted', 'Rediffuse')
_OUT = os.environ.get('DIFFAUDIT_OUTPUT', os.path.join(_DATA, 'shared', 'datasets'))

sys.path.insert(0, os.path.join(_SUPP, 'DDPM'))
from dataset_utils import MIACIFAR10
import numpy as np

def main():
    splits = np.load(os.path.join(_SUPP, 'DDPM', 'CIFAR10_train_ratio0.5.npz'))
    member_idx = splits['mia_train_idxs']
    print(f"Member indices: {len(member_idx)}")

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    ds_root = os.path.join(_DATA, 'shared', 'datasets')
    # torchvision downloads cifar-10 to root/cifar10/
    dataset = MIACIFAR10(member_idx, root=ds_root, train=True, download=True, transform=transform)
    print(f"Dataset size: {len(dataset)}")

    images = torch.stack([dataset[i][0] for i in range(len(dataset))])
    out_path = os.path.join(_OUT, 'cifar10_member_25k.pt')
    torch.save(images, out_path)
    print(f"Saved {images.shape} to {out_path}")
    print(f"Range: [{images.min():.3f}, {images.max():.3f}]")

if __name__ == '__main__':
    main()
