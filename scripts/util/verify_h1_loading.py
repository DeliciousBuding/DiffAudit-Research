import sys, os, json
from pathlib import Path

# Quick check: with the exact load_model() code from h1_activation_scout.py
PROJECT = Path("D:/Code/DiffAudit/Research")
MATERIALS = PROJECT / "references" / "materials" / "Rediffuse" / "DDPM"
sys.path.insert(0, str(MATERIALS))

import torch
from model_unet import UNet

T = 1000; CH = 128; CH_MULT = [1, 2, 2, 2]; ATTN = [1]; NUM_RES_BLOCKS = 2
DROPOUT = 0.1; DEVICE = torch.device("cpu")

# All Rediffuse-format checkpoints >100MB
checkpoints = [
    "D:/Code/DiffAudit/Download/checkpoints/pia-ddpm-cifar10/checkpoint.pt",
    "D:/Code/DiffAudit/Download/checkpoints/ddpm-cifar10-800k/checkpoint.pt",
    "D:/Code/DiffAudit/Download/checkpoints/ddpm-cifar100-800k/checkpoint.pt",
    "D:/Code/DiffAudit/Download/checkpoints/ddpm-cifar10-800k/checkpoint.pt",
    "D:/Code/DiffAudit/Download/checkpoints/ddpm-cifar100-800k/checkpoint.pt",
    "D:/Code/DiffAudit/Download/archive/rediffuse-stl10-bounded-scout-20260525/checkpoint-step-final.pt",
    "D:/Code/DiffAudit/Download/archive/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_EPS/ckpt-step99000.pt",
    "D:/Code/DiffAudit/Download/archive/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m1000_seed0_cont10k_EPS/ckpt-step9000.pt",
    "D:/Code/DiffAudit/Download/archive/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m1000_seed0_cont15k_EPS/ckpt-step5000.pt",
    "D:/Code/DiffAudit/Download/archive/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m1000_seed0_cont20k_EPS/ckpt-step5000.pt",
    "D:/Code/DiffAudit/Download/archive/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m1000_seed0_cont25k_EPS/ckpt-step5000.pt",
    "D:/Code/DiffAudit/Download/archive/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m1000_seed0_EPS/ckpt-step9000.pt",
    "D:/Code/DiffAudit/Download/archive/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m2000_seed0_EPS/ckpt-step8000.pt",
    "D:/Code/DiffAudit/Download/archive/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m5000_seed0_EPS/ckpt-step0.pt",
    "D:/Code/DiffAudit/Download/archive/collaborator-ddim-stl10-20260527/code/logs/DDPM_STL10_OVERFIT_m500_seed1_EPS/ckpt-step9000.pt",
    "D:/Code/DiffAudit/Download/checkpoints/openai-cifar10-500k/cifar10_openai_500k.pt",
    "D:/Code/DiffAudit/Download/checkpoints/ddim-cifar10-750k/DDIM-ckpt-step750000.pt",
]

# Exact load_model() logic from h1_activation_scout.py
for path in checkpoints:
    print(f"\n{'='*60}")
    print(f"  {os.path.basename(path)}")
    print(f"{'='*60}")
    try:
        model = UNet(T=T, ch=CH, ch_mult=CH_MULT, attn=ATTN,
                     num_res_blocks=NUM_RES_BLOCKS, dropout=DROPOUT).eval()
        ckpt = torch.load(path, map_location=DEVICE, weights_only=False)
        w = ckpt.get('ema_model', ckpt.get('net_model', ckpt))
        new = {k[7:] if k.startswith('module.') else k: v for k, v in w.items()}
        model.load_state_dict(new, strict=True)
        model_sd = model.state_dict()
        print(f"  [OK] STRICT load SUCCESS. {len(new)} keys matched.")
        # Verify hook paths exist
        downblocks = model.downblocks
        middleblocks = model.middleblocks
        upblocks = model.upblocks
        print(f"  [OK] downblocks: {len(downblocks)} modules")
        print(f"  [OK] middleblocks: {len(middleblocks)} modules")
        print(f"  [OK] upblocks: {len(upblocks)} modules")
        # Check hook sites from get_site_paths()
        late_down = model.downblocks[-1]
        mid_0 = model.middleblocks[0]
        mid_1 = model.middleblocks[1]
        early_up = model.upblocks[0]
        print(f"  [OK] Hook sites accessible: late_down, mid_0, mid_1, early_up")
    except Exception as e:
        # Try without strict
        try:
            model = UNet(T=T, ch=CH, ch_mult=CH_MULT, attn=ATTN,
                         num_res_blocks=NUM_RES_BLOCKS, dropout=DROPOUT).eval()
            model.load_state_dict(new, strict=False)
            missing = set(model.state_dict().keys()) - set(new.keys())
            unexpected = set(new.keys()) - set(model.state_dict().keys())
            print(f"  [FAIL] Strict load: {e}")
            print(f"  [WARN] Non-strict: {len(missing)} missing, {len(unexpected)} unexpected keys")
        except Exception as e2:
            print(f"  [FAIL] ALL loads: {e2}")
