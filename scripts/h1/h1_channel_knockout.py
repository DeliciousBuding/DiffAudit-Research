"""H1 Channel Knockout — causal verification of channel importance findings."""
import sys, pickle, torch, numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn import metrics as skm

PROJECT = Path(__file__).resolve().parents[1]
# GONE - module removed during restructuring; no replacement found on disk
# sys.path.insert(0, str(PROJECT/'references'/'materials'/'Rediffuse'/'DDPM'))
from model_unet import UNet
from dataset_utils import load_member_data

DEVICE = torch.device('cuda')
CKPT = 'D:/Code/DiffAudit/Download/checkpoints/ddpm-cifar10-800k/checkpoint.pt'
T, CH = 1000, 128; CH_MULT, ATTN, N_RB, DO = [1,2,2,2], [1], 2, 0.1
TIMESTEPS = [100, 400, 700]; N = 64

# Top-10 significant channels from mechanistic analysis
TOP_CHANNELS = [
    ('mid_1', 128), ('early_up', 99), ('early_up', 36),
    ('early_up', 13), ('early_up', 60), ('mid_0', 128),
    ('mid_1', 231), ('early_up', 2), ('early_up', 159),
    ('early_up', 196)
]

SITES_MAP = {'late_down':['downblocks','-1'], 'mid_0':['middleblocks','0'],
             'mid_1':['middleblocks','1'], 'early_up':['upblocks','0']}

def load_model():
    model = UNet(T=T, ch=CH, ch_mult=CH_MULT, attn=ATTN, num_res_blocks=N_RB, dropout=DO).eval()
    ckpt = torch.load(CKPT, map_location=DEVICE, weights_only=False)
    w = ckpt.get('ema_model', ckpt.get('net_model', ckpt))
    new = {k[7:] if k.startswith('module.') else k: v for k, v in w.items()}
    model.load_state_dict(new); model = model.to(DEVICE)
    betas = torch.linspace(0.0001, 0.02, T)
    model.alphas_cumprod = torch.cumprod(1 - betas, dim=0).to(DEVICE)
    return model

class ReadHook:
    def __init__(self): self.data = {}; self.handles = []
    def _h(self, n):
        def fn(m, i, o): self.data[n] = o.detach()
        return fn
    def reg(self, m, n, p):
        t = m
        for pp in p: t = t[int(pp)] if pp.lstrip('-').isdigit() else getattr(t, pp)
        self.handles.append(t.register_forward_hook(self._h(n)))
    def clear(self): self.data.clear()
    def remove(self):
        for h in self.handles: h.remove()

def make_knockout_hooks(model, knockout_chs_by_site):
    """Register hooks that zero out specific channels at specific sites."""
    handles = []
    for site_name, channels in knockout_chs_by_site.items():
        if site_name not in SITES_MAP: continue
        target = model
        for p in SITES_MAP[site_name]:
            target = target[int(p)] if p.lstrip('-').isdigit() else getattr(target, p)
        def make_hook(chs):
            def hook(module, input, output):
                output[:, chs] = 0
                return output
            return hook
        handles.append(target.register_forward_hook(make_hook(channels)))
    return handles

def extract(model, loader, knockout_chs=None):
    rhook = ReadHook()
    for sn in SITES_MAP: rhook.reg(model, sn, SITES_MAP[sn])
    ko_handles = make_knockout_hooks(model, knockout_chs) if knockout_chs else []

    samples = []; count = 0
    for batch in loader:
        imgs = batch[0].to(DEVICE); B = imgs.shape[0]
        if count >= N: break
        if B > N - count: imgs = imgs[:N-count]; B = imgs.shape[0]
        acts = [{} for _ in range(B)]
        for tv in TIMESTEPS:
            rhook.clear()
            tt = torch.full((B,), tv, device=DEVICE, dtype=torch.long)
            noise = torch.randn_like(imgs)
            ac = model.alphas_cumprod[tv]
            xt = ac.sqrt()*(imgs*2-1)+(1-ac).sqrt()*noise
            with torch.no_grad(): model(xt, tt)
            for sn in SITES_MAP:
                a = rhook.data.get(sn)
                if a is None: continue
                for i in range(B): acts[i][f'{sn}_t{tv}'] = a[i:i+1].cpu()
        samples.extend(acts); count += B
    rhook.remove()
    for h in ko_handles: h.remove()
    return samples[:N]

def featurize(raw):
    feats = []
    for s in raw:
        f = {}
        for k, act in s.items():
            C = act.shape[1]; flat = act.view(C, -1)
            mu = flat.abs().mean(dim=-1); vr = flat.var(dim=-1, unbiased=False)
            th = 0.01*flat.std(dim=-1, unbiased=False)
            sp = (flat.abs()<th.unsqueeze(-1)).float().mean(dim=-1)
            f[f'{k}_mu_mean'] = float(mu.mean())
            f[f'{k}_var_mean'] = float(vr.mean())
            f[f'{k}_sp_mean'] = float(sp.mean())
        feats.append(f)
    return feats

def eval_auc(mf, nf):
    all_f = mf + nf; y = np.concatenate([np.ones(len(mf)), np.zeros(len(nf))])
    keys = sorted([k for k in all_f[0] if isinstance(all_f[0][k], (float, int, np.floating))])
    X = np.array([[f[k] for k in keys] for f in all_f])
    lr = LogisticRegression(max_iter=5000, random_state=42, class_weight='balanced', solver='lbfgs')
    lr.fit(X, y)
    ms = lr.predict_proba(X[:len(mf)])[:,1]; ns = lr.predict_proba(X[len(mf):])[:,1]
    labels = np.concatenate([np.ones(len(mf)), np.zeros(len(nf))])
    scores = np.concatenate([ms, ns])
    auc = skm.roc_auc_score(labels, scores)
    fpr, tpr, _ = skm.roc_curve(labels, scores)
    tpr1 = float(tpr[np.argmin(np.abs(fpr-0.01))])
    return auc, tpr1, float(ms.mean()), float(ns.mean())

if __name__ == '__main__':
    print('Loading model...')
    model = load_model()
    _, _, ml, nl = load_member_data('CIFAR10', batch_size=64, shuffle=False, randaugment=False)

    # Baseline
    print('Baseline (no knockout)...')
    mb = extract(model, ml); nb = extract(model, nl)
    mfb = featurize(mb); nfb = featurize(nb)
    auc_b, tpr_b, mm_b, nm_b = eval_auc(mfb, nfb)
    print(f'  AUC={auc_b:.4f} TPR@1%={tpr_b:.4f} m_mean={mm_b:.4f} nm_mean={nm_b:.4f}')

    # Knockout: group channels by site
    ko_by_site = {}
    for site, ch in TOP_CHANNELS:
        ko_by_site.setdefault(site, []).append(ch)
    print(f'Knockout: { {k: len(v) for k, v in ko_by_site.items()} } channels zeroed')

    mk = extract(model, ml, knockout_chs=ko_by_site)
    nk = extract(model, nl, knockout_chs=ko_by_site)
    mfk = featurize(mk); nfk = featurize(nk)
    auc_k, tpr_k, mm_k, nm_k = eval_auc(mfk, nfk)
    print(f'  AUC={auc_k:.4f} TPR@1%={tpr_k:.4f} m_mean={mm_k:.4f} nm_mean={nm_k:.4f}')
    print(f'  Delta AUC = {auc_b - auc_k:+.4f} ({(auc_b-auc_k)*100:.1f} pct points)')

    # Per-site knockout
    for site in ['early_up', 'mid_1', 'mid_0']:
        chs = [c for s, c in TOP_CHANNELS if s == site]
        if not chs: continue
        ms = extract(model, ml, knockout_chs={site: chs})
        ns = extract(model, nl, knockout_chs={site: chs})
        mfs = featurize(ms); nfs = featurize(ns)
        auc_s, _, _, _ = eval_auc(mfs, nfs)
        print(f'  Knockout {site} ({len(chs)} chs): AUC={auc_s:.4f} Delta={auc_b-auc_s:+.4f}')

    print('Done.')
