"""
Smoke Test for Resume Screening & Candidate-Job Matching System.

Verifies:
  1. All modules import cleanly without error.
  2. Text preprocessing and schema normalization work properly.
  3. Skill gap analysis and coverage scoring produce expected outputs.
  4. Matching engine ranks candidates and computes dual-branch scores.
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))


def check(name: str, fn) -> bool:
    try:
        fn()
        print(f"  [PASS] {name}")
        return True
    except Exception as exc:
        print(f"  [FAIL] {name}: {exc}")
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print(" SMOKE TEST — Candidate-Job Matching System")
    print("=" * 60)
    results = []

    # 1. Module Imports
    def _imports():
        import config  # noqa
        from src import preprocessing, data_loader, matching_engine, benchmark, file_utils  # noqa
    results.append(check("module imports", _imports))

    # 2. Text Preprocessing & Cleaning
    def _preproc():
        from src.preprocessing import clean_text
        out = clean_text("Python, Machine Learning & SQL! Visit http://example.com")
        assert "python" in out and "http" not in out, out
        assert "machine" in out and "sql" in out
    results.append(check("text preprocessing & cleaning", _preproc))

    # 3. Schema Normalization
    def _norm():
        from src.preprocessing import build_candidate_representation, build_job_representation
        cand = build_candidate_representation(
            resume_id="R_TEST",
            summary="Experienced developer",
            experience_bullets=["Built web applications in React", "Managed PostgreSQL databases"],
            skills=["React", "PostgreSQL", "JavaScript"],
            role="Web Developer",
        )
        assert cand["candidate_id"] == "R_TEST"
        assert "React" in cand["resume_text"]
        assert "react" in cand["clean_resume_text"]

        job = build_job_representation(
            job_id="J_TEST",
            job_title="Frontend Engineer",
            description="Looking for Frontend Engineer",
            responsibilities=["Develop UI in React"],
            requirements=["2+ years experience"],
            must_have_skills=["React", "JavaScript"],
            nice_to_have_skills=["TypeScript"],
        )
        assert job["job_id"] == "J_TEST"
        assert "React" in job["job_text"]
        assert "react" in job["required_skills_normalized"]
    results.append(check("schema normalization (Candidate & Job)", _norm))

    # 4. Skill Gap Analysis
    def _skill_gap():
        from src.matching_engine import MatchingEngine
        engine = MatchingEngine(auto_load=True)
        gap = engine.compute_skill_gap(
            candidate_skills=["Python", "SQL", "Pandas", "Docker"],
            required_skills=["Python", "SQL", "Machine Learning"],
            preferred_skills=["Docker", "AWS"],
        )
        assert "Python" in gap["matched_required"]
        assert "Machine Learning" in gap["missing_required"]
        assert "Docker" in gap["matched_preferred"]
        assert "AWS" in gap["missing_preferred"]
        assert 0.0 < gap["skill_score"] < 100.0
    results.append(check("skill gap analysis & scoring", _skill_gap))

    # 5. End-to-End Candidate Ranking
    def _ranking():
        from src.matching_engine import MatchingEngine
        engine = MatchingEngine(auto_load=True)
        ranked = engine.rank_candidates_for_job(job_id=engine.jobs_df.iloc[0]["job_id"], top_k=5)
        assert len(ranked) == 5
        assert "overall_score" in ranked.columns
        assert ranked.iloc[0]["overall_score"] >= ranked.iloc[1]["overall_score"]
    results.append(check("end-to-end candidate ranking", _ranking))

    print("-" * 60)
    passed = sum(results)
    print(f" {passed}/{len(results)} checks passed.")
    print("=" * 60)
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
