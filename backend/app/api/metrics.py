from fastapi import APIRouter
from app.eval.eval_ml import run_ml_evaluation

router = APIRouter(prefix="/metrics", tags=["ML Evaluation & Observability"])

@router.get("/ml")
def get_ml_metrics():
    """
    Returns actual ML benchmark metrics: F1, Precision, NDCG@10, Prerequisite Recall, WER, and Latency.
    """
    return run_ml_evaluation()
