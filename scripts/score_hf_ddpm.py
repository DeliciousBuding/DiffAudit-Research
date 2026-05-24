"""PIA attack on HuggingFace google/ddpm-cifar10-32 using diffusers pipeline."""
import sys, os
import numpy as np
import torch
from torch.utils.data import DataLoader
from torchvision import transforms
from diffusers import DDPMPipeline

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DATA = os.environ.get('DIFFAUDIT_DATA', os.path.join(_REPO, 'Download'))
_SUPP = os.path.join(_DATA, 'shared', 'supplementary', 'rediffuse-openreview-supplement', 'extracted', 'Rediffuse')
sys.path.insert(0, os.path.join(_SUPP, 'DDPM'))
from dataset_utils import MIACIFAR10
from sklearn.metrics import roc_auc_score, roc_curve

BATCH, T = 32, 1000
DEVICE = torch.device('cuda')

# Noise schedule
betas = torch.linspace(1e-4, 0.02, T)
alphas = 1 - betas
alphas_bar = torch.cumprod(alphas, dim=0)

def main():
    print("Loading HF DDPM...", flush=True)
    pipeline = DDPMPipeline.from_pretrained("google/ddpm-cifar10-32")
    model = pipeline.unet.to(DEVICE).eval()
    print("Loaded HF DDPM", flush=True)

    splits = np.load(os.path.join(_SUPP, 'DDPM', 'CIFAR10_train_ratio0.5.npz'))
    member_idx, nonmember_idx = splits['mia_train_idxs'], splits['mia_eval_idxs']
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    ds_root = os.path.join(_DATA, 'shared', 'datasets')
    m_loader = DataLoader(MIACIFAR10(member_idx, root=ds_root, train=True, download=False, transform=transform), batch_size=BATCH, shuffle=False, num_workers=0)
    n_loader = DataLoader(MIACIFAR10(nonmember_idx, root=ds_root, train=True, download=False, transform=transform), batch_size=BATCH, shuffle=False, num_workers=0)

    # PIA attack at t=200
    t = 200
    ab = alphas_bar[t].to(DEVICE)
    sqrt_ab = ab.sqrt()
    sqrt_1m_ab = (1 - ab).sqrt()

    def run(loader, desc):
        scores = []
        with torch.no_grad():
            for i, batch in enumerate(loader):
                x0 = batch[0].to(DEVICE)
                # Epsilon prediction at t=0
                eps_0 = model(x0, torch.zeros(x0.size(0), device=DEVICE).long()).sample
                # Noisy version at t
                noise = torch.randn_like(x0)
                x_t = sqrt_ab * x0 + sqrt_1m_ab * noise
                # Epsilon prediction at t
                eps_t = model(x_t, torch.full((x0.size(0),), t, device=DEVICE).long()).sample
                # PIA score: L2 distance
                dist = ((eps_0 - eps_t).abs() ** 2).flatten(1).sum(dim=1)
                scores.append(dist.cpu())
                if (i + 1) % 200 == 0: print(f"  {desc}: {i+1}/{len(loader)}", flush=True)
        return -torch.cat(scores).numpy()

    print("PIA on HF DDPM...", flush=True)
    mem = run(m_loader, "M"); non = run(n_loader, "N")
    labels = np.concatenate([np.ones_like(mem), np.zeros_like(non)])
    scores = np.concatenate([mem, non])
    auc = roc_auc_score(labels, scores)
    fpr, tpr, _ = roc_curve(labels, scores)
    tpr_5 = float(tpr[(fpr - 0.05).argmin()]) if fpr.max() >= 0.05 else 0
    tpr_1 = float(tpr[(fpr - 0.01).argmin()]) if fpr.max() >= 0.01 else 0
    asr = float(((scores >= np.median(scores)) == labels).mean())
    print(f"\nHF DDPM (google/ddpm-cifar10-32): AUC={auc:.4f} ASR={asr:.4f} TPR@5%={tpr_5:.4f} TPR@1%={tpr_1:.4f}", flush=True)

if __name__ == '__main__':
    main()