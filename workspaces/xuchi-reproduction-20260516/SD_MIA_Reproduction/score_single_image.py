"""
Score one image with the saved Stable Diffusion MIA detector.

This command is intentionally separate from the dataset evaluation path. It
loads Stable Diffusion v1-4, runs the ReDiffuse reconstruction feature plan for
one input image, then applies a detector JSON produced by the offline sweep.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from attack import (
    ATTACKERS,
    DEVICE,
    EpsGetter,
    MyStableDiffusionPipeline,
    _make_betas,
    pixel_tensor_to_float_arrays,
    rediffuse_step_features,
    resolve_torch_dtype,
)


def preprocess_image(path: Path) -> torch.Tensor:
    transform = transforms.Compose(
        [
            transforms.Resize(512, interpolation=transforms.InterpolationMode.BILINEAR),
            transforms.CenterCrop(512),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5]),
        ]
    )
    return transform(Image.open(path).convert("RGB")).unsqueeze(0).to(DEVICE)


def compute_rediffuse_features(
    model: MyStableDiffusionPipeline,
    image: torch.Tensor,
    prompt: str,
    attack_num: int,
    average: int,
    interval: int = 10,
    k: int = 10,
    scorer: str = "vae_ssim",
) -> np.ndarray:
    betas = _make_betas().to(DEVICE)
    attacker = ATTACKERS["ReDiffuse"](
        betas,
        interval,
        average,
        attack_num,
        k,
        EpsGetter(model),
        None,
    )
    original = pixel_tensor_to_float_arrays(image)
    latents = model.prepare_latent(image)
    prompt_embeds = model.encode_input_prompt([prompt], do_classifier_free_guidance=False)
    reverse, denoise = attacker(latents, prompt_embeds)
    return rediffuse_step_features(model, original, reverse, denoise, scorer=scorer)


def feature_plan(name: str) -> List[Tuple[str, int, int]]:
    if name == "a2_avg3":
        return [("a2avg3", 2, 3)]
    if name == "a5_avg3":
        return [("a5avg3", 5, 3)]
    if name == "a2_a5_combined":
        return [("a2avg3", 2, 3), ("a5avg3", 5, 3)]
    raise ValueError("feature_plan must be a2_avg3, a5_avg3, or a2_a5_combined")


def detector_confidence(features: np.ndarray, detector: Dict) -> float:
    mode = str(detector.get("feature_mode", "first"))
    if mode.startswith("logistic_l2"):
        payload = detector.get("logistic") or {}
        coef = np.asarray(payload["coef"], dtype=np.float64)
        intercept = float(payload["intercept"])
        mean = np.asarray(payload["scaler_mean"], dtype=np.float64)
        scale = np.asarray(payload["scaler_scale"], dtype=np.float64)
        return float(((features - mean) / scale).dot(coef) + intercept)

    weights = detector.get("linear_weights") or {}
    a = weights.get("step0")
    b = weights.get("step1")
    if a is not None and b is not None:
        return float(float(a) * features[0] + float(b) * features[1])

    if mode in ("first", "step0"):
        return float(features[0])
    if mode == "last":
        return float(features[-1])
    if mode == "mean":
        return float(features.mean())
    if mode == "median":
        return float(np.median(features))
    if mode == "max":
        return float(features.max())
    if mode == "min":
        return float(features.min())
    if mode.startswith("step"):
        return float(features[int(mode[4:])])
    raise ValueError(f"unsupported detector feature_mode: {mode}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Score one image with the Stable Diffusion MIA detector.")
    parser.add_argument("--image", required=True, help="Input image path.")
    parser.add_argument("--prompt", required=True, help="Caption/prompt. Use BLIP caption for laion5_blip reproduction.")
    parser.add_argument("--detector-json", required=True)
    parser.add_argument("--feature-plan", default="a2_a5_combined", choices=["a2_avg3", "a5_avg3", "a2_a5_combined"])
    parser.add_argument("--checkpoint", default="CompVis/stable-diffusion-v1-4")
    parser.add_argument("--torch-dtype", default="auto", choices=["auto", "float16", "float32"])
    parser.add_argument("--output-json", default="")
    args = parser.parse_args()

    detector = json.loads(Path(args.detector_json).read_text(encoding="utf-8"))
    dtype = resolve_torch_dtype(args.torch_dtype)
    model = MyStableDiffusionPipeline.from_pretrained(args.checkpoint, torch_dtype=dtype).to(DEVICE)
    image = preprocess_image(Path(args.image))

    features = []
    feature_names = []
    with torch.no_grad():
        for prefix, attack_num, average in feature_plan(args.feature_plan):
            part = compute_rediffuse_features(
                model,
                image,
                args.prompt,
                attack_num=attack_num,
                average=average,
                interval=10,
                k=10,
                scorer="vae_ssim",
            )[0]
            features.extend(part.tolist())
            feature_names.extend(f"{prefix}_step{i}" for i in range(len(part)))

    feature_array = np.asarray(features, dtype=np.float64)
    confidence = detector_confidence(feature_array, detector)
    low_score = -confidence
    threshold_low = float(detector["threshold"])
    threshold_conf = -threshold_low
    is_member = bool(confidence >= threshold_conf)
    payload = {
        "image_path": str(Path(args.image)),
        "prompt": args.prompt,
        "score": confidence,
        "low_score": low_score,
        "threshold": threshold_conf,
        "threshold_low_score": threshold_low,
        "prediction": int(is_member),
        "prediction_name": "member" if is_member else "nonmember",
        "rule": "member_if_score_geq_threshold",
        "feature_plan": args.feature_plan,
        "feature_names": feature_names,
        "features": feature_array.tolist(),
        "detector_json": str(Path(args.detector_json)),
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output_json:
        Path(args.output_json).write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
