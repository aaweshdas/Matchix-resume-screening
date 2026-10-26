"""
Matching Engine for Resume <-> Job Description Matching.

Implements:
  1. Skill Extraction & Normalization
  2. Skill Matching (Required & Preferred skills coverage)
  3. Text Similarity (TF-IDF sublinear unigram+bigram cosine similarity)
  4. Overall Match Scoring (Blended multi-objective score)
  5. Skill Gap Analysis (Matched, Missing Required, Missing Preferred)
  6. High-throughput Candidate Ranking
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import config
from src.preprocessing import clean_text, extract_skills_from_text, to_string_list


class MatchingEngine:
    def __init__(self, auto_load: bool = True):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.skills_vocab: list[str] = []
        self.candidates_df: Optional[pd.DataFrame] = None
        self.jobs_df: Optional[pd.DataFrame] = None
        self.matches_df: Optional[pd.DataFrame] = None
        self.candidate_tfidf_matrix = None

        if auto_load:
            self.load_or_initialize()

    def load_or_initialize(self, force_retrain: bool = False) -> None:
        """Load normalized datasets, skill vocabulary, and vectorizer."""
        from src.data_loader import load_processed_data

        c_df, j_df, m_df, vocab = load_processed_data()
        self.candidates_df = c_df
        self.jobs_df = j_df
        self.matches_df = m_df
        self.skills_vocab = vocab

        # Check if vectorizer & candidate matrix exist
        if (
            not force_retrain
            and config.VECTORIZER_PATH.exists()
            and config.CANDIDATE_TFIDF_MATRIX_PATH.exists()
        ):
            self.vectorizer = joblib.load(config.VECTORIZER_PATH)
            self.candidate_tfidf_matrix = joblib.load(config.CANDIDATE_TFIDF_MATRIX_PATH)
        else:
            self.train_vectorizer()

    def train_vectorizer(self) -> None:
        """Fit TF-IDF vectorizer on combined corpus of resumes and job descriptions."""
        print("[matching_engine] Training TF-IDF vectorizer on corpus...")
        all_texts = list(self.candidates_df["clean_resume_text"]) + list(self.jobs_df["clean_job_text"])

        self.vectorizer = TfidfVectorizer(
            max_features=config.TFIDF_MAX_FEATURES,
            ngram_range=config.TFIDF_NGRAM_RANGE,
            min_df=config.TFIDF_MIN_DF,
            sublinear_tf=True,
        )
        self.vectorizer.fit(all_texts)
        joblib.dump(self.vectorizer, config.VECTORIZER_PATH)

        # Precompute candidate matrix
        print("[matching_engine] Precomputing candidate TF-IDF matrix (10,000 resumes)...")
        self.candidate_tfidf_matrix = self.vectorizer.transform(self.candidates_df["clean_resume_text"])
        joblib.dump(self.candidate_tfidf_matrix, config.CANDIDATE_TFIDF_MATRIX_PATH)
        print("[matching_engine] Vectorizer and candidate matrix persisted.")

    def compute_skill_gap(
        self,
        candidate_skills: Iterable[str],
        required_skills: Iterable[str],
        preferred_skills: Optional[Iterable[str]] = None,
        must_have_weight: float = config.DEFAULT_MUST_HAVE_WEIGHT,
        nice_to_have_weight: float = config.DEFAULT_NICE_TO_HAVE_WEIGHT,
    ) -> Dict[str, Any]:
        """Compute matched/missing skills and the weighted skill coverage score (0-100)."""
        cand_set = {s.lower().strip() for s in to_string_list(candidate_skills) if s.strip()}
        req_list = [s.strip() for s in to_string_list(required_skills) if s.strip()]
        pref_list = [s.strip() for s in to_string_list(preferred_skills) if s.strip()] if preferred_skills else []

        matched_req = [s for s in req_list if s.lower() in cand_set]
        missing_req = [s for s in req_list if s.lower() not in cand_set]

        matched_pref = [s for s in pref_list if s.lower() in cand_set]
        missing_pref = [s for s in pref_list if s.lower() not in cand_set]

        # Coverage calculations
        req_coverage = (len(matched_req) / len(req_list)) if req_list else 1.0
        pref_coverage = (len(matched_pref) / len(pref_list)) if pref_list else 1.0

        if req_list and pref_list:
            total_weight = must_have_weight + nice_to_have_weight
            skill_score = ((must_have_weight * req_coverage) + (nice_to_have_weight * pref_coverage)) / total_weight * 100.0
        elif req_list:
            skill_score = req_coverage * 100.0
        elif pref_list:
            skill_score = pref_coverage * 100.0
        else:
            skill_score = 100.0

        return {
            "skill_score": round(float(skill_score), 2),
            "required_coverage_pct": round(float(req_coverage * 100), 2),
            "preferred_coverage_pct": round(float(pref_coverage * 100), 2),
            "matched_required": matched_req,
            "missing_required": missing_req,
            "matched_preferred": matched_pref,
            "missing_preferred": missing_pref,
            "all_matched_skills": sorted(list(set(matched_req + matched_pref))),
        }

    def compute_text_similarity(self, resume_text: str, job_text: str) -> float:
        """Compute TF-IDF cosine similarity score between resume text and job text (0-100)."""
        c_clean = clean_text(resume_text)
        j_clean = clean_text(job_text)
        if not c_clean or not j_clean:
            return 0.0

        vecs = self.vectorizer.transform([c_clean, j_clean])
        sim = cosine_similarity(vecs[0], vecs[1])[0][0]
        return round(float(np.clip(sim, 0.0, 1.0)) * 100.0, 2)

    def match_single_pair(
        self,
        resume_text: str,
        job_text: str,
        candidate_skills: Iterable[str],
        required_skills: Iterable[str],
        preferred_skills: Optional[Iterable[str]] = None,
        skill_weight: float = config.DEFAULT_SKILL_WEIGHT,
        text_weight: float = config.DEFAULT_TEXT_WEIGHT,
    ) -> Dict[str, Any]:
        """Deep 1-on-1 match evaluation between a single resume and a single job description."""
        # 1. Skill Analysis
        gap = self.compute_skill_gap(candidate_skills, required_skills, preferred_skills)

        # 2. Text Similarity
        text_sim = self.compute_text_similarity(resume_text, job_text)

        # 3. Blended Overall Match Score
        norm_skill_wt = skill_weight / (skill_weight + text_weight)
        norm_text_wt = text_weight / (skill_weight + text_weight)
        overall = (norm_skill_wt * gap["skill_score"]) + (norm_text_wt * text_sim)

        return {
            "overall_match_score": round(float(overall), 2),
            "skill_score": gap["skill_score"],
            "text_similarity_score": text_sim,
            "skill_weight": round(norm_skill_wt, 2),
            "text_weight": round(norm_text_wt, 2),
            "gap_analysis": gap,
        }

    def rank_candidates_for_job(
        self,
        job_id: Optional[str] = None,
        job_dict: Optional[Dict[str, Any]] = None,
        top_k: int = 50,
        skill_weight: float = config.DEFAULT_SKILL_WEIGHT,
        text_weight: float = config.DEFAULT_TEXT_WEIGHT,
        must_have_weight: float = config.DEFAULT_MUST_HAVE_WEIGHT,
        nice_to_have_weight: float = config.DEFAULT_NICE_TO_HAVE_WEIGHT,
        role_filter: Optional[str] = None,
        seniority_filter: Optional[str] = None,
        industry_filter: Optional[str] = None,
        candidate_subset: Optional[pd.DataFrame] = None,
    ) -> pd.DataFrame:
        """Rank candidates against a job description.

        Accepts either an existing `job_id` from the dataset OR a custom `job_dict`.
        """
        # Resolve Job parameters
        if job_id and self.jobs_df is not None:
            job_rows = self.jobs_df[self.jobs_df["job_id"] == job_id]
            if job_rows.empty:
                raise ValueError(f"Job ID '{job_id}' not found in jobs dataset.")
            job_data = job_rows.iloc[0].to_dict()
        elif job_dict:
            job_data = job_dict
        else:
            raise ValueError("Either job_id or job_dict must be provided.")

        job_clean_text = job_data.get("clean_job_text") or clean_text(job_data.get("job_text", ""))
        req_skills = to_string_list(job_data.get("required_skills", []))
        pref_skills = to_string_list(job_data.get("preferred_skills", []))

        # Filter candidate pool
        pool_df = candidate_subset if candidate_subset is not None else self.candidates_df
        filtered_df = pool_df.copy()

        if role_filter and role_filter != "All":
            filtered_df = filtered_df[filtered_df["role"] == role_filter]
        if seniority_filter and seniority_filter != "All":
            filtered_df = filtered_df[filtered_df["seniority"] == seniority_filter]
        if industry_filter and industry_filter != "All":
            filtered_df = filtered_df[filtered_df["industry"] == industry_filter]

        if filtered_df.empty:
            return pd.DataFrame()

        # Vectorized Text Similarity
        job_vec = self.vectorizer.transform([job_clean_text])
        if candidate_subset is None and filtered_df.index.equals(self.candidates_df.index):
            pool_vecs = self.candidate_tfidf_matrix
        else:
            pool_vecs = self.vectorizer.transform(filtered_df["clean_resume_text"])

        cos_sims = cosine_similarity(pool_vecs, job_vec).flatten()
        cos_sims = np.clip(cos_sims, 0.0, 1.0) * 100.0

        # Vectorized / Fast Skill Matching
        norm_skill_wt = skill_weight / (skill_weight + text_weight)
        norm_text_wt = text_weight / (skill_weight + text_weight)

        req_set = {s.lower().strip() for s in req_skills if s.strip()}
        pref_set = {s.lower().strip() for s in pref_skills if s.strip()}

        rows = []
        for i, (_, cand) in enumerate(filtered_df.iterrows()):
            cand_skills = cand.get("skills_normalized", [s.lower() for s in cand.get("skills", [])])
            cand_set = set(cand_skills)

            # Matched & Missing
            matched_req = [s for s in req_skills if s.lower() in cand_set]
            missing_req = [s for s in req_skills if s.lower() not in cand_set]
            matched_pref = [s for s in pref_skills if s.lower() in cand_set]
            missing_pref = [s for s in pref_skills if s.lower() not in cand_set]

            req_cov = (len(matched_req) / len(req_skills)) if req_skills else 1.0
            pref_cov = (len(matched_pref) / len(pref_skills)) if pref_skills else 1.0

            if req_skills and pref_skills:
                total_w = must_have_weight + nice_to_have_weight
                skill_score = ((must_have_weight * req_cov) + (nice_to_have_weight * pref_cov)) / total_w * 100.0
            elif req_skills:
                skill_score = req_cov * 100.0
            elif pref_skills:
                skill_score = pref_cov * 100.0
            else:
                skill_score = 100.0

            t_score = cos_sims[i]
            overall_score = (norm_skill_wt * skill_score) + (norm_text_wt * t_score)

            rows.append({
                "candidate_id": cand["candidate_id"],
                "role": cand.get("role", ""),
                "seniority": cand.get("seniority", ""),
                "years_experience": cand.get("years_experience", 0),
                "industry": cand.get("industry", ""),
                "education": cand.get("education", ""),
                "overall_score": round(float(overall_score), 2),
                "skill_score": round(float(skill_score), 2),
                "text_score": round(float(t_score), 2),
                "matched_required": matched_req,
                "missing_required": missing_req,
                "matched_preferred": matched_pref,
                "missing_preferred": missing_pref,
                "resume_text": cand.get("resume_text", ""),
            })

        results_df = pd.DataFrame(rows).sort_values("overall_score", ascending=False).reset_index(drop=True)
        results_df.insert(0, "rank", range(1, len(results_df) + 1))

        if top_k is not None and top_k > 0:
            results_df = results_df.head(top_k)

        return results_df
