"""
Clause Classifier Inference Wrapper.
Provides a unified interface to predict clause categories using either:
- 'baseline' (TF-IDF + Logistic Regression)
- 'sbert' (Sentence-BERT Embeddings + Classifier)
"""

import joblib
from pathlib import Path
from typing import Dict, Any, List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

from src.utils.config import BASELINES_DIR, EMBEDDINGS_DIR

class ClauseClassifier:
    def __init__(self, model_type: str = "baseline"):
        self.model_type = model_type.lower()
        self.baseline_pipeline = None
        self.sbert_model = None
        self.sbert_clf = None
        self._load_model()

    def _load_model(self):
        if self.model_type == "baseline":
            model_path = BASELINES_DIR / "tfidf_logistic_regression.joblib"
            if not model_path.exists():
                raise FileNotFoundError(f"Baseline model not found at {model_path}. Run train_baseline.py first.")
            self.baseline_pipeline = joblib.load(model_path)
        elif self.model_type == "sbert":
            clf_path = EMBEDDINGS_DIR / "sbert_classifier.joblib"
            if not clf_path.exists():
                raise FileNotFoundError(f"SBERT classifier not found at {clf_path}. Run train_sbert.py first.")
            self.sbert_model = SentenceTransformer("all-MiniLM-L6-v2")
            self.sbert_clf = joblib.load(clf_path)
        else:
            raise ValueError(f"Unknown model_type: {self.model_type}. Choose 'baseline' or 'sbert'.")

    def predict_clause(self, clause_text: str) -> Dict[str, Any]:
        """
        Predicts category and confidence probability for a single clause.
        """
        if self.model_type == "baseline":
            pred_class = self.baseline_pipeline.predict([clause_text])[0]
            probs = self.baseline_pipeline.predict_proba([clause_text])[0]
            classes = self.baseline_pipeline.classes_
            conf = float(np.max(probs))
        else:
            emb = self.sbert_model.encode([clause_text], normalize_embeddings=True)
            pred_class = self.sbert_clf.predict(emb)[0]
            probs = self.sbert_clf.predict_proba(emb)[0]
            classes = self.sbert_clf.classes_
            conf = float(np.max(probs))

        top_classes = sorted(
            [{"category": cls_name, "probability": round(float(prob), 4)} for cls_name, prob in zip(classes, probs)],
            key=lambda x: x["probability"],
            reverse=True
        )[:3]

        return {
            "predicted_category": pred_class,
            "confidence": round(conf, 4),
            "model_used": self.model_type,
            "top_predictions": top_classes
        }
