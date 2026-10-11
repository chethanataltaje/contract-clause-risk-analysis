"""
Feature Extractor Module (Unit 1 & Unit 2).
Analyzes linguistic structures:
- Deontic Modality (Obligation: 'shall', 'must' vs. Permission: 'may')
- Conditionals ('if', 'provided that', 'subject to')
- Negations and Exclusion Boundaries ('in no event', 'shall not')
"""

import re
from typing import Dict, List, Any
from src.utils.config import (
    MODAL_OBLIGATIONS,
    MODAL_PERMISSIONS,
    CONDITIONALS,
    NEGATION_TERMS
)

def extract_linguistic_features(clause_text: str) -> Dict[str, Any]:
    """
    Identifies core linguistic patterns and returns pattern matches, counts, and flags.
    """
    text_lower = clause_text.lower()

    # Obligation vs. Permission
    found_obligations = [m for m in MODAL_OBLIGATIONS if re.search(rf"\b{re.escape(m)}\b", text_lower)]
    found_permissions = [m for m in MODAL_PERMISSIONS if re.search(rf"\b{re.escape(m)}\b", text_lower)]

    # Conditionals
    found_conditionals = [c for c in CONDITIONALS if re.search(rf"\b{re.escape(c)}\b", text_lower)]

    # Negations & Limitations
    found_negations = [n for n in NEGATION_TERMS if re.search(rf"\b{re.escape(n)}\b", text_lower)]

    # Classification of sentence modality type
    if found_obligations and not found_permissions:
        modality_type = "Strict Obligation"
    elif found_permissions and not found_obligations:
        modality_type = "Discretionary Permission"
    elif found_obligations and found_permissions:
        modality_type = "Mixed (Obligation + Permission)"
    else:
        modality_type = "Neutral / Declarative"

    return {
        "obligations": found_obligations,
        "permissions": found_permissions,
        "conditionals": found_conditionals,
        "negations": found_negations,
        "modality_type": modality_type,
        "has_obligation": len(found_obligations) > 0,
        "has_permission": len(found_permissions) > 0,
        "has_conditional": len(found_conditionals) > 0,
        "has_negation": len(found_negations) > 0,
        "total_linguistic_signals": len(found_obligations) + len(found_permissions) + len(found_conditionals) + len(found_negations)
    }
