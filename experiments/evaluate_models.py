"""
Model Benchmarking & Evaluation Suite.
Computes comparative performance metrics across all models:
- Precision, Recall, Macro-F1, Accuracy, Inference Latency
- Generates markdown & CSV comparison summaries.
"""

import sys
import time
from pathlib import Path
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.utils.config import PROCESSED_DATA_DIR, RESULTS_DIR
from src.nlp.clause_classifier import ClauseClassifier
from src.utils.logging_utils import get_logger

logger = get_logger("evaluate_models")

def run_benchmarks():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    test_path = PROCESSED_DATA_DIR / "test_clauses.csv"
    test_df = pd.read_csv(test_path)
    X_test = test_df["clause_text"].tolist()
    y_test = test_df["category"].tolist()

    models_to_test = ["baseline", "sbert"]
    benchmark_records = []

    for m_type in models_to_test:
        logger.info(f"Evaluating model: {m_type}...")
        clf_wrapper = ClauseClassifier(model_type=m_type)

        start_time = time.time()
        preds = []
        for text in X_test:
            res = clf_wrapper.predict_clause(text)
            preds.append(res["predicted_category"])
        total_time = time.time() - start_time
        latency_ms = (total_time / len(X_test)) * 1000

        acc = accuracy_score(y_test, preds)
        p, r, f1, _ = precision_recall_fscore_support(y_test, preds, average="macro", zero_division=0)

        benchmark_records.append({
            "Model Architecture": "TF-IDF + Logistic Regression" if m_type == "baseline" else "SBERT (all-MiniLM-L6-v2) + Classifier",
            "Accuracy": round(acc, 4),
            "Macro Precision": round(p, 4),
            "Macro Recall": round(r, 4),
            "Macro F1": round(f1, 4),
            "Avg Latency (ms/sample)": round(latency_ms, 2)
        })

    results_df = pd.DataFrame(benchmark_records)
    csv_path = RESULTS_DIR / "model_comparison_metrics.csv"
    results_df.to_csv(csv_path, index=False)
    logger.info(f"Saved benchmark results to {csv_path}")

    print("\n" + "="*70)
    print("                CLAUSEGUARD AI - MODEL BENCHMARK COMPARISON")
    print("="*70)
    print(results_df.to_string(index=False))
    print("="*70)

if __name__ == "__main__":
    run_benchmarks()
