"""
Train and benchmark classification models:
  1. Baseline: Logistic Regression
  2. Bagging: Random Forest
  3. Boosting: AdaBoost

Trained on TF-IDF features of the MIRRA Resume-Job Matching Dataset with
an 80/20 train/test stratified split (random_state=42).
Delegates to the unified ml.evaluate_models evaluation pipeline.
Saves models and outputs/models_benchmark.json, outputs/roc_curve.png,
outputs/auc_comparison.png, and outputs/confusion_matrix_*.png.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.evaluate_models import (
    calculate_roc_auc,
    calculate_confusion_matrix,
    generate_roc_curves,
    generate_auc_comparison,
    generate_confusion_matrices,
    run_evaluation_pipeline,
)


def train_and_evaluate_models() -> Dict[str, Any]:
    """Compatibility alias for the unified ML evaluation pipeline."""
    return run_evaluation_pipeline()


if __name__ == "__main__":
    train_and_evaluate_models()
