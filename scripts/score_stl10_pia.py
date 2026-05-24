"""PIA scoring for STL-10 DDPM checkpoint.
Computes denoising loss on member vs non-member images.
Set DIFFAUDIT_DATA / DIFFAUDIT_OUTPUT env vars to override default paths.
"""
import sys, os
import numpy as np
import torch
from torch.utils.data import DataLoader
from torchvision import transforms

# === Paths: env-var overridable, repo-relative defaults ===
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_RESEARCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_ROOT = os.environ.get('DIFFAUDIT_DATA', os.path.join(_REPO, 'Download'))
SUPP = os.path.join(DATA_ROOT, 'shared', 'supplementary', 'rediffuse-openreview-supplement', 'extracted', 'Rediffuse')
OUTPUT_DIR = os.environ.get('DIFFAUDIT_OUTPUT', os.path.join(_RESEARCH, 'outputs', 'stl10-10k'))
CKPT = os.path.join(OUTPUT_DIR, 'final.pt')

sys.path.insert(0, os.path.join(SUPP, 'DDPM'))
from dataset_utils import MIASTL10
from diffusion import GaussianDiffusionTrainer
from model_unet import UNet
from sklearn.metrics import roc_auc_score, roc_curve

BATCH = 64
T = 1000
DEVICE = torch.device('cuda')

def load_model(ckpt_path):
    ckpt = torch.load(ckpt_path, weights_only=True)
    state = ckpt.get('ema_model', ckpt.get('model'))
    model = UNet(T=T, ch=128, ch_mult=[1,2,2,2], attn=[1], num_res_blocks=2, dropout=0.1).to(DEVICE)
    clean = {k[7:] if k.startswith('module.') else k: v for k, v in state.items()}
    model.load_state_dict(clean)
    model.eval()
    return model

def compute_scores(model, loader, num_batches=None):
    trainer = GaussianDiffusionTrainer(model, 1e-4, 0.02, T).to(DEVICE)
    scores = []
    with torch.no_grad():
        for i, batch in enumerate(loader):
            x = batch[0] if isinstance(batch, (list, tuple)) else batch
            x = x.to(DEVICE)
            loss = trainer(x).flatten(1).mean(dim=-1)
            scores.append(loss.cpu())
            if num_batches and i + 1 >= num_batches:
                break
    scores = torch.cat(scores)
    return -scores.numpy()

def main():
    model = load_model(CKPT)
    print(f"Model loaded from {CKPT}", flush=True)

    splits = np.load(os.path.join(SUPP, 'DDPM', 'STL10_train_ratio0.5.npz'))
    member_idx = splits['mia_train_idxs']
    nonmember_idx = splits['mia_eval_idxs']
    print(f"Members: {len(member_idx)}, Non-members: {len(nonmember_idx)}", flush=True)

    transform = transforms.Compose([
        transforms.Resize(32),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])

    ds_root = os.path.join(DATA_ROOT, 'shared', 'datasets')
    member_set = MIASTL10(member_idx, root=ds_root, split='unlabeled',
                          download=False, transform=transform)
    nonmember_set = MIASTL10(nonmember_idx, root=ds_root, split='unlabeled',
                             download=False, transform=transform)

    member_loader = DataLoader(member_set, batch_size=BATCH, shuffle=False, num_workers=0)
    nonmember_loader = DataLoader(nonmember_set, batch_size=BATCH, shuffle=False, num_workers=0)

    print("Computing member scores...", flush=True)
    mem_scores = compute_scores(model, member_loader)
    print("Computing non-member scores...", flush=True)
    non_scores = compute_scores(model, nonmember_loader)

    labels = np.concatenate([np.ones_like(mem_scores), np.zeros_like(non_scores)])
    all_scores = np.concatenate([mem_scores, non_scores])

    auc = roc_auc_score(labels, all_scores)
    fpr, tpr, thresholds = roc_curve(labels, all_scores)

    tpr_at_1pct = tpr[(fpr - 0.01).argmin()]
    tpr_at_01pct = tpr[(fpr - 0.001).argmin()]
    optimal_idx = (tpr - fpr).argmax()
    asr = ((all_scores >= thresholds[optimal_idx]) == labels).mean()

    print(f"\n=== STL-10 DDPM MIA Results ===", flush=True)
    print(f"AUC: {auc:.4f}", flush=True)
    print(f"ASR: {asr:.4f}", flush=True)
    print(f"TPR@1%FPR: {tpr_at_1pct:.4f}", flush=True)
    print(f"TPR@0.1%FPR: {tpr_at_01pct:.4f}", flush=True)
    print(f"Member score mean: {mem_scores.mean():.4f}, std: {mem_scores.std():.4f}", flush=True)
    print(f"Non-member score mean: {non_scores.mean():.4f}, std: {non_scores.std():.4f}", flush=True)

    result = {'auc': auc, 'asr': asr, 'tpr_1fpr': tpr_at_1pct, 'tpr_01fpr': tpr_at_01pct,
              'fpr': fpr, 'tpr': tpr, 'mem_scores': mem_scores, 'non_scores': non_scores}
    np.savez(os.path.join(OUTPUT_DIR, 'pia_scores.npz'), **result)
    print(f"Saved to {os.path.join(OUTPUT_DIR, 'pia_scores.npz')}", flush=True)

if __name__ == '__main__':
    main()
