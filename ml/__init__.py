"""
ML evaluation and model benchmarking package.
"""
from ml.evaluate_models import (
    calculate_roc_auc,
    calculate_confusion_matrix,
    generate_roc_curves,
    generate_auc_comparison,
    generate_confusion_matrices,
    run_evaluation_pipeline,
)

__all__ = [
    "calculate_roc_auc",
    "calculate_confusion_matrix",
    "generate_roc_curves",
    "generate_auc_comparison",
    "generate_confusion_matrices",
    "run_evaluation_pipeline",
]
