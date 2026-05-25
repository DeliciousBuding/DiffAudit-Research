from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[3]
PAPER = Path(__file__).resolve().parents[1]
DATA = PAPER / "data"
FIGURES = PAPER / "figures"


def read_json(path: str) -> dict:
    with (ROOT / path).open("r", encoding="utf-8") as f:
        return json.load(f)


def metric_row(source: str, label: str, role: str, metrics: dict) -> dict:
    return {
        "source": source,
        "label": label,
        "role": role,
        "auc": metrics["auc"],
        "asr": metrics["asr"],
        "tpr_at_1pct_fpr": metrics["tpr_at_1pct_fpr"],
        "tpr_at_0_1pct_fpr": metrics["tpr_at_0_1pct_fpr"],
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_admitted_rows() -> list[dict]:
    bundle = read_json("workspaces/implementation/artifacts/admitted-evidence-bundle.json")
    rows = []
    for item in bundle["rows"]:
        rows.append(
            {
                "label": f"{item['track']}: {item['method']['attack']} / {item['method']['defense']}",
                "track": item["track"],
                "attack": item["method"]["attack"],
                "defense": item["method"]["defense"],
                "model": item["method"]["model"],
                "auc": item["metrics"]["auc"],
                "asr": item["metrics"]["asr"],
                "tpr_at_1pct_fpr": item["metrics"]["tpr_at_1pct_fpr"],
                "tpr_at_0_1pct_fpr": item["metrics"]["tpr_at_0_1pct_fpr"],
                "evidence_level": item["evidence_level"],
                "quality_cost": item["quality_cost"],
            }
        )
    return rows


def build_h2_rows() -> list[dict]:
    main = read_json("workspaces/black-box/artifacts/h2-output-cloud-geometry-20260525.json")
    shuffle = read_json("workspaces/black-box/artifacts/h2-output-cloud-geometry-label-shuffle-20260525.json")
    shared = read_json("workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-256-20260525.json")
    shared_shuffle = read_json(
        "workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-256-label-shuffle-20260525.json"
    )
    seed177 = read_json(
        "workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-seed177-256-20260525.json"
    )
    seed177_shuffle = read_json(
        "workspaces/black-box/artifacts/h2-output-cloud-geometry-shared-position-seed177-256-label-shuffle-20260525.json"
    )
    transfer = read_json("workspaces/black-box/artifacts/h2-output-cloud-transfer-shared-position-256-20260525.json")
    img2img = read_json("workspaces/black-box/artifacts/h2-img2img-output-cloud-portability-20260525.json")

    rows = [
        metric_row("h2-main", "output-cloud 512/512", "candidate", main["logistic"]["aggregate_metrics"]),
        metric_row("h2-main", "raw H2 logistic", "baseline", main["comparison"]["raw_h2_logistic"]),
        metric_row("h2-main", "lowpass H2 logistic", "baseline", main["comparison"]["lowpass_h2_logistic"]),
        metric_row("h2-main", "label shuffle", "sanity", shuffle["logistic"]["aggregate_metrics"]),
        metric_row("h2-control", "shared-position seed 176", "control", shared["logistic"]["aggregate_metrics"]),
        metric_row("h2-control", "shared-position label shuffle", "sanity", shared_shuffle["logistic"]["aggregate_metrics"]),
        metric_row("h2-control", "shared-position seed 177", "stability", seed177["logistic"]["aggregate_metrics"]),
        metric_row("h2-control", "seed 177 label shuffle", "sanity", seed177_shuffle["logistic"]["aggregate_metrics"]),
    ]
    for item in transfer["primary_transfer"]:
        rows.append(metric_row("h2-transfer", f"{item['source']} to {item['target']}", "transfer", item["aggregate_metrics"]))
    for packet in img2img["packets"]:
        rows.append(metric_row("h2-img2img", packet["name"], "portability", packet["logistic"]["aggregate_metrics"]))
    return rows


def build_negative_rows() -> list[dict]:
    rediffuse = {
        "auc": 0.4996337890625,
        "asr": 0.509765625,
        "tpr_at_1pct_fpr": 0.01171875,
        "tpr_at_0_1pct_fpr": 0.0,
    }
    rediffuse_norm = {
        "auc": 0.5052947998046875,
        "asr": 0.525390625,
        "tpr_at_1pct_fpr": 0.03125,
        "tpr_at_0_1pct_fpr": 0.01953125,
    }
    commoncanvas = read_json("workspaces/black-box/artifacts/commoncanvas-denoising-loss-20260513.json")["metric"]
    tracing = read_json("workspaces/gray-box/artifacts/tracing-roots-feature-packet-mia-20260515.json")["eval"]
    return [
        metric_row("rediffuse-stl10", "denoising-loss scout", "negative", rediffuse),
        metric_row("rediffuse-stl10", "score-norm scout", "negative", rediffuse_norm),
        metric_row("commoncanvas", "conditional denoising loss", "negative", commoncanvas),
        {
            "source": "tracing-roots",
            "label": "feature-packet replay",
            "role": "support",
            "auc": tracing["auc"],
            "asr": tracing["accuracy"],
            "tpr_at_1pct_fpr": tracing["tpr_at_1pct_fpr"],
            "tpr_at_0_1pct_fpr": tracing["tpr_at_0_1pct_fpr"],
        },
    ]


def plot_metric_bars(rows: list[dict], path: Path, title: str) -> None:
    labels = [row.get("label", row.get("attack", "row")) for row in rows]
    auc = [float(row["auc"]) for row in rows]
    tpr = [float(row["tpr_at_1pct_fpr"]) for row in rows]

    fig, ax = plt.subplots(figsize=(max(7, len(rows) * 0.9), 4.5))
    x = range(len(rows))
    width = 0.38
    ax.bar([i - width / 2 for i in x], auc, width, label="AUC", color="#3b6ea8")
    ax.bar([i + width / 2 for i in x], tpr, width, label="TPR@1%FPR", color="#d08b32")
    ax.axhline(0.5, color="#666666", linewidth=0.8, linestyle="--", label="random AUC")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("metric value")
    ax.set_title(title)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.legend(frameon=False, ncol=3)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    admitted = build_admitted_rows()
    h2 = build_h2_rows()
    negative = build_negative_rows()

    write_csv(DATA / "admitted_rows.csv", admitted)
    write_csv(DATA / "h2_output_cloud_rows.csv", h2)
    write_csv(DATA / "negative_support_rows.csv", negative)

    plot_metric_bars(admitted, FIGURES / "admitted_rows_metrics.pdf", "Admitted evidence bundle")
    h2_plot_rows = [row for row in h2 if row["role"] in {"candidate", "baseline", "sanity", "control", "stability", "transfer"}]
    plot_metric_bars(h2_plot_rows, FIGURES / "h2_output_cloud_controls.pdf", "H2 output-cloud geometry controls")
    plot_metric_bars(negative, FIGURES / "negative_and_support_rows.pdf", "Negative and support evidence")

    manifest = {
        "generated": [
            "data/admitted_rows.csv",
            "data/h2_output_cloud_rows.csv",
            "data/negative_support_rows.csv",
            "figures/admitted_rows_metrics.pdf",
            "figures/h2_output_cloud_controls.pdf",
            "figures/negative_and_support_rows.pdf",
        ],
        "source_policy": "All numbers are read from existing DiffAudit Research JSON artifacts or frozen evidence notes.",
    }
    (PAPER / "asset_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
