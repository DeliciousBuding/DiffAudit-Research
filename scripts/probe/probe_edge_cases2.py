import torch

# Dig deeper into the black-box derived model format
path = "D:/Code/DiffAudit/Download/supplements/recon-assets/ndss-2025-blackbox-membership-inference-fine-tuned-diffusion-models/derived-smoke/shadow_member.pt"
ckpt = torch.load(path, map_location='cpu', weights_only=False)

text_list = ckpt['text']
image_list = ckpt['image']
print(f"text: list of {len(text_list)} items")
print(f"image: list of {len(image_list)} items")

# Check first few items
if text_list:
    item0 = text_list[0]
    print(f"text[0] type: {type(item0).__name__}")
    if isinstance(item0, dict):
        print(f"  keys: {list(item0.keys())}")
    elif isinstance(item0, torch.Tensor):
        print(f"  shape: {list(item0.shape)} dtype: {item0.dtype}")

if image_list:
    item0 = image_list[0]
    print(f"image[0] type: {type(item0).__name__}")
    if isinstance(item0, dict):
        print(f"  keys: {list(item0.keys())}")
        for k, v in item0.items():
            if isinstance(v, torch.Tensor):
                print(f"    {k}: shape={list(v.shape)} dtype={v.dtype}")
    elif isinstance(item0, torch.Tensor):
        print(f"  shape: {list(item0.shape)} dtype: {item0.dtype}")

# Also check a derived-public-10 file (smaller, easier to inspect)
path2 = "D:/Code/DiffAudit/Download/supplements/recon-assets/ndss-2025-blackbox-membership-inference-fine-tuned-diffusion-models/derived-public-10/shadow_member_proxy.pt"
ckpt2 = torch.load(path2, map_location='cpu', weights_only=False)
print(f"\n=== DERIVED-PUBLIC-10 SHADOW_MEMBER_PROXY ===")
print(f"text: list of {len(ckpt2['text'])} items")
print(f"image: list of {len(ckpt2['image'])} items")

# Also check the cifar10_openai_500k.pt guided-diffusion model more carefully
path3 = "D:/Code/DiffAudit/Download/checkpoints/openai-cifar10-500k/cifar10_openai_500k.pt"
ckpt3 = torch.load(path3, map_location='cpu', weights_only=False)
print(f"\n=== CIFAR10_OPENAI_500K (guided-diffusion) ===")
print(f"Type: {type(ckpt3).__name__}")
if isinstance(ckpt3, dict):
    print(f"Top-level keys: {sorted(set(k.split('.')[0] for k in ckpt3))}")
    # Check channel sizes from key layers
    for k in ['input_blocks.0.0.weight', 'input_blocks.1.0.in_layers.0.weight', 'middle_block.0.in_layers.0.weight']:
        if k in ckpt3:
            print(f"  {k}: shape={list(ckpt3[k].shape)}")
    # Check if there's a wrapper
    print(f"  has 'model' key: {'model' in ckpt3}")
    print(f"  has 'state_dict' key: {'state_dict' in ckpt3}")
    # Is there a 'label_emb' key?
    print(f"  has 'label_emb': {'label_emb' in sorted(set(k.split('.')[0] for k in ckpt3))}")
