"""
Benchmark & Ground-Truth Evaluation for Candidate-Job Matching.

Evaluates the MatchingEngine against the 75,000 ground-truth relationships
(2,500 jobs x 30 relevant candidates) from the synthetic dataset.

Computes:
  - Precision@10, Precision@30
  - Recall@10, Recall@30, Recall@50, Recall@100
  - Mean Reciprocal Rank (MRR)
  - Mean Average Precision (MAP)
Generates:
  - outputs/matching_benchmark.json
  - outputs/matching_benchmark.csv
  - outputs/retrieval_metrics_bars.png
  - outputs/score_distribution.png
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config
from src.matching_engine import MatchingEngine


def compute_ap(retrieved_ids: List[str], relevant_set: set[str], k: int = 30) -> float:
    """Compute Average Precision at K."""
    hits = 0
    sum_precisions = 0.0
    for i, cid in enumerate(retrieved_ids[:k], start=1):
        if cid in relevant_set:
            hits += 1
            sum_precisions += hits / i
    return sum_precisions / min(len(relevant_set), k) if relevant_set else 0.0


def evaluate_retrieval(
    engine: MatchingEngine,
    num_jobs_to_eval: int = 100,
    top_k_retrieve: int = 100,
) -> Dict[str, float]:
    """Run evaluation over a representative sample of jobs."""
    print(f"\n[benchmark] Starting retrieval evaluation on {num_jobs_to_eval} jobs...")
    t0 = time.time()

    matches_df = engine.matches_df
    # Sample jobs reproducibly
    sample_jobs = matches_df.sample(n=min(num_jobs_to_eval, len(matches_df)), random_state=config.RANDOM_STATE)

    recalls_10 = []
    recalls_30 = []
    recalls_50 = []
    recalls_100 = []
    precisions_10 = []
    precisions_30 = []
    mrrs = []
    maps_30 = []

    for idx, row in sample_jobs.iterrows():
        jid = row["job_id"]
        rel_set = set(row["relevant_resume_ids"])
        total_rel = len(rel_set)

        ranked = engine.rank_candidates_for_job(job_id=jid, top_k=top_k_retrieve)
        retrieved_ids = list(ranked["candidate_id"])

        # Metrics
        hits_10 = len(set(retrieved_ids[:10]) & rel_set)
        hits_30 = len(set(retrieved_ids[:30]) & rel_set)
        hits_50 = len(set(retrieved_ids[:50]) & rel_set)
        hits_100 = len(set(retrieved_ids[:100]) & rel_set)

        recalls_10.append(hits_10 / total_rel if total_rel else 0.0)
        recalls_30.append(hits_30 / total_rel if total_rel else 0.0)
        recalls_50.append(hits_50 / total_rel if total_rel else 0.0)
        recalls_100.append(hits_100 / total_rel if total_rel else 0.0)

        precisions_10.append(hits_10 / 10.0)
        precisions_30.append(hits_30 / 30.0)

        # Reciprocal Rank of first relevant candidate
        rr = 0.0
        for rank_pos, cid in enumerate(retrieved_ids, start=1):
            if cid in rel_set:
                rr = 1.0 / rank_pos
                break
        mrrs.append(rr)

        # MAP@30
        maps_30.append(compute_ap(retrieved_ids, rel_set, k=30))

    elapsed = time.time() - t0

    metrics = {
        "num_evaluated_jobs": len(sample_jobs),
        "total_ground_truth_relationships": 75000,
        "relevant_per_job": 30,
        "precision_at_10": round(float(np.mean(precisions_10)), 4),
        "precision_at_30": round(float(np.mean(precisions_30)), 4),
        "recall_at_10": round(float(np.mean(recalls_10)), 4),
        "recall_at_30": round(float(np.mean(recalls_30)), 4),
        "recall_at_50": round(float(np.mean(recalls_50)), 4),
        "recall_at_100": round(float(np.mean(recalls_100)), 4),
        "mean_reciprocal_rank_mrr": round(float(np.mean(mrrs)), 4),
        "mean_average_precision_map30": round(float(np.mean(maps_30)), 4),
        "evaluation_time_seconds": round(elapsed, 2),
    }

    print("\n" + "=" * 65)
    print(" CANDIDATE-JOB MATCHING BENCHMARK RESULTS")
    print("=" * 65)
    for k, v in metrics.items():
        print(f"  {k:35}: {v}")
    print("=" * 65)

    # Save to JSON
    with open(config.BENCHMARK_JSON, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # Save to CSV
    pd.DataFrame([metrics]).to_csv(config.BENCHMARK_CSV, index=False)

    # Generate benchmark visualizations
    generate_benchmark_charts(metrics, engine)

    return metrics


def generate_benchmark_charts(metrics: Dict[str, float], engine: MatchingEngine) -> None:
    """Generate visual reports for the matching engine performance."""
    print("[benchmark] Generating benchmark comparison plots...")

    # 1. Retrieval Metrics Bar Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    metric_keys = [
        ("Precision@10", metrics["precision_at_10"]),
        ("Precision@30", metrics["precision_at_30"]),
        ("Recall@10", metrics["recall_at_10"]),
        ("Recall@30", metrics["recall_at_30"]),
        ("Recall@50", metrics["recall_at_50"]),
        ("MRR", metrics["mean_reciprocal_rank_mrr"]),
        ("MAP@30", metrics["mean_average_precision_map30"]),
    ]
    labels, vals = zip(*metric_keys)
    colors = ["#2563eb", "#3b82f6", "#16a34a", "#22c55e", "#4ade80", "#ea580c", "#9333ea"]

    bars = ax.bar(labels, vals, color=colors, edgecolor="white", width=0.55)
    for b in bars:
        height = b.get_height()
        ax.annotate(f"{height:.3f}",
                    xy=(b.get_x() + b.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Metric Score (0 - 1.0)", fontsize=11)
    ax.set_title("Matching Engine Retrieval & Ranking Performance (Against Ground Truth)", fontsize=13, fontweight="bold", pad=12)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    chart_path = config.OUTPUTS_DIR / "retrieval_metrics_bars.png"
    fig.savefig(chart_path, dpi=150)
    plt.close(fig)
    print(f"  saved {chart_path.name}")

    # 2. Score Distribution Plot (Sample top 1000 candidate scores for Job 0)
    sample_ranked = engine.rank_candidates_for_job(job_id=engine.jobs_df.iloc[0]["job_id"], top_k=200)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.hist(sample_ranked["overall_score"], bins=20, color="#2563eb", alpha=0.7, edgecolor="black", label="Overall Match Score")
    ax.hist(sample_ranked["skill_score"], bins=20, color="#16a34a", alpha=0.5, edgecolor="black", label="Skill Score")
    ax.hist(sample_ranked["text_score"], bins=20, color="#ea580c", alpha=0.4, edgecolor="black", label="Text Similarity Score")
    ax.set_xlabel("Score (0 - 100)", fontsize=11)
    ax.set_ylabel("Candidate Count", fontsize=11)
    ax.set_title("Score Distribution Across Top Candidates", fontsize=12, fontweight="bold", pad=10)
    ax.legend(framealpha=0.9)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    dist_path = config.OUTPUTS_DIR / "score_distribution.png"
    fig.savefig(dist_path, dpi=150)
    plt.close(fig)
    print(f"  saved {dist_path.name}")


if __name__ == "__main__":
    engine = MatchingEngine(auto_load=True)
    evaluate_retrieval(engine, num_jobs_to_eval=50)
