"""
Evidence-Based Explanations Module.
Generates human-readable, transparent rationales for each flagged clause.
"""

from typing import Dict, List, Any

def generate_clause_explanation(
    category: str,
    risk_level: str,
    triggered_rules: List[Dict[str, Any]],
    linguistic_feats: Dict[str, Any],
    info_feats: Dict[str, Any],
    ambiguity_feats: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Constructs a plain-English explanation of why a clause was flagged,
    what specific language triggered it, and recommended reviewer action.
    """
    summary_reasons = []
    
    for rule in triggered_rules:
        summary_reasons.append(rule["message"])

    if not summary_reasons:
        if risk_level == "Informational":
            summary_reasons.append("Standard bilateral contractual clause; no abnormal legal exposure or ambiguity detected.")
        else:
            summary_reasons.append(f"Classified as {category} with standard risk profile.")

    # Recommended action advice for the human reviewer
    if risk_level == "High Risk":
        recommendation = "High Priority: Request legal counsel review to negotiate explicit caps, reciprocal obligations, or minimum notice windows."
    elif risk_level == "Needs Review":
        recommendation = "Medium Priority: Clarify subjective phrases and confirm specific survival dates or notice requirements."
    else:
        recommendation = "Low Priority: Standard commercial clause. Verify alignment with business intent."

    return {
        "summary": " ".join(summary_reasons),
        "reasons": summary_reasons,
        "recommendation": recommendation,
        "flagged_linguistic_signals": {
            "obligations": linguistic_feats.get("obligations", []),
            "permissions": linguistic_feats.get("permissions", []),
            "negations": linguistic_feats.get("negations", []),
            "ambiguous_words": [t["term"] for t in ambiguity_feats.get("ambiguous_terms", [])]
        }
    }
