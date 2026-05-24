"""PIA v2 scoring for CIFAR-10 DDPM checkpoint — paper-accurate DDIM trajectory attack."""
import sys, os
import numpy as np
import torch
from torch.utils.data import DataLoader
from torchvision import transforms

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DATA = os.environ.get('DIFFAUDIT_DATA', os.path.join(_REPO, 'Download'))
_SUPP = os.path.join(_DATA, 'shared', 'supplementary', 'rediffuse-openreview-supplement', 'extracted', 'Rediffuse')
_OUTPUT = os.environ.get('DIFFAUDIT_OUTPUT', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'cifar10-10k'))
CKPT = os.path.join(_OUTPUT, 'final.pt')

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

def main():
    model = load_model(CKPT)
    print(f"Model loaded from {CKPT}", flush=True)

    betas = torch.linspace(1e-4, 0.02, T).to(DEVICE)
    eps_getter = EpsGetter(model)
    # Positional call matching micro_attack.py (PIA.__init__→Attacker.__init__ param routing)
    attacker = components.PIA(
        betas,       # → betas
        200,         # → interval
        1,           # → attack_num
        100,         # → k (placeholder, unused by PIA)
        eps_getter,  # → eps_getter (routed via super)
        10,          # → average (placeholder)
        None,        # → lp (not used; we compute L2 distance manually)
    )

    splits = np.load(os.path.join(_SUPP, 'DDPM', 'CIFAR10_train_ratio0.5.npz'))
    member_idx = splits['mia_train_idxs']
    nonmember_idx = splits['mia_eval_idxs']
    print(f"Members: {len(member_idx)}, Non-members: {len(nonmember_idx)}", flush=True)

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))  # [0,1] → [-1,1]
    ])

    ds_root = os.path.join(_DATA, 'shared', 'datasets')
    member_set = MIACIFAR10(member_idx, root=ds_root, train=True, download=False, transform=transform)
    nonmember_set = MIACIFAR10(nonmember_idx, root=ds_root, train=True, download=False, transform=transform)

    member_loader = DataLoader(member_set, batch_size=BATCH, shuffle=False, num_workers=0)
    nonmember_loader = DataLoader(nonmember_set, batch_size=BATCH, shuffle=False, num_workers=0)
    print(f"Batches: members={len(member_loader)}, non-members={len(nonmember_loader)}", flush=True)

    def run_attack(loader, desc):
        all_scores = []
        with torch.no_grad():
            for i, batch in enumerate(loader):
                x0 = batch[0].to(DEVICE)
                intermediate, intermediate_denoise = attacker(x0)
                dist = ((intermediate - intermediate_denoise).abs() ** 2).flatten(2).sum(dim=-1).flatten()
                all_scores.append(dist.cpu())
                if (i + 1) % 100 == 0:
                    print(f"  {desc}: {i+1}/{len(loader)} batches", flush=True)
        return torch.cat(all_scores).numpy()

    print("Running PIA attack on members...", flush=True)
    mem_scores = run_attack(member_loader, "Members")
    print(f"Member scores: mean={mem_scores.mean():.4f}, std={mem_scores.std():.4f}", flush=True)

    print("Running PIA attack on non-members...", flush=True)
    non_scores = run_attack(nonmember_loader, "Non-members")
    print(f"Non-member scores: mean={non_scores.mean():.4f}, std={non_scores.std():.4f}", flush=True)

    labels = np.concatenate([np.ones_like(mem_scores), np.zeros_like(non_scores)])
    all_scores = np.concatenate([mem_scores, non_scores])

    auc = roc_auc_score(labels, all_scores)
    fpr, tpr, thresholds = roc_curve(labels, all_scores)
    tpr_at_1pct = float(tpr[(fpr - 0.01).argmin()])
    tpr_at_01pct = float(tpr[(fpr - 0.001).argmin()])
    optimal_idx = (tpr - fpr).argmax()
    asr = float(((all_scores >= thresholds[optimal_idx]) == labels).mean())

    print(f"\n=== CIFAR-10 PIA v2 Results ===", flush=True)
    print(f"AUC: {auc:.4f}", flush=True)
    print(f"ASR: {asr:.4f}", flush=True)
    print(f"TPR@1%FPR: {tpr_at_1pct:.4f}", flush=True)
    print(f"TPR@0.1%FPR: {tpr_at_01pct:.4f}", flush=True)

    np.savez(os.path.join(_OUTPUT, 'pia_v2_scores.npz'),
             auc=auc, asr=asr, tpr_1fpr=tpr_at_1pct, tpr_01fpr=tpr_at_01pct,
             fpr=fpr, tpr=tpr, mem_scores=mem_scores, non_scores=non_scores)
    print(f"Saved to {os.path.join(_OUTPUT, 'pia_v2_scores.npz')}", flush=True)

if __name__ == '__main__':
    main()
