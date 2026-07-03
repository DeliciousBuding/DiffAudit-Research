import os
import os.path
import sys
from pathlib import Path

# sys.path.append('.')

import torch
import torchvision.datasets
import numpy as np

# from measures import ssim


PROJECT = Path(__file__).resolve().parents[2]  # Research/
WORKSPACE = PROJECT.parent
DEFAULT_MEMBER_SPLIT_ROOT = PROJECT / "data" / "splits"
DEFAULT_DATASET_ROOT = WORKSPACE / "Download" / "datasets"


def _path_from_env(env_name, default):
    return Path(os.environ.get(env_name, str(default))).expanduser()


def _dataset_dir(base_root, dataset_env_name, default_subdir):
    override = os.environ.get(dataset_env_name)
    if override:
        return str(Path(override).expanduser())
    return str(base_root / default_subdir)


class MIACIFAR10(torchvision.datasets.CIFAR10):

    def __init__(self, idxs, **kwargs):
        super(MIACIFAR10, self).__init__(**kwargs)
        self.idxs = idxs

    def __len__(self):
        return len(self.idxs)

    def __getitem__(self, item):
        item = self.idxs[item]
        return super(MIACIFAR10, self).__getitem__(item)
    
class MIACIFAR100(torchvision.datasets.CIFAR100):

    def __init__(self, idxs, **kwargs):
        super(MIACIFAR100, self).__init__(**kwargs)
        self.idxs = idxs

    def __len__(self):
        return len(self.idxs)

    def __getitem__(self, item):
        item = self.idxs[item]
        return super(MIACIFAR100, self).__getitem__(item)

class MIASTL10(torchvision.datasets.STL10):

    def __init__(self, idxs, **kwargs):
        super(MIASTL10, self).__init__(**kwargs)
        self.idxs = idxs

    def __len__(self):
        return len(self.idxs)

    def __getitem__(self, item):
        item = self.idxs[item]
        return super(MIASTL10, self).__getitem__(item)

class MIAImageFolder(torchvision.datasets.ImageFolder):

    def __init__(self, idxs, **kwargs):
        super(MIAImageFolder, self).__init__(**kwargs)
        self.idxs = idxs

    def __len__(self):
        return len(self.idxs)

    def __getitem__(self, item):
        item = self.idxs[item]
        return super(MIAImageFolder, self).__getitem__(item)


def load_member_data(dataset_name, batch_size=128, shuffle=False, randaugment=False,
                     dataset_root=None, member_split_root=None):
    member_split_root = Path(member_split_root) if member_split_root else _path_from_env(
        "DIFFAUDIT_MEMBER_SPLIT_ROOT", DEFAULT_MEMBER_SPLIT_ROOT)
    dataset_root = Path(dataset_root) if dataset_root else _path_from_env(
        "DIFFAUDIT_DATASET_ROOT", DEFAULT_DATASET_ROOT)
    if dataset_name.upper() == 'CIFAR10':
        splits = np.load(member_split_root / 'CIFAR10_train_ratio0.5.npz')
        member_idxs = splits['mia_train_idxs']
        nonmember_idxs = splits['mia_eval_idxs']
        # load MIA Datasets
        if randaugment:
            transforms = torchvision.transforms.Compose([torchvision.transforms.RandAugment(num_ops=5),
                                                         torchvision.transforms.ToTensor()])
        else:
            transforms = torchvision.transforms.Compose([
                torchvision.transforms.ToTensor()])
        cifar10_root = _dataset_dir(dataset_root, "DIFFAUDIT_CIFAR10_ROOT", "cifar10")
        member_set = MIACIFAR10(member_idxs, root=cifar10_root, train=True,
                                transform=transforms)
        nonmember_set = MIACIFAR10(nonmember_idxs, root=cifar10_root, train=True,
                                   transform=transforms)
    elif dataset_name.upper() == 'CIFAR100':
        splits = np.load(member_split_root / 'CIFAR100_train_ratio0.5.npz')
        member_idxs = splits['mia_train_idxs']
        nonmember_idxs = splits['mia_eval_idxs']
        # load MIA Datasets
        if randaugment:
            transforms = torchvision.transforms.Compose([torchvision.transforms.RandAugment(num_ops=5),
                                                         torchvision.transforms.ToTensor()])
        else:
            transforms = torchvision.transforms.Compose([
                torchvision.transforms.ToTensor()])
        cifar100_root = _dataset_dir(dataset_root, "DIFFAUDIT_CIFAR100_ROOT", "cifar100")
        member_set = MIACIFAR100(member_idxs, root=cifar100_root, train=True,
                                transform=transforms)
        nonmember_set = MIACIFAR100(nonmember_idxs, root=cifar100_root, train=True,
                                   transform=transforms)
    elif dataset_name.upper() == 'STL10':
        splits = np.load(member_split_root / 'STL10_train_ratio0.5.npz')
        member_idxs = splits['mia_train_idxs']
        nonmember_idxs = splits['mia_eval_idxs']
        transforms = torchvision.transforms.Compose([
            torchvision.transforms.Resize(32),
            torchvision.transforms.ToTensor()
        ])
        stl10_root = _dataset_dir(dataset_root, "DIFFAUDIT_STL10_ROOT", "stl10")
        member_set = MIASTL10(member_idxs, root=stl10_root, split='unlabeled',
                              transform=transforms)
        nonmember_set = MIASTL10(nonmember_idxs, root=stl10_root, split='unlabeled',
                                 transform=transforms)
    elif dataset_name.upper() == 'TINY-IN':
        splits = np.load(member_split_root / 'TINY-IN_train_ratio0.5.npz')
        member_idxs = splits['mia_train_idxs']
        nonmember_idxs = splits['mia_eval_idxs']
        transforms = torchvision.transforms.Compose([
            torchvision.transforms.Resize(32),
            torchvision.transforms.ToTensor()
        ])
        tiny_in_root = _dataset_dir(dataset_root, "DIFFAUDIT_TINY_IN_ROOT", "tiny-imagenet-200/train")
        member_set = MIAImageFolder(member_idxs, root=tiny_in_root,
                                    transform=transforms)
        nonmember_set = MIAImageFolder(nonmember_idxs, root=tiny_in_root,
                                       transform=transforms)
    else:
        raise NotImplementedError

    member_loader = torch.utils.data.DataLoader(member_set, batch_size=batch_size, shuffle=shuffle)
    nonmember_loader = torch.utils.data.DataLoader(nonmember_set, batch_size=batch_size, shuffle=shuffle)
    return member_set, nonmember_set, member_loader, nonmember_loader
