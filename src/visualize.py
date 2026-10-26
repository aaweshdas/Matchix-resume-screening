"""
Generate model-comparison graphs and per-model confusion matrices from the
metrics produced by train.py.

Outputs (PNG, 150 dpi) into outputs/:
  - model_comparison_bars.png      grouped bar chart of all 4 metrics
  - metric_<name>.png              one bar chart per metric across models
  - f1_ranking.png                 horizontal ranking by weighted F1
  - confusion_<model>.png          confusion matrix heatmap per model
  - metrics_heatmap.png            model x metric heatmap

Run:  python -m src.visualize
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

import config

# Non-interactive backend so it works on headless machines / servers.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

try:
    import seaborn as sns
    sns.set_style("whitegrid")
    _HAS_SNS = True
except Exception:
    _HAS_SNS = False

# Consistent, professional colour palette (one colour per model)
MODEL_COLORS = {
    "Linear SVM": "#2563eb",            # blue
    "Logistic Regression": "#16a34a",   # green
    "Random Forest": "#ea580c",         # orange
    "Multinomial Naive Bayes": "#9333ea",  # purple
}
PLOT_METRICS = [
    ("accuracy", "Accuracy"),
    ("precision_weighted", "Precision"),
    ("recall_weighted", "Recall"),
    ("f1_weighted", "F1 Score"),
]


def _load_metrics() -> dict:
    with open(config.METRICS_JSON, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _model_order(metrics):
    """Return models sorted by weighted F1 descending."""
    return sorted(metrics, key=lambda m: m["f1_weighted"], reverse=True)


def plot_grouped_bars(metrics):
    models = _model_order(metrics)
    names = [m["model"] for m in models]
    x = np.arange(len(PLOT_METRICS))
    width = 0.2

    fig, ax = plt.subplots(figsize=(11, 6))
    for i, m in enumerate(models):
        vals = [m[key] for key, _ in PLOT_METRICS]
        offset = (i - (len(models) - 1) / 2) * width
        bars = ax.bar(x + offset, vals, width, label=m["model"],
                      color=MODEL_COLORS.get(m["model"], None),
                      edgecolor="white", linewidth=0.5)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.01, f"{v:.2f}",
                    ha="center", va="bottom", fontsize=7.5, rotation=0)

    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in PLOT_METRICS], fontsize=11)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Score", fontsize=11)
    ax.set_title("Model Performance Comparison — Resume Screening",
                 fontsize=14, fontweight="bold", pad=14)
    ax.legend(loc="lower right", fontsize=9, framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    out = config.OUTPUTS_DIR / "model_comparison_bars.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  saved {out.name}")


def plot_per_metric(metrics):
    models = _model_order(metrics)
    names = [m["model"] for m in models]
    colors = [MODEL_COLORS.get(n) for n in names]
    for key, label in PLOT_METRICS:
        vals = [m[key] for m in models]
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(names, vals, color=colors, edgecolor="white")
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.008, f"{v:.3f}",
                    ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.set_ylim(0, 1.08)
        ax.set_ylabel(label, fontsize=11)
        ax.set_title(f"{label} by Model", fontsize=13, fontweight="bold")
        ax.tick_params(axis="x", rotation=15)
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        out = config.OUTPUTS_DIR / f"metric_{key}.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        print(f"  saved {out.name}")


def plot_f1_ranking(metrics):
    models = _model_order(metrics)[::-1]  # ascending for barh
    names = [m["model"] for m in models]
    vals = [m["f1_weighted"] for m in models]
    colors = [MODEL_COLORS.get(n) for n in names]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    bars = ax.barh(names, vals, color=colors, edgecolor="white")
    for b, v in zip(bars, vals):
        ax.text(v + 0.005, b.get_y() + b.get_height() / 2, f"{v:.3f}",
                va="center", fontsize=10, fontweight="bold")
    ax.set_xlim(0, 1.08)
    ax.set_xlabel("Weighted F1 Score", fontsize=11)
    ax.set_title("Model Ranking by F1 Score", fontsize=13, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    fig.tight_layout()
    out = config.OUTPUTS_DIR / "f1_ranking.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  saved {out.name}")


def plot_metrics_heatmap(metrics):
    models = _model_order(metrics)
    names = [m["model"] for m in models]
    keys = [k for k, _ in PLOT_METRICS] + ["precision_macro", "recall_macro",
                                           "f1_macro"]
    labels = [lbl for _, lbl in PLOT_METRICS] + ["Precision(macro)",
                                                 "Recall(macro)", "F1(macro)"]
    matrix = np.array([[m[k] for k in keys] for m in models])

    fig, ax = plt.subplots(figsize=(10, 5))
    if _HAS_SNS:
        sns.heatmap(matrix, annot=True, fmt=".3f", cmap="YlGnBu",
                    xticklabels=labels, yticklabels=names, vmin=0, vmax=1,
                    cbar_kws={"label": "Score"}, ax=ax, linewidths=0.5)
    else:
        im = ax.imshow(matrix, cmap="YlGnBu", vmin=0, vmax=1, aspect="auto")
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=30, ha="right")
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names)
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                ax.text(j, i, f"{matrix[i, j]:.3f}", ha="center", va="center",
                        fontsize=8)
        fig.colorbar(im, ax=ax, label="Score")
    ax.set_title("Metrics Heatmap (model x metric)", fontsize=13,
                 fontweight="bold")
    fig.tight_layout()
    out = config.OUTPUTS_DIR / "metrics_heatmap.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  saved {out.name}")


def plot_confusion_matrices(data):
    label_names = data["label_names"]
    confusions = data["confusion_matrices"]
    n_labels = len(label_names)
    # For readability, only annotate cells when the label set is small.
    annotate = n_labels <= 15
    show_ticklabels = n_labels <= 30

    for model_name, cm in confusions.items():
        cm = np.array(cm)
        # Row-normalize to show recall per class
        with np.errstate(invalid="ignore", divide="ignore"):
            cm_norm = cm / cm.sum(axis=1, keepdims=True)
            cm_norm = np.nan_to_num(cm_norm)

        fig, ax = plt.subplots(figsize=(min(1 + n_labels * 0.5, 16),
                                        min(1 + n_labels * 0.45, 14)))
        if _HAS_SNS:
            sns.heatmap(
                cm_norm, annot=annotate, fmt=".2f", cmap="Blues",
                xticklabels=label_names if show_ticklabels else False,
                yticklabels=label_names if show_ticklabels else False,
                vmin=0, vmax=1, cbar_kws={"label": "Recall (row-normalized)"},
                ax=ax, linewidths=0.3,
            )
        else:
            im = ax.imshow(cm_norm, cmap="Blues", vmin=0, vmax=1)
            fig.colorbar(im, ax=ax, label="Recall (row-normalized)")
            if show_ticklabels:
                ax.set_xticks(range(n_labels))
                ax.set_xticklabels(label_names, rotation=90, fontsize=7)
                ax.set_yticks(range(n_labels))
                ax.set_yticklabels(label_names, fontsize=7)

        ax.set_xlabel("Predicted", fontsize=11)
        ax.set_ylabel("Actual", fontsize=11)
        ax.set_title(f"Confusion Matrix — {model_name}", fontsize=13,
                     fontweight="bold")
        fig.tight_layout()
        safe = model_name.lower().replace(" ", "_")
        out = config.OUTPUTS_DIR / f"confusion_{safe}.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        print(f"  saved {out.name}")


def generate_all_graphs():
    data = _load_metrics()
    metrics = data["metrics"]
    plot_grouped_bars(metrics)
    plot_per_metric(metrics)
    plot_f1_ranking(metrics)
    plot_metrics_heatmap(metrics)
    plot_confusion_matrices(data)
    print(f"All graphs written to {config.OUTPUTS_DIR}")


if __name__ == "__main__":
    generate_all_graphs()
