"""
Project Health Check & Verification Script for Candidate-Job Matching System.

Verifies:
  1. Python environment and core package dependencies.
  2. Synthetic dataset artifacts & profile in data/.
  3. Matching engine artifacts (vectorizer, skills vocab, precomputed matrix).
  4. Benchmark evaluation outputs and visualization charts in outputs/.
  5. Live candidate-job ranking & skill gap analysis.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import config


def print_step(title: str):
    print(f"\n[CHECK] {title}")


def run_checks() -> bool:
    all_passed = True

    # 1. Environment & Packages
    print_step("Verifying installed Python packages...")
    packages = {
        "sklearn": "scikit-learn",
        "pandas": "pandas",
        "numpy": "numpy",
        "joblib": "joblib",
        "matplotlib": "matplotlib",
        "flask": "flask",
        "flask_cors": "flask-cors",
        "docx": "python-docx",
        "pdfplumber": "pdfplumber",
        "datasets": "datasets",
    }
    missing_pkgs = []
    for mod, display in packages.items():
        try:
            __import__(mod)
            print(f"  + {display}: OK")
        except ImportError:
            print(f"  x {display}: MISSING")
            missing_pkgs.append(display)

    if missing_pkgs:
        print(f"  [ERROR] Missing packages: {', '.join(missing_pkgs)}")
        all_passed = False
    else:
        print("  All essential libraries are installed.")

    # 2. Dataset Check (CSV Format: Raw & Processed)
    print_step(f"Verifying {config.DATASET_NAME} (CSV Format)...")
    required_data = [
        config.DATASET_PROFILE_JSON,
        config.RAW_RESUMES_FILE,
        config.RAW_JOBS_FILE,
        config.RAW_MATCHES_FILE,
        config.CANDIDATES_FILE,
        config.JOBS_FILE,
        config.MATCHES_FILE,
    ]
    for df_path in required_data:
        if df_path.exists() and df_path.stat().st_size > 0:
            print(f"  + Found CSV/Dataset artifact: {df_path.relative_to(config.PROJECT_ROOT)}")
        else:
            print(f"  x Missing: {df_path.relative_to(config.PROJECT_ROOT) if df_path.is_relative_to(config.PROJECT_ROOT) else df_path.name}")
            all_passed = False

    if config.DATASET_PROFILE_JSON.exists():
        with open(config.DATASET_PROFILE_JSON, "r", encoding="utf-8") as f:
            profile = json.load(f)
        stats = profile.get("summary_statistics", {})
        ds_name = profile.get("dataset_name", config.DATASET_NAME)
        fmt = profile.get("format", "CSV")
        print(f"  + Dataset: {ds_name} [{fmt}]")
        print(f"  + Profile Stats: {stats.get('total_resumes')} Resumes, {stats.get('total_jobs')} Jobs, {stats.get('total_candidate_job_relationships')} Relationships")

    # 3. Matching Engine Artifacts
    print_step("Verifying matching engine artifacts in models/...")
    engine_artifacts = [
        config.SKILLS_VOCAB_PATH,
        config.VECTORIZER_PATH,
        config.CANDIDATE_TFIDF_MATRIX_PATH,
    ]
    for art in engine_artifacts:
        if art.exists() and art.stat().st_size > 0:
            print(f"  + Found: {art.name}")
        else:
            print(f"  x Missing: {art.name}")
            all_passed = False

    # 4. Outputs & Visualizations
    print_step("Verifying benchmark outputs in outputs/...")
    bench_outputs = [
        config.BENCHMARK_JSON,
        config.OUTPUTS_DIR / "retrieval_metrics_bars.png",
        config.OUTPUTS_DIR / "score_distribution.png",
    ]
    for out in bench_outputs:
        if out.exists() and out.stat().st_size > 0:
            print(f"  + Found: {out.name}")
        else:
            print(f"  x Missing: {out.name}")
            all_passed = False

    # 5. Live Inference & Skill Gap Verification
    print_step("Running live candidate-job matching & ranking test...")
    try:
        from src.matching_engine import MatchingEngine
        engine = MatchingEngine(auto_load=True)

        sample_job = {
            "job_id": "TEST_JOB",
            "job_title": "Data Scientist",
            "job_text": "We need a Data Scientist with Python, Machine Learning, SQL, and Pandas.",
            "clean_job_text": "data scientist python machine learning sql pandas",
            "required_skills": ["Python", "Machine Learning", "SQL"],
            "preferred_skills": ["Docker", "Pandas"],
        }
        ranked = engine.rank_candidates_for_job(job_dict=sample_job, top_k=5)
        assert not ranked.empty, "Ranking returned empty DataFrame"
        top_cand = ranked.iloc[0]
        print(f"  + Live ranking passed! Top candidate: {top_cand['candidate_id']} ({top_cand['role']})")
        print(f"    Match Score: {top_cand['overall_score']:.1f}% | Skill Score: {top_cand['skill_score']:.1f}% | Text Sim: {top_cand['text_score']:.1f}%")

        # 1-on-1 match verification
        deep_match = engine.match_single_pair(
            resume_text="Senior ML engineer with Python, Machine Learning, and SQL.",
            job_text=sample_job["job_text"],
            candidate_skills=["Python", "Machine Learning", "SQL"],
            required_skills=sample_job["required_skills"],
            preferred_skills=sample_job["preferred_skills"],
        )
        assert deep_match["overall_match_score"] > 0, "Deep match score invalid"
        print(f"  + Live 1-on-1 match passed! Overall Score: {deep_match['overall_match_score']:.1f}%")
        print(f"    Matched Skills: {deep_match['gap_analysis']['matched_required']}")
        print(f"    Missing Preferred: {deep_match['gap_analysis']['missing_preferred']}")

    except Exception as e:
        print(f"  x Live matching verification failed: {e}")
        all_passed = False

    return all_passed


def main():
    print("=" * 65)
    print(" RESUME SCREENING & CANDIDATE-JOB MATCHING: HEALTH CHECK")
    print("=" * 65)
    success = run_checks()
    print("\n" + "=" * 65)
    if success:
        print(" STATUS: [ALL SYSTEMS OPERATIONAL] Everything is working properly!")
        print("=" * 65)
        return 0
    else:
        print(" STATUS: [ATTENTION REQUIRED] One or more components need setup.")
        print("=" * 65)
        return 1


if __name__ == "__main__":
    sys.exit(main())
