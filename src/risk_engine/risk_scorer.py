"""
Risk Scorer & Priority Aggregator Module.
Combines clause category, triggered rules, entity completeness, and ambiguity signals
into unified review priority tiers: High Risk, Needs Review, or Informational.
"""

from typing import Dict, List, Any
from src.risk_engine.risk_rules import evaluate_risk_rules
from src.risk_engine.explanations import generate_clause_explanation

def score_clause_risk(
    clause_id: str,
    clause_text: str,
    page_number: int,
    classification_result: Dict[str, Any],
    linguistic_feats: Dict[str, Any],
    info_feats: Dict[str, Any],
    ambiguity_feats: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Evaluates risk rules and calculates final review tier and priority score.
    """
    category = classification_result["predicted_category"]
    confidence = classification_result["confidence"]

    # Evaluate rules
    triggered_rules = evaluate_risk_rules(
        category=category,
        linguistic_feats=linguistic_feats,
        info_feats=info_feats,
        ambiguity_feats=ambiguity_feats
    )

    # Determine risk level from triggered rules
    has_high_rule = any(r["severity"] == "HIGH" for r in triggered_rules)
    has_medium_rule = any(r["severity"] == "MEDIUM" for r in triggered_rules)

    if has_high_rule:
        risk_level = "High Risk"
        risk_score = 0.85
    elif has_medium_rule or ambiguity_feats.get("is_ambiguous", False):
        risk_level = "Needs Review"
        risk_score = 0.55
    else:
        risk_level = "Informational"
        risk_score = 0.20

    # Generate explainable reasons
    explanation = generate_clause_explanation(
        category=category,
        risk_level=risk_level,
        triggered_rules=triggered_rules,
        linguistic_feats=linguistic_feats,
        info_feats=info_feats,
        ambiguity_feats=ambiguity_feats
    )

    return {
        "clause_id": clause_id,
        "page_number": page_number,
        "clause_text": clause_text,
        "predicted_category": category,
        "confidence": confidence,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "triggered_rules": triggered_rules,
        "explanation": explanation,
        "extracted_entities": {
            "amounts": info_feats.get("extracted_amounts", []),
            "deadlines": info_feats.get("extracted_deadlines", []),
            "parties": info_feats.get("extracted_parties", [])
        },
        "linguistic_summary": {
            "modality": linguistic_feats.get("modality_type", "Neutral"),
            "has_negation": linguistic_feats.get("has_negation", False),
            "is_ambiguous": ambiguity_feats.get("is_ambiguous", False)
        }
    }
