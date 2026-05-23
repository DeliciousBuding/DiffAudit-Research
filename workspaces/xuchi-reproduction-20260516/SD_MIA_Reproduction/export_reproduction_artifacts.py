"""
Export paper-style Stable Diffusion MIA reproduction artifacts.

Inputs:
  - a saved ReDiffuse scores NPZ with member_features/nonmember_features
  - a detector JSON exported by sweep_rediffuse_features.py

Outputs:
  - result.csv with image_path, label, score, prediction
  - metrics.json / metrics.csv with AUC, ASR, TPR@FPR=1%
  - roc_curve.csv and ROC plot

The exported `score` column is high-is-member membership confidence.  The
`low_score` column is kept for compatibility with existing detector JSON files,
where the decision rule is member_if_score_leq_threshold.
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from omegaconf import OmegaConf
from pycocotools.coco import COCO
from sklearn import metrics


def np_load_pickle_compat(path: Path):
    added = []
    if not hasattr(np, "_core"):
        aliases = {
            "numpy._core": np.core,
            "numpy._core.multiarray": np.core.multiarray,
            "numpy._core.numeric": np.core.numeric,
        }
        for name, module in aliases.items():
            if name not in sys.modules:
                sys.modules[name] = module
                added.append(name)
    try:
        return np.load(path, allow_pickle=True)
    finally:
        for name in added:
            sys.modules.pop(name, None)


def read_caption_map(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    frame = pd.read_csv(path)
    if "file_name" not in frame.columns:
        return {}
    text_col = "text" if "text" in frame.columns else frame.columns[0]
    return {str(row.file_name): str(getattr(row, text_col)) for row in frame.itertuples(index=False)}


def load_member_rows(data_dir: Path, n: int) -> List[Dict[str, str]]:
    metadata = np_load_pickle_compat(data_dir / "val-list-2500-random.npy")
    caption_map = read_caption_map(data_dir / "text_generation" / "images-random.csv")
    rows = []
    for idx in range(n):
        stem = str(metadata[idx][0])
        file_name = f"{stem}.jpg"
        rows.append(
            {
                "sample_index": idx,
                "image_path": str(data_dir / "images-random" / file_name),
                "file_name": file_name,
                "label": 1,
                "label_name": "member",
                "source": "LAION-5B member subset",
                "caption": caption_map.get(file_name, str(metadata[idx][1]) if len(metadata[idx]) > 1 else ""),
            }
        )
    return rows


def load_nonmember_rows(coco_img_dir: Path, coco_ann_file: Path, split_yaml: Path, data_dir: Path, n: int) -> List[Dict[str, str]]:
    coco = COCO(str(coco_ann_file))
    ids = list(sorted(coco.imgs.keys()))
    split = list(OmegaConf.load(split_yaml))
    caption_map = read_caption_map(data_dir / "text_generation" / "val2017.csv")
    rows = []
    for idx in range(n):
        coco_index = int(split[idx])
        image_info = coco.loadImgs(ids[coco_index])[0]
        file_name = str(image_info["file_name"])
        captions = coco.imgToAnns.get(int(image_info["id"]), [])
        rows.append(
            {
                "sample_index": idx,
                "image_path": str(coco_img_dir / file_name),
                "file_name": file_name,
                "label": 0,
                "label_name": "nonmember",
                "source": "COCO2017-val non-member subset",
                "caption": caption_map.get(file_name, captions[0]["caption"] if captions else ""),
            }
        )
    return rows


def detector_confidence(features: np.ndarray, detector: Dict) -> np.ndarray:
    mode = str(detector.get("feature_mode", "first"))
    if mode.startswith("logistic_l2"):
        payload = detector.get("logistic") or {}
        coef = np.asarray(payload["coef"], dtype=np.float64)
        intercept = float(payload["intercept"])
        mean = np.asarray(payload["scaler_mean"], dtype=np.float64)
        scale = np.asarray(payload["scaler_scale"], dtype=np.float64)
        return ((features - mean) / scale).dot(coef) + intercept

    if mode.startswith("linear_angle") or detector.get("linear_weights"):
        weights = detector.get("linear_weights") or {}
        a = weights.get("step0")
        b = weights.get("step1")
        if a is not None and b is not None:
            return float(a) * features[:, 0] + float(b) * features[:, 1]

    if mode in ("first", "step0"):
        return features[:, 0]
    if mode == "last":
        return features[:, -1]
    if mode == "mean":
        return features.mean(axis=1)
    if mode == "median":
        return np.median(features, axis=1)
    if mode == "max":
        return features.max(axis=1)
    if mode == "min":
        return features.min(axis=1)
    if mode.startswith("step"):
        return features[:, int(mode[4:])]
    raise ValueError(f"unsupported detector feature_mode: {mode}")


def compute_metrics(y_true: np.ndarray, confidence: np.ndarray) -> Tuple[Dict[str, float], np.ndarray, np.ndarray]:
    auc = float(metrics.roc_auc_score(y_true, confidence))
    fpr, tpr, _ = metrics.roc_curve(y_true, confidence)
    tpr_1fpr = float(tpr[np.argmin(np.abs(fpr - 0.01))])

    thresholds = np.unique(confidence)
    best_asr = -1.0
    best_thr = float(thresholds[0])
    for thr in thresholds:
        pred = confidence >= thr
        asr = float((pred == y_true.astype(bool)).mean())
        if asr > best_asr:
            best_asr = asr
            best_thr = float(thr)

    return (
        {
            "auc": auc,
            "asr": best_asr,
            "tpr_at_fpr_1pct": tpr_1fpr,
            "threshold_confidence": best_thr,
            "threshold_low_score": -best_thr,
        },
        fpr,
        tpr,
    )


def write_roc_plot(path: Path, fpr: np.ndarray, tpr: np.ndarray, auc: float) -> Path:
    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 5), dpi=160)
        ax.plot(fpr, tpr, label=f"ROC AUC = {auc:.4f}", color="#1f77b4", linewidth=2)
        ax.plot([0, 1], [0, 1], linestyle="--", color="#888888", linewidth=1)
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.set_title("Stable Diffusion MIA ROC")
        ax.grid(True, alpha=0.25)
        ax.legend(loc="lower right")
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
        return path
    except Exception:
        svg_path = path.with_suffix(".svg")
        points = []
        width, height, pad = 640, 480, 48
        for x, y in zip(fpr, tpr):
            px = pad + float(x) * (width - 2 * pad)
            py = height - pad - float(y) * (height - 2 * pad)
            points.append(f"{px:.2f},{py:.2f}")
        diagonal = f"{pad},{height-pad} {width-pad},{pad}"
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white"/>
<text x="{pad}" y="28" font-family="Arial" font-size="18">Stable Diffusion MIA ROC, AUC={auc:.4f}</text>
<polyline points="{diagonal}" fill="none" stroke="#888" stroke-dasharray="6,6" stroke-width="1"/>
<polyline points="{' '.join(points)}" fill="none" stroke="#1f77b4" stroke-width="2"/>
<text x="{width/2-50}" y="{height-10}" font-family="Arial" font-size="14">False Positive Rate</text>
<text x="8" y="{height/2}" font-family="Arial" font-size="14" transform="rotate(-90 16,{height/2})">True Positive Rate</text>
</svg>
"""
        svg_path.write_text(svg, encoding="utf-8")
        return svg_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Stable Diffusion MIA reproduction artifacts.")
    parser.add_argument("--scores-npz", required=True)
    parser.add_argument("--detector-json", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--data-dir", default=r"E:\stable_diffusion\coco_data\stable_diffusion_data")
    parser.add_argument("--coco-img-dir", default=r"E:\stable_diffusion\coco_data\coco_data\val2017")
    parser.add_argument("--coco-ann-file", default=r"E:\stable_diffusion\coco_data\coco_data\annotations\captions_val2017.json")
    parser.add_argument("--coco-split-yaml", default=r"E:\stable_diffusion\coco_data\SD_MIA_Reproduction\coco-2500-random.yaml")
    args = parser.parse_args()

    scores = np.load(args.scores_npz, allow_pickle=True)
    detector = json.loads(Path(args.detector_json).read_text(encoding="utf-8"))
    member_features = scores["member_features"].astype(np.float64)
    nonmember_features = scores["nonmember_features"].astype(np.float64)
    if member_features.shape != nonmember_features.shape:
        raise SystemExit(f"member/nonmember shape mismatch: {member_features.shape} vs {nonmember_features.shape}")

    member_conf = detector_confidence(member_features, detector)
    nonmember_conf = detector_confidence(nonmember_features, detector)
    confidence = np.concatenate([member_conf, nonmember_conf])
    y_true = np.concatenate([np.ones(len(member_conf), dtype=np.int32), np.zeros(len(nonmember_conf), dtype=np.int32)])
    metrics_payload, fpr, tpr = compute_metrics(y_true, confidence)
    threshold_conf = metrics_payload["threshold_confidence"]

    data_dir = Path(args.data_dir)
    rows = load_member_rows(data_dir, len(member_conf))
    rows.extend(
        load_nonmember_rows(
            Path(args.coco_img_dir),
            Path(args.coco_ann_file),
            Path(args.coco_split_yaml),
            data_dir,
            len(nonmember_conf),
        )
    )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    result_csv = out_dir / "result.csv"
    fields = [
        "global_index",
        "sample_index",
        "image_path",
        "file_name",
        "label",
        "label_name",
        "source",
        "caption",
        "score",
        "low_score",
        "threshold",
        "prediction",
        "prediction_name",
        "correct",
    ]
    with result_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for idx, (row, score, label) in enumerate(zip(rows, confidence, y_true)):
            pred = int(score >= threshold_conf)
            writer.writerow(
                {
                    **row,
                    "global_index": idx,
                    "score": float(score),
                    "low_score": float(-score),
                    "threshold": float(threshold_conf),
                    "prediction": pred,
                    "prediction_name": "member" if pred else "nonmember",
                    "correct": int(pred == int(label)),
                }
            )

    roc_csv = out_dir / "roc_curve.csv"
    with roc_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["fpr", "tpr"])
        writer.writeheader()
        writer.writerows({"fpr": float(x), "tpr": float(y)} for x, y in zip(fpr, tpr))

    roc_plot = write_roc_plot(out_dir / "roc_curve.png", fpr, tpr, metrics_payload["auc"])
    metrics_payload.update(
        {
            "dataset": detector.get("dataset", "laion5_blip"),
            "attacker_name": detector.get("attacker_name", "ReDiffuse"),
            "checkpoint": detector.get("checkpoint", "CompVis/stable-diffusion-v1-4"),
            "feature_mode": detector.get("feature_mode"),
            "rediffuse_scorer": detector.get("rediffuse_scorer"),
            "num_member": int(len(member_conf)),
            "num_nonmember": int(len(nonmember_conf)),
            "result_csv": str(result_csv),
            "roc_curve_csv": str(roc_csv),
            "roc_curve_plot": str(roc_plot),
            "score_direction": "higher score means more likely member",
            "prediction_rule": "member_if_score_geq_threshold",
            "detector_json": str(Path(args.detector_json)),
            "scores_npz": str(Path(args.scores_npz)),
        }
    )
    (out_dir / "metrics.json").write_text(json.dumps(metrics_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with (out_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(metrics_payload.keys()))
        writer.writeheader()
        writer.writerow(metrics_payload)

    print(f"[ok] wrote result csv: {result_csv}")
    print(f"[ok] wrote metrics: {out_dir / 'metrics.json'}")
    print(f"[ok] wrote ROC plot: {roc_plot}")
    print(
        f"[metrics] AUC={metrics_payload['auc']:.4f} "
        f"ASR={metrics_payload['asr']:.4f} "
        f"TPR@1%FPR={metrics_payload['tpr_at_fpr_1pct']:.4f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
