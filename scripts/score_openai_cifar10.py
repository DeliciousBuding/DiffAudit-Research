"""Quick PIA+NNS scoring on OpenAI CIFAR-10 500k checkpoint."""
import sys, os, copy
import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset
from torchvision import transforms

_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DATA = os.environ.get('DIFFAUDIT_DATA', os.path.join(_REPO, 'Download'))
_SUPP = os.path.join(_DATA, 'shared', 'supplementary', 'rediffuse-openreview-supplement', 'extracted', 'Rediffuse')
_OUTPUT = os.environ.get('DIFFAUDIT_OUTPUT', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'outputs', 'cifar10-openai-500k'))
CKPT = os.path.join(_DATA, 'shared', 'weights', 'cifar10_openai_500k.pt')

sys.path.insert(0, os.path.join(_SUPP, 'DDPM'))
from dataset_utils import MIACIFAR10
from model_unet import UNet
import components
import resnet
from sklearn.metrics import roc_auc_score, roc_curve

BATCH = 32; T = 1000; DEVICE = torch.device('cuda')
DTYPE = torch.float32  # OpenAI checkpoint is float32

class EpsGetter(components.EpsGetter):
    def __call__(self, xt, condition=None, noise_level=None, t=None):
        return self.model(xt, t=torch.ones([xt.shape[0]], device=xt.device).long() * t)

def main():
    print("Loading OpenAI 500k checkpoint...", flush=True)
    ckpt = torch.load(CKPT, weights_only=True, map_location='cpu')
    model = UNet(T=T, ch=128, ch_mult=[1,2,2,2], attn=[1], num_res_blocks=2, dropout=0.1).to(DEVICE)
    model.load_state_dict(ckpt); model.eval()
    print(f"Loaded successfully", flush=True)

    betas = torch.linspace(1e-4, 0.02, T).to(DEVICE)
    eps_getter = EpsGetter(model)
    attacker = components.PIA(betas, 200, 1, 100, eps_getter, 10, None)

    splits = np.load(os.path.join(_SUPP, 'DDPM', 'CIFAR10_train_ratio0.5.npz'))
    member_idx, nonmember_idx = splits['mia_train_idxs'], splits['mia_eval_idxs']
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
    ds_root = os.path.join(_DATA, 'shared', 'datasets')
    m_loader = DataLoader(MIACIFAR10(member_idx, root=ds_root, train=True, download=False, transform=transform), batch_size=BATCH, shuffle=False, num_workers=0)
    n_loader = DataLoader(MIACIFAR10(nonmember_idx, root=ds_root, train=True, download=False, transform=transform), batch_size=BATCH, shuffle=False, num_workers=0)

    # Raw PIA
    print("Running PIA...", flush=True)
    mem_scores, non_scores = [], []
    with torch.no_grad():
        for batch in m_loader:
            x0 = batch[0].to(DEVICE)
            i, d = attacker(x0)
            dist = ((i - d).abs() ** 2).flatten(2).sum(dim=-1).flatten()
            mem_scores.append(dist.cpu())
        for batch in n_loader:
            x0 = batch[0].to(DEVICE)
            i, d = attacker(x0)
            dist = ((i - d).abs() ** 2).flatten(2).sum(dim=-1).flatten()
            non_scores.append(dist.cpu())

    mem_raw = -torch.cat(mem_scores).numpy(); non_raw = -torch.cat(non_scores).numpy()
    labels = np.concatenate([np.ones_like(mem_raw), np.zeros_like(non_raw)])
    scores = np.concatenate([mem_raw, non_raw])
    auc = roc_auc_score(labels, scores)
    fpr, tpr, _ = roc_curve(labels, scores)
    tpr_5 = float(tpr[(fpr - 0.05).argmin()])
    tpr_1 = float(tpr[(fpr - 0.01).argmin()])
    asr = float(((scores >= np.median(scores)) == labels).mean())
    print(f"\nPIA: AUC={auc:.4f} ASR={asr:.4f} TPR@5%={tpr_5:.4f} TPR@1%={tpr_1:.4f}", flush=True)

    # NNS
    print("\nCollecting NNS features...", flush=True)
    m_diff, m_samp, n_diff, n_samp = [], [], [], []
    m_loader = DataLoader(MIACIFAR10(member_idx, root=ds_root, train=True, download=False, transform=transform), batch_size=BATCH, shuffle=False, num_workers=0, drop_last=True)
    n_loader = DataLoader(MIACIFAR10(nonmember_idx, root=ds_root, train=True, download=False, transform=transform), batch_size=BATCH, shuffle=False, num_workers=0, drop_last=True)
    with torch.no_grad():
        for batch in m_loader:
            x0 = batch[0].to(DEVICE)
            i, d = attacker(x0); m_diff.append(i[0].cpu()); m_samp.append(d[0].cpu())
        for batch in n_loader:
            x0 = batch[0].to(DEVICE)
            i, d = attacker(x0); n_diff.append(i[0].cpu()); n_samp.append(d[0].cpu())
    m_diff = torch.cat(m_diff); m_samp = torch.cat(m_samp)
    n_diff = torch.cat(n_diff); n_samp = torch.cat(n_samp)
    m_concat = (m_diff - m_samp).abs() ** 2; n_concat = (n_diff - n_samp).abs() ** 2
    num_train = int(m_concat.size(0) * 0.8)
    train_data = torch.cat([m_concat[:num_train], n_concat[:num_train]])
    train_labels = torch.cat([torch.ones(num_train), torch.zeros(num_train)]).float().view(-1,1)
    test_data = torch.cat([m_concat[num_train:], n_concat[num_train:]])
    test_labels = torch.cat([torch.ones(m_concat.size(0)-num_train), torch.zeros(n_concat.size(0)-num_train)]).float().view(-1,1)

    classifier = resnet.ResNet18(num_channels=3, num_classes=1).to(DEVICE)
    optim = torch.optim.SGD(classifier.parameters(), lr=0.001, momentum=0.9, weight_decay=5e-4)
    criterion = torch.nn.MSELoss()
    train_dl = DataLoader(TensorDataset(train_data, train_labels), batch_size=128, shuffle=True)
    test_dl = DataLoader(TensorDataset(test_data, test_labels), batch_size=128, shuffle=False)

    best_acc, best_state = 0, None
    for epoch in range(15):
        classifier.train()
        for data, label in train_dl:
            logit = classifier(data.to(DEVICE)); loss = criterion(logit, label.to(DEVICE))
            optim.zero_grad(); loss.backward(); optim.step()
        classifier.eval(); correct, total = 0, 0
        with torch.no_grad():
            for data, label in test_dl:
                pred = (classifier(data.to(DEVICE)) >= 0.5).float().cpu()
                correct += (pred == label).sum().item(); total += data.size(0)
        acc = correct/total
        if acc > best_acc: best_acc = acc; best_state = copy.deepcopy(classifier.state_dict())

    classifier.load_state_dict(best_state); classifier.eval()
    mem_nns, non_nns = [], []
    with torch.no_grad():
        for data, label in test_dl:
            logit = classifier(data.to(DEVICE)).cpu()
            mem_nns.append(logit[label.cpu()==1]); non_nns.append(logit[label.cpu()==0])
    mem_nns = torch.cat(mem_nns).flatten().numpy(); non_nns = torch.cat(non_nns).flatten().numpy()
    labels_nns = np.concatenate([np.ones_like(mem_nns), np.zeros_like(non_nns)])
    scores_nns = np.concatenate([mem_nns, non_nns])
    auc_nns = roc_auc_score(labels_nns, scores_nns)
    fpr_nns, tpr_nns, _ = roc_curve(labels_nns, scores_nns)
    first_nonzero = (fpr_nns > 0).argmax()
    min_fpr = fpr_nns[first_nonzero] if first_nonzero > 0 else 0
    tpr_at_first = tpr_nns[first_nonzero] if first_nonzero > 0 else 0
    asr_nns = float(((scores_nns >= np.median(scores_nns)) == labels_nns).mean())
    print(f"\nNNS: AUC={auc_nns:.4f} ASR={asr_nns:.4f} best_acc={best_acc:.4f} minFPR={min_fpr:.4f} TPR@minFPR={tpr_at_first:.4f}", flush=True)

    os.makedirs(_OUTPUT, exist_ok=True)
    np.savez(os.path.join(_OUTPUT, 'scores.npz'), pia_auc=auc, nns_auc=auc_nns, nns_asr=asr_nns)
    print(f"\n=== OpenAI 500k CIFAR-10 ===", flush=True)
    print(f"PIA AUC={auc:.4f} | NNS AUC={auc_nns:.4f} ASR={asr_nns:.4f} minFPR={min_fpr:.4f}", flush=True)

if __name__ == '__main__':
    main()