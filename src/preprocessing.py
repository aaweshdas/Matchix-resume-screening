"""
NLP Preprocessing and Schema Normalization for Candidate-Job Matching.

Provides:
  - Text normalization & cleaning (URL/email removal, stop-word filtering)
  - Candidate record normalization: (summary + experience_bullets + skills -> resume_text)
  - Job record normalization: (description + responsibilities + requirements -> job_text)
  - Skill extraction from raw text using a predefined or extracted skill lexicon
"""
from __future__ import annotations

import re
from typing import Any, Iterable

import numpy as np
import pandas as pd

# Compact English stop-word list
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "as", "at", "be", "because", "been", "before",
    "being", "below", "between", "both", "but", "by", "can", "did", "do",
    "does", "doing", "don", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers",
    "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is",
    "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no",
    "nor", "not", "now", "of", "off", "on", "once", "only", "or", "other",
    "our", "ours", "ourselves", "out", "over", "own", "s", "same", "she",
    "should", "so", "some", "such", "t", "than", "that", "the", "their",
    "theirs", "them", "themselves", "then", "there", "these", "they", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "we", "were", "what", "when", "where", "which", "while", "who", "whom",
    "why", "will", "with", "you", "your", "yours", "yourself", "yourselves",
}

_URL_RE = re.compile(r"http\S+|www\.\S+")
_EMAIL_RE = re.compile(r"\S+@\S+")
_NON_ALPHA_RE = re.compile(r"[^a-z0-9+#.\s]")
_MULTISPACE_RE = re.compile(r"\s+")
_DIGIT_TOKEN_RE = re.compile(r"\b\d+\b")


def clean_text(text: str) -> str:
    """Normalize a raw string into model-ready text."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = _URL_RE.sub(" ", text)
    text = _EMAIL_RE.sub(" ", text)
    text = _NON_ALPHA_RE.sub(" ", text)
    text = _DIGIT_TOKEN_RE.sub(" ", text)

    tokens = [t for t in text.split() if t not in STOP_WORDS and len(t) > 1]
    return _MULTISPACE_RE.sub(" ", " ".join(tokens)).strip()


def to_string_list(val: Any) -> list[str]:
    """Convert array/list/string into a list of strings."""
    if val is None:
        return []
    if isinstance(val, (list, np.ndarray, tuple, set)):
        return [str(x).strip() for x in val if str(x).strip()]
    if isinstance(val, str):
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            import ast
            try:
                parsed = ast.literal_eval(val)
                return [str(x).strip() for x in parsed if str(x).strip()]
            except Exception:
                pass
        return [s.strip() for s in re.split(r"[,;|/\n]", val) if s.strip()]
    return [str(val).strip()]


def build_candidate_representation(
    resume_id: str,
    summary: str,
    experience_bullets: Any,
    skills: Any,
    role: str = "",
    seniority: str = "",
    years_experience: int = 0,
    industry: str = "",
    education: str = "",
) -> dict[str, Any]:
    """Combine resume attributes into the internal normalized Candidate representation."""
    bullets = to_string_list(experience_bullets)
    skill_list = to_string_list(skills)

    text_parts = []
    if summary and str(summary).strip():
        text_parts.append(str(summary).strip())
    if bullets:
        text_parts.append(" ".join(bullets))
    if skill_list:
        text_parts.append("Key skills: " + ", ".join(skill_list) + ".")

    resume_text = " ".join(text_parts).strip()

    return {
        "candidate_id": str(resume_id).strip(),
        "resume_text": resume_text,
        "clean_resume_text": clean_text(resume_text),
        "skills": skill_list,
        "skills_normalized": [s.lower() for s in skill_list],
        "role": str(role).strip(),
        "seniority": str(seniority).strip(),
        "years_experience": int(years_experience) if str(years_experience).isdigit() else 0,
        "industry": str(industry).strip(),
        "education": str(education).strip(),
    }


def build_job_representation(
    job_id: str,
    job_title: str,
    description: str,
    responsibilities: Any,
    requirements: Any,
    must_have_skills: Any,
    nice_to_have_skills: Any = None,
    seniority: str = "",
    industry: str = "",
) -> dict[str, Any]:
    """Combine job attributes into the internal normalized Job representation."""
    resp_list = to_string_list(responsibilities)
    req_list = to_string_list(requirements)
    must_skills = to_string_list(must_have_skills)
    nice_skills = to_string_list(nice_to_have_skills)

    text_parts = []
    if job_title and str(job_title).strip():
        text_parts.append(f"Job Title: {job_title}.")
    if description and str(description).strip():
        text_parts.append(str(description).strip())
    if resp_list:
        text_parts.append("Responsibilities: " + " ".join(resp_list))
    if req_list:
        text_parts.append("Requirements: " + " ".join(req_list))
    if must_skills:
        text_parts.append("Required Skills: " + ", ".join(must_skills) + ".")
    if nice_skills:
        text_parts.append("Preferred Skills: " + ", ".join(nice_skills) + ".")

    job_text = " ".join(text_parts).strip()

    return {
        "job_id": str(job_id).strip(),
        "job_title": str(job_title).strip(),
        "job_text": job_text,
        "clean_job_text": clean_text(job_text),
        "required_skills": must_skills,
        "preferred_skills": nice_skills,
        "required_skills_normalized": [s.lower() for s in must_skills],
        "preferred_skills_normalized": [s.lower() for s in nice_skills],
        "seniority": str(seniority).strip(),
        "industry": str(industry).strip(),
    }


def extract_skills_from_text(text: str, skill_lexicon: Iterable[str]) -> set[str]:
    """Detect skills from free text using case-insensitive whole-word boundary matching."""
    if not text:
        return set()
    lowered = text.lower()
    found = set()
    for skill in skill_lexicon:
        s_norm = skill.lower().strip()
        if not s_norm:
            continue
        # Use regex boundary matching
        pattern = r"(?<!\w)" + re.escape(s_norm) + r"(?!\w)"
        if re.search(pattern, lowered):
            found.add(skill)
    return found
