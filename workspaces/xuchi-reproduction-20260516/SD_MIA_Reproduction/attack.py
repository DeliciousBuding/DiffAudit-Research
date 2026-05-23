"""
REDIFFUSE — Black-Box Membership Inference Attack for Stable Diffusion
Paper: "Towards Black-Box Membership Inference Attack for Diffusion Models" (ICML 2025)
Section 5.4 & Appendix A  —  Stable Diffusion experiment

Paper-exact settings:
  model     : CompVis/stable-diffusion-v1-4  (no fine-tuning)
  member    : LAION-5B subset, 2500 images
  nonmember : COCO2017-val,    2500 images
  T=1000, t=10 (interval), k=10, attack_num=1, n=10 (average)
  D(x, x_hat) = SSIM  (data_range=255, RGB 3-channel)
"""

import json
import base64
import io
import logging
import time
from itertools import chain
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

import fire
import numpy as np
import torch
from PIL import Image
from pytorch_lightning import seed_everything
from rich.logging import RichHandler
from rich.progress import track
from sklearn import metrics
from skimage.metrics import structural_similarity as ssim
from diffusers import StableDiffusionPipeline
from torchvision import transforms

import components
from dataset import load_member_data


DEVICE = torch.device("cuda:0") if torch.cuda.is_available() else torch.device("cpu")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pixel_tensor_to_float_arrays(x: torch.Tensor) -> np.ndarray:
    """
    Convert a normalized [-1,1] pixel tensor [B,3,H,W] to float32 numpy arrays
    [B,H,W,3] in [0, 1] range.  Keeps full float precision (no uint8 rounding).
    """
    x = x.detach().clamp(-1, 1)
    x = (x + 1.0) / 2.0                     # → [0, 1] float
    x = x.permute(0, 2, 3, 1).float().cpu().numpy()
    return x  # [B, H, W, 3] float32


def decode_reconstruction_images_float(
    model, latent_samples: torch.Tensor, decode_chunk_size: int = 4
) -> np.ndarray:
    """
    Decode 5-D latent samples [n, B, C, H, W] to averaged float32 numpy arrays
    [B, H, W, 3] in [0, 1] range.

    All operations done in float — no uint8 rounding until SSIM.
    Critical for ReDiffuse: averaging n=10 reconstructions in pixel space
    must preserve sub-integer precision (paper Section 4.3).
    """
    assert latent_samples.ndim == 5, (
        f"expected 5D [n, B, C, H, W] for ReDiffuse averaging, "
        f"got {tuple(latent_samples.shape)}"
    )
    n, B = latent_samples.shape[:2]
    flat = latent_samples.reshape(n * B, *latent_samples.shape[2:])  # [n*B, C, H, W]

    # Decode chunk-by-chunk, keep float in [0, 1]
    pieces: List[torch.Tensor] = []
    for chunk in torch.split(flat, decode_chunk_size, dim=0):
        with torch.no_grad():
            img = model.vae.decode(
                chunk / model.vae.config.scaling_factor, return_dict=False
            )[0]                                      # [chunk, 3, H, W] in [-1, 1]
        img = (img / 2.0 + 0.5).clamp(0, 1)          # [0, 1] float
        pieces.append(img.float().cpu())
    decoded = torch.cat(pieces, dim=0)               # [n*B, 3, H, W] float

    # Reshape to [n, B, 3, H, W], average over n (in float, no rounding)
    decoded = decoded.reshape(n, B, *decoded.shape[1:])
    averaged = decoded.mean(dim=0)                   # [B, 3, H, W] float

    # → numpy [B, H, W, 3] float32
    return averaged.permute(0, 2, 3, 1).numpy()


def decode_latent_images_float(
    model, latents: torch.Tensor, decode_chunk_size: int = 4
) -> np.ndarray:
    """Decode a [B, C, H, W] latent tensor to RGB float arrays [B, H, W, 3]."""
    pieces: List[torch.Tensor] = []
    for chunk in torch.split(latents, decode_chunk_size, dim=0):
        with torch.no_grad():
            img = model.vae.decode(
                chunk / model.vae.config.scaling_factor, return_dict=False
            )[0]
        img = (img / 2.0 + 0.5).clamp(0, 1)
        pieces.append(img.float().cpu())
    decoded = torch.cat(pieces, dim=0)
    return decoded.permute(0, 2, 3, 1).numpy()


def calculate_ssim(image1: np.ndarray, image2: np.ndarray) -> float:
    """
    SSIM between two float32 RGB arrays in [0, 1].
    data_range=1.0 keeps full float precision (paper-exact RGB SSIM).
    """
    return float(ssim(image1, image2, data_range=1.0, channel_axis=-1))


def rediffuse_step_features(
    model,
    original_images: np.ndarray,
    reverse_steps: torch.Tensor,
    denoise_steps: torch.Tensor,
    scorer: str = "original_ssim",
    decode_chunk_size: int = 4,
) -> np.ndarray:
    """
    Return per-step ReDiffuse SSIM features as [B, attack_num].

    Higher values mean a sample reconstructs more like a member.  Keeping every
    step lets us do cheap offline scoring sweeps without rerunning Stable
    Diffusion.
    """
    if denoise_steps.ndim != 6:
        raise ValueError(
            f"expected ReDiffuse denoise tensor [steps, average, B, C, H, W], "
            f"got {tuple(denoise_steps.shape)}"
        )
    if reverse_steps.ndim != 5:
        raise ValueError(
            f"expected ReDiffuse reverse tensor [steps, B, C, H, W], got {tuple(reverse_steps.shape)}"
        )

    step_features: List[List[float]] = []
    for step_idx in range(denoise_steps.shape[0]):
        if scorer == "latent_mse":
            recon_latent = denoise_steps[step_idx].mean(dim=0)
            dist = ((reverse_steps[step_idx] - recon_latent).float().abs() ** 2).flatten(1).mean(dim=-1)
            step_features.append((-dist).detach().cpu().numpy().astype(np.float32).tolist())
        else:
            recon = decode_reconstruction_images_float(
                model, denoise_steps[step_idx], decode_chunk_size=decode_chunk_size
            )
            if scorer == "original_ssim":
                reference = original_images
            elif scorer == "vae_ssim":
                reference = decode_latent_images_float(
                    model, reverse_steps[step_idx], decode_chunk_size=decode_chunk_size
                )
            else:
                raise ValueError("rediffuse_scorer must be original_ssim, vae_ssim, or latent_mse")
            step_features.append(
                [calculate_ssim(reference[i], recon[i]) for i in range(len(reference))]
            )
    return np.asarray(step_features, dtype=np.float32).T


def aggregate_rediffuse_features(features: np.ndarray, score_mode: str) -> np.ndarray:
    """
    Convert [N, attack_num] SSIM features to one similarity value per sample.
    Higher returned values mean more member-like.
    """
    if features.ndim == 1:
        features = features.reshape(-1, 1)
    if features.ndim != 2 or features.shape[1] == 0:
        raise ValueError(f"expected [N, steps] features, got {features.shape}")

    if score_mode == "first":
        return features[:, 0]
    if score_mode == "last":
        return features[:, -1]
    if score_mode == "mean":
        return features.mean(axis=1)
    if score_mode == "median":
        return np.median(features, axis=1)
    if score_mode == "max":
        return features.max(axis=1)
    if score_mode == "min":
        return features.min(axis=1)
    if score_mode.startswith("step"):
        idx = int(score_mode[4:])
        if idx < 0 or idx >= features.shape[1]:
            raise ValueError(f"{score_mode!r} out of range for {features.shape[1]} steps")
        return features[:, idx]
    raise ValueError(
        f"Unknown score_mode={score_mode!r}. "
        "Use first,last,mean,median,max,min, or step0/step1/..."
    )


def roc(member_scores: torch.Tensor, nonmember_scores: torch.Tensor, n_points: int = 2000):
    """Compute AUC, best-threshold ASR, FPR list, TPR list, and best threshold."""
    lo = min(member_scores.min(), nonmember_scores.min()).item()
    hi = max(member_scores.max(), nonmember_scores.max()).item()
    step = (hi - lo) / n_points if hi != lo else 1e-8

    FPR_list, TPR_list = [], []
    max_asr, best_thr = 0.0, lo

    for thr in torch.arange(lo, hi + step, step):
        TP = (member_scores <= thr).sum()
        TN = (nonmember_scores > thr).sum()
        FP = (nonmember_scores <= thr).sum()
        FN = (member_scores > thr).sum()
        TPR = (TP / (TP + FN)).item()
        FPR = (FP / (FP + TN)).item()
        ASR = ((TP + TN) / (TP + TN + FP + FN)).item()
        TPR_list.append(TPR)
        FPR_list.append(FPR)
        if ASR > max_asr:
            max_asr = ASR
            best_thr = thr

    FPR_arr = np.asarray(FPR_list)
    TPR_arr = np.asarray(TPR_list)
    auc = metrics.auc(FPR_arr, TPR_arr)
    return auc, max_asr, torch.from_numpy(FPR_arr), torch.from_numpy(TPR_arr), best_thr


# ---------------------------------------------------------------------------
# Stable Diffusion pipeline wrapper
# ---------------------------------------------------------------------------

class EpsGetter(components.EpsGetter):
    def __call__(self, xt, condition=None, noise_level=None, t=None):
        return self.model(t, condition, latents=xt)


class MyStableDiffusionPipeline(StableDiffusionPipeline):

    @torch.no_grad()
    def prepare_latent(self, img: torch.Tensor) -> torch.Tensor:
        """
        Paper Section 4.3:  z = Encoder(x)
        Use .mode() (posterior mean) for deterministic, unbiased encoding.
        """
        vae_dtype = next(self.vae.parameters()).dtype
        img = img.to(dtype=vae_dtype)
        latents = self.vae.encode(img).latent_dist.mode()
        return latents * self.vae.config.scaling_factor

    @torch.no_grad()
    def encode_input_prompt(self, prompt, do_classifier_free_guidance: bool = True):
        if hasattr(self, "encode_prompt"):
            prompt_embeds, negative_prompt_embeds = self.encode_prompt(
                prompt,
                DEVICE,
                1,
                do_classifier_free_guidance,
                negative_prompt=None,
                prompt_embeds=None,
                negative_prompt_embeds=None,
                lora_scale=None,
            )
            if do_classifier_free_guidance:
                return torch.cat([negative_prompt_embeds, prompt_embeds])
            return prompt_embeds

        return self._encode_prompt(
            prompt, DEVICE, 1, do_classifier_free_guidance,
            None, prompt_embeds=None, negative_prompt_embeds=None, lora_scale=None,
        )

    @torch.no_grad()
    def __call__(
        self,
        t,
        prompt_embeds,
        prompt: Union[str, List[str]] = None,
        height: Optional[int] = None,
        width: Optional[int] = None,
        guidance_scale: float = 1.0,   # paper-aligned: variation API uses no CFG (no text guidance amplification)
        negative_prompt: Optional[Union[str, List[str]]] = None,
        latents: Optional[torch.FloatTensor] = None,
        negative_prompt_embeds: Optional[torch.FloatTensor] = None,
        callback_steps: int = 1,
        cross_attention_kwargs: Optional[Dict[str, Any]] = None,
    ):
        height = height or self.unet.config.sample_size * self.vae_scale_factor
        width  = width  or self.unet.config.sample_size * self.vae_scale_factor
        self.check_inputs(prompt, height, width, callback_steps,
                          negative_prompt, prompt_embeds, negative_prompt_embeds)

        do_cfg = guidance_scale > 1.0
        latent_input = torch.cat([latents] * 2) if do_cfg else latents

        noise_pred = self.unet(
            latent_input, t,
            encoder_hidden_states=prompt_embeds,
            cross_attention_kwargs=cross_attention_kwargs,
            return_dict=False,
        )[0]

        if do_cfg:
            uncond, text = noise_pred.chunk(2)
            noise_pred = uncond + guidance_scale * (text - uncond)

        return noise_pred

    def get_image(self, latents: torch.Tensor) -> List[Image.Image]:
        """Decode scaled latents to PIL RGB images."""
        image = self.vae.decode(
            latents / self.vae.config.scaling_factor, return_dict=False
        )[0]
        return self.image_processor.postprocess(
            image, output_type="pil", do_denormalize=[True] * image.shape[0]
        )


# ---------------------------------------------------------------------------
# Beta schedule & attacker registry
# ---------------------------------------------------------------------------

def _make_betas(beta_start: float = 0.00085, beta_end: float = 0.012, T: int = 1000):
    """Linear beta schedule matching SD v1-4 training (Appendix A)."""
    return torch.from_numpy(np.linspace(beta_start, beta_end, T)).float()


ATTACKERS: Dict[str, Type[components.DDIMAttacker]] = {
    "SecMI":    components.SecMIAttacker,
    "PIA":      components.PIA,
    "PIAN":     components.PIAN,
    "Naive":    components.NaiveAttacker,
    "ReDiffuse": components.ReDiffuseAttacker,
}


def resolve_torch_dtype(name: str) -> torch.dtype:
    name = str(name).lower()
    if name == "auto":
        return torch.float16 if torch.cuda.is_available() else torch.float32
    if name in {"fp16", "float16", "half"}:
        return torch.float16
    if name in {"fp32", "float32", "full"}:
        return torch.float32
    raise ValueError("torch_dtype must be auto, float16, or float32")


# ---------------------------------------------------------------------------
# Progress / checkpoint helpers (optional, for long runs)
# ---------------------------------------------------------------------------

def _write_progress(base: Path, name: str, stage: str, done: int, total: int,
                    elapsed: float, eta: float) -> None:
    pct = done * 100.0 / total if total else 0.0
    payload = {"attacker": name, "stage": stage, "done": done, "total": total,
               "pct": round(pct, 2), "elapsed_min": round(elapsed / 60, 1),
               "eta_min": round(max(eta, 0) / 60, 1)}
    try:
        (base / "attack_progress.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError:
        pass


def _save_checkpoint(path: Path, meta: dict, members, nonmembers,
                     done: int, total: int, elapsed: float) -> None:
    payload = {"meta": meta, "members": members, "nonmembers": nonmembers,
               "done_batches": done, "total_batches": total, "elapsed_sec": elapsed}
    buf = io.BytesIO()
    torch.save(payload, buf, _use_new_zipfile_serialization=False)
    path.write_bytes(buf.getvalue())


def _load_checkpoint(path: Path, meta: dict) -> Optional[Dict]:
    if not path.exists():
        return None
    with path.open("rb") as f:
        state = torch.load(f, map_location="cpu")
    for k, v in meta.items():
        if state.get("meta", {}).get(k) != v:
            raise ValueError(f"checkpoint meta mismatch at key {k!r}")
    return state


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(
    attacker_name: str = "ReDiffuse",
    dataset: str = "laion5",
    checkpoint: str = "CompVis/stable-diffusion-v1-4",
    # --- Paper Appendix A exact settings for Stable Diffusion ---
    attack_num: int = 1,
    interval: int = 10,   # variation API diffusion step  t = 10
    k: int = 10,          # DDIM sampling interval
    average: int = 10,    # n independent reconstructions (n=10)
    # ------------------------------------------------------------
    seed: int = 0,
    batch_size: int = 4,
    result_csv: str = "result.csv",
    score_mode: str = "first",
    rediffuse_scorer: str = "original_ssim",
    scores_npz: Optional[str] = None,
    decode_chunk_size: int = 4,
    torch_dtype: str = "auto",
    resume: bool = True,
    checkpoint_every: int = 1,
    progress_every: int = 25,
    max_batches: Optional[int] = None,
    start_batch: int = 0,
):
    seed_everything(seed)

    logging.getLogger().handlers.clear()
    logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])
    logger = logging.getLogger(__name__)

    dtype = resolve_torch_dtype(torch_dtype)
    logger.info("device: %s", DEVICE)
    logger.info("loading model: %s (dtype=%s)", checkpoint, dtype)
    model = MyStableDiffusionPipeline.from_pretrained(checkpoint, torch_dtype=dtype).to(DEVICE)

    # --- attacker wrapper: saves original pixel images BEFORE VAE encoding ---
    def _wrap(attack):
        def _call(x, condition=None):
            orig_pil = pixel_tensor_to_float_arrays(x) if attacker_name == "ReDiffuse" else None
            x = model.prepare_latent(x)
            if condition is not None:
                # No CFG (guidance_scale=1.0) → only conditional embeddings, no uncond duplicate
                condition_enc = model.encode_input_prompt(condition, do_classifier_free_guidance=False)
            else:
                condition_enc = None
            return attack(x, condition_enc), orig_pil
        return _call

    logger.info("loading dataset: %s", dataset)
    _, _, train_loader, test_loader = load_member_data(dataset_name=dataset, batch_size=batch_size)

    betas = _make_betas().to(DEVICE)
    attacker_inner = ATTACKERS[attacker_name](betas, interval, average, attack_num, k, EpsGetter(model), None)
    attacker = _wrap(attacker_inner)

    # --- checkpoint / chunking ---
    full_total_batches = len(test_loader)
    chunk_start = max(0, int(start_batch))
    total_batches = full_total_batches
    if max_batches is not None:
        total_batches = min(total_batches, chunk_start + int(max_batches))
    partial_run = total_batches < full_total_batches or chunk_start > 0

    result_dir = Path(result_csv).resolve().parent
    ckpt_root  = result_dir.parent / "_checkpoint_cache" / result_dir.name
    ckpt_path  = ckpt_root / "attack_state.bin"
    ckpt_path.parent.mkdir(parents=True, exist_ok=True)
    ckpt_meta  = {"attacker_name": attacker_name, "dataset": dataset,
                  "checkpoint": checkpoint, "attack_num": attack_num,
                  "interval": interval, "k": k, "average": average,
                  "batch_size": batch_size, "seed": seed,
                  "score_mode": score_mode, "rediffuse_scorer": rediffuse_scorer,
                  "torch_dtype": str(dtype),
                  "scoring_version": 2}

    members, nonmembers = [], []
    resumed_batches, elapsed_offset = chunk_start, 0.0
    if resume and chunk_start == 0 and max_batches is None:
        try:
            state = _load_checkpoint(ckpt_path, ckpt_meta)
            if state is not None:
                members  = state["members"]
                nonmembers = state["nonmembers"]
                resumed_batches = min(state["done_batches"], total_batches)
                elapsed_offset  = state["elapsed_sec"]
                logger.info("resumed from checkpoint: batch %d/%d", resumed_batches, total_batches)
        except Exception as exc:
            logger.warning("ignoring stale checkpoint: %s", exc)

    _write_progress(result_dir, attacker_name, "running",
                    resumed_batches, total_batches, elapsed_offset,
                    elapsed_offset / max(resumed_batches, 1) * max(total_batches - resumed_batches, 0))

    t0 = time.perf_counter()
    with torch.no_grad():
        for batch_idx, (member, nonmember) in enumerate(
            track(zip(train_loader, chain(*([test_loader]))), total=total_batches)
        ):
            if batch_idx >= total_batches:
                break
            if batch_idx < resumed_batches:
                continue

            mem_cond, non_cond = member[1], nonmember[1]
            mem_x = member[0].to(DEVICE)
            non_x = nonmember[0].to(DEVICE)

            (rev_m, den_m), orig_m = attacker(mem_x, mem_cond)
            (rev_n, den_n), orig_n = attacker(non_x, non_cond)

            if attacker_name == "ReDiffuse":
                members.append(
                    rediffuse_step_features(
                        model, orig_m, rev_m, den_m,
                        scorer=rediffuse_scorer,
                        decode_chunk_size=decode_chunk_size,
                    )
                )
                nonmembers.append(
                    rediffuse_step_features(
                        model, orig_n, rev_n, den_n,
                        scorer=rediffuse_scorer,
                        decode_chunk_size=decode_chunk_size,
                    )
                )
            elif False:
                # den_m shape: [attack_num=1, n=10, B, C, H, W]  (6D)
                # den_m[0]   shape: [n=10, B, C, H, W]            (5D)
                #   → contains all 10 variations, NOT cut to 1
                # decode_reconstruction_images_float averages 10 reconstructions
                # in float32 pixel space (no uint8 rounding loss)
                assert den_m.ndim == 6 and den_m.shape[1] == average, (
                    f"expected den_m shape (1, {average}, B, C, H, W), got {tuple(den_m.shape)}"
                )
                recon_m = decode_reconstruction_images_float(model, den_m[0])
                recon_n = decode_reconstruction_images_float(model, den_n[0])
                for i in range(len(orig_m)):
                    members.append(calculate_ssim(orig_m[i], recon_m[i]))
                    nonmembers.append(calculate_ssim(orig_n[i], recon_n[i]))
            else:
                members.append(((rev_m - den_m).abs() ** 2).flatten(2).sum(dim=-1))
                nonmembers.append(((rev_n - den_n).abs() ** 2).flatten(2).sum(dim=-1))
                members    = [torch.cat(members, dim=0)]
                nonmembers = [torch.cat(nonmembers, dim=0)]

            done = batch_idx + 1
            elapsed = elapsed_offset + (time.perf_counter() - t0)
            eta = elapsed / done * max(total_batches - done, 0)
            _write_progress(result_dir, attacker_name, "running", done, total_batches, elapsed, eta)

            if checkpoint_every and (done % checkpoint_every == 0 or done == total_batches):
                _save_checkpoint(ckpt_path, ckpt_meta, members, nonmembers, done, total_batches, elapsed)
            if progress_every and (done % progress_every == 0 or done == total_batches):
                logger.info("batch %d/%d  (%.0f%%)  elapsed %.1f min  eta %.1f min",
                            done, total_batches, done * 100.0 / total_batches,
                            elapsed / 60, eta / 60)

    # --- compute metrics ---
    if attacker_name == "ReDiffuse":
        mem_features = np.concatenate(members, axis=0).astype(np.float32)
        non_features = np.concatenate(nonmembers, axis=0).astype(np.float32)
        mem_similarity = aggregate_rediffuse_features(mem_features, score_mode)
        non_similarity = aggregate_rediffuse_features(non_features, score_mode)

        # High SSIM means member; negate so low score = member for thresholding.
        mem_t = torch.from_numpy((-mem_similarity).astype(np.float32))
        non_t = torch.from_numpy((-non_similarity).astype(np.float32))
    elif False:
        # High SSIM → member; negate so that low score = member (consistent with ROC threshold)
        mem_t  = torch.tensor(members)  * -1
        non_t  = torch.tensor(nonmembers) * -1
    else:
        mem_t  = members[0]
        non_t  = nonmembers[0]

    total_elapsed = elapsed_offset + (time.perf_counter() - t0)
    if partial_run:
        if attacker_name == "ReDiffuse" and scores_npz:
            mem_features = np.concatenate(members, axis=0).astype(np.float32)
            non_features = np.concatenate(nonmembers, axis=0).astype(np.float32)
            buf = io.BytesIO()
            np.savez_compressed(
                buf,
                member_features=mem_features,
                nonmember_features=non_features,
                steps=np.arange(1, mem_features.shape[1] + 1, dtype=np.int32) * int(interval),
                dataset=np.asarray(dataset),
                attacker_name=np.asarray(attacker_name),
                checkpoint=np.asarray(checkpoint),
                attack_num=np.asarray(attack_num),
                interval=np.asarray(interval),
                k=np.asarray(k),
                average=np.asarray(average),
                score_mode=np.asarray(score_mode),
                rediffuse_scorer=np.asarray(rediffuse_scorer),
                torch_dtype=np.asarray(str(dtype)),
                chunk_start=np.asarray(chunk_start),
                chunk_end=np.asarray(total_batches),
                total_batches=np.asarray(full_total_batches),
            )
            print(base64.b64encode(buf.getvalue()).decode("ascii"))
        _write_progress(result_dir, attacker_name, "paused",
                        total_batches, full_total_batches, total_elapsed,
                        total_elapsed / max(total_batches, 1) * max(full_total_batches - total_batches, 0))
        logger.info("partial run finished at batch %d/%d; checkpoint kept at %s",
                    total_batches, full_total_batches, ckpt_path)
        return

    _write_progress(result_dir, attacker_name, "completed", total_batches, total_batches, total_elapsed, 0)

    auc, asr, fpr_arr, tpr_arr, best_thr = roc(mem_t, non_t, n_points=2000)
    asr = float(asr)
    tp_at_1fpr = tpr_arr[(fpr_arr - 0.01).abs().argmin()].item()
    thr_val    = best_thr.item() if hasattr(best_thr, "item") else float(best_thr)

    if scores_npz and attacker_name == "ReDiffuse":
        npz_path = Path(scores_npz)
        if not npz_path.is_absolute():
            npz_path = result_dir / npz_path
        npz_path.parent.mkdir(parents=True, exist_ok=True)
        buf = io.BytesIO()
        np.savez_compressed(
            buf,
            member_features=mem_features,
            nonmember_features=non_features,
            member_scores=mem_t.numpy(),
            nonmember_scores=non_t.numpy(),
            steps=np.arange(1, mem_features.shape[1] + 1, dtype=np.int32) * int(interval),
            dataset=np.asarray(dataset),
            attacker_name=np.asarray(attacker_name),
            checkpoint=np.asarray(checkpoint),
            attack_num=np.asarray(attack_num),
            interval=np.asarray(interval),
            k=np.asarray(k),
            average=np.asarray(average),
            score_mode=np.asarray(score_mode),
            rediffuse_scorer=np.asarray(rediffuse_scorer),
            torch_dtype=np.asarray(str(dtype)),
            auc=np.asarray(auc),
            asr=np.asarray(asr),
            tpr_1fpr=np.asarray(tp_at_1fpr),
            threshold=np.asarray(thr_val),
        )
        npz_path.write_bytes(buf.getvalue())
        print(f"Scores NPZ:    {npz_path}")

    print(f"AUC:          {auc:.4f}")
    print(f"ASR:          {asr:.4f}")
    print(f"TPR @ 1% FPR: {tp_at_1fpr:.4f}")
    print(f"Threshold:    {thr_val:.6f}")

    with open(result_csv, "a", encoding="utf-8") as f:
        f.write(f"{dataset},{attacker_name},{attack_num},{interval},{k},{average},"
                f"{auc:.4f},{asr:.4f},{tp_at_1fpr:.4f},{thr_val:.6f},{score_mode},{rediffuse_scorer}\n")

    if ckpt_path.exists():
        ckpt_path.unlink()


if __name__ == "__main__":
    fire.Fire(main)
