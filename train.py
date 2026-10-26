"""
Train & evaluate all four resume-classification models.

Pipeline:
  1. Load (or build) the dataset.
  2. Clean text -> TF-IDF features.
  3. Stratified train/test split.
  4. Train: Linear SVM, Logistic Regression, Random Forest, Multinomial NB.
  5. Evaluate: accuracy, precision, recall, F1 (weighted + macro).
  6. Persist: models, vectorizer, label encoder, metrics (CSV + JSON),
     per-model classification reports, confusion matrices.
  7. Trigger comparison-graph generation (src/visualize.py).

Run:  python train.py            (from the project root)
      python train.py --rebuild  (force dataset regeneration)
      python train.py --no-download  (skip HF download, use synthetic)
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

import config
from src.preprocessing import clean_text
from src.data_loader import load_or_build_dataset
from src.models import build_models


def evaluate(y_true, y_pred, label_names) -> dict:
    """Compute the full metric suite for one model."""
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision_weighted": precision_score(y_true, y_pred, average="weighted",
                                              zero_division=0),
        "recall_weighted": recall_score(y_true, y_pred, average="weighted",
                                        zero_division=0),
        "f1_weighted": f1_score(y_true, y_pred, average="weighted",
                               zero_division=0),
        "precision_macro": precision_score(y_true, y_pred, average="macro",
                                           zero_division=0),
        "recall_macro": recall_score(y_true, y_pred, average="macro",
                                     zero_division=0),
        "f1_macro": f1_score(y_true, y_pred, average="macro", zero_division=0),
    }


def main(rebuild: bool = False, allow_download: bool = True) -> None:
    t_start = time.time()
    print("=" * 70)
    print("RESUME SCREENING — MODEL TRAINING PIPELINE")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Data
    # ------------------------------------------------------------------
    df = load_or_build_dataset(force_rebuild=rebuild, allow_download=allow_download)
    print(f"\nDataset: {len(df)} resumes across {df['Category'].nunique()} categories.")

    print("Cleaning text ...")
    df["clean"] = df["Resume"].astype(str).map(clean_text)
    df = df[df["clean"].str.len() > 0].reset_index(drop=True)

    # ------------------------------------------------------------------
    # 2. Encode labels + TF-IDF features
    # ------------------------------------------------------------------
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(df["Category"])
    label_names = list(label_encoder.classes_)

    vectorizer = TfidfVectorizer(
        max_features=config.TFIDF_MAX_FEATURES,
        ngram_range=config.TFIDF_NGRAM_RANGE,
        min_df=config.TFIDF_MIN_DF,
        sublinear_tf=True,
    )
    X = vectorizer.fit_transform(df["clean"])
    print(f"TF-IDF matrix: {X.shape[0]} docs x {X.shape[1]} features.")

    # ------------------------------------------------------------------
    # 3. Split
    # ------------------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=config.TEST_SIZE,
        random_state=config.RANDOM_STATE,
        stratify=y,
    )
    print(f"Train: {X_train.shape[0]}  |  Test: {X_test.shape[0]}")

    # ------------------------------------------------------------------
    # 4 & 5. Train + evaluate every model
    # ------------------------------------------------------------------
    models = build_models()
    metrics_rows = []
    reports = {}
    confusions = {}

    for name, model in models.items():
        print(f"\n--- Training: {name} ---")
        t0 = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - t0

        y_pred = model.predict(X_test)
        m = evaluate(y_test, y_pred, label_names)
        m["model"] = name
        m["train_seconds"] = round(train_time, 2)
        metrics_rows.append(m)

        reports[name] = classification_report(
            y_test, y_pred, target_names=label_names, zero_division=0
        )
        confusions[name] = confusion_matrix(y_test, y_pred).tolist()

        # Persist the fitted model
        joblib.dump(model, config.MODEL_FILES[name])
        print(f"  accuracy={m['accuracy']:.4f}  "
              f"f1(weighted)={m['f1_weighted']:.4f}  "
              f"precision={m['precision_weighted']:.4f}  "
              f"recall={m['recall_weighted']:.4f}  "
              f"({train_time:.1f}s)")

    # ------------------------------------------------------------------
    # 6. Persist shared artefacts + metrics
    # ------------------------------------------------------------------
    joblib.dump(vectorizer, config.VECTORIZER_PATH)
    joblib.dump(label_encoder, config.LABEL_ENCODER_PATH)

    metrics_df = pd.DataFrame(metrics_rows)
    ordered_cols = ["model", "accuracy", "precision_weighted",
                    "recall_weighted", "f1_weighted",
                    "precision_macro", "recall_macro", "f1_macro",
                    "train_seconds"]
    metrics_df = metrics_df[ordered_cols].sort_values(
        "f1_weighted", ascending=False).reset_index(drop=True)
    metrics_df.to_csv(config.METRICS_CSV, index=False)

    with open(config.METRICS_JSON, "w", encoding="utf-8") as fh:
        json.dump(
            {
                "metrics": metrics_rows,
                "label_names": label_names,
                "n_samples": int(len(df)),
                "n_features": int(X.shape[1]),
                "confusion_matrices": confusions,
            },
            fh, indent=2,
        )

    # Human-readable per-model reports
    with open(config.OUTPUTS_DIR / "classification_reports.txt", "w",
              encoding="utf-8") as fh:
        for name, rep in reports.items():
            fh.write("=" * 70 + "\n")
            fh.write(f"{name}\n")
            fh.write("=" * 70 + "\n")
            fh.write(rep + "\n\n")

    print("\n" + "=" * 70)
    print("RESULTS SUMMARY (sorted by weighted F1)")
    print("=" * 70)
    print(metrics_df.to_string(index=False))

    best = metrics_df.iloc[0]
    print(f"\nBest model: {best['model']}  "
          f"(F1={best['f1_weighted']:.4f}, accuracy={best['accuracy']:.4f})")

    # ------------------------------------------------------------------
    # 7. Graphs
    # ------------------------------------------------------------------
    print("\nGenerating comparison graphs ...")
    try:
        from src.visualize import generate_all_graphs
        generate_all_graphs()
    except Exception as exc:
        print(f"[train] Graph generation skipped ({exc}). "
              f"Run `python -m src.visualize` after installing matplotlib/seaborn.")

    print(f"\nDone in {time.time() - t_start:.1f}s. "
          f"Artefacts in: {config.MODELS_DIR} and {config.OUTPUTS_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train resume-screening models.")
    parser.add_argument("--rebuild", action="store_true",
                        help="Force regeneration of the dataset.")
    parser.add_argument("--no-download", action="store_true",
                        help="Skip public-dataset download; use synthetic data.")
    args = parser.parse_args()
    main(rebuild=args.rebuild, allow_download=not args.no_download)
