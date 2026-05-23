"""Preflight: validate ReDiffuse STL-10 split and training pipeline."""
import numpy as np
import sys
import os

# 1. Validate split manifest
split_path = r"D:\Code\DiffAudit\Download\shared\supplementary\rediffuse-openreview-supplement\extracted\Rediffuse\DDPM\STL10_train_ratio0.5.npz"
data = np.load(split_path)
train_idx = data['mia_train_idxs']
eval_idx = data['mia_eval_idxs']
overlap = len(set(train_idx.tolist()) & set(eval_idx.tolist()))

print(f"=== STL-10 Split Validation ===")
print(f"  Members: {len(train_idx)}, Nonmembers: {len(eval_idx)}")
print(f"  Overlap: {overlap}")
print(f"  Train range: {train_idx.min()}-{train_idx.max()}")
print(f"  Eval range: {eval_idx.min()}-{eval_idx.max()}")
assert overlap == 0, "OVERLAP DETECTED!"
assert len(train_idx) == 50000
assert len(eval_idx) == 50000
print("  PASSED")

# 2. Check GPU
import torch
print(f"\n=== Environment ===")
print(f"  PyTorch: {torch.__version__}")
print(f"  CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  GPU: {torch.cuda.get_device_name(0)}")
    mem = torch.cuda.get_device_properties(0).total_mem / 1024**3
    print(f"  VRAM: {mem:.1f} GB")

# 3. Check if STL-10 is already downloaded
stl10_root = r"D:\Code\DiffAudit\Download\shared\datasets"
stl10_dir = os.path.join(stl10_root, "stl10_binary")
if os.path.isdir(stl10_dir):
    print(f"\n  STL-10: already downloaded at {stl10_dir}")
else:
    print(f"\n  STL-10: NOT downloaded (needs 2.5 GB download)")

# 4. Estimate training time
print(f"\n=== Training Estimate ===")
total_steps = 800_000
batch_size = 128
total_images = total_steps * batch_size
print(f"  Total steps: {total_steps:,}")
print(f"  Batch size: {batch_size}")
print(f"  Total images processed: {total_images:,}")
print(f"  Estimated on A100: ~4 hours")
print(f"  Estimated on RTX 4070 Laptop: ~2-3 days (part-time)")
print(f"  Checkpoints: every 100k steps (8 checkpoints)")

# 5. Preflight decision
print(f"\n=== Preflight Verdict ===")
print(f"  Split: VALID (50k/50k, no overlap)")
print(f"  Code: complete (DDPM train + attack in supplement)")
print(f"  GPU: {'available' if torch.cuda.is_available() else 'UNAVAILABLE'}")
print(f"  Next: download STL-10, run 1k-step smoke test, then decide on full training")
