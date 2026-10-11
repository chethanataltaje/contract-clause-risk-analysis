"""
Legal Risk Rules & Heuristics Module.
Applies transparent, configurable criteria to identified clause properties.
Distinguishes clause classification (CUAD) from risk severity evaluation.
"""

from typing import Dict, List, Any

def evaluate_risk_rules(
    category: str,
    linguistic_feats: Dict[str, Any],
    info_feats: Dict[str, Any],
    ambiguity_feats: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Evaluates clause features against legal risk heuristics.
    Returns list of triggered rules with severity level and description.
    """
    triggered_rules = []

    # 1. Limitation of Liability Heuristics
    if category == "Limitation of Liability":
        # Uncapped liability risk: No financial amount extracted
        if not info_feats.get("has_financial_entity", False):
            triggered_rules.append({
                "rule_id": "RULE_LIABILITY_UNCAPPED",
                "severity": "HIGH",
                "message": "Potential uncapped liability: Clause discusses limitation/liability but specifies no monetary ceiling ($ or %)."
            })
        # Broad exclusion / waiver of damages
        if linguistic_feats.get("has_negation", False):
            triggered_rules.append({
                "rule_id": "RULE_LIABILITY_BROAD_EXCLUSION",
                "severity": "MEDIUM",
                "message": "Broad liability exclusion: Contains strict negations ('in no event' / 'waives') excluding damage categories."
            })

    # 2. Termination for Convenience Heuristics
    elif category == "Termination for Convenience":
        deadlines = info_feats.get("extracted_deadlines", [])
        # Short or immediate notice
        has_short_notice = any(
            any(w in d.lower() for w in ["immediately", "0 days", "24 hours", "48 hours", "7 days"])
            for d in deadlines
        )
        if has_short_notice or not info_feats.get("has_deadline_entity", False):
            triggered_rules.append({
                "rule_id": "RULE_TERMINATION_IMMEDIATE_OR_UNDEFINED",
                "severity": "HIGH",
                "message": "Immediate or undefined notice: Contract may be terminable without adequate advance notice window."
            })
        else:
            triggered_rules.append({
                "rule_id": "RULE_TERMINATION_CONVENIENCE_STANDARD",
                "severity": "MEDIUM",
                "message": f"Termination for convenience with notice window ({', '.join(deadlines)})."
            })

    # 3. Indemnification Heuristics
    elif category == "Indemnification":
        if linguistic_feats.get("has_obligation", False):
            triggered_rules.append({
                "rule_id": "RULE_INDEMNIFICATION_MANDATORY",
                "severity": "HIGH",
                "message": "Mandatory third-party defense/indemnity obligation: Direct exposure to third-party claims and defense costs."
            })

    # 4. Non-Compete & Restrictive Covenants
    elif category == "Non-Compete":
        if not info_feats.get("has_deadline_entity", False):
            triggered_rules.append({
                "rule_id": "RULE_NON_COMPETE_PERPETUAL",
                "severity": "HIGH",
                "message": "Overly broad non-compete: No defined restrictive time period/expiration date identified."
            })
        else:
            triggered_rules.append({
                "rule_id": "RULE_NON_COMPETE_RESTRICTION",
                "severity": "HIGH",
                "message": f"Competitive restraint active for specified duration ({', '.join(info_feats['extracted_deadlines'])})."
            })

    # 5. Confidentiality Heuristics
    elif category == "Confidentiality":
        if not info_feats.get("has_deadline_entity", False):
            triggered_rules.append({
                "rule_id": "RULE_CONFIDENTIALITY_PERPETUAL",
                "severity": "MEDIUM",
                "message": "Perpetual confidentiality obligation: No finite survival duration (e.g. 3 or 5 years) detected."
            })

    # 6. Ambiguity Heuristics (Cross-cutting across any category)
    if ambiguity_feats.get("is_ambiguous", False):
        ambig_terms = [t["term"] for t in ambiguity_feats.get("ambiguous_terms", [])]
        triggered_rules.append({
            "rule_id": "RULE_AMBIGUOUS_STANDARDS",
            "severity": "MEDIUM",
            "message": f"Subjective or vague legal standards identified: {', '.join(ambig_terms)}."
        })

    # 7. Unilateral Permission Heuristics
    if linguistic_feats.get("has_permission", False) and not linguistic_feats.get("has_obligation", False):
        triggered_rules.append({
            "rule_id": "RULE_DISCRETIONARY_RIGHT",
            "severity": "LOW",
            "message": "Discretionary permission granted ('may' / 'entitled to') without counter-balancing obligation."
        })

    return triggered_rules
