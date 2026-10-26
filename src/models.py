"""
Model definitions for the Resume Screening project.

Four classifiers, exactly as requested:
  - Linear SVM               (LinearSVC, calibrated for probabilities)
  - Logistic Regression
  - Random Forest
  - Multinomial Naive Bayes

Each is returned as a fresh, unfitted estimator so the trainer can fit them
on the TF-IDF features.
"""
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB

import config


def build_models(random_state: int = config.RANDOM_STATE) -> dict:
    """Return a dict {model_name: unfitted_estimator}.

    LinearSVC is wrapped in CalibratedClassifierCV so the UI can display a
    confidence/probability for the predicted category (LinearSVC alone has no
    predict_proba). This keeps SVM behaviour while enabling probabilities.
    """
    return {
        "Linear SVM": CalibratedClassifierCV(
            LinearSVC(C=1.0, class_weight="balanced", random_state=random_state),
            cv=3,
        ),
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            C=5.0,
            class_weight="balanced",
            random_state=random_state,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=250,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=random_state,
        ),
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.1),
    }
