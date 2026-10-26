"""
Inference & candidate-ranking engine used by the Streamlit UI.

Loads the persisted vectorizer, label encoder, and trained models, then
provides:
  - predict_category(text, model_name)   -> (category, confidence)
  - resume_jd_score(resume, jd)           -> 0-100 match score (cosine sim)
  - rank_candidates(jd, resumes, ...)     -> ranked DataFrame with scores
  - matched / missing keyword analysis for explainability
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

import config
from src.preprocessing import clean_text, extract_keywords


class ModelNotTrainedError(RuntimeError):
    """Raised when artefacts are missing (i.e. train.py hasn't been run)."""


@lru_cache(maxsize=1)
def _load_shared():
    """Load vectorizer + label encoder once (cached)."""
    if not config.VECTORIZER_PATH.exists() or not config.LABEL_ENCODER_PATH.exists():
        raise ModelNotTrainedError(
            "Vectorizer / label encoder not found. Run `python train.py` first."
        )
    vectorizer = joblib.load(config.VECTORIZER_PATH)
    label_encoder = joblib.load(config.LABEL_ENCODER_PATH)
    return vectorizer, label_encoder


@lru_cache(maxsize=8)
def _load_model(model_name: str):
    path = config.MODEL_FILES.get(model_name)
    if path is None:
        raise ValueError(f"Unknown model '{model_name}'. "
                         f"Choices: {list(config.MODEL_FILES)}")
    if not path.exists():
        raise ModelNotTrainedError(
            f"Model '{model_name}' not found at {path}. Run `python train.py`."
        )
    return joblib.load(path)


def available_models() -> list[str]:
    """Return the list of models that have been trained & saved."""
    return [name for name, path in config.MODEL_FILES.items() if path.exists()]


def artefacts_exist() -> bool:
    return (config.VECTORIZER_PATH.exists()
            and config.LABEL_ENCODER_PATH.exists()
            and len(available_models()) > 0)


def predict_category(text: str, model_name: str = config.DEFAULT_UI_MODEL):
    """Predict the job category for a resume/text. Returns (label, confidence).

    confidence is a 0-1 probability when the model supports predict_proba,
    otherwise None.
    """
    vectorizer, label_encoder = _load_shared()
    model = _load_model(model_name)

    cleaned = clean_text(text)
    X = vectorizer.transform([cleaned])
    pred_idx = int(model.predict(X)[0])
    label = label_encoder.inverse_transform([pred_idx])[0]

    confidence = None
    if hasattr(model, "predict_proba"):
        try:
            proba = model.predict_proba(X)[0]
            confidence = float(np.max(proba))
        except Exception:
            confidence = None
    return label, confidence


def predict_top_k(text: str, model_name: str = config.DEFAULT_UI_MODEL,
                  k: int = 3):
    """Return the top-k (category, probability) pairs, if probabilities exist."""
    vectorizer, label_encoder = _load_shared()
    model = _load_model(model_name)
    cleaned = clean_text(text)
    X = vectorizer.transform([cleaned])

    if not hasattr(model, "predict_proba"):
        label, _ = predict_category(text, model_name)
        return [(label, None)]

    proba = model.predict_proba(X)[0]
    top_idx = np.argsort(proba)[::-1][:k]
    labels = label_encoder.inverse_transform(top_idx)
    return [(lbl, float(proba[i])) for lbl, i in zip(labels, top_idx)]


def resume_jd_score(resume_text: str, jd_text: str) -> float:
    """Return a 0-100 semantic match score between a resume and a JD.

    Uses TF-IDF cosine similarity in the same feature space the models were
    trained on, so the score is consistent with the classifier's view of text.
    """
    vectorizer, _ = _load_shared()
    resume_clean = clean_text(resume_text)
    jd_clean = clean_text(jd_text)
    if not resume_clean or not jd_clean:
        return 0.0
    vecs = vectorizer.transform([resume_clean, jd_clean])
    sim = cosine_similarity(vecs[0], vecs[1])[0][0]
    # Cosine sim on TF-IDF is in [0,1]; scale to 0-100.
    return round(float(sim) * 100, 2)


def keyword_overlap(resume_text: str, jd_text: str, top_k: int = 40):
    """Return (matched, missing) JD keywords for explainability."""
    jd_keys = extract_keywords(jd_text, top_k=top_k)
    resume_keys = extract_keywords(resume_text, top_k=200)
    matched = sorted(jd_keys & resume_keys)
    missing = sorted(jd_keys - resume_keys)
    return matched, missing


def rank_candidates(jd_text: str,
                    resumes: list[dict],
                    model_name: str = config.DEFAULT_UI_MODEL,
                    target_category: str | None = None) -> pd.DataFrame:
    """Rank candidate resumes against a job description.

    Parameters
    ----------
    jd_text : the job description.
    resumes : list of {"name": str, "text": str}.
    model_name : classifier used for category prediction.
    target_category : if set, resumes predicted to this category get a bonus,
                      reflecting role fit (optional).

    Returns a DataFrame sorted by final_score (desc) with per-candidate detail.
    """
    rows = []
    for r in resumes:
        name = r.get("name", "Candidate")
        text = r.get("text", "")
        match = resume_jd_score(text, jd_text)          # 0-100
        category, confidence = predict_category(text, model_name)
        matched, missing = keyword_overlap(text, jd_text)

        # Skill coverage: fraction of JD keywords present in the resume.
        total_jd = len(matched) + len(missing)
        coverage = (len(matched) / total_jd * 100) if total_jd else 0.0

        # Final score blends semantic similarity (70%) and keyword coverage
        # (30%). A small role-fit bonus applies if the predicted category
        # matches the target role.
        final = 0.70 * match + 0.30 * coverage
        role_fit = False
        if target_category and category == target_category:
            final = min(100.0, final + 5.0)
            role_fit = True

        rows.append({
            "Candidate": name,
            "Match Score": round(match, 2),
            "Skill Coverage %": round(coverage, 2),
            "Final Score": round(final, 2),
            "Predicted Category": category,
            "Confidence": round(confidence * 100, 1) if confidence is not None else None,
            "Role Fit": role_fit,
            "Matched Skills": ", ".join(matched[:15]),
            "Missing Skills": ", ".join(missing[:15]),
        })

    df = pd.DataFrame(rows).sort_values("Final Score", ascending=False)
    df.insert(0, "Rank", range(1, len(df) + 1))
    return df.reset_index(drop=True)
