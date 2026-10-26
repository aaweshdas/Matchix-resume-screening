"""
Data Loader & Normalization Pipeline for MIRRA Resume-Job Matching Dataset.

Loads the MIRRA Resume-Job Matching Dataset in CSV format (both raw and processed),
normalizes resumes and jobs into internal representations, extracts the skill vocabulary,
and provides access to candidate, job, and ground-truth match records.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Tuple

import pandas as pd
from huggingface_hub import hf_hub_download

import config
from src.preprocessing import (
    build_candidate_representation,
    build_job_representation,
    to_string_list,
)


def ensure_raw_dataset() -> None:
    """Ensure raw CSV files are available. If not, download and convert from Hugging Face."""
    if (
        config.RAW_RESUMES_FILE.exists()
        and config.RAW_JOBS_FILE.exists()
        and config.RAW_MATCHES_FILE.exists()
    ):
        return

    print("[data_loader] Raw CSV files not found. Fetching source data from Hugging Face...")
    raw_targets = {
        "resumes": ("resumes/train-00000-of-00001.parquet", config.RAW_RESUMES_FILE),
        "jobs": ("jobs/train-00000-of-00001.parquet", config.RAW_JOBS_FILE),
        "matches": ("matches/train-00000-of-00001.parquet", config.RAW_MATCHES_FILE),
    }
    for category, (remote_file, local_csv) in raw_targets.items():
        if not local_csv.exists():
            print(f"[data_loader] Fetching {remote_file} for {local_csv.name}...")
            temp_pqt = hf_hub_download(
                repo_id="michaelozon/candidate-matching-synthetic",
                filename=remote_file,
                repo_type="dataset",
                local_dir=config.RAW_DATA_DIR,
            )
            df = pd.read_parquet(temp_pqt)
            local_csv.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(local_csv, index=False)
            print(f"[data_loader] Converted and saved {local_csv} ({len(df)} rows)")


def load_raw_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load raw resumes, jobs, and matches CSV files."""
    ensure_raw_dataset()
    resumes_df = pd.read_csv(config.RAW_RESUMES_FILE)
    jobs_df = pd.read_csv(config.RAW_JOBS_FILE)
    matches_df = pd.read_csv(config.RAW_MATCHES_FILE)

    # Parse list columns from raw CSV
    if "skills" in resumes_df.columns:
        resumes_df["skills"] = resumes_df["skills"].apply(to_string_list)
    if "experience_bullets" in resumes_df.columns:
        resumes_df["experience_bullets"] = resumes_df["experience_bullets"].apply(to_string_list)

    if "must_have_skills" in jobs_df.columns:
        jobs_df["must_have_skills"] = jobs_df["must_have_skills"].apply(to_string_list)
    if "nice_to_have_skills" in jobs_df.columns:
        jobs_df["nice_to_have_skills"] = jobs_df["nice_to_have_skills"].apply(to_string_list)
    if "responsibilities" in jobs_df.columns:
        jobs_df["responsibilities"] = jobs_df["responsibilities"].apply(to_string_list)
    if "requirements" in jobs_df.columns:
        jobs_df["requirements"] = jobs_df["requirements"].apply(to_string_list)

    if "relevant_resume_ids" in matches_df.columns:
        matches_df["relevant_resume_ids"] = matches_df["relevant_resume_ids"].apply(to_string_list)

    return resumes_df, jobs_df, matches_df


def extract_skill_lexicon(resumes_df: pd.DataFrame, jobs_df: pd.DataFrame) -> list[str]:
    """Extract full distinct list of skills across resumes and jobs."""
    skills = set()
    for s_arr in resumes_df["skills"]:
        if hasattr(s_arr, "__iter__"):
            skills.update([str(x).strip() for x in s_arr if str(x).strip()])
    for s_arr in jobs_df["must_have_skills"]:
        if hasattr(s_arr, "__iter__"):
            skills.update([str(x).strip() for x in s_arr if str(x).strip()])
    for s_arr in jobs_df["nice_to_have_skills"]:
        if hasattr(s_arr, "__iter__"):
            skills.update([str(x).strip() for x in s_arr if str(x).strip()])
    return sorted(list(skills))


def _deserialize_processed_dfs(
    candidates_df: pd.DataFrame, jobs_df: pd.DataFrame, matches_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Deserialize JSON string lists back to Python lists after CSV load."""
    if "skills" in candidates_df.columns:
        candidates_df["skills"] = candidates_df["skills"].apply(to_string_list)
    if "skills_normalized" in candidates_df.columns:
        candidates_df["skills_normalized"] = candidates_df["skills_normalized"].apply(to_string_list)

    if "required_skills" in jobs_df.columns:
        jobs_df["required_skills"] = jobs_df["required_skills"].apply(to_string_list)
    if "preferred_skills" in jobs_df.columns:
        jobs_df["preferred_skills"] = jobs_df["preferred_skills"].apply(to_string_list)
    if "required_skills_normalized" in jobs_df.columns:
        jobs_df["required_skills_normalized"] = jobs_df["required_skills_normalized"].apply(to_string_list)
    if "preferred_skills_normalized" in jobs_df.columns:
        jobs_df["preferred_skills_normalized"] = jobs_df["preferred_skills_normalized"].apply(to_string_list)

    if "relevant_resume_ids" in matches_df.columns:
        matches_df["relevant_resume_ids"] = matches_df["relevant_resume_ids"].apply(to_string_list)

    return candidates_df, jobs_df, matches_df


def build_and_save_normalized(force: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    """Normalize raw data into candidates, jobs, and ground truth matches in CSV format."""
    if (
        not force
        and config.CANDIDATES_FILE.exists()
        and config.JOBS_FILE.exists()
        and config.MATCHES_FILE.exists()
        and config.SKILLS_VOCAB_PATH.exists()
    ):
        candidates_df = pd.read_csv(config.CANDIDATES_FILE)
        jobs_df = pd.read_csv(config.JOBS_FILE)
        matches_df = pd.read_csv(config.MATCHES_FILE)
        candidates_df, jobs_df, matches_df = _deserialize_processed_dfs(candidates_df, jobs_df, matches_df)

        with open(config.SKILLS_VOCAB_PATH, "r", encoding="utf-8") as f:
            skills_vocab = json.load(f)
        return candidates_df, jobs_df, matches_df, skills_vocab

    print("[data_loader] Processing raw data into normalized representations (CSV)...")
    raw_resumes, raw_jobs, raw_matches = load_raw_data()

    # 1. Normalize Candidates
    candidate_records = []
    for _, row in raw_resumes.iterrows():
        candidate_records.append(
            build_candidate_representation(
                resume_id=str(row["resume_id"]).strip(),
                summary=row.get("summary", ""),
                experience_bullets=row.get("experience_bullets", []),
                skills=row.get("skills", []),
                role=row.get("role", ""),
                seniority=row.get("seniority", ""),
                years_experience=row.get("years_experience", 0),
                industry=row.get("industry", ""),
                education=row.get("education", ""),
            )
        )
    candidates_df = pd.DataFrame(candidate_records)

    # 2. Normalize Jobs
    job_records = []
    for _, row in raw_jobs.iterrows():
        job_records.append(
            build_job_representation(
                job_id=str(row["job_id"]).strip(),
                job_title=row.get("job_title", ""),
                description=row.get("description", ""),
                responsibilities=row.get("responsibilities", []),
                requirements=row.get("requirements", []),
                must_have_skills=row.get("must_have_skills", []),
                nice_to_have_skills=row.get("nice_to_have_skills", []),
                seniority=row.get("seniority", ""),
                industry=row.get("industry", ""),
            )
        )
    jobs_df = pd.DataFrame(job_records)

    # 3. Ground Truth Matches
    matches_records = []
    for _, row in raw_matches.iterrows():
        r_ids = to_string_list(row.get("relevant_resume_ids", []))
        matches_records.append({
            "job_id": str(row["job_id"]).strip(),
            "relevant_resume_ids": json.dumps(r_ids),
            "relevant_count": len(r_ids),
        })
    matches_df = pd.DataFrame(matches_records)

    # 4. Extract Skills Lexicon
    skills_vocab = extract_skill_lexicon(raw_resumes, raw_jobs)
    with open(config.SKILLS_VOCAB_PATH, "w", encoding="utf-8") as f:
        json.dump(skills_vocab, f, indent=2)

    # Serialize list columns to JSON strings for CSV storage
    candidates_df_to_save = candidates_df.copy()
    candidates_df_to_save["skills"] = candidates_df_to_save["skills"].apply(json.dumps)
    candidates_df_to_save["skills_normalized"] = candidates_df_to_save["skills_normalized"].apply(json.dumps)

    jobs_df_to_save = jobs_df.copy()
    jobs_df_to_save["required_skills"] = jobs_df_to_save["required_skills"].apply(json.dumps)
    jobs_df_to_save["preferred_skills"] = jobs_df_to_save["preferred_skills"].apply(json.dumps)
    jobs_df_to_save["required_skills_normalized"] = jobs_df_to_save["required_skills_normalized"].apply(json.dumps)
    jobs_df_to_save["preferred_skills_normalized"] = jobs_df_to_save["preferred_skills_normalized"].apply(json.dumps)

    # Persist normalized CSVs
    candidates_df_to_save.to_csv(config.CANDIDATES_FILE, index=False)
    jobs_df_to_save.to_csv(config.JOBS_FILE, index=False)
    matches_df.to_csv(config.MATCHES_FILE, index=False)

    print(f"[data_loader] Saved normalized candidates ({len(candidates_df)}) -> {config.CANDIDATES_FILE}")
    print(f"[data_loader] Saved normalized jobs ({len(jobs_df)}) -> {config.JOBS_FILE}")
    print(f"[data_loader] Saved matches ({len(matches_df)}) -> {config.MATCHES_FILE}")
    print(f"[data_loader] Saved skill vocabulary ({len(skills_vocab)} skills) -> {config.SKILLS_VOCAB_PATH}")

    # Return with real python lists in memory
    candidates_df, jobs_df, matches_df = _deserialize_processed_dfs(candidates_df, jobs_df, matches_df)
    return candidates_df, jobs_df, matches_df, skills_vocab


def load_processed_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, list[str]]:
    """Load cached processed data or generate if not present."""
    return build_and_save_normalized(force=False)


if __name__ == "__main__":
    c_df, j_df, m_df, vocab = build_and_save_normalized(force=True)
    print("DataLoader execution completed successfully.")

