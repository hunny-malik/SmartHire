import os
import sys

# Re-export from app.eval.eval_ml to keep single source of truth
from app.eval.eval_ml import (
    compute_f1_precision_recall,
    evaluate_resume_extraction,
    compute_ndcg_at_k,
    evaluate_job_ranking,
    evaluate_skill_gap_dag,
    evaluate_voice_metrics,
    evaluate_semantic_embeddings,
    evaluate_interview_rubric,
    run_ml_evaluation,
    run_sync,
)

if __name__ == "__main__":
    res = run_sync()
    print("\n================== SMART HIRE ML BENCHMARKS (LIVE EMPIRICAL) ==================")
    print(f"Timestamp: {res['timestamp']}")
    for b in res["benchmarks"]:
        print(f"[{b['status']:<17}] {b['metric']:<36} | Target: {b['target']:<10} | Actual: {b['actual']:<8} | Gap: {b['gap']}")
    print(f"\nPassed: {res['summary']['passed']} / {res['summary']['total_benchmarks']} ML benchmarks.")
    print("===============================================================================\n")
