"""
Automated terminal runner to screen the 15 demo PDFs against the demo Job Description PDF.
Useful for quick verification or command-line demonstrations.
"""
from pathlib import Path
import pdfplumber
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from src.matching_engine import MatchingEngine
from src.preprocessing import extract_skills_from_text

def run_demo():
    print("=" * 80)
    print("RESUME SCREENING & CANDIDATE CLASSIFICATION SYSTEM - LIVE PDF DEMO")
    print("=" * 80)

    engine = MatchingEngine(auto_load=True)
    folder = PROJECT_ROOT / "sample_resumes"

    jd_path = folder / "Job_Description_Full_Stack_Engineer.pdf"
    if not jd_path.exists():
        print(f"Error: {jd_path} not found.")
        return

    print(f"\n[1] Parsing Target Job Description: {jd_path.name}")
    with pdfplumber.open(jd_path) as pdf:
        jd_raw = "\n".join(page.extract_text() or "" for page in pdf.pages)

    req_skills = ["Python", "JavaScript", "REST APIs", "SQL", "Git", "OOP", "Databases"]
    pref_skills = ["Docker", "CI/CD", "Unit Testing", "Agile", "Scrum", "Problem Solving"]

    print(f"    Required Skills : {', '.join(req_skills)}")
    print(f"    Preferred Skills: {', '.join(pref_skills)}")

    resume_files = sorted([p for p in folder.glob("*.pdf") if p.name != jd_path.name])
    print(f"\n[2] Ingesting and Screening {len(resume_files)} Candidate Resumes...")

    results = []
    for p in resume_files:
        with pdfplumber.open(p) as pdf:
            raw_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        skills = sorted(list(extract_skills_from_text(raw_text, engine.skills_vocab)))
        gap = engine.compute_skill_gap(skills, req_skills, pref_skills)
        text_sim = engine.compute_text_similarity(raw_text, jd_raw)
        overall = (0.55 * gap["skill_score"]) + (0.45 * text_sim)

        if overall >= 80:
            cls = "Top Tier Match"
        elif overall >= 65:
            cls = "Strong Candidate"
        elif overall >= 45:
            cls = "Moderate Fit"
        else:
            cls = "Low Match / Significant Gap"

        results.append({
            "filename": p.name,
            "overall": round(overall, 2),
            "skill_score": round(gap["skill_score"], 1),
            "text_sim": round(text_sim, 1),
            "classification": cls,
            "matched_skills": gap["all_matched_skills"],
            "missing_required": gap["missing_required"],
        })

    results.sort(key=lambda x: x["overall"], reverse=True)

    print("\n" + "=" * 90)
    print(f"{'Rank':<4} {'Match':<8} {'Skill%':<8} {'Text%':<8} {'Classification':<26} {'Candidate File'}")
    print("-" * 90)
    for i, r in enumerate(results, 1):
        print(f"{i:<4} {r['overall']:>5.1f}%  {r['skill_score']:>5.1f}%  {r['text_sim']:>5.1f}%  {r['classification']:<26} {r['filename']}")
    print("=" * 90)

if __name__ == "__main__":
    run_demo()
