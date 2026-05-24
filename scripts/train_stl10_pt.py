"""STL-10 DDPM training — optimized for RTX 4070 Laptop.
- AMP mixed precision for 2-3x faster training
- EMA updated every 10 steps (not every step) to reduce CPU bottleneck
- Flushed stdout for real-time monitoring
- Paths: set DIFFAUDIT_DATA / DIFFAUDIT_OUTPUT env vars to override defaults
"""
import os, copy, time, sys
import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset
from torchvision.utils import save_image

# === Paths: env-var overridable, repo-relative defaults ===
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_RESEARCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_ROOT = os.environ.get('DIFFAUDIT_DATA', os.path.join(_REPO, 'Download'))
SUPP = os.path.join(DATA_ROOT, 'shared', 'supplementary', 'rediffuse-openreview-supplement', 'extracted', 'Rediffuse')
OUTPUT_DIR = os.environ.get('DIFFAUDIT_OUTPUT', os.path.join(_RESEARCH, 'outputs', 'stl10-10k'))
PT_PATH = os.path.join(DATA_ROOT, 'shared', 'datasets', 'stl10_member_50k.pt')

sys.path.insert(0, os.path.join(SUPP, 'DDPM'))
from diffusion import GaussianDiffusionTrainer, GaussianDiffusionSampler
from model_unet import UNet

BATCH, TOTAL_STEPS = 48, 10000
IMG_SIZE, T = 32, 1000
EMA_EVERY = 10

def main():
    os.makedirs(os.path.join(OUTPUT_DIR, 'sample'), exist_ok=True)
    device = torch.device('cuda')
    print(f"GPU: {torch.cuda.get_device_name(0)}", flush=True)
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory/1024**3:.1f} GB", flush=True)
    print(f"Output: {OUTPUT_DIR}", flush=True)

    images = torch.load(PT_PATH, weights_only=True)
    print(f"Loaded: {images.shape}", flush=True)
    loader = DataLoader(TensorDataset(images), batch_size=BATCH, shuffle=True, drop_last=True,
                        num_workers=0, pin_memory=True)
    print(f"Batches: {len(loader)}", flush=True)

    model = UNet(T=T, ch=128, ch_mult=[1,2,2,2], attn=[1], num_res_blocks=2, dropout=0.1).to(device)
    ema_model = copy.deepcopy(model).eval()
    opt = torch.optim.Adam(model.parameters(), lr=2e-4)
    trainer = GaussianDiffusionTrainer(model, 1e-4, 0.02, T).to(device)
    sampler = GaussianDiffusionSampler(ema_model, 1e-4, 0.02, T, IMG_SIZE, 'epsilon', 'fixedlarge').to(device)
    scaler = torch.amp.GradScaler('cuda')
    print(f"Params: {sum(p.numel() for p in model.parameters())/1e6:.1f}M", flush=True)

    x_T = torch.randn(16, 3, IMG_SIZE, IMG_SIZE).to(device)
    losses, data_iter = [], iter(loader)
    t0 = time.time()

    for step in range(1, TOTAL_STEPS + 1):
        try: batch = next(data_iter)
        except StopIteration: data_iter = iter(loader); batch = next(data_iter)
        x_0 = batch[0].to(device, non_blocking=True)

        opt.zero_grad(set_to_none=True)
        with torch.amp.autocast('cuda'):
            loss = trainer(x_0).mean()
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt)
        scaler.update()

        if step % EMA_EVERY == 0:
            decay = 0.9999 ** EMA_EVERY
            for k, v in model.state_dict().items():
                ema_model.state_dict()[k].data.copy_(
                    ema_model.state_dict()[k].data * decay + v.data * (1 - decay))

        losses.append(loss.item())
        if step % 200 == 0 or step == 1:
            elapsed = time.time() - t0
            ips = step / elapsed if elapsed > 0 else 0
            eta = (TOTAL_STEPS - step) / ips / 60 if ips > 0 else 0
            avg = np.mean(losses[-100:]) if len(losses) >= 100 else np.mean(losses)
            mem = torch.cuda.memory_allocated() / 1024**3
            print(f"step {step}/{TOTAL_STEPS} | loss {avg:.4f} | {ips:.1f} it/s | ETA {eta:.0f}min | VRAM {mem:.1f}G", flush=True)

        if step % 2000 == 0:
            model.eval()
            with torch.no_grad(), torch.amp.autocast('cuda'):
                s = sampler(x_T)
                save_image((s + 1) / 2, os.path.join(OUTPUT_DIR, 'sample', f'step{step:06d}.png'))
            model.train()
            print(f"Sample saved at step {step}", flush=True)

        if step % 5000 == 0:
            ckpt = {'model': ema_model.state_dict(), 'step': step, 'losses': losses}
            torch.save(ckpt, os.path.join(OUTPUT_DIR, f'checkpoint-{step}.pt'))
            print(f"Saved checkpoint-{step}.pt", flush=True)

    torch.save({'model': ema_model.state_dict(), 'step': TOTAL_STEPS, 'losses': losses,
                 'total_hours': (time.time() - t0) / 3600}, os.path.join(OUTPUT_DIR, 'final.pt'))
    print(f"Done. {TOTAL_STEPS} steps. Final loss: {losses[-1]:.4f}", flush=True)

if __name__ == '__main__':
    main()
