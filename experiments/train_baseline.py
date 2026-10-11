"""
Baseline Model: TF-IDF + Logistic Regression Classifier.
Academic/Benchmark Baseline representing classical Statistical NLP (Unit 2).
"""

import sys
import time
import joblib
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score, f1_score

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.utils.config import PROCESSED_DATA_DIR, BASELINES_DIR
from src.utils.logging_utils import get_logger

logger = get_logger("train_baseline")

def train_and_evaluate_baseline():
    """
    Trains TF-IDF + Logistic Regression pipeline on train_clauses.csv
    and evaluates on test_clauses.csv (contract-level split).
    """
    BASELINES_DIR.mkdir(parents=True, exist_ok=True)

    train_path = PROCESSED_DATA_DIR / "train_clauses.csv"
    test_path = PROCESSED_DATA_DIR / "test_clauses.csv"

    if not train_path.exists() or not test_path.exists():
        raise FileNotFoundError("Processed datasets not found. Run prepare_data.py first.")

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    X_train = train_df["clause_text"]
    y_train = train_df["category"]
    X_test = test_df["clause_text"]
    y_test = test_df["category"]

    logger.info(f"Training TF-IDF + Logistic Regression on {len(X_train)} samples across {y_train.nunique()} classes...")

    # Build Pipeline: TF-IDF with sublinear tf scaling and (1, 2) n-grams
    model_pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            stop_words="english"
        )),
        ("clf", LogisticRegression(
            C=1.0,
            max_iter=500,
            class_weight="balanced",
            random_state=42
        ))
    ])

    start_train_time = time.time()
    model_pipeline.fit(X_train, y_train)
    train_duration = time.time() - start_train_time
    logger.info(f"Training completed in {train_duration:.4f} seconds.")

    # Measure test latency
    start_infer_time = time.time()
    y_pred = model_pipeline.predict(X_test)
    infer_duration = (time.time() - start_infer_time) / len(X_test) * 1000  # ms per sample

    accuracy = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")

    logger.info(f"--- Baseline Evaluation Results ---")
    logger.info(f"Accuracy: {accuracy:.4f} | Macro F1: {macro_f1:.4f} | Latency: {infer_duration:.2f} ms/sample")
    logger.info("\n" + classification_report(y_test, y_pred, zero_division=0))

    # Save trained model artifact
    model_path = BASELINES_DIR / "tfidf_logistic_regression.joblib"
    joblib.dump(model_pipeline, model_path)
    logger.info(f"Saved baseline pipeline to: {model_path}")

    return {
        "model_name": "TF-IDF + Logistic Regression",
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "latency_ms": infer_duration,
        "model_path": str(model_path)
    }

if __name__ == "__main__":
    res = train_and_evaluate_baseline()
    print("\n[SUCCESS] Baseline training completed successfully!")
    print(f"Accuracy: {res['accuracy'] * 100:.1f}% | Macro F1: {res['macro_f1']:.3f} | Latency: {res['latency_ms']:.2f} ms")
