"""
Semantic Classification Model: Sentence-BERT (SBERT) Embeddings + Classifier.
Represents dense semantic contextual vectors (Unit 2 & Unit 3).
"""

import sys
import time
import joblib
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, f1_score
from sentence_transformers import SentenceTransformer

# Add root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.utils.config import PROCESSED_DATA_DIR, EMBEDDINGS_DIR
from src.utils.logging_utils import get_logger

logger = get_logger("train_sbert")

MODEL_CHECKPOINT = "all-MiniLM-L6-v2"

def train_and_evaluate_sbert():
    """
    Computes SBERT dense sentence embeddings and trains a linear classifier
    on top of the semantic representations.
    """
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)

    train_path = PROCESSED_DATA_DIR / "train_clauses.csv"
    test_path = PROCESSED_DATA_DIR / "test_clauses.csv"

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    X_train_text = train_df["clause_text"].tolist()
    y_train = train_df["category"].values
    X_test_text = test_df["clause_text"].tolist()
    y_test = test_df["category"].values

    logger.info(f"Loading SentenceTransformer checkpoint: '{MODEL_CHECKPOINT}'...")
    encoder = SentenceTransformer(MODEL_CHECKPOINT)

    logger.info("Computing dense sentence embeddings for training clauses...")
    start_encode_train = time.time()
    X_train_emb = encoder.encode(X_train_text, show_progress_bar=False, normalize_embeddings=True)
    train_encode_time = time.time() - start_encode_train
    logger.info(f"Generated {X_train_emb.shape[0]} embeddings of dimension {X_train_emb.shape[1]} in {train_encode_time:.2f}s.")

    # Train classifier on top of dense embeddings
    clf = LogisticRegression(C=2.0, max_iter=500, class_weight="balanced", random_state=42)
    clf.fit(X_train_emb, y_train)

    # Encode test set and measure inference latency
    start_infer_time = time.time()
    X_test_emb = encoder.encode(X_test_text, show_progress_bar=False, normalize_embeddings=True)
    y_pred = clf.predict(X_test_emb)
    total_infer_time = time.time() - start_infer_time
    latency_per_sample_ms = (total_infer_time / len(X_test_text)) * 1000

    accuracy = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")

    logger.info("--- SBERT Semantic Model Evaluation Results ---")
    logger.info(f"Accuracy: {accuracy:.4f} | Macro F1: {macro_f1:.4f} | Latency: {latency_per_sample_ms:.2f} ms/sample")
    logger.info("\n" + classification_report(y_test, y_pred, zero_division=0))

    # Save artifacts
    clf_path = EMBEDDINGS_DIR / "sbert_classifier.joblib"
    joblib.dump(clf, clf_path)
    logger.info(f"Saved SBERT classifier artifact to: {clf_path}")

    return {
        "model_name": f"SBERT ({MODEL_CHECKPOINT}) + Linear Classifier",
        "accuracy": accuracy,
        "macro_f1": macro_f1,
        "latency_ms": latency_per_sample_ms,
        "embedding_dim": X_train_emb.shape[1]
    }

if __name__ == "__main__":
    res = train_and_evaluate_sbert()
    print("\n[SUCCESS] SBERT training and evaluation completed successfully!")
    print(f"Accuracy: {res['accuracy'] * 100:.1f}% | Macro F1: {res['macro_f1']:.3f} | Latency: {res['latency_ms']:.2f} ms")
