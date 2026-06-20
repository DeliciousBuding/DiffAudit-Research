#!/usr/bin/env python
"""
H1 CIFAR-100 Fine Temporal Grid (8 timesteps)
==============================================
Tests temporal distribution of DAAB on CIFAR-100 DDPM.
Compare against CIFAR-10 DDPM (distributed) and DDIM 750k (concentrated).

Usage:
  conda activate retrace-tr
  python scripts/h1_fine_grid_cifar100.py
"""
import sys, os, json, time, pickle, warnings
from pathlib import Path
import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.decomposition import PCA
from sklearn import metrics as skm

PROJECT = Path(__file__).resolve().parents[1]
MATERIALS = PROJECT / "references" / "materials" / "Rediffuse" / "DDPM"
sys.path.insert(0, str(MATERIALS))
from model_unet import UNet
from dataset_utils import load_member_data

warnings.filterwarnings("ignore")
DEVICE = torch.device("cuda")

T=1000; CH=128; CH_MULT=[1,2,2,2]; ATTN=[1]; NUM_RES_BLOCKS=2; DROPOUT=0.1
BETA_1=0.0001; BETA_T=0.02
CKPT="D:/Code/DiffAudit/Download/checkpoints/ddpm-cifar100-800k/checkpoint.pt"
OUT=PROJECT/"outputs"/"h1-scout"
TIMESTEPS=[50,100,150,200,300,400,600,800]
SITES=["late_down","mid_0"]
N_M,N_NM,SEED=64,64,42

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

SP={"late_down":["downblocks","-1"],"mid_0":["middleblocks","0"]}

def lm():
    m=UNet(T=T,ch=CH,ch_mult=CH_MULT,attn=ATTN,num_res_blocks=NUM_RES_BLOCKS,dropout=DROPOUT).eval()
    c=torch.load(CKPT,map_location=DEVICE,weights_only=False)
    w=c.get('ema_model',c.get('net_model',c))
    nw={k[7:] if k.startswith('module.') else k:v for k,v in w.items()}
    m.load_state_dict(nw); m=m.to(DEVICE)
    m.alphas_cumprod=torch.cumprod(1-torch.linspace(BETA_1,BETA_T,T),dim=0).to(DEVICE)
    return m

def ex(m,ld,h,sn,ts,mn,lb):
    smp=[]; cnt=0
    for b in ld:
        im=b[0].to(DEVICE); B=im.shape[0]
        nd=mn-cnt
        if nd<=0: break
        if B>nd: im=im[:nd]; B=nd
        ba=[{} for _ in range(B)]
        for tv in ts:
            h.c(); tt=torch.full((B,),tv,device=DEVICE,dtype=torch.long)
            nz=torch.randn_like(im); ac=m.alphas_cumprod[tv]
            xt=ac.sqrt()*(im*2-1)+(1-ac).sqrt()*nz
            with torch.no_grad(): m(xt,tt)
            for s in sn:
                a=h.d.get(s)
                if a is None: continue
                for i in range(B): ba[i][f"{s}_t{tv}"]=a[i:i+1].cpu()
        smp.extend(ba); cnt+=B
        if cnt%16==0: print(f"  [{lb}] {cnt}/{mn}...")
    return smp[:mn]

def cf(rs):
    fs=[]
    for s in rs:
        f={}
        for k,a in s.items():
            C=a.shape[1]; fl=a.view(C,-1)
            mu=fl.abs().mean(dim=-1); vr=fl.var(dim=-1,unbiased=False)
            f[f"{k}_mu_abs"]=mu.numpy(); f[f"{k}_var"]=vr.numpy()
            f[f"{k}_mu_abs_mean"]=float(mu.mean()); f[f"{k}_var_mean"]=float(vr.mean())
        fs.append(f)
    return fs

def bpm(fl,ss,ts,st):
    cmp=[]
    for s in ss:
        for t in ts:
            for tp in st:
                k=f"{s}_t{t}_{tp}"
                if k in fl[0]: cmp.append(np.stack([f[k] for f in fl],axis=0))
    return np.concatenate(cmp,axis=1) if cmp else None

def bfm(fl,pm,ss,ts,st):
    sk=[k for k in fl[0] if isinstance(fl[0][k],(float,int,np.floating))]
    Xs=np.array([[f.get(k,0.0) for k in sk] for f in fl])
    pa=bpm(fl,ss,ts,st)
    if pa is not None and pm is not None:
        return np.concatenate([Xs,pm.transform(pa)],axis=1)
    return Xs

def cm(ms,nms):
    m,n=np.asarray(ms),np.asarray(nms)
    lb=np.concatenate([np.ones_like(m),np.zeros_like(n)])
    best=0.5
    for fl in [False,True]:
        sc=np.concatenate([m,n])
        if fl: sc=-sc
        try: auc=skm.roc_auc_score(lb,sc)
        except: auc=0.5
        if auc>best: best=round(auc,6)
    return best

class SKO:
    def __init__(s,sn,kt): s.sn=sn; s.kt=kt; s.ct=None
    def st(s,t): s.ct=t
    def __call__(s,m,i,o):
        if s.ct==s.kt: return o*0.0
        return o

def rko(m,ld,h,mf,nmf,sn,tk,ss,ts):
    ko=SKO(sn,tk); tg=m
    for p in SP[sn]:
        if p.lstrip('-').isdigit(): tg=tg[int(p)]
        else: tg=getattr(tg,p)
    hnd=tg.register_forward_hook(ko)
    def exk(mx,lb):
        sm=[]; cnt=0
        for b in ld:
            im=b[0].to(DEVICE); B=im.shape[0]
            nd=mx-cnt
            if nd<=0: break
            if B>nd: im=im[:nd]; B=nd
            ba=[{} for _ in range(B)]
            for tv in ts:
                h.c(); ko.st(tv)
                tt=torch.full((B,),tv,device=DEVICE,dtype=torch.long)
                nz=torch.randn_like(im); ac=m.alphas_cumprod[tv]
                xt=ac.sqrt()*(im*2-1)+(1-ac).sqrt()*nz
                with torch.no_grad(): m(xt,tt)
                for s in ss:
                    a=h.d.get(s)
                    if a is None: continue
                    for i in range(B): ba[i][f"{s}_t{tv}"]=a[i:i+1].cpu()
            sm.extend(ba); cnt+=B
        return sm[:mx]
    mk=exk(N_M,f"mk_{sn}_t{tk}"); nmk=exk(N_NM,f"nmk_{sn}_t{tk}")
    mfk=cf(mk); nmfk=cf(nmk)
    af=mfk+nmfk; y=np.concatenate([np.ones(len(mfk)),np.zeros(len(nmfk))])
    pca=PCA(n_components=6,random_state=SEED)
    pa=bpm(af,ss,ts,["mu_abs","var"]); pca.fit(pa)
    X=bfm(af,pca,ss,ts,["mu_abs","var"])
    lr=LogisticRegression(max_iter=5000,random_state=SEED,class_weight='balanced',solver='lbfgs')
    lr.fit(X,y)
    Xm=bfm(mfk,pca,ss,ts,["mu_abs","var"]); Xnm=bfm(nmfk,pca,ss,ts,["mu_abs","var"])
    auc=cm(lr.predict_proba(Xm)[:,1],lr.predict_proba(Xnm)[:,1])
    hnd.remove(); return auc

def main():
    t0=time.time()
    print("="*60+"\nH1 CIFAR-100 Fine Temporal Grid\n"+"="*60)
    m=lm(); h=HM()
    for n in SITES: h.r(m,n,SP[n])
    _,_,ml,nml=load_member_data(dataset_name='CIFAR100',batch_size=64,shuffle=False,randaugment=False)
    cp=OUT/"h1_cifar100_fine_grid_acts.pkl"
    if cp.exists():
        with open(cp,"rb") as f: c=pickle.load(f)
        mr=c["mr"]; nmr=c["nmr"]
    else:
        mr=ex(m,ml,h,SITES,TIMESTEPS,N_M,"m")
        nmr=ex(m,nml,h,SITES,TIMESTEPS,N_NM,"nm")
        with open(cp,"wb") as f: pickle.dump({"mr":mr,"nmr":nmr},f)
    mf=cf(mr); nmf=cf(nmr); af=mf+nmf
    y=np.concatenate([np.ones(len(mf)),np.zeros(len(nmf))])
    pca=PCA(n_components=6,random_state=SEED)
    pa=bpm(af,SITES,TIMESTEPS,["mu_abs","var"]); pca.fit(pa)
    X=bfm(af,pca,SITES,TIMESTEPS,["mu_abs","var"])
    lr=LogisticRegression(max_iter=5000,random_state=SEED,class_weight='balanced',solver='lbfgs')
    lr.fit(X,y)
    Xm=bfm(mf,pca,SITES,TIMESTEPS,["mu_abs","var"])
    Xnm=bfm(nmf,pca,SITES,TIMESTEPS,["mu_abs","var"])
    base=cm(lr.predict_proba(Xm)[:,1],lr.predict_proba(Xnm)[:,1])
    print(f"\n  Baseline AUC: {base:.4f}")
    res={"ckpt":"CIFAR100-DDPM","base":base,"grid":{}}
    print("\nRunning KO grid...")
    for sn in SITES:
        for tv in TIMESTEPS:
            lb=f"{sn}_t{tv}"
            print(f"  {lb}...",end=" ",flush=True)
            a=rko(m,ml,h,mf,nmf,sn,tv,SITES,TIMESTEPS)
            d=round(base-a,4); res["grid"][lb]={"auc":a,"delta":d}
            print(f"AUC={a:.4f}  D={d:+.4f}")
    h.rm()
    op=OUT/"h1_cifar100_fine_grid.json"
    with open(op,"w") as f: json.dump(res,f,indent=2)
    print(f"\nSaved to {op}")
    print(f"\n{'Site':<12}"+"".join(f"{'t='+str(t):>10}" for t in TIMESTEPS))
    for sn in SITES:
        vs=[f"{res['grid'][f'{sn}_t{t}']['delta']:+.4f}" for t in TIMESTEPS]
        print(f"  {sn:<12}"+"".join(f"{v:>10}" for v in vs))
    print(f"\n  CIFAR-10 DDPM: late_down max|D|=0.029  mid_0 max|D|=0.024")
    print(f"  CIFAR-100:      late_down max|D|={max(abs(res['grid'][f'late_down_t{t}']['delta']) for t in TIMESTEPS):.3f}  mid_0 max|D|={max(abs(res['grid'][f'mid_0_t{t}']['delta']) for t in TIMESTEPS):.3f}")
    print(f"  DDIM 750k:      late_down max|D|=0.221  mid_0 max|D|=0.194")
    print(f"  Time: {time.time()-t0:.0f}s")

if __name__=="__main__": main()
