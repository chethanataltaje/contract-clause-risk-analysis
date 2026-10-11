"""
Unit tests for Step 3: Clause Classification Models & Inference Wrappers.
"""

import pytest
from src.nlp.clause_classifier import ClauseClassifier

def test_baseline_classifier_inference():
    clf = ClauseClassifier(model_type="baseline")
    test_clause = "In no event shall either party's cumulative liability under this Agreement exceed $10,000."
    res = clf.predict_clause(test_clause)
    
    assert res["predicted_category"] == "Limitation of Liability"
    assert res["confidence"] > (1.0 / 6.0)  # Must exceed random baseline chance (16.7%)
    assert res["model_used"] == "baseline"
    assert len(res["top_predictions"]) > 0

def test_sbert_classifier_inference():
    clf = ClauseClassifier(model_type="sbert")
    test_clause = "The Consultant shall not engage with any direct competitor for twenty-four months."
    res = clf.predict_clause(test_clause)
    
    assert res["predicted_category"] in ["Non-Compete", "Confidentiality"]
    assert res["confidence"] > 0.2
    assert res["model_used"] == "sbert"

def test_invalid_model_type_raises():
    with pytest.raises(ValueError):
        ClauseClassifier(model_type="unknown_model")
