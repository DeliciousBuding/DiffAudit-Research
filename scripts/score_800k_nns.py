"""NNS (Neural Network Scorer) on 800k checkpoint.
Replicates micro_attack.py type='nns': PIA features → ResNet18 classifier → MIA scores.
"""
import sys, os, copy
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
import resnet
from sklearn.metrics import roc_auc_score, roc_curve

BATCH = 32; T = 1000; DEVICE = torch.device('cuda')

class EpsGetter(components.EpsGetter):
    def __call__(self, xt, condition=None, noise_level=None, t=None):
        return self.model(xt, t=torch.ones([xt.shape[0]], device=xt.device).long() * t)

def load(ckpt_path):
    ckpt = torch.load(ckpt_path, weights_only=True)
    state = ckpt.get('ema_model', ckpt.get('model'))
    model = UNet(T=T, ch=128, ch_mult=[1,2,2,2], attn=[1], num_res_blocks=2, dropout=0.1).to(DEVICE)
    clean = {k[7:] if k.startswith('module.') else k: v for k, v in state.items()}
    model.load_state_dict(clean); model.eval(); return model

def main():
    model = load(CKPT); print("Loaded 800k checkpoint", flush=True)
    betas = torch.linspace(1e-4, 0.02, T).to(DEVICE); eps_getter = EpsGetter(model)
    attacker = components.PIA(betas, 200, 1, 100, eps_getter, 10, None)

    splits = np.load(os.path.join(_SUPP, 'DDPM', 'CIFAR10_train_ratio0.5.npz'))
    member_idx, nonmember_idx = splits['mia_train_idxs'], splits['mia_eval_idxs']

    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    ds_root = os.path.join(_DATA, 'shared', 'datasets')
    m_loader = DataLoader(MIACIFAR10(member_idx, root=ds_root, train=True, download=False, transform=transform), batch_size=BATCH, shuffle=False, num_workers=0, drop_last=True)
    n_loader = DataLoader(MIACIFAR10(nonmember_idx, root=ds_root, train=True, download=False, transform=transform), batch_size=BATCH, shuffle=False, num_workers=0, drop_last=True)

    # Step 1: Collect PIA features (diffusion + denoised tensors)
    print("Collecting PIA features...", flush=True)
    m_diff, m_sample, n_diff, n_sample = [], [], [], []
    with torch.no_grad():
        for batch in m_loader:
            x0 = batch[0].to(DEVICE)
            intermediate, intermediate_denoise = attacker(x0)
            m_diff.append(intermediate[0].cpu()); m_sample.append(intermediate_denoise[0].cpu())
        for batch in n_loader:
            x0 = batch[0].to(DEVICE)
            intermediate, intermediate_denoise = attacker(x0)
            n_diff.append(intermediate[0].cpu()); n_sample.append(intermediate_denoise[0].cpu())

    m_diff = torch.cat(m_diff); m_sample = torch.cat(m_sample)
    n_diff = torch.cat(n_diff); n_sample = torch.cat(n_sample)
    print(f"Features: member {m_diff.shape}, nonmember {n_diff.shape}", flush=True)

    # Step 2: Compute difference features (L2 norm)
    norm = 2
    m_concat = (m_diff - m_sample).abs() ** norm
    n_concat = (n_diff - n_sample).abs() ** norm
    num_timestep = m_concat.size(0) if m_concat.dim() == 1 else 1

    # Step 3: Split train/test (80/20)
    num_train = int(m_concat.size(0) * 0.8)
    train_m, test_m = m_concat[:num_train], m_concat[num_train:]
    train_n, test_n = n_concat[:num_train], n_concat[num_train:]
    print(f"Train: {train_m.size(0)}M+{train_n.size(0)}N, Test: {test_m.size(0)}M+{test_n.size(0)}N", flush=True)

    # Step 4: Train ResNet18 classifier
    in_channels = 3 * num_timestep
    print(f"Training ResNet18 (in_channels={in_channels})...", flush=True)
    classifier = resnet.ResNet18(num_channels=in_channels, num_classes=1).to(DEVICE)
    optim = torch.optim.SGD(classifier.parameters(), lr=0.001, momentum=0.9, weight_decay=5e-4)
    criterion = torch.nn.MSELoss()

    # Prepare DataLoader
    train_data = torch.cat([train_m, train_n])
    train_labels = torch.cat([torch.ones(train_m.size(0)), torch.zeros(train_n.size(0))]).float().view(-1, 1)
    train_ds = torch.utils.data.TensorDataset(train_data, train_labels)
    train_dl = DataLoader(train_ds, batch_size=128, shuffle=True)

    test_data = torch.cat([test_m, test_n])
    test_labels = torch.cat([torch.ones(test_m.size(0)), torch.zeros(test_n.size(0))]).float().view(-1, 1)
    test_ds = torch.utils.data.TensorDataset(test_data, test_labels)
    test_dl = DataLoader(test_ds, batch_size=128, shuffle=False)

    best_acc, best_state = 0, None
    for epoch in range(15):
        classifier.train(); total, correct = 0, 0
        for data, label in train_dl:
            data, label = data.to(DEVICE), label.to(DEVICE)
            logit = classifier(data); loss = criterion(logit, label)
            optim.zero_grad(); loss.backward(); optim.step()
            pred = (logit >= 0.5).float()
            correct += (pred == label).sum().item(); total += data.size(0)
        train_acc = correct / total

        classifier.eval(); total, correct = 0, 0
        with torch.no_grad():
            for data, label in test_dl:
                data, label = data.to(DEVICE), label.to(DEVICE)
                logit = classifier(data)
                pred = (logit >= 0.5).float()
                correct += (pred == label).sum().item(); total += data.size(0)
        test_acc = correct / total
        print(f"  Epoch {epoch+1}: train_acc={train_acc:.4f} test_acc={test_acc:.4f}", flush=True)
        if test_acc > best_acc:
            best_acc = test_acc; best_state = copy.deepcopy(classifier.state_dict())

    # Step 5: Score test set with best model
    classifier.load_state_dict(best_state); classifier.eval()
    mem_scores, non_scores = [], []
    with torch.no_grad():
        for data, label in test_dl:
            logit = classifier(data.to(DEVICE))
            logit_cpu = logit.detach().cpu()
            mem_scores.append(logit_cpu[label.cpu() == 1])
            non_scores.append(logit_cpu[label.cpu() == 0])

    mem_scores = torch.cat(mem_scores).flatten().numpy()
    non_scores = torch.cat(non_scores).flatten().numpy()

    labels = np.concatenate([np.ones_like(mem_scores), np.zeros_like(non_scores)])
    scores = np.concatenate([mem_scores, non_scores])
    auc = roc_auc_score(labels, scores)
    fpr, tpr, _ = roc_curve(labels, scores)
    tpr_5 = float(tpr[(fpr - 0.05).argmin()]) if fpr.max() >= 0.05 else 0
    tpr_1 = float(tpr[(fpr - 0.01).argmin()]) if fpr.max() >= 0.01 else 0
    tpr_01 = float(tpr[(fpr - 0.001).argmin()]) if fpr.max() >= 0.001 else 0
    asr = float(((scores >= np.median(scores)) == labels).mean())

    print(f"\n=== NNS Results (ResNet18 on PIA features, 800k) ===", flush=True)
    print(f"Best test acc: {best_acc:.4f}", flush=True)
    print(f"AUC: {auc:.4f}", flush=True)
    print(f"ASR: {asr:.4f}", flush=True)
    print(f"TPR@5%FPR: {tpr_5:.4f}", flush=True)
    print(f"TPR@1%FPR: {tpr_1:.4f}", flush=True)
    print(f"TPR@0.1%FPR: {tpr_01:.4f}", flush=True)
    print(f"Member mean: {mem_scores.mean():.4f}, Non-member mean: {non_scores.mean():.4f}", flush=True)

    os.makedirs(_OUTPUT, exist_ok=True)
    np.savez(os.path.join(_OUTPUT, 'nns_scores.npz'), auc=auc, asr=asr, tpr_1=tpr_1, tpr_01=tpr_01, mem_scores=mem_scores, non_scores=non_scores)
    print(f"Saved to {_OUTPUT}/nns_scores.npz", flush=True)

if __name__ == '__main__':
    main()
