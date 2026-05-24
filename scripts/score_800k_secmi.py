"""SecMI scoring on existing 800k CIFAR-10 checkpoint."""
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

BATCH = 16
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
            dist = ((intermediate - intermediate_denoise).abs() ** 2).flatten(2).sum(dim=-1).mean(dim=0)
            all_scores.append(dist.cpu())
            if (i + 1) % 100 == 0:
                print(f"  {desc}: {i+1}/{len(loader)}", flush=True)
    return -torch.cat(all_scores).numpy()  # negate: higher = member

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

    results = {}

    # SecMI configurations
    configs = [
        ("SecMI-i200-n4", 200, 4),
        ("SecMI-i100-n8", 100, 8),
        ("SecMI-i50-n16", 50, 16),
    ]

    for name, interval, attack_num in configs:
        print(f"\n{'='*50}", flush=True)
        print(f"Running {name}...", flush=True)
        attacker = components.SecMIAttacker(betas, interval, attack_num, 100, eps_getter, 10, None, None)
        mem = run_attack(attacker, member_loader, f"{name} Members")
        non = run_attack(attacker, nonmember_loader, f"{name} Non-members")
        labels = np.concatenate([np.ones_like(mem), np.zeros_like(non)])
        scores = np.concatenate([mem, non])
        auc = roc_auc_score(labels, scores)
        fpr, tpr, _ = roc_curve(labels, scores)
        tpr_1 = float(tpr[(fpr - 0.01).argmin()])
        tpr_01 = float(tpr[(fpr - 0.001).argmin()])
        asr = float(((scores >= np.median(scores)) == labels).mean())
        results[name] = {'auc': auc, 'asr': asr, 'tpr_1': tpr_1, 'tpr_01': tpr_01}
        print(f"{name}: AUC={auc:.4f} ASR={asr:.4f} TPR@1%={tpr_1:.4f} TPR@0.1%={tpr_01:.4f}", flush=True)

    os.makedirs(_OUTPUT, exist_ok=True)
    np.savez(os.path.join(_OUTPUT, 'secmi_all_scores.npz'), **results)
    print(f"\n=== Summary ===", flush=True)
    for name, r in results.items():
        print(f"{name}: AUC={r['auc']:.4f} ASR={r['asr']:.4f} TPR@1%={r['tpr_1']:.4f} TPR@0.1%={r['tpr_01']:.4f}", flush=True)

if __name__ == '__main__':
    main()
