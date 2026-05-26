from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[3]
PAPER = Path(__file__).resolve().parents[1]
DATA = PAPER / "data"
FIGURES = PAPER / "figures"

GATE_COLUMNS = [
    ("target_gate", "Target"),
    ("split_gate", "Split"),
    ("evidence_gate", "Evidence"),
    ("metric_gate", "Metric"),
    ("boundary_gate", "Boundary"),
    ("delta_gate", "Surface delta"),
]
GATE_PLOT_LABELS = {
    "Target": "Target",
    "Split": "Split",
    "Evidence": "Rows",
    "Metric": "Metric",
    "Boundary": "Boundary",
    "Surface delta": "Delta",
}
GATE_OUTCOMES = ["Pass", "Partial", "Fail"]
PDF_METADATA = {
    "Creator": "DiffAudit build_paper_assets.py",
    "CreationDate": datetime(2026, 5, 26, tzinfo=timezone.utc),
    "ModDate": datetime(2026, 5, 26, tzinfo=timezone.utc),
}


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


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


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


def build_artifact_gate_summaries() -> tuple[list[dict], list[dict]]:
    corpora = [
        ("v1 evidence-note corpus", DATA / "artifact_corpus_v1.csv"),
        ("fixed-search batch", DATA / "artifact_corpus_fixed_search_20260526.csv"),
    ]
    gate_rows: list[dict] = []
    strata_rows: list[dict] = []

    for corpus, path in corpora:
        rows = read_csv(path)
        for gate_col, gate_label in GATE_COLUMNS:
            counts = {outcome: 0 for outcome in GATE_OUTCOMES}
            for row in rows:
                outcome = row.get(gate_col, "").strip()
                if outcome not in counts:
                    counts[outcome] = 0
                counts[outcome] += 1
            for outcome in GATE_OUTCOMES:
                gate_rows.append(
                    {
                        "corpus": corpus,
                        "gate": gate_label,
                        "outcome": outcome,
                        "count": counts[outcome],
                    }
                )

        group_col = "stratum" if "stratum" in rows[0] else "inclusion_decision"
        group_counts: dict[str, int] = {}
        for row in rows:
            group = row[group_col].strip()
            group_counts[group] = group_counts.get(group, 0) + 1
        for group, count in sorted(group_counts.items()):
            strata_rows.append(
                {
                    "corpus": corpus,
                    "group_type": group_col,
                    "group": group,
                    "count": count,
                }
            )

    return gate_rows, strata_rows


def metric_plot_label(row: dict) -> str:
    label = row.get("label", row.get("attack", "row"))
    source = row.get("source", "")

    admitted_labels = {
        "black-box: recon DDIM public-100 step30 / none": "black-box recon",
        "gray-box: PIA GPU512 baseline / none": "gray-box PIA",
        "gray-box: PIA GPU512 baseline / provisional G-1 = stochastic-dropout (all_steps)": "PIA + G-1 dropout",
        "white-box: GSA 1k-3shadow / none": "white-box GSA",
        "white-box: GSA 1k-3shadow / W-1 strong-v3 full-scale": "DPDM W-1",
    }
    if label in admitted_labels:
        return admitted_labels[label]

    if source == "rediffuse-stl10" and label == "denoising-loss scout":
        return "ReDiffuse loss"
    if source == "rediffuse-stl10" and label == "score-norm scout":
        return "ReDiffuse norm"
    if source == "commoncanvas":
        return "CommonCanvas loss"
    if source == "tracing-roots":
        return "Tracing Roots features"

    h2_labels = {
        "output-cloud 512/512": "output-cloud",
        "raw H2 logistic": "raw H2",
        "lowpass H2 logistic": "lowpass H2",
        "label shuffle": "label shuffle",
        "shared-position seed 176": "seed176 control",
        "shared-position label shuffle": "seed176 shuffle",
        "shared-position seed 177": "seed177 control",
        "seed 177 label shuffle": "seed177 shuffle",
        "shared_position_seed176 to shared_position_seed177": "176 -> 177 transfer",
        "shared_position_seed177 to shared_position_seed176": "177 -> 176 transfer",
    }
    return h2_labels.get(label, label.replace("_", " "))


def plot_metric_bars(rows: list[dict], path: Path, title: str, figsize: tuple[float, float]) -> None:
    labels = [metric_plot_label(row) for row in rows]
    auc = [float(row["auc"]) for row in rows]
    tpr = [float(row["tpr_at_1pct_fpr"]) for row in rows]

    fig, ax = plt.subplots(figsize=figsize)
    y = list(range(len(rows)))
    height = 0.36
    ax.barh([i - height / 2 for i in y], auc, height, label="AUC", color="#376da6")
    ax.barh([i + height / 2 for i in y], tpr, height, label="TPR@1%", color="#d58f2f")
    ax.axvline(0.5, color="#666666", linewidth=0.8, linestyle="--", label="random")
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("metric value")
    ax.set_title(title, pad=18)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.2)
    ax.legend(
        frameon=False,
        ncol=3,
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        borderaxespad=0,
        fontsize=8,
    )
    fig.tight_layout(pad=0.6)
    fig.savefig(path, metadata=PDF_METADATA, bbox_inches="tight")
    plt.close(fig)


def plot_artifact_gate_summary(rows: list[dict], path: Path) -> None:
    corpora = []
    for row in rows:
        if row["corpus"] not in corpora:
            corpora.append(row["corpus"])

    colors = {"Pass": "#2f7d4f", "Partial": "#d49a2f", "Fail": "#b84a4a"}
    fig, axes = plt.subplots(len(corpora), 1, figsize=(8.0, 2.8 * len(corpora)), sharex=True)
    if len(corpora) == 1:
        axes = [axes]

    for ax, corpus in zip(axes, corpora):
        corpus_rows = [row for row in rows if row["corpus"] == corpus]
        gates = [label for _, label in GATE_COLUMNS]
        x_positions = list(range(len(gates)))
        bottoms = [0] * len(gates)
        for outcome in GATE_OUTCOMES:
            values = []
            for gate in gates:
                match = next(row for row in corpus_rows if row["gate"] == gate and row["outcome"] == outcome)
                values.append(int(match["count"]))
            ax.bar(x_positions, values, bottom=bottoms, label=outcome, color=colors[outcome])
            bottoms = [bottom + value for bottom, value in zip(bottoms, values)]
        ax.set_title(corpus)
        ax.set_ylabel("rows")
        ax.grid(axis="y", alpha=0.2)

    axes[-1].set_xlabel("evidence-contract gate")
    axes[-1].set_xticks(x_positions)
    axes[-1].set_xticklabels(
        [GATE_PLOT_LABELS.get(gate, gate) for gate in gates],
        rotation=35,
        ha="right",
    )
    fig.suptitle("Selected-corpus gate labels", y=0.98)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.94), frameon=False, ncol=3)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(path, metadata=PDF_METADATA, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    admitted = build_admitted_rows()
    h2 = build_h2_rows()
    negative = build_negative_rows()
    artifact_gate_summary, artifact_strata_summary = build_artifact_gate_summaries()

    write_csv(DATA / "admitted_rows.csv", admitted)
    write_csv(DATA / "h2_output_cloud_rows.csv", h2)
    write_csv(DATA / "negative_support_rows.csv", negative)
    write_csv(DATA / "artifact_gate_summary.csv", artifact_gate_summary)
    write_csv(DATA / "artifact_strata_summary.csv", artifact_strata_summary)

    plot_metric_bars(admitted, FIGURES / "admitted_rows_metrics.pdf", "Admitted evidence bundle", (3.9, 2.55))
    h2_plot_rows = [row for row in h2 if row["role"] in {"candidate", "baseline", "sanity", "control", "stability", "transfer"}]
    plot_metric_bars(h2_plot_rows, FIGURES / "h2_output_cloud_controls.pdf", "H2 output-cloud geometry controls", (7.1, 4.15))
    plot_artifact_gate_summary(artifact_gate_summary, FIGURES / "artifact_gate_summary.pdf")

    manifest_path = PAPER / "asset_manifest.json"
    previous_manifest = {}
    if manifest_path.exists():
        previous_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = {
        "generated": [
            "data/admitted_rows.csv",
            "data/h2_output_cloud_rows.csv",
            "data/negative_support_rows.csv",
            "data/artifact_gate_summary.csv",
            "data/artifact_strata_summary.csv",
            "figures/admitted_rows_metrics.pdf",
            "figures/h2_output_cloud_controls.pdf",
            "figures/artifact_gate_summary.pdf",
        ],
        "curated": previous_manifest.get("curated", []),
        "source_policy": "All numbers are read from existing DiffAudit Research JSON artifacts or frozen evidence notes.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
