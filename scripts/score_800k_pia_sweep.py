"""PIA sweep on 800k checkpoint — different intervals/attack_nums."""
import sys, os
import numpy as np
import torch
from torch.utils.data import DataLoader
from torchvision import transforms

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DATA = os.environ.get('DIFFAUDIT_DATA', os.path.join(_REPO, 'Download'))
_SUPP = os.path.join(_DATA, 'shared', 'supplementary', 'rediffuse-openreview-supplement', 'extracted', 'Rediffuse')
_OUTPUT = os.environ.get('DIFFAUDIT_OUTPUT', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'cifar10-800k-existing'))
CKPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'workspaces', 'gray-box', 'assets', 'pia', 'checkpoints', 'cifar10_ddpm', 'checkpoint.pt')

sys.path.insert(0, os.path.join(_SUPP, 'DDPM'))
from dataset_utils import MIACIFAR10
from model_unet import UNet
import components
from sklearn.metrics import roc_auc_score, roc_curve

BATCH = 32
T = 1000
DEVICE = torch.device('cuda')

class EpsGetter(components.EpsGetter):
    def __call__(self, xt, condition=None, noise_level=None, t=None):
        t_tensor = torch.ones([xt.shape[0]], device=xt.device).long() * t
        return self.model(xt, t=t_tensor)

def load_model(ckpt_path):
    ckpt = torch.load(ckpt_path, weights_only=True)
    state = ckpt.get('ema_model', ckpt.get('model'))
    model = UNet(T=T, ch=128, ch_mult=[1,2,2,2], attn=[1], num_res_blocks=2, dropout=0.1).to(DEVICE)
    clean = {k[7:] if k.startswith('module.') else k: v for k, v in state.items()}
    model.load_state_dict(clean)
    model.eval()
    return model

def run_attack(attacker, loader, desc):
    all_scores = []
    with torch.no_grad():
        for i, batch in enumerate(loader):
            x0 = batch[0].to(DEVICE)
            intermediate, intermediate_denoise = attacker(x0)
            # Average over timesteps if multiple, then L2 distance
            dist = ((intermediate - intermediate_denoise).abs() ** 2).flatten(2).sum(dim=-1)
            if dist.dim() > 1:
                dist = dist.mean(dim=0)
            else:
                dist = dist.flatten()
            all_scores.append(dist.cpu())
            if (i + 1) % 200 == 0:
                print(f"  {desc}: {i+1}/{len(loader)}", flush=True)
    return -torch.cat(all_scores).numpy()

def main():
    model = load_model(CKPT)
    print(f"Loaded 800k checkpoint", flush=True)
    betas = torch.linspace(1e-4, 0.02, T).to(DEVICE)
    eps_getter = EpsGetter(model)

    splits = np.load(os.path.join(_SUPP, 'DDPM', 'CIFAR10_train_ratio0.5.npz'))
    member_idx, nonmember_idx = splits['mia_train_idxs'], splits['mia_eval_idxs']

    transform = transforms.Compose([
        transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    ds_root = os.path.join(_DATA, 'shared', 'datasets')
    member_loader = DataLoader(
        MIACIFAR10(member_idx, root=ds_root, train=True, download=False, transform=transform),
        batch_size=BATCH, shuffle=False, num_workers=0)
    nonmember_loader = DataLoader(
        MIACIFAR10(nonmember_idx, root=ds_root, train=True, download=False, transform=transform),
        batch_size=BATCH, shuffle=False, num_workers=0)

    configs = [
        ("PIA-i200-n1", 200, 1),
        ("PIA-i100-n1", 100, 1),
        ("PIA-i50-n1", 50, 1),
        ("PIA-i200-n5", 200, 5),
    ]

    for name, interval, attack_num in configs:
        print(f"\n--- {name} ---", flush=True)
        attacker = components.PIA(betas, interval, attack_num, 100, eps_getter, 10, None)
        mem = run_attack(attacker, member_loader, f"{name} M")
        non = run_attack(attacker, nonmember_loader, f"{name} N")
        labels = np.concatenate([np.ones_like(mem), np.zeros_like(non)])
        scores = np.concatenate([mem, non])
        auc = roc_auc_score(labels, scores)
        fpr, tpr, _ = roc_curve(labels, scores)
        tpr_1 = float(tpr[(fpr - 0.01).argmin()])
        tpr_01 = float(tpr[(fpr - 0.001).argmin()])
        # Also check TPR@5%FPR for intermediate tail
        tpr_5 = float(tpr[(fpr - 0.05).argmin()])
        asr = float(((scores >= np.median(scores)) == labels).mean())
        print(f"{name}: AUC={auc:.4f} ASR={asr:.4f} TPR@5%={tpr_5:.4f} TPR@1%={tpr_1:.4f} TPR@0.1%={tpr_01:.4f}", flush=True)

    print("\n=== PIA Sweep Summary ===", flush=True)
    print("(AUC ASR TPR@5% TPR@1% TPR@0.1%)", flush=True)

if __name__ == '__main__':
    main()
