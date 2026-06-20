"""Matched-count knockout: targeted top-10 vs random 10 (fair comparison)."""
import sys, torch, numpy as np, random, json, pickle
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn import metrics as skm
from scipy import stats as sp_stats

PROJECT = Path(__file__).resolve().parents[1]
# GONE - module removed during restructuring; no replacement found on disk
# sys.path.insert(0, str(PROJECT/'references'/'materials'/'Rediffuse'/'DDPM'))
from model_unet import UNet
from dataset_utils import load_member_data

DEVICE = torch.device('cuda')
CKPT = 'D:/Code/DiffAudit/Download/checkpoints/ddpm-cifar10-800k/checkpoint.pt'
T, CH = 1000, 128; CH_MULT, ATTN, N_RB, DO = [1,2,2,2], [1], 2, 0.1
TIMESTEPS = [100, 400, 700]; N_SAMPLES = 64
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

def get_channel_counts(model):
    dummy = torch.randn(1, 3, 32, 32).to(DEVICE)
    data = {}
    class PH:
        def __init__(self): self.data = {}; self.handles = []
        def _h(self, n):
            def fn(m, i, o): self.data[n] = o.shape[1]
            return fn
        def reg(self, m, n, p):
            t = m
            for pp in p: t = t[int(pp)] if pp.lstrip('-').isdigit() else getattr(t, pp)
            self.handles.append(t.register_forward_hook(self._h(n)))
    ph = PH()
    for sn, sp in SITES_MAP.items(): ph.reg(model, sn, sp)
    with torch.no_grad(): model(dummy, torch.tensor([100], device=DEVICE))
    result = ph.data.copy()
    for h in ph.handles: h.remove()
    return result

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

def make_ko_hooks(model, ko_by_site, ch_counts):
    handles = []
    for sn, chs in ko_by_site.items():
        if sn not in SITES_MAP: continue
        target = model
        for p in SITES_MAP[sn]: target = target[int(p)] if p.lstrip('-').isdigit() else getattr(target, p)
        vc = [c for c in chs if c < ch_counts[sn]]
        if not vc: continue
        def mh(cl):
            def hook(m, i, o): o[:, cl] = 0; return o
            return hook
        handles.append(target.register_forward_hook(mh(vc)))
    return handles

def extract(model, loader, ch_counts, ko=None):
    rh = ReadHook()
    for sn in SITES_MAP: rh.reg(model, sn, SITES_MAP[sn])
    handles = make_ko_hooks(model, ko, ch_counts) if ko else []
    samples = []; count = 0
    for batch in loader:
        imgs = batch[0].to(DEVICE); B = imgs.shape[0]
        if count >= N_SAMPLES: break
        if B > N_SAMPLES - count: imgs = imgs[:N_SAMPLES-count]; B = imgs.shape[0]
        acts = [{} for _ in range(B)]
        for tv in TIMESTEPS:
            rh.clear()
            tt = torch.full((B,), tv, device=DEVICE, dtype=torch.long)
            noise = torch.randn_like(imgs)
            ac = model.alphas_cumprod[tv]
            xt = ac.sqrt()*(imgs*2-1)+(1-ac).sqrt()*noise
            with torch.no_grad(): model(xt, tt)
            for sn in SITES_MAP:
                a = rh.data.get(sn)
                if a is None: continue
                for i in range(B): acts[i][f'{sn}_t{tv}'] = a[i:i+1].cpu()
        samples.extend(acts); count += B
    rh.remove()
    for h in handles: h.remove()
    return samples[:N_SAMPLES]

def featurize(raw):
    feats = []
    for s in raw:
        f = {}
        for k, act in s.items():
            flat = act.view(act.shape[1], -1)
            mu = flat.abs().mean(dim=-1)
            f[f'{k}_mu_mean'] = float(mu.mean())
            f[f'{k}_var_mean'] = float(flat.var(dim=-1, unbiased=False).mean())
        feats.append(f)
    return feats

def eval_full(mf, nf):
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
    return auc, tpr1, lr, keys

if __name__ == '__main__':
    print('Loading model...')
    model = load_model()
    ch_counts = get_channel_counts(model)
    total_ch = sum(ch_counts.values())
    print(f'Channel counts: {ch_counts} (total={total_ch})')

    _, _, ml, nl = load_member_data('CIFAR10', batch_size=64, shuffle=False, randaugment=False)

    # Baseline
    print('Baseline...')
    mb = extract(model, ml, ch_counts); nb = extract(model, nl, ch_counts)
    mfb = featurize(mb); nfb = featurize(nb)
    auc_b, tpr_b, lr_b, keys_b = eval_full(mfb, nfb)
    print(f'  AUC={auc_b:.4f} TPR@1%={tpr_b:.4f}')

    # Compute top-10 channels from t-test
    print('Computing channel significance...')
    # GONE - pickle file removed; must be regenerated by re-running h1_activation_scout.py
    # with open('outputs/h1-scout/h1_raw_activations.pkl', 'rb') as f:
    #     cache = pickle.load(f)
    raise FileNotFoundError("outputs/h1-scout/h1_raw_activations.pkl has been removed - regenerate via h1_activation_scout.py")
    ch_tstats = []
    for sn in SITES_MAP:
        for tv in TIMESTEPS:
            key = f'{sn}_t{tv}'
            arr_m = np.stack([cache['member_raw'][i][key].numpy().flatten() for i in range(64)])
            arr_nm = np.stack([cache['nonmember_raw'][i][key].numpy().flatten() for i in range(64)])
            for ch in range(ch_counts[sn]):
                t, p = sp_stats.ttest_ind(arr_m[:,ch], arr_nm[:,ch])
                ch_tstats.append((abs(t), sn, ch, p))
    ch_tstats.sort(reverse=True)
    top10 = [(sn, ch) for _, sn, ch, _ in ch_tstats[:10]]
    targeted_ko = {}
    for sn, ch in top10: targeted_ko.setdefault(sn, []).append(ch)
    print(f'Top-10: { {k: len(v) for k, v in targeted_ko.items()} } channels')

    # Targeted top-10 knockout
    print('Targeted top-10 KO...')
    mt = extract(model, ml, ch_counts, ko=targeted_ko)
    nt = extract(model, nl, ch_counts, ko=targeted_ko)
    mft = featurize(mt); nft = featurize(nt)
    auc_t, tpr_t, _, _ = eval_full(mft, nft)
    print(f'  AUC={auc_t:.4f} Delta={auc_b-auc_t:+.4f}')

    # Random 10 channels x 10 seeds
    print('Random 10 channels (10 seeds)...')
    random_aucs = []
    n_targeted = sum(len(v) for v in targeted_ko.values())
    for seed in range(10):
        random.seed(seed)
        rko = {}
        # Match total count: same number of channels as targeted, proportionally distributed
        for sn, nc in ch_counts.items():
            n_ko = max(1, int(n_targeted * nc / total_ch))
            rko[sn] = random.sample(range(nc), min(n_ko, nc))
        mr = extract(model, ml, ch_counts, ko=rko)
        nr = extract(model, nl, ch_counts, ko=rko)
        mfr = featurize(mr); nfr = featurize(nr)
        auc_r, _, _, _ = eval_full(mfr, nfr)
        random_aucs.append(auc_r)
    random_aucs = np.array(random_aucs)
    print(f'  Mean AUC={random_aucs.mean():.4f} Std={random_aucs.std():.4f}')
    print(f'  Mean Delta={auc_b - random_aucs.mean():+.4f}')
    print(f'  Targeted Delta={auc_b - auc_t:+.4f}')
    print(f'  Targeted within 2*std of random? {abs(auc_b-auc_t - (auc_b-random_aucs.mean())) <= 2*random_aucs.std()}')

    # Frozen scorer on targeted KO
    all_ft = mft + nft
    X_ft = np.array([[f[k] for k in keys_b] for f in all_ft])
    ms_ft = lr_b.predict_proba(X_ft[:len(mft)])[:,1]
    ns_ft = lr_b.predict_proba(X_ft[len(mft):])[:,1]
    labels_f = np.concatenate([np.ones(len(mft)), np.zeros(len(nft))])
    scores_f = np.concatenate([ms_ft, ns_ft])
    auc_ft = skm.roc_auc_score(labels_f, scores_f)
    print(f'  Frozen scorer (targeted KO): AUC={auc_ft:.4f} Delta={auc_b-auc_ft:+.4f}')

    print(f'\nVerdict: targeted Delta={auc_b-auc_t:+.4f}, random mean Delta={auc_b-random_aucs.mean():+.4f}')
    if abs(auc_b-auc_t) <= random_aucs.std():
        print('Targeted KO effect is within random variation -> top channels NOT special.')
    else:
        print('Targeted KO differs from random -> channels may be causally relevant.')

    # Save
    results = {'baseline_auc': auc_b, 'targeted_auc': auc_t, 'targeted_delta': auc_b-auc_t,
               'random_aucs': random_aucs.tolist(), 'random_mean': float(random_aucs.mean()),
               'random_std': float(random_aucs.std()), 'frozen_targeted_auc': auc_ft,
               'channel_counts': ch_counts, 'n_targeted': n_targeted}
    outdir = PROJECT / 'outputs' / 'h1-scout'
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / 'h1_matched_knockout.json', 'w') as f:
        json.dump(results, f, indent=2)
    print('Saved.')
