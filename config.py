"""
Central configuration for the Resume Screening & Candidate-Job Matching System.

Focuses strictly on RESUME <-> JOB DESCRIPTION MATCHING using the
Candidate-Job Matching Synthetic Dataset.
"""
from pathlib import Path

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Raw dataset files (MIRRA Resume-Job Matching Dataset CSV files)
RAW_RESUMES_FILE = RAW_DATA_DIR / "resumes.csv"
RAW_JOBS_FILE = RAW_DATA_DIR / "jobs.csv"
RAW_MATCHES_FILE = RAW_DATA_DIR / "matches.csv"

# Normalized processed files (CSV format)
CANDIDATES_FILE = PROCESSED_DATA_DIR / "candidates.csv"
JOBS_FILE = PROCESSED_DATA_DIR / "jobs.csv"
MATCHES_FILE = PROCESSED_DATA_DIR / "matches.csv"
DATASET_PROFILE_JSON = DATA_DIR / "dataset_profile.json"

# Artifacts
SKILLS_VOCAB_PATH = MODELS_DIR / "skills_vocab.json"
VECTORIZER_PATH = MODELS_DIR / "matching_vectorizer.joblib"
TFIDF_VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.joblib"
LABEL_ENCODER_PATH = MODELS_DIR / "label_encoder.joblib"
CANDIDATE_TFIDF_MATRIX_PATH = MODELS_DIR / "candidate_tfidf.joblib"

# Model Checkpoints
MODEL_FILES = {
    "Linear SVM": MODELS_DIR / "linear_svm.joblib",
    "Logistic Regression": MODELS_DIR / "logistic_regression.joblib",
    "Random Forest": MODELS_DIR / "random_forest.joblib",
    "Multinomial Naive Bayes": MODELS_DIR / "multinomial_nb.joblib",
    "AdaBoost": MODELS_DIR / "adaboost.joblib",
}
DEFAULT_UI_MODEL = "Linear SVM"

# Evaluation Outputs
BENCHMARK_JSON = OUTPUTS_DIR / "matching_benchmark.json"
BENCHMARK_CSV = OUTPUTS_DIR / "matching_benchmark.csv"
METRICS_CSV = OUTPUTS_DIR / "metrics.csv"
METRICS_JSON = OUTPUTS_DIR / "metrics.json"
MODELS_BENCHMARK_JSON = OUTPUTS_DIR / "models_benchmark.json"

# Ensure directories exist
for _d in (DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, OUTPUTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------
# Matching & Training Hyperparameters
# ----------------------------------------------------------------------------
RANDOM_STATE = 42
TEST_SIZE = 0.2

# TF-IDF representation settings
TFIDF_MAX_FEATURES = 10000
TFIDF_NGRAM_RANGE = (1, 2)
TFIDF_MIN_DF = 2

# Scoring Weights
DEFAULT_SKILL_WEIGHT = 0.55
DEFAULT_TEXT_WEIGHT = 0.45
DEFAULT_MUST_HAVE_WEIGHT = 0.75
DEFAULT_NICE_TO_HAVE_WEIGHT = 0.25

# Dataset Metadata
DATASET_NAME = "MIRRA Resume-Job Matching Dataset"
IS_SYNTHETIC = True
LIMITATION_NOTICE = (
    "NOTICE: MIRRA Resume-Job Matching Dataset is configured in CSV format "
    "(raw and processed) for resume screening, semantic matching, and candidate classification."
)
