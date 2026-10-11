"""
Unit tests for Step 2 Linguistic & Information Extraction modules:
- feature_extractor.py (modals, conditionals, negations)
- information_extractor.py (amounts, deadlines, parties)
- ambiguity_detector.py (vague legal phrases)
"""

import pytest
from src.nlp.feature_extractor import extract_linguistic_features
from src.nlp.information_extractor import extract_key_information
from src.nlp.ambiguity_detector import detect_ambiguity

def test_linguistic_modal_obligation():
    clause = "The Vendor shall deliver the software and must comply with safety protocols."
    res = extract_linguistic_features(clause)
    assert res["has_obligation"] is True
    assert "shall" in res["obligations"]
    assert "must" in res["obligations"]
    assert res["modality_type"] == "Strict Obligation"

def test_linguistic_modal_permission():
    clause = "Either party may terminate discussions at its discretion."
    res = extract_linguistic_features(clause)
    assert res["has_permission"] is True
    assert "may" in res["permissions"]
    assert res["has_obligation"] is False
    assert res["modality_type"] == "Discretionary Permission"

def test_linguistic_conditionals_and_negations():
    clause = "In the event that Customer defaults, Supplier shall not be liable, in no event exceeding zero dollars."
    res = extract_linguistic_features(clause)
    assert res["has_conditional"] is True
    assert any("in the event that" in c for c in res["conditionals"])
    assert res["has_negation"] is True
    assert any("in no event" in n or "shall not" in n for n in res["negations"])

def test_information_extraction_amounts_and_percentages():
    clause = "Total liability is capped at $100,000, and a late fee of 15% or 5 percent applies."
    info = extract_key_information(clause)
    assert info["has_financial_entity"] is True
    assert any("$100,000" in amt for amt in info["extracted_amounts"])
    assert any("15%" in amt or "5 percent" in amt for amt in info["extracted_amounts"])

def test_information_extraction_deadlines_and_parties():
    clause = "Tenant shall provide ninety (90) days prior written notice to Landlord."
    info = extract_key_information(clause)
    assert info["has_deadline_entity"] is True
    assert any("90" in d for d in info["extracted_deadlines"])
    assert "Tenant" in info["extracted_parties"]
    assert "Landlord" in info["extracted_parties"]

def test_ambiguity_detection():
    vague_clause = "Vendor agrees to use best efforts to promptly resolve issues within reasonable time."
    res = detect_ambiguity(vague_clause)
    assert res["is_ambiguous"] is True
    assert res["ambiguity_count"] >= 3
    terms = [item["term"] for item in res["ambiguous_terms"]]
    assert any("best efforts" in t for t in terms)
    assert any("promptly" in t for t in terms)
    assert any("reasonable" in t for t in terms)

def test_clear_clause_not_ambiguous():
    clear_clause = "The payment shall be completed on the first day of each calendar month."
    res = detect_ambiguity(clear_clause)
    assert res["is_ambiguous"] is False
    assert res["ambiguity_count"] == 0
