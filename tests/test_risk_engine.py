"""
Unit tests for Step 4 Risk Engine & Explanations:
- test_risk_rules (uncapped liability, immediate termination, non-compete)
- test_risk_scorer (High Risk, Needs Review, Informational)
- test_explanations (evidence-based justification generation)
"""

import pytest
from src.risk_engine.risk_rules import evaluate_risk_rules
from src.risk_engine.risk_scorer import score_clause_risk
from src.risk_engine.explanations import generate_clause_explanation

def test_uncapped_liability_flags_high_risk():
    cat = "Limitation of Liability"
    ling = {"has_negation": True, "negations": ["in no event"]}
    info = {"has_financial_entity": False, "extracted_amounts": []}
    ambig = {"is_ambiguous": False, "ambiguous_terms": []}

    rules = evaluate_risk_rules(cat, ling, info, ambig)
    rule_ids = [r["rule_id"] for r in rules]
    
    assert "RULE_LIABILITY_UNCAPPED" in rule_ids
    assert any(r["severity"] == "HIGH" for r in rules)

def test_termination_immediate_flags_high_risk():
    cat = "Termination for Convenience"
    ling = {"has_permission": True, "permissions": ["may"]}
    info = {"has_deadline_entity": False, "extracted_deadlines": []}
    ambig = {"is_ambiguous": False, "ambiguous_terms": []}

    rules = evaluate_risk_rules(cat, ling, info, ambig)
    rule_ids = [r["rule_id"] for r in rules]
    assert "RULE_TERMINATION_IMMEDIATE_OR_UNDEFINED" in rule_ids

def test_vague_terms_flags_needs_review():
    cat = "Renewal / Term"
    ling = {"has_obligation": True, "has_negation": False}
    info = {"has_deadline_entity": True, "extracted_deadlines": ["1 year"]}
    ambig = {"is_ambiguous": True, "ambiguous_terms": [{"term": "best efforts", "description": "high burden"}]}

    rules = evaluate_risk_rules(cat, ling, info, ambig)
    rule_ids = [r["rule_id"] for r in rules]
    assert "RULE_AMBIGUOUS_STANDARDS" in rule_ids

def test_end_to_end_risk_scorer_output():
    classification = {
        "predicted_category": "Limitation of Liability",
        "confidence": 0.88,
        "model_used": "baseline"
    }
    ling = {"has_negation": True, "has_obligation": False, "has_permission": False, "modality_type": "Neutral"}
    info = {"has_financial_entity": False, "extracted_amounts": [], "extracted_deadlines": [], "extracted_parties": []}
    ambig = {"is_ambiguous": False, "ambiguous_terms": []}

    result = score_clause_risk(
        clause_id="CL-001",
        clause_text="In no event shall liability apply.",
        page_number=1,
        classification_result=classification,
        linguistic_feats=ling,
        info_feats=info,
        ambiguity_feats=ambig
    )

    assert result["risk_level"] == "High Risk"
    assert result["risk_score"] > 0.8
    assert len(result["triggered_rules"]) > 0
    assert "explanation" in result
    assert "High Priority" in result["explanation"]["recommendation"]
