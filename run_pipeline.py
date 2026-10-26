"""
Quickstart runner: builds the dataset, trains all models, and generates
graphs in one step. Equivalent to running `python train.py`, but with a
friendlier console banner and dependency check.

Usage:  python run_pipeline.py
"""
import importlib
import subprocess
import sys


REQUIRED = ["sklearn", "pandas", "numpy", "matplotlib", "joblib"]


def check_deps():
    missing = []
    for mod in REQUIRED:
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(mod)
    if missing:
        print("Missing required packages:", ", ".join(missing))
        print("Install everything with:\n    pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 70)
    print(" RESUME SCREENING & CANDIDATE RANKING — FULL PIPELINE")
    print("=" * 70)
    check_deps()
    # Import here so the dependency check runs first with a clean message.
    from train import main
    main()
    print("\nNext step: launch the MATCHIX Full-Stack Web Application with:")
    print("    run.bat               (Interactive Launcher)")
    print("    run_fullstack.bat     (Direct Full-Stack Launch: Flask + Vite React)")
    print("    python server.py      (Backend REST API on http://localhost:5000)")

