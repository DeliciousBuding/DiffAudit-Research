import torch, sys

# 1. Black-box derived model - what's in text/image keys?
path = "D:/Code/DiffAudit/Download/black-box/supplementary/recon-assets/ndss-2025-blackbox-membership-inference-fine-tuned-diffusion-models/derived-smoke/shadow_member.pt"
ckpt = torch.load(path, map_location='cpu', weights_only=False)
print('=== SMOKE SHADOW MEMBER ===')
print('Type:', type(ckpt))
print('Keys:', list(ckpt.keys()) if isinstance(ckpt, dict) else 'N/A')
if isinstance(ckpt, dict):
    for k, v in ckpt.items():
        if isinstance(v, torch.Tensor):
            print(f'  {k}: shape={list(v.shape)} dtype={v.dtype}')
        elif isinstance(v, dict):
            print(f'  {k}: dict with keys {list(v.keys())[:10]}')
        else:
            print(f'  {k}: {type(v).__name__}')

print()

# 2. cifar10_member_25k.pt
path2 = "D:/Code/DiffAudit/Download/shared/datasets/cifar10_member_25k.pt"
data = torch.load(path2, map_location='cpu', weights_only=False)
print('=== CIFAR10_MEMBER_25K ===')
print('Type:', type(data))
if isinstance(data, torch.Tensor):
    print(f'  shape={list(data.shape)} dtype={data.dtype}')
elif isinstance(data, dict):
    print(f'  keys={list(data.keys())}')
    for k, v in data.items():
        if isinstance(v, torch.Tensor):
            print(f'  {k}: shape={list(v.shape)} dtype={v.dtype}')
        elif isinstance(v, (list, tuple)):
            print(f'  {k}: len={len(v)} type={type(v[0]).__name__ if v else "empty"}')
        else:
            print(f'  {k}: {type(v).__name__}')
elif isinstance(data, (list, tuple)):
    print(f'  len={len(data)}')
    if data:
        item = data[0]
        if isinstance(item, torch.Tensor):
            print(f'  item shape={list(item.shape)}')
        elif isinstance(item, (list, tuple)):
            print(f'  item is tuple/list of len {len(item)}')
            if len(item) > 0 and isinstance(item[0], torch.Tensor):
                print(f'  item[0] shape={list(item[0].shape)}')

print()

# 3. stl10_member_50k.pt
path3 = "D:/Code/DiffAudit/Download/shared/datasets/stl10_member_50k.pt"
data3 = torch.load(path3, map_location='cpu', weights_only=False)
print('=== STL10_MEMBER_50K ===')
print('Type:', type(data3))
if isinstance(data3, torch.Tensor):
    print(f'  shape={list(data3.shape)} dtype={data3.dtype}')
elif isinstance(data3, dict):
    print(f'  keys={list(data3.keys())}')
    for k, v in data3.items():
        if isinstance(v, torch.Tensor):
            print(f'  {k}: shape={list(v.shape)} dtype={v.dtype}')
elif isinstance(data3, (list, tuple)):
    print(f'  len={len(data3)}')

print()

# 4. stl10_member_cache.pt
path4 = "D:/Code/DiffAudit/Download/shared/supplementary/collaborator-ddim-stl10-20260527/code/data/datasets/pytorch/stl10_member_cache.pt"
data4 = torch.load(path4, map_location='cpu', weights_only=False)
print('=== STL10_MEMBER_CACHE ===')
print('Type:', type(data4))
if isinstance(data4, torch.Tensor):
    print(f'  shape={list(data4.shape)} dtype={data4.dtype}')
elif isinstance(data4, dict):
    print(f'  keys={list(data4.keys())}')
    for k, v in data4.items():
        if isinstance(v, torch.Tensor):
            print(f'  {k}: shape={list(v.shape)} dtype={v.dtype}')
elif isinstance(data4, (list, tuple)):
    print(f'  len={len(data4)}')

print()

# 5. beans-lora-peft
path5 = "D:/Code/DiffAudit/Download/black-box/weights/beans-lora-member-denoising-loss-20260513/unet_lora_peft_state.pt"
data5 = torch.load(path5, map_location='cpu', weights_only=False)
print('=== BEANS LORA PEFT ===')
print('Type:', type(data5))
if isinstance(data5, dict):
    print(f'  keys count: {len(data5)}')
    # Check which UNet base this is for - Stable Diffusion or Rediffuse?
    sample_keys = list(data5.keys())[:5]
    print(f'  sample: {sample_keys}')
    top_level = set(k.split('.')[0] for k in data5)
    print(f'  top_level: {sorted(top_level)}')
