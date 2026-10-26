"""
Professional Model Evaluation Module for Resume Screening & Candidate Classification.

Provides reusable evaluation functions for:
1. ROC Curve generation (multi-model with AUC in legend)
2. AUC Score Comparison bar chart (sorted, best model highlighted)
3. Confusion Matrices (binary classification heatmaps for TP, FP, FN, TN)
4. Full metrics evaluation suite (Accuracy, Precision, Recall, F1, AUC, Latency)

Outputs saved to:
  - outputs/
  - static/assets/eval/
  - outputs/models_benchmark.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_curve,
    roc_auc_score,
    precision_recall_curve,
    average_precision_score,
)
from sklearn.model_selection import train_test_split

import config
from src.data_loader import load_processed_data

# Ensure output directories exist
EVAL_DIRS = [
    config.OUTPUTS_DIR,
    PROJECT_ROOT / "static" / "assets" / "eval",
]
for d in EVAL_DIRS:
    d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Core Reusable Metric Calculations
# ---------------------------------------------------------------------------

def calculate_roc_auc(y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, Any]:
    """
    Calculate ROC Curve and AUC Score from actual prediction probabilities.
    Returns:
      - auc: float (Area Under ROC Curve)
      - fpr: list of FPR points
      - tpr: list of TPR points
      - optimal_point: dict with FPR, TPR, threshold, and Youden's J statistic
      - roc_points: 51 linearly spaced coordinate pairs for rendering
    """
    auc_score = float(roc_auc_score(y_true, y_prob))
    fpr_raw, tpr_raw, thresholds = roc_curve(y_true, y_prob)

    # Youden's J statistic (TPR - FPR) to find optimal threshold
    j_scores = tpr_raw - fpr_raw
    best_j_idx = int(np.argmax(j_scores))
    optimal_point = {
        "fpr": round(float(fpr_raw[best_j_idx]), 4),
        "tpr": round(float(tpr_raw[best_j_idx]), 4),
        "threshold": round(float(thresholds[best_j_idx]), 4) if best_j_idx < len(thresholds) else 0.5,
        "youden_j": round(float(j_scores[best_j_idx]), 4),
    }

    # 51 interpolated ROC points across FPR [0.0, 1.0]
    interp_fpr = np.linspace(0.0, 1.0, 51)
    interp_tpr = np.interp(interp_fpr, fpr_raw, tpr_raw)
    interp_tpr[0] = 0.0
    interp_tpr[-1] = 1.0
    roc_points = [
        {"fpr": round(float(f), 4), "tpr": round(float(t), 4)}
        for f, t in zip(interp_fpr, interp_tpr)
    ]

    return {
        "auc": round(auc_score, 4),
        "auc_pct": round(auc_score * 100.0, 2),
        "optimal_point": optimal_point,
        "roc_points": roc_points,
    }


def calculate_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, Any]:
    """
    Calculate binary classification confusion matrix:
                     Actual
                  Match  No Match
    Pred Match      TP      FP
    Pred No Match   FN      TN
    """
    y_true_arr = np.asarray(y_true)
    y_pred_arr = np.asarray(y_pred)

    tp = int(np.sum((y_true_arr == 1) & (y_pred_arr == 1)))
    fp = int(np.sum((y_true_arr == 0) & (y_pred_arr == 1)))
    fn = int(np.sum((y_true_arr == 1) & (y_pred_arr == 0)))
    tn = int(np.sum((y_true_arr == 0) & (y_pred_arr == 0)))
    total = tp + fp + fn + tn

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "total": total,
        "tp_pct": round(float(tp / total * 100.0), 2) if total else 0.0,
        "fp_pct": round(float(fp / total * 100.0), 2) if total else 0.0,
        "fn_pct": round(float(fn / total * 100.0), 2) if total else 0.0,
        "tn_pct": round(float(tn / total * 100.0), 2) if total else 0.0,
        "matrix": [[tp, fp], [fn, tn]],
        "labels": {
            "actual": ["Match", "No Match"],
            "predicted": ["Pred Match", "Pred No Match"],
        },
    }


# ---------------------------------------------------------------------------
# Reusable Plot Generators
# ---------------------------------------------------------------------------

def generate_roc_curves(
    results: List[Dict[str, Any]], 
    out_paths: List[Path], 
    title: str = "ROC Curve - Model Comparison"
) -> None:
    """
    Plot ROC Curves for all classification models on the same chart:
    - Logistic Regression
    - Random Forest
    - AdaBoost
    Includes AUC in legend (e.g. Model (AUC = 0.XX)), diagonal random line, and styled layout.
    """
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)

    # Diagonal random-classifier reference line
    ax.plot([0, 1], [0, 1], linestyle="--", color="#64748b", label="Random Classifier (AUC = 0.50)", linewidth=1.5)

    for r in results:
        fpr = [p["fpr"] for p in r["roc_points"]]
        tpr = [p["tpr"] for p in r["roc_points"]]
        # Legend format required: <Model> (AUC = 0.XX)
        ax.plot(
            fpr, 
            tpr, 
            color=r["color"], 
            label=f"{r['model']} (AUC = {r['auc']:.2f})", 
            linewidth=2.4
        )
        opt = r.get("optimal_point", {})
        if opt and "fpr" in opt and "tpr" in opt:
            ax.scatter([opt["fpr"]], [opt["tpr"]], color=r["color"], s=50, edgecolors="white", linewidths=1.2, zorder=5)

    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.05])
    ax.set_xlabel("False Positive Rate (FPR)", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_ylabel("True Positive Rate (TPR / Recall)", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=12)
    ax.legend(loc="lower right", fontsize=9.5, framealpha=0.92)
    ax.grid(True, linestyle=":", alpha=0.5)
    fig.tight_layout()

    for p in out_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, dpi=150)
        print(f"[evaluate_models] Saved ROC Curve: {p}")
    plt.close(fig)


def generate_auc_comparison(
    results: List[Dict[str, Any]], 
    out_paths: List[Path], 
    title: str = "AUC Score Comparison"
) -> None:
    """
    Create a separate bar chart comparing the AUC scores:
    - Sorted from highest AUC to lowest AUC.
    - Numerical AUC value above each bar.
    - Range between 0 and 1.
    - Y-axis labeled as 'AUC Score'.
    - Best-performing model visually highlighted.
    """
    sorted_res = sorted(results, key=lambda r: r["auc"], reverse=True)
    models = [r["model"] for r in sorted_res]
    aucs = [r["auc"] for r in sorted_res]
    colors = [r["color"] for r in sorted_res]
    best_model_name = sorted_res[0]["model"]

    fig, ax = plt.subplots(figsize=(7.5, 5.5), dpi=150)
    bars = ax.bar(models, aucs, color=colors, width=0.45, edgecolor="#ffffff", linewidth=1.2)

    for bar, r in zip(bars, sorted_res):
        val = r["auc"]
        is_best = (r["model"] == best_model_name)

        label_text = f"{val:.4f}" + ("\n(BEST)" if is_best else "")
        ax.annotate(
            label_text,
            xy=(bar.get_x() + bar.get_width() / 2, val),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color="#fbbf24" if is_best else "#1e293b",
        )
        if is_best:
            bar.set_edgecolor("#fbbf24")
            bar.set_linewidth(2.6)

    ax.set_ylim([0.0, 1.12])
    ax.set_ylabel("AUC Score", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=14)
    ax.axhline(0.5, color="#64748b", linestyle="--", linewidth=1.2, label="Random Guess (0.50)")
    ax.legend(loc="lower right", fontsize=9, framealpha=0.9)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()

    for p in out_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(p, dpi=150)
        print(f"[evaluate_models] Saved AUC Comparison: {p}")
    plt.close(fig)


def generate_confusion_matrices(
    results: List[Dict[str, Any]], 
    out_dirs: List[Path]
) -> None:
    """
    Generate confusion matrix heatmaps for each model:
    - Logistic Regression Confusion Matrix
    - Random Forest Confusion Matrix
    - AdaBoost Confusion Matrix

    Format:
                     Actual
                  Match  No Match
    Pred Match      TP      FP
    Pred No Match   FN      TN
    Clearly labels TP, FP, FN, TN with actual counts and percentages.
    """
    for r in results:
        cm = r["confusion_matrix"]
        tp, fp, fn, tn = cm["tp"], cm["fp"], cm["fn"], cm["tn"]
        total = cm["total"]
        mat = np.array([[tp, fp], [fn, tn]])

        fig, ax = plt.subplots(figsize=(6.5, 5.5), dpi=150)
        im = ax.imshow(mat, cmap="Blues", interpolation="nearest")

        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.ax.tick_params(labelsize=9)

        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Match", "No Match"], fontsize=11, fontweight="bold")
        ax.set_yticklabels(["Pred Match", "Pred No Match"], fontsize=11, fontweight="bold")

        ax.set_xlabel("Actual Class", fontsize=11, fontweight="bold", labelpad=8)
        ax.set_ylabel("Predicted Class", fontsize=11, fontweight="bold", labelpad=8)
        ax.set_title(f"{r['model']} Confusion Matrix", fontsize=13, fontweight="bold", pad=14)

        cell_labels = [
            [f"True Positive (TP)\n{tp:,}\n({(tp/total*100):.1f}%)", f"False Positive (FP)\n{fp:,}\n({(fp/total*100):.1f}%)"],
            [f"False Negative (FN)\n{fn:,}\n({(fn/total*100):.1f}%)", f"True Negative (TN)\n{tn:,}\n({(tn/total*100):.1f}%)"],
        ]

        thresh = mat.max() / 2.0
        for i in range(2):
            for j in range(2):
                color = "white" if mat[i, j] > thresh else "#0f172a"
                ax.text(
                    j, i, cell_labels[i][j], 
                    ha="center", va="center", color=color,
                    fontsize=10.5, fontweight="bold", linespacing=1.35
                )

        fig.tight_layout()

        safe_name = r["model"].lower().replace(" ", "_")
        for d in out_dirs:
            out_file = d / f"confusion_matrix_{safe_name}.png"
            fig.savefig(out_file, dpi=150)
            print(f"[evaluate_models] Saved Confusion Matrix: {out_file}")
        plt.close(fig)

    # Also generate a 1x3 combined panel of all confusion matrices
    fig, axes = plt.subplots(1, len(results), figsize=(18, 5.5), dpi=150)
    for ax, r in zip(axes, results):
        cm = r["confusion_matrix"]
        tp, fp, fn, tn = cm["tp"], cm["fp"], cm["fn"], cm["tn"]
        total = cm["total"]
        mat = np.array([[tp, fp], [fn, tn]])
        im = ax.imshow(mat, cmap="Blues", interpolation="nearest")

        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_xticklabels(["Match", "No Match"], fontsize=10, fontweight="bold")
        ax.set_yticklabels(["Pred Match", "Pred No Match"], fontsize=10, fontweight="bold")
        ax.set_xlabel("Actual Class", fontsize=10, fontweight="bold")
        ax.set_ylabel("Predicted Class", fontsize=10, fontweight="bold")
        ax.set_title(f"{r['model']} Confusion Matrix\nAccuracy: {r['accuracy']}% | F1: {r['f1_score']}%", fontsize=11, fontweight="bold")

        cell_labels = [
            [f"TP: {tp:,}\n({tp/total*100:.1f}%)", f"FP: {fp:,}\n({fp/total*100:.1f}%)"],
            [f"FN: {fn:,}\n({fn/total*100:.1f}%)", f"TN: {tn:,}\n({tn/total*100:.1f}%)"],
        ]
        thresh = mat.max() / 2.0
        for i in range(2):
            for j in range(2):
                color = "white" if mat[i, j] > thresh else "#0f172a"
                ax.text(j, i, cell_labels[i][j], ha="center", va="center", color=color, fontsize=10, fontweight="bold")

    fig.suptitle("Comparative Confusion Matrices (Match vs. No Match)", fontsize=13, fontweight="bold", y=1.02)
    fig.tight_layout()
    for d in out_dirs:
        panel_file = d / "confusion_matrices_comparison.png"
        fig.savefig(panel_file, dpi=150)
        print(f"[evaluate_models] Saved 1x3 Confusion Matrices Panel: {panel_file}")
    plt.close(fig)


# ---------------------------------------------------------------------------
# End-to-End Evaluation Pipeline
# ---------------------------------------------------------------------------

def run_evaluation_pipeline() -> Dict[str, Any]:
    """
    Executes complete ML evaluation on the existing dataset, TF-IDF vectorizer,
    and models (Logistic Regression, Random Forest, AdaBoost).
    """
    print("\n" + "=" * 70)
    print("RESUME SCREENING & MATCHING — PROFESSIONAL ML EVALUATION PIPELINE")
    print("=" * 70)

    candidates_df, jobs_df, matches_df, vocab = load_processed_data()

    # Load TF-IDF Vectorizer
    if config.VECTORIZER_PATH.exists():
        vectorizer = joblib.load(config.VECTORIZER_PATH)
    else:
        from src.matching_engine import MatchingEngine
        engine = MatchingEngine(auto_load=True)
        vectorizer = engine.vectorizer

    print("[evaluate_models] Preparing balanced ground-truth evaluation dataset...")
    rng = np.random.RandomState(config.RANDOM_STATE)
    cand_dict = {row["candidate_id"]: row["clean_resume_text"] for _, row in candidates_df.iterrows()}
    all_cand_ids = list(cand_dict.keys())

    X_texts = []
    y = []

    sample_jobs = jobs_df.sample(n=min(300, len(jobs_df)), random_state=config.RANDOM_STATE)
    matches_lookup = {row["job_id"]: set(row["relevant_resume_ids"]) for _, row in matches_df.iterrows()}

    for _, jrow in sample_jobs.iterrows():
        jid = jrow["job_id"]
        jtext = jrow["clean_job_text"]
        pos_ids = list(matches_lookup.get(jid, set()))

        chosen_pos = pos_ids[:min(10, len(pos_ids))]
        for cid in chosen_pos:
            if cid in cand_dict:
                X_texts.append(cand_dict[cid] + " " + jtext)
                y.append(1)

        neg_ids = [cid for cid in rng.choice(all_cand_ids, size=len(chosen_pos) * 2) if cid not in pos_ids][:len(chosen_pos)]
        for cid in neg_ids:
            if cid in cand_dict:
                X_texts.append(cand_dict[cid] + " " + jtext)
                y.append(0)

    y = np.array(y)
    print(f"[evaluate_models] Dataset size: {len(y)} pairs (Positives: {np.sum(y == 1)}, Negatives: {np.sum(y == 0)})")

    # TF-IDF Transform
    X = vectorizer.transform(X_texts)

    # 80/20 Stratified Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=config.RANDOM_STATE, stratify=y
    )
    print(f"[evaluate_models] Train size: {X_train.shape[0]} | Test size: {X_test.shape[0]}")

    models_config = {
        "Logistic Regression": {
            "type": "Baseline",
            "model": LogisticRegression(max_iter=1000, random_state=config.RANDOM_STATE),
            "color": "#38bdf8",
        },
        "Random Forest": {
            "type": "Bagging",
            "model": RandomForestClassifier(n_estimators=100, max_depth=15, random_state=config.RANDOM_STATE, n_jobs=-1),
            "color": "#a78bfa",
        },
        "AdaBoost": {
            "type": "Boosting",
            "model": AdaBoostClassifier(n_estimators=80, random_state=config.RANDOM_STATE),
            "color": "#fbbf24",
        },
    }

    results = []

    for name, m_info in models_config.items():
        print(f"\n[evaluate_models] Training and evaluating {name} ({m_info['type']})...")
        clf = m_info["model"]

        t_start = time.time()
        clf.fit(X_train, y_train)
        train_time = time.time() - t_start

        # Measure prediction latency
        p_start = time.time()
        y_pred = clf.predict(X_test)
        pred_time_ms = (time.time() - p_start) / X_test.shape[0] * 1000.0

        # Predict probability or decision function
        if hasattr(clf, "predict_proba"):
            y_prob = clf.predict_proba(X_test)[:, 1]
        elif hasattr(clf, "decision_function"):
            y_prob = clf.decision_function(X_test)
        else:
            y_prob = y_pred

        # Core Metrics
        acc = float(accuracy_score(y_test, y_pred) * 100.0)
        prec = float(precision_score(y_test, y_pred, zero_division=0) * 100.0)
        rec = float(recall_score(y_test, y_pred, zero_division=0) * 100.0)
        f1 = float(f1_score(y_test, y_pred, zero_division=0) * 100.0)

        # ROC & AUC
        roc_data = calculate_roc_auc(y_test, y_prob)

        # PR & PR-AUC
        pr_prec_raw, pr_rec_raw, _ = precision_recall_curve(y_test, y_prob)
        pr_auc_score = float(average_precision_score(y_test, y_prob))
        interp_rec = np.linspace(0.0, 1.0, 51)
        interp_prec = np.interp(interp_rec, pr_rec_raw[::-1], pr_prec_raw[::-1])
        pr_points = [
            {"recall": round(float(r), 4), "precision": round(float(p), 4)}
            for r, p in zip(interp_rec, interp_prec)
        ]

        # Confusion Matrix
        cm_data = calculate_confusion_matrix(y_test, y_pred)

        # Save model joblib
        save_path = config.MODELS_DIR / f"{name.lower().replace(' ', '_')}.joblib"
        joblib.dump(clf, save_path)

        results.append({
            "model": name,
            "type": m_info["type"],
            "accuracy": round(acc, 2),
            "precision": round(prec, 2),
            "recall": round(rec, 2),
            "f1_score": round(f1, 2),
            "auc": roc_data["auc"],
            "auc_pct": roc_data["auc_pct"],
            "pr_auc": round(pr_auc_score, 4),
            "pr_auc_pct": round(pr_auc_score * 100.0, 2),
            "train_time": f"{train_time:.2f}s",
            "pred_time": f"{pred_time_ms:.1f}ms",
            "pred_time_ms": round(pred_time_ms, 3),
            "color": m_info["color"],
            "optimal_point": roc_data["optimal_point"],
            "roc_points": roc_data["roc_points"],
            "pr_points": pr_points,
            "confusion_matrix": cm_data,
        })

    # Dynamically determine the best-performing model based on F1-score (or composite F1 + AUC)
    best_model = max(results, key=lambda r: (r["f1_score"], r["auc"]))
    for r in results:
        r["is_winner"] = (r["model"] == best_model["model"])

    # Output dictionaries for frontends
    roc_curves_dict = {
        r["model"]: {
            "model": r["model"],
            "type": r["type"],
            "color": r["color"],
            "auc": r["auc"],
            "auc_pct": r["auc_pct"],
            "optimal_point": r["optimal_point"],
            "points": r["roc_points"],
        }
        for r in results
    }

    confusion_matrices_dict = {
        r["model"]: r["confusion_matrix"]
        for r in results
    }

    payload = {
        "title": "Model Evaluation",
        "subtitle": "Comprehensive ROC Curve, AUC Comparison, and Confusion Matrices across Logistic Regression, Random Forest, and AdaBoost",
        "split_info": "Same 80/20 Stratified Split (random_state=42)",
        "primary_metric": "f1_score",
        "best_model": {
            "model": best_model["model"],
            "type": best_model["type"],
            "accuracy": best_model["accuracy"],
            "precision": best_model["precision"],
            "recall": best_model["recall"],
            "f1_score": best_model["f1_score"],
            "auc": best_model["auc"],
            "pred_time": best_model["pred_time"],
        },
        "models": results,
        "roc_curves": roc_curves_dict,
        "confusion_matrices": confusion_matrices_dict,
    }

    # Persist JSON benchmark
    out_json = config.OUTPUTS_DIR / "models_benchmark.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"\n[evaluate_models] Saved benchmark JSON to: {out_json}")

    # Generate Image Artifacts across both outputs/ and static/assets/eval/
    print("\n[evaluate_models] Generating visualization plots...")

    # 1. ROC Curves
    roc_paths = [
        config.OUTPUTS_DIR / "roc_curve.png",
        config.OUTPUTS_DIR / "roc_curves.png",
        PROJECT_ROOT / "static" / "assets" / "eval" / "roc_curve.png",
    ]
    generate_roc_curves(results, roc_paths, title="ROC Curve - Model Comparison")

    # 2. AUC Score Comparison
    auc_paths = [
        config.OUTPUTS_DIR / "auc_comparison.png",
        config.OUTPUTS_DIR / "auc_comparison_bars.png",
        PROJECT_ROOT / "static" / "assets" / "eval" / "auc_comparison.png",
    ]
    generate_auc_comparison(results, auc_paths, title="AUC Score Comparison")

    # 3. Confusion Matrices
    cm_dirs = [
        config.OUTPUTS_DIR,
        PROJECT_ROOT / "static" / "assets" / "eval",
    ]
    generate_confusion_matrices(results, cm_dirs)

    print("\n" + "=" * 70)
    print("MODEL EVALUATION SUMMARY TABLE")
    print("=" * 70)
    summary_df = pd.DataFrame([
        {
            "Model": r["model"],
            "Accuracy": f"{r['accuracy']}%",
            "Precision": f"{r['precision']}%",
            "Recall": f"{r['recall']}%",
            "F1": f"{r['f1_score']}%",
            "AUC": f"{r['auc']:.4f}",
            "Prediction Latency": r["pred_time"],
            "Winner": "YES" if r["is_winner"] else "No",
        }
        for r in results
    ])
    print(summary_df.to_string(index=False))
    print("=" * 70)
    print(f"Best Performing Model: {best_model['model']} (Accuracy: {best_model['accuracy']}%, F1: {best_model['f1_score']}%, AUC: {best_model['auc']:.4f}, Recall: {best_model['recall']}%, Latency: {best_model['pred_time']})")
    print("=" * 70)

    return payload


if __name__ == "__main__":
    run_evaluation_pipeline()
