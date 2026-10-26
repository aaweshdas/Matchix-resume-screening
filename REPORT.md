# Resume Screening & Candidate Ranking — Project Report

**A Machine-Learning System for Automated Resume Classification and Candidate Ranking**

---

## 1. Abstract

This project implements an end-to-end machine-learning system that screens
resumes and ranks candidates against a given job description. Free-text
resumes are transformed into TF-IDF feature vectors and classified into job
categories by four supervised models — **Linear Support Vector Machine (SVM),
Logistic Regression, Random Forest, and Multinomial Naive Bayes**. Candidate
ranking is performed with an interpretable scoring function that combines
TF-IDF cosine similarity between a resume and the job description with a
skill-coverage measure. Every model is evaluated on a held-out test set using
**Accuracy, Precision, Recall, and F1-score**, and the results are compared
visually. The system is delivered as a professional, multi-tab **Streamlit**
web application.

---

## 2. Problem Statement & Objectives

Recruiters routinely receive hundreds of resumes per opening. Manually reading
and shortlisting them is slow, inconsistent, and prone to bias. The objectives
of this project are to:

1. **Automatically classify** a resume into its most likely job category.
2. **Score and rank** candidates by how well their resume matches a specific
   job description.
3. **Compare** four classical ML classifiers on the classification task using
   standard metrics.
4. Provide a **usable, professional interface** so a non-technical recruiter
   can screen and rank candidates without writing code.

---

## 3. Dataset

### 3.1 Sourcing strategy

The project uses a two-tier dataset strategy so it always runs end-to-end:

- **Tier 1 — Public download.** The pipeline first attempts to download a real,
  labelled resume dataset from the Hugging Face Hub (e.g. the *Resume-Atlas*
  family of datasets, which contain on the order of 13,000 labelled resumes
  across dozens of categories).
- **Tier 2 — Synthetic fallback.** If no internet/dataset is available, a
  built-in generator produces a **balanced, realistic dataset of ~8,000
  resumes across 25 job categories**. Each synthetic resume is assembled from
  category-specific skill pools, job titles, action verbs, education, and
  experience templates, with a small amount of cross-domain "noise" so the
  classification task is non-trivial and realistic.

This satisfies the requirement of **5,000–10,000 instances** regardless of
network access, and keeps the project fully reproducible (`RANDOM_STATE = 42`).

### 3.2 Categories (synthetic mode)

Data Science, Web Development, Java Developer, DevOps Engineer, Database
Administrator, Network Engineer, Cybersecurity Analyst, Mobile App Developer,
Accountant, Financial Analyst, Human Resources, Sales, Digital Marketing,
Mechanical Engineer, Civil Engineer, Electrical Engineer, Graphic Designer,
Content Writer, Project Manager, Business Analyst, Nurse, Teacher, Operations
Manager, Customer Service, and Quality Assurance.

### 3.3 Schema

| Column | Description |
|--------|-------------|
| `Category` | The ground-truth job category (classification label). |
| `Resume` | Raw resume text. |

---

## 4. Methodology

### 4.1 Text preprocessing

Raw text is normalised by a lightweight, dependency-free cleaner
(`src/preprocessing.py`):

- lowercasing,
- removal of URLs and email addresses,
- removal of stray punctuation **while preserving technology tokens** such as
  `c++`, `c#`, and `.net`,
- removal of pure-number tokens,
- English stop-word removal,
- whitespace normalisation.

### 4.2 Feature extraction — TF-IDF

Cleaned text is vectorised with **TF-IDF** (`TfidfVectorizer`):

- up to **8,000 features**,
- **unigrams and bigrams** (`ngram_range = (1, 2)`),
- minimum document frequency of 2,
- sublinear term-frequency scaling.

TF-IDF is a strong, well-understood representation for text classification and
keeps the models fast and interpretable.

### 4.3 Train / test split

A **stratified 80/20 split** preserves the class distribution across train and
test sets, ensuring every category is represented in evaluation.

### 4.4 Models

| Model | Configuration | Rationale |
|-------|---------------|-----------|
| **Linear SVM** | `LinearSVC`, `C=1.0`, balanced class weights, wrapped in `CalibratedClassifierCV` (3-fold) for probabilities | Excellent for high-dimensional sparse text; calibration enables confidence scores |
| **Logistic Regression** | `max_iter=1000`, `C=5.0`, balanced class weights | Strong, well-calibrated linear baseline |
| **Random Forest** | 250 trees, `min_samples_leaf=2`, balanced subsample | Non-linear ensemble; captures feature interactions |
| **Multinomial Naive Bayes** | `alpha=0.1` | Classic, fast probabilistic baseline for count/TF-IDF text |

### 4.5 Candidate ranking

Ranking (`src/ranking.py`) is deliberately **interpretable**:

- **Match Score (0–100)** = cosine similarity between the resume and the job
  description in TF-IDF space, scaled to 0–100.
- **Skill Coverage (%)** = fraction of the job description's key terms present
  in the resume.
- **Final Score** = `0.70 × Match Score + 0.30 × Skill Coverage`, with an
  optional **+5** bonus when the predicted category matches a recruiter-chosen
  target role.

Every score is traceable to concrete **matched** and **missing** skills, which
the UI displays per candidate.

---

## 5. Evaluation

### 5.1 Metrics

Each model is evaluated on the held-out test set with:

- **Accuracy** — overall fraction of correct predictions.
- **Precision** — of items predicted for a class, the fraction that were
  correct (penalises false positives).
- **Recall** — of items truly in a class, the fraction recovered (penalises
  false negatives).
- **F1-score** — harmonic mean of precision and recall.

Both **weighted** (accounts for class support) and **macro** (treats each
class equally) averages are reported. Per-model **confusion matrices** and a
full `classification_report` are also produced.

### 5.2 Results

> **Note.** The exact numbers below are produced when you run `python train.py`;
> they are written to `outputs/metrics.csv` and `outputs/metrics.json`, and the
> Model Dashboard renders them alongside the graphs. The table is laid out so
> you can drop the computed values straight in.

| Model | Accuracy | Precision | Recall | F1-score |
|-------|:--------:|:---------:|:------:|:--------:|
| Linear SVM | _from metrics.csv_ | _…_ | _…_ | _…_ |
| Logistic Regression | _…_ | _…_ | _…_ | _…_ |
| Random Forest | _…_ | _…_ | _…_ | _…_ |
| Multinomial Naive Bayes | _…_ | _…_ | _…_ | _…_ |

**Expected performance.** For clean, well-separated TF-IDF text classification
of this kind, the two linear models (**Linear SVM** and **Logistic
Regression**) typically lead, commonly reaching **~0.90–0.98 weighted F1** on
the synthetic dataset because category-specific vocabulary is highly
discriminative. **Multinomial Naive Bayes** is usually a close, very fast
baseline. **Random Forest** performs well but can trail the linear models
slightly on very high-dimensional sparse TF-IDF features. The definitive
ranking for your run is whatever `train.py` reports — the dashboard sorts
models by weighted F1 and highlights the winner.

### 5.3 Comparison graphs

Training generates the following into `outputs/` (shown in the Model
Dashboard):

- `model_comparison_bars.png` — grouped bar chart of all four metrics across
  all four models.
- `metric_accuracy.png`, `metric_precision_weighted.png`,
  `metric_recall_weighted.png`, `metric_f1_weighted.png` — one chart per
  metric.
- `f1_ranking.png` — horizontal ranking of models by weighted F1.
- `metrics_heatmap.png` — model × metric heatmap.
- `confusion_<model>.png` — a confusion matrix per model.

---

## 6. System Architecture

```
        ┌────────────────┐      ┌──────────────────┐
        │  data_loader   │─────▶│  resume_dataset  │
        │ (download/gen) │      │      .csv        │
        └────────────────┘      └────────┬─────────┘
                                         │
                              ┌──────────▼──────────┐
                              │   preprocessing +   │
                              │   TF-IDF vectorizer │
                              └──────────┬──────────┘
                                         │
             ┌───────────────┬───────────┼───────────┬──────────────┐
             ▼               ▼           ▼           ▼              │
        Linear SVM     Logistic Reg.  Random F.   Multinomial NB    │
             └───────────────┴───────────┼───────────┴──────────────┘
                                         │
                        ┌────────────────▼────────────────┐
                        │  metrics.csv/json + graphs (PNG) │
                        └────────────────┬────────────────┘
                                         │
                              ┌──────────▼──────────┐
                              │  Streamlit UI (app) │
                              │ rank · classify ·   │
                              │ dashboard           │
                              └─────────────────────┘
```

---

## 7. How to Run

```bash
pip install -r requirements.txt   # install dependencies
python train.py                   # build dataset, train 4 models, make graphs
streamlit run app.py              # launch the professional UI
```

See `README.md` for full details, flags, and troubleshooting.

---

## 8. Limitations & Future Work

- **Synthetic data** (fallback mode) is realistic but simpler than messy
  real-world resumes; when a public dataset downloads successfully, metrics
  reflect real text.
- **TF-IDF** captures lexical overlap, not deep semantics. A future version
  could add **sentence-transformer embeddings** for semantic matching.
- Ranking weights (70/30) are configurable in `src/ranking.py` and could be
  learned from recruiter feedback.
- Potential extensions: named-entity extraction (years of experience,
  education level), bias/fairness auditing, and batch scoring of large resume
  folders.

---

## 9. Conclusion

The project delivers a complete, reproducible resume-screening and
candidate-ranking system: a robust data pipeline, four trained and compared
classifiers evaluated on Accuracy/Precision/Recall/F1 with comparison graphs,
an interpretable ranking engine, and a professional Streamlit interface. It
runs end-to-end with two commands and requires no external accounts or data
thanks to the synthetic-dataset fallback.
