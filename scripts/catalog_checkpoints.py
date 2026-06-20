#!/usr/bin/env python
"""
Catalog ALL model checkpoint .pt files in D:/Code/DiffAudit/Download/
For each file >100MB with UNet weights: determine format, compatibility, dataset match.
"""
import sys, os, json
from pathlib import Path
from collections import OrderedDict

DOWNLOAD = Path("D:/Code/DiffAudit/Download")
REDIFFUSE_ROOT = Path("D:/Code/DiffAudit/Research/references/materials/Rediffuse/DDPM")
sys.path.insert(0, str(REDIFFUSE_ROOT))

import torch

# ── Rediffuse UNet signatures ──
# Rediffuse UNet attrs: time_embedding, head, downblocks, middleblocks, upblocks, tail
# Keys inside time_embedding: timembedding (an Embedding)
# Key names use full word 'time_embedding' not 'time_embed'

# guided-diffusion UNet: time_embed, input_blocks, middle_block, output_blocks, out

# secmi-bundle: stored as {'net_model': state_dict} with optional 'ema_model', 'optimizer', 'step'

REDIFFUSE_TOP_KEYS = {'head', 'tail', 'downblocks', 'middleblocks', 'upblocks', 'time_embedding'}
GUIDED_DIFFUSION_TOP_KEYS = {'time_embed', 'input_blocks', 'middle_block', 'output_blocks', 'out', 'label_emb'}

TARGET = "D:/Code/DiffAudit/Download"

def size_mb(p):
    return p.stat().st_size / (1024 * 1024)

def get_unet_state_dict(ckpt):
    """Extract the UNet state_dict from various checkpoint wrappers."""
    if isinstance(ckpt, dict):
        # secmi-bundle style: {'net_model': ..., 'ema_model': ..., 'step': ...}
        if 'net_model' in ckpt:
            return ckpt['net_model']
        if 'ema_model' in ckpt:
            return ckpt['ema_model']
        if 'model_state_dict' in ckpt:
            return ckpt['model_state_dict']
        if 'state_dict' in ckpt:
            return ckpt['state_dict']
        if 'model' in ckpt:
            return ckpt['model']
        # Check if it looks like a raw state_dict (has UNet-like keys)
        if any(k.startswith('time_embed') or k.startswith('head.') or k.startswith('downblocks.')
               for k in list(ckpt.keys())[:20]):
            return ckpt
        # Check if it has 'module.' prefix (DataParallel wrapper)
        if any(k.startswith('module.') for k in list(ckpt.keys())[:20]):
            return {k[7:]: v for k, v in ckpt.items()}
        return ckpt
    return ckpt

def strip_module_prefix(sd):
    """Strip 'module.' prefix from keys if present."""
    if any(k.startswith('module.') for k in sd):
        return {k[7:]: v for k, v in sd.items()}
    return sd

def classify_keys(sd):
    """Given a state_dict, classify the key structure."""
    keys = list(sd.keys())
    if not keys:
        return {"type": "empty", "keys": []}

    # Check top-level attribute sets
    top_level = set()
    for k in keys:
        top = k.split('.')[0]
        top_level.add(top)

    result = {
        "top_level_keys": sorted(top_level),
        "sample_keys": keys[:10],
        "num_keys": len(keys),
    }

    # Rediffuse UNet check
    rediffuse_match = top_level & REDIFFUSE_TOP_KEYS
    if 'time_embedding' in top_level:
        # Check for timembedding subkey
        te_keys = [k for k in keys if k.startswith('time_embedding.')]
        has_timembedding = any('timembedding' in k for k in te_keys)
        result["rediffuse_compat"] = {
            "has_time_embedding": True,
            "has_timembedding": has_timembedding,
            "has_downblocks": 'downblocks' in top_level,
            "has_middleblocks": 'middleblocks' in top_level,
            "has_upblocks": 'upblocks' in top_level,
            "has_head": 'head' in top_level,
            "has_tail": 'tail' in top_level,
            "matched_top_keys": sorted(rediffuse_match),
        }

    # guided-diffusion check
    guided_match = top_level & GUIDED_DIFFUSION_TOP_KEYS
    if guided_match:
        result["guided_diffusion_compat"] = {
            "has_time_embed": 'time_embed' in top_level,
            "has_input_blocks": 'input_blocks' in top_level,
            "has_middle_block": 'middle_block' in top_level,
            "has_output_blocks": 'output_blocks' in top_level,
            "matched_top_keys": sorted(guided_match),
        }

    # Determine overall format
    if len(rediffuse_match) >= 4:
        result["likely_format"] = "rediffuse-unet"
    elif len(guided_match) >= 3:
        result["likely_format"] = "guided-diffusion-unet"
    elif 'time_embedding' in top_level and result.get("rediffuse_compat", {}).get("has_timembedding"):
        result["likely_format"] = "rediffuse-unet"
    elif 'time_embed' in top_level:
        result["likely_format"] = "guided-diffusion-unet"
    else:
        result["likely_format"] = "unknown"

    return result

def check_ch_mult(sd):
    """Estimate ch and ch_mult from conv weight shapes in downblocks."""
    ch_vals = []
    for k in sd:
        if 'downblocks' in k or 'input_blocks' in k:
            if k.endswith('.weight') and ('conv' in k.lower() or 'block1' in k or 'block2' in k or 'proj' in k):
                shape = sd[k].shape
                if len(shape) >= 2:
                    ch_vals.append(shape[0])
    if not ch_vals:
        return None
    # Find first channel size (likely ch)
    return {"first_ch": min(ch_vals) if ch_vals else None, "max_ch": max(ch_vals) if ch_vals else None,
            "unique_ch_sizes": sorted(set(ch_vals))}

def check_attention(sd):
    """Check for attention blocks in downblocks/middleblocks."""
    has_attn = any('attn' in k.lower() for k in sd)
    return has_attn

def infer_dataset_from_path(path_str):
    """Heuristically determine dataset from path."""
    p = path_str.lower()
    datasets = []
    if 'cifar10' in p or 'cifar_10' in p:
        datasets.append('CIFAR10')
    if 'cifar100' in p or 'cifar_100' in p:
        datasets.append('CIFAR100')
    if 'stl10' in p or 'stl_10' in p:
        datasets.append('STL10')
    if 'celeba' in p or 'celeba' in p:
        datasets.append('CelebA')
    if 'imagenet' in p:
        datasets.append('ImageNet')
    return datasets if datasets else ['unknown']

def infer_step_from_path(path_str):
    """Heuristically determine training step from filename or path."""
    import re
    p = path_str.lower()
    # Look for step patterns
    m = re.search(r'step[_-]?(\d+)', p)
    if m:
        return int(m.group(1))
    m = re.search(r'ckpt[_-]?(\d+)', p)
    if m:
        return int(m.group(1))
    m = re.search(r'(\d+)k', p)
    if m:
        return int(m.group(1)) * 1000
    return None

def can_load_with_rediffuse(sd):
    """Check if state_dict can be loaded into Rediffuse UNet(ch=128, ch_mult=[1,2,2,2])."""
    from model_unet import UNet
    try:
        model = UNet(T=1000, ch=128, ch_mult=[1,2,2,2], attn=[1], num_res_blocks=2, dropout=0.1)
        # Strip module prefix
        clean = strip_module_prefix(sd)
        model.load_state_dict(clean, strict=False)
        # Check for missing / unexpected
        model_sd = model.state_dict()
        missing = set(model_sd.keys()) - set(clean.keys())
        unexpected = set(clean.keys()) - set(model_sd.keys())
        shape_mismatches = []
        for k in set(model_sd.keys()) & set(clean.keys()):
            if model_sd[k].shape != clean[k].shape:
                shape_mismatches.append(f"{k}: model={list(model_sd[k].shape)} ckpt={list(clean[k].shape)}")
        return {
            "loads": True,
            "missing_keys": sorted(missing)[:20] if missing else [],
            "unexpected_keys": sorted(unexpected)[:20] if unexpected else [],
            "shape_mismatches": shape_mismatches[:20],
        }
    except Exception as e:
        return {"loads": False, "error": str(e)[:300]}

def find_dataset_splits(path_str):
    """Find matching dataset split files."""
    base = Path(path_str)
    parent = base.parent
    # Look for .json, .txt, .csv files in same or parent directories
    candidates = []
    for ext in ['*.json', '*.txt', '*.csv', '*.pkl', '*.npy']:
        candidates.extend(parent.glob(ext))
        if parent.parent != parent:
            candidates.extend(parent.parent.glob(ext))
    # Also check known dataset locations
    dataset_dir = DOWNLOAD / "shared" / "datasets"
    if dataset_dir.exists():
        candidates.extend(dataset_dir.glob("*.pt"))
        candidates.extend(dataset_dir.glob("*.json"))

    relevant = []
    for c in candidates:
        cname = c.name.lower()
        # Match dataset keyword
        datasets = infer_dataset_from_path(str(path_str))
        for ds in datasets:
            if ds.lower() in cname:
                relevant.append(str(c))
                break
    return sorted(set(relevant))[:5]

def main():
    all_pt = sorted(DOWNLOAD.rglob("*.pt"))
    print(f"Found {len(all_pt)} .pt files total\n")

    results = []

    for pt_path in all_pt:
        mb = size_mb(pt_path)
        # Skip tiny files (<100MB) for UNet check, but still catalog
        print(f"  [{mb:.1f} MB] {pt_path.relative_to(DOWNLOAD)}")

        entry = {
            "path": str(pt_path),
            "relative_path": str(pt_path.relative_to(DOWNLOAD)),
            "size_bytes": pt_path.stat().st_size,
            "size_mb": round(mb, 2),
        }

        # Load checkpoint
        try:
            ckpt = torch.load(str(pt_path), map_location='cpu', weights_only=False)
        except Exception as e:
            entry["load_error"] = str(e)[:200]
            results.append(entry)
            continue

        # Determine checkpoint wrapper type
        if isinstance(ckpt, dict):
            wrapper_keys = list(ckpt.keys())
            entry["wrapper_keys"] = wrapper_keys[:20]
            if 'step' in ckpt:
                if isinstance(ckpt['step'], (int, float)):
                    entry["training_step"] = int(ckpt['step'])
                elif isinstance(ckpt['step'], torch.Tensor):
                    entry["training_step"] = ckpt['step'].item()
            if 'epoch' in ckpt:
                entry["epoch"] = ckpt['epoch'].item() if isinstance(ckpt['epoch'], torch.Tensor) else ckpt['epoch']
        else:
            entry["wrapper_keys"] = ["<raw_tensor_or_other>"]

        # Extract UNet state_dict
        sd = get_unet_state_dict(ckpt)
        if isinstance(sd, dict) and sd:
            key_info = classify_keys(sd)
            entry["key_analysis"] = key_info

            # Channel analysis
            ch_info = check_ch_mult(sd)
            if ch_info:
                entry["channel_analysis"] = ch_info

            # Attention check
            entry["has_attention"] = check_attention(sd)

            # Rediffuse compatibility load test (only for files > 100MB that look like UNets)
            if mb > 100 and key_info.get("likely_format") in ("rediffuse-unet", "guided-diffusion-unet"):
                entry["rediffuse_load_test"] = can_load_with_rediffuse(sd)

        # Heuristics
        entry["inferred_dataset"] = infer_dataset_from_path(str(pt_path))
        inferred_step = infer_step_from_path(str(pt_path))
        if inferred_step is not None:
            entry["inferred_step"] = inferred_step

        # Matching dataset splits
        entry["matching_dataset_files"] = find_dataset_splits(str(pt_path))

        results.append(entry)

    # ── Write output ──
    out_path = Path("D:/Code/DiffAudit/Research/outputs/catalog_checkpoints.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n\nResults written to {out_path}")
    print(f"Total .pt files: {len(results)}")

    # Summary
    unet_large = [r for r in results if r['size_mb'] > 100 and r.get('key_analysis', {}).get('likely_format') in ('rediffuse-unet', 'guided-diffusion-unet')]
    print(f"UNet checkpoints >100MB: {len(unet_large)}")
    for r in unet_large:
        lt = r.get('rediffuse_load_test', {})
        print(f"  {r['relative_path']}")
        print(f"    size={r['size_mb']}MB format={r.get('key_analysis',{}).get('likely_format','?')}")
        if lt:
            print(f"    loads={lt.get('loads')} missing={len(lt.get('missing_keys',[]))} unexpected={len(lt.get('unexpected_keys',[]))} shape_mismatches={len(lt.get('shape_mismatches',[]))}")

if __name__ == "__main__":
    main()
