#!/usr/bin/env python
"""CIFAR-100 channel knockout — matched-percent 4%, 30 seeds"""
import os, sys, json, pickle, numpy as np
from pathlib import Path
from scipy import stats as sps
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA
from sklearn import metrics as skm
import torch

PROJECT = Path(__file__).resolve().parents[2]  # Research/
DOWNLOAD = Path(os.environ.get("DIFFAUDIT_DOWNLOAD_ROOT", PROJECT.parent / "Download")).expanduser()
MATERIALS = PROJECT / "training" / "ddpm-cifar10"
sys.path.insert(0, str(MATERIALS))
from model_unet import UNet
from dataset_utils import load_member_data

DEV=torch.device('cuda')
T,CH=1000,128; CH_MULT=[1,2,2,2]; ATTN=[1]; NRB=2; DO=0.1
CKPT = DOWNLOAD / "checkpoints/ddpm-cifar100-800k/checkpoint.pt"
OUT=PROJECT/'outputs'/'h1-scout'
TS=[100,400,700]; SITES=['late_down','mid_0','mid_1','early_up']
NM,NNM,SEED,PCT,NS=64,64,42,0.04,30

class HM:
    def __init__(s): s.d={}; s.h=[]
    def _h(s,n):
        def f(m,i,o): s.d[n]=o.detach()
        return f
    def r(s,m,n,p):
        t=m
        for x in p:
            if x.lstrip('-').isdigit(): t=t[int(x)]
            else: t=getattr(t,x)
        s.h.append(t.register_forward_hook(s._h(n)))
    def c(s): s.d.clear()
    def rm(s):
        for h in s.h: h.remove()
        s.h.clear()

SP={'late_down':['downblocks','-1'],'mid_0':['middleblocks','0'],'mid_1':['middleblocks','1'],'early_up':['upblocks','0']}

def lm():
    m=UNet(T=T,ch=CH,ch_mult=CH_MULT,attn=ATTN,num_res_blocks=NRB,dropout=DO).eval()
    c=torch.load(CKPT,map_location=DEV,weights_only=False)
    w=c.get('ema_model',c.get('net_model',c))
    nw={k[7:] if k.startswith('module.') else k:v for k,v in w.items()}
    m.load_state_dict(nw); m=m.to(DEV)
    m.alphas_cumprod=torch.cumprod(1-torch.linspace(0.0001,0.02,T),dim=0).to(DEV)
    return m

def ex(m,ld,h,sn,ts,mn,lb):
    smp=[]; cnt=0
    for b in ld:
        im=b[0].to(DEV); B=im.shape[0]; nd=mn-cnt
        if nd<=0: break
        if B>nd: im=im[:nd]; B=nd
        ba=[{} for _ in range(B)]
        for tv in ts:
            h.c(); tt=torch.full((B,),tv,device=DEV,dtype=torch.long)
            nz=torch.randn_like(im); ac=m.alphas_cumprod[tv]
            xt=ac.sqrt()*(im*2-1)+(1-ac).sqrt()*nz
            with torch.no_grad(): m(xt,tt)
            for s in sn:
                a=h.d.get(s)
                if a is None: continue
                for i in range(B): ba[i][f'{s}_t{tv}']=a[i:i+1].cpu()
        smp.extend(ba); cnt+=B
        if cnt%16==0: print(f'  [{lb}] {cnt}/{mn}...')
    return smp[:mn]

def cf(rs):
    fs=[]
    for s in rs:
        f={}
        for k,a in s.items():
            C=a.shape[1]; fl=a.view(C,-1)
            mu=fl.abs().mean(dim=-1); vr=fl.var(dim=-1,unbiased=False)
            f[f'{k}_mu_abs']=mu.numpy(); f[f'{k}_var']=vr.numpy()
            f[f'{k}_mu_abs_mean']=float(mu.mean()); f[f'{k}_var_mean']=float(vr.mean())
        fs.append(f)
    return fs

def bpm(fl,ss,ts,st):
    cmp=[]
    for s in ss:
        for t in ts:
            for tp in st:
                k=f'{s}_t{t}_{tp}'
                if k in fl[0]: cmp.append(np.stack([f[k] for f in fl],axis=0))
    return np.concatenate(cmp,axis=1) if cmp else None

def bfm(fl,pm,ss,ts,st):
    sk=[k for k in fl[0] if isinstance(fl[0][k],(float,int,np.floating))]
    Xs=np.array([[f.get(k,0.0) for k in sk] for f in fl])
    pa=bpm(fl,ss,ts,st)
    if pa is not None and pm is not None: return np.concatenate([Xs,pm.transform(pa)],axis=1)
    return Xs

def cm(ms,nms):
    m,n=np.asarray(ms),np.asarray(nms)
    lb=np.concatenate([np.ones_like(m),np.zeros_like(n)])
    for fl in [False,True]:
        sc=np.concatenate([m,n])
        if fl: sc=-sc
        try: auc=round(skm.roc_auc_score(lb,sc),6); return auc
        except: pass
    return 0.5

# Find top channels
with open(OUT/'h1_cifar100_activations.pkl','rb') as f: cache=pickle.load(f)
mr=cache['member_raw']; nmr=cache['nonmember_raw']
mf=cf(mr); nmf=cf(nmr)
top_ch={}
for site in SITES:
    for tv in TS:
        k=f'{site}_t{tv}_mu_abs'
        if k not in mf[0]: continue
        ma=np.stack([f[k] for f in mf]); na=np.stack([f[k] for f in nmf])
        nc=ma.shape[1]; nk=max(1,int(nc*PCT))
        pv=[(sps.ttest_ind(ma[:,c],na[:,c])[1],c) for c in range(nc)]
        pv.sort()
        for _,c in pv[:nk]:
            if site not in top_ch: top_ch[site]=[]
            top_ch[site].append(c)
print(f'Top {PCT*100:.0f}%: {sum(len(v) for v in top_ch.values())} channels')

# Baseline
af=mf+nmf; y=np.concatenate([np.ones(len(mf)),np.zeros(len(nmf))])
pca=PCA(n_components=6,random_state=SEED)
pa=bpm(af,SITES,TS,['mu_abs','var']); pca.fit(pa)
X=bfm(af,pca,SITES,TS,['mu_abs','var'])
lr=LogisticRegression(max_iter=5000,random_state=SEED,class_weight='balanced',solver='lbfgs')
lr.fit(X,y)
Xm=bfm(mf,pca,SITES,TS,['mu_abs','var']); Xnm=bfm(nmf,pca,SITES,TS,['mu_abs','var'])
base=cm(lr.predict_proba(Xm)[:,1],lr.predict_proba(Xnm)[:,1])
print(f'Baseline AUC: {base:.4f}')

# KO experiment
m=lm(); h=HM()
for n in SITES: h.r(m,n,SP[n])
_,_,ml,nml=load_member_data(dataset_name='CIFAR100',batch_size=64,shuffle=False,randaugment=False)

class CKO:
    def __init__(s,cmap): s.cm=cmap; s.cs=None
    def ss(s,n): s.cs=n
    def __call__(s,md,i,o):
        if s.cs and s.cs in s.cm and s.cm[s.cs]:
            o2=o.clone(); o2[:,s.cm[s.cs]]=0; return o2
        return o

def rko(chmap,sd,lb):
    ko=CKO(chmap); hnds=[]
    for sn in SITES:
        t=m
        for p in SP[sn]:
            if p.lstrip('-').isdigit(): t=t[int(p)]
            else: t=getattr(t,p)
        hnds.append(t.register_forward_hook(ko))
    def exk(mx,lbl):
        sm=[]; cnt=0
        for b in ml:
            im=b[0].to(DEV); B=im.shape[0]; nd=mx-cnt
            if nd<=0: break
            if B>nd: im=im[:nd]; B=nd
            ba=[{} for _ in range(B)]
            for tv in TS:
                h.c()
                for sn in SITES: ko.ss(sn)
                tt=torch.full((B,),tv,device=DEV,dtype=torch.long)
                nz=torch.randn_like(im); ac=m.alphas_cumprod[tv]
                xt=ac.sqrt()*(im*2-1)+(1-ac).sqrt()*nz
                with torch.no_grad(): m(xt,tt)
                for sn in SITES:
                    a=h.d.get(sn)
                    if a is None: continue
                    for i in range(B): ba[i][f'{sn}_t{tv}']=a[i:i+1].cpu()
            sm.extend(ba); cnt+=B
        return sm[:mx]
    mk=exk(NM,f'm_{lb}'); nmk=exk(NNM,f'nm_{lb}')
    mfk=cf(mk); nmfk=cf(nmk); afk=mfk+nmfk
    yk=np.concatenate([np.ones(len(mfk)),np.zeros(len(nmfk))])
    pk=PCA(n_components=6,random_state=sd)
    pa=bpm(afk,SITES,TS,['mu_abs','var']); pk.fit(pa)
    Xk=bfm(afk,pk,SITES,TS,['mu_abs','var'])
    lrk=LogisticRegression(max_iter=5000,random_state=sd,class_weight='balanced',solver='lbfgs')
    lrk.fit(Xk,yk)
    Xmk=bfm(mfk,pk,SITES,TS,['mu_abs','var']); Xnmk=bfm(nmfk,pk,SITES,TS,['mu_abs','var'])
    auc=cm(lrk.predict_proba(Xmk)[:,1],lrk.predict_proba(Xnmk)[:,1])
    for hnd in hnds: hnd.remove()
    return auc

t_aucs=[]; r_aucs=[]
for si in range(NS):
    rs=SEED+si; np.random.seed(rs)
    ta=rko(top_ch,rs,f'targeted_s{si}')
    rm={}
    for sn in SITES:
        k=f'{sn}_t100_mu_abs'
        if k in mf[0]:
            nc=mf[0][k].shape[0]; nk=max(1,int(nc*PCT))
            rm[sn]=list(np.random.choice(nc,nk,replace=False))
    ra=rko(rm,rs,f'random_s{si}')
    t_aucs.append(ta); r_aucs.append(ra)
    print(f'  seed {si+1:2d}/{NS}: t={ta:.4f} r={ra:.4f} d={ta-ra:+.4f}')

h.rm()
ta=np.array(t_aucs); ra=np.array(r_aucs); diff=ta-ra
mu_d=np.mean(diff); sd_d=np.std(diff,ddof=1)
d=mu_d/sd_d if sd_d>0 else 0
_,pv=sps.ttest_rel(ta,ra)
ci_l=mu_d-1.96*sd_d/np.sqrt(NS); ci_h=mu_d+1.96*sd_d/np.sqrt(NS)

res={'ckpt':'CIFAR100-DDPM','base':base,'pct':PCT,'n_seeds':NS,
     'targeted':{'mu':float(np.mean(ta)),'std':float(np.std(ta,ddof=1))},
     'random':{'mu':float(np.mean(ra)),'std':float(np.std(ra,ddof=1))},
     'comparison':{'mean_diff':float(mu_d),'std_diff':float(sd_d),'cohens_d':float(d),'p':float(pv),'ci95':[float(ci_l),float(ci_h)]}}
with open(OUT/'h1_channel_knockout_cifar100.json','w') as f: json.dump(res,f,indent=2)
print(f'\nTargeted: mu={np.mean(ta):.4f} std={np.std(ta,ddof=1):.4f}')
print(f'Random:   mu={np.mean(ra):.4f} std={np.std(ra,ddof=1):.4f}')
print(f'Diff: mu={mu_d:+.4f} std={sd_d:.4f} d={d:.2f} p={pv:.3f}')
print(f'95% CI: [{ci_l:+.4f}, {ci_h:+.4f}]')
print(f'\nCross-checkpoint: CIFAR-10 DDPM d=0.21 p=0.26 | DDIM d=0.10 p=0.60 | CIFAR-100 d={d:.2f} p={pv:.3f}')
